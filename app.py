# =====================================
# YouTube Converter
# app.py
#
# FFmpeg単体テスト 最小構成版
# =====================================

from flask import Flask, render_template
from pathlib import Path
import subprocess
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
# 設定
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

print("==========================================", flush=True)


# =====================================
# Routes登録
# =====================================

print(
    "[APP] Registering routes",
    flush=True
)


# -------------------------------------
# index
# -------------------------------------

print(
    "[APP] register_index START",
    flush=True
)

register_index(app)

print(
    "[APP] register_index OK",
    flush=True
)


# -------------------------------------
# files
# -------------------------------------

print(
    "[APP] register_files START",
    flush=True
)

register_files(app)

print(
    "[APP] register_files OK",
    flush=True
)


# -------------------------------------
# convert
# -------------------------------------

print(
    "[APP] register_convert START",
    flush=True
)

register_convert(app)

print(
    "[APP] register_convert OK",
    flush=True
)


# -------------------------------------
# video-info
# -------------------------------------

print(
    "[APP] register_video_info START",
    flush=True
)

register_video_info(app)

print(
    "[APP] register_video_info OK",
    flush=True
)


# -------------------------------------
# check
# -------------------------------------

print(
    "[APP] register_check START",
    flush=True
)

register_check(app)

print(
    "[APP] register_check OK",
    flush=True
)


# -------------------------------------
# Gemini
# -------------------------------------

print(
    "[APP] register_gemini START",
    flush=True
)

register_gemini(app)

print(
    "[APP] register_gemini OK",
    flush=True
)


# -------------------------------------
# subtitle Blueprint
# -------------------------------------

print(
    "[APP] subtitle_bp register START",
    flush=True
)

app.register_blueprint(
    subtitle_bp
)

print(
    "[APP] subtitle_bp register OK",
    flush=True
)


# -------------------------------------
# completed files
# -------------------------------------

print(
    "[APP] register_completed_files START",
    flush=True
)

register_completed_files(app)

print(
    "[APP] register_completed_files OK",
    flush=True
)


# =====================================
# /test
#
# 単体テスト画面
# =====================================

