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
from urllib.parse import urlparse

from routes.status import (
    jobs,
    jobs_lock,
    update_file_status,
    update_job_status
)

from config import (
    BASE_DIR,
    DOWNLOAD_DIR
)


# ==========================================================
# Render Cookie
# ==========================================================

RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ==========================================================
# Local Cookie
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
# Cookie file
# ==========================================================

if os.environ.get("RENDER") == "true":

    SOURCE_COOKIE_FILE = RENDER_COOKIE_FILE

else:

    SOURCE_COOKIE_FILE = LOCAL_COOKIE_FILE


print(
    "==========================================",
    flush=True
)

print(
    "convert.py loaded",
    flush=True
)

print(
    "RENDER:",
    os.environ.get("RENDER"),
    flush=True
)

print(
    "Cookie:",
    SOURCE_COOKIE_FILE,
    flush=True
)

print(
    "==========================================",
    flush=True
)


# ==========================================================
# URL debug
# ==========================================================

def debug_url(url):

    if url is None:

        return None

    try:

        text = str(url)

    except Exception:

        return "<URL文字列化失敗>"

    if len(text) > 500:

        return (
            text[:500]
            + "... [truncated]"
        )

    return text


# ==========================================================
# YouTube URL validation
# ==========================================================

def validate_youtube_url(url):

    if url is None:

        raise ValueError(
            "YouTube URLがありません"
        )

    url = str(url).strip()

    if not url:

        raise ValueError(
            "YouTube URLが空です"
        )

    if len(url) > 2048:

        raise ValueError(
            "URLが長すぎます"
        )

    if "\x00" in url:

        raise ValueError(
            "URLに不正な文字が含まれています"
        )

    if "\r" in url or "\n" in url:

        raise ValueError(
            "URLに改行が含まれています"
        )

    parsed_url = urlparse(url)

    if parsed_url.scheme.lower() not in (
        "http",
        "https"
    ):

        raise ValueError(
            "httpまたはhttpsのURLを指定してください"
        )

    hostname = (
        parsed_url.hostname
        or ""
    ).lower()

    valid_hosts = {

        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "www.youtu.be"

    }

    if hostname not in valid_hosts:

        raise ValueError(
            "YouTube URLではありません"
        )

    if hostname in {

        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com"

    }:

        path = (
            parsed_url.path
            or ""
        ).lower()

        if path == "/watch":

            if "v=" not in parsed_url.query:

                raise ValueError(
                    "YouTube動画URLのvパラメータがありません"
                )

        elif path.startswith("/shorts/"):

            pass

        elif path.startswith("/live/"):

            pass

        elif path.startswith("/embed/"):

            pass

        else:

            raise ValueError(
                "YouTube動画URLとして認識できません"
            )

    if hostname in {

        "youtu.be",
        "www.youtu.be"

    }:

        path = (
            parsed_url.path
            or ""
        ).strip("/")

        if not path:

            raise ValueError(
                "youtu.beの動画IDがありません"
            )

    return url


# ==========================================================
# Cookie check
# ==========================================================

def check_cookie_file():

    if not os.path.isfile(
        SOURCE_COOKIE_FILE
    ):

        raise Exception(
            "Cookieファイルが見つかりません: "
            + SOURCE_COOKIE_FILE
        )

    size = os.path.getsize(
        SOURCE_COOKIE_FILE
    )

    if size <= 0:

        raise Exception(
            "Cookieファイルが空です"
        )

    print(
        "Cookie OK:",
        SOURCE_COOKIE_FILE,
        size,
        "bytes",
        flush=True
    )


# ==========================================================
# Temporary Cookie
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

        os.close(fd)

        shutil.copyfile(
            SOURCE_COOKIE_FILE,
            temp_cookie
        )

        return temp_cookie

    except Exception:

        if (
            temp_cookie
            and
            os.path.exists(temp_cookie)
        ):

            try:

                os.remove(
                    temp_cookie
                )

            except Exception:

                pass

        raise


# ==========================================================
# Remove temporary Cookie
# ==========================================================

def remove_temp_cookie_file(cookie_file):

    if (
        cookie_file
        and
        os.path.exists(cookie_file)
    ):

        try:

            os.remove(
                cookie_file
            )

        except Exception as e:

            print(
                "WARNING: Cookie削除失敗:",
                repr(e),
                flush=True
            )


