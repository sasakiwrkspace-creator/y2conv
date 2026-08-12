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

DOWNLOAD_DIR = "downloads"


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
            "Cookieファイルが空です: "
            + SOURCE_COOKIE_FILE
        )


# ==========================================================
# yt-dlp用一時Cookie作成
#
# Render Secretは読み取り専用のため、
# /tmp にコピーして使用する。
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


        print("==========================================")
        print("yt-dlp用一時Cookie作成")
        print("一時Cookie:", temp_cookie)
        print("==========================================")


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
                "WARNING: "
                "一時Cookie削除失敗:",
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
            "Denoが見つかりません:",
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
                "Deno OK:",
                result.stdout.strip()
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

    temp_cookie = create_temp_cookie_file()

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
        # メモリ節約
        # ----------------------------------------------

        "quiet":
            False,

        "no_warnings":
            False

    }


    # ======================================================
    # Deno
    # ======================================================

    if deno_available:

        ydl_opts["js_runtimes"] = {

            "deno": {

                "path":
                    DENO_PATH

            }

        }


        # --------------------------------------------------
        # EJS
        #
        # yt-dlp-ejsがrequirements.txtにある場合は
        # 基本的にそれを使用可能。
        #
        # GitHub取得も許可して現在のYouTube環境に対応。
        # --------------------------------------------------

        ydl_opts["remote_components"] = {

            "ejs":
                "github"

        }


    print("==========================================")
    print("yt-dlp設定")
    print("Cookie:", temp_cookie)
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
# 時間文字列 → 秒
#
# 対応:
#
# 00:15:30
# 15:30
# 30
#
# UIからは基本的に
#
# HH:MM:SS
#
# を受け取る。
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


    # ------------------------------------------------------
    # 数字だけ
    #
    # 例:
    # 30
    #
    # → 30秒
    # ------------------------------------------------------

    if value.isdigit():

        return int(
            value
        )


    parts = value.split(":")


    try:

        parts = [
            int(part)
            for part in parts
        ]

    except ValueError:

        raise ValueError(
            "時間形式が正しくありません: "
            + value
        )


    if len(parts) == 3:

        hours = parts[0]
        minutes = parts[1]
        seconds = parts[2]


    elif len(parts) == 2:

        hours = 0
        minutes = parts[0]
        seconds = parts[1]


    else:

        raise ValueError(
            "時間形式が正しくありません: "
            + value
        )


    if (
        minutes < 0
        or minutes >= 60
        or seconds < 0
        or seconds >= 60
        or hours < 0
    ):

        raise ValueError(
            "時間の値が正しくありません: "
            + value
        )


    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


# ==========================================================
# 秒 → HH:MM:SS
# ==========================================================

def seconds_to_time(
    seconds
):

    seconds = int(
        seconds
    )


    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    seconds = (
        seconds % 60
    )


    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )


# ==========================================================
# MP3ダウンロード
#
# ここではまだ時間カットしない。
#
# YouTube
#    ↓
# 音声format
#    ↓
# 元MP3
#
# その後、必要ならffmpegでカットする。
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

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temp_cookie = create_temp_cookie_file()


        # --------------------------------------------------
        # 出力ディレクトリ
        # --------------------------------------------------

        os.makedirs(
            output_dir,
            exist_ok=True
        )


        # --------------------------------------------------
        # Deno
        # --------------------------------------------------

        deno_available = check_deno()


        # --------------------------------------------------
        # yt-dlp設定
        #
        # 512MB対策として、
        # format診断用のextract_infoを別途実行しない。
        # ダウンロード1回だけにする。
        # --------------------------------------------------

        ydl_opts = {

            "cookiefile":
                temp_cookie,

            "noplaylist":
                True,

            # ------------------------------------------------
            # 音声のみ
            # ------------------------------------------------

            "format":
                "bestaudio/best",

            # ------------------------------------------------
            # 出力
            #
            # 日本語タイトルでも問題が起きにくいように
            # 通常のyt-dlpテンプレートを使用。
            # ------------------------------------------------

            "outtmpl":
                os.path.join(
                    output_dir,
                    "%(title)s.%(ext)s"
                ),

            # ------------------------------------------------
            # MP3変換
            # ------------------------------------------------

            "postprocessors": [

                {

                    "key":
                        "FFmpegExtractAudio",

                    "preferredcodec":
                        "mp3",

                    "preferredquality":
                        "192"

                }

            ],

            # ------------------------------------------------
            # ログ
            # ------------------------------------------------

            "quiet":
                False,

            "no_warnings":
                False,

            "verbose":
                True

        }


        # ==================================================
        # Deno / EJS
        # ==================================================

        if deno_available:

            ydl_opts["js_runtimes"] = {

                "deno": {

                    "path":
                        DENO_PATH

                }

            }


            ydl_opts["remote_components"] = {

                "ejs":
                    "github"

            }


        print("==========================================")
        print("MP3 yt-dlp設定")
        print("Format: bestaudio/best")
        print("Output:", output_dir)
        print(
            "Deno:",
            DENO_PATH
            if deno_available
            else "None"
        )
        print("==========================================")


        # ==================================================
        # ダウンロード
        # ==================================================

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
                "yt-dlpダウンロード失敗: "
                + str(result)
            )


        # ==================================================
        # MP3検索
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


        # --------------------------------------------------
        # 最新ファイル
        # --------------------------------------------------

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


        print("==========================================")
        print("MP3作成成功")
        print("ファイル:", mp3_file)
        print(
            "サイズ:",
            file_size,
            "bytes"
        )
        print("==========================================")


        return mp3_file


    finally:

        remove_temp_cookie_file(
            temp_cookie
        )


# ==========================================================
# MP3カット
#
# 重要:
#
# カット後のファイルを元ファイル名に置き換える。
#
# これにより、
#
# ダウンロードするMP3
#       =
# Geminiへ送るMP3
#
# になる。
# ==========================================================

def cut_mp3(
    mp3_file,
    start_time=None,
    end_time=None
):

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )


    # ======================================================
    # 時間指定なし
    # ======================================================

    if (
        start_seconds is None
        and end_seconds is None
    ):

        print(
            "MP3カットなし"
        )

        return mp3_file


    # ======================================================
    # 右側だけ入力
    #
    # 00:00:00 ～ end
    # ======================================================

    if (
        start_seconds is None
        and end_seconds is not None
    ):

        start_seconds = 0


    # ======================================================
    # 左側だけ入力
    #
    # start ～ 動画終了
    #
    # ffmpegにはendを指定しない。
    # ======================================================

    # start_secondsはそのまま使用。


    # ======================================================
    # 範囲チェック
    # ======================================================

    if (
        start_seconds is not None
        and end_seconds is not None
        and start_seconds >= end_seconds
    ):

        raise ValueError(
            "開始時間は終了時間より前にしてください"
        )


    print("==========================================")
    print("MP3カット開始")
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
        else "最後まで"
    )
    print("==========================================")


    # ======================================================
    # 一時ファイル
    # ======================================================

    root, ext = os.path.splitext(
        mp3_file
    )


    cut_file = (
        root
        + "_cut"
        + ext
    )


    # ======================================================
    # ffmpeg
    #
    # -ssを入力前に置いて高速シーク
    #
    # -c:a libmp3lame
    # → MP3を再エンコード
    #
    # これにより時間指定が正確になる。
    # ======================================================

    command = [

        "ffmpeg",

        "-y",

        "-ss",
        seconds_to_time(
            start_seconds
            if start_seconds is not None
            else 0
        ),

        "-i",
        mp3_file

    ]


    # ------------------------------------------------------
    # 終了時間あり
    #
    # ffmpegには「長さ」を渡す。
    # ------------------------------------------------------

    if end_seconds is not None:

        duration = (
            end_seconds
            - (
                start_seconds
                if start_seconds is not None
                else 0
            )
        )


        command.extend(
            [
                "-t",
                seconds_to_time(
                    duration
                )
            ]
        )


    command.extend(
        [

            "-vn",

            "-c:a",
            "libmp3lame",

            "-b:a",
            "192k",

            cut_file

        ]
    )


    print(
        "ffmpeg:",
        " ".join(command)
    )


    # ======================================================
    # ffmpeg実行
    #
    # stdoutは捨てる。
    # stderrだけ取得する。
    #
    # メモリ節約。
    # ======================================================

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


    # ======================================================
    # 完成確認
    # ======================================================

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


    # ======================================================
    # 元MP3を削除
    # ======================================================

    if os.path.exists(
        mp3_file
    ):

        os.remove(
            mp3_file
        )


    # ======================================================
    # カット後MP3を元の名前に戻す
    # ======================================================

    os.rename(
        cut_file,
        mp3_file
    )


    print("==========================================")
    print("MP3カット完了")
    print("ファイル:", mp3_file)
    print(
        "サイズ:",
        cut_size,
        "bytes"
    )
    print("==========================================")


    return mp3_file


