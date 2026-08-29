# =====================================
# YouTube Converter
# ytdlp.py
#
# YouTube → MP3
# =====================================

import os
import shutil
import tempfile
import subprocess

import yt_dlp

from yt_dlp.utils import download_range_func

from config import (
    DOWNLOAD_DIR,
    COOKIES_FILE
)


# =====================================
# Render Deno
# =====================================

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"


# =====================================
# 時間 → 秒
# =====================================

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


    except Exception as error:

        raise ValueError(
            "時間形式が正しくありません: "
            + value
        ) from error


# =====================================
# 秒 → HH:MM:SS
# =====================================

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


# =====================================
# Deno確認
# =====================================

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


# =====================================
# Cookie確認
# =====================================

def check_cookie():

    if not os.path.isfile(
        COOKIES_FILE
    ):

        raise RuntimeError(
            "cookies.txtが見つかりません: "
            + COOKIES_FILE
        )


    size = os.path.getsize(
        COOKIES_FILE
    )


    print(
        "[YTDLP] Cookie:",
        COOKIES_FILE,
        flush=True
    )

    print(
        "[YTDLP] Cookie size:",
        size,
        "bytes",
        flush=True
    )


    if size <= 0:

        raise RuntimeError(
            "cookies.txtが空です。"
        )


# =====================================
# 一時Cookie作成
# =====================================

def create_temp_cookie():

    check_cookie()


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


# =====================================
# 一時Cookie削除
# =====================================

def remove_temp_cookie(
    temporary_cookie
):

    if not temporary_cookie:
        return


    if not os.path.exists(
        temporary_cookie
    ):
        return


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
            "[YTDLP] 一時Cookie削除失敗:",
            repr(error),
            flush=True
        )


# =====================================
# yt-dlp設定
# =====================================

def get_ydl_options(
    temporary_cookie,
    output_template
):

    options = {

        "cookiefile":
            temporary_cookie,

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

        "overwrites":
            True

    }


    # =================================
    # Deno
    # =================================

    if check_deno():

        options["js_runtimes"] = {

            "deno": {

                "path":
                    DENO_PATH

            }

        }


        # =================================
        # EJS
        # =================================

        options["remote_components"] = {

            "ejs":
                "github"

        }


    return options


# =====================================
# MP3作成
#
# routes/convert.pyから
#
# create_mp3(
#     url,
#     start_time=...,
#     end_time=...
# )
#
# と呼び出す。
# =====================================

