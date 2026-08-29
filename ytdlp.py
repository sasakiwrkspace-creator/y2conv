import os
import re
import shutil
import subprocess
import tempfile

import yt_dlp

from yt_dlp.utils import download_range_func

from config import (
    BASE_DIR,
    DOWNLOAD_DIR
)


# ==========================================================
# Cookie
# ==========================================================

RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"

LOCAL_COOKIE_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt"
)


if os.environ.get("RENDER") == "true":

    SOURCE_COOKIE_FILE = RENDER_COOKIE_FILE

else:

    SOURCE_COOKIE_FILE = LOCAL_COOKIE_FILE


# ==========================================================
# Deno
#
# Dockerfileでは /root/.deno/bin/deno にインストールしている
# ==========================================================

DENO_PATH = "/root/.deno/bin/deno"


# ==========================================================
# 起動時確認
# ==========================================================

print("==========================================", flush=True)

print(
    "[YTDLP] 設定",
    flush=True
)

print(
    "[YTDLP] BASE_DIR:",
    BASE_DIR,
    flush=True
)

print(
    "[YTDLP] DOWNLOAD_DIR:",
    DOWNLOAD_DIR,
    flush=True
)

print(
    "[YTDLP] COOKIES_FILE:",
    SOURCE_COOKIE_FILE,
    flush=True
)

print(
    "[YTDLP] cookies exists:",
    os.path.exists(SOURCE_COOKIE_FILE),
    flush=True
)

print(
    "[YTDLP] Deno:",
    DENO_PATH,
    flush=True
)

