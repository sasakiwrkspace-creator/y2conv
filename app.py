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
# ・MP3アップロード → SRT
# ・MP4アップロード
# ・SRTアップロード
# ・MP4 + SRT → 字幕MP4
#
# タブ3:
# ・FFmpeg字幕焼き込み単体テスト
# ・downloads/test.mp4
# ・downloads/test.srt
# ・test_embed.mp4作成
#
# 完成ファイル確認:
# ・/find-completed-files
#
# 単体テスト:
# ・/test
# ・templates/test.html を表示
#
# 注意:
# ・converter.js / subtitle.js の処理は
#   このファイルでは行わない。
# ・subtitle_test_ffmpeg.py は Flask から呼び出す
#   単体テスト用モジュールとして使用する。
# =====================================


from flask import Flask, render_template


import config


from routes.index import register_index
from routes.files import register_files
from routes.convert import register_convert
from routes.check import register_video_info, register_check
from routes.gemini import register_gemini
from routes.completed_files import register_completed_files

# subtitle_routes.py は Blueprint方式
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
# Routes登録開始
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
# -------------------------------------

register_gemini(app)


# -------------------------------------
# subtitle
#
# subtitle_routes.py は Blueprint方式。
#
# タブ2:
#
# MP3アップロード
#     ↓
# Gemini
#     ↓
# SRT
#
# MP4アップロード
# SRTアップロード
#     ↓
# MP4 + SRT
#     ↓
# 字幕付きMP4
#
# -------------------------------------

app.register_blueprint(
    subtitle_bp
)


# -------------------------------------
# completed files
#
# POST /find-completed-files
#
# completed_files.py に処理を分離
# -------------------------------------

register_completed_files(
    app
)


# =====================================
# test route
#
# 単体テスト画面
#
# templates/test.html を表示する。
#
# ブラウザ:
#
# https://y2conv.onrender.com/test
#
# -------------------------------------

@app.route("/test")
def test_page():

    print(
        "★ /test が呼ばれました ★",
        flush=True
    )

    return render_template(
        "test.html"
    )


# =====================================
# FFmpeg字幕単体テスト
#
# POST /subtitle-test/ffmpeg
#
# test.html のFFmpegボタンから呼び出す。
#
# 実処理:
# subtitle_test_ffmpeg.py
#
# 入力:
# downloads/test.mp4
# downloads/test.srt
#
# 出力:
# downloads/test_embed.mp4
#
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

    try:

        # -------------------------------------
        # 単体テストモジュール読み込み
        # -------------------------------------

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


        # -------------------------------------
        # FFmpeg字幕焼き込み実行
        # -------------------------------------

        print(
            "[APP] run_ffmpeg_subtitle_test() START",
            flush=True
        )

        output_path = (
            run_ffmpeg_subtitle_test()
        )


        # -------------------------------------
        # 成功
        # -------------------------------------

        print(
            "[APP] run_ffmpeg_subtitle_test() SUCCESS",
            flush=True
        )

        print(
            f"[APP] output_path: {output_path}",
            flush=True
        )

        print(
            f"[APP] output_path type: "
            f"{type(output_path).__name__}",
            flush=True
        )


        # -------------------------------------
        # 最終ファイル確認
        # -------------------------------------

        try:

            from pathlib import Path

            final_path = Path(
                output_path
            ).resolve()

            print(
                f"[APP] final resolved path: "
                f"{final_path}",
                flush=True
            )

            print(
                f"[APP] final exists: "
                f"{final_path.exists()}",
                flush=True
            )

            print(
                f"[APP] final is_file: "
                f"{final_path.is_file()}",
                flush=True
            )

            if final_path.exists():

                try:

                    print(
                        f"[APP] final size: "
                        f"{final_path.stat().st_size} bytes",
                        flush=True
                    )

                except Exception as stat_error:

                    print(
                        f"[APP] final size取得失敗: "
                        f"{stat_error}",
                        flush=True
                    )

        except Exception as path_error:

            print(
                f"[APP] 最終ファイル確認失敗: "
                f"{path_error}",
                flush=True
            )


        print(
            "[APP] /subtitle-test/ffmpeg SUCCESS",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        return (
            "FFmpeg字幕焼き込み成功\n\n"
            f"出力ファイル:\n"
            f"{output_path}",
            200
        )


    except Exception as error:

        import traceback


        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] /subtitle-test/ffmpeg FAILED",
            flush=True
        )

        print(
            f"[APP] ERROR TYPE: "
            f"{type(error).__name__}",
            flush=True
        )

        print(
            f"[APP] ERROR: "
            f"{error}",
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

        print(
            "==========================================",
            flush=True
        )


        return (
            "FFmpeg字幕焼き込み失敗\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
            500
        )


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
