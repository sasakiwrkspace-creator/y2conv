# =====================================
# YouTube Converter
# ytdlp.py
#
# YouTube → MP3 / MP4変換
#
# ・Render Cookie対応
# ・Deno / EJS対応
# ・時間範囲指定対応
# ・MP3作成
# ・MP4作成
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
# Render Deno
# ==========================================================

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"


# ==========================================================
# Cookie確認
# ==========================================================

def check_cookie():

    if not os.path.isfile(
        COOKIES_FILE
    ):

        raise RuntimeError(
            "Renderのcookies.txtが見つかりません: "
            + str(COOKIES_FILE)
        )


    if os.path.getsize(
        COOKIES_FILE
    ) <= 0:

        raise RuntimeError(
            "cookies.txtが空です。"
        )


# ==========================================================
# Deno確認
# ==========================================================

def check_deno():

    if not os.path.isfile(
        DENO_PATH
    ):

        print(
            "[YTDLP] Denoが見つかりません:",
            DENO_PATH,
            flush=True
        )

        return False


    if not os.access(
        DENO_PATH,
        os.X_OK
    ):

        print(
            "[YTDLP] Denoに実行権限がありません:",
            DENO_PATH,
            flush=True
        )

        return False


    print(
        "[YTDLP] Deno:",
        DENO_PATH,
        flush=True
    )

    return True


# ==========================================================
# 一時Cookie作成
# ==========================================================

