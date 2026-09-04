# =====================================
# YouTube Converter
# app.py
#
# アプリケーションの入口
#
# 役割:
# ・Flaskアプリ起動
# ・各routes登録
# ・設定読み込み
#
# タブ1:
# ・YouTube URL
# ・動画情報取得
# ・MP3 / MP4変換
# ・Job監視
# ・MP3完成後のSRT / Gemini処理
#
# タブ2:
# ・ファイル変換
#
# 注意:
# ・converter.js / subtitle.js の処理は
#   このファイルでは行わない。
# =====================================


from flask import Flask

import config

from routes.index import register_index
from routes.files import register_files
from routes.convert import register_convert
from routes.check import register_video_info, register_check
from routes.gemini import register_gemini


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
# Routes登録
# =====================================

print("==========================================")
print("[APP] Registering routes")
print("==========================================")


# -------------------------------------
# index
# -------------------------------------

register_index(app)


# -------------------------------------
# files
# -------------------------------------

register_files(app)


# -------------------------------------
# convert
# -------------------------------------

register_convert(app)


# -------------------------------------
# video-info / check
# -------------------------------------

register_video_info(app)

register_check(app)


# -------------------------------------
# Gemini / SRT
#
# POST /gemini-transcribe
#
# converter.jsからMP3ファイル名を受け取り、
# Geminiで文字起こししてSRTを作成する。
# -------------------------------------

register_gemini(app)


# =====================================
# 登録ルート確認
# =====================================

print("==========================================")
print("[APP] Registered routes")
print("==========================================")


for rule in app.url_map.iter_rules():

    print(
        rule,
        "->",
        rule.endpoint
    )


print("==========================================")


# =====================================
# 起動確認
# =====================================

if __name__ == "__main__":

    print("==========================================")
    print("[APP] YouTube Converter")
    print("==========================================")

    print(
        "[APP] BASE_DIR:",
        BASE_DIR
    )

    print(
        "[APP] DOWNLOAD_DIR:",
        DOWNLOAD_DIR
    )

    print("==========================================")

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
