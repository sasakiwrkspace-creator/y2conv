```dockerfile
FROM python:3.12-slim

# ==========================================
# OSパッケージ
# ==========================================

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# ==========================================
# Deno
# ==========================================

RUN curl -fsSL https://deno.land/install.sh | sh

ENV DENO_INSTALL=/root/.deno
ENV PATH=/root/.deno/bin:$PATH


# ==========================================
# アプリケーション
# ==========================================

WORKDIR /app


# ==========================================
# Python dependencies
# ==========================================

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# ==========================================
# アプリケーションコピー
# ==========================================

COPY . .


# ==========================================
# 環境確認
# ==========================================

RUN echo "==========================================" && \
    echo "FFmpeg VERSION" && \
    ffmpeg -version | head -n 1 && \
    echo "==========================================" && \
    echo "Deno VERSION" && \
    deno --version && \
    echo "==========================================" && \
    echo "Python VERSION" && \
    python --version && \
    echo "==========================================" && \
    echo "yt-dlp VERSION" && \
    python -m yt_dlp --version && \
    echo "==========================================" && \
    echo "yt-dlp-ejs" && \
    pip show yt-dlp-ejs && \
    echo "=========================================="


# ==========================================
# Render起動
# ==========================================

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]
```
