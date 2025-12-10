FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# --------------------------------------------------------
# 1. 무거운 라이브러리 먼저 설치 (Layer Caching 활용)
# --------------------------------------------------------
# requirements-heavy.txt 파일이 변경되지 않는 한, 이 단계는
# 다음 빌드부터 캐시되어(Using cache) 즉시 넘어갑니다.
COPY requirements-heavy.txt .
RUN pip install --no-cache-dir -r requirements-heavy.txt

# --------------------------------------------------------
# 2. 자주 바뀌는 라이브러리 설치
# --------------------------------------------------------
# requirements.txt만 수정하면 여기부터만 새로 설치합니다.
# 위에서 깐 torch 등은 다시 받지 않습니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------------
# 3. 소스 코드 복사 및 실행
# --------------------------------------------------------
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]