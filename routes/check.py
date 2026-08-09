from flask import request, jsonify

import yt_dlp
import os
import tempfile
import shutil
import subprocess


# =========================================================
# Cookie
# =========================================================

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


# =========================================================
# Cookieファイル確認
# =========================================================

def get_cookie_file():

    if os.path.exists(RENDER_COOKIE_FILE):

        return RENDER_COOKIE_FILE

    if os.path.exists(LOCAL_COOKIE_FILE):

        return LOCAL_COOKIE_FILE

    return None


# =========================================================
# 一時Cookie作成
#
# /etc/secrets は読み取り専用なので、
# /tmpへコピーする
# =========================================================

def create_temp_cookie():

    source = get_cookie_file()

    if not source:

        raise Exception(
            "Cookieファイルが見つかりません"
        )

    print(
        "Cookieファイル確認OK:",
        source
    )

    cookie_size = os.path.getsize(
        source
    )

    print(
        "Cookieファイルサイズ:",
        cookie_size,
        "bytes"
    )

    if cookie_size == 0:

        raise Exception(
            "Cookieファイルが空です"
        )

    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        prefix="ytcookies_",
        delete=False,
        encoding="utf-8"
    )

    temp_path = temp_file.name

    temp_file.close()

    shutil.copyfile(
        source,
        temp_path
    )

    print(
        "一時Cookieファイル作成:",
        temp_path
    )

    print(
        "一時Cookieサイズ:",
        os.path.getsize(temp_path),
        "bytes"
    )

    return temp_path


# =========================================================
# Cookie削除
# =========================================================

def remove_temp_cookie(path):

    if not path:

        return

    try:

        if os.path.exists(path):

            os.remove(path)

            print(
                "一時Cookieファイル削除OK"
            )

    except Exception as e:

        print(
            "一時Cookieファイル削除失敗:",
            repr(e)
        )


# =========================================================
# 秒 → 時間表示
# =========================================================

def format_duration(duration_sec):

    if not duration_sec:

        return "0:00"

    duration_sec = int(
        duration_sec
    )

    hours = duration_sec // 3600

    minutes = (
        duration_sec % 3600
    ) // 60

    seconds = (
        duration_sec % 60
    )

    if hours > 0:

        return (
            f"{hours}:"
            f"{minutes:02}:"
            f"{seconds:02}"
        )

    return (
        f"{minutes}:"
        f"{seconds:02}"
    )


# =========================================================
# yt-dlp基本設定
# =========================================================

def get_ytdlp_options(cookie_file):

    return {

        # -----------------------------------------
        # ダウンロードしない
        # -----------------------------------------

        "skip_download": True,

        # -----------------------------------------
        # Cookie
        # -----------------------------------------

        "cookiefile": cookie_file,

        # -----------------------------------------
        # Playlist無効
        # -----------------------------------------

        "noplaylist": True,

        # -----------------------------------------
        # 通常の情報取得
        # -----------------------------------------

        "extract_flat": False,

        # -----------------------------------------
        # エラーをExceptionとして取得
        # -----------------------------------------

        "ignoreerrors": False,

        # -----------------------------------------
        # ログ
        # -----------------------------------------

        "quiet": False,

        "no_warnings": False,

        # -----------------------------------------
        # YouTube client
        # -----------------------------------------

        "extractor_args": {

            "youtube": {

                "player_client": [
                    "web"
                ]

            }

        }

    }


# =========================================================
# YouTube情報取得
# =========================================================

def get_youtube_info(
    url,
    cookie_file
):

    print(
        "=========================================="
    )

    print(
        "YouTube情報取得開始:",
        url
    )

    print(
        "=========================================="
    )

    ydl_opts = get_ytdlp_options(
        cookie_file
    )

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    if not info:

        raise Exception(
            "YouTube情報を取得できませんでした"
        )

    return info


# =========================================================
# YouTubeフォーマット取得
#
# 重要:
#
# 通常のextract_info()では、
# yt-dlpがデフォルトフォーマットを選択する際に
#
# Requested format is not available
#
# が発生する場合があります。
#
# そのため診断用として、
# format="all" を指定してフォーマット選択を
# できるだけ避けます。
# =========================================================

