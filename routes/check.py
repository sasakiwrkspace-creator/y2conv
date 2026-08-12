from flask import request, jsonify
import yt_dlp
import os
import shutil
import tempfile


# ==========================================================
# Cookieファイル設定
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

if os.environ.get("RENDER") == "true":
    ORIGINAL_COOKIE_FILE = RENDER_COOKIE_FILE
else:
    ORIGINAL_COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("check.py 起動")
print("Cookie設定")
print("RENDER:", os.environ.get("RENDER"))
print("元Cookieファイル:")
print(ORIGINAL_COOKIE_FILE)
print("==========================================")


# ==========================================================
# 一時Cookieファイル削除
# ==========================================================

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


# ==========================================================
# Cookieファイル準備
#
# Render:
# /etc/secrets/cookies.txt
#
# ↓ コピー
#
# /tmp/y2conv_cookies_xxxxx.txt
#
# yt-dlpには/tmp側を渡す
# ==========================================================

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
    print(
        "ファイル:",
        ORIGINAL_COOKIE_FILE
    )
    print(
        "サイズ:",
        original_size,
        "bytes"
    )
    print("==========================================")

    if original_size == 0:
        raise Exception(
            "Cookieファイルが空です: "
            + ORIGINAL_COOKIE_FILE
        )

    temp_file = tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".txt",
        prefix="y2conv_cookies_",
        delete=False
    )

    temp_cookie_file = temp_file.name

    temp_file.close()

    try:
        shutil.copyfile(
            ORIGINAL_COOKIE_FILE,
            temp_cookie_file
        )

    except Exception:
        remove_cookie_file(
            temp_cookie_file
        )
        raise

    if not os.path.exists(
        temp_cookie_file
    ):
        raise Exception(
            "一時Cookieファイルの作成に失敗しました: "
            + temp_cookie_file
        )

    file_size = os.path.getsize(
        temp_cookie_file
    )

    print("==========================================")
    print("yt-dlp用Cookieファイル作成OK")
    print(
        "一時Cookie:",
        temp_cookie_file
    )
    print(
        "サイズ:",
        file_size,
        "bytes"
    )
    print("==========================================")

    if file_size == 0:
        remove_cookie_file(
            temp_cookie_file
        )

        raise Exception(
            "一時Cookieファイルが空です"
        )

    cookie_count = 0
    youtube_cookie_count = 0

    try:
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

    except Exception as e:

        remove_cookie_file(
            temp_cookie_file
        )

        raise Exception(
            "Cookieファイルの読み込みに失敗しました: "
            + repr(e)
        )

    print("==========================================")
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

        remove_cookie_file(
            temp_cookie_file
        )

        raise Exception(
            "Cookieデータが0件です"
        )

    if youtube_cookie_count == 0:

        print(
            "WARNING: "
            "YouTube/Google Cookieが見つかりません"
        )

    return temp_cookie_file


# ==========================================================
# yt-dlp共通設定
# ==========================================================

def get_ydl_base_options():

    cookie_file = prepare_cookie_file()

    return {
        "cookiefile": cookie_file,
        "noplaylist": True,

        "js_runtimes": {
            "deno": {
                "path": "/opt/render/project/src/.deno/bin/deno"
            }
        },

        "remote_components": [
            "ejs:github"
        ]
    }

# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(url):

    print("Python:", os.sys.version)
    print("yt-dlp:", yt_dlp.version.__version__)
    print("Deno:", shutil.which("deno"))
    print("ffmpeg:", shutil.which("ffmpeg"))

    temp_cookie = None
    temp_cookie = None

    try:

        print("==========================================")
        print("YouTube情報取得開始")
        print("URL:", url)
        print("==========================================")

        ydl_opts = get_ydl_base_options()

        temp_cookie = ydl_opts.get(
            "cookiefile"
        )

        ydl_opts.update({
            "skip_download": True,
            "quiet": False,
            "no_warnings": False,
            "verbose": True
        })

        print("==========================================")
        print("yt-dlp設定")
        print("==========================================")

        print(
            "Cookie:",
            temp_cookie
        )

        print(
            "JavaScript Runtime:",
            "deno"
        )

        print(
            "EJS:",
            "github"
        )

        print("==========================================")

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:
        
            print("==========================================")
            print("extract_info開始")
            print("==========================================")
        
            print(">>> extract_info 実行直前")
        
            info = ydl.extract_info(
                url,
                download=False
            )
        
            print(">>> extract_info 実行完了")
        
        print(">>> YoutubeDL終了")

        if not info:

            raise Exception(
                "YouTube情報を取得できませんでした"
            )

        return info

    finally:

        remove_cookie_file(
            temp_cookie
        )


# ==========================================================
# Format診断
# ==========================================================

