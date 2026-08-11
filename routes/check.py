from flask import request, jsonify
import yt_dlp
import os
import sys
import subprocess
import shutil
import tempfile


# ============================================================
# Cookieファイル
# ============================================================

# Render Secret File
RENDER_COOKIE_FILE = "/etc/secrets/cookies.txt"


# ============================================================
# プロジェクトルート
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# ローカルCookie
# ============================================================

LOCAL_COOKIE_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt"
)


# ============================================================
# Cookie元ファイル選択
# ============================================================

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


# ============================================================
# 実行環境診断
# ============================================================

def diagnose_environment():

    print("==========================================")
    print("実行環境診断")
    print("==========================================")

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------

    print(
        "RENDER:",
        os.environ.get("RENDER")
    )

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    print("------------------------------------------")
    print("Python version:")
    print(
        sys.version
    )

    print(
        "Python executable:",
        sys.executable
    )

    # --------------------------------------------------------
    # yt-dlp
    # --------------------------------------------------------

    print("------------------------------------------")
    print("yt-dlp version:")

    try:

        print(
            yt_dlp.version.__version__
        )

    except Exception as e:

        print(
            "取得失敗:",
            repr(e)
        )

    # --------------------------------------------------------
    # yt-dlp-ejs
    # --------------------------------------------------------

    print("------------------------------------------")
    print("yt-dlp-ejs:")

    try:

        import yt_dlp_ejs

        print(
            "インストール済み"
        )

        print(
            "version:",
            getattr(
                yt_dlp_ejs,
                "__version__",
                "不明"
            )
        )

    except Exception as e:

        print(
            "利用不可 / 未インストール"
        )

        print(
            "理由:",
            repr(e)
        )

    # --------------------------------------------------------
    # Deno
    # --------------------------------------------------------

    print("------------------------------------------")
    print("Deno:")

    try:

        result = subprocess.run(
            [
                "deno",
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(
            "returncode:",
            result.returncode
        )

        if result.stdout.strip():

            print(
                result.stdout.strip()
            )

        if result.stderr.strip():

            print(
                "stderr:",
                result.stderr.strip()
            )

    except Exception as e:

        print(
            "Deno確認失敗:",
            repr(e)
        )

    # --------------------------------------------------------
    # ffmpeg
    # --------------------------------------------------------

    print("------------------------------------------")
    print("ffmpeg:")

    try:

        result = subprocess.run(
            [
                "ffmpeg",
                "-version"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(
            "returncode:",
            result.returncode
        )

        if result.stdout.strip():

            lines = result.stdout.strip().splitlines()

            if lines:

                print(
                    lines[0]
                )

    except Exception as e:

        print(
            "ffmpeg確認失敗:",
            repr(e)
        )

    # --------------------------------------------------------
    # PATH
    # --------------------------------------------------------

    print("------------------------------------------")
    print("PATH:")

    print(
        os.environ.get(
            "PATH",
            ""
        )
    )

    print("==========================================")


# ============================================================
# 一時Cookieファイル作成
# ============================================================

def prepare_cookie_file():

    # --------------------------------------------------------
    # 元Cookie存在確認
    # --------------------------------------------------------

    if not os.path.exists(
        ORIGINAL_COOKIE_FILE
    ):

        raise Exception(
            "Cookieファイルが見つかりません: "
            + ORIGINAL_COOKIE_FILE
        )

    # --------------------------------------------------------
    # 元ファイルサイズ
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # /tmpに一時ファイル作成
    # --------------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".txt",
        prefix="y2conv_check_cookies_",
        delete=False
    )

    temp_cookie_file = temp_file.name

    temp_file.close()

    try:

        # ----------------------------------------------------
        # Cookieコピー
        # ----------------------------------------------------

        shutil.copyfile(
            ORIGINAL_COOKIE_FILE,
            temp_cookie_file
        )

        # ----------------------------------------------------
        # コピー確認
        # ----------------------------------------------------

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

            raise Exception(
                "一時Cookieファイルが空です"
            )

        # ====================================================
        # Cookie数確認
        # ====================================================

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

                    # ----------------------------------------
                    # Netscape Cookie形式
                    # ----------------------------------------

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

        # ----------------------------------------------------
        # 作成途中で失敗した場合も削除
        # ----------------------------------------------------

        try:

            if os.path.exists(
                temp_cookie_file
            ):

                os.remove(
                    temp_cookie_file
                )

        except Exception:

            pass

        raise


# ============================================================
# 一時Cookie削除
# ============================================================

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


# ============================================================
# YouTube情報取得
# ============================================================

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

        # ----------------------------------------------------
        # Cookie準備
        # ----------------------------------------------------

        temp_cookie = prepare_cookie_file()

        # ----------------------------------------------------
        # yt-dlp設定
        # ----------------------------------------------------

        ydl_opts = {

            # Cookie
            "cookiefile":
            temp_cookie,

            # EJS challenge solver
            "remote_components": {
                "ejs": "github"
            },

            # JavaScript runtime
            "js_runtimes": {
                "deno": {}
            },

            # Playlist無効
            "noplaylist":
            True,

            # ダウンロードしない
            "skip_download":
            True,

            # 詳細ログ
            "quiet":
            False,

            "no_warnings":
            False,

            "verbose":
            True

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
            temp_cookie
        )

        print(
            "EJS:",
            "github"
        )

        print(
            "JavaScript Runtime:",
            "deno"
        )

        print(
            "noplaylist:",
            True
        )

        print(
            "skip_download:",
            True
        )

        print(
            "format:",
            "指定なし"
        )

        print("==========================================")

        # ----------------------------------------------------
        # extract_info
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # 結果確認
        # ----------------------------------------------------

        if not info:

            raise Exception(
                "YouTube情報を取得できませんでした"
            )

        print("==========================================")
        print("extract_info成功")
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

        # ----------------------------------------------------
        # 一時Cookie削除
        # ----------------------------------------------------

        remove_cookie_file(
            temp_cookie
        )


# ============================================================
# Format診断
# ============================================================

def diagnose_formats(
    info
):

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
            "FPS=",
            f.get("fps"),
            "ABR=",
            f.get("abr"),
            "ASR=",
            f.get("asr"),
            "PROTO=",
            f.get("protocol")
        )

    print("==========================================")

    # ========================================================
    # 音声format
    # ========================================================

    audio_formats = []

    print("==========================================")
    print("音声format")
    print("==========================================")

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
                f.get("asr"),
                "PROTO=",
                f.get("protocol")
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

        vcodec = f.get(
            "vcodec"
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
                f.get("format_id"),
                "EXT=",
                f.get("ext"),
                "RES=",
                f.get("resolution"),
                "FPS=",
                f.get("fps"),
                "VCODEC=",
                f.get("vcodec"),
                "ACODEC=",
                f.get("acodec"),
                "PROTO=",
                f.get("protocol")
            )

    print("==========================================")

    print(
        "動画format数:",
        len(video_formats)
    )

    print("==========================================")

    # ========================================================
    # 代表format
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

def register_check(
    app
):

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
            # 実行環境診断
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
            # Cookie確認
            # =================================================

            # prepare_cookie_file() は
            # get_youtube_info() 内で実行するため、
            # ここでは直接Cookieを開かない

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
                str(e)

            })
