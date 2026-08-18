from flask import request, jsonify

import yt_dlp
from yt_dlp.utils import download_range_func

import uuid
import threading
import os
import shutil
import tempfile
import subprocess
import re
import time

from datetime import datetime

from routes.status import jobs
from cleanup import cleanup_downloads

from paths import (
    BASE_DIR,
    DOWNLOAD_DIR
)


# ==========================================================
# Render Cookie
# ==========================================================

RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ==========================================================
# ローカルCookie
# ==========================================================

LOCAL_COOKIE_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt"
)


# ==========================================================
# Deno
# ==========================================================

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"


# ==========================================================
# Cookieファイル選択
# ==========================================================

if os.environ.get("RENDER") == "true":

    SOURCE_COOKIE_FILE = RENDER_COOKIE_FILE

else:

    SOURCE_COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================", flush=True)
print("convert.py Cookie設定", flush=True)
print("RENDER:", os.environ.get("RENDER"), flush=True)
print("Cookie:", SOURCE_COOKIE_FILE, flush=True)
print("==========================================", flush=True)


# ==========================================================
# Cookie確認
# ==========================================================

def check_cookie_file():

    if not os.path.exists(
        SOURCE_COOKIE_FILE
    ):

        raise Exception(
            "Cookieファイルが見つかりません: "
            + SOURCE_COOKIE_FILE
        )


    file_size = os.path.getsize(
        SOURCE_COOKIE_FILE
    )


    print("==========================================", flush=True)
    print("Cookieファイル確認", flush=True)
    print("ファイル:", SOURCE_COOKIE_FILE, flush=True)
    print("サイズ:", file_size, "bytes", flush=True)
    print("==========================================", flush=True)


    if file_size == 0:

        raise Exception(
            "Cookieファイルが空です"
        )


# ==========================================================
# 一時Cookie作成
# ==========================================================

def create_temp_cookie_file():

    check_cookie_file()

    temp_cookie = None


    try:

        fd, temp_cookie = tempfile.mkstemp(
            prefix="y2conv_cookies_",
            suffix=".txt",
            dir="/tmp"
        )


        os.close(
            fd
        )


        shutil.copyfile(
            SOURCE_COOKIE_FILE,
            temp_cookie
        )


        print(
            "一時Cookie作成:",
            temp_cookie,
            flush=True
        )


        return temp_cookie


    except Exception:

        if (
            temp_cookie
            and
            os.path.exists(
                temp_cookie
            )
        ):

            try:

                os.remove(
                    temp_cookie
                )

            except Exception:

                pass


        raise


# ==========================================================
# 一時Cookie削除
# ==========================================================

def remove_temp_cookie_file(
    cookie_file
):

    if (
        cookie_file
        and
        os.path.exists(
            cookie_file
        )
    ):

        try:

            os.remove(
                cookie_file
            )


            print(
                "一時Cookie削除:",
                cookie_file,
                flush=True
            )


        except Exception as e:

            print(
                "WARNING: Cookie削除失敗:",
                repr(e),
                flush=True
            )


# ==========================================================
# Deno確認
# ==========================================================

def check_deno():

    if not os.path.isfile(
        DENO_PATH
    ):

        print(
            "Denoがありません:",
            DENO_PATH,
            flush=True
        )

        return False


    if not os.access(
        DENO_PATH,
        os.X_OK
    ):

        print(
            "Deno実行権限なし:",
            DENO_PATH,
            flush=True
        )

        return False


    return True


# ==========================================================
# 時間を秒へ変換
# ==========================================================

def time_to_seconds(
    value
):

    if value is None:

        return None


    value = str(
        value
    ).strip()


    if not value:

        return None


    parts = value.split(":")


    try:

        if len(parts) == 1:

            seconds = float(
                parts[0]
            )


            if seconds < 0:

                raise ValueError


            return seconds


        if len(parts) == 2:

            minutes = float(
                parts[0]
            )

            seconds = float(
                parts[1]
            )


            if (
                minutes < 0
                or seconds < 0
                or seconds >= 60
            ):

                raise ValueError


            return (
                minutes * 60
                + seconds
            )


        if len(parts) == 3:

            hours = float(
                parts[0]
            )

            minutes = float(
                parts[1]
            )

            seconds = float(
                parts[2]
            )


            if (
                hours < 0
                or minutes < 0
                or seconds < 0
                or minutes >= 60
                or seconds >= 60
            ):

                raise ValueError


            return (
                hours * 3600
                + minutes * 60
                + seconds
            )


        raise ValueError


    except Exception as e:

        raise ValueError(

            "時間形式が正しくありません: "
            + value

        ) from e


