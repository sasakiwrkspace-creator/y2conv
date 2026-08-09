from flask import request, jsonify
import yt_dlp
import uuid
import threading
import os
import subprocess

from routes.status import jobs
from cleanup import cleanup_downloads


# ==========================================
# Cookieファイル
# ==========================================

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


# ==========================================
# Render / ローカル判定
# ==========================================

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


# ==========================================
# Cookie確認
# ==========================================

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


# ==========================================
# YouTube情報・format診断
# ==========================================

def diagnose_formats(url):

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


    ydl_opts = {

        "cookiefile":
        COOKIE_FILE,

        "noplaylist":
        True,

        "verbose":
        True,

        "skip_download":
        True

    }


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


    # ==========================================
    # 基本情報
    # ==========================================

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


    # ==========================================
    # Format一覧
    # ==========================================

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


# ==========================================
# 変換処理
# ==========================================

def convert_task(
    job_id,
    url,
    outputs,
    start_time=None,
    end_time=None
):

    try:

        # ==========================================
        # Cookie確認
        # ==========================================

        check_cookie_file()


        # ==========================================
        # 24時間以上経過したファイルを削除
        # ==========================================

        cleanup_downloads()


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


        # ==========================================
        # Job running
        # ==========================================

        jobs[job_id] = {

            "status":
            "running"

        }


        output_dir = "downloads"


        os.makedirs(
            output_dir,
            exist_ok=True
        )


        files = []


        # ==========================================
        # MP3
        # ==========================================

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


            # ==========================================
            # YouTube情報・format診断
            # ==========================================

            info = diagnose_formats(
                url
            )


            # ==========================================
            # MP3ダウンロード
            #
            # 今回確認できた format 140 を優先
            #
            # 140:
            # m4a / audio only
            # AAC 約129kbps
            #
            # 140がない場合はbest audioへフォールバック
            # ==========================================

            print(
                "=========================================="
            )

            print(
                "MP3ダウンロード開始"
            )

            print(
                "format: 140/bestaudio/best"
            )

            print(
                "MP3品質: 192kbps"
            )

            print(
                "=========================================="
            )


            ydl_opts = {

                "cookiefile":
                COOKIE_FILE,

                "format":
                "140/bestaudio/best",

                "outtmpl":
                f"{output_dir}/%(title)s.%(ext)s",

                "noplaylist":
                True,

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

            }


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


            # ==========================================
            # MP3ファイル名
            # ==========================================

            mp3_file = os.path.splitext(
                filename
            )[0] + ".mp3"


            # ==========================================
            # MP3存在確認
            # ==========================================

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


            # ==========================================
            # MP3ファイルサイズ
            # ==========================================

            mp3_size = os.path.getsize(
                mp3_file
            )


            print(
                "MP3ファイルサイズ:",
                mp3_size,
                "bytes"
            )


            # ==========================================
            # MP3時間指定カット
            # ==========================================

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


                cut_file = os.path.splitext(
                    mp3_file
                )[0] + "_cut.mp3"


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


            # ==========================================
            # ファイル一覧へ追加
            # ==========================================

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


        # ==========================================
        # MP4
        # ==========================================

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


            # ==========================================
            # MP4 format
            #
            # mp4動画 + m4a音声を優先
            # ==========================================

            ydl_opts = {

                "cookiefile":
                COOKIE_FILE,

                "format":
                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",

                "merge_output_format":
                "mp4",

                "outtmpl":
                f"{output_dir}/%(title)s.%(ext)s",

                "noplaylist":
                True

            }


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


            mp4_file = os.path.splitext(
                filename
            )[0] + ".mp4"


            # ==========================================
            # MP4存在確認
            # ==========================================

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


            # ==========================================
            # MP4時間指定カット
            # ==========================================

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


                cut_file = os.path.splitext(
                    mp4_file
                )[0] + "_cut.mp4"


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


            # ==========================================
            # ファイル一覧へ追加
            # ==========================================

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


        # ==========================================
        # 完了
        # ==========================================

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


    # ==========================================
    # エラー
    # ==========================================

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


# ==========================================
# /convert
# ==========================================

def register_convert(app):


    @app.route(
        "/convert",
        methods=["POST"]
    )

    def convert():

        try:

            data = request.get_json()


            # ==========================================
            # JSON確認
            # ==========================================

            if not data:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "JSONデータがありません"

                })


            # ==========================================
            # URL
            # ==========================================

            url = data.get(
                "url"
            )


            # ==========================================
            # 出力形式
            # ==========================================

            outputs = data.get(
                "outputs",
                []
            )


            # ==========================================
            # 時間指定
            # ==========================================

            start_time = data.get(
                "start_time"
            )


            end_time = data.get(
                "end_time"
            )


            # ==========================================
            # URL確認
            # ==========================================

            if not url:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "URLがありません"

                })


            # ==========================================
            # outputs確認
            # ==========================================

            if not outputs:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "出力形式が指定されていません"

                })


            # ==========================================
            # outputsの確認
            # ==========================================

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


            # ==========================================
            # Job ID
            # ==========================================

            job_id = str(
                uuid.uuid4()
            )


            # ==========================================
            # Jobを先に登録
            #
            # これにより、thread開始前に
            # statusへアクセスされても
            # 「jobなし」になりません。
            # ==========================================

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


            # ==========================================
            # バックグラウンド処理
            # ==========================================

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


            # ==========================================
            # Job IDを返す
            # ==========================================

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
