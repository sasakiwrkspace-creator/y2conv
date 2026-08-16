from flask import request, jsonify

import yt_dlp
from yt_dlp.utils import download_range_func

import uuid
import threading
import os
import shutil
import tempfile

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
            and os.path.exists(
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
        and os.path.exists(
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
                + minutes * 60
                + seconds
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
# yt-dlp設定
#
# 時間範囲指定がある場合は
# yt-dlpのdownload_rangesを使用する。
# ==========================================================

def get_ydl_options(
    temp_cookie,
    output_template,
    start_time=None,
    end_time=None
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
        # プログレス表示を抑制
        # --------------------------------------------------

        "noprogress":
            True

    }


    # ======================================================
    # 時間範囲指定
    # ======================================================

    if (
        start_time is not None
        and end_time is not None
    ):

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


        print("==========================================")
        print("yt-dlp時間範囲指定")
        print("開始:", start_time)
        print("終了:", end_time)
        print("開始秒:", start_seconds)
        print("終了秒:", end_seconds)
        print("==========================================")


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


        # --------------------------------------------------
        # 時間範囲ダウンロード時の精度向上
        # --------------------------------------------------

        options["force_keyframes_at_cuts"] = True


        # --------------------------------------------------
        # HLS等での範囲取得を安定させるため
        # HTTPSを優先
        # --------------------------------------------------

        options["format_sort"] = [
            "proto:https"
        ]


    else:

        print("==========================================")
        print("yt-dlp時間範囲指定なし")
        print("動画全体を取得")
        print("==========================================")


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
# 時間指定なし
#   YouTube
#       ↓
#   音声全体
#       ↓
#   MP3
#
# 時間指定あり
#   YouTube
#       ↓
#   yt-dlpで指定範囲
#       ↓
#   MP3
#
# ※後からcut_mp3()でカットする方式ではない。
# ==========================================================

def download_mp3(
    url,
    output_dir,
    start_time=None,
    end_time=None
):

    print("==========================================")
    print("MP3作成開始")
    print("URL:", url)
    print("出力:", output_dir)
    print("開始時間:", start_time)
    print("終了時間:", end_time)
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
        # ==================================================

        output_template = os.path.join(

            output_dir,

            "%(title)s.%(ext)s"

        )


        # ==================================================
        # yt-dlp設定
        # ==================================================

        ydl_opts = get_ydl_options(

            temp_cookie,

            output_template,

            start_time,

            end_time

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


        if (
            start_time is not None
            and end_time is not None
        ):

            print(
                "download_ranges: ON"
            )

            print(
                "range:",
                start_time,
                "->",
                end_time
            )

        else:

            print(
                "download_ranges: OFF"
            )


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
        # 作成されたMP3を探す
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


        # ==================================================
        # ファイルサイズ
        # ==================================================

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
        print("開始時間:", start_time)
        print("終了時間:", end_time)
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
        #
        # 時間指定があれば
        # yt-dlp側で直接範囲指定する。
        # ==================================================

        result = download_mp3(

            url,

            output_dir,

            start_time,

            end_time

        )


        mp3_file = result["file"]

        title = result["title"]

        duration = result["duration"]


        # ==================================================
        # 時間指定のログ
        # ==================================================

        if (
            start_time is not None
            and end_time is not None
        ):

            print("==========================================")
            print("時間範囲MP3作成")
            print("yt-dlp側で範囲指定済み")
            print("開始:", start_time)
            print("終了:", end_time)
            print("==========================================")


        else:

            print("==========================================")
            print("時間指定なし")
            print("MP3全体を使用")
            print("==========================================")


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
            # 時間形式チェック
            # ==================================================

            if start_time:

                try:

                    start_seconds = time_to_seconds(
                        start_time
                    )

                    if start_seconds < 0:

                        raise ValueError

                except Exception:

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "開始時間の形式が正しくありません"

                    }), 400


            if end_time:

                try:

                    end_seconds = time_to_seconds(
                        end_time
                    )

                    if end_seconds < 0:

                        raise ValueError

                except Exception:

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "終了時間の形式が正しくありません"

                    }), 400


            # ==================================================
            # 終了時間だけ指定
            #
            # 00:00:00から開始
            # ==================================================

            if (
                not start_time
                and end_time
            ):

                start_time = "00:00:00"


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
            # 時間チェック
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