# ==========================================================
# 秒を HH:MM:SS へ変換
# ==========================================================

def seconds_to_time(
    seconds
):

    if seconds is None:

        return "00:00:00"


    try:

        seconds = int(
            round(
                float(seconds)
            )
        )

    except Exception:

        return "00:00:00"


    if seconds < 0:

        seconds = 0


    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = seconds % 60


    return (

        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"

    )


# ==========================================================
# 現在時刻
# ==========================================================

def get_current_time_text():

    return datetime.now().strftime(
        "%H:%M:%S"
    )


# ==========================================================
# FFmpeg確認
# ==========================================================

def check_ffmpeg():

    try:

        result = subprocess.run(

            [
                "ffmpeg",
                "-version"
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,

            timeout=10

        )


        return (
            result.returncode == 0
        )


    except Exception:

        return False


# ==========================================================
# FFprobe確認
# ==========================================================

def check_ffprobe():

    try:

        result = subprocess.run(

            [
                "ffprobe",
                "-version"
            ],

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,

            timeout=10

        )


        return (
            result.returncode == 0
        )


    except Exception:

        return False


# ==========================================================
# FFprobeで実際のファイル再生時間を取得
# ==========================================================

def get_media_duration(
    file_path
):

    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            "メディアファイルがありません: "
            + file_path
        )


    if not check_ffprobe():

        raise Exception(
            "ffprobeが利用できません"
        )


    command = [

        "ffprobe",

        "-v",
        "error",

        "-show_entries",
        "format=duration",

        "-of",
        "default=noprint_wrappers=1:nokey=1",

        file_path

    ]


    print(
        "DEBUG: ffprobe START",
        file_path,
        flush=True
    )


    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=60

        )

    except subprocess.TimeoutExpired as e:

        raise Exception(
            "ffprobeが60秒でタイムアウトしました"
        ) from e


    print(
        "DEBUG: ffprobe END",
        flush=True
    )


    if result.returncode != 0:

        raise Exception(

            "メディア再生時間取得失敗: "
            + result.stderr.strip()

        )


    try:

        return float(
            result.stdout.strip()
        )

    except Exception as e:

        raise Exception(
            "メディア再生時間を取得できませんでした"
        ) from e


# ==========================================================
# yt-dlp共通オプション
# ==========================================================

def get_ydl_base_options(
    temp_cookie,
    output_template
):

    options = {

        "cookiefile":
            temp_cookie,

        "noplaylist":
            True,

        "outtmpl":
            output_template,

        "quiet":
            False,

        "no_warnings":
            False,

        "noprogress":
            True,

        "restrictfilenames":
            False,

        # --------------------------------------------------
        # ネットワークタイムアウト
        # --------------------------------------------------

        "socket_timeout":
            30,

        # --------------------------------------------------
        # リトライ
        # --------------------------------------------------

        "retries":
            3,

        "fragment_retries":
            3,

        "extractor_retries":
            3

    }


    # ======================================================
    # Deno
    # ======================================================

    if check_deno():

        options["js_runtimes"] = {

            "deno": {

                "path":
                    DENO_PATH

            }

        }


        options["remote_components"] = {

            "ejs":
                "github"

        }


    return options


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_video_info(
    url,
    temp_cookie
):

    options = {

        "cookiefile":
            temp_cookie,

        "noplaylist":
            True,

        "quiet":
            True,

        "no_warnings":
            False,

        "socket_timeout":
            30,

        "retries":
            3,

        "extractor_retries":
            3

    }


    if check_deno():

        options["js_runtimes"] = {

            "deno": {

                "path":
                    DENO_PATH

            }

        }


        options["remote_components"] = {

            "ejs":
                "github"

        }


    print(
        "DEBUG: get_video_info START",
        flush=True
    )


    with yt_dlp.YoutubeDL(
        options
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )


    print(
        "DEBUG: get_video_info RETURNED",
        flush=True
    )


    if not info:

        raise Exception(
            "YouTube情報を取得できませんでした"
        )


    return info


# ==========================================================
# ソース動画・音声ダウンロード
#
# A方式:
#
# YouTube
#   ↓
# yt-dlpで指定範囲を取得
#   ↓
# source.webm
#   ↓
# 後段FFmpeg
#
# ここでは force_keyframes_at_cuts を使用しない。
# ==========================================================