@app.route("/test")
def test_page():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] /test START",
        flush=True
    )

    print(
        "[APP] test.html を表示します",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return render_template(
        "test.html"
    )


# =====================================
# FFmpeg単体テスト
#
# 重要:
#
# ここでは字幕処理を一切しない。
#
# 動作:
#
# ブラウザ
#   ↓
# POST
#   ↓
# MP4存在確認
#   ↓
# FFmpeg起動
#   ↓
# wait()
#   ↓
# FFmpeg終了
#   ↓
# ブラウザへ結果
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] /subtitle-test/ffmpeg START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    # =====================================
    # STEP 1
    # MP4パス
    # =====================================

    print(
        "[APP] STEP 1: MP4パス確認",
        flush=True
    )

    input_path = (
        Path(DOWNLOAD_DIR)
        / "test.mp4"
    )

    print(
        f"[APP] input_path: {input_path}",
        flush=True
    )


    # =====================================
    # STEP 2
    # MP4存在確認
    # =====================================

    print(
        "[APP] STEP 2: MP4存在確認 START",
        flush=True
    )

    exists = input_path.exists()

    print(
        f"[APP] MP4 exists: {exists}",
        flush=True
    )

    if not exists:

        print(
            "[APP] MP4が存在しません",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return (
            "FFmpegテスト失敗\n\n"
            "入力ファイルが存在しません:\n"
            f"{input_path}",
            500
        )


    # =====================================
    # STEP 3
    # ファイルサイズ確認
    # =====================================

    try:

        file_size = (
            input_path.stat().st_size
        )

        print(
            f"[APP] MP4 size: {file_size} bytes",
            flush=True
        )

    except Exception as error:

        print(
            "[APP] MP4サイズ取得失敗",
            flush=True
        )

        print(
            f"[APP] ERROR: {error}",
            flush=True
        )


    # =====================================
    # STEP 4
    # FFmpegパス
    # =====================================

    print(
        "[APP] STEP 3: FFmpegパス確認",
        flush=True
    )

    ffmpeg_path = "/usr/bin/ffmpeg"

    print(
        f"[APP] ffmpeg_path: {ffmpeg_path}",
        flush=True
    )


    # =====================================
    # STEP 5
    # 出力ファイル
    #
    # 字幕なし
    # 単純コピー
    # =====================================

    output_path = (
        Path(DOWNLOAD_DIR)
        / "test_ffmpeg_output.mp4"
    )

    print(
        f"[APP] output_path: {output_path}",
        flush=True
    )


    # =====================================
    # STEP 6
    # FFmpegコマンド
    #
    # ここでは映像変換すらしない。
    #
    # -c copy
    #
    # つまりMP4をそのまま
    # 別ファイルへコピーするだけ。
    #
    # 目的:
    #
    # 「FFmpegを起動して終了を待つ」
    #
    # だけを確認する。
    # =====================================

    command = [
        ffmpeg_path,
        "-y",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-c",
        "copy",
        str(output_path),
    ]


    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] STEP 4: FFmpeg START",
        flush=True
    )

    print(
        "[APP] FFmpeg command:",
        flush=True
    )

    print(
        " ".join(command),
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    # =====================================
    # STEP 7
    # FFmpeg起動
    #
    # ここが重要。
    #
    # FFmpegはこの1回だけ起動する。
    # =====================================

    try:

        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

    except Exception as error:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] FFmpeg起動 FAILED",
            flush=True
        )

        print(
            f"[APP] ERROR TYPE: "
            f"{type(error).__name__}",
            flush=True
        )

        print(
            f"[APP] ERROR: {error}",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return (
            "FFmpeg起動失敗\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
            500
        )


    print(
        f"[APP] FFmpeg PID: {process.pid}",
        flush=True
    )

    print(
        "[APP] FFmpeg WAIT START",
        flush=True
    )


    # =====================================
    # STEP 8
    # FFmpeg終了待ち
    #
    # timeoutなし。
    #
    # まず純粋に
    # FFmpegが終了するかだけを見る。
    # =====================================

    try:

        stderr_data, _ = process.communicate()

        returncode = process.returncode

    except Exception as error:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] FFmpeg WAIT FAILED",
            flush=True
        )

        print(
            f"[APP] ERROR TYPE: "
            f"{type(error).__name__}",
            flush=True
        )

        print(
            f"[APP] ERROR: {error}",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return (
            "FFmpeg待機失敗\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
            500
        )


    # =====================================
    # STEP 9
    # FFmpeg終了
    # =====================================

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] FFmpeg FINISHED",
        flush=True
    )

    print(
        f"[APP] returncode: {returncode}",
        flush=True
    )


    if stderr_data:

        print(
            "[APP] FFmpeg stderr:",
            flush=True
        )

        print(
            stderr_data,
            flush=True
        )


    # =====================================
    # STEP 10
    # 終了結果
    # =====================================

    if returncode == 0:

        output_exists = (
            output_path.exists()
        )

        print(
            f"[APP] output exists: "
            f"{output_exists}",
            flush=True
        )

        if output_exists:

            try:

                output_size = (
                    output_path.stat().st_size
                )

                print(
                    f"[APP] output size: "
                    f"{output_size} bytes",
                    flush=True
                )

            except Exception:
                pass


        print(
            "[APP] ブラウザへ「FFmpeg終了」を返します",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return (
            "【字幕FFmpegテスト完了】\n\n"
            "FFmpeg終了",
            200
        )


    # =====================================
    # FFmpeg異常終了
    # =====================================

    print(
        "[APP] FFmpeg異常終了",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return (
        "【字幕FFmpegテスト失敗】\n\n"
        "FFmpegが異常終了しました。\n\n"
        f"returncode: {returncode}\n\n"
        f"{stderr_data}",
        500
    )


# =====================================
# Routes確認
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] Registered routes",
    flush=True
)

print(
    "==========================================",
    flush=True
)


for rule in app.url_map.iter_rules():

    print(
        f"[APP] {rule} -> {rule.endpoint}",
        flush=True
    )


# =====================================
# 起動完了
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] app.py READY",
    flush=True
)

print(
    "[APP] FFmpegはまだ実行していません",
    flush=True
)

print(
    "==========================================",
    flush=True
)


# =====================================
# Flask起動
# =====================================

if __name__ == "__main__":

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] Flask START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
