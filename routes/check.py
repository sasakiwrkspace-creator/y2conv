```python
from flask import request, jsonify
import yt_dlp
import os
import shutil
import tempfile
import subprocess
from urllib.parse import urlparse, parse_qs, unquote


# ==========================================================
# Cookieファイル
# ==========================================================

# Render Secret File
RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ==========================================================
# プロジェクトルート
#
# y2conv/
# ├── app.py
# ├── cookies.txt
# └── routes/
#     └── check.py
#
# check.py から2階層戻る
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
# Render / Local 判定
# ==========================================================

if os.environ.get("RENDER") == "true":
    ORIGINAL_COOKIE_FILE = RENDER_COOKIE_FILE
else:
    ORIGINAL_COOKIE_FILE = LOCAL_COOKIE_FILE


print("==========================================")
print("check.py 起動")
print("==========================================")
print(
    "RENDER:",
    os.environ.get("RENDER")
)
print(
    "元Cookieファイル:",
    ORIGINAL_COOKIE_FILE
)
print("==========================================")


# ==========================================================
# 環境診断
# ==========================================================

def diagnose_environment():

    print("==========================================")
    print("環境診断")
    print("==========================================")

    # ------------------------------------------------------
    # Python
    # ------------------------------------------------------

    print(
        "Python:",
        os.sys.version
    )

    # ------------------------------------------------------
    # yt-dlp
    # ------------------------------------------------------

    try:

        print(
            "yt-dlp version:",
            yt_dlp.version.__version__
        )

    except Exception as e:

        print(
            "yt-dlp version取得失敗:",
            repr(e)
        )

    # ------------------------------------------------------
    # yt-dlp-ejs
    # ------------------------------------------------------

    try:

        import yt_dlp_ejs

        print(
            "yt-dlp-ejs:",
            "インストール済み"
        )

        try:

            print(
                "yt-dlp-ejs version:",
                getattr(
                    yt_dlp_ejs,
                    "__version__",
                    "不明"
                )
            )

        except Exception:

            pass

    except Exception as e:

        print(
            "yt-dlp-ejs:",
            "未インストールまたは読み込み失敗"
        )

        print(
            "yt-dlp-ejs ERROR:",
            repr(e)
        )

    # ------------------------------------------------------
    # Deno
    # ------------------------------------------------------

    deno_path = shutil.which("deno")

    print(
        "Deno PATH:",
        deno_path
    )

    if deno_path:

        try:

            result = subprocess.run(

                [
                    deno_path,
                    "--version"
                ],

                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10

            )

            print(
                "Deno version:",
                result.stdout.strip()
            )

            if result.stderr.strip():

                print(
                    "Deno stderr:",
                    result.stderr.strip()
                )

        except Exception as e:

            print(
                "Deno version取得失敗:",
                repr(e)
            )

    else:

        print(
            "WARNING: DenoがPATH上にありません"
        )

    # ------------------------------------------------------
    # FFmpeg
    # ------------------------------------------------------

    ffmpeg_path = shutil.which("ffmpeg")

    print(
        "FFmpeg PATH:",
        ffmpeg_path
    )

    if ffmpeg_path:

        try:

            result = subprocess.run(

                [
                    ffmpeg_path,
                    "-version"
                ],

                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10

            )

            first_line = (
                result.stdout.splitlines()[0]
                if result.stdout
                else ""
            )

            print(
                "FFmpeg:",
                first_line
            )

        except Exception as e:

            print(
                "FFmpeg version取得失敗:",
                repr(e)
            )

    print("==========================================")


# ==========================================================
# Cookie確認・/tmpコピー
# ==========================================================

def prepare_cookie_file():

    # ------------------------------------------------------
    # 元Cookie存在確認
    # ------------------------------------------------------

    if not os.path.exists(
        ORIGINAL_COOKIE_FILE
    ):

        raise Exception(
            "Cookieファイルが見つかりません: "
            + ORIGINAL_COOKIE_FILE
        )

    # ------------------------------------------------------
    # 元Cookieサイズ
    # ------------------------------------------------------

    original_size = os.path.getsize(
        ORIGINAL_COOKIE_FILE
    )

    print("==========================================")
    print("元Cookieファイル確認")
    print("==========================================")

    print(
        "ファイル:",
        ORIGINAL_COOKIE_FILE
    )

    print(
        "サイズ:",
        original_size,
        "bytes"
    )

    if original_size == 0:

        raise Exception(
            "Cookieファイルが空です"
        )

    # ------------------------------------------------------
    # /tmpに一時ファイル作成
    # ------------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(

        mode="wb",

        prefix="y2conv_cookies_",

        suffix=".txt",

        delete=False

    )

    temp_cookie_file = temp_file.name

    temp_file.close()

    # ------------------------------------------------------
    # Cookieコピー
    # ------------------------------------------------------

    shutil.copyfile(

        ORIGINAL_COOKIE_FILE,

        temp_cookie_file

    )

    # ------------------------------------------------------
    # コピー確認
    # ------------------------------------------------------

    if not os.path.exists(
        temp_cookie_file
    ):

        raise Exception(
            "一時Cookieファイルの作成に失敗しました: "
            + temp_cookie_file
        )

    temp_size = os.path.getsize(
        temp_cookie_file
    )

    print("==========================================")
    print("yt-dlp用Cookieファイル作成")
    print("==========================================")

    print(
        "一時Cookie:",
        temp_cookie_file
    )

    print(
        "サイズ:",
        temp_size,
        "bytes"
    )

    if temp_size == 0:

        raise Exception(
            "一時Cookieファイルが空です"
        )

    # ------------------------------------------------------
    # Cookie行数診断
    # ------------------------------------------------------

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

        raise Exception(
            "Cookieファイル読み込み失敗: "
            + repr(e)
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
            "WARNING: YouTube/Google Cookieがありません"
        )

    return temp_cookie_file


# ==========================================================
# 一時Cookie削除
# ==========================================================

def remove_cookie_file(
    cookie_file
):

    if not cookie_file:
        return

    try:

        if os.path.exists(
            cookie_file
        ):

            os.remove(
                cookie_file
            )

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
# GoogleリダイレクトURLをYouTube URLへ変換
# ==========================================================

def normalize_youtube_url(
    url
):

    print("==========================================")
    print("URL診断")
    print("==========================================")

    print(
        "受信URL:",
        url
    )

    try:

        parsed = urlparse(
            url
        )

        host = (
            parsed.netloc
            .lower()
        )

        # --------------------------------------------------
        # Google URL
        # --------------------------------------------------

        if (
            "google.com" in host
            and parsed.path == "/url"
        ):

            query = parse_qs(
                parsed.query
            )

            target = query.get(
                "url"
            )

            if target:

                target_url = unquote(
                    target[0]
                )

                print(
                    "Googleリダイレクト検出"
                )

                print(
                    "内部URL:",
                    target_url
                )

                url = target_url

        # --------------------------------------------------
        # YouTube watch URL
        # --------------------------------------------------

        parsed = urlparse(
            url
        )

        host = (
            parsed.netloc
            .lower()
        )

        if (
            "youtube.com" in host
            and parsed.path == "/watch"
        ):

            query = parse_qs(
                parsed.query
            )

            video_id = query.get(
                "v"
            )

            if video_id:

                clean_url = (
                    "https://www.youtube.com/watch?v="
                    + video_id[0]
                )

                print(
                    "正規化後URL:",
                    clean_url
                )

                print("==========================================")

                return clean_url

        # --------------------------------------------------
        # youtu.be
        # --------------------------------------------------

        if "youtu.be" in host:

            video_id = (
                parsed.path
                .strip("/")
            )

            if video_id:

                clean_url = (
                    "https://www.youtube.com/watch?v="
                    + video_id
                )

                print(
                    "正規化後URL:",
                    clean_url
                )

                print("==========================================")

                return clean_url

    except Exception as e:

        print(
            "URL正規化失敗:",
            repr(e)
        )

    print(
        "URLはそのまま使用します"
    )

    print("==========================================")

    return url


# ==========================================================
# yt-dlp設定
# ==========================================================

def get_ydl_options(
    cookie_file
):

    options = {

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        "cookiefile":
        cookie_file,

        # --------------------------------------------------
        # Playlist無効
        # --------------------------------------------------

        "noplaylist":
        True,

        # --------------------------------------------------
        # ダウンロードしない
        # --------------------------------------------------

        "skip_download":
        True,

        # --------------------------------------------------
        # JavaScript Runtime
        # --------------------------------------------------

        "js_runtimes": {
            "deno": {}
        },

        # --------------------------------------------------
        # EJS
        # --------------------------------------------------

        "remote_components": {
            "ejs": "github"
        },

        # --------------------------------------------------
        # ログ
        # --------------------------------------------------

        "quiet":
        False,

        "no_warnings":
        False,

        "verbose":
        True

    }

    return options


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(
    url
):

    temp_cookie = None

    try:

        print("==========================================")
        print("YouTube情報取得開始")
        print("==========================================")

        print(
            "URL:",
            url
        )

        # --------------------------------------------------
        # URL正規化
        # --------------------------------------------------

        normalized_url = normalize_youtube_url(
            url
        )

        print(
            "yt-dlpへ渡すURL:",
            normalized_url
        )

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temp_cookie = prepare_cookie_file()

        # --------------------------------------------------
        # yt-dlp設定
        # --------------------------------------------------

        ydl_opts = get_ydl_options(
            temp_cookie
        )

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
            "EJS Remote Components:",
            "github"
        )

        print("==========================================")

        # --------------------------------------------------
        # extract_info
        # --------------------------------------------------

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                "extract_info開始"
            )

            info = ydl.extract_info(

                normalized_url,

                download=False

            )

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

def diagnose_formats(
    info
):

    print("==========================================")
    print("YouTube基本情報")
    print("==========================================")

    print(
        "Video ID:",
        info.get("id")
    )

    print(
        "Extractor:",
        info.get("extractor")
    )

    print(
        "タイトル:",
        info.get("title")
    )

    print(
        "再生時間:",
        info.get("duration"),
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

    print("==========================================")
    print("利用可能format一覧")
    print("==========================================")

    audio_formats = []
    video_formats = []

    for f in formats:

        format_id = f.get(
            "format_id"
        )

        ext = f.get(
            "ext"
        )

        vcodec = f.get(
            "vcodec"
        )

        acodec = f.get(
            "acodec"
        )

        resolution = f.get(
            "resolution"
        )

        abr = f.get(
            "abr"
        )

        asr = f.get(
            "asr"
        )

        fps = f.get(
            "fps"
        )

        protocol = f.get(
            "protocol"
        )

        print(
            "ID=",
            format_id,
            "EXT=",
            ext,
            "VCODEC=",
            vcodec,
            "ACODEC=",
            acodec,
            "RES=",
            resolution,
            "FPS=",
            fps,
            "ABR=",
            abr,
            "ASR=",
            asr,
            "PROTO=",
            protocol
        )

        # --------------------------------------------------
        # 音声のみ
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 動画
        # --------------------------------------------------

        if (
            vcodec
            and vcodec != "none"
        ):

            video_formats.append(
                f
            )

    print("==========================================")
    print(
        "音声format数:",
        len(audio_formats)
    )

    print(
        "動画format数:",
        len(video_formats)
    )

    print("==========================================")

    # ------------------------------------------------------
    # 音声format
    # ------------------------------------------------------

    print("音声format詳細")
    print("==========================================")

    for f in audio_formats:

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
            f.get("asr"),
            "PROTO=",
            f.get("protocol")
        )

    print("==========================================")

    # ------------------------------------------------------
    # 代表format
    # ------------------------------------------------------

    representative_ids = [
        "140",
        "249",
        "250",
        "251",
        "18",
        "22"
    ]

    representative = {}

    for format_id in representative_ids:

        found = None

        for f in formats:

            if str(
                f.get("format_id")
            ) == format_id:

                found = f
                break

        representative[
            format_id
        ] = found

        print(
            format_id + ":",
            "あり" if found else "なし"
        )

    print("==========================================")

    return {

        "video_id":
        info.get("id"),

        "title":
        info.get("title"),

        "duration":
        info.get("duration"),

        "extractor":
        info.get("extractor"),

        "format_count":
        len(formats),

        "audio_format_count":
        len(audio_formats),

        "video_format_count":
        len(video_formats),

        "has_140":
        representative["140"] is not None,

        "has_249":
        representative["249"] is not None,

        "has_250":
        representative["250"] is not None,

        "has_251":
        representative["251"] is not None,

        "has_18":
        representative["18"] is not None,

        "has_22":
        representative["22"] is not None

    }


# ==========================================================
# /check
# ==========================================================

def register_check(
    app
):

    @app.route(
        "/check",
        methods=["POST"]
    )
    def check():

        print("==========================================")
        print("/check 呼び出し")
        print("==========================================")

        try:

            # =================================================
            # 環境診断
            # =================================================

            diagnose_environment()

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
            # duration
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

            # =================================================
            # 成功
            # =================================================

            print("==========================================")
            print("/check 成功")
            print("==========================================")

            return jsonify({

                "success":
                True,

                "filename":
                diagnosis["title"],

                "duration":
                duration,

                "video_id":
                diagnosis["video_id"],

                "extractor":
                diagnosis["extractor"],

                "format_count":
                diagnosis["format_count"],

                "audio_format_count":
                diagnosis["audio_format_count"],

                "video_format_count":
                diagnosis["video_format_count"],

                "has_140":
                diagnosis["has_140"],

                "has_249":
                diagnosis["has_249"],

                "has_250":
                diagnosis["has_250"],

                "has_251":
                diagnosis["has_251"],

                "has_18":
                diagnosis["has_18"],

                "has_22":
                diagnosis["has_22"]

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

                "success":
                False,

                "message":
                str(e),

                "error_type":
                type(e).__name__

            })
```
