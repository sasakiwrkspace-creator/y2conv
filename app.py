# =====================================
# YouTube Converter
# app.py
#
# 今回の調査版
#
# 目的:
# ・Flask起動
# ・/test 表示
# ・FFmpegボタンを押した時だけ
#   subtitle_test_ffmpeg.py の処理を呼ぶ
#
# 重要:
# ・app.py 起動時にはFFmpegを実行しない
# ・FFmpeg実行は POST /subtitle-test/ffmpeg
#   が呼ばれた時だけ
# =====================================


from flask import Flask, render_template


# =====================================
# 設定
# =====================================

import config


# =====================================
# 既存Routes
# =====================================

from routes.index import register_index
from routes.files import register_files
from routes.convert import register_convert
from routes.check import register_video_info, register_check
from routes.gemini import register_gemini
from routes.completed_files import register_completed_files

from routes.subtitle_routes import subtitle_bp


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
# 起動ログ
# =====================================

print("==========================================", flush=True)
print("[APP] app.py START", flush=True)
print("==========================================", flush=True)

print(
    f"[APP] BASE_DIR: {BASE_DIR}",
    flush=True
)

print(
    f"[APP] DOWNLOAD_DIR: {DOWNLOAD_DIR}",
    flush=True
)


# =====================================
# Routes登録
# =====================================

print("==========================================", flush=True)
print("[APP] Registering routes", flush=True)
print("==========================================", flush=True)


# -------------------------------------
# index
# -------------------------------------

print("[APP] register_index START", flush=True)

register_index(app)

print("[APP] register_index OK", flush=True)


# -------------------------------------
# files
# -------------------------------------

print("[APP] register_files START", flush=True)

register_files(app)

print("[APP] register_files OK", flush=True)


# -------------------------------------
# convert
# -------------------------------------

print("[APP] register_convert START", flush=True)

register_convert(app)

print("[APP] register_convert OK", flush=True)


# -------------------------------------
# video-info / check
# -------------------------------------

print("[APP] register_video_info START", flush=True)

register_video_info(app)

print("[APP] register_video_info OK", flush=True)


print("[APP] register_check START", flush=True)

register_check(app)

print("[APP] register_check OK", flush=True)


# -------------------------------------
# Gemini
# -------------------------------------

print("[APP] register_gemini START", flush=True)

register_gemini(app)

print("[APP] register_gemini OK", flush=True)


# -------------------------------------
# subtitle Blueprint
# -------------------------------------

print("[APP] subtitle_bp register START", flush=True)

app.register_blueprint(
    subtitle_bp
)

print("[APP] subtitle_bp register OK", flush=True)


# -------------------------------------
# completed files
# -------------------------------------

print("[APP] register_completed_files START", flush=True)

register_completed_files(app)

print("[APP] register_completed_files OK", flush=True)


# =====================================
# TEST画面
#
# GET /test
#
# ここではFFmpegを絶対に実行しない
# =====================================

@app.route("/test", methods=["GET"])
def test_page():

    print("==========================================", flush=True)
    print("[APP] /test START", flush=True)

    print(
        "[APP] test.html を表示します",
        flush=True
    )

    print("[APP] /test END", flush=True)
    print("==========================================", flush=True)

    return render_template("test.html")


# =====================================
# FFmpegテスト
#
# POST /subtitle-test/ffmpeg
#
# ブラウザのボタンを押した時だけ実行
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    print("==========================================", flush=True)
    print("[APP] /subtitle-test/ffmpeg START", flush=True)
    print("==========================================", flush=True)


    # -------------------------------------
    # この時点で初めて
    # subtitle_test_ffmpeg を読み込む
    #
    # importだけではFFmpegを実行しないことが前提
    # -------------------------------------

    print(
        "[APP] subtitle_test_ffmpeg import START",
        flush=True
    )

    try:

        from subtitle_test_ffmpeg import (
            run_ffmpeg_subtitle_test
        )

    except Exception as error:

        import traceback

        print(
            "[APP] subtitle_test_ffmpeg import FAILED",
            flush=True
        )

        print(
            f"[APP] ERROR TYPE: {type(error).__name__}",
            flush=True
        )

        print(
            f"[APP] ERROR: {error}",
            flush=True
        )

        traceback.print_exc()

        return (
            "FFmpeg処理開始前にエラー\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
            500
        )


    print(
        "[APP] subtitle_test_ffmpeg import OK",
        flush=True
    )


    # -------------------------------------
    # FFmpeg処理開始
    # -------------------------------------

    print("==========================================", flush=True)

    print(
        "[APP] run_ffmpeg_subtitle_test() START",
        flush=True
    )

    print(
        "[APP] ここから先はsubtitle_test_ffmpeg.py",
        flush=True
    )

    print("==========================================", flush=True)


    try:

        output_path = run_ffmpeg_subtitle_test()


    except Exception as error:

        import traceback

        print("==========================================", flush=True)

        print(
            "[APP] run_ffmpeg_subtitle_test() FAILED",
            flush=True
        )

        print(
            f"[APP] ERROR TYPE: {type(error).__name__}",
            flush=True
        )

        print(
            f"[APP] ERROR: {error}",
            flush=True
        )

        print(
            "[APP] TRACEBACK START",
            flush=True
        )

        traceback.print_exc()

        print(
            "[APP] TRACEBACK END",
            flush=True
        )

        print("==========================================", flush=True)


        return (
            "FFmpeg処理失敗\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
            500
        )


    # -------------------------------------
    # FFmpeg処理終了
    # -------------------------------------

    print("==========================================", flush=True)

    print(
        "[APP] run_ffmpeg_subtitle_test() END",
        flush=True
    )

    print(
        f"[APP] output_path: {output_path}",
        flush=True
    )

    print("==========================================", flush=True)


    # -------------------------------------
    # ブラウザへ返す
    # -------------------------------------

    return (
        "【字幕FFmpegテスト完了】\n\n"
        "FFmpeg終了",
        200
    )


# =====================================
# ルート一覧
# =====================================

print("==========================================", flush=True)
print("[APP] Registered routes", flush=True)
print("==========================================", flush=True)


for rule in app.url_map.iter_rules():

    print(
        f"[APP] {rule} -> {rule.endpoint}",
        flush=True
    )


print("==========================================", flush=True)


# =====================================
# app.py 読み込み完了
# =====================================

print("==========================================", flush=True)
print("[APP] app.py READY", flush=True)
print("[APP] FFmpegはまだ実行していません", flush=True)
print("==========================================", flush=True)


# =====================================
# ローカル起動
# =====================================

if __name__ == "__main__":

    print("==========================================", flush=True)
    print("[APP] YouTube Converter", flush=True)
    print("[APP] Flask starting...", flush=True)
    print("==========================================", flush=True)

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
