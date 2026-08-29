# =====================================
# YouTube Converter
# ytdlp.py
#
# YouTube → MP3 / MP4変換
#
# Render対応
# Cookie + Deno + EJS
# =====================================


import os
import shutil
import tempfile
import subprocess
import re

import yt_dlp

from yt_dlp.utils import download_range_func

from config import (
    DOWNLOAD_DIR,
    COOKIES_FILE
)


# ==========================================================
# Deno
# ==========================================================

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"


# ==========================================================
# Deno確認
# ==========================================================

def check_deno():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] Deno確認",
        flush=True
    )

    print(
        "[YTDLP] DENO_PATH:",
        DENO_PATH,
        flush=True
    )

    exists = os.path.isfile(
        DENO_PATH
    )

    executable = (
        os.access(
            DENO_PATH,
            os.X_OK
        )
        if exists
        else False
    )

    print(
        "[YTDLP] Deno exists:",
        exists,
        flush=True
    )

    print(
        "[YTDLP] Deno executable:",
        executable,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return (
        exists
        and
        executable
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
# メディア再生時間取得
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
# 時間を秒へ変換
#
# 対応:
#
# 10
# 1:30
# 01:30
# 1:02:30
# 00:00:00
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

        # --------------------------------------------------
        # 秒
        # --------------------------------------------------

        if len(parts) == 1:

            seconds = float(
                parts[0]
            )

            if seconds < 0:

                raise ValueError

            return seconds


        # --------------------------------------------------
        # 分:秒
        # --------------------------------------------------

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


        # --------------------------------------------------
        # 時:分:秒
        # --------------------------------------------------

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
# 秒 → HH:MM:SS
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
# 安全なファイル名
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
# Cookie確認
# ==========================================================

def check_cookie_file():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] Cookie確認",
        flush=True
    )

    print(
        "[YTDLP] COOKIES_FILE:",
        COOKIES_FILE,
        flush=True
    )


    if not os.path.isfile(
        COOKIES_FILE
    ):

        raise RuntimeError(
            "Renderのcookies.txtが見つかりません: "
            + COOKIES_FILE
        )


    file_size = os.path.getsize(
        COOKIES_FILE
    )


    print(
        "[YTDLP] Cookie exists:",
        True,
        flush=True
    )

    print(
        "[YTDLP] Cookie size:",
        file_size,
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    if file_size <= 0:

        raise RuntimeError(
            "cookies.txtが空です。"
        )


# ==========================================================
# 一時Cookie作成
# ==========================================================

def create_temp_cookie_file():

    check_cookie_file()


    temporary_cookie = None


    try:

        temporary_file = tempfile.NamedTemporaryFile(

            mode="wb",

            suffix=".txt",

            prefix="y2conv_cookies_",

            delete=False

        )


        temporary_cookie = (
            temporary_file.name
        )


        temporary_file.close()


        shutil.copyfile(

            COOKIES_FILE,

            temporary_cookie

        )


        print(
            "[YTDLP] 一時Cookie作成:",
            temporary_cookie,
            flush=True
        )


        return temporary_cookie


    except Exception:

        if (
            temporary_cookie
            and
            os.path.exists(
                temporary_cookie
            )
        ):

            try:

                os.remove(
                    temporary_cookie
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
                "[YTDLP] 一時Cookie削除:",
                cookie_file,
                flush=True
            )


        except Exception as error:

            print(
                "[YTDLP] WARNING: Cookie削除失敗:",
                repr(error),
                flush=True
            )


# ==========================================================
# yt-dlp共通オプション
# ==========================================================

def get_ydl_base_options(
    temp_cookie,
    output_template
):

    options = {

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        "cookiefile":
            temp_cookie,


        # --------------------------------------------------
        # Playlist無効
        # --------------------------------------------------

        "noplaylist":
            True,


        # --------------------------------------------------
        # 出力
        # --------------------------------------------------

        "outtmpl":
            output_template,


        # --------------------------------------------------
        # ログ
        # --------------------------------------------------

        "quiet":
            False,

        "no_warnings":
            False,

        "noprogress":
            True,


        # --------------------------------------------------
        # ファイル名
        # --------------------------------------------------

        "restrictfilenames":
            False,


        # --------------------------------------------------
        # Deno
        #
        # 重要:
        # dict形式でpathを指定
        # --------------------------------------------------

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },


        # --------------------------------------------------
        # EJS
        #
        # 以前動作していた設定
        # --------------------------------------------------

        "remote_components": {

            "ejs":
                "github"

        }

    }


    return options


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_video_info(
    url,
    temp_cookie
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] YouTube情報取得開始",
        flush=True
    )

    print(
        "[YTDLP] URL:",
        url,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    options = {

        "cookiefile":
            temp_cookie,

        "noplaylist":
            True,

        "quiet":
            False,

        "no_warnings":
            False,

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        "remote_components": {

            "ejs":
                "github"

        }

    }


    print(
        "[YTDLP] get_video_info options:",
        options,
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
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] YouTube情報取得完了",
        flush=True
    )

    print(
        "[YTDLP] title:",
        info.get(
            "title",
            ""
        ),
        flush=True
    )

    print(
        "[YTDLP] duration:",
        info.get(
            "duration"
        ),
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return info


# ==========================================================
# YouTube元データダウンロード
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


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] YouTube元データダウンロード",
        flush=True
    )

    print(
        "[YTDLP] URL:",
        url,
        flush=True
    )

    print(
        "[YTDLP] need_video:",
        need_video,
        flush=True
    )

    print(
        "[YTDLP] start_seconds:",
        start_seconds,
        flush=True
    )

    print(
        "[YTDLP] end_seconds:",
        end_seconds,
        flush=True
    )

    print(
        "==========================================",
        flush=True
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
    # MP4
    # ======================================================

    if need_video:

        options["format"] = (

            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
            "best[ext=mp4]/"
            "best"

        )


        options["merge_output_format"] = (
            "mp4"
        )


    # ======================================================
    # MP3
    # ======================================================

    else:

        options["format"] = (
            "bestaudio/best"
        )


    # ======================================================
    # 時間指定
    # ======================================================

    if (
        start_seconds is not None
        and
        end_seconds is not None
    ):

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
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


        options["force_keyframes_at_cuts"] = False


        print(
            "[YTDLP] 時間範囲:",
            seconds_to_time(start_seconds),
            "～",
            seconds_to_time(end_seconds),
            flush=True
        )


    else:

        print(
            "[YTDLP] Fullダウンロード",
            flush=True
        )


    print(
        "[YTDLP] format:",
        options.get("format"),
        flush=True
    )


    print(
        "[YTDLP] js_runtimes:",
        options.get("js_runtimes"),
        flush=True
    )


    print(
        "[YTDLP] remote_components:",
        options.get("remote_components"),
        flush=True
    )


    # ======================================================
    # ダウンロード
    # ======================================================

    try:

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            info = ydl.extract_info(

                url,

                download=True

            )


    except Exception as error:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[YTDLP] ダウンロードエラー",
            flush=True
        )

        print(
            "[YTDLP] error type:",
            type(error).__name__,
            flush=True
        )

        print(
            "[YTDLP] error:",
            repr(error),
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        raise


    if not info:

        raise Exception(
            "YouTubeダウンロード情報を取得できませんでした"
        )


    # ======================================================
    # ファイル検索
    # ======================================================

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


        files.append(
            full_path
        )


    print(
        "[YTDLP] source files:",
        files,
        flush=True
    )


    if not files:

        raise Exception(
            "YouTube元ファイルが作成されませんでした"
        )


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


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] 元データ取得完了",
        flush=True
    )

    print(
        "[YTDLP] source_file:",
        source_file,
        flush=True
    )

    print(
        "[YTDLP] size:",
        os.path.getsize(
            source_file
        ),
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return source_file, info


# ==========================================================
# FFmpeg → MP3
# ==========================================================

def create_mp3(
    source_file,
    output_file,
    start_seconds=None,
    end_seconds=None
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] MP3作成開始",
        flush=True
    )

    print(
        "[YTDLP] input:",
        source_file,
        flush=True
    )

    print(
        "[YTDLP] output:",
        output_file,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    if not os.path.isfile(
        source_file
    ):

        raise Exception(
            "MP3入力ファイルがありません: "
            + source_file
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
        "-1",

        output_file

    ]


    print(
        "[YTDLP] FFmpeg MP3:",
        command,
        flush=True
    )


    try:

        result = subprocess.run(

            command,

            stdout=None,

            stderr=None,

            timeout=300

        )


    except subprocess.TimeoutExpired:

        raise Exception(
            "MP3作成が5分以内に終了しませんでした"
        )


    if result.returncode != 0:

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


    if not os.path.isfile(
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


    duration = get_media_duration(
        output_file
    )


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] MP3作成完了",
        flush=True
    )

    print(
        "[YTDLP] file:",
        output_file,
        flush=True
    )

    print(
        "[YTDLP] size:",
        file_size,
        "bytes",
        flush=True
    )

    print(
        "[YTDLP] duration:",
        duration,
        "seconds",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return duration


# ==========================================================
# FFmpeg → MP4
# ==========================================================

def create_mp4(
    source_file,
    output_file,
    start_seconds=None,
    end_seconds=None
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] MP4作成開始",
        flush=True
    )

    print(
        "[YTDLP] input:",
        source_file,
        flush=True
    )

    print(
        "[YTDLP] output:",
        output_file,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    if not os.path.isfile(
        source_file
    ):

        raise Exception(
            "MP4入力ファイルがありません: "
            + source_file
        )


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
        "[YTDLP] FFmpeg MP4:",
        command,
        flush=True
    )


    try:

        result = subprocess.run(

            command,

            stdout=None,

            stderr=None,

            timeout=600

        )


    except subprocess.TimeoutExpired:

        raise Exception(
            "MP4作成が10分以内に終了しませんでした"
        )


    if result.returncode != 0:

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


    if not os.path.isfile(
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


    duration = get_media_duration(
        output_file
    )


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] MP4作成完了",
        flush=True
    )

    print(
        "[YTDLP] file:",
        output_file,
        flush=True
    )

    print(
        "[YTDLP] size:",
        file_size,
        "bytes",
        flush=True
    )

    print(
        "[YTDLP] duration:",
        duration,
        "seconds",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return duration


# ==========================================================
# MP3 / MP4変換メイン
#
# convert.pyから使用
# ==========================================================

def convert(
    url,
    outputs,
    start_time=None,
    end_time=None
):

    if not url:

        raise ValueError(
            "YouTube URLが指定されていません。"
        )


    # ======================================================
    # 出力形式
    # ======================================================

    valid_outputs = []


    if isinstance(
        outputs,
        list
    ):

        if "mp3" in outputs:

            valid_outputs.append(
                "mp3"
            )


        if "mp4" in outputs:

            valid_outputs.append(
                "mp4"
            )


    if not valid_outputs:

        raise ValueError(
            "MP3またはMP4を指定してください。"
        )


    # ======================================================
    # 時間
    # ======================================================

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )


    if (
        start_seconds is not None
        and
        end_seconds is None
    ):

        raise ValueError(
            "終了時間を入力してください。"
        )


    if (
        start_seconds is None
        and
        end_seconds is not None
    ):

        start_seconds = 0

        start_time = "00:00:00"


    if (
        start_seconds is not None
        and
        end_seconds is not None
    ):

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )


    # ======================================================
    # Cookie
    # ======================================================

    temp_cookie = None

    temp_source_dir = None


    try:

        temp_cookie = (
            create_temp_cookie_file()
        )


        # ==================================================
        # YouTube情報
        # ==================================================

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
                "元動画の再生時間を取得できませんでした。"
            )


        full_duration = float(
            full_duration
        )


        # ==================================================
        # 時間範囲確認
        # ==================================================

        if end_seconds is not None:

            if end_seconds > full_duration:

                raise ValueError(

                    "終了時間が動画の再生時間を超えています。"

                )


        if start_seconds is not None:

            if start_seconds >= full_duration:

                raise ValueError(

                    "開始時間が動画の再生時間を超えています。"

                )


        # ==================================================
        # 予定再生時間
        # ==================================================

        if (
            start_seconds is not None
            and
            end_seconds is not None
        ):

            requested_duration = (

                end_seconds
                - start_seconds

            )

        else:

            requested_duration = (
                full_duration
            )


        # ==================================================
        # 一時ディレクトリ
        # ==================================================

        temp_source_dir = tempfile.mkdtemp(

            prefix="y2conv_source_"

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
        # 出力先
        # ==================================================

        os.makedirs(

            DOWNLOAD_DIR,

            exist_ok=True

        )


        mp3_file = os.path.join(

            DOWNLOAD_DIR,

            title + ".mp3"

        )


        mp4_file = os.path.join(

            DOWNLOAD_DIR,

            title + ".mp4"

        )


        files = []


        actual_mp3_duration = None

        actual_mp4_duration = None


        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in valid_outputs:

            actual_mp3_duration = create_mp3(

                source_file,

                mp3_file,

                start_seconds,

                end_seconds

            )


            files.append(

                os.path.basename(
                    mp3_file
                )

            )


        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in valid_outputs:

            actual_mp4_duration = create_mp4(

                source_file,

                mp4_file,

                start_seconds,

                end_seconds

            )


            files.append(

                os.path.basename(
                    mp4_file
                )

            )


        # ==================================================
        # 実測時間
        # ==================================================

        actual_duration = (

            actual_mp3_duration

            if actual_mp3_duration is not None

            else actual_mp4_duration

        )


        # ==================================================
        # 結果
        # ==================================================

        return {

            "success":
                True,

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
                end_seconds

        }


    finally:

        # ==================================================
        # Cookie削除
        # ==================================================

        remove_temp_cookie_file(

            temp_cookie

        )


        # ==================================================
        # 元ファイル削除
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
                    "[YTDLP] 一時元ファイル削除:",
                    temp_source_dir,
                    flush=True
                )


            except Exception as error:

                print(
                    "[YTDLP] WARNING: "
                    "一時元ファイル削除失敗:",
                    repr(error),
                    flush=True
                )