# ==========================================================
# MP4
#
# 今回の新しいMP3 → Gemini構成では基本的に使用しない。
#
# 既存UIでMP4を残したい場合に備えて残している。
# ==========================================================

def download_mp4(
    url,
    output_dir
):

    print("==========================================")
    print("MP4ダウンロード開始")
    print("==========================================")


    ydl_opts = None
    temp_cookie = None


    try:

        ydl_opts, temp_cookie = (
            get_ydl_base_options()
        )


        ydl_opts.update({

            "format":
                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",

            "merge_output_format":
                "mp4",

            "outtmpl":
                os.path.join(
                    output_dir,
                    "%(title)s.%(ext)s"
                )

        })


        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )


            if not info:

                raise Exception(
                    "YouTube情報を取得できませんでした"
                )


            filename = ydl.prepare_filename(
                info
            )


        mp4_file = (
            os.path.splitext(
                filename
            )[0]
            + ".mp4"
        )


        if not os.path.exists(
            mp4_file
        ):

            raise Exception(
                "MP4ファイルが作成されませんでした: "
                + mp4_file
            )


        file_size = os.path.getsize(
            mp4_file
        )


        print(
            "MP4完成:",
            mp4_file
        )


        print(
            "MP4サイズ:",
            file_size,
            "bytes"
        )


        return mp4_file


    finally:

        remove_temp_cookie_file(
            temp_cookie
        )


# ==========================================================
# MP4カット
# ==========================================================

def cut_mp4(
    mp4_file,
    start_time,
    end_time
):

    print("==========================================")
    print("MP4時間指定カット開始")
    print(
        "開始:",
        start_time
    )
    print(
        "終了:",
        end_time
    )
    print("==========================================")


    cut_file = (
        os.path.splitext(
            mp4_file
        )[0]
        + "_cut.mp4"
    )


    command = [

        "ffmpeg",

        "-y",

        "-ss",
        start_time,

        "-i",
        mp4_file,

        "-to",
        end_time,

        "-c",
        "copy",

        cut_file

    ]


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
            "ffmpeg処理失敗(mp4)"
        )


    if not os.path.exists(
        cut_file
    ):

        raise Exception(
            "カット後MP4が作成されませんでした"
        )


    if os.path.exists(
        mp4_file
    ):

        os.remove(
            mp4_file
        )


    os.rename(
        cut_file,
        mp4_file
    )