# ==========================================================
# Deno
# ==========================================================

def check_deno():

    return (

        os.path.isfile(DENO_PATH)
        and
        os.access(
            DENO_PATH,
            os.X_OK
        )

    )


# ==========================================================
# Time -> seconds
# ==========================================================

def time_to_seconds(value):

    if value is None:

        return None

    value = str(value).strip()

    if not value:

        return None

    parts = value.split(":")

    try:

        if len(parts) == 1:

            seconds = float(parts[0])

            if seconds < 0:

                raise ValueError

            return seconds

        if len(parts) == 2:

            minutes = float(parts[0])

            seconds = float(parts[1])

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

            hours = float(parts[0])

            minutes = float(parts[1])

            seconds = float(parts[2])

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
# Seconds -> HH:MM:SS
# ==========================================================

def seconds_to_time(seconds):

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

    seconds = max(
        0,
        seconds
    )

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
# Current time
# ==========================================================

def get_current_time_text():

    return datetime.now().strftime(
        "%H:%M:%S"
    )


# ==========================================================
# FFmpeg
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

        return result.returncode == 0

    except Exception:

        return False


# ==========================================================
# FFprobe
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

        return result.returncode == 0

    except Exception:

        return False


# ==========================================================
# Media duration
# ==========================================================

def get_media_duration(file_path):

    if not os.path.isfile(file_path):

        raise FileNotFoundError(
            "メディアファイルがありません: "
            + file_path
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

    result = subprocess.run(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True,

        timeout=30

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
# yt-dlp base options
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
            False,

        "restrictfilenames":
            False,

        "continuedl":
            False,

        "retries":
            3,

        "fragment_retries":
            3,

        "concurrent_fragment_downloads":
            1

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

    return options


# ==========================================================
# Video info
# ==========================================================

def get_video_info(
    url,
    temp_cookie
):

    url = validate_youtube_url(
        url
    )

    options = {

        "cookiefile":
            temp_cookie,

        "noplaylist":
            True,

        "quiet":
            True,

        "no_warnings":
            False,

        "skip_download":
            True

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

    if not info:

        raise Exception(
            "YouTube情報を取得できませんでした"
        )

    print(
        "DEBUG: get_video_info END",
        flush=True
    )

    return info


# ==========================================================
# Source download
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

    # ------------------------------------------------------
    # MP4
    # ------------------------------------------------------

    if need_video:

        # メモリ節約のため720p以下
        options["format"] = (
            "bestvideo[height<=720]+"
            "bestaudio/"
            "best[height<=720]/"
            "best"
        )

        options["merge_output_format"] = "mp4"

        print(
            "MP4 download format: <=720p",
            flush=True
        )

    # ------------------------------------------------------
    # MP3 only
    # ------------------------------------------------------

    else:

        options["format"] = (
            "bestaudio/best"
        )

        print(
            "MP3 download format: audio",
            flush=True
        )

    # ------------------------------------------------------
    # Range
    # ------------------------------------------------------

    if (
        start_seconds is not None
        and end_seconds is not None
    ):

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

        options["force_keyframes_at_cuts"] = False

    print(
        "==========================================",
        flush=True
    )

    print(
        "YouTube download START",
        flush=True
    )

    print(
        "need_video:",
        need_video,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    with yt_dlp.YoutubeDL(
        options
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

    if not info:

        raise Exception(
            "YouTubeダウンロード情報を取得できませんでした"
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

        if not filename.startswith(
            "source_"
        ):

            continue

        if filename.endswith(
            ".part"
        ):

            continue

        if filename.endswith(
            ".ytdl"
        ):

            continue

        if os.path.getsize(
            full_path
        ) <= 0:

            continue

        files.append(
            full_path
        )

    if not files:

        raise Exception(
            "YouTube元ファイルが作成されませんでした"
        )

    source_file = max(
        files,
        key=os.path.getmtime
    )

    print(
        "YouTube source:",
        source_file,
        flush=True
    )

    print(
        "Source size:",
        os.path.getsize(source_file),
        "bytes",
        flush=True
    )

    return source_file, info


# ==========================================================
# Safe filename
# ==========================================================

def safe_filename(title):

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
# Remove old output
# ==========================================================

def remove_existing_file(
    file_path
):

    if os.path.exists(
        file_path
    ):

        try:

            os.remove(
                file_path
            )

            print(
                "既存ファイル削除:",
                file_path,
                flush=True
            )

        except Exception as e:

            raise Exception(
                "既存ファイルを削除できません: "
                + str(e)
            )


# ==========================================================
# MP3
# ==========================================================

def create_mp3(
    source_file,
    output_file,
    start_seconds=None,
    end_seconds=None
):

    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )

    remove_existing_file(
        output_file
    )

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
        "-1"

    ]

    if (
        start_seconds is not None
        and end_seconds is not None
    ):

        command.extend([

            "-ss",
            str(start_seconds),

            "-to",
            str(end_seconds)

        ])

    command.append(
        output_file
    )

    print(
        "DEBUG: FFmpeg MP3 START",
        flush=True
    )

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=None,
        timeout=600
    )

    print(
        "DEBUG: FFmpeg MP3 END:",
        result.returncode,
        flush=True
    )

    if result.returncode != 0:

        raise Exception(
            "MP3作成に失敗しました"
        )

    if not os.path.isfile(
        output_file
    ):

        raise Exception(
            "MP3ファイルが作成されませんでした"
        )

    if os.path.getsize(
        output_file
    ) <= 0:

        raise Exception(
            "MP3ファイルが0 bytesです"
        )

    return get_media_duration(
        output_file
    )


# ==========================================================
# MP4
# ==========================================================

def create_mp4(
    source_file,
    output_file,
    start_seconds=None,
    end_seconds=None
):

    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )

    remove_existing_file(
        output_file
    )

    command = [

        "ffmpeg",

        "-y",

        "-i",
        source_file

    ]

    # ------------------------------------------------------
    # 範囲指定
    # ------------------------------------------------------

    if (
        start_seconds is not None
        and end_seconds is not None
    ):

        duration = (
            end_seconds
            - start_seconds
        )

        command.extend([

            "-ss",
            str(start_seconds),

            "-t",
            str(duration)

        ])

    # ------------------------------------------------------
    # MP4出力
    # ------------------------------------------------------

    command.extend([

        "-c:v",
        "copy",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-movflags",
        "+faststart",

        output_file

    ])

    print(
        "DEBUG: FFmpeg MP4 START",
        flush=True
    )

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=None,
        timeout=600
    )

    print(
        "DEBUG: FFmpeg MP4 END:",
        result.returncode,
        flush=True
    )

    if result.returncode != 0:

        raise Exception(
            "MP4作成に失敗しました"
        )

    if not os.path.isfile(
        output_file
    ):

        raise Exception(
            "MP4ファイルが作成されませんでした"
        )

    if os.path.getsize(
        output_file
    ) <= 0:

        raise Exception(
            "MP4ファイルが0 bytesです"
        )

    return get_media_duration(
        output_file
    )


# ==========================================================
# File complete
# ==========================================================

def mark_file_complete(
    job_id,
    file_type,
    file_path,
    duration=None
):

    filename = os.path.basename(
        file_path
    )

    update_file_status(

        job_id,

        file_type,

        "complete",

        filename=filename,

        duration=duration,

        duration_text=(
            seconds_to_time(duration)
            if duration is not None
            else None
        )

    )

    print(
        "FILE COMPLETE:",
        file_type,
        filename,
        flush=True
    )


# ==========================================================
# Convert task
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

        update_job_status(

            job_id,

            "running",

            execution_start=
                execution_start_text

        )

        for file_type in outputs:

            update_file_status(

                job_id,

                file_type,

                "pending"

            )

        # --------------------------------------------------
        # Tool check
        # --------------------------------------------------

        if not check_ffmpeg():

            raise Exception(
                "ffmpegが利用できません"
            )

        if not check_ffprobe():

            raise Exception(
                "ffprobeが利用できません"
            )

        # --------------------------------------------------
        # Time
        # --------------------------------------------------

        start_seconds = time_to_seconds(
            start_time
        )

        end_seconds = time_to_seconds(
            end_time
        )

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temp_cookie = (
            create_temp_cookie_file()
        )

        # --------------------------------------------------
        # Video info
        # --------------------------------------------------

        set_message = (
            "動画情報を取得しています..."
        )

        update_job_status(
            job_id,
            "running",
            progress_message=set_message
        )

        info = get_video_info(
            url,
            temp_cookie
        )

        title = safe_filename(
            info.get(
                "title",
                "youtube"
            )
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

        # --------------------------------------------------
        # Validate range
        # --------------------------------------------------

        if (
            start_seconds is not None
            and end_seconds is None
        ):

            raise Exception(
                "終了時間を入力してください"
            )

        if (
            start_seconds is None
            and end_seconds is not None
        ):

            start_seconds = 0

        if (
            start_seconds is not None
            and end_seconds is not None
        ):

            if end_seconds <= start_seconds:

                raise Exception(
                    "終了時間は開始時間より後にしてください"
                )

            if start_seconds >= full_duration:

                raise Exception(
                    "開始時間が動画の再生時間を超えています"
                )

            if end_seconds > full_duration:

                raise Exception(
                    "終了時間が動画の再生時間を超えています"
                )

            requested_duration = (
                end_seconds
                - start_seconds
            )

        else:

            requested_duration = (
                full_duration
            )

        # --------------------------------------------------
        # Job info
        # --------------------------------------------------

        update_job_status(

            job_id,

            "running",

            title=title,

            duration=requested_duration,

            duration_text=seconds_to_time(
                requested_duration
            ),

            full_duration=full_duration,

            full_duration_text=seconds_to_time(
                full_duration
            ),

            start_time=start_time or "",

            end_time=end_time or "",

            progress_message=
                "YouTube動画をダウンロードしています..."

        )

        # --------------------------------------------------
        # Source
        # --------------------------------------------------

        temp_source_dir = tempfile.mkdtemp(
            prefix="y2conv_source_"
        )

        need_video = (
            "mp4" in outputs
        )

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

        # --------------------------------------------------
        # Output paths
        # --------------------------------------------------

        output_dir = DOWNLOAD_DIR

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        mp3_file = os.path.join(
            output_dir,
            title + ".mp3"
        )

        mp4_file = os.path.join(
            output_dir,
            title + ".mp4"
        )

        actual_mp3_duration = None
        actual_mp4_duration = None

        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in outputs:

            update_file_status(

                job_id,

                "mp3",

                "running"

            )

            update_job_status(

                job_id,

                "running",

                progress_message=
                    "MP3を作成しています..."

            )

            try:

                actual_mp3_duration = create_mp3(

                    source_file,

                    mp3_file,

                    start_seconds,

                    end_seconds

                )

                mark_file_complete(

                    job_id,

                    "mp3",

                    mp3_file,

                    actual_mp3_duration

                )

            except Exception as e:

                update_file_status(

                    job_id,

                    "mp3",

                    "error",

                    message=str(e)

                )

                raise

        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in outputs:

            update_file_status(

                job_id,

                "mp4",

                "running"

            )

            update_job_status(

                job_id,

                "running",

                progress_message=
                    "MP4を作成しています..."

            )

            try:

                actual_mp4_duration = create_mp4(

                    source_file,

                    mp4_file,

                    start_seconds,
                    end_seconds

                )

                mark_file_complete(

                    job_id,

                    "mp4",

                    mp4_file,

                    actual_mp4_duration

                )

            except Exception as e:

                update_file_status(

                    job_id,

                    "mp4",

                    "error",

                    message=str(e)

                )

                raise

        # ==================================================
        # Complete
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

        actual_duration = (
            actual_mp3_duration
            if actual_mp3_duration is not None
            else actual_mp4_duration
        )

        all_complete = True

        for file_type in outputs:

            file_info = jobs[job_id].get(
                "files",
                {}
            ).get(
                file_type,
                {}
            )

            if file_info.get(
                "status"
            ) != "complete":

                all_complete = False

        if all_complete:

            update_job_status(

                job_id,

                "complete",

                actual_duration=actual_duration,

                actual_duration_text=
                    seconds_to_time(
                        actual_duration
                    ),

                mp3_duration=
                    actual_mp3_duration,

                mp3_duration_text=
                    seconds_to_time(
                        actual_mp3_duration
                    ),

                mp4_duration=
                    actual_mp4_duration,

                mp4_duration_text=
                    seconds_to_time(
                        actual_mp4_duration
                    ),

                execution_end=
                    execution_end_text,

                execution_seconds=
                    execution_seconds,

                execution_seconds_text=
                    f"{execution_seconds}秒",

                progress_message=
                    "変換が完了しました。"

            )

            print(
                "==========================================",
                flush=True
            )

            print(
                "JOB COMPLETE:",
                job_id,
                flush=True
            )

            print(
                "FILES:",
                jobs[job_id].get(
                    "files"
                ),
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

    except Exception as e:

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

        error_message = str(e)

        print(
            "==========================================",
            flush=True
        )

        print(
            "CONVERT ERROR:",
            repr(e),
            flush=True
        )

        print(
            "JOB:",
            job_id,
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        update_job_status(

            job_id,

            "error",

            message=error_message,

            error_type=type(e).__name__,

            execution_end=execution_end_text,

            execution_seconds=execution_seconds,

            execution_seconds_text=
                f"{execution_seconds}秒",

            progress_message=
                "変換に失敗しました。"

        )

        for file_type in outputs:

            file_info = jobs[job_id].get(
                "files",
                {}
            ).get(
                file_type
            )

            if not file_info:

                continue

            if file_info.get(
                "status"
            ) in (
                "pending",
                "running"
            ):

                update_file_status(

                    job_id,

                    file_type,

                    "error",

                    message=error_message

                )

    finally:

        remove_temp_cookie_file(
            temp_cookie
        )

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

            except Exception as e:

                print(
                    "WARNING: source cleanup:",
                    repr(e),
                    flush=True
                )


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

            # --------------------------------------------------
            # URL
            # --------------------------------------------------

            url = data.get(
                "url"
            )

            try:

                url = validate_youtube_url(
                    url
                )

            except ValueError as e:

                return jsonify({

                    "success":
                        False,

                    "message":
                        str(e)

                }), 400

            # --------------------------------------------------
            # Outputs
            # --------------------------------------------------

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

            # --------------------------------------------------
            # Time
            # --------------------------------------------------

            start_time = data.get(
                "start_time"
            )

            end_time = data.get(
                "end_time"
            )

            # --------------------------------------------------
            # 新形式 time_range にも対応
            # converter.jsからはこちらが来る
            # --------------------------------------------------

            time_range = data.get(
                "time_range"
            )

            if isinstance(
                time_range,
                dict
            ):

                if start_time is None:

                    start_time = (
                        time_range.get(
                            "start_time"
                        )
                        or
                        time_range.get(
                            "start"
                        )
                    )

                if end_time is None:

                    end_time = (
                        time_range.get(
                            "end_time"
                        )
                        or
                        time_range.get(
                            "end"
                        )
                    )

            if start_time is not None:

                start_time = str(
                    start_time
                ).strip()

            if end_time is not None:

                end_time = str(
                    end_time
                ).strip()

            if start_time == "":

                start_time = None

            if end_time == "":

                end_time = None

            try:

                start_seconds = time_to_seconds(
                    start_time
                )

                end_seconds = time_to_seconds(
                    end_time
                )

            except ValueError as e:

                return jsonify({

                    "success":
                        False,

                    "message":
                        str(e)

                }), 400

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

            if (
                start_seconds is None
                and end_seconds is not None
            ):

                start_seconds = 0

                start_time = "00:00:00"

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

            # --------------------------------------------------
            # Job ID
            # --------------------------------------------------

            job_id = str(
                uuid.uuid4()
            )

            # --------------------------------------------------
            # File status
            # --------------------------------------------------

            file_status = {}

            for file_type in valid_outputs:

                file_status[file_type] = {

                    "status":
                        "pending"

                }

            # --------------------------------------------------
            # Job
            # --------------------------------------------------

            with jobs_lock:

                jobs[job_id] = {

                    "status":
                        "queued",

                    "files":
                        file_status,

                    "outputs":
                        valid_outputs,

                    "start_time":
                        start_time or "",

                    "end_time":
                        end_time or "",

                    "created_at":
                        get_current_time_text(),

                    "progress_message":
                        "変換処理を開始しています..."

                }

            print(
                "==========================================",
                flush=True
            )

            print(
                "JOB REGISTER:",
                job_id,
                flush=True
            )

            print(
                "OUTPUTS:",
                valid_outputs,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            # --------------------------------------------------
            # Background thread
            # --------------------------------------------------

            thread = threading.Thread(

                target=convert_task,

                args=(

                    job_id,

                    url,

                    valid_outputs,

                    start_time,

                    end_time

                ),

                name=(
                    "convert-"
                    + job_id
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
                "convert endpoint error:",
                repr(e),
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500
