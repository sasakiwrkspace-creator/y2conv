from flask import request, jsonify
import os
import sys
import shutil
import tempfile
import subprocess
import urllib.request
import zipfile

import yt_dlp


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

if os.environ.get("RENDER") == "true":
    ORIGINAL_COOKIE_FILE = RENDER_COOKIE_FILE
else:
    ORIGINAL_COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("check.py 起動")
print("==========================================")
print("Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("使用するCookieファイル:")
print(ORIGINAL_COOKIE_FILE)
print("==========================================")


def remove_cookie_file(cookie_file):
    if not cookie_file:
        return

    try:
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
            print(
                "一時Cookieファイル削除OK:",
                cookie_file
            )
    except Exception as e:
        print(
            "一時Cookieファイル削除失敗:",
            repr(e)
        )


def find_deno():
    deno = shutil.which("deno")

    if deno:
        return deno

    tmp_deno = os.path.join(
        tempfile.gettempdir(),
        "y2conv_deno",
        "deno"
    )

    if os.path.exists(tmp_deno):
        try:
            os.chmod(tmp_deno, 0o755)
        except Exception:
            pass

        try:
            result = subprocess.run(
                [
                    tmp_deno,
                    "--version"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return tmp_deno

        except Exception:
            pass

    return None


def prepare_deno():
    deno = find_deno()

    if deno:
        print("Deno確認OK:")
        print(deno)
        return deno

    print("Denoが見つかりません")
    print("Render用Denoを/tmpへ準備します")

    deno_dir = os.path.join(
        tempfile.gettempdir(),
        "y2conv_deno"
    )

    os.makedirs(
        deno_dir,
        exist_ok=True
    )

    deno_path = os.path.join(
        deno_dir,
        "deno"
    )

    zip_path = os.path.join(
        deno_dir,
        "deno.zip"
    )

    download_url = (
        "https://github.com/denoland/deno/releases/latest/"
        "download/deno-x86_64-unknown-linux-gnu.zip"
    )

    try:

        print("Denoダウンロード開始")
        print("保存先:", deno_path)

        urllib.request.urlretrieve(
            download_url,
            zip_path
        )

        print("Denoダウンロード完了")

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as z:

            z.extractall(
                deno_dir
            )

        if not os.path.exists(
            deno_path
        ):

            raise Exception(
                "Deno実行ファイルが見つかりません"
            )

        os.chmod(
            deno_path,
            0o755
        )

        result = subprocess.run(
            [
                deno_path,
                "--version"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )

        print("Deno確認結果:")
        print(result.stdout)

        if result.returncode != 0:
            raise Exception(
                result.stderr
            )

        return deno_path

    except Exception as e:

        print(
            "Deno準備失敗:",
            repr(e)
        )

        return None

    finally:

        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception:
            pass


def prepare_cookie_file():

    if not os.path.exists(
        ORIGINAL_COOKIE_FILE
    ):

        raise Exception(
            "Cookieファイルが見つかりません: "
            + ORIGINAL_COOKIE_FILE
        )

    original_size = os.path.getsize(
        ORIGINAL_COOKIE_FILE
    )

    print("==========================================")
    print("元Cookieファイル確認OK")
    print("ファイル:", ORIGINAL_COOKIE_FILE)
    print("サイズ:", original_size, "bytes")
    print("==========================================")

    if original_size == 0:

        raise Exception(
            "Cookieファイルが空です: "
            + ORIGINAL_COOKIE_FILE
        )

    temp_file = tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".txt",
        prefix="y2conv_check_cookies_",
        delete=False
    )

    temp_cookie_file = temp_file.name
    temp_file.close()

    try:

        shutil.copyfile(
            ORIGINAL_COOKIE_FILE,
            temp_cookie_file
        )

        file_size = os.path.getsize(
            temp_cookie_file
        )

        if file_size == 0:

            raise Exception(
                "一時Cookieファイルが空です"
            )

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

                fields = line.split("\t")

                if len(fields) >= 7:

                    cookie_count += 1

                    domain = fields[0].lower()

                    if (
                        "youtube.com" in domain
                        or "google.com" in domain
                    ):

                        youtube_cookie_count += 1

                else:

                    cookie_count += 1

        print("==========================================")
        print("yt-dlp用Cookieファイル作成OK")
        print("一時Cookie:", temp_cookie_file)
        print("サイズ:", file_size, "bytes")
        print("Cookieデータ行数:", cookie_count)
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

        return temp_cookie_file

    except Exception:

        remove_cookie_file(
            temp_cookie_file
        )

        raise


def get_ydl_options():

    cookie_file = prepare_cookie_file()

    deno = prepare_deno()

    options = {

        "cookiefile":
        cookie_file,

        "noplaylist":
        True,

        "quiet":
        False,

        "no_warnings":
        False,

        "verbose":
        True,

        "skip_download":
        True,

        "remote_components":
        {
            "ejs:github"
        }

    }

    if deno:

        options["js_runtimes"] = {
            "deno": deno
        }

    print("==========================================")
    print("yt-dlp設定")
    print("==========================================")
    print(
        "yt-dlp version:",
        yt_dlp.version.__version__
    )
    print(
        "Cookie:",
        cookie_file
    )
    print(
        "EJS:",
        "ejs:github"
    )
    print(
        "Deno:",
        deno if deno else "利用不可"
    )
    print(
        "noplaylist:",
        True
    )
    print(
        "skip_download:",
        True
    )
    print("==========================================")

    return options


def diagnose_formats(url):

    temp_cookie = None

    try:

        print("==========================================")
        print("YouTube情報取得開始")
        print("==========================================")
        print("URL:", url)
        print("==========================================")

        ydl_opts = get_ydl_options()

        temp_cookie = ydl_opts.get(
            "cookiefile"
        )

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

        print("==========================================")
        print("YouTube情報取得成功")
        print("==========================================")
        print(
            "動画タイトル:",
            info.get("title")
        )
        print(
            "再生時間:",
            info.get("duration"),
            "秒"
        )
        print(
            "動画ID:",
            info.get("id")
        )
        print("==========================================")

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

        print("==========================================")

        return info

    except Exception as e:

        print("==========================================")
        print("YouTube情報取得失敗")
        print("==========================================")
        print(
            "ERROR TYPE:",
            type(e).__name__
        )
        print(
            "ERROR:",
            repr(e)
        )
        print("==========================================")

        raise

    finally:

        remove_cookie_file(
            temp_cookie
        )


def register_check(app):

    @app.route(
        "/check",
        methods=["POST"]
    )
    def check():

        print("==========================================")
        print("/check 呼び出し")
        print("==========================================")

        try:

            data = request.get_json(
                silent=True
            )

            if not data:

                return jsonify({
                    "success": False,
                    "message": "JSONデータがありません"
                })

            url = data.get(
                "url"
            )

            if not url:

                return jsonify({
                    "success": False,
                    "message": "URLがありません"
                })

            print("==========================================")
            print("受信URL:", url)
            print("==========================================")

            info = diagnose_formats(
                url
            )

            return jsonify({
                "success": True,
                "title": info.get("title"),
                "duration": info.get("duration"),
                "id": info.get("id")
            })

        except Exception as e:

            print("==========================================")
            print("/check エラー")
            print("==========================================")
            print(
                "ERROR TYPE:",
                type(e).__name__
            )
            print(
                "ERROR:",
                repr(e)
            )
            print("==========================================")

            return jsonify({
                "success": False,
                "message": str(e)
            })
