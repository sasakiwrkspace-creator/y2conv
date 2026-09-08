# =====================================
# YouTube Converter
# app.py
#
# FFmpeg字幕 最小テスト
# force_style追加版
#
# 流れ:
#
# ブラウザ
#   ↓
# Python
#   ↓
# test.mp4確認
#   ↓
# test.srt確認
#   ↓
# FFmpegを1回だけ起動
#   ↓
# subtitles + force_style
#   ↓
# test_embed.mp4
#   ↓
# FFmpeg終了
#   ↓
# ブラウザ表示
#
# 今回追加するもの:
#
# ・force_style
#
# 今回まだ追加しないもの:
#
# ・fontsdir
# ・scale
# ・-progress
# ・ログ読み取りスレッド
# ・バックグラウンド処理
# ・subtitle_test_ffmpeg.py
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

print("==========================================", flush=True)
print("[APP] app.py START", flush=True)
print("==========================================", flush=True)


app = Flask(__name__)


# =====================================
# 設定
# =====================================

BASE_DIR = config.BASE_DIR
DOWNLOAD_DIR = config.DOWNLOAD_DIR


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

app.register_blueprint(
    subtitle_bp
)

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
        "[TEST] /test が呼ばれました",
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
# FFmpeg字幕テスト
#
# POST:
# /subtitle-test/ffmpeg
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    import subprocess
    import traceback
    from pathlib import Path


    print(
        "==========================================",
        flush=True
    )

    print(
        "[TEST] /subtitle-test/ffmpeg START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    try:

        # =====================================
        # STEP 1
        # test.mp4確認
        # =====================================

        input_path = (
            Path(DOWNLOAD_DIR)
            / "test.mp4"
        )

        print(
            "[TEST] STEP 1: test.mp4確認",
            flush=True
        )

        print(
            f"[TEST] input: {input_path}",
            flush=True
        )


        if not input_path.exists():

            print(
                "[TEST] test.mp4 がありません",
                flush=True
            )

            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "入力ファイルが存在しません:\n"
                f"{input_path}",
                500
            )


        if not input_path.is_file():

            print(
                "[TEST] test.mp4 がファイルではありません",
                flush=True
            )

            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "test.mp4 が通常のファイルではありません。",
                500
            )


        print(
            f"[TEST] test.mp4 size: "
            f"{input_path.stat().st_size} bytes",
            flush=True
        )


        # =====================================
        # STEP 2
        # test.srt確認
        # =====================================

        subtitle_path = (
            Path(DOWNLOAD_DIR)
            / "test.srt"
        )

        print(
            "[TEST] STEP 2: test.srt確認",
            flush=True
        )

        print(
            f"[TEST] subtitle: {subtitle_path}",
            flush=True
        )


        if not subtitle_path.exists():

            print(
                "[TEST] test.srt がありません",
                flush=True
            )

            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "字幕ファイルが存在しません:\n"
                f"{subtitle_path}",
                500
            )


        if not subtitle_path.is_file():

            print(
                "[TEST] test.srt がファイルではありません",
                flush=True
            )

            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "test.srt が通常のファイルではありません。",
                500
            )


        print(
            f"[TEST] test.srt size: "
            f"{subtitle_path.stat().st_size} bytes",
            flush=True
        )


        # =====================================
        # STEP 3
        # 出力先
        # =====================================

        output_path = (
            Path(DOWNLOAD_DIR)
            / "test_embed.mp4"
        )

        print(
            "[TEST] STEP 3: 出力先",
            flush=True
        )

        print(
            f"[TEST] output: {output_path}",
            flush=True
        )


        # =====================================
        # 既存ファイル削除
        # =====================================

        if output_path.exists():

            print(
                "[TEST] 既存test_embed.mp4を削除",
                flush=True
            )

            output_path.unlink()

            print(
                "[TEST] 既存ファイル削除完了",
                flush=True
            )


        # =====================================
        # STEP 4
        # force_style
        #
        # 字幕処理そのものは前回成功済み。
        #
        # 今回は見た目だけ追加。
        #
        # 白文字
        # 赤い縁取り
        # =====================================

        force_style = (
            "FontName=Noto Sans CJK JP,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H000000FF,"
            "Outline=5"
        )


        subtitle_filter = (
            "subtitles="
            + str(subtitle_path)
            + ":force_style='"
            + force_style
            + "'"
        )


        print(
            "[TEST] STEP 4: 字幕フィルター作成",
            flush=True
        )

        print(
            f"[TEST] force_style: "
            f"{force_style}",
            flush=True
        )

        print(
            f"[TEST] filter: "
            f"{subtitle_filter}",
            flush=True
        )


        # =====================================
        # STEP 5
        # FFmpegコマンド
        # =====================================

        ffmpeg_command = [

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
            "[TEST] STEP 5: FFmpegコマンド",
            flush=True
        )

        print(
            " ".join(ffmpeg_command),
            flush=True
        )


        # =====================================
        # STEP 6
        # FFmpeg開始
        #
        # 1回だけ起動。
        # 終了するまで待つ。
        # =====================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] STEP 6: FFmpeg START",
            flush=True
        )

        print(
            "[TEST] FFmpegを1回だけ起動します",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        result = subprocess.run(

            ffmpeg_command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=120,

            check=False
        )


        # =====================================
        # STEP 7
        # FFmpeg終了
        # =====================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] STEP 7: FFmpeg END",
            flush=True
        )

        print(
            f"[TEST] returncode: "
            f"{result.returncode}",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        # =====================================
        # FFmpeg失敗
        # =====================================

        if result.returncode != 0:

            print(
                "[TEST] FFmpeg FAILED",
                flush=True
            )

            print(
                "[TEST] stderr:",
                flush=True
            )

            print(
                result.stderr,
                flush=True
            )


            if output_path.exists():

                try:

                    output_path.unlink()

                except Exception:

                    pass


            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "FFmpeg処理失敗\n\n"
                f"returncode:\n"
                f"{result.returncode}\n\n"
                f"stderr:\n"
                f"{result.stderr}",
                500
            )


        # =====================================
        # STEP 8
        # 出力確認
        # =====================================

        print(
            "[TEST] STEP 8: 出力確認",
            flush=True
        )


        if not output_path.exists():

            print(
                "[TEST] test_embed.mp4 がありません",
                flush=True
            )

            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "FFmpegは終了しましたが、"
                "test_embed.mp4 が作成されませんでした。",
                500
            )


        output_size = (
            output_path.stat().st_size
        )


        print(
            f"[TEST] output exists: True",
            flush=True
        )

        print(
            f"[TEST] output size: "
            f"{output_size} bytes",
            flush=True
        )


        # =====================================
        # STEP 9
        # ブラウザへ返す
        # =====================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] SUCCESS",
            flush=True
        )

        print(
            "[TEST] ブラウザへ結果を返します",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        return (
            "【字幕FFmpegテスト完了】\n\n"
            "FFmpeg終了\n\n"
            "出力ファイル:\n"
            f"{output_path}\n\n"
            "出力サイズ:\n"
            f"{output_size} bytes",
            200
        )


    except subprocess.TimeoutExpired:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] FFmpeg TIMEOUT",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "FFmpegが120秒以内に終了しませんでした。",
            500
        )


    except Exception as error:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] EXCEPTION",
            flush=True
        )

        print(
            f"[TEST] ERROR TYPE: "
            f"{type(error).__name__}",
            flush=True
        )

        print(
            f"[TEST] ERROR: "
            f"{error}",
            flush=True
        )

        print(
            "[TEST] TRACEBACK START",
            flush=True
        )

        traceback.print_exc()

        print(
            "[TEST] TRACEBACK END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "字幕FFmpegテストに失敗しました。\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
            500
        )


# =====================================
# Route確認
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
        rule,
        "->",
        rule.endpoint,
        flush=True
    )


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
        "[APP] Flask直接起動",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
