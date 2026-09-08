# =====================================
# YouTube Converter
# app.py
#
# 調査用最小構成
#
# 今回の目的:
#
# 1. app.py が正常起動しているか
# 2. 起動時に余計な処理が動いていないか
# 3. /test が正常に表示されるか
# 4. /subtitle-test/ffmpeg が呼ばれたか
# 5. FFmpegを起動せずにブラウザへ応答できるか
#
# IMPORTANT:
# このファイルではFFmpegを一切起動しない。
# subtitle_test_ffmpeg.py もimportしない。
# =====================================


from flask import Flask, render_template


# =====================================
# Flask生成
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] app.py import START",
    flush=True
)

print(
    "[APP] Flask instance CREATE",
    flush=True
)

app = Flask(__name__)

print(
    "[APP] Flask instance CREATE OK",
    flush=True
)


# =====================================
# /test
#
# ブラウザから開く確認用
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
        "[APP] Python is responding",
        flush=True
    )

    print(
        "[APP] render_template START",
        flush=True
    )

    result = render_template(
        "test.html"
    )

    print(
        "[APP] render_template END",
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
# FFmpegテスト用ルート
#
# IMPORTANT:
#
# 現段階ではFFmpegを一切起動しない。
#
# ブラウザ
#   ↓
# POST
#   ↓
# Python
#   ↓
# 「FFmpeg終了」
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

    print(
        "[APP] FFmpeg START処理には入りません",
        flush=True
    )

    print(
        "[APP] subprocessは呼びません",
        flush=True
    )

    print(
        "[APP] subtitle_test_ffmpeg.pyはimportしません",
        flush=True
    )

    print(
        "[APP] FFmpeg終了をブラウザへ返します",
        flush=True
    )

    print(
        "[APP] /subtitle-test/ffmpeg END",
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

    print(
        "[APP] path:",
        flush=True
    )

    try:
        from flask import request

        print(
            request.path,
            flush=True
        )

        print(
            "[APP] method:",
            request.method,
            flush=True
        )

    except Exception as e:

        print(
            "[APP] request情報取得失敗:",
            e,
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
# 登録URL確認
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] Registered routes START",
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
    "[APP] Registered routes END",
    flush=True
)

print(
    "==========================================",
    flush=True
)


# =====================================
# import完了
# =====================================

print(
    "[APP] app.py import END",
    flush=True
)


# =====================================
# 起動
# =====================================

if __name__ == "__main__":

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] MAIN START",
        flush=True
    )

    print(
        "[APP] FFmpeg: DISABLED",
        flush=True
    )

    print(
        "[APP] subtitle_test_ffmpeg.py: DISABLED",
        flush=True
    )

    print(
        "[APP] Flask starting...",
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