def create_temp_cookie():

    check_cookie()


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


    try:

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

        if os.path.exists(
            temporary_cookie
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

def remove_temp_cookie(
    temporary_cookie
):

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


            print(
                "[YTDLP] 一時Cookie削除:",
                temporary_cookie,
                flush=True
            )


        except Exception as error:

            print(
                "[YTDLP] 一時Cookie削除エラー:",
                repr(error),
                flush=True
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
# 時間 → 秒
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

        # ----------------------------------------------
        # 秒
        # ----------------------------------------------

        if len(parts) == 1:

            seconds = float(
                parts[0]
            )

            if seconds < 0:

                raise ValueError


            return seconds


        # ----------------------------------------------
        # 分:秒
        # ----------------------------------------------

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


        # ----------------------------------------------
        # 時:分:秒
        # ----------------------------------------------

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


    except Exception as error:

        raise ValueError(

            "時間形式が正しくありません: "
            + value

        ) from error


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

        raise RuntimeError(
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

        raise RuntimeError(

            "メディア再生時間取得失敗: "
            + result.stderr.strip()

        )


    try:

        return float(
            result.stdout.strip()
        )

    except Exception as error:

        raise RuntimeError(
            "メディア再生時間を取得できませんでした"
        ) from error


# ==========================================================
# yt-dlp共通オプション
# ==========================================================

def get_ydl_options(
    temporary_cookie,
    output_template,
    need_video=False,
    start_seconds=None,
    end_seconds=None
):

    options = {

        # ----------------------------------------------
        # Cookie
        # ----------------------------------------------

        "cookiefile":
            temporary_cookie,


        # ----------------------------------------------
        # プレイリスト禁止
        # ----------------------------------------------

        "noplaylist":
            True,


        # ----------------------------------------------
        # 出力
        # ----------------------------------------------

        "outtmpl":
            output_template,


        # ----------------------------------------------
        # ログ
        # ----------------------------------------------

        "quiet":
            False,

        "no_warnings":
            False,

        "noprogress":
            True,


        # ----------------------------------------------
        # ファイル名
        # ----------------------------------------------

        "restrictfilenames":
            False

    }


    # ======================================================
    # Deno / EJS
    #
    # ★重要
    #
    # js_runtimes は
    #
    # {
    #     "deno": {}
    # }
    #
    # の形式にする。
    # ======================================================

    if check_deno():

        options["js_runtimes"] = {

            "deno": {}

        }


        # ==================================================
        # EJS remote component
        #
        # 現在のyt-dlp形式
        # ==================================================

        options["remote_components"] = {

            "ejs":
                "github"

        }


    # ======================================================
    # MP4
    # ======================================================

    if need_video:

        options["format"] = (

            "bestvideo[ext=mp4]+"
            "bestaudio[ext=m4a]/"
            "best[ext=mp4]/"
            "best"

        )

        options["merge_output_format"] = "mp4"


    # ======================================================
    # MP3
    # ======================================================

    else:

        options["format"] = (
            "bestaudio/best"
        )


    # ======================================================
    # 時間範囲
    # ======================================================

    if (
        start_seconds is not None
        and
        end_seconds is not None
    ):

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください"
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
            "[YTDLP] 時間範囲: FULL",
            flush=True
        )


    return options


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_video_info(
    url,
    temporary_cookie
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
            temporary_cookie,

        "noplaylist":
            True,

        "quiet":
            False,

        "no_warnings":
            False

    }


    if check_deno():

        options["js_runtimes"] = {

            "deno": {}

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

        raise RuntimeError(
            "YouTube情報を取得できませんでした"
        )


    print(
        "[YTDLP] YouTube情報取得完了",
        flush=True
    )


    return info


# ==========================================================
# YouTube元ファイルダウンロード
# ==========================================================

def download_source(
    url,
    temporary_cookie,
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


    options = get_ydl_options(

        temporary_cookie,

        source_template,

        need_video,

        start_seconds,

        end_seconds

    )


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] YouTubeダウンロード開始",
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
        "==========================================",
        flush=True
    )


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
            "[YTDLP] YouTubeダウンロードエラー",
            flush=True
        )

        print(
            "[YTDLP] ERROR:",
            repr(error),
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        raise


    if not info:

        raise RuntimeError(
            "YouTube元データを取得できませんでした"
        )


    # ======================================================
    # ダウンロードファイル検索
    # ======================================================

    files = []


    for filename in os.listdir(
        source_dir
    ):

        filepath = os.path.join(

            source_dir,

            filename

        )


        if not os.path.isfile(
            filepath
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
            filepath
        )


    if not files:

        raise RuntimeError(
            "YouTube元ファイルが作成されませんでした"
        )


    source_file = max(

        files,

        key=os.path.getmtime

    )


    if os.path.getsize(
        source_file
    ) <= 0:

        raise RuntimeError(
            "YouTube元ファイルが0 bytesです"
        )


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] YouTubeダウンロード完了",
        flush=True
    )

    print(
        "[YTDLP] ファイル:",
        source_file,
        flush=True
    )

    print(
        "[YTDLP] サイズ:",
        os.path.getsize(source_file),
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return source_file, info


# ==========================================================
# MP3作成
#
# ★ convert.pyとの互換性のため
#
# start_time
# end_time
#
# を受け取る。
# ==========================================================

def create_mp3(
    source_file,
    output_file,
    start_time=None,
    end_time=None,
    start_seconds=None,
    end_seconds=None
):

    # ======================================================
    # 互換処理
    #
    # convert.pyが
    #
    # start_time
    # end_time
    #
    # を渡した場合も動作する。
    # ======================================================

    if start_seconds is None:

        start_seconds = time_to_seconds(
            start_time
        )


    if end_seconds is None:

        end_seconds = time_to_seconds(
            end_time
        )


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] MP3作成開始",
        flush=True
    )

    print(
        "[YTDLP] 入力:",
        source_file,
        flush=True
    )

    print(
        "[YTDLP] 出力:",
        output_file,
        flush=True
    )

    print(
        "[YTDLP] 開始:",
        start_seconds,
        flush=True
    )

    print(
        "[YTDLP] 終了:",
        end_seconds,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    if not check_ffmpeg():

        raise RuntimeError(
            "ffmpegが利用できません"
        )


    if not os.path.exists(
        source_file
    ):

        raise RuntimeError(
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


    result = subprocess.run(

        command,

        stdout=None,

        stderr=None,

        timeout=300

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


        raise RuntimeError(
            "MP3作成に失敗しました"
        )


    if not os.path.exists(
        output_file
    ):

        raise RuntimeError(
            "MP3ファイルが作成されませんでした"
        )


    file_size = os.path.getsize(
        output_file
    )


    if file_size <= 0:

        raise RuntimeError(
            "MP3ファイルが0 bytesです"
        )


    actual_duration = get_media_duration(
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
        "[YTDLP] ファイル:",
        output_file,
        flush=True
    )

    print(
        "[YTDLP] サイズ:",
        file_size,
        "bytes",
        flush=True
    )

    print(
        "[YTDLP] 再生時間:",
        actual_duration,
        "秒",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return actual_duration


# ==========================================================
# MP4作成
# ==========================================================

def create_mp4(
    source_file,
    output_file,
    start_time=None,
    end_time=None,
    start_seconds=None,
    end_seconds=None
):

    # ======================================================
    # 互換処理
    # ======================================================

    if start_seconds is None:

        start_seconds = time_to_seconds(
            start_time
        )


    if end_seconds is None:

        end_seconds = time_to_seconds(
            end_time
        )


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] MP4作成開始",
        flush=True
    )

    print(
        "[YTDLP] 入力:",
        source_file,
        flush=True
    )

    print(
        "[YTDLP] 出力:",
        output_file,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    if not check_ffmpeg():

        raise RuntimeError(
            "ffmpegが利用できません"
        )


    if not os.path.exists(
        source_file
    ):

        raise RuntimeError(
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


    result = subprocess.run(

        command,

        stdout=None,

        stderr=None,

        timeout=600

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


        raise RuntimeError(
            "MP4作成に失敗しました"
        )


    if not os.path.exists(
        output_file
    ):

        raise RuntimeError(
            "MP4ファイルが作成されませんでした"
        )


    file_size = os.path.getsize(
        output_file
    )


    if file_size <= 0:

        raise RuntimeError(
            "MP4ファイルが0 bytesです"
        )


    actual_duration = get_media_duration(
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
        "[YTDLP] ファイル:",
        output_file,
        flush=True
    )

    print(
        "[YTDLP] サイズ:",
        file_size,
        "bytes",
        flush=True
    )

    print(
        "[YTDLP] 再生時間:",
        actual_duration,
        "秒",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return actual_duration


# ==========================================================
# メイン変換
#
# convert.pyから使用する場合の共通処理
# ==========================================================

def convert(
    url,
    outputs,
    start_time=None,
    end_time=None
):

    temporary_cookie = None

    source_dir = None


    try:

        # ==================================================
        # Cookie
        # ==================================================

        temporary_cookie = (
            create_temp_cookie()
        )


        # ==================================================
        # 時間
        # ==================================================

        start_seconds = time_to_seconds(
            start_time
        )


        end_seconds = time_to_seconds(
            end_time
        )


        # ==================================================
        # 終了時間だけ指定
        # ==================================================

        if (
            start_seconds is None
            and
            end_seconds is not None
        ):

            start_seconds = 0

            start_time = "00:00:00"


        # ==================================================
        # 開始時間だけ指定
        # ==================================================

        if (
            start_seconds is not None
            and
            end_seconds is None
        ):

            raise ValueError(
                "終了時間を入力してください"
            )


        # ==================================================
        # 時間チェック
        # ==================================================

        if (
            start_seconds is not None
            and
            end_seconds is not None
        ):

            if end_seconds <= start_seconds:

                raise ValueError(
                    "終了時間は開始時間より後にしてください"
                )


        # ==================================================
        # 出力形式
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

            raise ValueError(
                "MP3またはMP4を指定してください"
            )


        # ==================================================
        # YouTube情報
        # ==================================================

        info = get_video_info(

            url,

            temporary_cookie

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

            raise RuntimeError(
                "動画の再生時間を取得できませんでした"
            )


        full_duration = float(
            full_duration
        )


        # ==================================================
        # 範囲確認
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
        # 必要な元データ
        # ==================================================

        need_video = (
            "mp4" in valid_outputs
        )


        # ==================================================
        # 一時ディレクトリ
        # ==================================================

        source_dir = tempfile.mkdtemp(

            prefix="y2conv_source_"

        )


        # ==================================================
        # YouTubeダウンロード
        # ==================================================

        source_file, downloaded_info = (
            download_source(

                url,

                temporary_cookie,

                source_dir,

                need_video,

                start_seconds,

                end_seconds

            )
        )


        # ==================================================
        # 出力
        # ==================================================

        os.makedirs(

            DOWNLOAD_DIR,

            exist_ok=True

        )


        files = []


        mp3_file = os.path.join(

            DOWNLOAD_DIR,

            title + ".mp3"

        )


        mp4_file = os.path.join(

            DOWNLOAD_DIR,

            title + ".mp4"

        )


        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in valid_outputs:

            create_mp3(

                source_file,

                mp3_file,

                start_seconds=start_seconds,

                end_seconds=end_seconds

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

            create_mp4(

                source_file,

                mp4_file,

                start_seconds=start_seconds,

                end_seconds=end_seconds

            )


            files.append(

                os.path.basename(
                    mp4_file
                )

            )


        # ==================================================
        # 結果
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


        return {

            "success":
                True,

            "title":
                title,

            "files":
                files,

            "duration":
                requested_duration,

            "duration_text":
                seconds_to_time(
                    requested_duration
                ),

            "full_duration":
                full_duration,

            "full_duration_text":
                seconds_to_time(
                    full_duration
                )

        }


    finally:

        # ==================================================
        # Cookie削除
        # ==================================================

        remove_temp_cookie(
            temporary_cookie
        )


        # ==================================================
        # 一時元ファイル削除
        # ==================================================

        if (
            source_dir
            and
            os.path.exists(
                source_dir
            )
        ):

            try:

                shutil.rmtree(
                    source_dir
                )


                print(
                    "[YTDLP] 一時元ファイル削除:",
                    source_dir,
                    flush=True
                )


            except Exception as error:

                print(
                    "[YTDLP] 一時元ファイル削除エラー:",
                    repr(error),
                    flush=True
                )
