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

# Render Secret File
RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ==========================================================
# プロジェクトのルートディレクトリ
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
#
# Renderでは /tmp を使用
# ==========================================================

DOWNLOAD_DIR = "/tmp/y2conv_downloads"


# ==========================================================
# Cookieファイル選択
#
# Render:
# /etc/secrets/cookies.txt
#
# ローカル:
# プロジェクト直下/cookies.txt
# ==========================================================

if os.environ.get("RENDER") == "true":
    SOURCE_COOKIE_FILE = RENDER_COOKIE_FILE
else:
    SOURCE_COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("convert.py Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("元Cookieファイル:")
print(SOURCE_COOKIE_FILE)
print("==========================================")


# ==========================================================
# Cookie確認
# ==========================================================

def check_cookie_file():

    if not os.path.exists(
        SOURCE_COOKIE_FILE
    ):

        raise Exception(
            f"Cookieファイルが見つかりません: {SOURCE_COOKIE_FILE}"
        )

    file_size = os.path.getsize(
        SOURCE_COOKIE_FILE
    )

    print("==========================================")
    print("Cookieファイル確認")
    print("==========================================")

    print(
        "Cookieファイル:",
        SOURCE_COOKIE_FILE
    )

    print(
        "Cookieファイルサイズ:",
        file_size,
        "bytes"
    )

    if file_size == 0:

        raise Exception(
            f"Cookieファイルが空です: {SOURCE_COOKIE_FILE}"
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

                cookie_count += 1

                fields = line.split("\t")

                if len(fields) >= 7:

                    domain = fields[0].lower()

                    if (
                        "youtube.com" in domain
                        or "google.com" in domain
                    ):

                        youtube_cookie_count += 1

    except Exception as e:

        raise Exception(
            f"Cookieファイル読み込み失敗: {e}"
        )

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
# yt-dlp用Cookieファイル作成
#
# 重要:
# /etc/secrets/cookies.txt は読み取り専用。
#
# yt-dlpはCookieファイルを読み込むだけではなく、
# Cookie Jarを書き戻す場合があるため、
# /tmpへコピーして使用する。
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
        print("yt-dlp用Cookieファイル作成OK")
        print("==========================================")

        print(
            "元Cookie:",
            SOURCE_COOKIE_FILE
        )

        print(
            "一時Cookie:",
            temp_cookie
        )

        print(
            "サイズ:",
            file_size,
            "bytes"
        )

        return temp_cookie

    except Exception:

        if temp_cookie and os.path.exists(
            temp_cookie
        ):

            try:
                os.remove(temp_cookie)
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
                "一時Cookieファイル削除OK:",
                cookie_file
            )

        except Exception as e:

            print(
                "WARNING: 一時Cookie削除失敗:",
                repr(e)
            )


# ==========================================================
# Deno確認
# ==========================================================

def check_deno():

    print("==========================================")
    print("Deno確認")
    print("==========================================")

    if not os.path.exists(
        DENO_PATH
    ):

        print(
            "Deno: 見つかりません"
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

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        "cookiefile":
        temp_cookie,

        # --------------------------------------------------
        # Playlist無効
        # --------------------------------------------------

        "noplaylist":
        True

    }

    # ------------------------------------------------------
    # Deno
    # ------------------------------------------------------

    if deno_available:

        ydl_opts[
            "js_runtimes"
        ] = {

            "deno":
            DENO_PATH

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
        DENO_PATH if deno_available else "None"
    )

    print(
        "EJS:",
        "yt-dlp-ejs package"
    )

    print("==========================================")

    return ydl_opts, temp_cookie


# ==========================================================
# YouTube情報・format診断
# ==========================================================

def diagnose_formats(url):

    print("==========================================")
    print("YouTube情報取得開始")
    print("URL:", url)
    print("==========================================")

    ydl_opts = None
    temp_cookie = None

    try:

        ydl_opts, temp_cookie = get_ydl_base_options()

        ydl_opts.update({

            "quiet":
            False,

            "no_warnings":
            False,

            "verbose":
            True,

            "skip_download":
            True

        })

        print("==========================================")
        print("extract_info開始")
        print("==========================================")

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

        # ==================================================
        # 基本情報
        # ==================================================

        title = info.get(
            "title"
        )

        duration = info.get(
            "duration"
        )

        print("==========================================")

        print(
            "動画タイトル:",
            title
        )

        print(
            "再生時間:",
            duration,
            "秒"
        )

        print("==========================================")

        # ==================================================
        # Format一覧
        # ==================================================

        formats = info.get(
            "formats",
            []
        )

        print(
            "利用可能format数:",
            len(formats)
        )

        print("==========================================")
        print("利用可能format一覧")
        print("==========================================")

        for f in formats:

            print(

                "ID=",
                f.get("format_id"),

                "EXT=",
                f.get("ext"),

                "VCODEC=",
                f.get("vcodec"),

                "ACODEC=",
                f.get("acodec"),

                "RES=",
                f.get("resolution"),

                "ABR=",
                f.get("abr")

            )

        # ==================================================
        # 音声format
        # ==================================================

        print("==========================================")
        print("音声format一覧")
        print("==========================================")

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

        print("==========================================")

        print(
            "音声format数:",
            len(audio_formats)
        )

        print("==========================================")

        return info

    finally:

        remove_temp_cookie_file(
            temp_cookie
        )


# ==========================================================
# MP3変換
# ==========================================================

def download_mp3(
    url,
    output_dir
):

    print("==========================================")
    print("MP3ダウンロード開始")
    print("==========================================")

    ydl_opts = None
    temp_cookie = None

    try:

        ydl_opts, temp_cookie = get_ydl_base_options()

        ydl_opts.update({

            # --------------------------------------------------
            # 音声
            # --------------------------------------------------

            "format":
            "140/bestaudio/best",

            # --------------------------------------------------
            # 出力
            # --------------------------------------------------

            "outtmpl":
            os.path.join(
                output_dir,
                "%(title)s.%(ext)s"
            ),

            # --------------------------------------------------
            # MP3変換
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
            "140/bestaudio/best"
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
                + mp3_file
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

        remove_temp_cookie_file(
            temp_cookie
        )


# ==========================================================
# MP4変換
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

        ydl_opts, temp_cookie = get_ydl_base
```
