# =====================================
# YouTube Converter
# app.py
#
# 完全最小テスト版
#
# 目的:
#
#   まずアプリケーションの通信だけを確認する。
#
#   ブラウザ
#       ↓
#   Flask
#       ↓
#   /subtitle-test/ffmpeg
#       ↓
#   「FFmpeg終了」
#       ↓
#   ブラウザ
#
#
# IMPORTANT
#
# このファイルでは、
#
# ・FFmpegを起動しない
# ・subtitle_test_ffmpeg.pyをimportしない
# ・routes.*をimportしない
# ・subtitle_fontをimportしない
# ・SRTを読まない
# ・MP4を読まない
# ・Geminiを呼ばない
# ・動画変換をしない
#
# =====================================


from flask import Flask


# =====================================
# Flask
# =====================================

app = Flask(__name__)


# =====================================
# 起動ログ
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] MINIMAL TEST APP START",
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
    "[APP] routes.*: DISABLED",
    flush=True
)

print(
    "==========================================",
    flush=True
)


# =====================================
# トップページ
# =====================================

@app.route("/")
def index():

    print(
        "[APP] GET /",
        flush=True
    )

    return """
<!DOCTYPE html>

<html lang="ja">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>FFmpeg 最小テスト</title>

    <style>

        body {
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            padding: 40px;

            background: #f5f5f5;

            color: #222;
        }

        .container {

            max-width: 700px;

            margin: 0 auto;

            background: white;

            padding: 30px;

            border-radius: 12px;

            box-shadow:
                0 2px 10px
                rgba(0, 0, 0, 0.08);
        }

        h1 {

            margin-top: 0;

        }

        button {

            padding:
                14px 24px;

            font-size: 18px;

            border: none;

            border-radius: 8px;

            background: #2563eb;

            color: white;

            cursor: pointer;
        }

        button:hover {

            background: #1d4ed8;

        }

        button:disabled {

            background: #999;

            cursor: not-allowed;

        }

        #result {

            margin-top: 25px;

            padding: 20px;

            border-radius: 8px;

            background: #eee;

            font-size: 20px;

            min-height: 30px;
        }

        .success {

            background: #dcfce7 !important;

            color: #166534;

        }

        .error {

            background: #fee2e2 !important;

            color: #991b1b;

        }

    </style>

</head>


<body>

<div class="container">

    <h1>
        FFmpeg 最小テスト
    </h1>


    <p>
        このテストではFFmpegを実行しません。
    </p>


    <p>
        ブラウザ → Python → ブラウザ
        の通信だけを確認します。
    </p>


    <button
        id="testButton"
        onclick="runTest()"
    >
        テスト開始
    </button>


    <div id="result">

        まだ実行していません。

    </div>

</div>


<script>

async function runTest() {

    const button =
        document.getElementById(
            "testButton"
        );

    const result =
        document.getElementById(
            "result"
        );


    console.log(
        "[BROWSER] テスト開始"
    );


    button.disabled = true;


    result.className = "";


    result.textContent =
        "Pythonを呼び出しています...";


    try {

        console.log(
            "[BROWSER] POST /subtitle-test/ffmpeg"
        );


        const response =
            await fetch(
                "/subtitle-test/ffmpeg",
                {
                    method: "POST"
                }
            );


        console.log(
            "[BROWSER] response received",
            response.status
        );


        const text =
            await response.text();


        console.log(
            "[BROWSER] response:",
            text
        );


        if (response.ok) {

            result.className =
                "success";


            result.textContent =
                text;


            console.log(
                "[BROWSER] テスト成功"
            );

        } else {

            result.className =
                "error";


            result.textContent =
                "HTTPエラー: " +
                response.status +
                "\\n" +
                text;


            console.error(
                "[BROWSER] HTTPエラー",
                response.status
            );
        }


    } catch (error) {

        console.error(
            "[BROWSER] 通信エラー",
            error
        );


        result.className =
            "error";


        result.textContent =
            "通信エラー: " +
            error;


    } finally {

        button.disabled = false;

    }

}

</script>


</body>

</html>
"""


# =====================================
# FFmpegテスト
#
# IMPORTANT:
#
# ここではFFmpegを実行しない。
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


    # -------------------------------------
    # Python到達確認
    # -------------------------------------

    print(
        "[APP] Pythonルート到達",
        flush=True
    )


    # -------------------------------------
    # FFmpeg無効確認
    # -------------------------------------

    print(
        "[APP] FFmpegは実行しません",
        flush=True
    )


    # -------------------------------------
    # subtitle_test_ffmpeg.py無効確認
    # -------------------------------------

    print(
        "[APP] subtitle_test_ffmpeg.pyは呼びません",
        flush=True
    )


    # -------------------------------------
    # routes無効確認
    # -------------------------------------

    print(
        "[APP] routesモジュールは呼びません",
        flush=True
    )


    # -------------------------------------
    # 処理終了
    # -------------------------------------

    print(
        "[APP] Python処理終了",
        flush=True
    )


    print(
        "[APP] ブラウザへ「FFmpeg終了」を返します",
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
        200,
        {
            "Content-Type":
                "text/plain; charset=utf-8"
        }
    )


# =====================================
# ヘルスチェック
#
# Render確認用
# =====================================

@app.route(
    "/health"
)
def health():

    print(
        "[APP] GET /health",
        flush=True
    )

    return (
        "OK",
        200
    )


# =====================================
# ルート確認
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] Registered routes:",
    flush=True
)


for rule in app.url_map.iter_rules():

    print(
        f"[APP] {rule}",
        flush=True
    )


print(
    "==========================================",
    flush=True
)


# =====================================
# 直接実行
#
# RenderでGunicornを使用する場合は、
# 通常ここは実行されない。
#
# 例:
#
# gunicorn app:app
#
# =====================================

if __name__ == "__main__":

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] Direct execution mode",
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
        threaded=True
    )
