from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook

from datetime import datetime, timedelta
import requests
import os

# ===== 환경 변수 =====
appkey = Variable.get("app_key")
appsecret = Variable.get("app_secret")

URL_BASE = "https://openapivts.koreainvestment.com:29443"
PRICE_PATH = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

TOKEN_PATH = "/opt/airflow/data/access_token.txt"
POSTGRES_CONN_ID = "stock_postgres"

STOCK_CODES = ["005930", "000660"]  # 원하면 종목 더 추가 가능

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 11, 20),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

dag = DAG(
    dag_id="hourly_stock_to_postgres",
    default_args=default_args,
    description="Fetch stock prices hourly and save to Postgres",
    schedule_interval="0 9-18 * * 1-5",  # 09:00~18:00, 평일 매시간 실행
)


def read_token():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError("Access token file not found")
    with open(TOKEN_PATH, "r") as f:
        token = f.read().strip()
    return token


def fetch_and_store_stock_data(**context):
    access_token = read_token()

    today = datetime.today().strftime("%Y%m%d")

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appKey": appkey,
        "appSecret": appsecret,
        "tr_id": "FHKST03010100",  # 기간별 일자데이터
        "custtype": "P",
    }

    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    url = f"{URL_BASE}{PRICE_PATH}"

    for code in STOCK_CODES:
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": code,
            "FID_INPUT_DATE_1": today,
            "FID_INPUT_DATE_2": today,
            "FID_PERIOD_DIV_CODE": "D",
            "FID_ORG_ADJ_PRC": "1",
        }

        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            print(f"[{code}] API error: {res.text}")
            continue

        data = res.json()
        rows = data.get("output2", [])

        if not rows:
            print(f"[{code}] No price data")
            continue

        for row in rows:
            trade_date = datetime.strptime(row["stck_bsop_date"], "%Y%m%d").date()

            sql = """
            INSERT INTO stock_daily_prices
                (symbol, trade_date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, trade_date) DO UPDATE
            SET open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
            """

            hook.run(
                sql,
                parameters=(
                    code,
                    trade_date,
                    float(row["stck_oprc"]),
                    float(row["stck_hgpr"]),
                    float(row["stck_lwpr"]),
                    float(row["stck_clpr"]),
                    float(row["acml_vol"]),
                ),
            )

        print(f"[{code}] 저장 완료")


fetch_and_store_task = PythonOperator(
    task_id="fetch_and_store_stock_data",
    python_callable=fetch_and_store_stock_data,
    provide_context=True,
    dag=dag,
)
