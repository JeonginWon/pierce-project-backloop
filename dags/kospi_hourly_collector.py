from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Airflow가 dags 폴더의 모듈을 못 찾을 경우를 대비해 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock_collector import collect_data
from db_writer import save_to_db

def collect_and_save():
    """수집 후 DB 저장 파이프라인"""
    # 1. 데이터 수집
    data_list = collect_data()
    
    if not data_list:
        print("❌ 수집된 데이터가 없습니다.")
        return

    # 2. DB 저장
    saved, updated = save_to_db(data_list)
    print(f"🎉 최종 완료: 신규 {saved}건 / 업데이트 {updated}건")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 26),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'kospi_hourly_collector',
    default_args=default_args,
    description='코스피 1시간봉 수집 및 저장',
    schedule_interval='0 9-16 * * 1-5', # (추천) 평일 9시~16시 매시 정각 실행
    catchup=False,
    tags=['stock', 'kospi'],
)

task = PythonOperator(
    task_id='collect_hourly_data',
    python_callable=collect_and_save,
    dag=dag,
)