# ==========================================================
# 変換処理
#
# 新しい設計:
#
# /convert
#    ↓
# YouTube
#    ↓
# MP3
#    ↓
# 時間指定があればffmpeg
#    ↓
# 完成MP3
#    ↓
# ブラウザへ返す
#
# Geminiはここでは実行しない。
#
# Geminiは後から /gemini-transcribe
# で実行する。
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
        #
        # Gemini用のMP3まで消さないように、
        # cleanup.pyの設定には注意。
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


        print(
            "出力ディレクトリ:",
            output_dir
        )


        files = []


        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in outputs:

            # ------------------------------------------------
            # 1. YouTube → MP3
            # ------------------------------------------------

            mp3_file = download_mp3(
                url,
                output_dir
            )


            # ------------------------------------------------
            # 2. 時間指定
            #
            # 空ならカットしない。
            # ------------------------------------------------

            if (
                start_time
                or end_time
            ):

                mp3_file = cut_mp3(

                    mp3_file,

                    start_time,

                    end_time

                )


            # ------------------------------------------------
            # 3. 完成MP3
            #
            # このファイルが
            #
            # ・ユーザーのダウンロード
            # ・Geminiへの入力
            #
            # の両方になる。
            # ------------------------------------------------

            files.append(
                os.path.basename(
                    mp3_file
                )
            )


        # ==================================================
        # MP4
        #
        # 新画面では基本的に使わない。
        # ==================================================

        if "mp4" in outputs:

            mp4_file = download_mp4(
                url,
                output_dir
            )


            if (
                start_time
                or end_time
            ):

                # ------------------------------------------------
                # MP4については
                # 左だけ/右だけの詳細処理は
                # 今回のMP3中心設計では不要。
                # 両方指定された場合のみカット。
                # ------------------------------------------------

                if (
                    start_time
                    and end_time
                ):

                    cut_mp4(

                        mp4_file,

                        start_time,

                        end_time

                    )


            files.append(
                os.path.basename(
                    mp4_file
                )
            )


        # ==================================================
        # 出力確認
        # ==================================================

        if not files:

            raise Exception(
                "作成されたファイルがありません"
            )


        # ==================================================
        # 完了
        # ==================================================

        jobs[job_id] = {

            "status":
                "complete",

            "files":
                files

        }


        print("==========================================")
        print("変換完了")
        print("JOB:", job_id)
        print("FILES:", files)
        print("==========================================")


    # ======================================================
    # エラー
    # ======================================================

    except Exception as e:

        print("==========================================")
        print("変換エラー")
        print("JOB:", job_id)
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


            url = str(
                url
            ).strip()


            # ==================================================
            # outputs
            #
            # 新画面では基本的にmp3。
            # 既存UIとの互換性のためmp4も許可。
            # ==================================================

            outputs = data.get(
                "outputs",
                ["mp3"]
            )


            if not isinstance(
                outputs,
                list
            ):

                outputs = [
                    "mp3"
                ]


            valid_outputs = []


            for output in outputs:

                if output in [
                    "mp3",
                    "mp4"
                ]:

                    if output not in valid_outputs:

                        valid_outputs.append(
                            output
                        )


            # ==================================================
            # outputsが空ならMP3
            #
            # 新UIではoutputsを送らなくても
            # MP3を作成できる。
            # ==================================================

            if not valid_outputs:

                valid_outputs = [
                    "mp3"
                ]


            # ==================================================
            # 時間
            # ==================================================

            start_time = data.get(
                "start_time"
            )


            end_time = data.get(
                "end_time"
            )


            # --------------------------------------------------
            # 空文字をNoneにする
            # --------------------------------------------------

            if start_time is not None:

                start_time = str(
                    start_time
                ).strip()


                if not start_time:

                    start_time = None


            if end_time is not None:

                end_time = str(
                    end_time
                ).strip()


                if not end_time:

                    end_time = None


            # ==================================================
            # 時間形式チェック
            # ==================================================

            try:

                start_seconds = time_to_seconds(
                    start_time
                )


                end_seconds = time_to_seconds(
                    end_time
                )


                # ------------------------------------------------
                # 右側だけ
                # ------------------------------------------------

                if (
                    start_seconds is None
                    and end_seconds is not None
                ):

                    pass


                # ------------------------------------------------
                # 両方
                # ------------------------------------------------

                elif (
                    start_seconds is not None
                    and end_seconds is not None
                ):

                    if start_seconds >= end_seconds:

                        return jsonify({

                            "success":
                                False,

                            "message":
                                "開始時間は終了時間より前にしてください"

                        }), 400


            except ValueError as e:

                return jsonify({

                    "success":
                        False,

                    "message":
                        str(e)

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
