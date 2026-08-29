FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# ==========================================================
# OSパッケージ
# ==========================================================

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*


# ==========================================================
# Deno
# ==========================================================

RUN curl -fsSL https://deno.land/install.sh | sh

ENV PATH="/root/.deno/bin:${PATH}"


# ==========================================================
# Python dependencies
# ==========================================================

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ==========================================================
# アプリケーション
# ==========================================================

COPY . .


# ==========================================================
# 起動前の環境確認 + Gunicorn
# ==========================================================

CMD ["sh", "-c", "\
echo '==========================================' && \
echo 'DOCKER ENVIRONMENT' && \
echo '==========================================' && \
echo 'Python:' && \
python --version && \
echo '------------------------------------------' && \
echo 'yt-dlp:' && \
pip show yt-dlp && \
echo '------------------------------------------' && \
echo 'yt-dlp-ejs:' && \
pip show yt-dlp-ejs && \
echo '------------------------------------------' && \
echo 'Deno:' && \
/root/.deno/bin/deno --version && \
echo '------------------------------------------' && \
echo 'FFmpeg:' && \
ffmpeg -version | head -n 1 && \
echo '------------------------------------------' && \
echo 'APP:' && \
pwd && \
ls -la && \
echo '==========================================' && \
echo 'Starting Gunicorn...' && \
echo '==========================================' && \
gunicorn --bind 0.0.0.0:${PORT:-10000} app:app --timeout 1800 \
"]
