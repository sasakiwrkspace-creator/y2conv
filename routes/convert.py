from flask import request, jsonify

import yt_dlp
import uuid
import threading
import os
import subprocess
import shutil
import tempfile
import glob

from routes.status import jobs
from cleanup import cleanup_downloads


# ==========================================================
# Render Cookie
# ==========================================================

RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ==========================================================
# プロジェクトルート
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
# Deno
# ==========================================================

DENO_PATH = "/opt/render/project/src/.deno/bin/deno"


# ==========================================================
# ダウンロードディレクトリ
# ==========================================================

DOWNLOAD_DIR = os.path.join(
    BASE_DIR,
    "downloads"
)


# ==========================================================
# Cookieファイル選択
# ==========================================================

if os.environ.get("RENDER") == "true":

    SOURCE_COOKIE_FILE = RENDER_COOKIE_FILE

else:

    SOURCE_COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("convert.py 起動")
print("==========================================")
print(
    "RENDER:",
    os.environ.get("RENDER")
)
print(
    "Cookie:",
    SOURCE_COOKIE_FILE
)
print(
    "Deno:",
    DENO_PATH
)
print(
    "Download:",
    DOWNLOAD_DIR
)
print("==========================================")


# ==========================================================
# 時間文字列 → 秒
#
# 例:
#
# 0:15      → 15
# 1:30      → 90
# 01:02:30  → 3750
#
# ==========================================================

def time_to_seconds(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    try:

        parts = value.split(":")

        if len(parts) == 1:

            return float(parts[0])

        if len(parts) == 2:

            minutes = float(parts[0])
            seconds = float(parts[1])

            return (
                minutes * 60
                + seconds
            )

        if len(parts) == 3:

            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])

            return (
                hours * 3600
                + minutes * 60
                + seconds
            )

        raise ValueError(
            "時間形式が不正です"
        )

    except Exception:

        raise ValueError(
            f"時間形式が不正です: {value}"
        )


# ==========================================================
# 秒 → 時間文字列
#
# 例:
#
# 15  → 0:15
# 90  → 1:30
#
# ==========================================================

