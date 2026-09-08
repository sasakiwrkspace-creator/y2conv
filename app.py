# =====================================
# YouTube Converter
# app.py
#
# FFmpeg字幕テスト切り分け版
# =====================================

import os
import traceback
from pathlib import Path

from flask import Flask, render_template

import config

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
# 設定
# =====================================

BASE_DIR = config.BASE_DIR
DOWNLOAD_DIR = config.DOWNLOAD_DIR


print("==========================================", flush=True)
print("[APP] app.py START", flush=True)
print("==========================================", flush=True)

print("[APP] BASE_DIR:", BASE_DIR, flush=True)
print("[APP] DOWNLOAD_DIR:", DOWNLOAD_DIR, flush=True)


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
# video-info
# -------------------------------------

print("[APP] register_video_info START", flush=True)

register_video_info(app)

print("[APP] register_video_info OK", flush=True)


# -------------------------------------
# check
# -------------------------------------

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
# subtitle blueprint
# -------------------------------------

print("[APP] subtitle_bp register START", flush=True)

app.register_blueprint(subtitle_bp)

print("[APP] subtitle_bp register OK", flush=True)


# -------------------------------------
# completed files
# -------------------------------------

print("[APP] register_completed_files START", flush=True)

register_completed_files(app)

print("[APP] register_completed_files OK", flush=True)


# =====================================
# /test
# =====================================

@app.route("/test")
def test_page():

    print("==========================================", flush=True)
    print("[APP] /test START", flush=True)

    return render_template("test.html")


# =====================================
# FFmpeg字幕テスト
#
# 重要:
#
# このroute以外では
# subtitle_test_ffmpeg.pyを呼ばない。
#
# ボタン
#   ↓
# POST
#   ↓
# このroute
#   ↓
# MP4確認
#   ↓
# Python
#   ↓
# FFmpeg 1回
#   ↓
# FFmpeg終了待ち
#   ↓
# ブラウザへ結果
#
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    print("==========================================", flush=True)
    print("[APP] /subtitle-test/ffmpeg START", flush=True)
    print("==========================================", flush=True)

    try:

        # =====================================
        # パス
        # =====================================

        input_path = Path(
            DOWNLOAD_DIR
        ) / "test.mp4"

        output_path = Path(
            DOWNLOAD_DIR
        ) / "test_embed.mp4"


        print(
            "[APP] 入力ファイル:",
            input_path,
            flush=True
        )

        print(
            "[APP] 出力ファイル:",
            output_path,
            flush=True
        )


        # =====================================
        # MP4存在確認
        # =====================================

        print(
            "[APP] MP4存在確認 START",
            flush=True
        )

        if not input_path.exists():

            raise FileNotFoundError(
                f"入力ファイルが存在しません: {input_path}"
            )


        if not input_path.is_file():

            raise FileNotFoundError(
                f"入力パスがファイルではありません: {input_path}"
            )


        input_size = input_path.stat().st_size


        print(
            "[APP] MP4存在確認 OK",
            flush=True
        )

        print(
            f"[APP] 入力サイズ: {input_size} bytes",
            flush=True
        )


        # =====================================
        # 出力ファイル削除
        #
        # 前回のファイルを残さない。
        # =====================================

        if output_path.exists():

            print(
                "[APP] 前回のtest_embed.mp4を削除",
                flush=True
            )

            output_path.unlink()


        # =====================================
        # subtitle_test_ffmpeg.py
        # =====================================

        print(
            "[APP] subtitle_test_ffmpeg import START",
            flush=True
        )

        from subtitle_test_ffmpeg import (
            run_ffmpeg_subtitle_test
        )

        print(
            "[APP] subtitle_test_ffmpeg import OK",
            flush=True
        )


        # =====================================
        # FFmpeg開始
        #
        # ここで1回だけ呼ぶ。
        # =====================================

        print("==========================================", flush=True)
        print("[APP] FFmpeg START", flush=True)
        print("==========================================", flush=True)

        result = run_ffmpeg_subtitle_test(
            input_path=str(input_path),
            output_path=str(output_path)
        )

        print("==========================================", flush=True)
        print("[APP] FFmpeg RETURN", flush=True)
        print("==========================================", flush=True)

        print(
            "[APP] result:",
            result,
            flush=True
        )


        # =====================================
        # 出力確認
        # =====================================

        print(
            "[APP] 出力ファイル確認 START",
            flush=True
        )


        if not output_path.exists():

            raise FileNotFoundError(
                "FFmpegは終了しましたが、"
                f"出力ファイルが存在しません: {output_path}"
            )


        if not output_path.is_file():

            raise FileNotFoundError(
                "出力パスがファイルではありません: "
                f"{output_path}"
            )


        output_size = output_path.stat().st_size


        print(
            "[APP] 出力ファイル確認 OK",
            flush=True
        )

        print(
            f"[APP] 出力サイズ: {output_size} bytes",
            flush=True
        )


        # =====================================
        # 成功
        # =====================================

        message = (
            "【字幕FFmpegテスト完了】\n\n"
            "FFmpeg終了\n\n"
            f"入力ファイル:\n"
            f"{input_path}\n\n"
            f"入力サイズ:\n"
            f"{input_size} bytes\n\n"
            f"出力ファイル:\n"
            f"{output_path}\n\n"
            f"出力サイズ:\n"
            f"{output_size} bytes"
        )


        print("==========================================", flush=True)
        print("[APP] /subtitle-test/ffmpeg SUCCESS", flush=True)
        print("==========================================", flush=True)


        return (
            message,
            200,
            {
                "Content-Type": "text/plain; charset=utf-8"
            }
        )


    # =====================================
    # エラー
    # =====================================

    except Exception as error:

        print("==========================================", flush=True)
        print("[APP] /subtitle-test/ffmpeg FAILED", flush=True)
        print("==========================================", flush=True)

        print(
            "[APP] ERROR TYPE:",
            type(error).__name__,
            flush=True
        )

        print(
            "[APP] ERROR:",
            str(error),
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


        message = (
            "【字幕FFmpegテスト失敗】\n\n"
            "字幕FFmpegテストに失敗しました。\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}\n\n"
            "サーバーログにもTracebackを出力しました。"
        )


        return (
            message,
            500,
            {
                "Content-Type": "text/plain; charset=utf-8"
            }
        )


# =====================================
# Routes確認
# =====================================

print("==========================================", flush=True)
print("[APP] Registered routes", flush=True)
print("==========================================", flush=True)


for rule in app.url_map.iter_rules():

    print(
        rule,
        "->",
        rule.endpoint,
        flush=True
    )


print("==========================================", flush=True)


# =====================================
# READY
# =====================================

print("==========================================", flush=True)
print("[APP] app.py READY", flush=True)
print("[APP] FFmpegはまだ実行していません", flush=True)
print("==========================================", flush=True)


# =====================================
# 起動
# =====================================

if __name__ == "__main__":

    print(
        "[APP] Starting Flask server",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
