from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from pgvector.django import CosineDistance

from .models import (
    User, Post, Follow, 
    StockDailyPrice, StockHolding, TransactionHistory,
    HistoricalNews, LatestNews
)
from .serializers import (
    UserSerializer, PostSerializer, FollowSerializer,
    StockDailyPriceSerializer, StockHoldingSerializer, TransactionHistorySerializer,
    HistoricalNewsSerializer, LatestNewsSerializer
)

# --- AI 모델 지연 로딩 (메모리 최적화) ---
embedding_model = None

def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        print("⏳ 임베딩 모델 로딩 시작...")
        from langchain_huggingface import HuggingFaceEmbeddings
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ 모델 로딩 완료!")
    return embedding_model
# --------------------------------------

# 1. 일반 CRUD ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

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

# 2. RAG (뉴스) ViewSets - 자동 임베딩 및 검색 기능
class HistoricalNewsViewSet(viewsets.ModelViewSet):
    queryset = HistoricalNews.objects.all()
    serializer_class = HistoricalNewsSerializer

    # 저장 시 자동 임베딩
    def perform_create(self, serializer):
        text = serializer.validated_data.get('body')
        if text:
            model = get_embedding_model()
            vector = model.embed_query(text)
            serializer.save(body_embedding_vector=vector)
        else:
            serializer.save()

    # 유사도 검색 기능 (POST /api/historical-news/search/)
    @action(detail=False, methods=['post'])
    def search(self, request):
        query_text = request.data.get('query')
        if not query_text:
            return Response({"error": "query 필드가 필요합니다."}, status=400)
        
        model = get_embedding_model()
        query_vector = model.embed_query(query_text)
        
        # 코사인 유사도로 상위 5개 검색
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
            model = get_embedding_model()
            vector = model.embed_query(text)
            serializer.save(body_embedding_vector=vector)
        else:
            serializer.save()