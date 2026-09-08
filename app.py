from flask import Flask, render_template
from pathlib import Path
import traceback
import config

from routes.index import register_index
from routes.files import register_files
from routes.convert import register_convert
from routes.check import register_video_info, register_check
from routes.gemini import register_gemini
from routes.completed_files import register_completed_files
from routes.subtitle_routes import subtitle_bp


app = Flask(__name__)


BASE_DIR = config.BASE_DIR
DOWNLOAD_DIR = config.DOWNLOAD_DIR


print("==========================================", flush=True)
print("[APP] app.py START", flush=True)
print("[APP] BASE_DIR:", BASE_DIR, flush=True)
print("[APP] DOWNLOAD_DIR:", DOWNLOAD_DIR, flush=True)
print("==========================================", flush=True)


# =====================================
# Routes
# =====================================

register_index(app)

register_files(app)

register_convert(app)

register_video_info(app)

register_check(app)

register_gemini(app)

app.register_blueprint(subtitle_bp)

register_completed_files(app)


# =====================================
# テスト画面
# =====================================

@app.route("/test")
def test_page():

    print(
        "[APP] /test",
        flush=True
    )

    return render_template("test.html")


# =====================================
# FFmpeg字幕テスト
#
# FFmpegを実行するのは
# subtitle_test_ffmpeg.pyだけ。
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

        # ---------------------------------
        # モジュール読み込み
        # ---------------------------------

        from subtitle_test_ffmpeg import (
            run_ffmpeg_subtitle_test
        )

        print(
            "[APP] run_ffmpeg_subtitle_test() START",
            flush=True
        )

        # ---------------------------------
        # ここで1回だけ呼ぶ
        # ---------------------------------

        output_path = run_ffmpeg_subtitle_test()

        # ---------------------------------
        # 結果確認
        # ---------------------------------

        output_path = Path(output_path)

        if not output_path.exists():

            raise FileNotFoundError(
                f"出力ファイルがありません: {output_path}"
            )

        output_size = output_path.stat().st_size

        print(
            "[APP] run_ffmpeg_subtitle_test() END",
            flush=True
        )

        print(
            f"[APP] output: {output_path}",
            flush=True
        )

        print(
            f"[APP] size: {output_size} bytes",
            flush=True
        )

        # ---------------------------------
        # ブラウザへ返す
        # ---------------------------------

        return (
            "【字幕FFmpegテスト完了】\n\n"
            "FFmpeg終了\n\n"
            f"出力ファイル:\n"
            f"{output_path}\n\n"
            f"出力サイズ:\n"
            f"{output_size} bytes"
        ), 200

    except Exception as error:

        print("==========================================", flush=True)
        print("[APP] FFmpeg TEST FAILED", flush=True)
        print(
            f"[APP] ERROR TYPE: {type(error).__name__}",
            flush=True
        )
        print(
            f"[APP] ERROR: {error}",
            flush=True
        )

        traceback.print_exc()

        print("==========================================", flush=True)

        return (
            "【字幕FFmpegテスト失敗】\n\n"
            "字幕FFmpegテストに失敗しました。\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}"
        ), 500


# =====================================
# Route確認
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
print("[APP] FFmpegは起動時には実行しません", flush=True)
print("==========================================", flush=True)


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
