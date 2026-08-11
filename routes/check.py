from flask import request, jsonify
import os
import shutil
import tempfile
import yt_dlp

from routes.status import jobs

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
print("check.py 起動")
print("==========================================")
print("Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("元Cookieファイル:")
print(ORIGINAL_COOKIE_FILE)
print("==========================================")

def remove_cookie_file(cookie_file):
if not cookie_file:
return


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


def prepare_cookie_file():
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
print("yt-dlp用Cookieファイル作成OK")
print("一時Cookie:", temp_cookie_file)
print("サイズ:", file_size, "bytes")
print("Cookieデータ行数:", cookie_count)
print(
    "YouTube/Google Cookie数:",
    youtube_cookie_count
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


def get_deno_path():
render_deno = (
"/opt/render/project/src/.deno/bin/deno"
)


if os.path.isfile(render_deno):
    return render_deno

path_deno = shutil.which("deno")

if path_deno:
    return path_deno

return None


def get_ydl_base_options():
cookie_file = prepare_cookie_file()


deno_path = get_deno_path()

if deno_path:
    js_runtimes = {
        "deno": {
            "path": deno_path
        }
    }

    print("Deno:", deno_path)

else:
    js_runtimes = {
        "deno": {}
    }

    print(
        "WARNING: Denoが見つかりません"
    )

options = {
    "cookiefile": cookie_file,
    "noplaylist": True,
    "js_runtimes": js_runtimes,
    "remote_components": {
        "ejs:github"
    }
}

print("==========================================")
print("yt-dlp基本設定")
print("==========================================")
print(
    "Cookie:",
    cookie_file
)
print(
    "Deno:",
    deno_path
)
print(
    "js_runtimes:",
    js_runtimes
)
print(
    "remote_components:",
    options["remote_components"]
)
print("==========================================")

return options


def get_video_info(url):
temp_cookie = None


try:
    print("==========================================")
    print("YouTube情報取得開始")
    print("==========================================")
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
        "skip_download": True,
        "noplaylist": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/146.0.0.0 "
                "Safari/537.36"
            ),
            "Accept": (
                "text/html,"
                "application/xhtml+xml,"
                "application/xml;q=0.9,"
                "*/*;q=0.8"
            ),
            "Accept-Language": (
                "en-US,en;q=0.5"
            ),
            "Sec-Fetch-Mode": "navigate"
        }
    })

    print("==========================================")
    print("extract_info開始")
    print("==========================================")

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    if not info:
        raise Exception(
            "YouTube情報を取得できませんでした"
        )

    print("==========================================")
    print("YouTube情報取得成功")
    print("==========================================")
    print(
        "動画タイトル:",
        info.get("title")
    )
    print(
        "動画ID:",
        info.get("id")
    )
    print(
        "再生時間:",
        info.get("duration")
    )
    print(
        "チャンネル:",
        info.get("uploader")
    )
    print(
        "thumbnail:",
        info.get("thumbnail")
    )
    print("==========================================")

    return info

finally:
    remove_cookie_file(
        temp_cookie
    )


def register_check(app):


@app.route(
    "/check",
    methods=["POST"]
)
def check():

    print("==========================================")
    print("/check 呼び出し")
    print("==========================================")

    try:
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

        url = str(url).strip()

        print("==========================================")
        print("受信URL:", url)
        print("==========================================")

        if (
            "youtube.com/" not in url
            and "youtu.be/" not in url
        ):
            return jsonify({
                "success": False,
                "message": "YouTube URLではありません"
            })

        info = get_video_info(
            url
        )

        result = {
            "success": True,
            "url": url,
            "id": info.get("id"),
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "uploader": info.get("uploader"),
            "channel": info.get("channel"),
            "webpage_url": info.get(
                "webpage_url",
                url
            )
        }

        print("==========================================")
        print("/check 成功")
        print("TITLE:", info.get("title"))
        print("ID:", info.get("id"))
        print("DURATION:", info.get("duration"))
        print("==========================================")

        return jsonify(
            result
        )

    except yt_dlp.utils.DownloadError as e:

        print("==========================================")
        print("/check YouTube取得失敗")
        print("ERROR TYPE: DownloadError")
        print("ERROR:", repr(e))
        print("==========================================")

        return jsonify({
            "success": False,
            "message": str(e)
        })

    except Exception as e:

        print("==========================================")
        print("/check エラー")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        print("==========================================")

        return jsonify({
            "success": False,
            "message": str(e)
        })

