from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
# import json  <-- json= 파라미터를 쓰면 이 줄은 없어도 됩니다.

# 주소 확인 (서비스 이름: django)
DJANGO_API_URL = "http://django:8000/api/historical-news/"

def send_news_to_django(**context):
    sample_news = [
        {
            "title": "삼성전자, 3분기 실적 발표",
            "body": "삼성전자가 3분기 매출 70조원을 기록하며...",
            "news_collection_date": "2024-10-01",
            "impacted_ticker": "005930"
        },
        {
            "title": "비트코인 급등, 1억 돌파하나",
            "body": "가상화폐 시장이 다시 뜨거워지고 있다...",
            "news_collection_date": "2024-11-20",
            "impacted_ticker": "BTC"
        }
    ]

    # headers 설정도 필요 없습니다. requests가 알아서 합니다.

    for news in sample_news:
        try:
            # 👇 [핵심 수정] data=... 대신 json=news 로 변경!
            response = requests.post(DJANGO_API_URL, json=news)
            
            if response.status_code == 201:
                print(f"✅ 저장 성공: {news['title']}")
            else:
                # 에러 메시지를 더 자세히 보기 위해 response.json() 출력
                print(f"❌ 저장 실패: {news['title']} - {response.text}")
                
        except Exception as e:
            print(f"💥 에러 발생: {e}")

with DAG(
    dag_id='news_ingestion_v2',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['RAG', 'News']
) as dag:

    ingest_task = PythonOperator(
        task_id='send_news',
        python_callable=send_news_to_django
    )