# =====================================
# YouTube Converter
# app.py
#
# 現在の調査用最小構成
#
# 目的:
# ・アプリ起動確認
# ・既存Route登録
# ・/test 表示
# ・ブラウザのボタン
#       ↓
#   Python
#       ↓
#   test.mp4存在確認
#       ↓
#   FFmpegを1回だけ起動
#       ↓
#   FFmpeg終了を待つ
#       ↓
#   test_embed.mp4作成
#       ↓
#   ブラウザに「FFmpeg終了」
#
# 注意:
# ・字幕処理は行わない
# ・SRTは使用しない
# ・字幕フィルターは使用しない
# ・FFmpegのループ処理はしない
# ・バックグラウンドFFmpegは使用しない
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
# プロジェクト設定
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
        "[APP] /test が呼ばれました",
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
# POST /subtitle-test/ffmpeg
#
# 今回はここだけを調査する。
#
# 処理:
#
# ブラウザ
#   ↓
# Python
#   ↓
# test.mp4確認
#   ↓
# FFmpeg 1回
#   ↓
# test_embed.mp4
#   ↓
# FFmpeg終了
#   ↓
# ブラウザへ返す
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
    print("[TEST] /subtitle-test/ffmpeg START", flush=True)
    print("==========================================", flush=True)


    try:

        # =====================================
        # 1. 入力ファイル
        # =====================================

        input_path = (
            Path(DOWNLOAD_DIR)
            / "test.mp4"
        )

        print(
            "[TEST] STEP 1: 入力ファイル確認",
            flush=True
        )

        print(
            f"[TEST] input: {input_path}",
            flush=True
        )


        if not input_path.exists():

            print(
                "[TEST] ERROR: test.mp4 が存在しません",
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
                "[TEST] ERROR: test.mp4 がファイルではありません",
                flush=True
            )

            return (
                "【字幕FFmpegテスト失敗】\n\n"
                "入力ファイルが通常のファイルではありません:\n"
                f"{input_path}",
                500
            )


        input_size = (
            input_path.stat().st_size
        )

        print(
            f"[TEST] test.mp4 exists: True",
            flush=True
        )

        print(
            f"[TEST] test.mp4 size: "
            f"{input_size} bytes",
            flush=True
        )


        # =====================================
        # 2. 出力先
        #
        # 今後は必ず test_embed.mp4
        # =====================================

        output_path = (
            Path(DOWNLOAD_DIR)
            / "test_embed.mp4"
        )

        print(
            "[TEST] STEP 2: 出力先確認",
            flush=True
        )

        print(
            f"[TEST] output: {output_path}",
            flush=True
        )


        # =====================================
        # 3. 古い出力を削除
        # =====================================

        if output_path.exists():

            print(
                "[TEST] 既存test_embed.mp4を削除します",
                flush=True
            )

            output_path.unlink()

            print(
                "[TEST] 既存ファイル削除完了",
                flush=True
            )


        # =====================================
        # 4. FFmpegコマンド
        #
        # 字幕なし。
        #
        # test.mp4をそのままMP4として
        # test_embed.mp4へ変換する。
        #
        # 低メモリ環境用:
        # ・scaleなし
        # ・字幕なし
        # ・threads 1
        # ・ultrafast
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
            "[TEST] STEP 3: FFmpegコマンド",
            flush=True
        )

        print(
            "[TEST] FFmpeg command:",
            flush=True
        )

        print(
            " ".join(ffmpeg_command),
            flush=True
        )


        # =====================================
        # 5. FFmpeg起動
        #
        # 重要:
        # subprocess.run() なので
        # FFmpeg終了までここで待つ。
        #
        # ループしない。
        # =====================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] STEP 4: FFmpeg START",
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
        # 6. FFmpeg終了
        # =====================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] STEP 5: FFmpeg END",
            flush=True
        )

        print(
            f"[TEST] FFmpeg returncode: "
            f"{result.returncode}",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        # =====================================
        # 7. FFmpegエラー
        # =====================================

        if result.returncode != 0:

            print(
                "[TEST] FFmpeg FAILED",
                flush=True
            )

            print(
                "[TEST] FFmpeg stderr:",
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
        # 8. 出力確認
        # =====================================

        print(
            "[TEST] STEP 6: 出力ファイル確認",
            flush=True
        )


        if not output_path.exists():

            print(
                "[TEST] ERROR: 出力ファイルがありません",
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
        # 9. ブラウザへ返す
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
            "[TEST] ブラウザへ「FFmpeg終了」を返します",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        return (
            "【字幕FFmpegテスト完了】\n\n"
            "FFmpeg終了\n\n"
            f"出力ファイル:\n"
            f"{output_path}\n\n"
            f"出力サイズ:\n"
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
# 登録Route確認
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

    print(
        "[APP] Flask直接起動",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
