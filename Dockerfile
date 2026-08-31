FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==========================================================
# Application directory
# ==========================================================

WORKDIR /app

# ==========================================================
# OS packages
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

ENV DENO_INSTALL=/app/.deno
ENV DENO_PATH=/app/.deno/bin/deno
ENV PATH="/app/.deno/bin:${PATH}"

RUN curl -fsSL https://deno.land/install.sh | sh

# ==========================================================
# Deno verification
# ==========================================================

RUN echo "==========================================" && \
    echo "DENO INSTALL CHECK" && \
    echo "==========================================" && \
    echo "DENO_INSTALL: ${DENO_INSTALL}" && \
    echo "DENO_PATH: ${DENO_PATH}" && \
    echo "PATH: ${PATH}" && \
    echo "------------------------------------------" && \
    ls -la /app/.deno/bin && \
    echo "------------------------------------------" && \
    which deno && \
    deno --version && \
    echo "=========================================="

# ==========================================================
# Python dependencies
# ==========================================================

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================================
# Application
# ==========================================================

COPY . .

# ==========================================================
# Final environment verification
# ==========================================================

RUN echo "==========================================" && \
    echo "FINAL ENVIRONMENT CHECK" && \
    echo "==========================================" && \
    echo "Working directory:" && \
    pwd && \
    echo "------------------------------------------" && \
    echo "Python:" && \
    python --version && \
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
    python -c "import yt_dlp_ejs; print(yt_dlp_ejs.__file__)" && \
    echo "------------------------------------------" && \
    echo "Deno:" && \
    echo "DENO_INSTALL=${DENO_INSTALL}" && \
    echo "DENO_PATH=${DENO_PATH}" && \
    which deno && \
    deno --version && \
    echo "------------------------------------------" && \
    echo "FFmpeg:" && \
    which ffmpeg && \
    ffmpeg -version | head -n 1 && \
    echo "------------------------------------------" && \
    echo "FFprobe:" && \
    which ffprobe && \
    ffprobe -version | head -n 1 && \
    echo "=========================================="

# ==========================================================
# Start
# ==========================================================

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "1800", "app:app"]