def seconds_to_time(seconds):

    if seconds is None:
        return "0:00"

    seconds = int(
        float(seconds)
    )

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = (
        seconds % 60
    )

    if hours > 0:

        return (
            f"{hours}:"
            f"{minutes:02d}:"
            f"{secs:02d}"
        )

    return (
        f"{minutes}:"
        f"{secs:02d}"
    )


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
    print("元Cookieファイル確認")
    print("==========================================")
    print(
        "ファイル:",
        SOURCE_COOKIE_FILE
    )
    print(
        "サイズ:",
        file_size,
        "bytes"
    )
    print("==========================================")

    if file_size == 0:

        raise Exception(
            "Cookieファイルが空です: "
            + SOURCE_COOKIE_FILE
        )

    cookie_count = 0
    youtube_cookie_count = 0

    try:

        with open(
            SOURCE_COOKIE_FILE,
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

                fields = line.split("\t")

                if len(fields) >= 7:

                    cookie_count += 1

                    domain = (
                        fields[0]
                        .lower()
                    )

                    if (
                        "youtube.com"
                        in domain
                        or
                        "google.com"
                        in domain
                    ):

                        youtube_cookie_count += 1

    except Exception as e:

        raise Exception(
            "Cookieファイル読み込み失敗: "
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

        raise Exception(
            "Cookieデータが0件です"
        )

    if youtube_cookie_count == 0:

        print(
            "WARNING: "
            "YouTube/Google Cookieが見つかりません"
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

        file_size = os.path.getsize(
            temp_cookie
        )

        print("==========================================")
        print("yt-dlp用Cookie作成OK")
        print(
            "一時Cookie:",
            temp_cookie
        )
        print(
            "サイズ:",
            file_size,
            "bytes"
        )
        print("==========================================")

        if file_size == 0:

            raise Exception(
                "一時Cookieファイルが空です"
            )

        return temp_cookie

    except Exception:

        if (
            temp_cookie
            and os.path.exists(temp_cookie)
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

    if not cookie_file:
        return

    if not os.path.exists(
        cookie_file
    ):
        return

    try:

        os.remove(
            cookie_file
        )

        print(
            "一時Cookie削除OK:",
            cookie_file
        )

    except Exception as e:

        print(
            "WARNING: "
            "一時Cookie削除失敗:",
            repr(e)
        )


# ==========================================================
# Deno確認
# ==========================================================

def check_deno():

    print("==========================================")
    print("Deno確認")
    print("==========================================")

    if not os.path.isfile(
        DENO_PATH
    ):

        print(
            "Denoなし:",
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

    try:

        result = subprocess.run(

            [
                DENO_PATH,
                "--version"
            ],

            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10

        )

        if result.returncode == 0:

            print(
                result.stdout.strip()
            )

            print(
                "Deno確認OK"
            )

            return True

        print(
            "Deno実行失敗:",
            result.stderr.strip()
        )

        return False

    except Exception as e:

        print(
            "Deno確認エラー:",
            repr(e)
        )

        return False


# ==========================================================
# yt-dlp共通設定
# ==========================================================

def get_ydl_base_options():

    temp_cookie = (
        create_temp_cookie_file()
    )

    deno_available = check_deno()

    ydl_opts = {

        # ----------------------------------------------
        # Cookie
        # ----------------------------------------------

        "cookiefile":
        temp_cookie,

        # ----------------------------------------------
        # Playlist無効
        # ----------------------------------------------

        "noplaylist":
        True,

        # ----------------------------------------------
        # ネットワーク関連
        # ----------------------------------------------

        "socket_timeout":
        30,

        "retries":
        3,

        "fragment_retries":
        3

    }

    # ----------------------------------------------
    # Deno
    # ----------------------------------------------

    if deno_available:

        ydl_opts[
            "js_runtimes"
        ] = {

            "deno": {

                "path":
                DENO_PATH

            }

        }

        ydl_opts[
            "remote_components"
        ] = {

            "ejs":
            "github"

        }

    print("==========================================")
    print("yt-dlp設定")
    print("==========================================")

    print(
        "Cookie:",
        temp_cookie
    )

    print(
        "Deno:",
        DENO_PATH
        if deno_available
        else "None"
    )

    print(
        "EJS:",
        "github"
        if deno_available
        else "None"
    )

    print("==========================================")

    return (
        ydl_opts,
        temp_cookie
    )


# ==========================================================
# YouTube情報取得
#
# MP3作成前に情報を取る
#
# 注意:
# ここではformat診断を大量に出さない。
#
# 512MB対策として余計な処理を避ける。
#
# ==========================================================

def get_youtube_info(url):

    ydl_opts = None
    temp_cookie = None

    try:

        print("==========================================")
        print("YouTube情報取得開始")
        print(
            "URL:",
            url
        )
        print("==========================================")

        (
            ydl_opts,
            temp_cookie
        ) = get_ydl_base_options()

        ydl_opts.update({

            "skip_download":
            True,

            "quiet":
            False,

            "no_warnings":
            False,

            "verbose":
            True

        })

        print(
            ">>> extract_info 実行直前"
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        print(
            ">>> extract_info 実行完了"
        )

        if not info:

            raise Exception(
                "YouTube情報を取得できませんでした"
            )

        title = info.get(
            "title",
            "タイトル取得失敗"
        )

        duration = info.get(
            "duration"
        )

        video_id = info.get(
            "id"
        )

        print("==========================================")
        print(
            "タイトル:",
            title
        )
        print(
            "Video ID:",
            video_id
        )
        print(
            "再生時間:",
            duration,
            "秒"
        )
        print("==========================================")

        return info

    finally:

        remove_temp_cookie_file(
            temp_cookie
        )


# ==========================================================
# MP3ファイル検索
# ==========================================================

def find_mp3_file(
    output_dir,
    before_files=None
):

    if before_files is None:

        before_files = set()

    mp3_files = []

    for filename in os.listdir(
        output_dir
    ):

        if not filename.lower().endswith(
            ".mp3"
        ):
            continue

        full_path = os.path.join(
            output_dir,
            filename
        )

        if not os.path.isfile(
            full_path
        ):
            continue

        mp3_files.append(
            full_path
        )

    if not mp3_files:

        return None

    # 新しく作成されたファイルを優先
    new_files = [

        path

        for path in mp3_files

        if path not in before_files

    ]

    if new_files:

        return max(
            new_files,
            key=os.path.getmtime
        )

    return max(
        mp3_files,
        key=os.path.getmtime
    )


# ==========================================================
# MP3直接作成
#
# YouTube
#   ↓
# 音声
#   ↓
# ffmpeg
#   ↓
# MP3
#
# ここでは時間カットしない。
#
# ==========================================================

def download_mp3(
    url,
    output_dir
):

    print("==========================================")
    print("MP3作成開始")
    print(
        "URL:",
        url
    )
    print("==========================================")

    ydl_opts = None
    temp_cookie = None

    try:

        # ----------------------------------------------
        # Cookie + yt-dlp
        # ----------------------------------------------

        (
            ydl_opts,
            temp_cookie
        ) = get_ydl_base_options()

        # ----------------------------------------------
        # 出力先
        # ----------------------------------------------

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        # ----------------------------------------------
        # 変換前ファイル一覧
        # ----------------------------------------------

        before_files = set()

        for filename in os.listdir(
            output_dir
        ):

            before_files.add(
                os.path.join(
                    output_dir,
                    filename
                )
            )

        # ----------------------------------------------
        # MP3設定
        # ----------------------------------------------

        ydl_opts.update({

            # 音声のみ
            "format":
            "bestaudio/best",

            # 出力
            "outtmpl":
            os.path.join(
                output_dir,
                "%(id)s.%(ext)s"
            ),

            # MP3変換
            "postprocessors": [

                {

                    "key":
                    "FFmpegExtractAudio",

                    "preferredcodec":
                    "mp3",

                    "preferredquality":
                    "128"

                }

            ],

            # ログ
            "quiet":
            False,

            "no_warnings":
            False,

            "verbose":
            True

        })

        print("==========================================")
        print("MP3設定")
        print("==========================================")

        print(
            "Format:",
            "bestaudio/best"
        )

        print(
            "Quality:",
            "128 kbps"
        )

        print(
            "Output:",
            output_dir
        )

        print(
            "Cookie:",
            temp_cookie
        )

        print("==========================================")

        # ----------------------------------------------
        # yt-dlp
        # ----------------------------------------------

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                ">>> yt-dlp.download()開始"
            )

            result = ydl.download(
                [url]
            )

            print(
                ">>> yt-dlp.download()完了"
            )

        if result != 0:

            raise Exception(
                "yt-dlp MP3作成失敗: "
                + str(result)
            )

        # ----------------------------------------------
        # MP3確認
        # ----------------------------------------------

        mp3_file = find_mp3_file(
            output_dir,
            before_files
        )

        if not mp3_file:

            raise Exception(
                "MP3ファイルが作成されませんでした"
            )

        file_size = os.path.getsize(
            mp3_file
        )

        print("==========================================")
        print("MP3作成成功")
        print(
            "ファイル:",
            mp3_file
        )
        print(
            "サイズ:",
            file_size,
            "bytes"
        )
        print("==========================================")

        if file_size == 0:

            raise Exception(
                "MP3ファイルが0 bytesです"
            )

        return mp3_file

    finally:

        remove_temp_cookie_file(
            temp_cookie
        )


# ==========================================================
# MP3カット
#
# この関数は「Geminiへ送る直前」に使用する。
#
# MP3作成時には呼び出さない。
#
# ==========================================================

def cut_mp3(
    mp3_file,
    start_time,
    end_time
):

    print("==========================================")
    print("MP3カット開始")
    print("==========================================")

    print(
        "元ファイル:",
        mp3_file
    )

    print(
        "開始:",
        start_time
    )

    print(
        "終了:",
        end_time
    )

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )

    if start_seconds is None:

        raise Exception(
            "開始時間が指定されていません"
        )

    if end_seconds is None:

        raise Exception(
            "終了時間が指定されていません"
        )

    if start_seconds < 0:

        raise Exception(
            "開始時間が0未満です"
        )

    if end_seconds <= start_seconds:

        raise Exception(
            "終了時間は開始時間より後にしてください"
        )

    cut_file = (
        os.path.splitext(
            mp3_file
        )[0]
        + "_cut.mp3"
    )

    print(
        "開始秒:",
        start_seconds
    )

    print(
        "終了秒:",
        end_seconds
    )

    print(
        "出力:",
        cut_file
    )

    # ----------------------------------------------
    # ffmpeg
    #
    # -ss を入力前に置くことで
    # 不要な部分をなるべく処理しない。
    #
    # ----------------------------------------------

    command = [

        "ffmpeg",

        "-y",

        "-ss",
        str(start_seconds),

        "-i",
        mp3_file,

        "-t",
        str(
            end_seconds
            - start_seconds
        ),

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-b:a",
        "128k",

        cut_file

    ]

    print(
        "FFmpeg:",
        " ".join(command)
    )

    result = subprocess.run(

        command,

        stdout=subprocess.DEVNULL,

        stderr=subprocess.PIPE,

        text=True

    )

    if result.returncode != 0:

        print(
            result.stderr
        )

        raise Exception(
            "ffmpeg MP3カット失敗"
        )

    if not os.path.exists(
        cut_file
    ):

        raise Exception(
            "カット後MP3が作成されませんでした"
        )

    cut_size = os.path.getsize(
        cut_file
    )

    if cut_size == 0:

        try:
            os.remove(
                cut_file
            )
        except Exception:
            pass

        raise Exception(
            "カット後MP3が0 bytesです"
        )

    print("==========================================")
    print("MP3カット完了")
    print(
        "ファイル:",
        cut_file
    )
    print(
        "サイズ:",
        cut_size,
        "bytes"
    )
    print("==========================================")

    return cut_file


# ==========================================================
# MP3カット後、元ファイルを削除
# ==========================================================

def replace_with_cut_mp3(
    original_file,
    cut_file
):

    if not os.path.exists(
        cut_file
    ):

        raise Exception(
            "カットMP3がありません"
        )

    if os.path.exists(
        original_file
    ):

        os.remove(
            original_file
        )

    os.rename(
        cut_file,
        original_file
    )

    return original_file


# ==========================================================
# MP3作成JOB
#
# 重要:
#
# この関数ではMP3作成後に終了する。
#
# Geminiには送らない。
# 時間指定のcutもしない。
#
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
        # running
        # ==================================================

        jobs[job_id] = {

            "status":
            "running",

            "url":
            url,

            "requested_outputs":
            outputs,

            "original_start_time":
            start_time,

            "original_end_time":
            end_time

        }

        print("==========================================")
        print("変換JOB開始")
        print(
            "JOB:",
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
        print(
            "開始時間:",
            start_time
        )
        print(
            "終了時間:",
            end_time
        )
        print("==========================================")

        # ==================================================
        # Cookie確認
        # ==================================================

        check_cookie_file()

        # ==================================================
        # 古いファイル削除
        # ==================================================

        try:

            cleanup_downloads()

        except Exception as e:

            print(
                "WARNING: "
                "cleanup_downloads失敗:",
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

        print(
            "出力ディレクトリ:",
            output_dir
        )

        # ==================================================
        # MP3のみ
        # ==================================================

        if "mp3" not in outputs:

            raise Exception(
                "現在の軽量MP3処理では"
                "mp3のみ対応しています"
            )

        # ==================================================
        # YouTube情報取得
        #
        # タイトル・再生時間を取得
        # ==================================================

        info = get_youtube_info(
            url
        )

        title = info.get(
            "title",
            "タイトル取得失敗"
        )

        duration_sec = info.get(
            "duration"
        )

        video_id = info.get(
            "id"
        )

        if duration_sec is None:

            duration_sec = 0

        duration_sec = int(
            duration_sec
        )

        duration = seconds_to_time(
            duration_sec
        )

        # ==================================================
        # MP3作成
        # ==================================================

        mp3_file = download_mp3(
            url,
            output_dir
        )

        mp3_filename = os.path.basename(
            mp3_file
        )

        mp3_size = os.path.getsize(
            mp3_file
        )

        # ==================================================
        # ★ここで処理を止める
        #
        # まだcutしない
        # まだGeminiへ送らない
        #
        # ==================================================

        jobs[job_id] = {

            "status":
            "mp3_ready",

            "url":
            url,

            "video_id":
            video_id,

            "title":
            title,

            "duration":
            duration,

            "duration_seconds":
            duration_sec,

            "mp3_file":
            mp3_filename,

            "mp3_path":
            mp3_file,

            "mp3_size":
            mp3_size,

            # ------------------------------------------
            # 最初に入力された時間を退避
            # ------------------------------------------

            "original_start_time":
            start_time,

            "original_end_time":
            end_time,

            # ------------------------------------------
            # 現在の時間
            #
            # 最初はoriginalと同じ
            # ------------------------------------------

            "current_start_time":
            start_time,

            "current_end_time":
            end_time

        }

        print("==========================================")
        print("MP3作成完了")
        print("==========================================")

        print(
            "JOB:",
            job_id
        )

        print(
            "タイトル:",
            title
        )

        print(
            "開始:",
            start_time
        )

        print(
            "終了:",
            end_time
        )

        print(
            "MP3:",
            mp3_file
        )

        print(
            "MP3サイズ:",
            mp3_size,
            "bytes"
        )

        print(
            "STATUS:",
            "mp3_ready"
        )

        print("==========================================")

        # ==================================================
        # ここで終了
        # ==================================================

        return

    except Exception as e:

        print("==========================================")
        print("変換JOBエラー")
        print("==========================================")

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


# ==========================================================
# /convert
#
# MP3作成を開始する
#
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
                    "URLがありません"

                }), 400

            # ==================================================
            # outputs
            # ==================================================

            outputs = data.get(
                "outputs",
                ["mp3"]
            )

            if isinstance(
                outputs,
                str
            ):

                outputs = [
                    outputs
                ]

            # ==================================================
            # 現在はMP3だけ許可
            # ==================================================

            valid_outputs = []

            for output in outputs:

                if output == "mp3":

                    if output not in valid_outputs:

                        valid_outputs.append(
                            output
                        )

            if not valid_outputs:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "現在はMP3出力のみ対応しています"

                }), 400

            # ==================================================
            # 時間
            #
            # ここではまだcutしない。
            #
            # 元の値を保存するだけ。
            # ==================================================

            start_time = data.get(
                "start_time"
            )

            end_time = data.get(
                "end_time"
            )

            # ==================================================
            # 時間形式チェック
            # ==================================================

            if start_time:

                try:

                    time_to_seconds(
                        start_time
                    )

                except Exception as e:

                    return jsonify({

                        "success":
                        False,

                        "message":
                        str(e)

                    }), 400

            if end_time:

                try:

                    time_to_seconds(
                        end_time
                    )

                except Exception as e:

                    return jsonify({

                        "success":
                        False,

                        "message":
                        str(e)

                    }), 400

            # ==================================================
            # 開始 < 終了
            # ==================================================

            if (
                start_time
                and end_time
            ):

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

                if (
                    end_seconds
                    <= start_seconds
                ):

                    return jsonify({

                        "success":
                        False,

                        "message":
                        "終了時間は開始時間より後にしてください"

                    }), 400

            # ==================================================
            # JOB ID
            # ==================================================

            job_id = str(
                uuid.uuid4()
            )

            # ==================================================
            # JOB登録
            # ==================================================

            jobs[job_id] = {

                "status":
                "queued"

            }

            print("==========================================")
            print("JOB登録")
            print("==========================================")

            print(
                "JOB:",
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
                "開始:",
                start_time
            )

            print(
                "終了:",
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

                ),

                daemon=True

            )

            thread.start()

            # ==================================================
            # JOB ID返却
            # ==================================================

            return jsonify({

                "success":
                True,

                "job_id":
                job_id,

                "status":
                "queued"

            })

        except Exception as e:

            print("==========================================")
            print("/convertエラー")
            print("==========================================")

            print(
                "ERROR TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                repr(e)
            )

            print("==========================================")

            return jsonify({

                "success":
                False,

                "message":
                str(e)

            }), 500


# ==========================================================
# /prepare-gemini
#
# ★次の段階でGeminiに送るための入口
#
# 現段階ではGemini APIを呼ばず、
# 「どのMP3を使うか」を決定するところまで。
#
# ==========================================================

def register_gemini_prepare(app):


    @app.route(
        "/prepare-gemini",
        methods=["POST"]
    )
    def prepare_gemini():

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

            # ==================================================
            # JOB ID
            # ==================================================

            job_id = data.get(
                "job_id"
            )

            if not job_id:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "job_idがありません"

                }), 400

            # ==================================================
            # JOB確認
            # ==================================================

            job = jobs.get(
                job_id
            )

            if not job:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "JOBが見つかりません"

                }), 404

            # ==================================================
            # MP3完成待ち
            # ==================================================

            if job.get(
                "status"
            ) != "mp3_ready":

                return jsonify({

                    "success":
                    False,

                    "message":
                    "MP3がまだ完成していません",

                    "status":
                    job.get("status")

                }), 409

            # ==================================================
            # 現在の時間
            # ==================================================

            current_start = data.get(
                "start_time"
            )

            current_end = data.get(
                "end_time"
            )

            original_start = job.get(
                "original_start_time"
            )

            original_end = job.get(
                "original_end_time"
            )

            # ==================================================
            # 時間変更判定
            # ==================================================

            changed = (

                current_start
                !=
                original_start

                or

                current_end
                !=
                original_end

            )

            original_mp3 = job.get(
                "mp3_path"
            )

            if not original_mp3:

                raise Exception(
                    "JOBにMP3ファイル情報がありません"
                )

            if not os.path.exists(
                original_mp3
            ):

                raise Exception(
                    "MP3ファイルが存在しません: "
                    + original_mp3
                )

            # ==================================================
            # 変更あり
            #
            # 元MP3 → cut MP3
            # ==================================================

            if changed:

                if (
                    not current_start
                    or
                    not current_end
                ):

                    return jsonify({

                        "success":
                        False,

                        "message":
                        "開始時間と終了時間の両方を指定してください"

                    }), 400

                print("==========================================")
                print("Gemini送信前MP3カット")
                print("==========================================")

                print(
                    "元開始:",
                    original_start
                )

                print(
                    "元終了:",
                    original_end
                )

                print(
                    "現在開始:",
                    current_start
                )

                print(
                    "現在終了:",
                    current_end
                )

                print(
                    "変更あり:",
                    True
                )

                cut_file = cut_mp3(

                    original_mp3,

                    current_start,

                    current_end

                )

                # ------------------------------------------
                # Gemini用MP3を確定
                #
                # 元MP3は残す。
                #
                # 512MB対策として、
                # 不要になったら後でcleanupする。
                # ------------------------------------------

                gemini_mp3 = cut_file

            else:

                print("==========================================")
                print("Gemini送信前MP3カット不要")
                print("==========================================")

                print(
                    "変更あり:",
                    False
                )

                gemini_mp3 = original_mp3

            # ==================================================
            # JOB更新
            # ==================================================

            jobs[job_id].update({

                "current_start_time":
                current_start,

                "current_end_time":
                current_end,

                "time_changed":
                changed,

                "gemini_mp3":
                gemini_mp3,

                "gemini_mp3_filename":
                os.path.basename(
                    gemini_mp3
                ),

                "gemini_mp3_size":
                os.path.getsize(
                    gemini_mp3
                ),

                "status":
                "gemini_ready"

            })

            print("==========================================")
            print("Gemini用MP3準備完了")
            print("==========================================")

            print(
                "JOB:",
                job_id
            )

            print(
                "Gemini MP3:",
                gemini_mp3
            )

            print(
                "変更あり:",
                changed
            )

            print(
                "STATUS:",
                "gemini_ready"
            )

            print("==========================================")

            # ==================================================
            # 現段階ではGemini APIには送らない
            # ==================================================

            return jsonify({

                "success":
                True,

                "job_id":
                job_id,

                "status":
                "gemini_ready",

                "title":
                job.get("title"),

                "original_mp3":
                job.get("mp3_file"),

                "gemini_mp3":
                os.path.basename(
                    gemini_mp3
                ),

                "time_changed":
                changed,

                "start_time":
                current_start,

                "end_time":
                current_end,

                "message":
                "Gemini送信用MP3の準備が完了しました"

            })

        except Exception as e:

            print("==========================================")
            print("/prepare-geminiエラー")
            print("==========================================")

            print(
                "ERROR TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                repr(e)
            )

            print("==========================================")

            return jsonify({

                "success":
                False,

                "message":
                str(e)

            }), 500
