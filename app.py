# =====================================
# YouTube Converter
# app.py
#
# アプリケーションの入口
#
# 役割:
# ・Flaskアプリ起動
# ・index.html表示
# ・staticファイル提供
# ・downloadsファイル提供
# =====================================

import os

from flask import Flask, render_template, send_from_directory

import config


# =====================================
# Flask
# =====================================

app = Flask(__name__)


# =====================================
# プロジェクト設定
# =====================================

BASE_DIR = config.BASE_DIR
DOWNLOAD_DIR = config.DOWNLOAD_DIR


# =====================================
# トップページ
# =====================================

@app.route("/")
def index():
    return render_template(
        "index.html"
    )


# =====================================
# downloads
#
# 作成したMP3 / MP4 / SRTを
# ブラウザからダウンロードする
# =====================================

@app.route("/download/<path:filename>")
def download_file(filename):

    return send_from_directory(
        DOWNLOAD_DIR,
        filename,
        as_attachment=True
    )


# =====================================
# 起動確認
# =====================================

@app.route("/health")
def health():

    return {
        "status": "ok"
    }


# =====================================
# アプリ起動
# =====================================

if __name__ == "__main__":

    print("==========================================")
    print("YouTube Converter")
    print("==========================================")
    print("BASE_DIR:", BASE_DIR)
    print("DOWNLOAD_DIR:", DOWNLOAD_DIR)
    print("==========================================")

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
