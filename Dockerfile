FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ==========================================
# OSパッケージ
# ==========================================

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ==========================================
# Deno
# ==========================================

RUN curl -fsSL https://deno.land/install.sh | sh

ENV DENO_DIR="/root/.cache/deno"
ENV PATH="/root/.deno/bin:${PATH}"

# ==========================================
# Python dependencies
# ==========================================

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# アプリ
# ==========================================

COPY . .

# ==========================================
# 起動
# ==========================================

CMD ["sh", "-c", "echo '===== ENVIRONMENT =====' && python --version && pip show yt-dlp && echo '===== DENO =====' && /root/.deno/bin/deno --version && echo '===== FFMPEG =====' && ffmpeg -version | head -n 1 && echo '===== APP =====' && pwd && ls -la && echo '========================' && gunicorn --bind 0.0.0.0:10000 app:app"]
