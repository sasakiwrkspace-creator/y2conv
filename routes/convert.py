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

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"
DENO_DIR = "/opt/render/project/src/.deno/bin"

if os.path.exists(DENO_DIR):


current_path = os.environ.get(
    "PATH",
    ""
)

if DENO_DIR not in current_path.split(
    os.pathsep
):

    os.environ["PATH"] = (
        DENO_DIR
        + os.pathsep
        + current_path
    )


if os.environ.get("RENDER") == "true":


ORIGINAL_COOKIE_FILE = (
    RENDER_COOKIE_FILE
)


else:


ORIGINAL_COOKIE_FILE = (
    LOCAL_COOKIE_FILE
)


print("==========================================")
print("Cookie設定")
print(
"RENDER:",
os.environ.get("RENDER")
)
print(
"元Cookieファイル:",
ORIGINAL_COOKIE_FILE
)
print("==========================================")

print("==========================================")
print("Deno設定")
print(
"Deno:",
DENO_PATH
)
print(
"Deno exists:",
os.path.exists(DENO_PATH)
)
print(
"Deno executable:",
os.access(
DENO_PATH,
os.X_OK
)
)
print("==========================================")

def remove_cookie_file(
cookie_file
):


if not cookie_file:
    return

try:

    if os.path.exists(
        cookie_file
    ):

        os.remove(
            cookie_file
        )

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


print("==========================================")
print(
    "元Cookieファイル確認OK"
)
print(
    "ファイル:",
    ORIGINAL_COOKIE_FILE
)
print(
    "サイズ:",
    original_size,
    "bytes"
)
print("==========================================")


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


temp_cookie_file = (
    temp_file.name
)


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


