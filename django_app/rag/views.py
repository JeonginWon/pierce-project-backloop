from rest_framework import viewsets
from rest_framework.decorators import action  # 👈 추가됨
from rest_framework.response import Response  # 👈 추가됨
from pgvector.django import CosineDistance    # 👈 추가됨 (거리 계산용)

from .models import VectorTest, Member
from .serializers import VectorTestSerializer, MemberSerializer

# 전역 변수
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

class VectorTestViewSet(viewsets.ModelViewSet):
    queryset = VectorTest.objects.all()
    serializer_class = VectorTestSerializer

    # 1. 저장할 때 (기존과 동일)
    def perform_create(self, serializer):
        text = serializer.validated_data.get('content')
        model = get_embedding_model()
        vector = model.embed_query(text)
        serializer.save(embedding=vector)

    # 2. 검색할 때 (⭐ 새로 추가된 기능!)
    # 주소: POST /api/vectors/search/
    @action(detail=False, methods=['post'])
    def search(self, request):
        # 사용자가 보낸 질문 받기
        query_text = request.data.get('query')
        if not query_text:
            return Response({"error": "query 필드가 필요합니다."}, status=400)

        # 질문을 벡터로 변환
        model = get_embedding_model()
        query_vector = model.embed_query(query_text)

        # DB에서 가장 유사한(거리가 가까운) 데이터 3개 찾기
        # CosineDistance: 코사인 유사도 (작을수록 유사함)
        results = VectorTest.objects.annotate(
            distance=CosineDistance('embedding', query_vector)
        ).order_by('distance')[:3]

        # 결과 반환
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer