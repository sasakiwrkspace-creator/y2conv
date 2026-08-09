#!/usr/bin/env bash

set -e

echo "=========================================="
echo "Render build開始"
echo "=========================================="

echo "Python version"
python --version

echo "=========================================="
echo "Python dependencies install"
echo "=========================================="

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

echo "=========================================="
echo "Deno install"
echo "=========================================="

curl -fsSL https://deno.land/install.sh | sh

export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"

echo "=========================================="
echo "Deno version"
echo "=========================================="

deno --version

echo "=========================================="
echo "yt-dlp version"
echo "=========================================="

python -m yt_dlp --version

echo "=========================================="
echo "yt-dlp-ejs"
echo "=========================================="

python -m pip show yt-dlp-ejs

echo "=========================================="
echo "FFmpeg確認"
echo "=========================================="

ffmpeg -version

echo "=========================================="
echo "Build完了"
echo "=========================================="
