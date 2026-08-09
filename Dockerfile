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
        unzip \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Deno
# ==========================================

RUN curl -fsSL https://deno.land/install.sh | sh

ENV DENO_INSTALL=/root/.deno
ENV PATH=/root/.deno/bin:$PATH

# ==========================================
# アプリ
# ==========================================

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ==========================================
# 環境確認
# ==========================================

RUN echo "==========================================" && \
    echo "FFmpeg" && \
    ffmpeg -version && \
    echo "==========================================" && \
    echo "Deno" && \
    deno --version && \
    echo "==========================================" && \
    echo "Python" && \
    python --version && \
    echo "==========================================" && \
    echo "yt-dlp" && \
    python -m yt_dlp --version && \
    echo "=========================================="

# ==========================================
# Render起動
# ==========================================

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]
```
