# =====================================
# YouTube Converter
# app.py
#
# FFmpeg単体テスト診断版
#
# 流れ:
#
# ブラウザ
#   ↓
# /subtitle-test/ffmpeg
#   ↓
# Python
#   ↓
# /app/downloads の状態確認
#   ↓
# test.mp4 存在確認
#   ↓
# FFmpegを1回だけ起動
#   ↓
# FFmpeg終了を待つ
#   ↓
# test_embed.mp4確認
#   ↓
# ブラウザへ結果表示
#
# =====================================

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
# subtitle Blueprint
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
# FFmpeg単体テスト
#
# 重要:
#
# このrouteでは最初に
# FFmpegを起動しない。
#
# まずdownloadsの中身を確認する。
#
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    import os
    import subprocess
    import traceback
    from pathlib import Path


    print("==========================================", flush=True)
    print("[APP] /subtitle-test/ffmpeg START", flush=True)
    print("==========================================", flush=True)


    # =====================================
    # STEP 1
    # DOWNLOAD_DIR確認
    # =====================================

    print("[APP] STEP 1: DOWNLOAD_DIR確認", flush=True)

    download_dir = Path(DOWNLOAD_DIR)

    print(
        f"[APP] DOWNLOAD_DIR = {download_dir}",
        flush=True
    )

    print(
        f"[APP] DOWNLOAD_DIR absolute = "
        f"{download_dir.resolve()}",
        flush=True
    )

    print(
        f"[APP] DOWNLOAD_DIR exists = "
        f"{download_dir.exists()}",
        flush=True
    )

    print(
        f"[APP] DOWNLOAD_DIR is_dir = "
        f"{download_dir.is_dir()}",
        flush=True
    )


    # =====================================
    # STEP 2
    # downloads一覧
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 2: downloads一覧", flush=True)
    print("==========================================", flush=True)


    files = []

    try:

        if download_dir.exists() and download_dir.is_dir():

            for item in sorted(
                download_dir.iterdir(),
                key=lambda x: x.name
            ):

                try:

                    if item.is_file():

                        size = item.stat().st_size

                        line = (
                            f"FILE: {item.name} "
                            f"({size} bytes)"
                        )

                    elif item.is_dir():

                        line = (
                            f"DIR : {item.name}"
                        )

                    else:

                        line = (
                            f"OTHER: {item.name}"
                        )

                    files.append(line)

                    print(
                        f"[APP] {line}",
                        flush=True
                    )

                except Exception as item_error:

                    line = (
                        f"ERROR: {item.name} "
                        f"({item_error})"
                    )

                    files.append(line)

                    print(
                        f"[APP] {line}",
                        flush=True
                    )

        else:

            files.append(
                "downloads directory does not exist"
            )

            print(
                "[APP] downloads directory does not exist",
                flush=True
            )

    except Exception as list_error:

        files.append(
            f"一覧取得エラー: {list_error}"
        )

        print(
            f"[APP] downloads一覧取得エラー: "
            f"{list_error}",
            flush=True
        )


    # =====================================
    # STEP 3
    # test.mp4確認
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 3: test.mp4存在確認", flush=True)
    print("==========================================", flush=True)


    input_path = (
        download_dir / "test.mp4"
    )


    print(
        f"[APP] input_path = {input_path}",
        flush=True
    )

    print(
        f"[APP] input absolute = "
        f"{input_path.resolve()}",
        flush=True
    )

    print(
        f"[APP] input exists = "
        f"{input_path.exists()}",
        flush=True
    )

    print(
        f"[APP] input is_file = "
        f"{input_path.is_file()}",
        flush=True
    )


    # =====================================
    # test.mp4がない場合
    #
    # FFmpegは絶対に起動しない
    # =====================================

    if not input_path.exists():

        print("==========================================", flush=True)
        print(
            "[APP] test.mp4 NOT FOUND",
            flush=True
        )
        print(
            "[APP] FFmpegは起動しません",
            flush=True
        )
        print("==========================================", flush=True)


        browser_text = (
            "【字幕FFmpegテスト診断】\n\n"
            "FFmpegは起動していません。\n\n"
            "理由:\n"
            "test.mp4 が存在しません。\n\n"
            f"確認パス:\n"
            f"{input_path.resolve()}\n\n"
            "downloadsの中身:\n"
        )

        if files:

            browser_text += "\n".join(files)

        else:

            browser_text += "(空です)"


        return browser_text, 400


    # =====================================
    # STEP 4
    # MP4サイズ確認
    # =====================================

    try:

        input_size = (
            input_path.stat().st_size
        )

    except Exception as size_error:

        print(
            f"[APP] test.mp4サイズ取得失敗: "
            f"{size_error}",
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "test.mp4のサイズ取得に失敗しました。\n\n"
            f"ERROR:\n{size_error}",
            500
        )


    print(
        f"[APP] test.mp4 size = "
        f"{input_size} bytes",
        flush=True
    )


    # =====================================
    # STEP 5
    # 出力先
    #
    # 今後は必ず test_embed.mp4
    # =====================================

    output_path = (
        download_dir / "test_embed.mp4"
    )


    print("==========================================", flush=True)
    print("[APP] STEP 5: 出力先", flush=True)
    print("==========================================", flush=True)

    print(
        f"[APP] output_path = {output_path}",
        flush=True
    )


    # =====================================
    # STEP 6
    # 既存output削除
    #
    # FFmpegを1回だけ起動するため、
    # 前回のファイルを残さない。
    # =====================================

    if output_path.exists():

        print(
            "[APP] 既存test_embed.mp4を削除",
            flush=True
        )

        try:

            output_path.unlink()

            print(
                "[APP] 既存test_embed.mp4削除OK",
                flush=True
            )

        except Exception as delete_error:

            print(
                "[APP] 既存output削除失敗:",
                delete_error,
                flush=True
            )

            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "既存のtest_embed.mp4を削除できませんでした。\n\n"
                f"ERROR:\n{delete_error}",
                500
            )


    # =====================================
    # STEP 7
    # FFmpegコマンド
    #
    # ここで初めてFFmpegを起動する。
    #
    # 字幕処理はまだ戻さない。
    #
    # 今回は「FFmpegが普通に動くか」
    # だけを確認する。
    #
    # scaleのみ。
    # subtitlesフィルターなし。
    # =====================================

    command = [
        "/usr/bin/ffmpeg",

        "-y",
        "-nostdin",
        "-hide_banner",

        "-loglevel",
        "error",

        "-i",
        str(input_path),

        "-vf",
        "scale=640:360",

        "-c:v",
        "libx264",

        "-threads",
        "1",

        "-preset",
        "ultrafast",

        "-crf",
        "28",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-movflags",
        "+faststart",

        str(output_path),
    ]


    print("==========================================", flush=True)
    print("[APP] STEP 6: FFmpeg開始", flush=True)
    print("==========================================", flush=True)

    print(
        "[APP] FFmpegはここで1回だけ起動します",
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


    # =====================================
    # STEP 8
    # FFmpeg 1回だけ実行
    # =====================================

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
            check=False
        )


    except subprocess.TimeoutExpired:

        print(
            "[APP] FFmpeg TIMEOUT",
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpegが120秒以内に終了しませんでした。",
            500
        )


    except Exception as ffmpeg_start_error:

        print(
            "[APP] FFmpeg起動例外:",
            ffmpeg_start_error,
            flush=True
        )

        traceback.print_exc()

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpeg起動時に例外が発生しました。\n\n"
            f"ERROR TYPE:\n"
            f"{type(ffmpeg_start_error).__name__}\n\n"
            f"ERROR:\n"
            f"{ffmpeg_start_error}",
            500
        )


    # =====================================
    # STEP 9
    # FFmpeg終了確認
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 7: FFmpeg終了", flush=True)
    print("==========================================", flush=True)

    print(
        f"[APP] FFmpeg returncode: "
        f"{result.returncode}",
        flush=True
    )


    if result.stdout:

        print(
            "[APP] FFmpeg stdout:",
            flush=True
        )

        print(
            result.stdout,
            flush=True
        )


    if result.stderr:

        print(
            "[APP] FFmpeg stderr:",
            flush=True
        )

        print(
            result.stderr,
            flush=True
        )


    # =====================================
    # STEP 10
    # returncode確認
    # =====================================

    if result.returncode != 0:

        print(
            "[APP] FFmpeg FAILED",
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpegが終了しましたが、成功コードではありません。\n\n"
            f"returncode:\n"
            f"{result.returncode}\n\n"
            f"stderr:\n"
            f"{result.stderr}",
            500
        )


    # =====================================
    # STEP 11
    # output確認
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 8: 出力ファイル確認", flush=True)
    print("==========================================", flush=True)


    print(
        f"[APP] output exists: "
        f"{output_path.exists()}",
        flush=True
    )


    if not output_path.exists():

        print(
            "[APP] FFmpeg成功だがoutputがありません",
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpegはreturncode=0で終了しましたが、"
            "test_embed.mp4が作成されていません。\n\n"
            f"出力予定:\n"
            f"{output_path}",
            500
        )


    try:

        output_size = (
            output_path.stat().st_size
        )

    except Exception as output_size_error:

        print(
            "[APP] outputサイズ取得失敗:",
            output_size_error,
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "test_embed.mp4は存在しますが、"
            "サイズを取得できませんでした。\n\n"
            f"ERROR:\n{output_size_error}",
            500
        )


    print(
        f"[APP] output size: "
        f"{output_size} bytes",
        flush=True
    )


    # =====================================
    # STEP 12
    # 成功
    # =====================================

    print("==========================================", flush=True)
    print("[APP] FFmpeg TEST SUCCESS", flush=True)
    print("==========================================", flush=True)


    return (
        "【字幕FFmpegテスト完了】\n\n"
        "FFmpeg終了\n\n"
        f"入力ファイル:\n"
        f"{input_path.resolve()}\n\n"
        f"入力サイズ:\n"
        f"{input_size} bytes\n\n"
        f"出力ファイル:\n"
        f"{output_path.resolve()}\n\n"
        f"出力サイズ:\n"
        f"{output_size} bytes",
        200
    )


# =====================================
# 登録ルート確認
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
print("[APP] app.py READY", flush=True)
print("[APP] FFmpegはまだ実行していません", flush=True)
print("==========================================", flush=True)


# =====================================
# 起動
# =====================================

if __name__ == "__main__":

    print("==========================================", flush=True)
    print("[APP] YouTube Converter", flush=True)
    print("==========================================", flush=True)

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
