from flask import request, jsonify
import yt_dlp
import os
import tempfile


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
# Cookieファイル判定
# ==========================================

if os.path.exists(RENDER_COOKIE_FILE):

    COOKIE_FILE = RENDER_COOKIE_FILE

else:

    COOKIE_FILE = LOCAL_COOKIE_FILE


print(
    "使用するCookieファイル:",
    COOKIE_FILE
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
        COOKIE_FILE,
        file_size,
        "bytes"
    )


# ==========================================
# 一時Cookieファイル作成
#
# Render Secret File は
# 直接yt-dlpに渡すと問題になる場合があるため、
# /tmp にコピーして使用する
# ==========================================

def create_temp_cookie_file():

    check_cookie_file()

    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8"
    )

    temp_cookie_path = temp_file.name

    try:

        with open(
            COOKIE_FILE,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as source:

            for line in source:

                temp_file.write(line)

        temp_file.close()

        print(
            "一時Cookieファイル作成:",
            temp_cookie_path
        )

        return temp_cookie_path

    except Exception:

        temp_file.close()

        if os.path.exists(temp_cookie_path):

            os.remove(
                temp_cookie_path
            )

        raise


# ==========================================
# 時間フォーマット
# ==========================================

def format_duration(duration_sec):

    if not duration_sec:

        return "0:00"

    try:

        duration_sec = int(
            duration_sec
        )

    except Exception:

        return "0:00"

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


# ==========================================
# /check
#
# YouTube情報取得
# ==========================================

def register_check(app):

    @app.route(
        "/check",
        methods=["POST"]
    )
    def check():

        temp_cookie_path = None

        try:

            # ==========================================
            # JSON取得
            # ==========================================

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


            # ==========================================
            # URL
            # ==========================================

            url = data.get(
                "url"
            )


            if not url:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "YouTube URLを入力してください"

                }), 400


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


            # ==========================================
            # Cookie
            # ==========================================

            temp_cookie_path = create_temp_cookie_file()


            # ==========================================
            # yt-dlp設定
            #
            # 情報取得だけなので
            # skip_download=True
            #
            # formatを指定しない
            # ==========================================

            ydl_opts = {

                "quiet":
                False,

                "no_warnings":
                False,

                "skip_download":
                True,

                "noplaylist":
                True,

                "cookiefile":
                temp_cookie_path,

                "extract_flat":
                False,

                "ignoreerrors":
                False

            }


            # ==========================================
            # YouTube情報取得
            # ==========================================

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


            # ==========================================
            # タイトル
            # ==========================================

            title = info.get(
                "title"
            )


            if not title:

                title = "タイトル取得失敗"


            # ==========================================
            # 再生時間
            # ==========================================

            duration_sec = info.get(
                "duration"
            )


            duration = format_duration(
                duration_sec
            )


            # ==========================================
            # 基本情報ログ
            # ==========================================

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
                "動画ID:",
                info.get("id")
            )

            print(
                "=========================================="
            )


            # ==========================================
            # 成功
            # ==========================================

            return jsonify({

                "success":
                True,

                "filename":
                title,

                "title":
                title,

                "duration":
                duration,

                "duration_sec":
                duration_sec,

                "id":
                info.get("id")

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

            }), 200


        finally:

            # ==========================================
            # 一時Cookie削除
            # ==========================================

            if (
                temp_cookie_path
                and os.path.exists(
                    temp_cookie_path
                )
            ):

                try:

                    os.remove(
                        temp_cookie_path
                    )

                    print(
                        "一時Cookieファイル削除OK"
                    )

                except Exception as e:

                    print(
                        "一時Cookieファイル削除失敗:",
                        e
                    )