def diagnose_formats(info):

    print("==========================================")
    print("YouTube基本情報")
    print("==========================================")

    title = info.get(
        "title"
    )

    duration = info.get(
        "duration"
    )

    video_id = info.get(
        "id"
    )

    extractor = info.get(
        "extractor"
    )

    print(
        "Video ID:",
        video_id
    )

    print(
        "Extractor:",
        extractor
    )

    print(
        "タイトル:",
        title
    )

    print(
        "再生時間:",
        duration,
        "秒"
    )

    formats = info.get(
        "formats",
        []
    )

    print("==========================================")
    print("FORMAT診断")
    print("==========================================")

    print(
        "利用可能format数:",
        len(formats)
    )

    audio_formats = []

    print("==========================================")
    print("音声format")
    print("==========================================")

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

        asr = f.get(
            "asr"
        )

        protocol = f.get(
            "protocol"
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
                format_id,
                "EXT=",
                ext,
                "ACODEC=",
                acodec,
                "ABR=",
                abr,
                "ASR=",
                asr,
                "PROTO=",
                protocol
            )

    print("==========================================")
    print(
        "音声format数:",
        len(audio_formats)
    )
    print("==========================================")

    video_formats = []

    print("==========================================")
    print("動画format")
    print("==========================================")

    for f in formats:

        format_id = f.get(
            "format_id"
        )

        ext = f.get(
            "ext"
        )

        resolution = f.get(
            "resolution"
        )

        vcodec = f.get(
            "vcodec"
        )

        acodec = f.get(
            "acodec"
        )

        fps = f.get(
            "fps"
        )

        protocol = f.get(
            "protocol"
        )

        if (
            vcodec
            and vcodec != "none"
        ):

            video_formats.append(
                f
            )

            print(
                "VIDEO",
                "ID=",
                format_id,
                "EXT=",
                ext,
                "RES=",
                resolution,
                "FPS=",
                fps,
                "VCODEC=",
                vcodec,
                "ACODEC=",
                acodec,
                "PROTO=",
                protocol
            )

    print("==========================================")
    print(
        "動画format数:",
        len(video_formats)
    )
    print("==========================================")

    format_140 = None
    format_251 = None
    format_249 = None
    format_18 = None

    for f in formats:

        format_id = str(
            f.get("format_id")
        )

        if format_id == "140":
            format_140 = f

        elif format_id == "251":
            format_251 = f

        elif format_id == "249":
            format_249 = f

        elif format_id == "18":
            format_18 = f

    print("==========================================")
    print("代表format確認")
    print("==========================================")

    print(
        "140:",
        "あり" if format_140 else "なし"
    )

    print(
        "251:",
        "あり" if format_251 else "なし"
    )

    print(
        "249:",
        "あり" if format_249 else "なし"
    )

    print(
        "18:",
        "あり" if format_18 else "なし"
    )

    print("==========================================")

    if len(audio_formats) == 0:

        print(
            "WARNING: 音声formatが取得できていません"
        )

    else:

        print(
            "OK: 音声formatを取得できています"
        )

    if len(video_formats) == 0:

        print(
            "WARNING: 動画formatが取得できていません"
        )

    else:

        print(
            "OK: 動画formatを取得できています"
        )

    print("==========================================")

    return {
        "title": title,
        "duration": duration,
        "video_id": video_id,
        "format_count": len(formats),
        "audio_format_count": len(audio_formats),
        "video_format_count": len(video_formats),
        "has_140": format_140 is not None,
        "has_251": format_251 is not None,
        "has_249": format_249 is not None,
        "has_18": format_18 is not None
    }


# ==========================================================
# /check
# ==========================================================

def register_check(app):

    @app.route(
        "/check",
        methods=["POST"]
    )
    def check():

        try:

            print("==========================================")
            print("/check 呼び出し")
            print("==========================================")

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
                    "message": "YouTube URLを入力してください"
                })

            print(
                "受信URL:",
                url
            )

            info = get_youtube_info(
                url
            )

            diagnosis = diagnose_formats(
                info
            )

            title = info.get(
                "title",
                "タイトル取得失敗"
            )

            duration_sec = info.get(
                "duration",
                0
            )

            if duration_sec is None:
                duration_sec = 0

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

            return jsonify({
                "success": True,
                "filename": title,
                "duration": duration,
                "video_id": diagnosis["video_id"],
                "format_count": diagnosis["format_count"],
                "audio_format_count": diagnosis["audio_format_count"],
                "video_format_count": diagnosis["video_format_count"],
                "has_140": diagnosis["has_140"],
                "has_251": diagnosis["has_251"],
                "has_249": diagnosis["has_249"],
                "has_18": diagnosis["has_18"]
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


print("==========================================")
print("実行環境確認")
print("Python:", os.sys.version)
print("yt-dlp:", yt_dlp.version.__version__)
print("Deno:", shutil.which("deno"))
print("ffmpeg:", shutil.which("ffmpeg"))
print("==========================================")

