from flask import request, jsonify

import yt_dlp
import uuid
import threading
import os
import shutil
import tempfile
import subprocess

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
# yt-dlp設定
#
# 重要:
#
# 時間指定はここでは行わない。
#
# YouTubeから音声を取得した後、
# FFmpegで開始～終了を正確に切り出す。
#
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
        # 音声
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
# 時間指定なし:
#
# YouTube
#   ↓
# yt-dlp
#   ↓
# 音声
#   ↓
# FFmpeg
#   ↓
# FULL MP3
#
#
# 時間指定あり:
#
# YouTube
#   ↓
# yt-dlp
#   ↓
# 音声
#   ↓
# FFmpeg
#   ↓
# 開始～終了だけ
#   ↓
# MP3
#
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
    print("開始:", start_time)
    print("終了:", end_time)
    print("==========================================")


    temp_cookie = None

    temp_audio_dir = None


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
        # 時間を秒へ変換
        # ==================================================

        start_seconds = None

        end_seconds = None


        if start_time:

            start_seconds = time_to_seconds(
                start_time
            )


        if end_time:

            end_seconds = time_to_seconds(
                end_time
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

                raise Exception(
                    "終了時間は開始時間より後にしてください"
                )


        # ==================================================
        # 開始だけ指定は禁止
        # ==================================================

        if (
            start_seconds is not None
            and
            end_seconds is None
        ):

            raise Exception(
                "終了時間を入力してください"
            )


        # ==================================================
        # 一時音声ディレクトリ
        #
        # 最終MP3とは別の場所に作る。
        # ==================================================

        temp_audio_dir = tempfile.mkdtemp(

            prefix="y2conv_audio_",

            dir="/tmp"

        )


        # ==================================================
        # yt-dlp一時出力
        #
        # 日本語タイトルの影響を避けるため、
        # IDベースの英数字ファイル名にする。
        # ==================================================

        temp_output_template = os.path.join(

            temp_audio_dir,

            "%(id)s.%(ext)s"

        )


        # ==================================================
        # yt-dlp設定
        #
        # ここでは時間範囲を指定しない。
        # ==================================================

        ydl_opts = get_ydl_options(

            temp_cookie,

            temp_output_template

        )


        print("==========================================")
        print("YouTube音声取得開始")
        print("時間範囲: FULL取得")
        print("==========================================")


        # ==================================================
        # yt-dlp
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


        # ==================================================
        # 情報確認
        # ==================================================

        if not info:

            raise Exception(
                "YouTube情報を取得できませんでした"
            )


        # ==================================================
        # 元動画の再生時間
        # ==================================================

        full_duration = info.get(
            "duration"
        )


        # ==================================================
        # タイトル
        # ==================================================

        title = info.get(

            "title",

            ""

        )


        if not title:

            title = "audio"


        # ==================================================
        # yt-dlpが作成した音声を探す
        # ==================================================

        audio_files = []


        for filename in os.listdir(

            temp_audio_dir

        ):

            full_path = os.path.join(

                temp_audio_dir,

                filename

            )


            if os.path.isfile(
                full_path
            ):

                audio_files.append(
                    full_path
                )


        # ==================================================
        # 音声ファイル確認
        # ==================================================

        if not audio_files:

            raise Exception(
                "YouTube音声ファイルが作成されませんでした"
            )


        # ==================================================
        # 最新の音声ファイル
        # ==================================================

        source_audio = max(

            audio_files,

            key=os.path.getmtime

        )


        print(
            "取得音声:",
            source_audio
        )


        # ==================================================
        # 最終MP3ファイル
        #
        # 日本語タイトルもそのまま使用する。
        # ==================================================

        output_mp3 = os.path.join(

            output_dir,

            title + ".mp3"

        )


        # ==================================================
        # 同名ファイル削除
        # ==================================================

        if os.path.exists(
            output_mp3
        ):

            try:

                os.remove(
                    output_mp3
                )

            except Exception as e:

                raise Exception(

                    "既存MP3を削除できませんでした: "

                    + str(e)

                )


        # ==================================================
        # 時間指定あり
        # ==================================================

        if (
            start_seconds is not None
            and
            end_seconds is not None
        ):

            clip_duration = (

                end_seconds
                -
                start_seconds

            )


            print("==========================================")
            print("FFmpeg時間切り出し")
            print("開始秒:", start_seconds)
            print("終了秒:", end_seconds)
            print("切り出し時間:", clip_duration)
            print("==========================================")


            # ==================================================
            # FFmpeg
            #
            # -ss = 開始位置
            # -t  = 切り出す長さ
            #
            # 例:
            #
            # 60秒 ～ 109秒
            #
            # -ss 60
            # -t 49
            #
            # → 49秒
            # ==================================================

            command = [

                "ffmpeg",

                "-y",

                "-ss",
                str(start_seconds),

                "-i",
                source_audio,

                "-t",
                str(clip_duration),

                "-vn",

                "-codec:a",
                "libmp3lame",

                "-b:a",
                "128k",

                output_mp3

            ]


            print(
                "FFmpeg command:",
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
                    "FFmpeg ERROR:"
                )

                print(
                    result.stderr
                )


                raise Exception(
                    "FFmpegによる時間切り出しに失敗しました"
                )


        # ==================================================
        # 時間指定なし
        # ==================================================

        else:

            clip_duration = full_duration


            print("==========================================")
            print("FULL MP3作成")
            print("==========================================")


            # ==================================================
            # FFmpeg
            # ==================================================

            command = [

                "ffmpeg",

                "-y",

                "-i",
                source_audio,

                "-vn",

                "-codec:a",
                "libmp3lame",

                "-b:a",
                "128k",

                output_mp3

            ]


            print(
                "FFmpeg command:",
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
                    "FFmpeg ERROR:"
                )

                print(
                    result.stderr
                )


                raise Exception(
                    "MP3変換に失敗しました"
                )


        # ==================================================
        # 完成MP3確認
        # ==================================================

        if not os.path.exists(
            output_mp3
        ):

            raise Exception(
                "MP3ファイルが作成されませんでした"
            )


        file_size = os.path.getsize(
            output_mp3
        )


        if file_size <= 0:

            raise Exception(
                "MP3ファイルが0 bytesです"
            )


        # ==================================================
        # 結果表示
        # ==================================================

        print("==========================================")
        print("MP3作成成功")
        print("タイトル:", title)
        print("切り出し後再生時間:", clip_duration)
        print("Full再生時間:", full_duration)
        print("MP3:", output_mp3)
        print("サイズ:", file_size, "bytes")
        print("==========================================")


        return {

            "file":
                output_mp3,

            "title":
                title,

            # ----------------------------------------------
            # 実際に作成したMP3の長さ
            # ----------------------------------------------

            "duration":
                clip_duration,

            # ----------------------------------------------
            # 元YouTube動画の長さ
            # ----------------------------------------------

            "full_duration":
                full_duration

        }


    finally:

        # ==================================================
        # 一時Cookie削除
        # ==================================================

        remove_temp_cookie_file(

            temp_cookie

        )


        # ==================================================
        # 一時音声ディレクトリ削除
        # ==================================================

        if (
            temp_audio_dir
            and
            os.path.exists(
                temp_audio_dir
            )
        ):

            try:

                shutil.rmtree(

                    temp_audio_dir

                )


                print(
                    "一時音声ディレクトリ削除:",
                    temp_audio_dir
                )


            except Exception as e:

                print(
                    "WARNING: "
                    "一時音声ディレクトリ削除失敗:",
                    repr(e)
                )


# ==========================================================
# 時間を秒へ変換
#
# 対応:
#
# 59
# 1:30
# 00:01:30
#
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

        # ==================================================
        # 秒
        # ==================================================

        if len(parts) == 1:

            seconds = float(
                parts[0]
            )


            if seconds < 0:

                raise ValueError


            return seconds


        # ==================================================
        # 分:秒
        # ==================================================

        if len(parts) == 2:

            minutes = float(
                parts[0]
            )

            seconds = float(
                parts[1]
            )


            if (
                minutes < 0
                or
                seconds < 0
                or
                seconds >= 60
            ):

                raise ValueError


            return (

                minutes * 60
                +
                seconds

            )


        # ==================================================
        # 時:分:秒
        # ==================================================

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
                or
                minutes < 0
                or
                seconds < 0
                or
                minutes >= 60
                or
                seconds >= 60
            ):

                raise ValueError


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
            +
            value

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
        # MP3確認
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

            output_dir,

            start_time,

            end_time

        )


        mp3_file = result["file"]

        title = result["title"]

        duration = result["duration"]

        full_duration = result["full_duration"]


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


            # ------------------------------------------------
            # 実際に作成したMP3の再生時間
            # ------------------------------------------------

            "duration":
                duration,


            # ------------------------------------------------
            # 元YouTube動画の再生時間
            # ------------------------------------------------

            "full_duration":
                full_duration,


            # ------------------------------------------------
            # 指定時間
            # ------------------------------------------------

            "start_time":
                start_time or "",


            "end_time":
                end_time or ""

        }


        print("==========================================")
        print("MP3変換完了")
        print("JOB:", job_id)
        print("TITLE:", title)
        print("DURATION:", duration)
        print("FULL DURATION:", full_duration)
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
            # 時間を秒へ変換
            # ==================================================

            start_seconds = None

            end_seconds = None


            if start_time:

                try:

                    start_seconds = time_to_seconds(
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

                    end_seconds = time_to_seconds(
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
            # 開始だけ
            # ==================================================

            if (
                start_seconds is not None
                and
                end_seconds is None
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "終了時間を入力してください"

                }), 400


            # ==================================================
            # 終了だけ
            #
            # 例:
            #
            # 開始:
            # 空欄
            #
            # 終了:
            # 01:00
            #
            # ↓
            #
            # 00:00 ～ 01:00
            # ==================================================

            if (
                start_seconds is None
                and
                end_seconds is not None
            ):

                start_time = "00:00:00"

                start_seconds = 0


            # ==================================================
            # 開始・終了チェック
            # ==================================================

            if (
                start_seconds is not None
                and
                end_seconds is not None
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
