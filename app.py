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
# =====================================

from flask import Flask

import config

from routes.index import register_index
from routes.files import register_files
from routes.convert import register_convert
from routes.check import register_video_info, register_check


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

register_index(app)

register_files(app)

register_convert(app)

register_video_info(app)

register_check(app)


# =====================================
# 登録ルート確認
# =====================================

print("==========================================")
print("[APP] Registered routes")

for rule in app.url_map.iter_rules():

    print(
        rule
    )

print("==========================================")


# =====================================
# 起動確認
# =====================================

if __name__ == "__main__":

    print("==========================================")
    print("YouTube Converter")
    print("==========================================")

    print(
        "BASE_DIR:",
        BASE_DIR
    )

    print(
        "DOWNLOAD_DIR:",
        DOWNLOAD_DIR
    )

    print("==========================================")

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
