from flask import request, jsonify
import yt_dlp
import os
import shutil
import tempfile
import subprocess
import traceback


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


# ==========================================================
# Deno
#
# 固定パスではなく、PATHから検索する
#
# Dockerfile:
# ENV DENO_INSTALL=/app/.deno
# ENV PATH="/app/.deno/bin:${PATH}"
#
# したがって通常は:
# /app/.deno/bin/deno
# ==========================================================

def find_deno():

    # ------------------------------------------------------
    # 1. PATHから検索
    # ------------------------------------------------------

    deno_from_path = shutil.which(
        "deno"
    )

    if deno_from_path:

        return deno_from_path

    # ------------------------------------------------------
    # 2. Dockerfileで想定しているパス
    # ------------------------------------------------------

    candidates = [

        "/app/.deno/bin/deno",

        "/opt/render/project/src/.deno/bin/deno",

        os.path.expanduser(
            "~/.deno/bin/deno"
        )

    ]

    for candidate in candidates:

        if os.path.isfile(candidate):

            if os.access(
                candidate,
                os.X_OK
            ):

                return candidate

    return None


DENO_PATH = find_deno()


# ==========================================================
# 起動ログ
# ==========================================================

print(
    "==========================================",
    flush=True
)

print(
    "check.py 起動",
    flush=True
)

print(
    "Cookie設定",
    flush=True
)

print(
    "RENDER:",
    os.environ.get("RENDER"),
    flush=True
)

print(
    "元Cookieファイル:",
    ORIGINAL_COOKIE_FILE,
    flush=True
)

print(
    "==========================================",
    flush=True
)

print(
    "Deno確認",
    flush=True
)

print(
    "Deno PATH:",
    DENO_PATH,
    flush=True
)

print(
    "shutil.which('deno'):",
    shutil.which("deno"),
    flush=True
)

print(
    "PATH:",
    os.environ.get("PATH"),
    flush=True
)

print(
    "==========================================",
    flush=True
)


# ==========================================================
# 一時Cookieファイル削除
# ==========================================================

def remove_cookie_file(cookie_file):

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
                cookie_file,
                flush=True
            )

    except Exception as e:

        print(
            "WARNING: 一時Cookieファイル削除失敗:",
            repr(e),
            flush=True
        )


# ==========================================================
# Cookieファイル準備
#
# 元:
# /etc/secrets/cookies.txt
#
# ↓
#
# /tmp/y2conv_cookies_xxxxx.txt
#
# yt-dlpには/tmp側を渡す
# ==========================================================

