from flask import request, jsonify

import yt_dlp
import uuid
import threading
import os
import shutil
import tempfile
import subprocess
import re

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


print("==========================================")
print("convert.py Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("Cookie:", SOURCE_COOKIE_FILE)
print("==========================================")


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


    print("==========================================")
    print("Cookieファイル確認")
    print("ファイル:", SOURCE_COOKIE_FILE)
    print("サイズ:", file_size, "bytes")
    print("==========================================")


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
            temp_cookie
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
                cookie_file
            )


        except Exception as e:

            print(
                "WARNING: Cookie削除失敗:",
                repr(e)
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
            DENO_PATH
        )

        return False


    if not os.access(
        DENO_PATH,
        os.X_OK
    ):

        print(
            "Deno実行権限なし:",
            DENO_PATH
        )

        return False


    return True


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
#
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
# 秒を HH:MM:SS へ変換
#
# 画面表示用
#
# 60
# ↓
# 00:01:00
#
# 396
# ↓
# 00:06:36
#
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


    result = subprocess.run(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

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

        # --------------------------------------------------
        # ファイル名に使用できない文字対策
        # --------------------------------------------------

        "restrictfilenames":
            False

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
#
# ダウンロード前に元動画の長さを取得
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
            False

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


    return info


# ==========================================================
# ソース動画ダウンロード
#
# MP3 / MP4の元データとして使用する。
#
# 指定時間がある場合も、
# ここでは時間判定・カットをしない。
#
# 最終的な時間カットはFFmpegで行う。
#
# ==========================================================

def download_source(
    url,
    temp_cookie,
    source_dir,
    need_video
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
    #
    # 映像 + 音声
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
    #
    # 音声のみ
    # ======================================================

    else:

        options["format"] = (
            "bestaudio/best"
        )


    print("==========================================")
    print("YouTube元データダウンロード開始")
    print("URL:", url)
    print("need_video:", need_video)
    print("==========================================")


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


    # ======================================================
    # ダウンロードされたファイルを探す
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


        if filename.startswith(
            "source_"
        ):

            files.append(
                full_path
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


    print("==========================================")
    print("YouTube元データダウンロード完了")
    print("ファイル:", source_file)
    print(
        "サイズ:",
        os.path.getsize(source_file),
        "bytes"
    )
    print("==========================================")


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


    # Windows / Linux / macOSで問題になりやすい文字
    title = re.sub(

        r'[\\/:*?"<>|]+',

        "_",

        title

    )


    # 改行削除

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
# 指定時間あり:
#
# start ～ end
#
# のみを実際に出力。
#
# 指定時間なし:
#
# Full
#
# ==========================================================

def create_mp3(
    source_file,
    output_file,
    start_seconds=None,
    end_seconds=None
):

    print("==========================================")
    print("MP3作成")
    print("入力:", source_file)
    print("出力:", output_file)
    print("開始:", start_seconds)
    print("終了:", end_seconds)
    print("==========================================")


    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    command = [

        "ffmpeg",

        "-y"

    ]


    # ======================================================
    # 時間指定
    #
    # -ss / -to ではなく
    # -ss + -t を使用。
    #
    # これにより
    #
    # end - start
    #
    # の長さを明確に指定する。
    # ======================================================

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

            "-i",
            source_file,

            "-t",
            str(duration)

        ])


    else:

        command.extend([

            "-i",
            source_file

        ])


    command.extend([

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-b:a",
        "128k",

        "-map_metadata",
        "-1",

        output_file

    ])


    print(
        "FFmpeg:",
        command
    )


    result = subprocess.run(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )


    if result.returncode != 0:

        print(
            result.stderr
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


    actual_duration = get_media_duration(
        output_file
    )


    print("==========================================")
    print("MP3作成完了")
    print("ファイル:", output_file)
    print("サイズ:", file_size)
    print(
        "実際の再生時間:",
        actual_duration
    )
    print("==========================================")


    return actual_duration


# ==========================================================
# FFmpegでMP4作成
#
# 指定時間あり:
#
# start ～ end
#
# のみを実際に出力。
#
# 指定時間なし:
#
# Full
#
# ==========================================================

def create_mp4(
    source_file,
    output_file,
    start_seconds=None,
    end_seconds=None
):

    print("==========================================")
    print("MP4作成")
    print("入力:", source_file)
    print("出力:", output_file)
    print("開始:", start_seconds)
    print("終了:", end_seconds)
    print("==========================================")


    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    command = [

        "ffmpeg",

        "-y"

    ]


    # ======================================================
    # 時間指定
    # ======================================================

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

            "-i",
            source_file,

            "-t",
            str(duration)

        ])


    else:

        command.extend([

            "-i",
            source_file

        ])


    # ======================================================
    # MP4
    #
    # 映像は再エンコード。
    # 音声もAACに統一。
    #
    # 互換性を優先。
    # ======================================================

    command.extend([

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

    ])


    print(
        "FFmpeg:",
        command
    )


    result = subprocess.run(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )


    if result.returncode != 0:

        print(
            result.stderr
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


    print("==========================================")
    print("MP4作成完了")
    print("ファイル:", output_file)
    print("サイズ:", file_size)
    print(
        "実際の再生時間:",
        actual_duration
    )
    print("==========================================")


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
                end_time or ""

        }


        print("==========================================")
        print("変換処理開始")
        print("JOB:", job_id)
        print("URL:", url)
        print("OUTPUTS:", outputs)
        print("START:", start_time)
        print("END:", end_time)
        print("==========================================")


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

        temp_cookie = (
            create_temp_cookie_file()
        )


        # ==================================================
        # 古いファイル削除
        # ==================================================

        try:

            cleanup_downloads()

        except Exception as e:

            print(
                "WARNING: cleanup失敗:",
                repr(e)
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


        if (
            start_seconds is None
            and end_seconds is not None
        ):

            # 終了時間だけなら0秒から
            start_seconds = 0


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

        print("==========================================")
        print("YouTube情報取得")
        print("==========================================")


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


        print("タイトル:", title)
        print(
            "Full再生時間:",
            full_duration
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
        # 指定時間から期待再生時間を計算
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


        print("==========================================")
        print("再生時間計算")
        print(
            "開始:",
            seconds_to_time(start_seconds)
            if start_seconds is not None
            else "00:00:00"
        )
        print(
            "終了:",
            seconds_to_time(end_seconds)
            if end_seconds is not None
            else seconds_to_time(full_duration)
        )
        print(
            "再生時間:",
            seconds_to_time(requested_duration)
        )
        print(
            "Full:",
            seconds_to_time(full_duration)
        )
        print("==========================================")


        # ==================================================
        # 一時元ファイル保存場所
        # ==================================================

        temp_source_dir = tempfile.mkdtemp(
            prefix="y2conv_source_"
        )


        # ==================================================
        # MP4が必要か
        #
        # MP4を作る場合は映像＋音声を取得。
        #
        # MP3だけなら音声だけ。
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

                need_video

            )
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


        actual_duration = None


        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in valid_outputs:

            mp3_duration = create_mp3(

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


            actual_duration = (
                mp3_duration
            )


        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in valid_outputs:

            mp4_duration = create_mp4(

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


            # ------------------------------------------------
            # MP3がない場合はMP4の再生時間を使用
            # ------------------------------------------------

            if actual_duration is None:

                actual_duration = (
                    mp4_duration
                )


        # ==================================================
        # 指定時間ありの場合
        #
        # MP3 / MP4の実測値を使用。
        #
        # 画面表示用には
        #
        # 00:01:00
        #
        # のように返す。
        # ==================================================

        if actual_duration is None:

            actual_duration = (
                requested_duration
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

            # ------------------------------------------------
            # 実際に作成されたファイルの再生時間
            # ------------------------------------------------

            "duration":
                actual_duration,

            "duration_text":
                seconds_to_time(
                    actual_duration
                ),

            # ------------------------------------------------
            # 元動画Full
            # ------------------------------------------------

            "full_duration":
                full_duration,

            "full_duration_text":
                seconds_to_time(
                    full_duration
                ),

            # ------------------------------------------------
            # 指定時間
            # ------------------------------------------------

            "start_time":
                start_time or "",

            "end_time":
                end_time or "",

            "start_seconds":
                start_seconds,

            "end_seconds":
                end_seconds

        }


        print("==========================================")
        print("変換完了")
        print("JOB:", job_id)
        print("TITLE:", title)
        print(
            "DURATION:",
            actual_duration
        )
        print(
            "DURATION TEXT:",
            seconds_to_time(
                actual_duration
            )
        )
        print(
            "FULL DURATION:",
            full_duration
        )
        print(
            "FULL DURATION TEXT:",
            seconds_to_time(
                full_duration
            )
        )
        print(
            "FILES:",
            files
        )
        print("==========================================")


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
                    temp_source_dir
                )


            except Exception as e:

                print(
                    "WARNING: "
                    "一時元動画ディレクトリ削除失敗:",
                    repr(e)
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
            #
            # MP3 / MP4 / 両方
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
            #
            # 00:00 ～ 終了時間
            #
            # として扱う。
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


            print("==========================================")
            print("JOB登録")
            print("JOB:", job_id)
            print("URL:", url)
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

            }), 500