def get_youtube_formats(
    url,
    cookie_file
):

    print(
        "=========================================="
    )

    print(
        "YouTubeフォーマット診断開始:",
        url
    )

    print(
        "=========================================="
    )

    ydl_opts = get_ytdlp_options(
        cookie_file
    )

    # -----------------------------------------
    # フォーマット選択によるエラーを避ける
    # -----------------------------------------

    ydl_opts["format"] = "all"

    # -----------------------------------------
    # 診断用
    # -----------------------------------------

    ydl_opts["quiet"] = True

    ydl_opts["no_warnings"] = False

    try:

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

    except Exception as e:

        print(
            "フォーマット診断エラー:",
            repr(e)
        )

        raise

    if not info:

        raise Exception(
            "YouTube情報を取得できませんでした"
        )

    formats = []

    for f in info.get(
        "formats",
        []
    ):

        formats.append({

            "format_id":
                f.get("format_id"),

            "ext":
                f.get("ext"),

            "resolution":
                f.get("resolution"),

            "width":
                f.get("width"),

            "height":
                f.get("height"),

            "fps":
                f.get("fps"),

            "vcodec":
                f.get("vcodec"),

            "acodec":
                f.get("acodec"),

            "format_note":
                f.get("format_note"),

            "filesize":
                f.get("filesize"),

            "filesize_approx":
                f.get("filesize_approx"),

            "tbr":
                f.get("tbr"),

            "protocol":
                f.get("protocol"),

            "dynamic_range":
                f.get("dynamic_range")

        })

    print(
        "取得フォーマット数:",
        len(formats)
    )

    return formats


# =========================================================
# コマンド確認
# =========================================================

def command_info(
    command,
    args=None
):

    if args is None:

        args = []

    try:

        result = subprocess.run(

            [command] + args,

            capture_output=True,

            text=True,

            timeout=10

        )

        return {

            "installed":
                True,

            "returncode":
                result.returncode,

            "stdout":
                result.stdout.strip(),

            "stderr":
                result.stderr.strip()

        }

    except FileNotFoundError:

        return {

            "installed":
                False,

            "error":
                "command not found"

        }

    except Exception as e:

        return {

            "installed":
                False,

            "error":
                repr(e)

        }


# =========================================================
# 実行ファイルの場所確認
# =========================================================

def command_path(
    command
):

    try:

        result = subprocess.run(

            [
                "which",
                command
            ],

            capture_output=True,

            text=True,

            timeout=5

        )

        path = result.stdout.strip()

        if path:

            return path

        return None

    except Exception:

        return None


# =========================================================
# /check
#
# YouTube動画情報確認
# =========================================================

