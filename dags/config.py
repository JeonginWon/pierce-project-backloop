import os

# API 설정
MOJITO_API_KEY = os.getenv('MOJITO_API_KEY')
MOJITO_API_SECRET = os.getenv('MOJITO_API_SECRET')
MOJITO_ACC_NO = os.getenv('MOJITO_ACC_NO')

# Django DB 연결
DJANGO_DB = {
    'host': os.getenv('DJANGO_DB_HOST', 'postgres'),
    'database': os.getenv('DJANGO_DB_NAME', 'ragdb'),
    'user': os.getenv('DJANGO_DB_USER', 'admin'),
    'password': os.getenv('DJANGO_DB_PASSWORD', 'admin'),
    'port': 5432
}

# 수집 설정
TIMEFRAME = "60"
MAX_WORKERS = 5
API_DELAY = 0.05