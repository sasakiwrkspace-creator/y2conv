# =====================================
# YouTube Converter
# app.py
#
# FFmpeg字幕単体テスト
#
# 今回のテスト:
#
# ブラウザ
#   ↓
# Python
#   ↓
# test.mp4 存在確認
#   ↓
# test.srt 存在確認
#   ↓
# FFmpegを1回だけ起動
#   ↓
# 字幕を焼き込み
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

print(
    "[APP] BASE_DIR:",
    BASE_DIR,
    flush=True
)

print(
    "[APP] DOWNLOAD_DIR:",
    DOWNLOAD_DIR,
    flush=True
)


# =====================================
# Routes登録
# =====================================

print("==========================================", flush=True)
print("[APP] Registering routes", flush=True)
print("==========================================", flush=True)


print("[APP] register_index START", flush=True)

register_index(app)

print("[APP] register_index OK", flush=True)


print("[APP] register_files START", flush=True)

register_files(app)

print("[APP] register_files OK", flush=True)


print("[APP] register_convert START", flush=True)

register_convert(app)

print("[APP] register_convert OK", flush=True)


print("[APP] register_video_info START", flush=True)

register_video_info(app)

print("[APP] register_video_info OK", flush=True)


print("[APP] register_check START", flush=True)

register_check(app)

print("[APP] register_check OK", flush=True)


print("[APP] register_gemini START", flush=True)

register_gemini(app)

print("[APP] register_gemini OK", flush=True)


print("[APP] subtitle_bp register START", flush=True)

app.register_blueprint(subtitle_bp)

print("[APP] subtitle_bp register OK", flush=True)


print("[APP] register_completed_files START", flush=True)

register_completed_files(app)

print("[APP] register_completed_files OK", flush=True)


# =====================================
# /test
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

    return render_template("test.html")


