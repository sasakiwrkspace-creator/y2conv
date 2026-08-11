from flask import request, jsonify
import yt_dlp
import os


# ============================================================
# Cookieファイル
# ============================================================

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


# ============================================================
# Render / ローカル判定
# ============================================================

if os.environ.get("RENDER") == "true":
    COOKIE_FILE = RENDER_COOKIE_FILE
else:
    COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("check.py 起動")
print("使用するCookieファイル:")
print(COOKIE_FILE)
print("==========================================")


# ============================================================
# Cookie確認
# ============================================================

def check_cookie_file():

    if not os.path.exists(COOKIE_FILE):

        raise Exception(
            f"Cookieファイルが見つかりません: {COOKIE_FILE}"
        )

    file_size = os.path.getsize(
        COOKIE_FILE
    )

    print("==========================================")
    print("Cookieファイル確認")
    print("==========================================")

    print(
        "Cookieファイル:",
        COOKIE_FILE
    )

    print(
        "Cookieファイルサイズ:",
        file_size,
        "bytes"
    )

    cookie_count = 0
    youtube_cookie_count = 0

    try:

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


# ============================================================
# YouTube情報取得
# ============================================================

def get_youtube_info(url):

    print("==========================================")
    print("YouTube情報取得開始")
    print("==========================================")

    print(
        "URL:",
        url
    )

    # --------------------------------------------------------
    # yt-dlp設定
    # --------------------------------------------------------

    ydl_opts = {

        # Cookie
        "cookiefile": COOKIE_FILE,

        # Playlist無効
        "noplaylist": True,

        # ダウンロードしない
        "skip_download": True,

        # 詳細ログ
        "quiet": False,

        "no_warnings": False,

        "verbose": True

    }

    print("==========================================")
    print("yt-dlp設定")
    print("==========================================")

    print(
        "Cookie:",
        COOKIE_FILE
    )

    print(
        "JavaScript Runtime:",
        "無効"
    )

    print(
        "Remote Components:",
        "無効"
    )

    print("==========================================")

    # --------------------------------------------------------
    # extract_info
    # --------------------------------------------------------

    try:

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

    except Exception as e:

        print("==========================================")
        print("YouTube情報取得失敗")
        print("==========================================")

        print(
            "ERROR:",
            repr(e)
        )

        print("==========================================")

        raise

    if not info:

        raise Exception(
            "YouTube情報を取得できませんでした"
        )

    return info


# ============================================================
# Format診断
# ============================================================

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

    # ========================================================
    # Format一覧
    # ========================================================

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

    # ========================================================
    # 音声format
    # ========================================================

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

        # 音声のみ
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

    # ========================================================
    # 動画format
    # ========================================================

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

    # ========================================================
    # 特定format確認
    # ========================================================

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

    # ========================================================
    # 結果
    # ========================================================

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

        "title":
        title,

        "duration":
        duration,

        "video_id":
        video_id,

        "format_count":
        len(formats),

        "audio_format_count":
        len(audio_formats),

        "video_format_count":
        len(video_formats),

        "has_140":
        format_140 is not None,

        "has_251":
        format_251 is not None,

        "has_249":
        format_249 is not None,

        "has_18":
        format_18 is not None

    }


# ============================================================
# /check
# ============================================================

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

            # =================================================
            # JSON
            # =================================================

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

            # =================================================
            # URL
            # =================================================

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
                "受信URL:",
                url
            )

            # =================================================
            # Cookie確認
            # =================================================

            check_cookie_file()

            # =================================================
            # YouTube情報取得
            # =================================================

            info = get_youtube_info(
                url
            )

            # =================================================
            # Format診断
            # =================================================

            diagnosis = diagnose_formats(
                info
            )

            # =================================================
            # タイトル
            # =================================================

            title = info.get(
                "title",
                "タイトル取得失敗"
            )

            # =================================================
            # 再生時間
            # =================================================

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

            # =================================================
            # 成功レスポンス
            # =================================================

            return jsonify({

                "success":
                True,

                "filename":
                title,

                "duration":
                duration,

                "video_id":
                diagnosis["video_id"],

                "format_count":
                diagnosis["format_count"],

                "audio_format_count":
                diagnosis["audio_format_count"],

                "video_format_count":
                diagnosis["video_format_count"],

                "has_140":
                diagnosis["has_140"],

                "has_251":
                diagnosis["has_251"],

                "has_249":
                diagnosis["has_249"],

                "has_18":
                diagnosis["has_18"]

            })

        except Exception as e:

            print("==========================================")
            print("/check エラー")
            print("==========================================")

            print(
                "ERROR:",
                repr(e)
            )

            print("==========================================")

            return jsonify({

                "success":
                False,

                "message":
                str(e)

            })