def prepare_cookie_file():

    print(
        "==========================================",
        flush=True
    )

    print(
        "Cookieファイル準備開始",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    # ------------------------------------------------------
    # 元Cookie存在確認
    # ------------------------------------------------------

    if not os.path.isfile(
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

    print(
        "元Cookieファイル:",
        ORIGINAL_COOKIE_FILE,
        flush=True
    )

    print(
        "元Cookieサイズ:",
        original_size,
        "bytes",
        flush=True
    )

    if original_size == 0:

        raise Exception(
            "Cookieファイルが空です: "
            + ORIGINAL_COOKIE_FILE
        )

    # ------------------------------------------------------
    # 一時ファイル作成
    # ------------------------------------------------------

    temp_cookie_file = None

    try:

        fd, temp_cookie_file = tempfile.mkstemp(
            prefix="y2conv_cookies_",
            suffix=".txt",
            dir="/tmp"
        )

        os.close(
            fd
        )

        print(
            "一時Cookieファイル作成:",
            temp_cookie_file,
            flush=True
        )

        # --------------------------------------------------
        # コピー
        # --------------------------------------------------

        shutil.copyfile(
            ORIGINAL_COOKIE_FILE,
            temp_cookie_file
        )

    except Exception:

        remove_cookie_file(
            temp_cookie_file
        )

        raise

    # ------------------------------------------------------
    # コピー後確認
    # ------------------------------------------------------

    if not os.path.isfile(
        temp_cookie_file
    ):

        raise Exception(
            "一時Cookieファイルの作成に失敗しました: "
            + str(temp_cookie_file)
        )

    file_size = os.path.getsize(
        temp_cookie_file
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        "yt-dlp用Cookieファイル作成OK",
        flush=True
    )

    print(
        "一時Cookie:",
        temp_cookie_file,
        flush=True
    )

    print(
        "サイズ:",
        file_size,
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    if file_size == 0:

        remove_cookie_file(
            temp_cookie_file
        )

        raise Exception(
            "一時Cookieファイルが空です"
        )

    # ======================================================
    # Cookie内容確認
    # ======================================================

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

                fields = line.split(
                    "\t"
                )

                # Netscape cookie format
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

    print(
        "==========================================",
        flush=True
    )

    print(
        "Cookieデータ行数:",
        cookie_count,
        flush=True
    )

    print(
        "YouTube/Google Cookie数:",
        youtube_cookie_count,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    # ------------------------------------------------------
    # Cookie件数確認
    # ------------------------------------------------------

    if cookie_count == 0:

        remove_cookie_file(
            temp_cookie_file
        )

        raise Exception(
            "Cookieデータが0件です"
        )

    if youtube_cookie_count == 0:

        print(
            "WARNING: YouTube/Google Cookieが見つかりません",
            flush=True
        )

    print(
        "Cookie準備完了",
        flush=True
    )

    return temp_cookie_file


# ==========================================================
# Deno単体テスト
# ==========================================================

def test_deno():

    print(
        "==========================================",
        flush=True
    )

    print(
        "Deno単体テスト開始",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    # ------------------------------------------------------
    # Deno再検索
    # ------------------------------------------------------

    deno_path = find_deno()

    print(
        "Deno検出結果:",
        deno_path,
        flush=True
    )

    print(
        "shutil.which('deno'):",
        shutil.which("deno"),
        flush=True
    )

    print(
        "PATH:",
        os.environ.get("PATH"),
        flush=True
    )

    # ------------------------------------------------------
    # Denoがない
    # ------------------------------------------------------

    if not deno_path:

        print(
            "Denoが存在しません",
            flush=True
        )

        print(
            "Deno単体テスト失敗",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return False

    # ------------------------------------------------------
    # ファイル存在確認
    # ------------------------------------------------------

    if not os.path.isfile(
        deno_path
    ):

        print(
            "Denoファイルが存在しません:",
            deno_path,
            flush=True
        )

        return False

    # ------------------------------------------------------
    # 実行権限確認
    # ------------------------------------------------------

    if not os.access(
        deno_path,
        os.X_OK
    ):

        print(
            "Denoに実行権限がありません:",
            deno_path,
            flush=True
        )

        return False

    # ------------------------------------------------------
    # --version
    # ------------------------------------------------------

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
            "Deno returncode:",
            result.returncode,
            flush=True
        )

        print(
            "Deno stdout:",
            result.stdout.strip(),
            flush=True
        )

        print(
            "Deno stderr:",
            result.stderr.strip(),
            flush=True
        )

        if result.returncode == 0:

            print(
                "Deno単体テストOK",
                flush=True
            )

            print(
                "Deno実行ファイル:",
                deno_path,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            return True

        print(
            "Deno単体テスト失敗",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return False

    except subprocess.TimeoutExpired:

        print(
            "Deno単体テストTIMEOUT",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return False

    except Exception as e:

        print(
            "Deno単体テストエラー:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        print(
            "==========================================",
            flush=True
        )

        return False


# ==========================================================
# yt-dlp共通設定
# ==========================================================

def get_ydl_base_options():

    print(
        "==========================================",
        flush=True
    )

    print(
        "yt-dlp共通設定開始",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    cookie_file = None

    try:

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        cookie_file = prepare_cookie_file()

        # --------------------------------------------------
        # Deno確認
        # --------------------------------------------------

        deno_path = find_deno()

        print(
            "yt-dlp用Deno:",
            deno_path,
            flush=True
        )

        if not deno_path:

            raise Exception(
                "Denoが利用できません"
            )

        # --------------------------------------------------
        # Deno単体テスト
        # --------------------------------------------------

        deno_available = test_deno()

        if not deno_available:

            raise Exception(
                "Denoが正常に起動できません"
            )

        # --------------------------------------------------
        # yt-dlp設定
        # --------------------------------------------------

        ydl_opts = {

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
            # JavaScript Runtime
            # --------------------------------------------------

            "js_runtimes": {

                "deno": {

                    "path":
                    deno_path

                }

            },

            # --------------------------------------------------
            # EJS
            # --------------------------------------------------

            "remote_components": [

                "ejs:github"

            ]

        }

        print(
            "==========================================",
            flush=True
        )

        print(
            "yt-dlp設定",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        print(
            "Cookie:",
            cookie_file,
            flush=True
        )

        print(
            "Deno:",
            deno_path,
            flush=True
        )

        print(
            "EJS:",
            "ejs:github",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return ydl_opts

    except Exception:

        remove_cookie_file(
            cookie_file
        )

        raise


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(url):

    print(
        "==========================================",
        flush=True
    )

    print(
        "YouTube情報取得開始",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        "URL:",
        url,
        flush=True
    )

    print(
        "Python:",
        sys_version(),
        flush=True
    )

    print(
        "yt-dlp:",
        yt_dlp.version.__version__,
        flush=True
    )

    print(
        "Deno PATH:",
        find_deno(),
        flush=True
    )

    print(
        "ffmpeg:",
        shutil.which("ffmpeg"),
        flush=True
    )

    temp_cookie = None

    try:

        # ==================================================
        # yt-dlp設定
        # ==================================================

        ydl_opts = get_ydl_base_options()

        temp_cookie = ydl_opts.get(
            "cookiefile"
        )

        # ==================================================
        # 診断用設定
        # ==================================================

        ydl_opts.update({

            "skip_download":
            True,

            "quiet":
            False,

            "no_warnings":
            False,

            "verbose":
            True

        })

        print(
            "==========================================",
            flush=True
        )

        print(
            "yt-dlp設定確認",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        print(
            "Cookie:",
            temp_cookie,
            flush=True
        )

        print(
            "JavaScript Runtime:",
            ydl_opts.get(
                "js_runtimes"
            ),
            flush=True
        )

        print(
            "EJS:",
            ydl_opts.get(
                "remote_components"
            ),
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        # ==================================================
        # YoutubeDL
        # ==================================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "YoutubeDL作成開始",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                ">>> YoutubeDL作成完了",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            print(
                "extract_info開始",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            print(
                ">>> extract_info 実行直前",
                flush=True
            )

            try:

                info = ydl.extract_info(
                    url,
                    download=False
                )

            except Exception as e:

                print(
                    "==========================================",
                    flush=True
                )

                print(
                    "extract_info ERROR",
                    flush=True
                )

                print(
                    "==========================================",
                    flush=True
                )

                print(
                    "ERROR TYPE:",
                    type(e).__name__,
                    flush=True
                )

                print(
                    "ERROR:",
                    repr(e),
                    flush=True
                )

                print(
                    "==========================================",
                    flush=True
                )

                traceback.print_exc()

                raise

            print(
                ">>> extract_info 実行完了",
                flush=True
            )

        print(
            ">>> YoutubeDL終了",
            flush=True
        )

        # ==================================================
        # 結果確認
        # ==================================================

        if not info:

            raise Exception(
                "YouTube情報を取得できませんでした"
            )

        print(
            "==========================================",
            flush=True
        )

        print(
            "YouTube情報取得成功",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        print(
            "Video ID:",
            info.get("id"),
            flush=True
        )

        print(
            "タイトル:",
            info.get("title"),
            flush=True
        )

        print(
            "再生時間:",
            info.get("duration"),
            flush=True
        )

        print(
            "Extractor:",
            info.get("extractor"),
            flush=True
        )

        print(
            "Format数:",
            len(
                info.get(
                    "formats",
                    []
                )
            ),
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return info

    finally:

        print(
            "get_youtube_info終了処理",
            flush=True
        )

        remove_cookie_file(
            temp_cookie
        )


# ==========================================================
# Python version helper
# ==========================================================

def sys_version():

    import sys

    return sys.version


# ==========================================================
# Format診断
# ==========================================================

def diagnose_formats(info):

    print(
        "==========================================",
        flush=True
    )

    print(
        "FORMAT診断開始",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

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

    formats = info.get(
        "formats",
        []
    )

    print(
        "Video ID:",
        video_id,
        flush=True
    )

    print(
        "Extractor:",
        extractor,
        flush=True
    )

    print(
        "タイトル:",
        title,
        flush=True
    )

    print(
        "再生時間:",
        duration,
        "秒",
        flush=True
    )

    print(
        "利用可能format数:",
        len(formats),
        flush=True
    )

    # ======================================================
    # 音声
    # ======================================================

    audio_formats = []

    print(
        "==========================================",
        flush=True
    )

    print(
        "音声format",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

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
                "ID=", format_id,
                "EXT=", ext,
                "ACODEC=", acodec,
                "ABR=", abr,
                "ASR=", asr,
                "PROTO=", protocol,
                flush=True
            )

    print(
        "==========================================",
        flush=True
    )

    print(
        "音声format数:",
        len(audio_formats),
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    # ======================================================
    # 動画
    # ======================================================

    video_formats = []

    print(
        "==========================================",
        flush=True
    )

    print(
        "動画format",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

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
                "ID=", format_id,
                "EXT=", ext,
                "RES=", resolution,
                "FPS=", fps,
                "VCODEC=", vcodec,
                "ACODEC=", acodec,
                "PROTO=", protocol,
                flush=True
            )

    print(
        "==========================================",
        flush=True
    )

    print(
        "動画format数:",
        len(video_formats),
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    # ======================================================
    # 代表format
    # ======================================================

    format_140 = None
    format_251 = None
    format_249 = None
    format_18 = None

    for f in formats:

        format_id = str(
            f.get(
                "format_id"
            )
        )

        if format_id == "140":

            format_140 = f

        elif format_id == "251":

            format_251 = f

        elif format_id == "249":

            format_249 = f

        elif format_id == "18":

            format_18 = f

    print(
        "==========================================",
        flush=True
    )

    print(
        "代表format確認",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        "140:",
        "あり" if format_140 else "なし",
        flush=True
    )

    print(
        "251:",
        "あり" if format_251 else "なし",
        flush=True
    )

    print(
        "249:",
        "あり" if format_249 else "なし",
        flush=True
    )

    print(
        "18:",
        "あり" if format_18 else "なし",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    if len(audio_formats) == 0:

        print(
            "WARNING: 音声formatが取得できていません",
            flush=True
        )

    else:

        print(
            "OK: 音声formatを取得できています",
            flush=True
        )

    if len(video_formats) == 0:

        print(
            "WARNING: 動画formatが取得できていません",
            flush=True
        )

    else:

        print(
            "OK: 動画formatを取得できています",
            flush=True
        )

    print(
        "==========================================",
        flush=True
    )

    print(
        "FORMAT診断完了",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

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


# ==========================================================
# /video-info
#
# タブ1 YouTube Converter専用
#
# POST:
#
# {
#     "url": "https://www.youtube.com/watch?v=..."
# }
#
# Response:
#
# {
#     "success": true,
#     "title": "...",
#     "duration": 123
# }
# ==========================================================

def register_video_info(app):

    @app.route(
        "/video-info",
        methods=["POST"]
    )
    def video_info():

        print(
            "==========================================",
            flush=True
        )

        print(
            "/video-info 呼び出し",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        try:

            # ==================================================
            # JSON
            # ==================================================

            data = request.get_json(
                silent=True
            )

            if not data:

                print(
                    "/video-info JSONなし",
                    flush=True
                )

                return jsonify({

                    "success":
                    False,

                    "message":
                    "JSONデータがありません"

                }), 400

            # ==================================================
            # URL
            # ==================================================

            url = data.get(
                "url"
            )

            if not url:

                print(
                    "/video-info URLなし",
                    flush=True
                )

                return jsonify({

                    "success":
                    False,

                    "message":
                    "YouTube URLを入力してください"

                }), 400

            print(
                "/video-info 受信URL:",
                url,
                flush=True
            )

            # ==================================================
            # YouTube情報取得
            # ==================================================

            print(
                "==========================================",
                flush=True
            )

            print(
                "/video-info YouTube情報取得開始",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            info = get_youtube_info(
                url
            )

            # ==================================================
            # 情報確認
            # ==================================================

            if not info:

                raise Exception(
                    "YouTube情報を取得できませんでした"
                )

            title = info.get(
                "title"
            )

            duration = info.get(
                "duration"
            )

            video_id = info.get(
                "id"
            )

            # --------------------------------------------------
            # タイトル
            # --------------------------------------------------

            if not title:

                title = "不明"

            # --------------------------------------------------
            # duration
            # --------------------------------------------------

            if duration is None:

                duration = 0

            try:

                duration = int(
                    duration
                )

            except Exception:

                duration = 0

            # ==================================================
            # 完了ログ
            # ==================================================

            print(
                "==========================================",
                flush=True
            )

            print(
                "/video-info 正常完了",
                flush=True
            )

            print(
                "タイトル:",
                title,
                flush=True
            )

            print(
                "再生時間:",
                duration,
                flush=True
            )

            print(
                "Video ID:",
                video_id,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            # ==================================================
            # JSON
            # ==================================================

            return jsonify({

                "success":
                True,

                "title":
                title,

                "video_title":
                title,

                "duration":
                duration,

                "video_duration":
                duration,

                "video_id":
                video_id

            })

        except Exception as e:

            print(
                "==========================================",
                flush=True
            )

            print(
                "/video-info エラー",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            print(
                "ERROR TYPE:",
                type(e).__name__,
                flush=True
            )

            print(
                "ERROR:",
                repr(e),
                flush=True
            )

            traceback.print_exc()

            print(
                "==========================================",
                flush=True
            )

            return jsonify({

                "success":
                False,

                "message":
                str(e)

            }), 500


# ==========================================================
# /check
#
# 既存の診断用API
# ==========================================================

def register_check(app):

    @app.route(
        "/check",
        methods=["POST"]
    )
    def check():

        try:

            print(
                "==========================================",
                flush=True
            )

            print(
                "/check 呼び出し",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            # ==================================================
            # JSON
            # ==================================================

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

            # ==================================================
            # URL
            # ==================================================

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
                "受信URL:",
                url,
                flush=True
            )

            # ==================================================
            # Deno単体テスト
            # ==================================================

            print(
                "==========================================",
                flush=True
            )

            print(
                "/check Deno確認",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            deno_ok = test_deno()

            if not deno_ok:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "Denoが正常に起動できません"

                }), 500

            # ==================================================
            # YouTube情報取得
            # ==================================================

            print(
                "==========================================",
                flush=True
            )

            print(
                "/check YouTube情報取得開始",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            info = get_youtube_info(
                url
            )

            print(
                "==========================================",
                flush=True
            )

            print(
                "/check YouTube情報取得完了",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            # ==================================================
            # Format診断
            # ==================================================

            diagnosis = diagnose_formats(
                info
            )

            # ==================================================
            # 基本情報
            # ==================================================

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

            try:

                duration_sec = int(
                    duration_sec
                )

            except Exception:

                duration_sec = 0

            # ==================================================
            # 時間
            # ==================================================

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

            # ==================================================
            # 完了
            # ==================================================

            print(
                "==========================================",
                flush=True
            )

            print(
                "/check 正常完了",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

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

            print(
                "==========================================",
                flush=True
            )

            print(
                "/check エラー",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            print(
                "ERROR TYPE:",
                type(e).__name__,
                flush=True
            )

            print(
                "ERROR:",
                repr(e),
                flush=True
            )

            traceback.print_exc()

            print(
                "==========================================",
                flush=True
            )

            return jsonify({

                "success":
                False,

                "message":
                str(e)

            }), 500


# ==========================================================
# 実行環境確認
# ==========================================================

print(
    "==========================================",
    flush=True
)

print(
    "実行環境確認",
    flush=True
)

print(
    "==========================================",
    flush=True
)

import sys

print(
    "Python:",
    sys.version,
    flush=True
)

print(
    "Python executable:",
    sys.executable,
    flush=True
)

print(
    "yt-dlp:",
    yt_dlp.version.__version__,
    flush=True
)

print(
    "Deno:",
    find_deno(),
    flush=True
)

print(
    "Deno which:",
    shutil.which("deno"),
    flush=True
)

print(
    "ffmpeg:",
    shutil.which("ffmpeg"),
    flush=True
)

print(
    "ffprobe:",
    shutil.which("ffprobe"),
    flush=True
)

print(
    "PATH:",
    os.environ.get("PATH"),
    flush=True
)

print(
    "==========================================",
    flush=True
)
