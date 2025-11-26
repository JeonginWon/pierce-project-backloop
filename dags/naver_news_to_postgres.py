from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import json
import requests
import re

# 네이버 API 설정
CLIENT_ID = "azhP2a68ejoD_N1Bwp55"
CLIENT_SECRET = "I9LYuloz92"

# Django API 주소 (LatestNews 테이블용)
DJANGO_API_URL = "http://django:8000/api/latest-news/"

def clean_html(text):
    """HTML 태그 제거"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    # &quot; 같은 엔티티도 처리해주면 더 좋습니다 (선택)
    return cleantext

def get_request_url(url):
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", CLIENT_ID)
    req.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"[ERROR] API Request Failed: {e}")
        return None

def get_naver_search(keyword, start, display):
    base = "https://openapi.naver.com/v1/search/news.json"
    params = f"?query={urllib.parse.quote(keyword)}&start={start}&display={display}&sort=date"
    url = base + params
    
    result = get_request_url(url)
    return json.loads(result) if result else None

def crawl_and_send_to_django(**context):
    keyword = context["params"].get("keyword", "증시")
    print(f"🔍 검색어: {keyword}")

    display = 100
    start = 1
    
    json_data = get_naver_search(keyword, start, display)
    
    success_count = 0
    fail_count = 0

    if json_data and "items" in json_data:
        for item in json_data["items"]:
            # 1. 날짜 처리
            try:
                raw_date = item['pubDate']
                dt_obj = datetime.strptime(raw_date, "%a, %d %b %Y %H:%M:%S +0900")
                formatted_date = dt_obj.strftime("%Y-%m-%d")
            except:
                formatted_date = datetime.now().strftime("%Y-%m-%d")

            # 2. Payload 생성 (url 추가됨!)
            # originallink가 있으면 그걸 쓰고, 없으면 네이버 링크(link)를 씁니다.
            news_link = item.get("originallink") or item.get("link")

            payload = {
                "title": clean_html(item["title"]),
                "body": clean_html(item["description"]),
                "news_collection_date": formatted_date,
                "url": news_link,  # 👈 [추가] 여기가 핵심입니다!
                "views": 0
            }

            # 3. Django 전송
            try:
                # json=payload 로 보내면 헤더 자동 설정됨
                response = requests.post(DJANGO_API_URL, json=payload)
                
                if response.status_code == 201:
                    success_count += 1
                else:
                    print(f"❌ 저장 실패: {payload['title']} - {response.text}")
                    fail_count += 1
            except Exception as e:
                print(f"💥 전송 에러: {e}")
                fail_count += 1

    print(f"결과: 성공 {success_count}건 / 실패 {fail_count}건")

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="naver_news_to_postgres",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    params={"keyword": "삼성전자"}
) as dag:

    task = PythonOperator(
        task_id="crawl_and_send_news",
        python_callable=crawl_and_send_to_django,
        provide_context=True
    )