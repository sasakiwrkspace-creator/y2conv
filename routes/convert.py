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


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


LOCAL_COOKIE_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt"
)


# ==========================================================
# Render / ローカル判定
# ==========================================================

if os.path.exists(RENDER_COOKIE_FILE):

    COOKIE_FILE = RENDER_COOKIE_FILE

else:

    COOKIE_FILE = LOCAL_COOKIE_FILE


print(
    "=========================================="
)

print(
    "使用するCookieファイル:",
    COOKIE_FILE
)

print(
    "=========================================="
)


# ==========================================================
# Cookieファイル確認
# ==========================================================

def check_cookie_file():

    if not os.path.exists(COOKIE_FILE):

        raise Exception(
            f"Cookieファイルが見つかりません: {COOKIE_FILE}"
        )


    file_size = os.path.getsize(
        COOKIE_FILE
    )


    print(
        "Cookieファイル確認OK:",
        COOKIE_FILE
    )

    print(
        "Cookieファイルサイズ:",
        file_size,
        "bytes"
    )


    cookie_count = 0
    youtube_cookie_count = 0


    with open(
        COOKIE_FILE,
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


            cookie_count += 1


            fields = line.split("\t")


            if len(fields) >= 7:

                domain = fields[0].lower()


                if (
                    "youtube.com" in domain
                    or "google.com" in domain
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


# ==========================================================
# 一時Cookieファイル作成
#
# RenderのSecret Fileは読み取り専用なので、
# yt-dlpには /tmp の書き込み可能なコピーを渡す。
# ==========================================================

def create_temp_cookie_file():

    check_cookie_file()


    temp_cookie = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        prefix="ytcookies_",
        delete=False,
        encoding="utf-8"
    )


    temp_cookie_path = temp_cookie.name


    temp_cookie.close()


    shutil.copyfile(
        COOKIE_FILE,
        temp_cookie_path
    )


    print(
        "一時Cookieファイル作成:",
        temp_cookie_path
    )


    return temp_cookie_path


# ==========================================================
# 一時Cookieファイル削除
# ==========================================================

def remove_temp_cookie_file(
    temp_cookie_path
):

    if not temp_cookie_path:

        return


    try:

        if os.path.exists(
            temp_cookie_path
        ):

            os.remove(
                temp_cookie_path
            )


            print(
                "一時Cookieファイル削除OK:",
                temp_cookie_path
            )

    except Exception as e:

        print(
            "一時Cookieファイル削除失敗:",
            repr(e)
        )


# ==========================================================
# yt-dlp 共通設定
# ==========================================================

def create_ydl_base_options(
    temp_cookie_file
):

    return {

        # ------------------------------------------
        # Cookie
        # ------------------------------------------

        "cookiefile":
        temp_cookie_file,


        # ------------------------------------------
        # playlist防止
        # ------------------------------------------

        "noplaylist":
        True,


        # ------------------------------------------
        # Deno
        # ------------------------------------------

        "js_runtimes": {
            "deno": {}
        },

        # ------------------------------------------
        # エラー表示
        # ------------------------------------------

        "no_warnings":
        False

    }


# ==========================================================
# YouTube情報・format診断
# ==========================================================

def diagnose_formats(
    url,
    temp_cookie_file
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


    ydl_opts = create_ydl_base_options(
        temp_cookie_file
    )


    ydl_opts.update({

        "skip_download":
        True,

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
# 変換処理
# ==========================================================

def convert_task(
    job_id,
    url,
    outputs,
    start_time=None,
    end_time=None
):

    temp_cookie_file = None


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
            "=========================================="
        )


        # ==================================================
        # Cookie確認
        # ==================================================

        check_cookie_file()


        # ==================================================
        # Cookieを/tmpへコピー
        # ==================================================

        temp_cookie_file = (
            create_temp_cookie_file()
        )


        # ==================================================
        # 24時間以上経過したファイルを削除
        # ==================================================

        cleanup_downloads()


        # ==================================================
        # output directory
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

            print(
                "=========================================="
            )

            print(
                "MP3変換開始"
            )

            print(
                "=========================================="
            )


            # ==================================================
            # Format診断
            # ==================================================

            info = diagnose_formats(
                url,
                temp_cookie_file
            )


            # ==================================================
            # MP3ダウンロード
            #
            # 140 = m4a / AAC / 約129kbps
            #
            # 140が存在しない場合はbestaudio
            # ==================================================

            print(
                "=========================================="
            )

            print(
                "MP3ダウンロード開始"
            )

            print(
                "format: 140/bestaudio"
            )

            print(
                "MP3品質: 192kbps"
            )

            print(
                "=========================================="
            )


            ydl_opts = create_ydl_base_options(
                temp_cookie_file
            )


            ydl_opts.update({

                "format":
                "140/bestaudio",

                "outtmpl":
                f"{output_dir}/%(title)s.%(ext)s",

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


            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(

                    url,

                    download=True

                )


                filename = ydl.prepare_filename(
                    info
                )


            # ==================================================
            # MP3ファイル名
            # ==================================================

            mp3_file = os.path.splitext(
                filename
            )[0] + ".mp3"


            # ==================================================
            # MP3存在確認
            # ==================================================

            if not os.path.exists(
                mp3_file
            ):

                raise Exception(
                    f"MP3ファイルが作成されませんでした: {mp3_file}"
                )


            print(
                "MP3ファイル作成:",
                mp3_file
            )


            # ==================================================
            # MP3サイズ
            # ==================================================

            mp3_size = os.path.getsize(
                mp3_file
            )


            print(
                "MP3ファイルサイズ:",
                mp3_size,
                "bytes"
            )


            # ==================================================
            # MP3時間指定カット
            # ==================================================

            if (
                start_time
                and end_time
                and start_time < end_time
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


                result = subprocess.run([

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

                ])


                if result.returncode != 0:

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


            # ==================================================
            # ファイル一覧へ追加
            # ==================================================

            files.append(
                os.path.basename(
                    mp3_file
                )
            )


            print(
                "=========================================="
            )

            print(
                "MP3完成:",
                mp3_file
            )

            print(
                "=========================================="
            )


        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in outputs:

            print(
                "=========================================="
            )

            print(
                "MP4変換開始"
            )

            print(
                "=========================================="
            )


            # ==================================================
            # MP4
            #
            # mp4動画 + m4a音声
            #
            # 例:
            #
            # 137 + 140
            # 136 + 140
            # 135 + 140
            # 134 + 140
            # ==================================================

            ydl_opts = create_ydl_base_options(
                temp_cookie_file
            )


            ydl_opts.update({

                "format":
                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",

                "merge_output_format":
                "mp4",

                "outtmpl":
                f"{output_dir}/%(title)s.%(ext)s"

            })


            print(
                "MP4 format:",
                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            )


            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(

                    url,

                    download=True

                )


                filename = ydl.prepare_filename(
                    info
                )


            # ==================================================
            # MP4ファイル
            # ==================================================

            mp4_file = os.path.splitext(
                filename
            )[0] + ".mp4"


            # ==================================================
            # MP4存在確認
            # ==================================================

            if not os.path.exists(
                mp4_file
            ):

                raise Exception(
                    f"MP4ファイルが作成されませんでした: {mp4_file}"
                )


            print(
                "MP4ファイル作成:",
                mp4_file
            )


            # ==================================================
            # MP4時間指定カット
            # ==================================================

            if (
                start_time
                and end_time
                and start_time < end_time
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


                result = subprocess.run([

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

                ])


                if result.returncode != 0:

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


            # ==================================================
            # ファイル一覧へ追加
            # ==================================================

            files.append(
                os.path.basename(
                    mp4_file
                )
            )


            print(
                "=========================================="
            )

            print(
                "MP4完成:",
                mp4_file
            )

            print(
                "=========================================="
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


    finally:

        # ==================================================
        # 一時Cookie削除
        # ==================================================

        remove_temp_cookie_file(
            temp_cookie_file
        )


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

            data = request.get_json()


            # ==================================================
            # JSON確認
            # ==================================================

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


            # ==================================================
            # 出力形式
            # ==================================================

            outputs = data.get(
                "outputs",
                []
            )


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
            # URL確認
            # ==================================================

            if not url:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "URLがありません"

                })


            # ==================================================
            # outputs確認
            # ==================================================

            if not outputs:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "出力形式が指定されていません"

                })


            # ==================================================
            # outputs確認
            # ==================================================

            valid_outputs = []


            for output in outputs:

                if output in [
                    "mp3",
                    "mp4"
                ]:

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
                "=========================================="
            )


            # ==================================================
            # バックグラウンド処理
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


            thread.start()


            # ==================================================
            # Job IDを返す
            # ==================================================

            return jsonify({

                "success":
                True,

                "job_id":
                job_id

            })


        except Exception as e:

            print(
                "=========================================="
            )

            print(
                "convertエラー:",
                repr(e)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success":
                False,

                "message":
                str(e)

            })