# =====================================
# FFmpeg字幕単体テスト
#
# 重要:
#
# FFmpegはこのPOSTが呼ばれた時だけ
# 1回だけ起動する。
#
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

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

    print(
        "[APP] STEP 1: DOWNLOAD_DIR確認",
        flush=True
    )


    download_dir = Path(
        DOWNLOAD_DIR
    )


    print(
        f"[APP] DOWNLOAD_DIR: "
        f"{download_dir.resolve()}",
        flush=True
    )

    print(
        f"[APP] exists: "
        f"{download_dir.exists()}",
        flush=True
    )

    print(
        f"[APP] is_dir: "
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

        if (
            download_dir.exists()
            and download_dir.is_dir()
        ):

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
                            f"DIR: {item.name}"
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
    print("[APP] STEP 3: test.mp4確認", flush=True)
    print("==========================================", flush=True)


    input_path = (
        download_dir / "test.mp4"
    )


    print(
        f"[APP] input_path: "
        f"{input_path.resolve()}",
        flush=True
    )

    print(
        f"[APP] input exists: "
        f"{input_path.exists()}",
        flush=True
    )

    print(
        f"[APP] input is_file: "
        f"{input_path.is_file()}",
        flush=True
    )


    if not input_path.exists():

        print(
            "[APP] test.mp4 NOT FOUND",
            flush=True
        )

        print(
            "[APP] FFmpegは起動しません",
            flush=True
        )


        browser_text = (
            "【字幕FFmpegテスト診断】\n\n"
            "FFmpegは起動していません。\n\n"
            "test.mp4 が存在しません。\n\n"
            "確認パス:\n"
            f"{input_path.resolve()}\n\n"
            "downloadsの中身:\n"
        )


        if files:

            browser_text += (
                "\n".join(files)
            )

        else:

            browser_text += "(空です)"


        return browser_text, 400


    # =====================================
    # STEP 4
    # test.srt確認
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 4: test.srt確認", flush=True)
    print("==========================================", flush=True)


    subtitle_path = (
        download_dir / "test.srt"
    )


    print(
        f"[APP] subtitle_path: "
        f"{subtitle_path.resolve()}",
        flush=True
    )

    print(
        f"[APP] subtitle exists: "
        f"{subtitle_path.exists()}",
        flush=True
    )

    print(
        f"[APP] subtitle is_file: "
        f"{subtitle_path.is_file()}",
        flush=True
    )


    if not subtitle_path.exists():

        print(
            "[APP] test.srt NOT FOUND",
            flush=True
        )

        print(
            "[APP] FFmpegは起動しません",
            flush=True
        )


        browser_text = (
            "【字幕FFmpegテスト診断】\n\n"
            "FFmpegは起動していません。\n\n"
            "test.srt が存在しません。\n\n"
            "確認パス:\n"
            f"{subtitle_path.resolve()}\n\n"
            "downloadsの中身:\n"
        )


        if files:

            browser_text += (
                "\n".join(files)
            )

        else:

            browser_text += "(空です)"


        return browser_text, 400


    # =====================================
    # STEP 5
    # 入力サイズ
    # =====================================

    try:

        input_size = (
            input_path.stat().st_size
        )

        subtitle_size = (
            subtitle_path.stat().st_size
        )

    except Exception as size_error:

        print(
            "[APP] サイズ取得失敗:",
            size_error,
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "入力ファイルのサイズ取得に失敗しました。\n\n"
            f"ERROR:\n{size_error}",
            500
        )


    print(
        f"[APP] test.mp4 size: "
        f"{input_size} bytes",
        flush=True
    )

    print(
        f"[APP] test.srt size: "
        f"{subtitle_size} bytes",
        flush=True
    )


    # =====================================
    # STEP 6
    # test.srt内容を確認
    #
    # FFmpegを起動する前に
    # SRT自体が読めるか確認する。
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 6: test.srt確認", flush=True)
    print("==========================================", flush=True)


    try:

        with open(
            subtitle_path,
            "r",
            encoding="utf-8-sig"
        ) as subtitle_file:

            subtitle_text = (
                subtitle_file.read()
            )


        print(
            "[APP] test.srt 読み込みOK",
            flush=True
        )

        print(
            "[APP] test.srt 内容:",
            flush=True
        )

        print(
            subtitle_text,
            flush=True
        )


    except Exception as srt_error:

        print(
            "[APP] test.srt読み込み失敗:",
            srt_error,
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "test.srtを読み込めませんでした。\n\n"
            f"ERROR TYPE:\n"
            f"{type(srt_error).__name__}\n\n"
            f"ERROR:\n"
            f"{srt_error}",
            500
        )


    # =====================================
    # STEP 7
    # 出力先
    # =====================================

    output_path = (
        download_dir / "test_embed.mp4"
    )


    print("==========================================", flush=True)
    print("[APP] STEP 7: 出力先確認", flush=True)
    print("==========================================", flush=True)


    print(
        f"[APP] output_path: "
        f"{output_path.resolve()}",
        flush=True
    )


    # =====================================
    # STEP 8
    # 既存output削除
    # =====================================

    if output_path.exists():

        print(
            "[APP] 既存test_embed.mp4を削除",
            flush=True
        )

        try:

            output_path.unlink()

            print(
                "[APP] 既存output削除OK",
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
    # STEP 9
    # 字幕フィルター作成
    #
    # ここで字幕処理を初めて追加する。
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 9: 字幕フィルター作成", flush=True)
    print("==========================================", flush=True)


    # FFmpeg filter内で使用するパス
    #
    # 今回はLinux上なので
    # /app/downloads/test.srt
    # をそのまま使用する。
    #
    # Windowsのようなドライブ文字はない。
    #

    subtitle_filter = (
        "scale=640:360,"
        f"subtitles='{subtitle_path}':"
        "fontsdir='/usr/share/fonts/opentype/noto':"
        "force_style="
        "'FontName=Noto Sans CJK JP,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00FF0000,"
        "Outline=5'"
    )


    print(
        "[APP] subtitle filter:",
        flush=True
    )

    print(
        subtitle_filter,
        flush=True
    )


    # =====================================
    # STEP 10
    # FFmpegコマンド作成
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 10: FFmpegコマンド作成", flush=True)
    print("==========================================", flush=True)


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
        subtitle_filter,

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


    print(
        "[APP] FFmpeg command:",
        flush=True
    )

    print(
        " ".join(command),
        flush=True
    )


    # =====================================
    # STEP 11
    # FFmpeg起動
    #
    # ここで1回だけ。
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 11: FFmpeg開始", flush=True)
    print("==========================================", flush=True)

    print(
        "[APP] FFmpegを1回だけ起動します",
        flush=True
    )


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


    except Exception as ffmpeg_error:

        print(
            "[APP] FFmpeg起動例外:",
            ffmpeg_error,
            flush=True
        )

        traceback.print_exc()

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpeg起動時に例外が発生しました。\n\n"
            f"ERROR TYPE:\n"
            f"{type(ffmpeg_error).__name__}\n\n"
            f"ERROR:\n"
            f"{ffmpeg_error}",
            500
        )


    # =====================================
    # STEP 12
    # FFmpeg終了
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 12: FFmpeg終了", flush=True)
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
    # STEP 13
    # returncode確認
    # =====================================

    if result.returncode != 0:

        print(
            "[APP] FFmpeg FAILED",
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpegが終了しましたが、"
            "returncodeが0ではありません。\n\n"
            f"returncode:\n"
            f"{result.returncode}\n\n"
            f"FFmpeg stderr:\n"
            f"{result.stderr}",
            500
        )


    # =====================================
    # STEP 14
    # 出力ファイル確認
    # =====================================

    print("==========================================", flush=True)
    print("[APP] STEP 14: 出力確認", flush=True)
    print("==========================================", flush=True)


    print(
        f"[APP] output exists: "
        f"{output_path.exists()}",
        flush=True
    )


    if not output_path.exists():

        print(
            "[APP] FFmpeg成功だがoutputなし",
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpegはreturncode=0で終了しましたが、"
            "test_embed.mp4がありません。\n\n"
            f"出力予定:\n"
            f"{output_path.resolve()}",
            500
        )


    try:

        output_size = (
            output_path.stat().st_size
        )

    except Exception as output_error:

        print(
            "[APP] outputサイズ取得失敗:",
            output_error,
            flush=True
        )

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "test_embed.mp4は存在しますが、"
            "サイズ取得に失敗しました。\n\n"
            f"ERROR:\n{output_error}",
            500
        )


    # =====================================
    # STEP 15
    # 成功
    # =====================================

    print("==========================================", flush=True)
    print("[APP] FFmpeg字幕テスト成功", flush=True)
    print("==========================================", flush=True)


    return (
        "【字幕FFmpegテスト完了】\n\n"
        "FFmpeg終了\n\n"
        f"入力ファイル:\n"
        f"{input_path.resolve()}\n\n"
        f"入力サイズ:\n"
        f"{input_size} bytes\n\n"
        f"SRTファイル:\n"
        f"{subtitle_path.resolve()}\n\n"
        f"SRTサイズ:\n"
        f"{subtitle_size} bytes\n\n"
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
