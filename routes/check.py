from flask import request, jsonify
import yt_dlp
import os
import tempfile
import shutil


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
# yt-dlpがCookieを扱う際の問題を避けるため
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

    print(
        "Cookieファイルサイズ:",
        os.path.getsize(source),
        "bytes"
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
# YouTube情報取得
# =========================================================

def get_youtube_info(url, cookie_file):

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

    ydl_opts = {

        # -----------------------------------------
        # ダウンロードしない
        # -----------------------------------------

        "skip_download": True,

        # -----------------------------------------
        # Cookie
        # -----------------------------------------

        "cookiefile":
        cookie_file,

        # -----------------------------------------
        # Playlist無効
        # -----------------------------------------

        "noplaylist":
        True,

        # -----------------------------------------
        # 情報取得
        # -----------------------------------------

        "extract_flat":
        False,

        # -----------------------------------------
        # エラーを通常のExceptionとして取得
        # -----------------------------------------

        "ignoreerrors":
        False,

        # -----------------------------------------
        # ログを見やすくする
        # -----------------------------------------

        "quiet":
        False,

        "no_warnings":
        False,

        # -----------------------------------------
        # YouTube client
        #
        # webを優先
        # -----------------------------------------

        "extractor_args": {

            "youtube": {

                "player_client": [
                    "web"
                ]

            }

        }

    }

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
# /check
# =========================================================

def register_check(app):

    @app.route(
        "/check",
        methods=["POST"]
    )

    def check():

        temp_cookie = None

        try:

            # =====================================
            # JSON
            # =====================================

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


            # =====================================
            # URL
            # =====================================

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


            # =====================================
            # Cookie
            # =====================================

            temp_cookie = create_temp_cookie()


            # =====================================
            # YouTube情報取得
            # =====================================

            info = get_youtube_info(
                url,
                temp_cookie
            )


            # =====================================
            # タイトル
            # =====================================

            title = info.get(
                "title"
            )

            if not title:

                title = "タイトル取得失敗"


            # =====================================
            # 再生時間
            # =====================================

            duration_sec = info.get(
                "duration"
            )

            duration = format_duration(
                duration_sec
            )


            # =====================================
            # 結果
            # =====================================

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
                "=========================================="
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
                str(e)

            })


        finally:

            # =====================================
            # 一時Cookie削除
            # =====================================

            remove_temp_cookie(
                temp_cookie
            )

