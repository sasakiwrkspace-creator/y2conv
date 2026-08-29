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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# ==========================================================
# Deno
#
# yt-dlp の JavaScript challenge 対策
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
# 起動前確認
#
# ここで以下を確認する
# - Python
# - yt-dlp
# - yt-dlp-ejs
# - Deno
# - FFmpeg
# - ファイル配置
# ==========================================================

CMD ["sh", "-c", "\
echo '==========================================' && \
echo 'ENVIRONMENT' && \
echo '==========================================' && \
python --version && \
echo '' && \
echo '------------------------------------------' && \
echo 'yt-dlp:' && \
yt-dlp --version && \
echo '' && \
echo 'yt-dlp-ejs:' && \
pip show yt-dlp-ejs || true && \
echo '' && \
echo '------------------------------------------' && \
echo 'Deno:' && \
/root/.deno/bin/deno --version && \
echo '' && \
echo '------------------------------------------' && \
echo 'FFmpeg:' && \
ffmpeg -version | head -n 1 && \
echo '' && \
echo '------------------------------------------' && \
echo 'APP:' && \
pwd && \
ls -la && \
echo '' && \
echo '==========================================' && \
echo 'Starting Gunicorn...' && \
echo '==========================================' && \
gunicorn --bind 0.0.0.0:${PORT:-10000} app:app --timeout 1800 \
"]