def register_check(app):


    # =====================================================
    # /check
    # =====================================================

    @app.route(
        "/check",
        methods=["POST"]
    )
    def check():

        temp_cookie = None

        try:

            # =============================================
            # JSON
            # =============================================

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


            # =============================================
            # URL
            # =============================================

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


            print(
                "=========================================="
            )

            print(
                "CHECK START"
            )

            print(
                "URL:",
                url
            )

            print(
                "=========================================="
            )


            # =============================================
            # Cookie
            # =============================================

            temp_cookie = create_temp_cookie()


            # =============================================
            # YouTube情報取得
            # =============================================

            info = get_youtube_info(
                url,
                temp_cookie
            )


            # =============================================
            # タイトル
            # =============================================

            title = info.get(
                "title"
            )

            if not title:

                title = "タイトル取得失敗"


            # =============================================
            # 再生時間
            # =============================================

            duration_sec = info.get(
                "duration"
            )

            duration = format_duration(
                duration_sec
            )


            # =============================================
            # フォーマット情報
            # =============================================

            formats = []

            format_error = None

            try:

                formats = get_youtube_formats(
                    url,
                    temp_cookie
                )

            except Exception as e:

                format_error = str(e)

                print(
                    "フォーマット取得失敗:",
                    repr(e)
                )


            # =============================================
            # 結果ログ
            # =============================================

            print(
                "=========================================="
            )

            print(
                "YouTube情報取得成功"
            )

            print(
                "タイトル:",
                title
            )

            print(
                "再生時間:",
                duration
            )

            print(
                "フォーマット数:",
                len(formats)
            )

            if format_error:

                print(
                    "フォーマットエラー:",
                    format_error
                )

            print(
                "=========================================="
            )


            # =============================================
            # 結果
            # =============================================

            return jsonify({

                "success":
                    True,

                "filename":
                    title,

                "duration":
                    duration,

                "format_count":
                    len(formats),

                "formats":
                    formats,

                "format_error":
                    format_error

            })


        except Exception as e:

            print(
                "=========================================="
            )

            print(
                "check error:",
                repr(e)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e),

                "error_type":
                    type(e).__name__

            })


        finally:

            # =============================================
            # 一時Cookie削除
            # =============================================

            remove_temp_cookie(
                temp_cookie
            )


    # =====================================================
    # /system-check
    #
    # Render / Docker環境確認
    # =====================================================

    @app.route(
        "/system-check",
        methods=["GET"]
    )
    def system_check():

        result = {}


        # =============================================
        # Python
        # =============================================

        result["python"] = command_info(
            "python",
            ["--version"]
        )


        # =============================================
        # Python3
        # =============================================

        result["python3"] = command_info(
            "python3",
            ["--version"]
        )


        # =============================================
        # Python実行ファイル
        # =============================================

        result["python_executable"] = {

            "path":
                os.sys.executable

        }


        # =============================================
        # Python版yt-dlp
        # =============================================

        try:

            result["python_yt_dlp"] = {

                "installed":
                    True,

                "version":
                    yt_dlp.version.__version__

            }

        except Exception as e:

            result["python_yt_dlp"] = {

                "installed":
                    False,

                "error":
                    repr(e)

            }


        # =============================================
        # yt-dlp CLI
        # =============================================

        result["yt-dlp"] = command_info(
            "yt-dlp",
            ["--version"]
        )

        result["yt-dlp"]["path"] = command_path(
            "yt-dlp"
        )


        # =============================================
        # FFmpeg
        # =============================================

        result["ffmpeg"] = command_info(
            "ffmpeg",
            [
                "-version"
            ]
        )

        result["ffmpeg"]["path"] = command_path(
            "ffmpeg"
        )


        # =============================================
        # FFprobe
        # =============================================

        result["ffprobe"] = command_info(
            "ffprobe",
            [
                "-version"
            ]
        )

        result["ffprobe"]["path"] = command_path(
            "ffprobe"
        )


        # =============================================
        # Cookie
        # =============================================

        cookie_file = get_cookie_file()

        if cookie_file:

            try:

                cookie_size = os.path.getsize(
                    cookie_file
                )

            except Exception:

                cookie_size = None


            result["cookie"] = {

                "exists":
                    True,

                "path":
                    cookie_file,

                "size":
                    cookie_size

            }

        else:

            result["cookie"] = {

                "exists":
                    False,

                "path":
                    None,

                "size":
                    0

            }


        # =============================================
        # /etc/secrets確認
        # =============================================

        result["secrets_directory"] = {

            "exists":
                os.path.exists(
                    "/etc/secrets"
                ),

            "is_directory":
                os.path.isdir(
                    "/etc/secrets"
                )

        }


        # =============================================
        # /tmp書き込み確認
        # =============================================

        test_path = None

        try:

            temp_file = tempfile.NamedTemporaryFile(

                mode="w",

                prefix="render_check_",

                suffix=".txt",

                delete=False

            )

            test_path = temp_file.name

            temp_file.write(
                "Render Docker write test"
            )

            temp_file.close()


            result["tmp"] = {

                "writable":
                    True,

                "path":
                    test_path

            }


        except Exception as e:

            result["tmp"] = {

                "writable":
                    False,

                "error":
                    repr(e)

            }


        finally:

            if test_path:

                try:

                    if os.path.exists(
                        test_path
                    ):

                        os.remove(
                            test_path
                        )

                except Exception:

                    pass


        # =============================================
        # 現在のディレクトリ
        # =============================================

        result["working_directory"] = {

            "path":
                os.getcwd()

        }


        # =============================================
        # Pythonファイル位置
        # =============================================

        result["current_file"] = {

            "path":
                os.path.abspath(
                    __file__
                )

        }


        # =============================================
        # 結果
        # =============================================

        return jsonify({

            "success":
                True,

            "environment":
                result

        })


# =========================================================
# End of file
# =========================================================

