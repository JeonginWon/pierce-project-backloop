from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import json
import psycopg2
import os

# 네이버 API
client_id = "azhP2a68ejoD_N1Bwp55"
client_secret = "I9LYuloz92"

def getRequestUrl(url):
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            return response.read().decode('utf-8')
    except Exception as e:
        print("[ERROR]", e)
        return None


def getNaverSearch(node, keyword, start, display):
    base = "https://openapi.naver.com/v1/search"
    node = f"/{node}.json"
    params = f"?query={urllib.parse.quote(keyword)}&start={start}&display={display}"
    url = base + node + params

    result = getRequestUrl(url)
    return json.loads(result) if result else None


def parse_item(post, cnt):
    pubdate = datetime.strptime(post['pubDate'], "%a, %d %b %Y %H:%M:%S +0900")
    pubdate = pubdate.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "title": post["title"],
        "description": post["description"],
        "org_link": post["originallink"],
        "link": post["link"],
        "pubdate": pubdate
    }


def crawl_and_insert(**context):
    keyword = context["params"].get("keyword", "증시")

    node = "news"
    start = 1
    results = []

    jsonData = getNaverSearch(node, keyword, start, 100)

    while jsonData and jsonData["display"] != 0:
        for idx, item in enumerate(jsonData["items"], start=1):
            parsed = parse_item(item, idx)
            results.append(parsed)

        start = jsonData["start"] + jsonData["display"]
        jsonData = getNaverSearch(node, keyword, start, 100)

    # PostgreSQL 연결
    conn = psycopg2.connect(
        host="postgres",             # docker-compose 기준
        port=5432,
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB")
    )
    cur = conn.cursor()

    # 테이블 생성
    cur.execute("""
        CREATE TABLE IF NOT EXISTS naver_news (
            id SERIAL PRIMARY KEY,
            title TEXT,
            description TEXT,
            org_link TEXT,
            link TEXT,
            pubdate TIMESTAMP
        );
    """)

    # 데이터 INSERT
    for r in results:
        cur.execute("""
            INSERT INTO naver_news (title, description, org_link, link, pubdate)
            VALUES (%s, %s, %s, %s, %s)
        """, (r["title"], r["description"], r["org_link"], r["link"], r["pubdate"]))

    conn.commit()
    cur.close()
    conn.close()

    print(f"[INFO] {len(results)} rows saved into PostgreSQL.")


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}

with DAG(
    dag_id="naver_news_to_postgres",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    params={"keyword": "삼성전자"}
):

    task = PythonOperator(
        task_id="crawl_and_insert_pg",
        python_callable=crawl_and_insert,
        provide_context=True
    )
