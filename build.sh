#!/usr/bin/env bash

set -e

echo "=========================================="
echo "Render build開始"
echo "=========================================="

echo "Python dependencies install"

pip install -r requirements.txt


echo "=========================================="
echo "Deno install"
echo "=========================================="

curl -fsSL https://deno.land/install.sh | sh


echo "=========================================="
echo "Deno PATH設定"
echo "=========================================="

export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"


echo "Deno version"

deno --version


echo "=========================================="
echo "FFmpeg確認"
echo "=========================================="

ffmpeg -version


echo "=========================================="
echo "yt-dlp確認"
echo "=========================================="

python -m yt_dlp --version


echo "=========================================="
echo "yt-dlp-ejs確認"
echo "=========================================="

pip show yt-dlp-ejs


echo "=========================================="
echo "Build完了"
echo "=========================================="