def download_source(
    url,
    temp_cookie,
    source_dir,
    need_video,
    start_seconds=None,
    end_seconds=None
):

    os.makedirs(
        source_dir,
        exist_ok=True
    )


    source_template = os.path.join(

        source_dir,

        "source_%(id)s.%(ext)s"

    )


    options = get_ydl_base_options(

        temp_cookie,

        source_template

    )


    # ======================================================
    # MP4が必要
    # ======================================================

    if need_video:

        options["format"] = (

            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
            "best[ext=mp4]/"
            "best"

        )


        options["merge_output_format"] = "mp4"


    # ======================================================
    # MP3だけ
    # ======================================================

    else:

        options["format"] = (
            "bestaudio/best"
        )


    # ======================================================
    # 時間範囲
    #
    # A方式ではここでのみ範囲指定。
    #
    # force_keyframes_at_cuts は使用しない。
    # ======================================================

    if (
        start_seconds is not None
        and end_seconds is not None
    ):

        if end_seconds <= start_seconds:

            raise Exception(
                "ダウンロード範囲が正しくありません"
            )


        options["download_ranges"] = (
            download_range_func(
                None,
                [
                    (
                        start_seconds,
                        end_seconds
                    )
                ]
            )
        )


        print("==========================================", flush=True)
        print("yt-dlp時間範囲指定", flush=True)
        print(
            "開始:",
            start_seconds,
            "(",
            seconds_to_time(start_seconds),
            ")",
            flush=True
        )
        print(
            "終了:",
            end_seconds,
            "(",
            seconds_to_time(end_seconds),
            ")",
            flush=True
        )
        print(
            "範囲:",
            end_seconds - start_seconds,
            "秒",
            flush=True
        )
        print(
            "force_keyframes_at_cuts: False",
            flush=True
        )
        print("==========================================", flush=True)


    else:

        print("==========================================", flush=True)
        print("yt-dlp時間範囲指定なし", flush=True)
        print("Fullダウンロード", flush=True)
        print("==========================================", flush=True)


    print("==========================================", flush=True)
    print("YouTube元データダウンロード開始", flush=True)
    print("URL:", url, flush=True)
    print("need_video:", need_video, flush=True)
    print(
        "start_seconds:",
        start_seconds,
        flush=True
    )
    print(
        "end_seconds:",
        end_seconds,
        flush=True
    )
    print("==========================================", flush=True)


    # ======================================================
    # yt-dlp開始
    # ======================================================

    print(
        "DEBUG: yt-dlp START",
        flush=True
    )


    info = None


    try:

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            print(
                "DEBUG: YoutubeDL object created",
                flush=True
            )


            info = ydl.extract_info(

                url,

                download=True

            )


            print(
                "DEBUG: extract_info returned",
                flush=True
            )


    except Exception as e:

        print("==========================================", flush=True)
        print("DEBUG: yt-dlp EXCEPTION", flush=True)
        print(
            "TYPE:",
            type(e).__name__,
            flush=True
        )
        print(
            "ERROR:",
            repr(e),
            flush=True
        )
        print("==========================================", flush=True)

        raise


    print(
        "DEBUG: yt-dlp RETURNED",
        flush=True
    )


    if not info:

        raise Exception(
            "YouTubeダウンロード情報を取得できませんでした"
        )


    # ======================================================
    # ダウンロードされたファイルを探す
    # ======================================================

    print(
        "DEBUG: ダウンロードファイル検索開始",
        flush=True
    )


    files = []


    for filename in os.listdir(
        source_dir
    ):

        full_path = os.path.join(

            source_dir,

            filename

        )


        if not os.path.isfile(
            full_path
        ):

            continue


        if filename.startswith(
            "source_"
        ):

            files.append(
                full_path
            )


    print(
        "DEBUG: source files:",
        files,
        flush=True
    )


    if not files:

        raise Exception(
            "YouTube元ファイルが作成されませんでした"
        )


    # ======================================================
    # 一番新しいファイル
    # ======================================================

    source_file = max(

        files,

        key=os.path.getmtime

    )


    if os.path.getsize(
        source_file
    ) <= 0:

        raise Exception(
            "YouTube元ファイルが0 bytesです"
        )


    print("==========================================", flush=True)
    print("YouTube元データダウンロード完了", flush=True)
    print("ファイル:", source_file, flush=True)
    print(
        "サイズ:",
        os.path.getsize(source_file),
        "bytes",
        flush=True
    )


    if (
        start_seconds is not None
        and end_seconds is not None
    ):

        print(
            "取得予定範囲:",
            seconds_to_time(start_seconds),
            "～",
            seconds_to_time(end_seconds),
            flush=True
        )

    else:

        print(
            "取得範囲: Full",
            flush=True
        )


    print("==========================================", flush=True)


    return source_file, info


