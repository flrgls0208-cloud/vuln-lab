# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# 앱 소스 코드 복사
COPY . /app

# 🌟 [수정 포인트] 파일 업로드(uploads)와 LFI(files)용 폴더 명시적 생성
RUN mkdir -p /app/uploads /app/files

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden.
# 🌟 [주의] requirements.txt에 gunicorn이 반드시 있어야 합니다.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
