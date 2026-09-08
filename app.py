# =====================================
# YouTube Converter
# app.py
#
# アプリケーションの入口
#
# 今回の調査目的:
#
# ・既存のimport / route登録は通常通り行う
# ・/test も通常通り表示する
# ・FFmpegボタンのrouteだけはFFmpegを実行しない
#
# 調査段階:
#
# ブラウザ
#   ↓
# POST /subtitle-test/ffmpeg
#   ↓
# Python
#   ↓
# 何もしない
#   ↓
# ブラウザに「FFmpeg終了」
#
# IMPORTANT:
# この段階では
# subtitle_test_ffmpeg.py をimportしない。
# FFmpegも起動しない。
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

print(
    "==========================================",
    flush=True
)

print(
    "[APP] Registering routes",
    flush=True
)

print(
    "==========================================",
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
    "[APP] register_index END",
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
    "[APP] register_files END",
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
    "[APP] register_convert END",
    flush=True
)


# -------------------------------------
# video-info / check
# -------------------------------------

print(
    "[APP] register_video_info START",
    flush=True
)

register_video_info(app)

print(
    "[APP] register_video_info END",
    flush=True
)


print(
    "[APP] register_check START",
    flush=True
)

register_check(app)

print(
    "[APP] register_check END",
    flush=True
)


# -------------------------------------
# Gemini / SRT
# -------------------------------------

print(
    "[APP] register_gemini START",
    flush=True
)

register_gemini(app)

print(
    "[APP] register_gemini END",
    flush=True
)


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

print(
    "[APP] subtitle_bp register START",
    flush=True
)

app.register_blueprint(
    subtitle_bp
)

print(
    "[APP] subtitle_bp register END",
    flush=True
)


# -------------------------------------
# completed files
# -------------------------------------

print(
    "[APP] register_completed_files START",
    flush=True
)

register_completed_files(
    app
)

print(
    "[APP] register_completed_files END",
    flush=True
)


# =====================================
# test route
#
# 単体テスト画面
#
# ブラウザ:
#
# /test
#
# =====================================

@app.route(
    "/test",
    methods=["GET"]
)
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
        "[APP] render_template(test.html) START",
        flush=True
    )

    result = render_template(
        "test.html"
    )

    print(
        "[APP] render_template(test.html) END",
        flush=True
    )

    print(
        "[APP] /test END",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return result


# =====================================
# FFmpeg字幕単体テスト
#
# POST /subtitle-test/ffmpeg
#
# =====================================
#
# IMPORTANT:
#
# ★ 今回はFFmpegを一切起動しない
# ★ subtitle_test_ffmpeg.pyもimportしない
# ★ run_ffmpeg_subtitle_test()も呼ばない
#
# まずここだけを確認する。
#
# ブラウザ
#   ↓
# ボタン
#   ↓
# POST
#   ↓
# このroute
#   ↓
# 「FFmpeg終了」
#   ↓
# ブラウザ
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
        "[TEST] ① /subtitle-test/ffmpeg START",
        flush=True
    )


    # -------------------------------------
    # ここでは何もしない
    # -------------------------------------

    print(
        "[TEST] ② subtitle_test_ffmpeg.py はimportしません",
        flush=True
    )

    print(
        "[TEST] ③ run_ffmpeg_subtitle_test() は呼びません",
        flush=True
    )

    print(
        "[TEST] ④ FFmpegは起動しません",
        flush=True
    )


    # -------------------------------------
    # ブラウザへ返す
    # -------------------------------------

    print(
        "[TEST] ⑤ ブラウザへ「FFmpeg終了」を返します",
        flush=True
    )


    print(
        "[TEST] ⑥ /subtitle-test/ffmpeg END",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return (
        "FFmpeg終了",
        200
    )


# =====================================
# 404確認
# =====================================

@app.errorhandler(404)
def page_not_found(error):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] 404 NOT FOUND",
        flush=True
    )

    try:

        from flask import request

        print(
            "[APP] method:",
            request.method,
            flush=True
        )

        print(
            "[APP] path:",
            request.path,
            flush=True
        )

    except Exception as request_error:

        print(
            "[APP] request情報取得失敗:",
            request_error,
            flush=True
        )

    print(
        "==========================================",
        flush=True
    )


    return (
        "Not Found",
        404
    )


# =====================================
# 登録ルート確認
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
        "[APP] ROUTE:",
        rule,
        "->",
        rule.endpoint,
        flush=True
    )


print(
    "==========================================",
    flush=True
)


# =====================================
# 起動確認
# =====================================

print(
    "[APP] app.py loaded successfully",
    flush=True
)

print(
    "[APP] FFmpeg test route: DISABLED",
    flush=True
)

print(
    "[APP] subtitle_test_ffmpeg.py: NOT IMPORTED",
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
        "[APP] YouTube Converter",
        flush=True
    )

    print(
        "[APP] MAIN START",
        flush=True
    )

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

    print(
        "[APP] FFmpeg:",
        "DISABLED",
        flush=True
    )

    print(
        "[APP] subtitle_test_ffmpeg.py:",
        "DISABLED",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False,
        use_reloader=False
    )
