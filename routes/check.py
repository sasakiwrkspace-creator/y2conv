from flask import request, jsonify
import yt_dlp
import os
import shutil
import tempfile

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

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"

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
print("==========================================")
print("Cookieファイル準備")
print("==========================================")


print(
    "元Cookieファイル:",
    ORIGINAL_COOKIE_FILE
)

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
    if os.path.exists(
        temp_cookie_file
    ):
        os.remove(
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

            if not line:
                continue

            if line.startswith("#"):
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
print(
    "一時Cookie:",
    temp_cookie_file
)
print(
    "サイズ:",
    file_size,
    "bytes"
)
print(
    "Cookieデータ行数:",
    cookie_count
)
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


def get_ydl_base_options():


cookie_file = prepare_cookie_file()

js_runtime_config = {}

if os.path.exists(
    DENO_PATH
):

    js_runtime_config = {
        "deno": {
            "executable": DENO_PATH
        }
    }

    print("==========================================")
    print("Deno確認")
    print("==========================================")
    print(
        "Deno:",
        DENO_PATH
    )
    print(
        "Deno存在:",
        True
    )
    print("==========================================")

else:

    js_runtime_config = {
        "deno": {}
    }

    print("==========================================")
    print("Deno確認")
    print("==========================================")
    print(
        "Deno:",
        DENO_PATH
    )
    print(
        "Deno存在:",
        False
    )
    print("==========================================")

options = {
    "cookiefile": cookie_file,
    "noplaylist": True,
    "js_runtimes": js_runtime_config,
    "remote_components": {
        "ejs:github"
    }
}

print("==========================================")
print("yt-dlp基本設定")
print("==========================================")
print(
    "yt-dlp version:",
    yt_dlp.version.__version__
)
print(
    "Cookie:",
    cookie_file
)
print(
    "js_runtimes:",
    options["js_runtimes"]
)
print(
    "remote_components:",
    options["remote_components"]
)
print(
    "noplaylist:",
    options["noplaylist"]
)
print("==========================================")

return options


def diagnose_formats(url):


temp_cookie = None

try:

    print("==========================================")
    print("YouTube情報取得開始")
    print("==========================================")
    print(
        "URL:",
        url
    )
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

    try:

        print("==========================================")
        print("/check 呼び出し")
        print("==========================================")

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

        info = diagnose_formats(
            url
        )

        formats = info.get(
            "formats",
            []
        )

        has_audio = False
        has_video = False

        for f in formats:

            vcodec = f.get(
                "vcodec"
            )

            acodec = f.get(
                "acodec"
            )

            if (
                acodec
                and acodec != "none"
            ):
                has_audio = True

            if (
                vcodec
                and vcodec != "none"
            ):
                has_video = True

        result = {
            "success": True,
            "title": info.get("title"),
            "video_id": info.get("id"),
            "duration": info.get("duration"),
            "has_audio": has_audio,
            "has_video": has_video,
            "format_count": len(formats)
        }

        print("==========================================")
        print("/check 成功")
        print("==========================================")

        print(
            "TITLE:",
            result["title"]
        )

        print(
            "VIDEO ID:",
            result["video_id"]
        )

        print(
            "DURATION:",
            result["duration"]
        )

        print(
            "HAS AUDIO:",
            result["has_audio"]
        )

        print(
            "HAS VIDEO:",
            result["has_video"]
        )

        print(
            "FORMAT COUNT:",
            result["format_count"]
        )

        print("==========================================")

        return jsonify(
            result
        )

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

