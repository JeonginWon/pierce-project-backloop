import openai
from django.conf import settings
from pgvector.django import CosineDistance
from django.db.models import F
from .models import HistoricalNews, LatestNews


# Django settings에서 API 키 가져오기
client = openai.OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE
)

def get_embedding(text):
    """텍스트를 벡터로 변환하는 함수"""
    try:
        if not text: 
            return None
        
        # 텍스트 전처리
        text = text.replace("\n", " ")
        if len(text) > 5000:
            text = text[:5000]

        # OpenAI API 호출
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
        
    except Exception as e:
        print(f"💥 임베딩 생성 실패: {e}")
        return None
    
def update_similarity_score(news_instance):
    """
    최신 뉴스가 저장될 때, 과거 뉴스 중 가장 유사한 것과의 점수를 계산해 저장함
    """
    # 👇 [수정 1] embedding -> body_embedding_vector 로 변경
    if not news_instance.body_embedding_vector:
        return

    try:
        # 1. 가장 유사한 과거 뉴스 1개 찾기
        most_similar = HistoricalNews.objects.annotate(
            # 👇 [수정 2] 모델 필드명에 맞춰서 'body_embedding_vector'로 변경
            distance=CosineDistance('body_embedding_vector', news_instance.body_embedding_vector)
        ).order_by('distance').first()

        # 2. 점수 변환 및 저장
        if most_similar:
            score = 1.0 - most_similar.distance
            news_instance.max_similarity_score = score
            news_instance.save(update_fields=['max_similarity_score'])
            print(f"✨ [유사도 계산 완료] {news_instance.title} : {score:.4f}")
            
    except Exception as e:
        print(f"❌ 유사도 계산 실패: {e}")