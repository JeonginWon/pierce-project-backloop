# rag/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied

from django.contrib.auth.hashers import check_password

from django.conf import settings
from django.db.models import Count
from pgvector.django import CosineDistance

import openai

from .models import (
    User, Post, Follow,
    StockDailyPrice, StockHolding, TransactionHistory,
    HistoricalNews, LatestNews,
    Comment, PostLike,
)
from .serializers import (
    UserSerializer, UserReadSerializer, UserLoginSerializer,
    PostWriteSerializer, PostReadSerializer, CommentSerializer,
    FollowSerializer,
    StockDailyPriceSerializer, StockHoldingSerializer, TransactionHistorySerializer,
    HistoricalNewsSerializer, LatestNewsSerializer
)

# --- OpenAI 클라이언트 지연 로딩 ---
openai_client = None

def get_openai_client():
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    # 👇 .env에서 주소 가져오기
    api_base = getattr(settings, 'OPENAI_API_BASE', None) 

    if not api_key:
        print("❌ [CRITICAL] OPENAI_API_KEY가 없습니다!")
        return None
        
    if not api_base:
        print("⚠️ [Warning] OPENAI_API_BASE가 없습니다. 공식 서버로 접속합니다.")

    return openai.OpenAI(
        api_key=api_key,
        base_url=api_base
    )

def get_embedding(text):
    """OpenAI API를 사용하여 텍스트를 벡터(1536차원)로 변환"""
    client = get_openai_client()
    try:
        # 공백 제거 및 줄바꿈 처리
        text = text.replace("\n", " ")
        
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"💥 OpenAI 임베딩 생성 실패: {e}")
        return None

# --------------------------------------

# 1. User ViewSet -----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["register", "login", "create"]:
            return [AllowAny()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = UserReadSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserReadSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            read_data = UserReadSerializer(user).data
            return Response(read_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        login_serializer = UserLoginSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        nickname = login_serializer.validated_data["nickname"]
        password = login_serializer.validated_data["password"]

        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return Response({"detail": "존재하지 않는 닉네임입니다."}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, user.password):
            return Response({"detail": "비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        request.session["user_id"] = user.id

        return Response({
            "message": "로그인 성공",
            "user": UserReadSerializer(user).data,
        })

    @action(detail=False, methods=["post"])
    def logout(self, request):
        request.session.flush()
        return Response({"message": "로그아웃 되었습니다."})

    @action(detail=False, methods=["get"])
    def me(self, request):
        user_id = request.session.get("user_id")
        if not user_id:
            return Response({"detail": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "유저를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserReadSerializer(user)
        return Response(serializer.data)


# ---------------------------------------------
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("author")
    serializer_class = PostWriteSerializer

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "feed"]:
            return PostReadSerializer
        return PostWriteSerializer

    def get_queryset(self):
        qs = Post.objects.all().select_related("author")
        qs = qs.annotate(
            comment_count=Count("comments"),
            like_count=Count("likes"),
        )
        return qs

    def _get_current_user(self, request):
        user_id = request.session.get("user_id")
        if not user_id:
            raise PermissionDenied("로그인이 필요합니다.")
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise PermissionDenied("유저 정보를 찾을 수 없습니다.")

    def perform_create(self, serializer):
        user = self._get_current_user(self.request)
        serializer.save(author=user)

    def perform_update(self, serializer):
        user = self._get_current_user(self.request)
        post = self.get_object()
        if post.author_id != user.id:
            raise PermissionDenied("본인이 작성한 글만 수정할 수 있습니다.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self._get_current_user(self.request)
        if instance.author_id != user.id:
            raise PermissionDenied("본인이 작성한 글만 삭제할 수 있습니다.")
        instance.delete()

    @action(detail=False, methods=["get"])
    def feed(self, request):
        ticker = request.query_params.get("ticker")
        qs = self.get_queryset().order_by("-created_at")
        if ticker:
            qs = qs.filter(ticker=ticker)

        serializer = self.get_serializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        user = self._get_current_user(request)
        post = self.get_object()

        like_obj, created = PostLike.objects.get_or_create(post=post, user=user)
        if not created:
            like_obj.delete()
            liked = False
        else:
            liked = True

        like_count = post.likes.count()
        return Response({
            "liked": liked,
            "like_count": like_count,
        })

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        post = self.get_object()

        if request.method == "GET":
            comments = post.comments.select_related("author").order_by("created_at")
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        user = self._get_current_user(request)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

class StockDailyPriceViewSet(viewsets.ModelViewSet):
    queryset = StockDailyPrice.objects.all()
    serializer_class = StockDailyPriceSerializer

class StockHoldingViewSet(viewsets.ModelViewSet):
    queryset = StockHolding.objects.all()
    serializer_class = StockHoldingSerializer

class TransactionHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer


# === [여기서부터 뉴스 관련 ViewSet (중복 없이 정리됨)] ===

class HistoricalNewsViewSet(viewsets.ModelViewSet):
    queryset = HistoricalNews.objects.all()
    serializer_class = HistoricalNewsSerializer

    def perform_create(self, serializer):
        text = serializer.validated_data.get('body')
        if text:
            vector = get_embedding(text)
            if vector:
                serializer.save(body_embedding_vector=vector)
            else:
                serializer.save()
        else:
            serializer.save()

    # 과거 뉴스 검색 (POST /api/historical-news/search/)
    @action(detail=False, methods=['post'])
    def search(self, request):
        query_text = request.data.get('query')
        if not query_text:
            return Response({"error": "query 필드가 필요합니다."}, status=400)
        
        query_vector = get_embedding(query_text)
        if not query_vector:
            return Response({"error": "임베딩 생성 실패"}, status=500)
        
        results = HistoricalNews.objects.annotate(
            distance=CosineDistance('body_embedding_vector', query_vector)
        ).order_by('distance')[:5]

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class LatestNewsViewSet(viewsets.ModelViewSet):
    queryset = LatestNews.objects.all()
    serializer_class = LatestNewsSerializer

    def perform_create(self, serializer):
        text = serializer.validated_data.get('body')
        if text:
            vector = get_embedding(text)
            if vector:
                serializer.save(body_embedding_vector=vector)
            else:
                serializer.save()
        else:
            serializer.save()

    # 1. [수정됨] 같은 최신 뉴스끼리 추천 (URL: /api/latest-news/{id}/similar_latest/)
    @action(detail=True, methods=['get'], url_path='similar_latest')
    def similar_latest_news(self, request, pk=None):
        news_item = self.get_object() 
        query_vector = news_item.body_embedding_vector
        
        if not query_vector:
             return Response({"error": "임베딩 벡터가 없습니다."}, status=400)

        results = LatestNews.objects.exclude(pk=pk).annotate(
            distance=CosineDistance('body_embedding_vector', query_vector)
        ).order_by('distance')[:5]

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    # 2. [수정됨] 과거 뉴스에서 추천 (URL: /api/latest-news/{id}/similar_historical/)
    @action(detail=True, methods=['get'], url_path='similar_historical')
    def similar_historical_news(self, request, pk=None):
        latest_news = self.get_object()
        query_vector = latest_news.body_embedding_vector
        
        # 🚨 [중요 수정] numpy array는 'if not'을 쓰면 에러가 납니다. 'is None'으로 체크해야 합니다.
        if query_vector is None:
            return Response({"message": "아직 AI 분석이 완료되지 않았습니다."}, status=200)

        # pgvector는 numpy array를 그대로 쿼리에 넣어도 잘 작동합니다.
        similar_docs = HistoricalNews.objects.annotate(
            distance=CosineDistance('body_embedding_vector', query_vector)
        ).order_by('distance')[:3]

        serializer = HistoricalNewsSerializer(similar_docs, many=True)
        return Response(serializer.data)

    # 3. 검색 기능
    @action(detail=False, methods=['post'])
    def search(self, request):
        query_text = request.data.get('query')
        if not query_text:
            return Response({"error": "query 필드가 필요합니다."}, status=400)
        
        try:
            query_vector = get_embedding(query_text)
            if not query_vector:
                return Response({"error": "임베딩 생성 실패"}, status=500)

            results = LatestNews.objects.annotate(
                distance=CosineDistance('body_embedding_vector', query_vector)
            ).order_by('distance')[:5]

            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)