# ==========================================================
# 安全なファイル名作成
# ==========================================================

def safe_filename(
    title
):

    if not title:

        title = "youtube"


    title = str(
        title
    ).strip()


    title = re.sub(

        r'[\\/:*?"<>|]+',

        "_",

        title

    )


    title = title.replace(
        "\r",
        " "
    )

    title = title.replace(
        "\n",
        " "
    )


    title = title.strip(
        " ."
    )


    if not title:

        title = "youtube"


    return title


# ==========================================================
# FFmpegでMP3作成
#
# A方式:
#
# source_file はすでにyt-dlpで範囲指定済み。
#
# ここでは -ss / -t を使用しない。
# ==========================================================

def create_mp3(
    source_file,
    output_file
):

    print("==========================================", flush=True)
    print("MP3作成", flush=True)
    print("入力:", source_file, flush=True)
    print("出力:", output_file, flush=True)
    print("==========================================", flush=True)


    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    # ======================================================
    # 入力ファイル確認
    # ======================================================

    if not os.path.exists(
        source_file
    ):

        raise Exception(
            "MP3入力ファイルがありません: "
            + source_file
        )


    source_size = os.path.getsize(
        source_file
    )


    if source_size <= 0:

        raise Exception(
            "MP3入力ファイルが0 bytesです"
        )


    print(
        "MP3入力サイズ:",
        source_size,
        "bytes",
        flush=True
    )


    # ======================================================
    # FFmpeg
    #
    # 時間指定なし。
    # ======================================================

    command = [

        "ffmpeg",

        "-y",

        "-i",
        source_file,

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-b:a",
        "128k",

        "-map_metadata",
        "-1",

        output_file

    ]


    print(
        "FFmpeg:",
        command,
        flush=True
    )


    print(
        "DEBUG: FFmpeg MP3 START",
        flush=True
    )


    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=600

        )

    except subprocess.TimeoutExpired as e:

        print(
            "DEBUG: FFmpeg MP3 TIMEOUT",
            flush=True
        )


        if os.path.exists(
            output_file
        ):

            try:

                os.remove(
                    output_file
                )

            except Exception:

                pass


        raise Exception(
            "MP3作成が600秒でタイムアウトしました"
        ) from e


    print(
        "DEBUG: FFmpeg MP3 END",
        flush=True
    )


    if result.returncode != 0:

        print(
            "FFmpeg stderr:",
            result.stderr,
            flush=True
        )


        if os.path.exists(
            output_file
        ):

            try:

                os.remove(
                    output_file
                )

            except Exception:

                pass


        raise Exception(
            "MP3作成に失敗しました"
        )


    if not os.path.exists(
        output_file
    ):

        raise Exception(
            "MP3ファイルが作成されませんでした"
        )


    file_size = os.path.getsize(
        output_file
    )


    if file_size <= 0:

        raise Exception(
            "MP3ファイルが0 bytesです"
        )


    print("==========================================", flush=True)
    print("DEBUG: MP3保存先確認", flush=True)
    print(
        "output_file:",
        output_file,
        flush=True
    )
    print(
        "絶対パス:",
        os.path.abspath(output_file),
        flush=True
    )
    print(
        "exists:",
        os.path.exists(output_file),
        flush=True
    )

    if os.path.exists(output_file):

        print(
            "size:",
            os.path.getsize(output_file),
            flush=True
        )

    print(
        "DOWNLOAD_DIR:",
        DOWNLOAD_DIR,
        flush=True
    )


    try:

        print(
            "downloads内容:",
            os.listdir(DOWNLOAD_DIR),
            flush=True
        )

    except Exception as e:

        print(
            "downloads読み込み失敗:",
            repr(e),
            flush=True
        )


    print("==========================================", flush=True)


    print(
        "DEBUG: MP3 duration START",
        flush=True
    )


    actual_duration = get_media_duration(
        output_file
    )


    print(
        "DEBUG: MP3 duration END",
        flush=True
    )


    print("==========================================", flush=True)
    print("MP3作成完了", flush=True)
    print("ファイル:", output_file, flush=True)
    print("サイズ:", file_size, flush=True)
    print(
        "実際の再生時間:",
        actual_duration,
        flush=True
    )
    print(
        "ファイル存在確認:",
        os.path.isfile(output_file),
        flush=True
    )
    print("==========================================", flush=True)


    return actual_duration


