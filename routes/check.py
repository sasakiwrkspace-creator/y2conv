from flask import request, jsonify
import yt_dlp
import os
import shutil
import tempfile
import subprocess


# ==========================================
# Cookie設定
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
# Cookieファイル判定
# ==========================================

if os.path.exists(RENDER_COOKIE_FILE):
    COOKIE_FILE = RENDER_COOKIE_FILE
else:
    COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("check.py 起動")
print("Cookieファイル:", COOKIE_FILE)
print("==========================================")


# ==========================================
# Cookie確認
# ==========================================

def check_cookie_file():

    result = {
        "exists": False,
        "path": COOKIE_FILE,
        "size": 0,
        "cookie_count": 0,
        "youtube_google_cookie_count": 0,
        "error": None
    }

    try:

        if not os.path.exists(COOKIE_FILE):

            result["error"] = (
                f"Cookieファイルがありません: {COOKIE_FILE}"
            )

            return result


        result["exists"] = True

        result["size"] = os.path.getsize(
            COOKIE_FILE
        )


        cookie_count = 0
        youtube_google_cookie_count = 0


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
                        youtube_google_cookie_count += 1


        result["cookie_count"] = cookie_count

        result["youtube_google_cookie_count"] = (
            youtube_google_cookie_count
        )


        print(
            "Cookieファイル確認OK:",
            COOKIE_FILE
        )

        print(
            "Cookieサイズ:",
            result["size"],
            "bytes"
        )

        print(
            "Cookieデータ行数:",
            cookie_count
        )

        print(
            "YouTube/Google Cookie数:",
            youtube_google_cookie_count
        )


    except Exception as e:

        result["error"] = str(e)

        print(
            "Cookie確認エラー:",
            repr(e)
        )


    return result


# ==========================================
# 一時Cookieファイル作成
#
# Render Secret Fileは読み取り専用なので、
# /tmpへコピーして使用する
# ==========================================

