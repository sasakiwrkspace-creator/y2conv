from flask import request, jsonify
import yt_dlp
import uuid
import threading
import os
import subprocess
import shutil
import tempfile

from routes.status import jobs
from cleanup import cleanup_downloads

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

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"

print("==========================================")
print("Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("元Cookieファイル:")
print(ORIGINAL_COOKIE_FILE)
print("==========================================")

def prepare_cookie_file():
if not os.path.exists(ORIGINAL_COOKIE_FILE):
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
    if os.path.exists(temp_cookie_file):
        os.remove(temp_cookie_file)
    raise

if not os.path.exists(temp_cookie_file):
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


def get_ydl_base_options():
cookie_file = prepare_cookie_file()


options = {
    "cookiefile": cookie_file,
    "noplaylist": True,
    "remote_components": {
        "ejs": "github"
    }
}

if os.path.exists(DENO_PATH):
    options["js_runtimes"] = {
        "deno": {
            "path": DENO_PATH
        }
    }

    print("Deno:")
    print(DENO_PATH)
    print("Deno存在確認: OK")

else:
    options["js_runtimes"] = {
        "deno": {}
    }

    print(
        "WARNING: 指定Denoが見つかりません:",
        DENO_PATH
    )

print("==========================================")
print("yt-dlp基本設定")
print("==========================================")
print(
    "Cookie:",
    cookie_file
)
print(
    "noplaylist:",
    True
)
print(
    "remote_components:",
    options["remote_components"]
)
print(
    "js_runtimes:",
    options["js_runtimes"]
)
print("==========================================")

return options


def diagnose_formats(url):
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
        "skip_download": True
    })

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        print("extract_info開始")

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
    print(
        "動画ID:",
        info.get("id")
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


def download_mp3(url, output_dir):
temp_cookie = None


try:
    print("==========================================")
    print("MP3ダウンロード開始")
    print("==========================================")
    print("URL:", url)
    print("==========================================")

    ydl_opts = get_ydl_base_options()

    temp_cookie = ydl_opts.get(
        "cookiefile"
    )

    ydl_opts.update({
        "format": "bestaudio/best",
        "outtmpl": os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        ),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }
        ]
    })

    print(
        "MP3 format:",
        "bestaudio/best"
    )

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        if not info:
            raise Exception(
                "YouTube情報を取得できませんでした"
            )

        filename = ydl.prepare_filename(
            info
        )

    mp3_file = (
        os.path.splitext(filename)[0]
        + ".mp3"
    )

    if not os.path.exists(mp3_file):
        raise Exception(
            "MP3ファイルが作成されませんでした: "
            + mp3_file
        )

    print(
        "MP3完成:",
        mp3_file
    )

    print(
        "MP3サイズ:",
        os.path.getsize(mp3_file),
        "bytes"
    )

    return mp3_file

finally:
    remove_cookie_file(
        temp_cookie
    )


def download_mp4(url, output_dir):
temp_cookie = None


try:
    print("==========================================")
    print("MP4ダウンロード開始")
    print("==========================================")
    print("URL:", url)
    print("==========================================")

    ydl_opts = get_ydl_base_options()

    temp_cookie = ydl_opts.get(
        "cookiefile"
    )

    ydl_opts.update({
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        )
    })

    print(
        "MP4 format:",
        "bestvideo*+bestaudio/best"
    )

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        if not info:
            raise Exception(
                "YouTube情報を取得できませんでした"
            )

        filename = ydl.prepare_filename(
            info
        )

    mp4_file = (
        os.path.splitext(filename)[0]
        + ".mp4"
    )

    if not os.path.exists(mp4_file):
        raise Exception(
            "MP4ファイルが作成されませんでした: "
            + mp4_file
        )

    print(
        "MP4完成:",
        mp4_file
    )

    print(
        "MP4サイズ:",
        os.path.getsize(mp4_file),
        "bytes"
    )

    return mp4_file

finally:
    remove_cookie_file(
        temp_cookie
    )


