from flask import request, jsonify
import yt_dlp
import os
import shutil
import tempfile

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

if os.environ.get("RENDER") == "true":
ORIGINAL_COOKIE_FILE = RENDER_COOKIE_FILE
else:
ORIGINAL_COOKIE_FILE = LOCAL_COOKIE_FILE

print("==========================================")
print("Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("元Cookieファイル:")
print(ORIGINAL_COOKIE_FILE)
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
if not os.path.exists(
ORIGINAL_COOKIE_FILE
):
raise Exception(
"Cookieファイルが見つかりません: "
+ ORIGINAL_COOKIE_FILE
)

```
original_size = os.path.getsize(
    ORIGINAL_COOKIE_FILE
)

if original_size == 0:
    raise Exception(
        "Cookieファイルが空です: "
        + ORIGINAL_COOKIE_FILE
    )

temp_file = tempfile.NamedTemporaryFile(
    mode="wb",
    suffix=".txt",
    prefix="y2conv_cookies_",
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
    "yt-dlp用Cookieファイル:",
    temp_cookie_file
)
print(
    "Cookieデータ行数:",
    cookie_count
)
print(
    "YouTube/Google Cookie数:",
    youtube_cookie_count
)
print(
    "Cookieサイズ:",
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
        "WARNING: YouTube/Google Cookieが見つかりません"
    )

return temp_cookie_file
```

def get_ydl_base_options():
cookie_file = prepare_cookie_file()

```
return {
    "cookiefile": cookie_file,
    "noplaylist": True,
    "js_runtimes": {
        "deno": {}
    },
    "remote_components": {
        "ejs": "github"
    }
}
```

def diagnose_formats(url):
temp_cookie = None

```
try:
    print("==========================================")
    print("YouTube情報取得開始")
    print("URL:", url)
    print("==========================================")

    ydl_opts = get_ydl_base_options()

    temp_cookie = ydl_opts.get(
        "cookiefile"
    )

    ydl_opts.update({
        "quiet": False,
        "no_warnings": False,
        "verbose": True,
        "skip_download": True
    })

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

    print("==========================================")
    print(
        "動画タイトル:",
        info.get("title")
    )
    print(
        "再生時間:",
        info.get("duration"),
        "秒"
    )
    print("==========================================")

    formats = info.get(
        "formats",
        []
    )

    print(
        "利用可能format数:",
        len(formats)
    )

    print("==========================================")
    print("利用可能format一覧")
    print("==========================================")

    for f in formats:
        print(
            "ID=",
            f.get("format_id"),
            "EXT=",
            f.get("ext"),
            "VCODEC=",
            f.get("vcodec"),
            "ACODEC=",
            f.get("acodec"),
            "RES=",
            f.get("resolution"),
            "ABR=",
            f.get("abr")
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
    methods=["GET", "POST"]
)
def check():

    temp_cookie = None

    try:
        if request.method == "POST":
            data = request.get_json(
                silent=True
            ) or {}

            url = data.get(
                "url"
            )

        else:
            url = request.args.get(
                "url"
            )

        if not url:
            return jsonify({
                "success": False,
                "message": "URLがありません"
            }), 400

        print("==========================================")
        print("CHECK開始")
        print("URL:", url)
        print("==========================================")

        info = diagnose_formats(
            url
        )

        return jsonify({
            "success": True,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "format_count": len(
                info.get("formats", [])
            )
        })

    except Exception as e:

        print("==========================================")
        print("CHECKエラー")
        print("ERROR:", repr(e))
        print("==========================================")

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        remove_cookie_file(
            temp_cookie
        )
```
