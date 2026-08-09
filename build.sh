#!/usr/bin/env bash

echo "##########################################"
echo "### BUILD.SH TEST START ###"
echo "##########################################"

pwd
ls -la

echo "##########################################"
echo "### BUILD.SH CONTENT TEST ###"
echo "##########################################"

echo "Deno version"
deno --version || true

echo "yt-dlp version"
python -m yt_dlp --version || true

echo "yt-dlp-ejs"
pip show yt-dlp-ejs || true

echo "##########################################"
echo "### BUILD.SH TEST END ###"
echo "##########################################"

set -e

pip install -r requirements.txt