# ==========================================================
# FFmpegでMP4作成
#
# A方式:
#
# source_file はすでにyt-dlpで範囲指定済み。
#
# ここでは -ss / -t を使用しない。
# ==========================================================

def create_mp4(
    source_file,
    output_file
):

    print("==========================================", flush=True)
    print("MP4作成", flush=True)
    print("入力:", source_file, flush=True)
    print("出力:", output_file, flush=True)
    print("==========================================", flush=True)


    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    if not os.path.exists(
        source_file
    ):

        raise Exception(
            "MP4入力ファイルがありません: "
            + source_file
        )


    source_size = os.path.getsize(
        source_file
    )


    if source_size <= 0:

        raise Exception(
            "MP4入力ファイルが0 bytesです"
        )


    # ======================================================
    # FFmpeg
    #
    # 時間指定なし。
    # ======================================================

    command = [

        "ffmpeg",

        "-y",

        "-i",
        source_file,

        "-map",
        "0:v:0",

        "-map",
        "0:a:0?",

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "23",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-movflags",
        "+faststart",

        "-map_metadata",
        "-1",

        output_file

    ]


    print(
        "FFmpeg:",
        command,
        flush=True
    )


    print(
        "DEBUG: FFmpeg MP4 START",
        flush=True
    )


    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=1800

        )

    except subprocess.TimeoutExpired as e:

        print(
            "DEBUG: FFmpeg MP4 TIMEOUT",
            flush=True
        )


        if os.path.exists(
            output_file
        ):

            try:

                os.remove(
                    output_file
                )

            except Exception:

                pass


        raise Exception(
            "MP4作成が1800秒でタイムアウトしました"
        ) from e


    print(
        "DEBUG: FFmpeg MP4 END",
        flush=True
    )


    if result.returncode != 0:

        print(
            "FFmpeg stderr:",
            result.stderr,
            flush=True
        )


        if os.path.exists(
            output_file
        ):

            try:

                os.remove(
                    output_file
                )

            except Exception:

                pass


        raise Exception(
            "MP4作成に失敗しました"
        )


    if not os.path.exists(
        output_file
    ):

        raise Exception(
            "MP4ファイルが作成されませんでした"
        )


    file_size = os.path.getsize(
        output_file
    )


    if file_size <= 0:

        raise Exception(
            "MP4ファイルが0 bytesです"
        )


    actual_duration = get_media_duration(
        output_file
    )


    print("==========================================", flush=True)
    print("MP4作成完了", flush=True)
    print("ファイル:", output_file, flush=True)
    print("サイズ:", file_size, flush=True)
    print(
        "実際の再生時間:",
        actual_duration,
        flush=True
    )
    print("==========================================", flush=True)


    return actual_duration


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

    temp_cookie = None

    temp_source_dir = None


    execution_start_timestamp = time.time()

    execution_start_text = (
        get_current_time_text()
    )


    try:

        # ==================================================
        # Job running
        # ==================================================

        jobs[job_id] = {

            "status":
                "running",

            "files":
                [],

            "outputs":
                outputs,

            "start_time":
                start_time or "",

            "end_time":
                end_time or "",

            "execution_start":
                execution_start_text

        }


        print("==========================================", flush=True)
        print("変換処理開始", flush=True)
        print("JOB:", job_id, flush=True)
        print("URL:", url, flush=True)
        print("OUTPUTS:", outputs, flush=True)
        print("START:", start_time, flush=True)
        print("END:", end_time, flush=True)
        print(
            "実行開始:",
            execution_start_text,
            flush=True
        )
        print("==========================================", flush=True)


        # ==================================================
        # FFmpeg確認
        # ==================================================

        if not check_ffmpeg():

            raise Exception(
                "ffmpegが利用できません"
            )


        if not check_ffprobe():

            raise Exception(
                "ffprobeが利用できません"
            )


        # ==================================================
        # Cookie
        # ==================================================

        print(
            "DEBUG: Cookie作成 START",
            flush=True
        )


        temp_cookie = (
            create_temp_cookie_file()
        )


        print(
            "DEBUG: Cookie作成 END",
            flush=True
        )


        # ==================================================
        # 古いファイル削除
        # ==================================================

        try:

            cleanup_downloads()

        except Exception as e:

            print(
                "WARNING: cleanup失敗:",
                repr(e),
                flush=True
            )


        # ==================================================
        # 出力ディレクトリ
        # ==================================================

        output_dir = DOWNLOAD_DIR


        os.makedirs(

            output_dir,

            exist_ok=True

        )


        # ==================================================
        # 時間を秒へ変換
        # ==================================================

        start_seconds = (
            time_to_seconds(
                start_time
            )
        )


        end_seconds = (
            time_to_seconds(
                end_time
            )
        )


        # ==================================================
        # 時間チェック
        # ==================================================

        if (
            start_seconds is not None
            and end_seconds is None
        ):

            raise Exception(
                "終了時間を入力してください"
            )


        # ==================================================
        # 終了時間だけ指定
        # ==================================================

        if (
            start_seconds is None
            and end_seconds is not None
        ):

            start_seconds = 0

            start_time = "00:00:00"


        # ==================================================
        # 開始・終了両方指定
        # ==================================================

        if (
            start_seconds is not None
            and end_seconds is not None
        ):

            if start_seconds < 0:

                raise Exception(
                    "開始時間は0以上にしてください"
                )


            if end_seconds <= start_seconds:

                raise Exception(
                    "終了時間は開始時間より後にしてください"
                )


        # ==================================================
        # 出力形式確認
        # ==================================================

        valid_outputs = []


        if "mp3" in outputs:

            valid_outputs.append(
                "mp3"
            )


        if "mp4" in outputs:

            valid_outputs.append(
                "mp4"
            )


        if not valid_outputs:

            raise Exception(
                "MP3またはMP4を指定してください"
            )


        # ==================================================
        # 元動画情報取得
        # ==================================================

        print("==========================================", flush=True)
        print("YouTube情報取得", flush=True)
        print("==========================================", flush=True)


        info = get_video_info(

            url,

            temp_cookie

        )


        title = info.get(
            "title",
            "youtube"
        )


        title = safe_filename(
            title
        )


        full_duration = info.get(
            "duration"
        )


        if full_duration is None:

            raise Exception(
                "元動画の再生時間を取得できませんでした"
            )


        full_duration = float(
            full_duration
        )


        print(
            "タイトル:",
            title,
            flush=True
        )

        print(
            "Full再生時間:",
            full_duration,
            flush=True
        )


        # ==================================================
        # 指定時間が元動画を超えていないか
        # ==================================================

        if end_seconds is not None:

            if end_seconds > full_duration:

                raise Exception(

                    "終了時間が動画の再生時間を超えています。"
                    f"終了: {seconds_to_time(end_seconds)} / "
                    f"Full: {seconds_to_time(full_duration)}"

                )


        if start_seconds is not None:

            if start_seconds >= full_duration:

                raise Exception(

                    "開始時間が動画の再生時間を超えています。"
                    f"開始: {seconds_to_time(start_seconds)} / "
                    f"Full: {seconds_to_time(full_duration)}"

                )


        # ==================================================
        # 選択時間から再生時間を計算
        # ==================================================

        if (
            start_seconds is not None
            and end_seconds is not None
        ):

            requested_duration = (

                end_seconds
                - start_seconds

            )

        else:

            requested_duration = (
                full_duration
            )


        print("==========================================", flush=True)
        print(
            "再生時間計算",
            flush=True
        )
        print(
            "開始:",
            seconds_to_time(start_seconds)
            if start_seconds is not None
            else "00:00:00",
            flush=True
        )
        print(
            "終了:",
            seconds_to_time(end_seconds)
            if end_seconds is not None
            else seconds_to_time(full_duration),
            flush=True
        )
        print(
            "再生時間:",
            seconds_to_time(requested_duration),
            flush=True
        )
        print(
            "Full:",
            seconds_to_time(full_duration),
            flush=True
        )
        print("==========================================", flush=True)


        # ==================================================
        # 一時元ファイル保存場所
        # ==================================================

        temp_source_dir = tempfile.mkdtemp(
            prefix="y2conv_source_"
        )


        print(
            "一時元ファイルディレクトリ:",
            temp_source_dir,
            flush=True
        )


        # ==================================================
        # MP4が必要か
        # ==================================================

        need_video = (
            "mp4" in valid_outputs
        )


        # ==================================================
        # YouTube元データ取得
        # ==================================================

        source_file, downloaded_info = (
            download_source(

                url,

                temp_cookie,

                temp_source_dir,

                need_video,

                start_seconds,

                end_seconds

            )
        )


        # ==================================================
        # download_source完了確認
        # ==================================================

        print(
            "DEBUG: download_source RETURNED",
            flush=True
        )

        print(
            "DEBUG: source_file:",
            source_file,
            flush=True
        )


        if not os.path.exists(
            source_file
        ):

            raise Exception(
                "download_source後に元ファイルが存在しません"
            )


        print(
            "DEBUG: source_file size:",
            os.path.getsize(source_file),
            "bytes",
            flush=True
        )


        # ==================================================
        # 出力ファイル名
        # ==================================================

        mp3_file = os.path.join(

            output_dir,

            title + ".mp3"

        )


        mp4_file = os.path.join(

            output_dir,

            title + ".mp4"

        )


        files = []


        # ==================================================
        # 実際に作成されたファイルの再生時間
        # ==================================================

        actual_duration = None

        actual_mp3_duration = None

        actual_mp4_duration = None


        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in valid_outputs:

            print(
                "==========================================",
                flush=True
            )

            print(
                "DEBUG: MP3処理開始",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            actual_mp3_duration = create_mp3(

                source_file,

                mp3_file

            )


            files.append(
                os.path.basename(
                    mp3_file
                )
            )


            actual_duration = (
                actual_mp3_duration
            )


            print(
                "DEBUG: MP3処理終了",
                flush=True
            )


        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in valid_outputs:

            print(
                "==========================================",
                flush=True
            )

            print(
                "DEBUG: MP4処理開始",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            actual_mp4_duration = create_mp4(

                source_file,

                mp4_file

            )


            files.append(
                os.path.basename(
                    mp4_file
                )
            )


            if actual_duration is None:

                actual_duration = (
                    actual_mp4_duration
                )


            print(
                "DEBUG: MP4処理終了",
                flush=True
            )


        # ==================================================
        # 実行終了時刻
        # ==================================================

        execution_end_timestamp = time.time()

        execution_end_text = (
            get_current_time_text()
        )


        execution_seconds = int(
            round(
                execution_end_timestamp
                - execution_start_timestamp
            )
        )


        # ==================================================
        # Job complete
        # ==================================================

        jobs[job_id] = {

            "status":
                "complete",

            "files":
                files,

            "outputs":
                valid_outputs,

            "title":
                title,

            "duration":
                requested_duration,

            "duration_text":
                seconds_to_time(
                    requested_duration
                ),

            "actual_duration":
                actual_duration,

            "actual_duration_text":
                seconds_to_time(
                    actual_duration
                ),

            "mp3_duration":
                actual_mp3_duration,

            "mp3_duration_text":
                seconds_to_time(
                    actual_mp3_duration
                ),

            "mp4_duration":
                actual_mp4_duration,

            "mp4_duration_text":
                seconds_to_time(
                    actual_mp4_duration
                ),

            "full_duration":
                full_duration,

            "full_duration_text":
                seconds_to_time(
                    full_duration
                ),

            "start_time":
                start_time or "",

            "end_time":
                end_time or "",

            "start_seconds":
                start_seconds,

            "end_seconds":
                end_seconds,

            "execution_start":
                execution_start_text,

            "execution_end":
                execution_end_text,

            "execution_seconds":
                execution_seconds,

            "execution_seconds_text":
                f"{execution_seconds}秒"

        }


        print("==========================================", flush=True)
        print("変換完了", flush=True)
        print("JOB:", job_id, flush=True)
        print("TITLE:", title, flush=True)

        print(
            "選択再生時間:",
            requested_duration,
            flush=True
        )

        print(
            "選択再生時間 TEXT:",
            seconds_to_time(
                requested_duration
            ),
            flush=True
        )

        print(
            "実ファイル再生時間:",
            actual_duration,
            flush=True
        )

        print(
            "Full再生時間:",
            full_duration,
            flush=True
        )

        print(
            "Full再生時間 TEXT:",
            seconds_to_time(
                full_duration
            ),
            flush=True
        )

        print(
            "実行開始:",
            execution_start_text,
            flush=True
        )

        print(
            "実行終了:",
            execution_end_text,
            flush=True
        )

        print(
            "実行時間:",
            execution_seconds,
            "秒",
            flush=True
        )

        print(
            "FILES:",
            files,
            flush=True
        )

        print("==========================================", flush=True)


    except Exception as e:

        # ==================================================
        # エラー時も実行時間を保存
        # ==================================================

        execution_end_timestamp = time.time()

        execution_end_text = (
            get_current_time_text()
        )


        execution_seconds = int(
            round(
                execution_end_timestamp
                - execution_start_timestamp
            )
        )


        print("==========================================", flush=True)
        print("変換エラー", flush=True)
        print("JOB:", job_id, flush=True)
        print(
            "ERROR TYPE:",
            type(e).__name__,
            flush=True
        )
        print(
            "ERROR:",
            repr(e),
            flush=True
        )
        print(
            "実行開始:",
            execution_start_text,
            flush=True
        )
        print(
            "実行終了:",
            execution_end_text,
            flush=True
        )
        print(
            "実行時間:",
            execution_seconds,
            "秒",
            flush=True
        )
        print("==========================================", flush=True)


        jobs[job_id] = {

            "status":
                "error",

            "message":
                str(e),

            "outputs":
                outputs,

            "start_time":
                start_time or "",

            "end_time":
                end_time or "",

            "execution_start":
                execution_start_text,

            "execution_end":
                execution_end_text,

            "execution_seconds":
                execution_seconds,

            "execution_seconds_text":
                f"{execution_seconds}秒"

        }


    finally:

        # ==================================================
        # 一時Cookie削除
        # ==================================================

        remove_temp_cookie_file(
            temp_cookie
        )


        # ==================================================
        # 一時元動画削除
        # ==================================================

        if (
            temp_source_dir
            and
            os.path.exists(
                temp_source_dir
            )
        ):

            try:

                shutil.rmtree(
                    temp_source_dir
                )


                print(
                    "一時元動画ディレクトリ削除:",
                    temp_source_dir,
                    flush=True
                )


            except Exception as e:

                print(
                    "WARNING: "
                    "一時元動画ディレクトリ削除失敗:",
                    repr(e),
                    flush=True
                )


# ==========================================================
# /convert
# ==========================================================

def register_convert(
    app
):

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

                }), 400


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
                        "YouTube URLがありません"

                }), 400


            url = str(
                url
            ).strip()


            # ==================================================
            # outputs
            # ==================================================

            outputs = data.get(
                "outputs",
                []
            )


            if not isinstance(
                outputs,
                list
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "outputsが正しくありません"

                }), 400


            valid_outputs = []


            if "mp3" in outputs:

                valid_outputs.append(
                    "mp3"
                )


            if "mp4" in outputs:

                valid_outputs.append(
                    "mp4"
                )


            if not valid_outputs:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3またはMP4を指定してください"

                }), 400


            # ==================================================
            # 時間
            # ==================================================

            start_time = data.get(
                "start_time"
            )


            end_time = data.get(
                "end_time"
            )


            if start_time is not None:

                start_time = str(
                    start_time
                ).strip()


            if end_time is not None:

                end_time = str(
                    end_time
                ).strip()


            # ==================================================
            # 空文字
            # ==================================================

            if start_time == "":

                start_time = None


            if end_time == "":

                end_time = None


            # ==================================================
            # 時間を秒へ変換
            # ==================================================

            start_seconds = (
                time_to_seconds(
                    start_time
                )
            )


            end_seconds = (
                time_to_seconds(
                    end_time
                )
            )


            # ==================================================
            # 時間チェック
            # ==================================================

            if (
                start_seconds is not None
                and end_seconds is None
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "終了時間を入力してください"

                }), 400


            # ==================================================
            # 終了時間だけの場合
            # ==================================================

            if (
                start_seconds is None
                and end_seconds is not None
            ):

                start_seconds = 0

                start_time = "00:00:00"


            # ==================================================
            # 開始・終了両方
            # ==================================================

            if (
                start_seconds is not None
                and end_seconds is not None
            ):

                if end_seconds <= start_seconds:

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "終了時間は開始時間より後にしてください"

                    }), 400


            # ==================================================
            # Job ID
            # ==================================================

            job_id = str(
                uuid.uuid4()
            )


            # ==================================================
            # Job登録
            # ==================================================

            jobs[job_id] = {

                "status":
                    "queued",

                "outputs":
                    valid_outputs,

                "start_time":
                    start_time or "",

                "end_time":
                    end_time or ""

            }


            print("==========================================", flush=True)
            print("JOB登録", flush=True)
            print("JOB:", job_id, flush=True)
            print("URL:", url, flush=True)
            print(
                "OUTPUTS:",
                valid_outputs,
                flush=True
            )
            print(
                "START:",
                start_time,
                flush=True
            )
            print(
                "END:",
                end_time,
                flush=True
            )
            print("==========================================", flush=True)


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

                ),

                name=f"convert-{job_id}",

                daemon=True

            )


            thread.start()


            print(
                "DEBUG: convert thread started",
                job_id,
                flush=True
            )


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
                repr(e),
                flush=True
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500
