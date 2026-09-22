FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==========================================================
# Application
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
    ca-certificates \
    fontconfig \
    fonts-noto-cjk \
    fonts-noto-cjk-extra && \
    fc-cache -fv && \
    rm -rf /var/lib/apt/lists/*


# ==========================================================
# Japanese fonts check
# ==========================================================

RUN echo "==========================================" && \
    echo "JAPANESE FONT CHECK" && \
    echo "==========================================" && \
    fc-cache -V && \
    echo "------------------------------------------" && \
    fc-list :lang=ja family | sort -u | head -n 50 && \
    echo "------------------------------------------" && \
    fc-match "Noto Sans CJK JP" && \
    fc-match "Noto Serif CJK JP" && \
    echo "=========================================="


# ==========================================================
# Deno
#
# Deno official binary
# ==========================================================

COPY --from=denoland/deno:bin-2.6.4 /deno /usr/local/bin/deno

RUN chmod +x /usr/local/bin/deno


# ==========================================================
# Deno verification
# ==========================================================

RUN echo "==========================================" && \
    echo "DENO CHECK" && \
    echo "==========================================" && \
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
# Final environment check
# ==========================================================

RUN echo "==========================================" && \
    echo "FINAL ENVIRONMENT CHECK" && \
    echo "==========================================" && \
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
