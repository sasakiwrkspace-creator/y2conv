from flask import request, jsonify
import yt_dlp
import os
import shutil
import tempfile


# ==========================================
# Cookieファイル
# ==========================================

RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"
LOCAL_COOKIE_FILE = "cookies.txt"


if os.path.exists(RENDER_COOKIE_FILE):

    COOKIE_FILE = RENDER_COOKIE_FILE

else:

    COOKIE_FILE = LOCAL_COOKIE_FILE


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
        f"Cookieファイル確認OK: "
        f"{COOKIE_FILE}, "
        f"{file_size} bytes"
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


            if not line:

                continue


            if line.startswith("#"):

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
# 書き込み可能なCookieファイルを作成
# ==========================================

def create_temp_cookie_file():

    if not os.path.exists(COOKIE_FILE):

        raise Exception(
            f"Cookieファイルが見つかりません: {COOKIE_FILE}"
        )


    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        prefix="ytcookies_",
        delete=False,
        encoding="utf-8"
    )


    temp_cookie_file = temp_file.name


    temp_file.close()


    shutil.copyfile(
        COOKIE_FILE,
        temp_cookie_file
    )


    print(
        "一時Cookieファイル作成:",
        temp_cookie_file
    )


    return temp_cookie_file


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

            # ==========================================
            # URL取得
            # ==========================================

            data = request.get_json()


            if not data:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "リクエストデータがありません"

                })


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


            # ==========================================
            # Cookie確認
            # ==========================================

            check_cookie_file()


            # ==========================================
            # Secret Fileを/tmpへコピー
            # ==========================================

            temp_cookie_file = (
                create_temp_cookie_file()
            )


            print(
                "YouTube情報取得開始:",
                url
            )


            # ==========================================
            # yt-dlp
            # ==========================================

            ydl_opts = {

                "quiet":
                True,

                "no_warnings":
                False,

                "skip_download":
                True,

                # 書き込み可能な一時Cookie
                "cookiefile":
                temp_cookie_file,

                # YouTube JS challenge
                "js_runtimes": {
                    "deno": {}
                }

            }


            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False
                )


            # ==========================================
            # タイトル
            # ==========================================

            title = info.get(
                "title",
                "タイトル取得失敗"
            )


            # ==========================================
            # 再生時間
            # ==========================================

            duration_sec = info.get(
                "duration",
                0
            )


            if not duration_sec:

                duration_sec = 0


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


            # ==========================================
            # 成功
            # ==========================================

            print(
                "YouTube情報取得成功:",
                title,
                duration
            )


            return jsonify({

                "success":
                True,

                "filename":
                title,

                "duration":
                duration

            })


        except Exception as e:

            print(
                "check error:",
                e
            )


            return jsonify({

                "success":
                False,

                "message":
                str(e)

            })


        finally:

            # ==========================================
            # 一時Cookie削除
            # ==========================================

            if (
                temp_cookie_file
                and os.path.exists(temp_cookie_file)
            ):

                try:

                    os.remove(
                        temp_cookie_file
                    )


                    print(
                        "一時Cookieファイル削除OK"
                    )

                except Exception as cleanup_error:

                    print(
                        "一時Cookie削除失敗:",
                        cleanup_error
                    )
