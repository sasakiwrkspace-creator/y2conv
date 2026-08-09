```python
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
# Cookieファイル
# ==========================================================

RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ==========================================================
# プロジェクトルート
#
# convert.py
#     ↓
# routes/
#     ↓
# プロジェクトルート
#
# app.py と同じ階層
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================================
# ローカルCookie
#
# app.py と同じ階層の cookies.txt
# ==========================================================

LOCAL_COOKIE_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt"
)


# ==========================================================
# Render判定
#
# Render側のEnvironment Variablesに
#
# RENDER=true
#
# を設定する
# ==========================================================

IS_RENDER = (
    os.environ.get(
        "RENDER",
        ""
    ).lower()
    == "true"
)


# ==========================================================
# 使用する元Cookieファイル
# ==========================================================

if IS_RENDER:

    ORIGINAL_COOKIE_FILE = RENDER_COOKIE_FILE

else:

    ORIGINAL_COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("Cookie環境:")
print(
    "Render"
    if IS_RENDER
    else "Local"
)
print("元Cookieファイル:")
print(ORIGINAL_COOKIE_FILE)
print(
    "Cookie存在:",
    os.path.exists(
        ORIGINAL_COOKIE_FILE
    )
)
print("==========================================")


# ==========================================================
# yt-dlp用Cookieファイル作成
#
# /etc/secrets は読み取り専用の場合があるため、
# 各処理ごとに /tmp へコピーする
#
# 固定ファイル名は使わない
# → 複数ジョブ同時実行時の競合を防止
# ==========================================================

def prepare_cookie_file():

    # ------------------------------------------------------
    # 元Cookieファイル存在確認
    # ------------------------------------------------------

    if not os.path.exists(
        ORIGINAL_COOKIE_FILE
    ):

        raise Exception(
            "Cookieファイルが見つかりません: "
            f"{ORIGINAL_COOKIE_FILE}"
        )


    # ------------------------------------------------------
    # 元Cookieファイルサイズ
    # ------------------------------------------------------

    original_size = os.path.getsize(
        ORIGINAL_COOKIE_FILE
    )


    print(
        "元Cookieファイルサイズ:",
        original_size,
        "bytes"
    )


    if original_size <= 0:

        raise Exception(
            "Cookieファイルが空です: "
            f"{ORIGINAL_COOKIE_FILE}"
        )


    # ------------------------------------------------------
    # 一時ファイル作成
    #
    # 固定名ではなくランダムなファイル名を使用
    # ------------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(

        mode="wb",

        prefix="y2conv_cookies_",

        suffix=".txt",

        dir="/tmp",

        delete=False

    )


    temp_cookie_file = temp_file.name

    temp_file.close()


    try:

        # --------------------------------------------------
        # Cookieコピー
        # --------------------------------------------------

        shutil.copyfile(

            ORIGINAL_COOKIE_FILE,

            temp_cookie_file

        )


        # --------------------------------------------------
        # コピー確認
        # --------------------------------------------------

        if not os.path.exists(
            temp_cookie_file
        ):

            raise Exception(
                "yt-dlp用Cookieファイルの作成に失敗しました"
            )


        file_size = os.path.getsize(
            temp_cookie_file
        )


        print(
            "Cookieファイル準備OK:",
            temp_cookie_file
        )

        print(
            "Cookieファイルサイズ:",
            file_size,
            "bytes"
        )


        if file_size <= 0:

            raise Exception(
                "コピーしたCookieファイルが空です"
            )


        # --------------------------------------------------
        # Cookie数確認
        #
        # Cookieの内容そのものはログに出さない
        # --------------------------------------------------

        cookie_count = 0

        youtube_cookie_count = 0


        with open(

            temp_cookie_file,

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


                fields = line.split(
                    "\t"
                )


                # Netscape形式Cookie
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


        print(
            "Cookieデータ行数:",
            cookie_count
        )

        print(
            "YouTube/Google Cookie数:",
            youtube_cookie_count
        )


        if cookie_count == 0:

            raise Exception(
                "Cookieデータが0件です"
            )


        if youtube_cookie_count == 0:

            print(
                "WARNING: "
                "YouTube/Google Cookieが見つかりません"
            )


        return temp_cookie_file


    except Exception:

        # 作成途中でエラーになった場合は削除

        try:

            if os.path.exists(
                temp_cookie_file
            ):

                os.remove(
                    temp_cookie_file
                )

        except Exception:

            pass


        raise


# ==========================================================
# 一時Cookie削除
# ==========================================================

def remove_cookie_file(
    cookie_file
):

    if not cookie_file:

        return


    try:

        if os.path.exists(
            cookie_file
        ):

            os.remove(
                cookie_file
            )

            print(
                "一時Cookieファイル削除OK:",
                cookie_file
            )

    except Exception as e:

        print(
            "一時Cookieファイル削除失敗:",
            repr(e)
        )


# ==========================================================
# yt-dlp共通設定
#
# Cookieファイルを受け取って使用する
# ==========================================================

def get_ydl_base_options(
    cookie_file
):

    options = {

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        "cookiefile":
            cookie_file,


        # --------------------------------------------------
        # Playlist無効
        # --------------------------------------------------

        "noplaylist":
            True,


        # --------------------------------------------------
        # JavaScript Runtime
        #
        # yt-dlpが対応している場合に使用
        # --------------------------------------------------

        "js_runtimes": {
            "deno": {}
        },


        # --------------------------------------------------
        # EJS challenge solver
        # --------------------------------------------------

        "remote_components": {
            "ejs": "github"
        },


        # --------------------------------------------------
        # エラーをExceptionとして取得
        # --------------------------------------------------

        "ignoreerrors":
            False,


        # --------------------------------------------------
        # ログ
        # --------------------------------------------------

        "quiet":
            False,

        "no_warnings":
            False

    }


    return options


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

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=10

        )


        if result.returncode != 0:

            raise Exception(
                "FFmpegが正常に実行できません"
            )


        first_line = (
            result.stdout
            .splitlines()[0]
            if result.stdout
            else ""
        )


        print(
            "FFmpeg確認OK:",
            first_line
        )


    except FileNotFoundError:

        raise Exception(
            "FFmpegがインストールされていません"
        )


    except Exception as e:

        raise Exception(
            "FFmpeg確認失敗: "
            f"{e}"
        )


# ==========================================================
# YouTube情報・format診断
#
# 診断だけを行う。
#
# ここで失敗しても、
# 実際のMP3/MP4変換処理は続行可能。
# ==========================================================

def diagnose_formats(
    url,
    cookie_file
):

    print(
        "=========================================="
    )

    print(
        "YouTube情報取得開始"
    )

    print(
        "URL:",
        url
    )

    print(
        "=========================================="
    )


    ydl_opts = get_ydl_base_options(
        cookie_file
    )


    ydl_opts.update({

        # --------------------------------------------------
        # ダウンロードしない
        # --------------------------------------------------

        "skip_download":
            True,


        # --------------------------------------------------
        # formatを固定しない
        # --------------------------------------------------

        "format":
            None,


        # --------------------------------------------------
        # 詳細ログ
        # --------------------------------------------------

        "quiet":
            False,

        "no_warnings":
            False,

        "verbose":
            True

    })


    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        print(
            "extract_info開始"
        )


        info = ydl.extract_info(

            url,

            download=False

        )


    if not info:

        raise Exception(
            "YouTube情報を取得できませんでした"
        )


    # ======================================================
    # 基本情報
    # ======================================================

    title = info.get(
        "title"
    )


    duration = info.get(
        "duration"
    )


    print(
        "=========================================="
    )

    print(
        "動画タイトル:",
        title
    )

    print(
        "再生時間:",
        duration,
        "秒"
    )

    print(
        "=========================================="
    )


    # ======================================================
    # Format一覧
    # ======================================================

    formats = info.get(
        "formats",
        []
    )


    print(
        "利用可能format数:",
        len(formats)
    )


    print(
        "=========================================="
    )

    print(
        "音声format一覧"
    )

    print(
        "=========================================="
    )


    audio_formats = []


    for f in formats:

        acodec = f.get(
            "acodec"
        )


        vcodec = f.get(
            "vcodec"
        )


        if (
            acodec
            and acodec != "none"
            and (
                not vcodec
                or vcodec == "none"
            )
        ):

            audio_formats.append(
                f
            )


            print(

                "AUDIO",

                "ID=",
                f.get("format_id"),

                "EXT=",
                f.get("ext"),

                "ACODEC=",
                f.get("acodec"),

                "ABR=",
                f.get("abr"),

                "ASR=",
                f.get("asr")

            )


    print(
        "=========================================="
    )

    print(
        "音声format数:",
        len(audio_formats)
    )

    print(
        "=========================================="
    )


    return info


# ==========================================================
# MP3変換
# ==========================================================

def download_mp3(
    url,
    output_dir
):

    cookie_file = None


    try:

        print(
            "=========================================="
        )

        print(
            "MP3ダウンロード開始"
        )

        print(
            "=========================================="
        )


        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        cookie_file = prepare_cookie_file()


        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

        ydl_opts = get_ydl_base_options(
            cookie_file
        )


        ydl_opts.update({

            # --------------------------------------------------
            # MP3用format
            #
            # 140固定をやめる。
            #
            # 140がRender側で取得できない場合でも、
            # 利用可能な音声formatを選択する。
            # --------------------------------------------------

            "format":
                "bestaudio/best",


            # --------------------------------------------------
            # 出力
            # --------------------------------------------------

            "outtmpl":
                os.path.join(
                    output_dir,
                    "%(title)s.%(ext)s"
                ),


            # --------------------------------------------------
            # FFmpegでMP3へ変換
            # --------------------------------------------------

            "postprocessors": [

                {

                    "key":
                        "FFmpegExtractAudio",

                    "preferredcodec":
                        "mp3",

                    "preferredquality":
                        "192"

                }

            ]

        })


        print(
            "MP3 format:",
            "bestaudio/best"
        )

        print(
            "MP3品質:",
            "192kbps"
        )


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


        # ==================================================
        # MP3ファイル
        # ==================================================

        mp3_file = (
            os.path.splitext(
                filename
            )[0]
            + ".mp3"
        )


        if not os.path.exists(
            mp3_file
        ):

            raise Exception(
                "MP3ファイルが作成されませんでした: "
                f"{mp3_file}"
            )


        file_size = os.path.getsize(
            mp3_file
        )


        print(
            "MP3完成:",
            mp3_file
        )


        print(
            "MP3サイズ:",
            file_size,
            "bytes"
        )


        return mp3_file


    finally:

        # --------------------------------------------------
        # 一時Cookie削除
        # --------------------------------------------------

        remove_cookie_file(
            cookie_file
        )


# ==========================================================
# MP4変換
# ==========================================================

def download_mp4(
    url,
    output_dir
):

    cookie_file = None


    try:

        print(
            "=========================================="
        )

        print(
            "MP4ダウンロード開始"
        )

        print(
            "=========================================="
        )


        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        cookie_file = prepare_cookie_file()


        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

        ydl_opts = get_ydl_base_options(
            cookie_file
        )


        ydl_opts.update({

            # --------------------------------------------------
            # MP4動画 + M4A音声
            #
            # MP4/M4Aが存在すれば優先。
            # なければ利用可能なvideo+audioへフォールバック。
            # --------------------------------------------------

            "format":
                "bv*[ext=mp4]+ba[ext=m4a]/"
                "bv*[ext=mp4]+ba/"
                "bv*+ba/"
                "b[ext=mp4]/"
                "best",


            # --------------------------------------------------
            # MP4として結合
            # --------------------------------------------------

            "merge_output_format":
                "mp4",


            # --------------------------------------------------
            # 出力
            # --------------------------------------------------

            "outtmpl":
                os.path.join(
                    output_dir,
                    "%(title)s.%(ext)s"
                )

        })


        print(
            "MP4 format:",
            "bv*[ext=mp4]+ba[ext=m4a]/"
            "bv*[ext=mp4]+ba/"
            "bv*+ba/"
            "b[ext=mp4]/"
            "best"
        )


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


        # ==================================================
        # MP4ファイル
        # ==================================================

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
                f"{mp4_file}"
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

        # --------------------------------------------------
        # 一時Cookie削除
        # --------------------------------------------------

        remove_cookie_file(
            cookie_file
        )


# ==========================================================
# MP3カット
# ==========================================================

def cut_mp3(
    mp3_file,
    start_time,
    end_time
):

    print(
        "=========================================="
    )

    print(
        "MP3時間指定カット開始"
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
        "=========================================="
    )


    cut_file = (
        os.path.splitext(
            mp3_file
        )[0]
        + "_cut.mp3"
    )


    result = subprocess.run(

        [

            "ffmpeg",

            "-y",

            "-i",
            mp3_file,

            "-ss",
            start_time,

            "-to",
            end_time,

            "-c",
            "copy",

            cut_file

        ],

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )


    if result.returncode != 0:

        print(
            result.stderr
        )

        raise Exception(
            "ffmpeg処理失敗(mp3)"
        )


    if not os.path.exists(
        cut_file
    ):

        raise Exception(
            "カット後のMP3ファイルが作成されませんでした"
        )


    if os.path.exists(
        mp3_file
    ):

        os.remove(
            mp3_file
        )


    os.rename(
        cut_file,
        mp3_file
    )


    print(
        "MP3時間指定カット完了"
    )


# ==========================================================
# MP4カット
# ==========================================================

def cut_mp4(
    mp4_file,
    start_time,
    end_time
):

    print(
        "=========================================="
    )

    print(
        "MP4時間指定カット開始"
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
        "=========================================="
    )


    cut_file = (
        os.path.splitext(
            mp4_file
        )[0]
        + "_cut.mp4"
    )


    result = subprocess.run(

        [

            "ffmpeg",

            "-y",

            "-i",
            mp4_file,

            "-ss",
            start_time,

            "-to",
            end_time,

            "-c",
            "copy",

            cut_file

        ],

        stdout=subprocess.PIPE,

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
            "カット後のMP4ファイルが作成されませんでした"
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


    print(
        "MP4時間指定カット完了"
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

        # ==================================================
        # Job running
        # ==================================================

        jobs[job_id] = {

            "status":
                "running"

        }


        print(
            "=========================================="
        )

        print(
            "変換開始:",
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
            "START:",
            start_time
        )

        print(
            "END:",
            end_time
        )

        print(
            "=========================================="
        )


        # ==================================================
        # Cookie確認
        # ==================================================

        if not os.path.exists(
            ORIGINAL_COOKIE_FILE
        ):

            raise Exception(
                "元Cookieファイルが見つかりません: "
                f"{ORIGINAL_COOKIE_FILE}"
            )


        print(
            "Cookie環境:",
            "Render"
            if IS_RENDER
            else "Local"
        )

        print(
            "Cookieファイル:",
            ORIGINAL_COOKIE_FILE
        )

        print(
            "Cookieサイズ:",
            os.path.getsize(
                ORIGINAL_COOKIE_FILE
            ),
            "bytes"
        )


        # ==================================================
        # FFmpeg確認
        # ==================================================

        check_ffmpeg()


        # ==================================================
        # 古いファイル削除
        # ==================================================

        cleanup_downloads()


        # ==================================================
        # 出力ディレクトリ
        # ==================================================

        output_dir = "downloads"


        os.makedirs(

            output_dir,

            exist_ok=True

        )


        files = []


        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in outputs:

            # ------------------------------------------------
            # format診断
            #
            # 診断失敗しても変換は継続
            # ------------------------------------------------

            diagnostic_cookie = None


            try:

                diagnostic_cookie = (
                    prepare_cookie_file()
                )


                diagnose_formats(

                    url,

                    diagnostic_cookie

                )


            except Exception as e:

                print(
                    "format診断失敗:",
                    repr(e)
                )


            finally:

                remove_cookie_file(
                    diagnostic_cookie
                )


            # ------------------------------------------------
            # MP3取得
            # ------------------------------------------------

            mp3_file = download_mp3(

                url,

                output_dir

            )


            # ------------------------------------------------
            # 時間指定
            # ------------------------------------------------

            if (
                start_time
                and end_time
                and start_time < end_time
            ):

                cut_mp3(

                    mp3_file,

                    start_time,

                    end_time

                )


            files.append(
                os.path.basename(
                    mp3_file
                )
            )


        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in outputs:

            mp4_file = download_mp4(

                url,

                output_dir

            )


            # ------------------------------------------------
            # 時間指定
            # ------------------------------------------------

            if (
                start_time
                and end_time
                and start_time < end_time
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
        # 完了
        # ==================================================

        jobs[job_id] = {

            "status":
                "complete",

            "files":
                files

        }


        print(
            "=========================================="
        )

        print(
            "変換完了"
        )

        print(
            "JOB:",
            job_id
        )

        print(
            "FILES:",
            files
        )

        print(
            "=========================================="
        )


    # ======================================================
    # エラー
    # ======================================================

    except Exception as e:

        print(
            "=========================================="
        )

        print(
            "変換エラー"
        )

        print(
            "JOB:",
            job_id
        )

        print(
            "ERROR:",
            repr(e)
        )

        print(
            "=========================================="
        )


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

                })


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

                })


            # ==================================================
            # outputs
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
                        "outputsは配列で指定してください"

                })


            if not outputs:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "出力形式が指定されていません"

                })


            # ==================================================
            # 有効な出力形式だけ残す
            # ==================================================

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


            if not valid_outputs:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "mp3またはmp4を指定してください"

                })


            # ==================================================
            # 時間指定
            # ==================================================

            start_time = data.get(
                "start_time"
            )


            end_time = data.get(
                "end_time"
            )


            # ==================================================
            # Job ID
            # ==================================================

            job_id = str(
                uuid.uuid4()
            )


            # ==================================================
            # Jobを先に登録
            # ==================================================

            jobs[job_id] = {

                "status":
                    "queued"

            }


            print(
                "=========================================="
            )

            print(
                "JOB登録:",
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
                "START:",
                start_time
            )

            print(
                "END:",
                end_time
            )

            print(
                "Cookie環境:",
                "Render"
                if IS_RENDER
                else "Local"
            )

            print(
                "Cookie:",
                ORIGINAL_COOKIE_FILE
            )

            print(
                "=========================================="
            )


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

            })
```
