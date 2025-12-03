import os
import django
import pandas as pd
import time
import openai
from django.conf import settings

# 1. Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from rag.models import HistoricalNews, StockDailyPrice

# 2. OpenAI 클라이언트 설정
client = openai.OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE
)

def get_embedding(text):
    """OpenAI API로 임베딩 생성 (길이 제한 적용)"""
    try:
        if not text: return None
        text = text.replace("\n", " ")
        
        # 👇 [핵심 수정] 너무 긴 텍스트는 잘라냅니다.
        # OpenAI max token은 8192개입니다. 안전하게 8192글자로 제한합니다.
        if len(text) > 5000:
            text = text[:5000]

        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"💥 임베딩 실패: {e}")
        return None

def import_news():
    print("📰 뉴스 데이터 적재 및 임베딩 생성 시작... (시간이 좀 걸립니다)")
    
    try:
        df = pd.read_csv('news_data_20251203_1625.csv')
    except FileNotFoundError:
        print("❌ 뉴스 CSV 파일을 찾을 수 없습니다.")
        return

    news_list = []
    total = len(df)

    for idx, row in df.iterrows():
        impacted_ticker = str(row['impacted_ticker'])
        if len(impacted_ticker) > 500:
            impacted_ticker = impacted_ticker[:500]

        vector = get_embedding(row['body'])
        
        news = HistoricalNews(
            news_collection_date=row['news_collection_date'],
            title=row['title'],
            body=row['body'],
            url=row['url'],
            impacted_ticker=impacted_ticker,
            body_embedding_vector=vector
        )
        news_list.append(news)

        if (idx + 1) % 10 == 0:
            print(f"   ... {idx + 1}/{total} 처리 중")

    HistoricalNews.objects.bulk_create(news_list)
    print(f"✅ 뉴스 {len(news_list)}건 저장 및 임베딩 완료!")

def import_stock():
    print("\n📈 주식 데이터 적재 시작...")
    try:
        df = pd.read_csv('stock_data_20251203_1625.csv')
    except FileNotFoundError:
        print("❌ 주식 CSV 파일을 찾을 수 없습니다.")
        return

    df['ticker'] = df['ticker'].astype(str).str.zfill(6)
    df.drop_duplicates(subset=['ticker', 'date'], keep='first', inplace=True)

    stock_list = []
    print(f"📊 처리할 주식 데이터: {len(df)}건")
    
    for _, row in df.iterrows():
        stock = StockDailyPrice(
            symbol=row['ticker'],
            trade_date=row['date'],
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume']
        )
        stock_list.append(stock)

    StockDailyPrice.objects.bulk_create(stock_list, ignore_conflicts=True)
    print(f"✅ 주식 데이터 저장 완료!")

if __name__ == '__main__':
    # DB 초기화 후 새로 저장하는 코드
    print("🧹 기존 데이터를 초기화합니다...")
    HistoricalNews.objects.all().delete()
    StockDailyPrice.objects.all().delete()
    
    import_news()
    import_stock()