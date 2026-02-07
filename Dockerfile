# Python 3.9 슬림 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출 (Cloud Run 기본 포트 8080)
EXPOSE 8080

# Streamlit 실행
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]
