from flask import request, jsonify
import os
import shutil
import tempfile
import yt_dlp

print("==========================================")
print("check.py 起動")
print("==========================================")

RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"

BASE_DIR = os.path.dirname(
os.path.dirname(
os.path.abspath(**file**)
)
)

LOCAL_COOKIE_FILE = os.path.join(
BASE_DIR,
"cookies.txt"
)

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"
DENO_DIR = "/opt/render/project/src/.deno/bin"

if os.environ.get("RENDER") == "true":
ORIGINAL_COOKIE_FILE = RENDER_COOKIE_FILE
else:
ORIGINAL_COOKIE_FILE = LOCAL_COOKIE_FILE

if os.path.isdir(DENO_DIR):
current_path = os.environ.get("PATH", "")
if DENO_DIR not in current_path.split(os.pathsep):
os.environ["PATH"] = (
DENO_DIR
+ os.pathsep
+ current_path
)

print("==========================================")
print("Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("元Cookieファイル:")
print(ORIGINAL_COOKIE_FILE)
print("==========================================")

print("==========================================")
print("Deno設定")
print("Deno path:")
print(DENO_PATH)
print("Deno exists:", os.path.exists(DENO_PATH))
print("Deno executable:", os.access(DENO_PATH, os.X_OK))
print("==========================================")

def remove_cookie_file(cookie_file):
if not cookie_file:
return

```
try:
    if os.path.exists(cookie_file):
        os.remove(cookie_file)

        print(
            "一時Cookieファイル削除OK:",
            cookie_file
        )

except Exception as e:
    print(
        "一時Cookieファイル削除失敗:",
        repr(e)
    )
```

def prepare_cookie_file():
print("==========================================")
print("Cookie準備開始")
print("==========================================")

```
if not os.path.exists(
    ORIGINAL_COOKIE_FILE
):
    raise Exception(
        "Cookieファイルが見つかりません: "
        + ORIGINAL_COOKIE_FILE
    )

original_size = os.path.getsize(
    ORIGINAL_COOKIE_FILE
)

print(
    "元Cookieサイズ:",
    original_size,
    "bytes"
)

if original_size == 0:
    raise Exception(
        "Cookieファイルが空です: "
        + ORIGINAL_COOKIE_FILE
    )

temp_file = tempfile.NamedTemporaryFile(
    mode="wb",
    suffix=".txt",
    prefix="y2conv_check_cookies_",
    delete=False
)

temp_cookie_file = temp_file.name
temp_file.close()

try:
    shutil.copyfile(
        ORIGINAL_COOKIE_FILE,
        temp_cookie_file
    )

except Exception:
    remove_cookie_file(
        temp_cookie_file
    )
    raise

if not os.path.exists(
    temp_cookie_file
):
    raise Exception(
        "一時Cookieファイルの作成に失敗しました: "
        + temp_cookie_file
    )

file_size = os.path.getsize(
    temp_cookie_file
)

print(
    "一時Cookie:",
    temp_cookie_file
)

print(
    "一時Cookieサイズ:",
    file_size,
    "bytes"
)

if file_size == 0:
    remove_cookie_file(
        temp_cookie_file
    )

    raise Exception(
        "一時Cookieファイルが空です"
    )

cookie_count = 0
youtube_cookie_count = 0

try:
    with open(
        temp_cookie_file,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:
            line = line.strip()

            if (
                not line
                or line.startswith("#")
            ):
                continue

            fields = line.split("\t")

            if len(fields) >= 7:
                cookie_count += 1

                domain = fields[0].lower()

                if (
                    "youtube.com" in domain
                    or "google.com" in domain
                ):
                    youtube_cookie_count += 1

            else:
                cookie_count += 1

except Exception as e:
    remove_cookie_file(
        temp_cookie_file
    )

    raise Exception(
        "Cookieファイルの読み込みに失敗しました: "
        + repr(e)
    )

print("==========================================")
print(
    "Cookieデータ行数:",
    cookie_count
)
print(
    "YouTube/Google Cookie数:",
    youtube_cookie_count
)
print(
    "一時Cookieサイズ:",
    file_size,
    "bytes"
)
print("==========================================")

if cookie_count == 0:
    remove_cookie_file(
        temp_cookie_file
    )

    raise Exception(
        "Cookieデータが0件です"
    )

if youtube_cookie_count == 0:
    print(
        "WARNING: "
        "YouTube/Google Cookieが見つかりません"
    )

return temp_cookie_file
```

def get_ydl_options(cookie_file):
return {
"cookiefile": cookie_file,

```
    "noplaylist": True,

    "js_runtimes": {
        "deno": DENO_PATH
    },

    "remote_components": {
        "ejs:github"
    },

    "quiet": False,

    "no_warnings": False,

    "verbose": True,

    "skip_download": True
}
```

def diagnose_environment():
print("==========================================")
print("実行環境診断")
print("==========================================")

```
print(
    "RENDER:",
    os.environ.get("RENDER")
)

print("------------------------------------------")
print("Python version:")

import sys

print(
    sys.version
)

print(
    "Python executable:",
    sys.executable
)

print("------------------------------------------")
print("yt-dlp version:")

try:
    print(
        yt_dlp.version.__version__
    )
except Exception:
    print("不明")

print("------------------------------------------")
print("yt-dlp-ejs:")

try:
    import yt_dlp_ejs

    print("インストール済み")

    version = getattr(
        yt_dlp_ejs,
        "__version__",
        None
    )

    print(
        "version:",
        version if version else "不明"
    )

except Exception as e:
    print(
        "読み込み失敗:",
        repr(e)
    )

print("------------------------------------------")
print("Deno:")

print(
    "path:",
    DENO_PATH
)

print(
    "exists:",
    os.path.exists(DENO_PATH)
)

print(
    "executable:",
    os.access(
        DENO_PATH,
        os.X_OK
    )
)

if os.path.exists(DENO_PATH):
    import subprocess

    try:
        result = subprocess.run(
            [
                DENO_PATH,
                "--version"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        print(
            "returncode:",
            result.returncode
        )

        print(
            result.stdout
        )

        if result.stderr:
            print(
                result.stderr
            )

    except Exception as e:
        print(
            "Deno実行失敗:",
            repr(e)
        )

print("------------------------------------------")
print("PATH:")

print(
    os.environ.get(
        "PATH",
        ""
    )
)

print("==========================================")
```

def get_youtube_info(url):
temp_cookie = None

```
try:
    print("==========================================")
    print("YouTube情報取得開始")
    print("==========================================")
    print(
        "URL:",
        url
    )
    print("==========================================")

    temp_cookie = prepare_cookie_file()

    ydl_opts = get_ydl_options(
        temp_cookie
    )

    print("==========================================")
    print("yt-dlp設定")
    print("==========================================")

    print(
        "yt-dlp version:",
        yt_dlp.version.__version__
    )

    print(
        "Cookie:",
        temp_cookie
    )

    print(
        "EJS: ejs:github"
    )

    print(
        "JavaScript Runtime:",
        DENO_PATH
    )

    print(
        "noplaylist:",
        ydl_opts["noplaylist"]
    )

    print(
        "skip_download:",
        ydl_opts["skip_download"]
    )

    print("==========================================")

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        print(
            "extract_info開始"
        )

        info = ydl.extract_info(
            url,
            download=False
        )

    if not info:
        raise Exception(
            "YouTube情報を取得できませんでした"
        )

    return info

finally:
    remove_cookie_file(
        temp_cookie
    )
```

def register_check(app):

```
@app.route(
    "/check",
    methods=["POST"]
)
def check():

    print("==========================================")
    print("/check 呼び出し")
    print("==========================================")

    try:
        diagnose_environment()

        data = request.get_json(
            silent=True
        )

        if not data:
            return jsonify({
                "success": False,
                "message": "JSONデータがありません"
            })

        url = data.get(
            "url"
        )

        if not url:
            return jsonify({
                "success": False,
                "message": "URLがありません"
            })

        print(
            "受信URL:",
            url
        )

        info = get_youtube_info(
            url
        )

        formats = info.get(
            "formats",
            []
        )

        audio_formats = []

        for f in formats:

            acodec = f.get(
                "acodec"
            )

            vcodec = f.get(
                "vcodec"
            )

            if (
                acodec
                and acodec != "none"
                and (
                    not vcodec
                    or vcodec == "none"
                )
            ):
                audio_formats.append(
                    f
                )

        print("==========================================")
        print("YouTube情報取得成功")
        print("==========================================")

        print(
            "タイトル:",
            info.get("title")
        )

        print(
            "再生時間:",
            info.get("duration")
        )

        print(
            "format数:",
            len(formats)
        )

        print(
            "音声format数:",
            len(audio_formats)
        )

        print("==========================================")

        return jsonify({
            "success": True,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "format_count": len(formats),
            "audio_format_count": len(
                audio_formats
            )
        })

    except Exception as e:

        print("==========================================")
        print("/check エラー")
        print("==========================================")

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print("==========================================")

        return jsonify({
            "success": False,
            "message": str(e)
        })

