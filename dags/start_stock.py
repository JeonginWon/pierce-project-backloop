# 매일 아침 API 토큰 호출 dag

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import requests
import json
import os


# 기본 설정
appkey = Variable.get("app_key")
appsecret = Variable.get("app_secret")
url_base = 'https://openapivts.koreainvestment.com:29443'
path = '/oauth2/tokenP'

TOKEN_PATH = "/opt/airflow/data/access_token.txt"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_token',
    default_args=default_args,
    description='Retrieve an access token from Korea Investment API',
    schedule_interval="55 8 * * 1-5",
)


def get_access_token(**kwargs):
    data = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": appsecret
    }

    res = requests.post(url=f"{url_base}{path}", json=data)

    if res.status_code == 200:
        token_info = res.json()
        access_token = token_info.get('access_token')
        print("Access Token:", access_token)

        # 폴더 자동 생성
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)

        # 토큰 저장
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(access_token)

        # XCom 전달
        kwargs['ti'].xcom_push(key='access_token', value=access_token)

    else:
        raise ValueError(f"Token 발급 실패: {res.status_code}, {res.text}")


get_token_task = PythonOperator(
    task_id='get_access_token',
    python_callable=get_access_token,
    provide_context=True,
    dag=dag,
)
