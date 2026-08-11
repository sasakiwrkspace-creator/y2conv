from flask import request, jsonify
import yt_dlp
import uuid
import threading
import os
import subprocess

from routes.status import jobs
from cleanup import cleanup_downloads


# ==========================================================
# Cookieファイル
# ==========================================================

# Render Secret File
RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ==========================================================
# プロジェクトのルートディレクトリ
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================================
# ローカルCookie
# ==========================================================

LOCAL_COOKIE_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt"
)


# ==========================================================
# Cookieファイル選択
#
# check.py と同じ方式
#
# Render:
# /etc/secrets/cookies.txt
#
# ローカル:
# プロジェクト直下/cookies.txt
# ==========================================================

if os.environ.get("RENDER") == "true":
    COOKIE_FILE = RENDER_COOKIE_FILE
else:
    COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("convert.py Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("使用するCookieファイル:")
print(COOKIE_FILE)
print("==========================================")


# ==========================================================
# Cookie確認
#
# check.py と同じ方式
# ==========================================================

def check_cookie_file():

    if not os.path.exists(COOKIE_FILE):

        raise Exception(
            f"Cookieファイルが見つかりません: {COOKIE_FILE}"
        )

    file_size = os.path.getsize(
        COOKIE_FILE
    )

    print("==========================================")
    print("Cookieファイル確認")
    print("==========================================")

    print(
        "Cookieファイル:",
        COOKIE_FILE
    )

    print(
        "Cookieファイルサイズ:",
        file_size,
        "bytes"
    )

    if file_size == 0:

        raise Exception(
            f"Cookieファイルが空です: {COOKIE_FILE}"
        )

    cookie_count = 0
    youtube_cookie_count = 0

    try:

        with open(
            COOKIE_FILE,
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

                cookie_count += 1

                fields = line.split("\t")

                if len(fields) >= 7:

                    domain = fields[0].lower()

                    if (
                        "youtube.com" in domain
                        or "google.com" in domain
                    ):

                        youtube_cookie_count += 1

    except Exception as e:

        raise Exception(
            f"Cookieファイル読み込み失敗: {e}"
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

        raise Exception(
            "Cookieデータが0件です"
        )

    if youtube_cookie_count == 0:

        print(
            "WARNING: "
            "YouTube/Google Cookieが見つかりません"
        )


# ==========================================================
# yt-dlp共通設定
#
# check.py と同じCookie方式
# ==========================================================

def get_ydl_base_options():

    check_cookie_file()

    return {

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        "cookiefile":
        COOKIE_FILE,

        # --------------------------------------------------
        # EJS challenge solver
        # --------------------------------------------------

        "remote_components": {
            "ejs": "github"
        },

        # --------------------------------------------------
        # JavaScript Runtime
        # --------------------------------------------------

        "js_runtimes": {
            "deno": {}
        },

        # --------------------------------------------------
        # Playlist無効
        # --------------------------------------------------

        "noplaylist":
        True

    }


# ==========================================================
# YouTube情報・format診断
# ==========================================================

def diagnose_formats(url):

    print("==========================================")
    print("YouTube情報取得開始")
    print("URL:", url)
    print("==========================================")

    ydl_opts = get_ydl_base_options()

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
    print("yt-dlp設定")
    print("==========================================")

    print(
        "yt-dlp version:",
        yt_dlp.version.__version__
    )

    print(
        "Cookie:",
        COOKIE_FILE
    )

    print(
        "EJS:",
        "github"
    )

    print(
        "JavaScript Runtime:",
        "deno"
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

    # ======================================================
    # 基本情報
    # ======================================================

    title = info.get(
        "title"
    )

    duration = info.get(
        "duration"
    )

    print("==========================================")
    print(
        "動画タイトル:",
        title
    )
    print(
        "再生時間:",
        duration,
        "秒"
    )
    print("==========================================")

    # ======================================================
    # Format一覧
    # ======================================================

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

    # ======================================================
    # 音声format
    # ======================================================

    print("==========================================")
    print("音声format一覧")
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


# ==========================================================
# MP3変換
# ==========================================================

def download_mp3(
    url,
    output_dir
):

    print("==========================================")
    print("MP3ダウンロード開始")
    print("==========================================")

    ydl_opts = get_ydl_base_options()

    ydl_opts.update({

        # --------------------------------------------------
        # 音声
        #
        # 140があれば140
        # なければbestaudio
        # 最後にbest
        # --------------------------------------------------

        "format":
        "140/bestaudio/best",

        # --------------------------------------------------
        # 出力
        # --------------------------------------------------

        "outtmpl":
        os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        ),

        # --------------------------------------------------
        # MP3変換
        # --------------------------------------------------

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
        "140/bestaudio/best"
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

        filename = ydl.prepare_filename(
            info
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

    file_size = os.path.getsize(
        mp3_file
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


# ==========================================================
# MP4変換
# ==========================================================

def download_mp4(
    url,
    output_dir
):

    print("==========================================")
    print("MP4ダウンロード開始")
    print("==========================================")

    ydl_opts = get_ydl_base_options()

    ydl_opts.update({

        # --------------------------------------------------
        # MP4動画 + M4A音声
        # --------------------------------------------------

        "format":
        "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",

        # --------------------------------------------------
        # MP4として結合
        # --------------------------------------------------

        "merge_output_format":
        "mp4",

        # --------------------------------------------------
        # 出力
        # --------------------------------------------------

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

        filename = ydl.prepare_filename(
            info
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

    file_size = os.path.getsize(
        mp4_file
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


# ==========================================================
# MP3カット
# ==========================================================

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


# ==========================================================
# MP4カット
# ==========================================================

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


# ==========================================================
# 変換処理
# ==========================================================

def convert_task(
    job_id,
    url,
    outputs,
    start_time=None,
    end_time=None
):

    try:

        # ==================================================
        # Job running
        # ==================================================

        jobs[job_id] = {
            "status": "running"
        }

        print("==========================================")
        print("変換開始:", job_id)
        print("URL:", url)
        print("OUTPUTS:", outputs)
        print("==========================================")

        # ==================================================
        # Cookie確認
        #
        # check.py と同じ方式
        # ==================================================

        check_cookie_file()

        # ==================================================
        # 古いファイル削除
        # ==================================================

        cleanup_downloads()

        # ==================================================
        # 出力ディレクトリ
        # ==================================================

        output_dir = "downloads"

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        files = []

        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in outputs:

            # ----------------------------------------------
            # format診断
            # ----------------------------------------------

            try:

                diagnose_formats(
                    url
                )

            except Exception as e:

                print(
                    "format診断失敗:",
                    repr(e)
                )

                # 診断失敗しても
                # 実際のダウンロードは試す

            # ----------------------------------------------
            # MP3取得
            # ----------------------------------------------

            mp3_file = download_mp3(
                url,
                output_dir
            )

            # ----------------------------------------------
            # 時間指定
            # ----------------------------------------------

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

        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in outputs:

            mp4_file = download_mp4(
                url,
                output_dir
            )

            # ----------------------------------------------
            # 時間指定
            # ----------------------------------------------

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

        # ==================================================
        # 完了
        # ==================================================

        jobs[job_id] = {

            "status":
            "complete",

            "files":
            files

        }

        print("==========================================")
        print("変換完了")
        print("JOB:", job_id)
        print("FILES:", files)
        print("==========================================")

    # ======================================================
    # エラー
    # ======================================================

    except Exception as e:

        print("==========================================")
        print("変換エラー")
        print("JOB:", job_id)
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        print("==========================================")

        jobs[job_id] = {

            "status":
            "error",

            "message":
            str(e)

        }


# ==========================================================
# /convert
# ==========================================================

def register_convert(app):

    @app.route(
        "/convert",
        methods=["POST"]
    )
    def convert():

        try:

            # ==================================================
            # JSON
            # ==================================================

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

            # ==================================================
            # URL
            # ==================================================

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

            # ==================================================
            # outputs
            # ==================================================

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

            # ==================================================
            # 有効な出力形式だけ残す
            # ==================================================

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

            # ==================================================
            # 時間指定
            # ==================================================

            start_time = data.get(
                "start_time"
            )

            end_time = data.get(
                "end_time"
            )

            # ==================================================
            # Job ID
            # ==================================================

            job_id = str(
                uuid.uuid4()
            )

            # ==================================================
            # Jobを先に登録
            # ==================================================

            jobs[job_id] = {

                "status":
                "queued"

            }

            print("==========================================")
            print("JOB登録:", job_id)
            print("URL:", url)
            print("OUTPUTS:", valid_outputs)
            print("START:", start_time)
            print("END:", end_time)
            print("==========================================")

            # ==================================================
            # Thread
            # ==================================================

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

            # ==================================================
            # Job ID返却
            # ==================================================

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
