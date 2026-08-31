FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# =====================================
# OSパッケージ
# =====================================

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# =====================================
# Deno
# =====================================
#
# /root/.deno/bin ではなく
# /usr/local/bin に配置する。
#
# Python / Gunicorn / yt-dlp から
# 確実にPATHで見えるようにする。
# =====================================

RUN curl -fsSL https://deno.land/install.sh | sh && \
    cp /root/.deno/bin/deno /usr/local/bin/deno && \
    chmod +x /usr/local/bin/deno


# =====================================
# Deno PATH
# =====================================

ENV PATH="/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"


# =====================================
# Python dependencies
# =====================================

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# =====================================
# アプリケーション
# =====================================

COPY . .


# =====================================
# 環境確認
# =====================================

RUN echo "==========================================" && \
    echo "DOCKER ENVIRONMENT" && \
    echo "==========================================" && \
    echo "Python:" && \
    python --version && \
    echo "------------------------------------------" && \
    echo "Python executable:" && \
    which python && \
    echo "------------------------------------------" && \
    echo "Gunicorn:" && \
    which gunicorn && \
    gunicorn --version && \
    echo "------------------------------------------" && \
    echo "yt-dlp:" && \
    which yt-dlp && \
    yt-dlp --version && \
    echo "------------------------------------------" && \
    echo "yt-dlp-ejs:" && \
    pip show yt-dlp-ejs && \
    echo "------------------------------------------" && \
    echo "Deno:" && \
    which deno && \
    deno --version && \
    echo "------------------------------------------" && \
    echo "FFmpeg:" && \
    which ffmpeg && \
    ffmpeg -version | head -n 1 && \
    echo "=========================================="


# =====================================
# Render
# =====================================

ENV PORT=10000


# =====================================
# 起動
# =====================================

CMD ["sh", "-c", "echo '==========================================' && echo 'Starting Gunicorn...' && echo 'PATH:' && echo \"$PATH\" && echo 'Deno:' && which deno && deno --version && echo '==========================================' && gunicorn --bind 0.0.0.0:${PORT:-10000} --timeout 1800 app:app"]
