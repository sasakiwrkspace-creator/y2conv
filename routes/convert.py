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

from paths import DOWNLOAD_DIR

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
#
# /etc/secrets/cookies.txt は読み取り専用のため、
# /tmpへコピーしてyt-dlpから使用する。
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
            "一時Cookie作成:",
            temp_cookie
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

    if (
        cookie_file
        and os.path.exists(cookie_file)
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
# yt-dlp設定
#
# 512MB環境を考慮して必要最小限
# ==========================================================

def get_ydl_options(
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
        # 音声のみ
        # --------------------------------------------------

        "format":
            "bestaudio/best",


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


        # --------------------------------------------------
        # 不要な情報を極力保持しない
        # --------------------------------------------------

        "noprogress":
            True

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
# MP3ダウンロード
#
# YouTube
# ↓
# 音声
# ↓
# ffmpeg
# ↓
# MP3
# ==========================================================

def download_mp3(
    url,
    output_dir
):

    print("==========================================")
    print("MP3作成開始")
    print("URL:", url)
    print("==========================================")


    temp_cookie = None


    try:

        # ==================================================
        # Cookie
        # ==================================================

        temp_cookie = (
            create_temp_cookie_file()
        )


        # ==================================================
        # 出力ディレクトリ
        # ==================================================

        os.makedirs(
            output_dir,
            exist_ok=True
        )


        # ==================================================
        # 出力ファイル
        #
        # YouTubeタイトル.mp3
        # ==================================================

        output_template = os.path.join(

            output_dir,

            "%(title)s.%(ext)s"

        )


        # ==================================================
        # yt-dlp
        # ==================================================

        ydl_opts = get_ydl_options(

            temp_cookie,

            output_template

        )


        # ==================================================
        # MP3変換
        # ==================================================

        ydl_opts["postprocessors"] = [

            {

                "key":
                    "FFmpegExtractAudio",

                "preferredcodec":
                    "mp3",

                "preferredquality":
                    "128"

            }

        ]


        print("==========================================")
        print("yt-dlp MP3設定")
        print("format: bestaudio/best")
        print("MP3 quality: 128kbps")
        print("==========================================")


        # ==================================================
        # ダウンロード
        # ==================================================

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                ">>> yt-dlp開始"
            )


            info = ydl.extract_info(
                url,
                download=True
            )


            print(
                ">>> yt-dlp完了"
            )


        if not info:

            raise Exception(
                "YouTube情報を取得できませんでした"
            )


        # ==================================================
        # 作成されたファイルを探す
        # ==================================================

        mp3_files = []


        for filename in os.listdir(
            output_dir
        ):

            if filename.lower().endswith(
                ".mp3"
            ):

                full_path = os.path.join(
                    output_dir,
                    filename
                )


                if os.path.isfile(
                    full_path
                ):

                    mp3_files.append(
                        full_path
                    )


        if not mp3_files:

            raise Exception(
                "MP3ファイルが作成されませんでした"
            )


        # ==================================================
        # 最新ファイル
        # ==================================================

        mp3_file = max(

            mp3_files,

            key=os.path.getmtime

        )


        file_size = os.path.getsize(
            mp3_file
        )


        if file_size <= 0:

            raise Exception(
                "MP3ファイルが0 bytesです"
            )


        # ==================================================
        # タイトル
        # ==================================================

        title = info.get(
            "title",
            ""
        )


        duration = info.get(
            "duration"
        )


        print("==========================================")
        print("MP3作成成功")
        print("タイトル:", title)
        print("再生時間:", duration)
        print("MP3:", mp3_file)
        print("サイズ:", file_size, "bytes")
        print("==========================================")


        return {

            "file":
                mp3_file,

            "title":
                title,

            "duration":
                duration

        }


    finally:

        remove_temp_cookie_file(
            temp_cookie
        )


# ==========================================================
# 時間を秒へ変換
#
# 00:00:30
# 00:30
# 30
# ==========================================================

def time_to_seconds(
    value
):

    if not value:

        return 0


    value = str(
        value
    ).strip()


    if not value:

        return 0


    parts = value.split(":")


    try:

        if len(parts) == 1:

            return float(
                parts[0]
            )


        if len(parts) == 2:

            minutes = float(
                parts[0]
            )

            seconds = float(
                parts[1]
            )

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

            return (

                hours * 3600
                +
                minutes * 60
                +
                seconds

            )


        raise ValueError(
            "時間形式が正しくありません"
        )


    except Exception:

        raise ValueError(
            "時間形式が正しくありません: "
            + value
        )


# ==========================================================
# MP3カット
#
# 元MP3
# ↓
# ffmpeg
# ↓
# カット後MP3
#
# 元MP3を残さない。
#
# これによりGeminiへ送るMP3と
# ユーザーがダウンロードするMP3を
# 同じファイルにする。
# ==========================================================

def cut_mp3(
    mp3_file,
    start_time,
    end_time
):

    print("==========================================")
    print("MP3カット開始")
    print("ファイル:", mp3_file)
    print("開始:", start_time)
    print("終了:", end_time)
    print("==========================================")


    start_seconds = time_to_seconds(
        start_time
    )


    end_seconds = time_to_seconds(
        end_time
    )


    if end_seconds <= start_seconds:

        raise Exception(
            "終了時間は開始時間より後にしてください"
        )


    # ==================================================
    # 一時ファイル
    #
    # 同じディレクトリに作成
    # ==================================================

    base, ext = os.path.splitext(
        mp3_file
    )


    cut_file = (
        base
        + "_cut"
        + ext
    )


    # ==================================================
    # ffmpeg
    #
    # -ssを入力前に置いて高速seek
    #
    # -c copyではなく再エンコードする。
    # MP3の開始位置を正確に合わせるため。
    #
    # 128kbpsで再エンコード。
    # ==================================================

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
        "ffmpeg command:",
        command
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


        if os.path.exists(
            cut_file
        ):

            try:

                os.remove(
                    cut_file
                )

            except Exception:

                pass


        raise Exception(
            "ffmpeg MP3カット失敗"
        )


    # ==================================================
    # 完成確認
    # ==================================================

    if not os.path.exists(
        cut_file
    ):

        raise Exception(
            "カット後MP3が作成されませんでした"
        )


    cut_size = os.path.getsize(
        cut_file
    )


    if cut_size <= 0:

        raise Exception(
            "カット後MP3が0 bytesです"
        )


    # ==================================================
    # 元MP3削除
    # ==================================================

    try:

        os.remove(
            mp3_file
        )

    except Exception as e:

        print(
            "WARNING: 元MP3削除失敗:",
            repr(e)
        )


    # ==================================================
    # 元と同じ名前へ変更
    #
    # 重要
    #
    # Geminiに渡すファイル名も
    # ダウンロードするファイル名も
    # 同じになる。
    # ==================================================

    os.rename(
        cut_file,
        mp3_file
    )


    print("==========================================")
    print("MP3カット完了")
    print("開始:", start_time)
    print("終了:", end_time)
    print("MP3:", mp3_file)
    print("サイズ:", cut_size, "bytes")
    print("==========================================")


    return mp3_file


# ==========================================================
# 変換処理
#
# MP3だけを作成する。
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

            "status":
                "running"

        }


        print("==========================================")
        print("変換開始")
        print("JOB:", job_id)
        print("URL:", url)
        print("OUTPUTS:", outputs)
        print("START:", start_time)
        print("END:", end_time)
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


        files = []


        # ==================================================
        # MP3
        # ==================================================

        if "mp3" not in outputs:

            raise Exception(
                "MP3出力が指定されていません"
            )


        # ==================================================
        # MP3作成
        # ==================================================

        result = download_mp3(

            url,

            output_dir

        )


        mp3_file = result["file"]

        title = result["title"]

        duration = result["duration"]


        # ==================================================
        # 時間指定判定
        # ==================================================

        has_start = bool(
            start_time
        )


        has_end = bool(
            end_time
        )


        # ==================================================
        # 時間指定なし
        #
        # そのままMP3を使用
        # ==================================================

        if not has_start and not has_end:

            print("==========================================")
            print("時間指定なし")
            print("MP3をそのまま使用")
            print("==========================================")


        # ==================================================
        # 開始なし・終了あり
        #
        # 00:00:00から終了時間
        # ==================================================

        elif not has_start and has_end:

            print("==========================================")
            print("開始時間なし")
            print("00:00:00から終了時間までカット")
            print("終了:", end_time)
            print("==========================================")


            mp3_file = cut_mp3(

                mp3_file,

                "00:00:00",

                end_time

            )


        # ==================================================
        # 開始あり・終了なし
        #
        # UI側では通常発生しない。
        # サーバー側でも安全のためエラー。
        # ==================================================

        elif has_start and not has_end:

            raise Exception(
                "終了時間を入力してください"
            )


        # ==================================================
        # 開始・終了あり
        # ==================================================

        else:

            print("==========================================")
            print("時間指定あり")
            print("開始:", start_time)
            print("終了:", end_time)
            print("==========================================")


            mp3_file = cut_mp3(

                mp3_file,

                start_time,

                end_time

            )


        # ==================================================
        # 最終MP3確認
        # ==================================================

        if not os.path.exists(
            mp3_file
        ):

            raise Exception(
                "最終MP3ファイルが存在しません"
            )


        final_size = os.path.getsize(
            mp3_file
        )


        if final_size <= 0:

            raise Exception(
                "最終MP3ファイルが0 bytesです"
            )


        # ==================================================
        # 完成ファイル
        # ==================================================

        files.append(

            os.path.basename(
                mp3_file
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

            "title":
                title,

            "duration":
                duration,

            "start_time":
                start_time or "",

            "end_time":
                end_time or ""

        }


        print("==========================================")
        print("MP3変換完了")
        print("JOB:", job_id)
        print("TITLE:", title)
        print("START:", start_time)
        print("END:", end_time)
        print("MP3:", mp3_file)
        print("SIZE:", final_size)
        print("FILES:", files)
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


            # ==================================================
            # outputs
            # ==================================================

            outputs = data.get(
                "outputs",
                []
            )


            # 今回はMP3だけ
            valid_outputs = []


            if "mp3" in outputs:

                valid_outputs.append(
                    "mp3"
                )


            if not valid_outputs:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3を指定してください"

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


            # ==================================================
            # 空文字をNone化
            # ==================================================

            if start_time is not None:

                start_time = str(
                    start_time
                ).strip()


            if end_time is not None:

                end_time = str(
                    end_time
                ).strip()


            if not start_time:

                start_time = None


            if not end_time:

                end_time = None


            # ==================================================
            # サーバー側時間チェック
            # ==================================================

            if (
                start_time
                and end_time
            ):

                start_seconds = time_to_seconds(
                    start_time
                )

                end_seconds = time_to_seconds(
                    end_time
                )


                if end_seconds <= start_seconds:

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "終了時間は開始時間より後にしてください"

                    }), 400


            # ==================================================
            # 開始だけ入力
            # ==================================================

            if (
                start_time
                and not end_time
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "終了時間を入力してください"

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
                    "queued"

            }


            print("==========================================")
            print("JOB登録")
            print("JOB:", job_id)
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

            }), 500