def create_temp_cookie():

    if not os.path.exists(COOKIE_FILE):

        raise Exception(
            f"Cookieファイルがありません: {COOKIE_FILE}"
        )


    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        prefix="ytcookies_",
        delete=False,
        encoding="utf-8"
    )


    temp_path = temp_file.name


    try:

        with open(
            COOKIE_FILE,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as source:

            shutil.copyfileobj(
                source,
                temp_file
            )


        temp_file.close()


        print(
            "一時Cookieファイル作成:",
            temp_path
        )


        return temp_path


    except Exception:

        try:
            temp_file.close()
        except Exception:
            pass


        try:
            os.remove(temp_path)
        except Exception:
            pass


        raise


# ==========================================
# コマンド存在確認
# ==========================================

def check_command(command):

    try:

        result = subprocess.run(
            [
                command,
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )


        output = (
            result.stdout
            or result.stderr
            or ""
        ).strip()


        first_line = (
            output.splitlines()[0]
            if output
            else ""
        )


        return {

            "available":
            result.returncode == 0,

            "version":
            first_line,

            "raw":
            output

        }


    except FileNotFoundError:

        return {

            "available":
            False,

            "version":
            None,

            "raw":
            f"{command} が見つかりません"

        }


    except Exception as e:

        return {

            "available":
            False,

            "version":
            None,

            "raw":
            str(e)

        }


# ==========================================
# yt-dlpバージョン
# ==========================================

def get_ytdlp_version():

    try:

        return {

            "available":
            True,

            "version":
            yt_dlp.version.__version__

        }


    except Exception as e:

        return {

            "available":
            False,

            "version":
            None,

            "error":
            str(e)

        }


# ==========================================
# YouTube情報取得
# ==========================================

def get_youtube_info(
    url,
    cookie_file
):

    print("==========================================")

    print(
        "YouTube情報取得開始:",
        url
    )

    print(
        "使用Cookie:",
        cookie_file
    )

    print("==========================================")


    ydl_opts = {

        # Cookie
        "cookiefile":
        cookie_file,

        # プレイリスト無効
        "noplaylist":
        True,

        # ダウンロードしない
        "skip_download":
        True,

        # 診断用
        "quiet":
        False,

        "no_warnings":
        False,

        "ignoreerrors":
        False

    }


    try:

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )


        return {

            "success":
            True,

            "info":
            info,

            "error":
            None

        }


    except Exception as e:

        print(
            "YouTube情報取得エラー:",
            repr(e)
        )


        return {

            "success":
            False,

            "info":
            None,

            "error":
            str(e)

        }


# ==========================================
# Format解析
# ==========================================

def analyze_formats(info):

    formats = []


    if info:

        formats = info.get(
            "formats",
            []
        )


    audio_formats = []

    video_formats = []

    video_audio_formats = []


    for f in formats:

        format_id = f.get(
            "format_id"
        )

        ext = f.get(
            "ext"
        )

        acodec = f.get(
            "acodec"
        )

        vcodec = f.get(
            "vcodec"
        )

        abr = f.get(
            "abr"
        )

        tbr = f.get(
            "tbr"
        )

        resolution = f.get(
            "resolution"
        )

        protocol = f.get(
            "protocol"
        )


        item = {

            "format_id":
            format_id,

            "ext":
            ext,

            "acodec":
            acodec,

            "vcodec":
            vcodec,

            "abr":
            abr,

            "tbr":
            tbr,

            "resolution":
            resolution,

            "protocol":
            protocol

        }


        # ======================================
        # 音声のみ
        # ======================================

        if (
            acodec
            and acodec != "none"
            and (
                not vcodec
                or vcodec == "none"
            )
        ):

            audio_formats.append(
                item
            )


        # ======================================
        # 動画のみ
        # ======================================

        elif (
            vcodec
            and vcodec != "none"
            and (
                not acodec
                or acodec == "none"
            )
        ):

            video_formats.append(
                item
            )


        # ======================================
        # 動画＋音声
        # ======================================

        elif (
            vcodec
            and vcodec != "none"
            and acodec
            and acodec != "none"
        ):

            video_audio_formats.append(
                item
            )


    return {

        "total":
        len(formats),

        "audio_only":
        audio_formats,

        "video_only":
        video_formats,

        "video_audio":
        video_audio_formats

    }


# ==========================================
# /check
# ==========================================

def register_check(app):

    @app.route(
        "/check",
        methods=["POST"]
    )

    def check():

        temp_cookie_file = None


        try:

            # ==================================
            # JSON取得
            # ==================================

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


            # ==================================
            # URL取得
            # ==================================

            url = data.get(
                "url"
            )


            if not url:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "YouTube URLを入力してください"

                })


            print("==========================================")

            print(
                "CHECK開始:",
                url
            )

            print("==========================================")


            # ==================================
            # Cookie確認
            # ==================================

            cookie_status = (
                check_cookie_file()
            )


            if not cookie_status["exists"]:

                return jsonify({

                    "success":
                    False,

                    "message":
                    cookie_status["error"],

                    "diagnostic": {

                        "cookie":
                        cookie_status,

                        "yt_dlp":
                        get_ytdlp_version(),

                        "deno":
                        check_command("deno"),

                        "ffmpeg":
                        check_command("ffmpeg")

                    }

                })


            # ==================================
            # 一時Cookie作成
            # ==================================

            try:

                temp_cookie_file = (
                    create_temp_cookie()
                )


            except Exception as e:

                print(
                    "一時Cookie作成失敗:",
                    repr(e)
                )


                return jsonify({

                    "success":
                    False,

                    "message":
                    "一時Cookieファイルを作成できません",

                    "error":
                    str(e),

                    "diagnostic": {

                        "cookie":
                        cookie_status,

                        "yt_dlp":
                        get_ytdlp_version(),

                        "deno":
                        check_command("deno"),

                        "ffmpeg":
                        check_command("ffmpeg")

                    }

                })


            # ==================================
            # YouTube情報取得
            # ==================================

            result = get_youtube_info(

                url,

                temp_cookie_file

            )


            # ==================================
            # YouTube取得失敗
            # ==================================

            if not result["success"]:

                error_message = (
                    result["error"]
                )


                print(
                    "check error:",
                    error_message
                )


                return jsonify({

                    "success":
                    False,

                    "message":
                    error_message,

                    "diagnostic": {

                        "url":
                        url,

                        "cookie":
                        cookie_status,

                        "yt_dlp":
                        get_ytdlp_version(),

                        "deno":
                        check_command("deno"),

                        "ffmpeg":
                        check_command("ffmpeg"),

                        "youtube": {

                            "success":
                            False,

                            "error":
                            error_message

                        }

                    }

                })


            # ==================================
            # info
            # ==================================

            info = result["info"]


            # ==================================
            # タイトル
            # ==================================

            title = info.get(
                "title",
                "タイトル取得失敗"
            )


            # ==================================
            # 再生時間
            # ==================================

            duration_sec = info.get(
                "duration"
            )


            duration = "不明"


            if duration_sec is not None:

                try:

                    duration_sec = int(
                        duration_sec
                    )


                    hours = (
                        duration_sec // 3600
                    )


                    minutes = (
                        duration_sec % 3600
                    ) // 60


                    seconds = (
                        duration_sec % 60
                    )


                    if hours > 0:

                        duration = (
                            f"{hours}:"
                            f"{minutes:02}:"
                            f"{seconds:02}"
                        )

                    else:

                        duration = (
                            f"{minutes}:"
                            f"{seconds:02}"
                        )


                except Exception:

                    duration = "不明"


            # ==================================
            # Format解析
            # ==================================

            format_info = (
                analyze_formats(info)
            )


            # ==================================
            # ログ
            # ==================================

            print("==========================================")

            print(
                "動画タイトル:",
                title
            )

            print(
                "再生時間:",
                duration
            )

            print(
                "Format総数:",
                format_info["total"]
            )

            print(
                "音声のみ:",
                len(
                    format_info["audio_only"]
                )
            )

            print(
                "動画のみ:",
                len(
                    format_info["video_only"]
                )
            )

            print(
                "動画+音声:",
                len(
                    format_info["video_audio"]
                )
            )

            print("==========================================")


            # ==================================
            # Format状態
            # ==================================

            if format_info["total"] == 0:

                format_status = (
                    "formatを取得できませんでした"
                )


            elif len(
                format_info["audio_only"]
            ) == 0:

                format_status = (
                    "音声formatが取得できませんでした"
                )


            else:

                format_status = (
                    "音声format取得OK"
                )


            # ==================================
            # 成功レスポンス
            # ==================================

            return jsonify({

                "success":
                True,

                "filename":
                title,

                "duration":
                duration,

                "diagnostic": {

                    "cookie":
                    cookie_status,

                    "yt_dlp":
                    get_ytdlp_version(),

                    "deno":
                    check_command("deno"),

                    "ffmpeg":
                    check_command("ffmpeg"),

                    "youtube": {

                        "title":
                        title,

                        "duration_seconds":
                        duration_sec,

                        "format_status":
                        format_status,

                        "format_count":
                        format_info["total"],

                        "audio_only_count":
                        len(
                            format_info["audio_only"]
                        ),

                        "video_only_count":
                        len(
                            format_info["video_only"]
                        ),

                        "video_audio_count":
                        len(
                            format_info["video_audio"]
                        ),

                        "audio_formats":
                        format_info["audio_only"],

                        "video_formats":
                        format_info["video_only"],

                        "video_audio_formats":
                        format_info["video_audio"]

                    }

                }

            })


        except Exception as e:

            print("==========================================")

            print(
                "check error:",
                repr(e)
            )

            print("==========================================")


            return jsonify({

                "success":
                False,

                "message":
                str(e),

                "diagnostic": {

                    "yt_dlp":
                    get_ytdlp_version(),

                    "deno":
                    check_command("deno"),

                    "ffmpeg":
                    check_command("ffmpeg")

                }

            })


        finally:

            # ==================================
            # 一時Cookie削除
            # ==================================

            if temp_cookie_file:

                try:

                    if os.path.exists(
                        temp_cookie_file
                    ):

                        os.remove(
                            temp_cookie_file
                        )


                        print(
                            "一時Cookieファイル削除OK"
                        )


                except Exception as e:

                    print(
                        "一時Cookie削除失敗:",
                        repr(e)
                    )