def cut_mp3(
mp3_file,
start_time,
end_time
):
print("==========================================")
print("MP3時間指定カット開始")
print("開始:", start_time)
print("終了:", end_time)
print("==========================================")


cut_file = (
    os.path.splitext(mp3_file)[0]
    + "_cut.mp3"
)

result = subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i",
        mp3_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-c",
        "copy",
        cut_file
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

if result.returncode != 0:
    print(result.stderr)

    raise Exception(
        "ffmpeg処理失敗(mp3)"
    )

if not os.path.exists(cut_file):
    raise Exception(
        "カット後のMP3ファイルが作成されませんでした"
    )

if os.path.exists(mp3_file):
    os.remove(mp3_file)

os.rename(
    cut_file,
    mp3_file
)

print(
    "MP3時間指定カット完了"
)


def cut_mp4(
mp4_file,
start_time,
end_time
):
print("==========================================")
print("MP4時間指定カット開始")
print("開始:", start_time)
print("終了:", end_time)
print("==========================================")


cut_file = (
    os.path.splitext(mp4_file)[0]
    + "_cut.mp4"
)

result = subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i",
        mp4_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-c",
        "copy",
        cut_file
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

if result.returncode != 0:
    print(result.stderr)

    raise Exception(
        "ffmpeg処理失敗(mp4)"
    )

if not os.path.exists(cut_file):
    raise Exception(
        "カット後のMP4ファイルが作成されませんでした"
    )

if os.path.exists(mp4_file):
    os.remove(mp4_file)

os.rename(
    cut_file,
    mp4_file
)

print(
    "MP4時間指定カット完了"
)


def convert_task(
job_id,
url,
outputs,
start_time=None,
end_time=None
):
try:
jobs[job_id] = {
"status": "running"
}


    print("==========================================")
    print("変換開始:", job_id)
    print("URL:", url)
    print("OUTPUTS:", outputs)
    print("START:", start_time)
    print("END:", end_time)
    print("==========================================")

    cleanup_downloads()

    output_dir = "downloads"

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    files = []

    if "mp3" in outputs:
        try:
            diagnose_formats(
                url
            )
        except Exception as e:
            print(
                "format診断失敗:",
                repr(e)
            )

        mp3_file = download_mp3(
            url,
            output_dir
        )

        if (
            start_time
            and end_time
            and start_time < end_time
        ):
            cut_mp3(
                mp3_file,
                start_time,
                end_time
            )

        files.append(
            os.path.basename(
                mp3_file
            )
        )

    if "mp4" in outputs:
        mp4_file = download_mp4(
            url,
            output_dir
        )

        if (
            start_time
            and end_time
            and start_time < end_time
        ):
            cut_mp4(
                mp4_file,
                start_time,
                end_time
            )

        files.append(
            os.path.basename(
                mp4_file
            )
        )

    jobs[job_id] = {
        "status": "complete",
        "files": files
    }

    print("==========================================")
    print("変換完了")
    print("JOB:", job_id)
    print("FILES:", files)
    print("==========================================")

except Exception as e:
    print("==========================================")
    print("変換エラー")
    print("JOB:", job_id)
    print("ERROR:", repr(e))
    print("==========================================")

    jobs[job_id] = {
        "status": "error",
        "message": str(e)
    }


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

        duration = info.get(
            "duration"
        )

        title = info.get(
            "title"
        )

        video_id = info.get(
            "id"
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

        print("==========================================")
        print("YouTube情報取得成功")
        print("TITLE:", title)
        print("VIDEO ID:", video_id)
        print("DURATION:", duration)
        print("HAS AUDIO:", has_audio)
        print("HAS VIDEO:", has_video)
        print("FORMAT COUNT:", len(formats))
        print("==========================================")

        return jsonify({
            "success": True,
            "title": title,
            "video_id": video_id,
            "duration": duration,
            "has_audio": has_audio,
            "has_video": has_video,
            "format_count": len(formats)
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