def create_mp3(
    url,
    start_time=None,
    end_time=None
):

    # =================================
    # URL確認
    # =================================

    if not url:

        raise ValueError(
            "YouTube URLが指定されていません。"
        )


    url = str(
        url
    ).strip()


    # =================================
    # 時間変換
    # =================================

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )


    # =================================
    # 終了時間だけ指定
    #
    # 例:
    #
    # start_time = None
    # end_time   = 00:00:10
    #
    # ↓
    #
    # 00:00:00 ～ 00:00:10
    # =================================

    if (
        start_seconds is None
        and
        end_seconds is not None
    ):

        start_seconds = 0


    # =================================
    # 開始時間だけ指定
    # =================================

    if (
        start_seconds is not None
        and
        end_seconds is None
    ):

        raise ValueError(
            "終了時間を入力してください。"
        )


    # =================================
    # 時間チェック
    # =================================

    if (
        start_seconds is not None
        and
        end_seconds is not None
    ):

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )


    # =================================
    # downloads
    # =================================

    os.makedirs(

        DOWNLOAD_DIR,

        exist_ok=True

    )


    # =================================
    # 一時Cookie
    # =================================

    temporary_cookie = None


    # =================================
    # 一時元ファイル
    # =================================

    temporary_source_dir = None


    try:

        # =================================
        # Cookie
        # =================================

        temporary_cookie = (
            create_temp_cookie()
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
            "[YTDLP] yt-dlp:",
            yt_dlp.version.__version__,
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        # =================================
        # 一時ディレクトリ
        # =================================

        temporary_source_dir = tempfile.mkdtemp(

            prefix="y2conv_source_"

        )


        source_template = os.path.join(

            temporary_source_dir,

            "source_%(id)s.%(ext)s"

        )


        # =================================
        # yt-dlp設定
        # =================================

        options = get_ydl_options(

            temporary_cookie,

            source_template

        )


        # =================================
        # 音声
        # =================================

        options["format"] = (
            "bestaudio/best"
        )


        # =================================
        # 時間範囲
        # =================================

        if (
            start_seconds is not None
            and
            end_seconds is not None
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


            print(
                "[YTDLP] download range:",
                seconds_to_time(start_seconds),
                "-",
                seconds_to_time(end_seconds),
                flush=True
            )


        else:

            print(
                "[YTDLP] download range: FULL",
                flush=True
            )


        # =================================
        # YouTubeダウンロード
        # =================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[YTDLP] YouTubeダウンロード開始",
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
                "[YTDLP] yt-dlpエラー:",
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
                "YouTube情報を取得できませんでした。"
            )


        # =================================
        # タイトル
        # =================================

        title = info.get(

            "title",

            "youtube"

        )


        title = str(
            title
        ).strip()


        # =================================
        # ファイル名として使用できない文字
        # =================================

        for character in (

            "\\",
            "/",
            ":",
            "*",
            "?",
            "\"",
            "<",
            ">",
            "|"

        ):

            title = title.replace(

                character,

                "_"

            )


        title = title.strip(
            " ."
        )


        if not title:

            title = "youtube"


        # =================================
        # ダウンロードされた元ファイル検索
        # =================================

        source_files = []


        for filename in os.listdir(

            temporary_source_dir

        ):

            filepath = os.path.join(

                temporary_source_dir,

                filename

            )


            if not os.path.isfile(
                filepath
            ):
                continue


            if filename.endswith(
                ".part"
            ):
                continue


            if filename.startswith(
                "source_"
            ):

                source_files.append(
                    filepath
                )


        if not source_files:

            raise RuntimeError(
                "YouTube音声ファイルが作成されませんでした。"
            )


        source_file = max(

            source_files,

            key=os.path.getmtime

        )


        source_size = os.path.getsize(

            source_file

        )


        print(
            "[YTDLP] 元音声ファイル:",
            source_file,
            flush=True
        )

        print(
            "[YTDLP] 元音声サイズ:",
            source_size,
            "bytes",
            flush=True
        )


        if source_size <= 0:

            raise RuntimeError(
                "YouTube音声ファイルが0 bytesです。"
            )


        # =================================
        # MP3出力先
        # =================================

        output_file = os.path.join(

            DOWNLOAD_DIR,

            title + ".mp3"

        )


        # =================================
        # FFmpeg
        # =================================

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
            "==========================================",
            flush=True
        )

        print(
            "[YTDLP] FFmpeg開始",
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


        # =================================
        # FFmpeg実行
        # =================================

        result = subprocess.run(

            command,

            stdout=None,

            stderr=None,

            timeout=300

        )


        print(
            "[YTDLP] FFmpeg returncode:",
            result.returncode,
            flush=True
        )


        # =================================
        # FFmpegエラー
        # =================================

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
                "FFmpegによるMP3作成に失敗しました。"
            )


        # =================================
        # MP3確認
        # =================================

        if not os.path.isfile(
            output_file
        ):

            raise RuntimeError(
                "MP3ファイルが作成されませんでした。"
            )


        output_size = os.path.getsize(

            output_file

        )


        if output_size <= 0:

            raise RuntimeError(
                "MP3ファイルが0 bytesです。"
            )


        # =================================
        # 完了
        # =================================

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
            output_size,
            "bytes",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        # =================================
        # routes/convert.pyへ返す
        # =================================

        return {

            "success":
                True,

            "filename":
                os.path.basename(
                    output_file
                ),

            "path":
                output_file

        }


    finally:

        # =================================
        # 一時Cookie削除
        # =================================

        remove_temp_cookie(

            temporary_cookie

        )


        # =================================
        # 一時元ファイル削除
        # =================================

        if (
            temporary_source_dir
            and
            os.path.exists(
                temporary_source_dir
            )
        ):

            try:

                shutil.rmtree(

                    temporary_source_dir

                )


                print(
                    "[YTDLP] 一時ファイル削除:",
                    temporary_source_dir,
                    flush=True
                )


            except Exception as error:

                print(
                    "[YTDLP] 一時ファイル削除失敗:",
                    repr(error),
                    flush=True
                )