print(
    "[YTDLP] Deno exists:",
    os.path.isfile(DENO_PATH),
    flush=True
)

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

    if os.path.getsize(
        SOURCE_COOKIE_FILE
    ) <= 0:

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

        os.close(fd)

        shutil.copyfile(
            SOURCE_COOKIE_FILE,
            temp_cookie
        )

        print(
            "[YTDLP] 一時Cookie作成:",
            temp_cookie,
            flush=True
        )

        return temp_cookie

    except Exception:

        if (
            temp_cookie
            and
            os.path.exists(temp_cookie)
        ):

            try:
                os.remove(temp_cookie)
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
        os.path.exists(cookie_file)
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
                "[YTDLP] Cookie削除失敗:",
                repr(error),
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
            "[YTDLP] Denoがありません:",
            DENO_PATH,
            flush=True
        )

        return False

    if not os.access(
        DENO_PATH,
        os.X_OK
    ):

        print(
            "[YTDLP] Deno実行権限がありません:",
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

    except Exception as error:

        raise ValueError(
            "時間形式が正しくありません: "
            + value
        ) from error


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
# yt-dlpオプション
# ==========================================================

def get_ydl_options(
    cookie_file,
    output_template
):

    options = {

        "cookiefile":
            cookie_file,

        "noplaylist":
            True,

        "outtmpl":
            output_template,

        "format":
            "bestaudio/best",

        "quiet":
            False,

        "no_warnings":
            False,

        "noprogress":
            True,

        "restrictfilenames":
            False

    }


    # ======================================================
    # Deno + EJS
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

        print(
            "[YTDLP] Deno使用:",
            DENO_PATH,
            flush=True
        )

    else:

        print(
            "[YTDLP] Denoなし",
            flush=True
        )


    return options


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_video_info(
    url,
    cookie_file
):

    options = get_ydl_options(
        cookie_file,
        os.path.join(
            DOWNLOAD_DIR,
            "%(id)s.%(ext)s"
        )
    )

    print(
        "[YTDLP] YouTube情報取得開始",
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
        "[YTDLP] YouTube情報取得完了",
        flush=True
    )

    return info


# ==========================================================
# YouTube音声ダウンロード
# ==========================================================

def download_audio(
    url,
    cookie_file,
    source_dir,
    start_seconds=None,
    end_seconds=None
):

    os.makedirs(
        source_dir,
        exist_ok=True
    )

    output_template = os.path.join(
        source_dir,
        "source_%(id)s.%(ext)s"
    )

    options = get_ydl_options(
        cookie_file,
        output_template
    )


    # ======================================================
    # 時間範囲
    # ======================================================

    if (
        start_seconds is not None
        and end_seconds is not None
    ):

        if end_seconds <= start_seconds:

            raise Exception(
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

        print(
            "[YTDLP] download section:",
            f"{start_seconds}-{end_seconds}",
            flush=True
        )

    else:

        print(
            "[YTDLP] download section: FULL",
            flush=True
        )


    # ======================================================
    # YouTube取得
    # ======================================================

    print(
        "[YTDLP] YouTube取得開始",
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
            "[YTDLP] yt-dlp ERROR:",
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
            "YouTube音声を取得できませんでした"
        )


    # ======================================================
    # ダウンロードファイル検索
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

        if os.path.getsize(
            full_path
        ) <= 0:

            continue

        files.append(
            full_path
        )


    if not files:

        raise Exception(
            "YouTube音声ファイルが作成されませんでした"
        )


    source_file = max(
        files,
        key=os.path.getmtime
    )


    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] ダウンロード完了",
        flush=True
    )

    print(
        "[YTDLP] source:",
        source_file,
        flush=True
    )

    print(
        "[YTDLP] size:",
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

        return result.returncode == 0

    except Exception:

        return False


# ==========================================================
# MP3作成
#
# URLを直接受け取る
# ==========================================================

def create_mp3(
    url,
    start_time=None,
    end_time=None
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
        "[YTDLP] URL:",
        url,
        flush=True
    )

    print(
        "[YTDLP] start_time:",
        start_time,
        flush=True
    )

    print(
        "[YTDLP] end_time:",
        end_time,
        flush=True
    )

    print(
        "[YTDLP] DOWNLOAD_DIR:",
        DOWNLOAD_DIR,
        flush=True
    )

    print(
        "[YTDLP] COOKIES_FILE:",
        SOURCE_COOKIE_FILE,
        flush=True
    )

    print(
        "[YTDLP] cookies exists:",
        os.path.exists(
            SOURCE_COOKIE_FILE
        ),
        flush=True
    )

    print(
        "[YTDLP] Deno:",
        DENO_PATH,
        flush=True
    )

    print(
        "[YTDLP] Deno exists:",
        os.path.isfile(
            DENO_PATH
        ),
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    # ======================================================
    # URL
    # ======================================================

    if not url:

        raise Exception(
            "YouTube URLが指定されていません"
        )


    url = str(
        url
    ).strip()


    # ======================================================
    # FFmpeg
    # ======================================================

    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    # ======================================================
    # 出力ディレクトリ
    # ======================================================

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True
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
        and end_seconds is None
    ):

        raise Exception(
            "終了時間を入力してください"
        )


    # ======================================================
    # 終了時間だけ指定
    # 00:00:00 ～ end
    # ======================================================

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


    temp_cookie = None
    source_dir = None


    try:

        # ==================================================
        # Cookie
        # ==================================================

        temp_cookie = create_temp_cookie_file()


        # ==================================================
        # YouTube情報取得
        # ==================================================

        info = get_video_info(
            url,
            temp_cookie
        )


        # ==================================================
        # タイトル
        # ==================================================

        title = safe_filename(
            info.get(
                "title",
                "youtube"
            )
        )


        print(
            "[YTDLP] タイトル:",
            title,
            flush=True
        )


        # ==================================================
        # 動画時間
        # ==================================================

        duration = info.get(
            "duration"
        )


        if duration is not None:

            duration = float(
                duration
            )


        print(
            "[YTDLP] 動画時間:",
            duration,
            flush=True
        )


        # ==================================================
        # 時間範囲確認
        # ==================================================

        if (
            duration is not None
            and end_seconds is not None
            and end_seconds > duration
        ):

            raise Exception(
                "終了時間が動画の再生時間を超えています"
            )


        if (
            duration is not None
            and start_seconds is not None
            and start_seconds >= duration
        ):

            raise Exception(
                "開始時間が動画の再生時間を超えています"
            )


        # ==================================================
        # 一時保存ディレクトリ
        # ==================================================

        source_dir = tempfile.mkdtemp(
            prefix="y2conv_source_"
        )


        print(
            "[YTDLP] 一時保存先:",
            source_dir,
            flush=True
        )


        # ==================================================
        # YouTube音声取得
        # ==================================================

        source_file, downloaded_info = download_audio(
            url,
            temp_cookie,
            source_dir,
            start_seconds,
            end_seconds
        )


        # ==================================================
        # MP3出力先
        # ==================================================

        output_file = os.path.join(
            DOWNLOAD_DIR,
            title + ".mp3"
        )


        print(
            "==========================================",
            flush=True
        )

        print(
            "[YTDLP] MP3変換開始",
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


        # ==================================================
        # FFmpeg
        #
        # yt-dlp側ですでに時間範囲を指定しているので、
        # ここでは -ss / -t を使わない。
        # ==================================================

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
            "[YTDLP] FFmpeg:",
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


        print(
            "[YTDLP] FFmpeg returncode:",
            result.returncode,
            flush=True
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


        # ==================================================
        # MP3確認
        # ==================================================

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


        print(
            "==========================================",
            flush=True
        )

        print(
            "[YTDLP] MP3作成完了",
            flush=True
        )

        print(
            "[YTDLP] filename:",
            os.path.basename(
                output_file
            ),
            flush=True
        )

        print(
            "[YTDLP] path:",
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
            "==========================================",
            flush=True
        )


        return {
            "filename": os.path.basename(output_file),
            "path": output_file,
            "title": title
        }


    finally:

        # ==================================================
        # Cookie削除
        # ==================================================

        remove_temp_cookie_file(
            temp_cookie
        )


        # ==================================================
        # 一時音声削除
        # ==================================================

        if (
            source_dir
            and
            os.path.exists(source_dir)
        ):

            try:

                shutil.rmtree(
                    source_dir
                )

                print(
                    "[YTDLP] 一時ファイル削除:",
                    source_dir,
                    flush=True
                )

            except Exception as error:

                print(
                    "[YTDLP] 一時ファイル削除失敗:",
                    repr(error),
                    flush=True
                )