print("==========================================")
print(
    "yt-dlp用Cookieファイル作成OK"
)
print(
    "一時Cookie:",
    temp_cookie_file
)
print(
    "サイズ:",
    file_size,
    "bytes"
)
print("==========================================")


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


            fields = line.split(
                "\t"
            )


            if len(fields) >= 7:

                cookie_count += 1


                domain = (
                    fields[0].lower()
                )


                if (
                    "youtube.com"
                    in domain
                    or
                    "google.com"
                    in domain
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


def get_ydl_base_options():


cookie_file = (
    prepare_cookie_file()
)


return {

    "cookiefile":
    cookie_file,


    "noplaylist":
    True,


    "js_runtimes": {

        "deno":
        DENO_PATH

    },


    "remote_components": {

        "ejs:github"

    }

}


def diagnose_formats(
url
):


temp_cookie = None


try:

    print("==========================================")
    print(
        "YouTube情報取得開始"
    )
    print(
        "URL:",
        url
    )
    print("==========================================")


    ydl_opts = (
        get_ydl_base_options()
    )


    temp_cookie = (
        ydl_opts.get(
            "cookiefile"
        )
    )


    ydl_opts.update({

        "quiet":
        False,

        "no_warnings":
        False,

        "verbose":
        True,

        "skip_download":
        True

    })


    print("==========================================")
    print(
        "yt-dlp設定"
    )
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
    print(
        "利用可能format一覧"
    )
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
    print(
        "音声format一覧"
    )
    print("==========================================")


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


            print(
                "AUDIO",
                "ID=",
                f.get("format_id"),
                "EXT=",
                f.get("ext"),
                "ACODEC=",
                f.get("acodec"),
                "ABR=",
                f.get("abr"),
                "ASR=",
                f.get("asr")
            )


    print("==========================================")
    print(
        "音声format数:",
        len(audio_formats)
    )
    print("==========================================")


    return info


finally:

    remove_cookie_file(
        temp_cookie
    )


def download_mp3(
url,
output_dir
):


temp_cookie = None


try:

    print("==========================================")
    print(
        "MP3ダウンロード開始"
    )
    print("==========================================")


    ydl_opts = (
        get_ydl_base_options()
    )


    temp_cookie = (
        ydl_opts.get(
            "cookiefile"
        )
    )


    ydl_opts.update({

        "format":
        "bestaudio/best",


        "outtmpl":
        os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        ),


        "postprocessors": [

            {

                "key":
                "FFmpegExtractAudio",

                "preferredcodec":
                "mp3",

                "preferredquality":
                "192"

            }

        ]

    })


    print(
        "MP3 format:",
        "bestaudio/best"
    )


    print(
        "MP3品質:",
        "192kbps"
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


        filename = (
            ydl.prepare_filename(
                info
            )
        )


    mp3_file = (
        os.path.splitext(
            filename
        )[0]
        + ".mp3"
    )


    if not os.path.exists(
        mp3_file
    ):

        raise Exception(
            "MP3ファイルが作成されませんでした: "
            + mp3_file
        )


    file_size = (
        os.path.getsize(
            mp3_file
        )
    )


    print(
        "MP3完成:",
        mp3_file
    )


    print(
        "MP3サイズ:",
        file_size,
        "bytes"
    )


    return mp3_file


finally:

    remove_cookie_file(
        temp_cookie
    )


def download_mp4(
url,
output_dir
):


temp_cookie = None


try:

    print("==========================================")
    print(
        "MP4ダウンロード開始"
    )
    print("==========================================")


    ydl_opts = (
        get_ydl_base_options()
    )


    temp_cookie = (
        ydl_opts.get(
            "cookiefile"
        )
    )


    ydl_opts.update({

        "format":
        "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",


        "merge_output_format":
        "mp4",


        "outtmpl":
        os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        )

    })


    print(
        "MP4 format:",
        "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
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


        filename = (
            ydl.prepare_filename(
                info
            )
        )


    mp4_file = (
        os.path.splitext(
            filename
        )[0]
        + ".mp4"
    )


    if not os.path.exists(
        mp4_file
    ):

        raise Exception(
            "MP4ファイルが作成されませんでした: "
            + mp4_file
        )


    file_size = (
        os.path.getsize(
            mp4_file
        )
    )


    print(
        "MP4完成:",
        mp4_file
    )


    print(
        "MP4サイズ:",
        file_size,
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
print(
    "MP3時間指定カット開始"
)
print(
    "開始:",
    start_time
)
print(
    "終了:",
    end_time
)
print("==========================================")


cut_file = (
    os.path.splitext(
        mp3_file
    )[0]
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

    print(
        result.stderr
    )

    raise Exception(
        "ffmpeg処理失敗(mp3)"
    )


if not os.path.exists(
    cut_file
):

    raise Exception(
        "カット後のMP3ファイルが作成されませんでした"
    )


if os.path.exists(
    mp3_file
):

    os.remove(
        mp3_file
    )


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
print(
    "MP4時間指定カット開始"
)
print(
    "開始:",
    start_time
)
print(
    "終了:",
    end_time
)
print("==========================================")


cut_file = (
    os.path.splitext(
        mp4_file
    )[0]
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

    print(
        result.stderr
    )

    raise Exception(
        "ffmpeg処理失敗(mp4)"
    )


if not os.path.exists(
    cut_file
):

    raise Exception(
        "カット後のMP4ファイルが作成されませんでした"
    )


if os.path.exists(
    mp4_file
):

    os.remove(
        mp4_file
    )


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
    print(
        "変換開始:",
        job_id
    )
    print(
        "URL:",
        url
    )
    print(
        "OUTPUTS:",
        outputs
    )
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

        "status":
        "complete",

        "files":
        files

    }


    print("==========================================")
    print(
        "変換完了"
    )
    print(
        "JOB:",
        job_id
    )
    print(
        "FILES:",
        files
    )
    print("==========================================")


except Exception as e:

    print("==========================================")
    print(
        "変換エラー"
    )
    print(
        "JOB:",
        job_id
    )
    print(
        "ERROR TYPE:",
        type(e).__name__
    )
    print(
        "ERROR:",
        repr(e)
    )
    print("==========================================")


    jobs[job_id] = {

        "status":
        "error",

        "message":
        str(e)

    }


def register_convert(app):


@app.route(
    "/convert",
    methods=["POST"]
)
def convert():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({

                "success":
                False,

                "message":
                "JSONデータがありません"

            })


        url = data.get(
            "url"
        )


        if not url:

            return jsonify({

                "success":
                False,

                "message":
                "URLがありません"

            })


        outputs = data.get(
            "outputs",
            []
        )


        if not outputs:

            return jsonify({

                "success":
                False,

                "message":
                "出力形式が指定されていません"

            })


        valid_outputs = []


        for output in outputs:

            if output in [
                "mp3",
                "mp4"
            ]:

                if output not in valid_outputs:

                    valid_outputs.append(
                        output
                    )


        if not valid_outputs:

            return jsonify({

                "success":
                False,

                "message":
                "mp3またはmp4を指定してください"

            })


        start_time = data.get(
            "start_time"
        )


        end_time = data.get(
            "end_time"
        )


        job_id = str(
            uuid.uuid4()
        )


        jobs[job_id] = {

            "status":
            "queued"

        }


        print("==========================================")
        print(
            "JOB登録:",
            job_id
        )
        print(
            "URL:",
            url
        )
        print(
            "OUTPUTS:",
            valid_outputs
        )
        print(
            "START:",
            start_time
        )
        print(
            "END:",
            end_time
        )
        print("==========================================")


        thread = threading.Thread(

            target=convert_task,

            args=(

                job_id,

                url,

                valid_outputs,

                start_time,

                end_time

            )

        )


        thread.daemon = True


        thread.start()


        return jsonify({

            "success":
            True,

            "job_id":
            job_id

        })


    except Exception as e:

        print(
            "convertエラー:",
            repr(e)
        )


        return jsonify({

            "success":
            False,

            "message":
            str(e)

        })

