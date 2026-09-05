import sys
import os
import traceback
import shutil
import subprocess
import tempfile
import re

from pathlib import Path


# ==========================================================
# 起動時 DEBUG
# ==========================================================

print("==========================================", flush=True)
print("[DEBUG] ytdlp.py loaded", flush=True)
print("[DEBUG] Python:", sys.version, flush=True)
print("[DEBUG] Python executable:", sys.executable, flush=True)
print("[DEBUG] Current working directory:", os.getcwd(), flush=True)
print("[DEBUG] yt-dlp module loading...", flush=True)


# ==========================================================
# Deno
# ==========================================================

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)

print(
    "[DEBUG] DENO_PATH:",
    DENO_PATH,
    flush=True
)

print(
    "[DEBUG] PATH:",
    os.environ.get("PATH"),
    flush=True
)


# ==========================================================
# Cookie
# ==========================================================

COOKIES_SOURCE = "/etc/secrets/cookies.txt"

print(
    "[DEBUG] COOKIES_SOURCE:",
    COOKIES_SOURCE,
    flush=True
)

print(
    "[DEBUG] Cookie exists:",
    os.path.isfile(COOKIES_SOURCE),
    flush=True
)


# ==========================================================
# yt-dlp import
# ==========================================================

try:

    import yt_dlp

    print(
        "[DEBUG] yt_dlp imported",
        flush=True
    )

    print(
        "[DEBUG] yt_dlp version:",
        yt_dlp.version.__version__,
        flush=True
    )

    print(
        "[DEBUG] yt_dlp location:",
        yt_dlp.__file__,
        flush=True
    )

except Exception as e:

    print(
        "[DEBUG] yt_dlp import ERROR:",
        repr(e),
        flush=True
    )

    traceback.print_exc()

    raise


# ==========================================================
# yt-dlp-ejs確認
# ==========================================================

try:

    import yt_dlp_ejs

    print(
        "[DEBUG] yt_dlp_ejs imported",
        flush=True
    )

    print(
        "[DEBUG] yt_dlp_ejs location:",
        yt_dlp_ejs.__file__,
        flush=True
    )

except Exception as e:

    print(
        "[DEBUG] yt_dlp_ejs import ERROR:",
        repr(e),
        flush=True
    )

    traceback.print_exc()


# ==========================================================
# Deno確認
# ==========================================================

print(
    "[DEBUG] Deno configured path:",
    DENO_PATH,
    flush=True
)

print(
    "[DEBUG] Deno exists:",
    os.path.isfile(DENO_PATH),
    flush=True
)

print(
    "[DEBUG] Deno executable:",
    os.access(DENO_PATH, os.X_OK),
    flush=True
)

print(
    "[DEBUG] Deno which:",
    shutil.which("deno"),
    flush=True
)


if os.path.isfile(DENO_PATH):

    try:

        result = subprocess.run(
            [
                DENO_PATH,
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(
            "[DEBUG] deno returncode:",
            result.returncode,
            flush=True
        )

        print(
            "[DEBUG] deno stdout:",
            result.stdout,
            flush=True
        )

        print(
            "[DEBUG] deno stderr:",
            result.stderr,
            flush=True
        )

    except Exception as e:

        print(
            "[DEBUG] deno execution ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

else:

    print(
        "[DEBUG] Deno NOT FOUND:",
        DENO_PATH,
        flush=True
    )


# ==========================================================
# FFmpeg確認
# ==========================================================

print(
    "[DEBUG] ffmpeg path:",
    shutil.which("ffmpeg"),
    flush=True
)

print(
    "[DEBUG] ffprobe path:",
    shutil.which("ffprobe"),
    flush=True
)


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
        "[DEBUG] ffmpeg returncode:",
        result.returncode,
        flush=True
    )

    if result.stdout:

        print(
            "[DEBUG] ffmpeg version:",
            result.stdout.splitlines()[0],
            flush=True
        )

except Exception as e:

    print(
        "[DEBUG] ffmpeg execution ERROR:",
        repr(e),
        flush=True
    )


print("==========================================", flush=True)


# ==========================================================
# downloadsフォルダ
# ==========================================================

def _get_download_dir():

    download_dir = (
        Path(os.getcwd())
        /
        "downloads"
    )

    download_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return download_dir


# ==========================================================
# ファイル名安全化
# ==========================================================

def _sanitize_filename(title):

    if not title:

        title = "YouTube Video"

    title = str(
        title
    ).strip()

    title = re.sub(
        r"[\r\n\t]+",
        " ",
        title
    )

    title = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        title
    )

    title = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    title = title.rstrip(
        " ."
    )

    if not title:

        title = "YouTube Video"

    title = title[:180]

    title = title.rstrip(
        " ."
    )

    if not title:

        title = "YouTube Video"

    return title


# ==========================================================
# Cookie確認
# ==========================================================

def _validate_cookie_file():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[DEBUG] Cookie validation START",
        flush=True
    )

    cookie_path = Path(
        COOKIES_SOURCE
    )

    print(
        "[DEBUG] Cookie path:",
        cookie_path,
        flush=True
    )

    if not cookie_path.is_file():

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            +
            str(cookie_path)
        )

    size = cookie_path.stat().st_size

    print(
        "[DEBUG] Cookie size:",
        size,
        "bytes",
        flush=True
    )

    if size <= 0:

        raise RuntimeError(
            "Cookieファイルのサイズが0です: "
            +
            str(cookie_path)
        )

    # ------------------------------------------------------
    # Netscape形式確認
    # Cookieの値そのものはログに出さない
    # ------------------------------------------------------

    try:

        with open(
            cookie_path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:

            first_lines = []

            for _ in range(20):

                line = f.readline()

                if not line:

                    break

                first_lines.append(
                    line.rstrip("\r\n")
                )

        valid_header = any(
            line.strip()
            in (
                "# HTTP Cookie File",
                "# Netscape HTTP Cookie File"
            )
            for line in first_lines
        )

        print(
            "[DEBUG] Cookie Netscape header:",
            valid_header,
            flush=True
        )

        cookie_line_count = 0

        for line in first_lines:

            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith("#"):
                continue

            parts = stripped.split("\t")

            if len(parts) >= 7:

                cookie_line_count += 1

        print(
            "[DEBUG] Cookie sample entries:",
            cookie_line_count,
            flush=True
        )

        if not valid_header:

            print(
                "[DEBUG] WARNING: Cookie header "
                "is not standard Netscape format",
                flush=True
            )

    except Exception as e:

        print(
            "[DEBUG] Cookie read ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

    print(
        "[DEBUG] Cookie validation COMPLETE",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return str(
        cookie_path
    )


# ==========================================================
# Cookie準備
#
# 元Cookieを一時ファイルへコピーする。
# ==========================================================

def _prepare_cookie_file():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[DEBUG] Cookieファイル準備開始",
        flush=True
    )

    source_path = _validate_cookie_file()

    temporary_cookie_path = None

    try:

        source_size = os.path.getsize(
            source_path
        )

        print(
            "[DEBUG] 元Cookieサイズ:",
            source_size,
            "bytes",
            flush=True
        )

        if source_size <= 0:

            raise RuntimeError(
                "元Cookieファイルのサイズが0です。"
            )

        temporary_cookie_file = (
            tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=".txt",
                prefix="y2conv_cookies_",
                delete=False
            )
        )

        temporary_cookie_path = (
            temporary_cookie_file.name
        )

        temporary_cookie_file.close()

        shutil.copyfile(
            source_path,
            temporary_cookie_path
        )

        copied_size = os.path.getsize(
            temporary_cookie_path
        )

        print(
            "[DEBUG] 元Cookie:",
            source_path,
            flush=True
        )

        print(
            "[DEBUG] 一時Cookie:",
            temporary_cookie_path,
            flush=True
        )

        print(
            "[DEBUG] 一時Cookieサイズ:",
            copied_size,
            "bytes",
            flush=True
        )

        if copied_size <= 0:

            raise RuntimeError(
                "一時Cookieファイルのサイズが0です。"
            )

        return temporary_cookie_path

    except Exception as e:

        print(
            "[DEBUG] Cookie preparation ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

            except Exception:

                pass

        raise

    finally:

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# yt-dlpオプション
# ==========================================================

def _build_ydl_options(
    output_dir,
    format_string,
    temporary_cookie_path=None
):

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    download_template = str(
        output_dir
        /
        "%(id)s.%(ext)s"
    )

    ydl_opts = {

        # --------------------------------------------------
        # 出力
        # --------------------------------------------------

        "outtmpl":
            download_template,

        # --------------------------------------------------
        # フォーマット
        # --------------------------------------------------

        "format":
            format_string,

        # --------------------------------------------------
        # Playlist禁止
        # --------------------------------------------------

        "noplaylist":
            True,

        # --------------------------------------------------
        # ログ
        # --------------------------------------------------

        "quiet":
            False,

        "no_warnings":
            False,

        "verbose":
            True,

        # --------------------------------------------------
        # HTTP
        # --------------------------------------------------

        "http_headers": {

            "User-Agent":
                (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131.0.0.0 "
                    "Safari/537.36"
                ),

            "Accept-Language":
                "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"

        },

        # --------------------------------------------------
        # EJS
        # --------------------------------------------------

        "remote_components": {
            "ejs:github"
        }

    }

    # ======================================================
    # Deno
    # ======================================================

    if (
        DENO_PATH
        and
        os.path.isfile(DENO_PATH)
        and
        os.access(DENO_PATH, os.X_OK)
    ):

        ydl_opts[
            "js_runtimes"
        ] = {

            "deno": {

                "path":
                    DENO_PATH

            }

        }

        print(
            "[DEBUG] Deno runtime ENABLED:",
            DENO_PATH,
            flush=True
        )

    else:

        ydl_opts[
            "js_runtimes"
        ] = {}

        print(
            "[DEBUG] Deno runtime DISABLED",
            flush=True
        )

    # ======================================================
    # Cookie
    # ======================================================

    if temporary_cookie_path:

        cookie_path = Path(
            temporary_cookie_path
        )

        if not cookie_path.is_file():

            raise FileNotFoundError(
                "一時Cookieファイルが存在しません: "
                +
                str(cookie_path)
            )

        cookie_size = cookie_path.stat().st_size

        if cookie_size <= 0:

            raise RuntimeError(
                "一時Cookieファイルのサイズが0です。"
            )

        ydl_opts[
            "cookiefile"
        ] = str(
            cookie_path
        )

    # ======================================================
    # DEBUG
    # ======================================================

    print(
        "[DEBUG] yt-dlp format:",
        format_string,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp output:",
        download_template,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp Deno:",
        ydl_opts.get("js_runtimes"),
        flush=True
    )

    print(
        "[DEBUG] yt-dlp cookie:",
        temporary_cookie_path,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp cookie enabled:",
        bool(
            ydl_opts.get(
                "cookiefile"
            )
        ),
        flush=True
    )

    print(
        "[DEBUG] yt-dlp EJS:",
        ydl_opts.get(
            "remote_components"
        ),
        flush=True
    )

    return ydl_opts


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(url):

    temporary_cookie_path = None

    try:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[DEBUG] get_youtube_info START",
            flush=True
        )

        print(
            "[DEBUG] URL:",
            url,
            flush=True
        )

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        # --------------------------------------------------
        # Options
        # --------------------------------------------------

        ydl_opts = _build_ydl_options(

            output_dir=
                _get_download_dir(),

            format_string=
                "bestaudio/best",

            temporary_cookie_path=
                temporary_cookie_path

        )

        print(
            "[DEBUG] get_youtube_info extract START",
            flush=True
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        if not info:

            raise RuntimeError(
                "YouTube情報を取得できませんでした"
            )

        print(
            "[INFO] Video ID:",
            info.get("id"),
            flush=True
        )

        print(
            "[INFO] Title:",
            info.get("title"),
            flush=True
        )

        print(
            "[INFO] Duration:",
            info.get("duration"),
            flush=True
        )

        print(
            "[INFO] Extractor:",
            info.get("extractor"),
            flush=True
        )

        print(
            "[INFO] Format count:",
            len(
                info.get("formats") or []
            ),
            flush=True
        )

        print(
            "[DEBUG] get_youtube_info SUCCESS",
            flush=True
        )

        return info

    except Exception as e:

        print(
            "[DEBUG] get_youtube_info ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

                    print(
                        "[DEBUG] 一時Cookieファイル削除OK:",
                        temporary_cookie_path,
                        flush=True
                    )

            except Exception as e:

                print(
                    "[DEBUG] 一時Cookie削除ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            "[DEBUG] get_youtube_info END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# YouTube → source
#
# MP3用途
# ==========================================================

def download_source(url):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[DEBUG] download_source START",
        flush=True
    )

    print(
        "[DEBUG] URL:",
        url,
        flush=True
    )

    if not url:

        raise ValueError(
            "YouTube URLが空です"
        )

    output_dir = _get_download_dir()

    temporary_cookie_path = None

    try:

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        # --------------------------------------------------
        # MP3用途なので音声優先
        # --------------------------------------------------

        ydl_opts = _build_ydl_options(

            output_dir=
                output_dir,

            format_string=
                "bestaudio/best",

            temporary_cookie_path=
                temporary_cookie_path

        )

        info = None

        expected_filename = None

        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                "[DEBUG] download_source extract/download START",
                flush=True
            )

            # --------------------------------------------------
            # ここで一度だけ extract_info(download=True)
            #
            # 以前のコードでは
            #
            # extract_info(download=False)
            # ↓
            # ydl.download()
            #
            # と二重にYouTubeへアクセスしていた。
            #
            # --------------------------------------------------

            info = ydl.extract_info(
                url,
                download=True
            )

            if info is None:

                raise RuntimeError(
                    "YouTube情報を取得できませんでした"
                )

            print(
                "[DEBUG] source video id:",
                info.get("id"),
                flush=True
            )

            print(
                "[DEBUG] source title:",
                info.get("title"),
                flush=True
            )

            print(
                "[DEBUG] source duration:",
                info.get("duration"),
                flush=True
            )

            print(
                "[DEBUG] source extractor:",
                info.get("extractor"),
                flush=True
            )

            expected_filename = (
                ydl.prepare_filename(
                    info
                )
            )

            print(
                "[DEBUG] expected filename:",
                expected_filename,
                flush=True
            )

            print(
                "[DEBUG] download_source download SUCCESS",
                flush=True
            )

        # ======================================================
        # ダウンロードファイル検索
        # ======================================================

        downloaded_file = None

        # ------------------------------------------------------
        # 1. prepare_filename
        # ------------------------------------------------------

        if expected_filename:

            expected_path = Path(
                expected_filename
            )

            if expected_path.is_file():

                downloaded_file = (
                    expected_path
                )

                print(
                    "[DEBUG] expected file found:",
                    downloaded_file,
                    flush=True
                )

        # ------------------------------------------------------
        # 2. ID検索
        # ------------------------------------------------------

        if downloaded_file is None:

            video_id = info.get(
                "id"
            )

            if video_id:

                possible_files = []

                for path in output_dir.glob(
                    video_id + ".*"
                ):

                    if not path.is_file():
                        continue

                    if path.suffix.lower() in (
                        ".part",
                        ".ytdl",
                        ".temp"
                    ):
                        continue

                    try:

                        size = path.stat().st_size

                    except Exception:

                        size = 0

                    if size <= 0:
                        continue

                    possible_files.append(
                        path
                    )

                if possible_files:

                    possible_files.sort(
                        key=lambda p:
                            p.stat().st_mtime,
                        reverse=True
                    )

                    downloaded_file = (
                        possible_files[0]
                    )

                    print(
                        "[DEBUG] ID search file found:",
                        downloaded_file,
                        flush=True
                    )

        # ------------------------------------------------------
        # 3. 最終確認
        # ------------------------------------------------------

        if downloaded_file is None:

            raise FileNotFoundError(
                "ダウンロードしたsourceファイルを"
                "確認できませんでした"
            )

        file_size = (
            downloaded_file.stat().st_size
        )

        if file_size <= 0:

            raise RuntimeError(
                "sourceファイルのサイズが0です"
            )

        print(
            "[DEBUG] downloaded source:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] downloaded source size:",
            file_size,
            "bytes",
            flush=True
        )

        # ======================================================
        # 結果
        # ======================================================

        result = {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "title":
                info.get("title")
                or
                "YouTube Video",

            "duration":
                info.get("duration"),

            "video_id":
                info.get("id"),

            "info":
                info

        }

        print(
            "[DEBUG] download_source RESULT:",
            {
                "path":
                    result["path"],

                "filename":
                    result["filename"],

                "title":
                    result["title"],

                "duration":
                    result["duration"],

                "video_id":
                    result["video_id"]

            },
            flush=True
        )

        print(
            "[DEBUG] download_source COMPLETE",
            flush=True
        )

        return result

    except Exception as e:

        print(
            "[DEBUG] download_source ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

                    print(
                        "[DEBUG] 一時Cookieファイル削除OK:",
                        temporary_cookie_path,
                        flush=True
                    )

            except Exception as e:

                print(
                    "[DEBUG] 一時Cookie削除ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            "[DEBUG] download_source END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# Cookieを使ったYouTube接続テスト
# ==========================================================

def test_youtube_cookie(url):

    temporary_cookie_path = None

    try:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[TEST] YouTube Cookie test START",
            flush=True
        )

        print(
            "[TEST] URL:",
            url,
            flush=True
        )

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        print(
            "[TEST] temporary cookie:",
            temporary_cookie_path,
            flush=True
        )

        # --------------------------------------------------
        # Options
        # --------------------------------------------------

        ydl_opts = _build_ydl_options(

            output_dir=
                _get_download_dir(),

            format_string=
                "bestaudio/best",

            temporary_cookie_path=
                temporary_cookie_path

        )

        print(
            "[TEST] extract_info START",
            flush=True
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        if not info:

            raise RuntimeError(
                "YouTube情報を取得できませんでした"
            )

        print(
            "[TEST] ==========================================",
            flush=True
        )

        print(
            "[TEST] SUCCESS",
            flush=True
        )

        print(
            "[TEST] ID:",
            info.get("id"),
            flush=True
        )

        print(
            "[TEST] TITLE:",
            info.get("title"),
            flush=True
        )

        print(
            "[TEST] DURATION:",
            info.get("duration"),
            flush=True
        )

        print(
            "[TEST] FORMAT COUNT:",
            len(
                info.get("formats") or []
            ),
            flush=True
        )

        print(
            "[TEST] ==========================================",
            flush=True
        )

        return info

    except Exception as e:

        print(
            "[TEST] ==========================================",
            flush=True
        )

        print(
            "[TEST] ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        print(
            "[TEST] ==========================================",
            flush=True
        )

        raise

    finally:

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

                    print(
                        "[TEST] temporary cookie removed",
                        flush=True
                    )

            except Exception as e:

                print(
                    "[TEST] temporary cookie remove ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            "[TEST] YouTube Cookie test END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# source削除
# ==========================================================

def cleanup_download(download_result):

    if not download_result:

        return

    source_path = (

        download_result.get("path")

        if isinstance(
            download_result,
            dict
        )

        else None

    )

    if not source_path:

        return

    try:

        path = Path(
            source_path
        )

        if (
            path.exists()
            and
            path.is_file()
        ):

            path.unlink()

            print(
                "[DEBUG] source removed:",
                path,
                flush=True
            )

    except Exception as e:

        print(
            "[DEBUG] cleanup_download ERROR:",
            repr(e),
            flush=True
        )


# ==========================================================
# 後方互換
# ==========================================================

def _download_with_ytdlp(
    url,
    output_dir,
    format_string,
    merge_output_format=None,
    mode_name="UNKNOWN"
):

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_cookie_path = None

    try:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[DEBUG]",
            mode_name,
            "START",
            flush=True
        )

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        ydl_opts = _build_ydl_options(

            output_dir=
                output_dir,

            format_string=
                format_string,

            temporary_cookie_path=
                temporary_cookie_path

        )

        if merge_output_format:

            ydl_opts[
                "merge_output_format"
            ] = merge_output_format

        print(
            "[DEBUG]",
            mode_name,
            "download START",
            flush=True
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            if not info:

                raise RuntimeError(
                    f"{mode_name} "
                    "extract_info() returned None"
                )

            prepared_filename = (
                ydl.prepare_filename(
                    info
                )
            )

        prepared_path = Path(
            prepared_filename
        )

        downloaded_file = None

        # --------------------------------------------------
        # prepare_filename
        # --------------------------------------------------

        if prepared_path.is_file():

            downloaded_file = (
                prepared_path
            )

            print(
                "[DEBUG]",
                mode_name,
                "prepared file found:",
                downloaded_file,
                flush=True
            )

        # --------------------------------------------------
        # merged file
        # --------------------------------------------------

        if (
            downloaded_file is None
            and
            merge_output_format
        ):

            merged_path = (

                output_dir
                /
                f"{info.get('id')}."
                f"{merge_output_format}"

            )

            if merged_path.is_file():

                downloaded_file = (
                    merged_path
                )

                print(
                    "[DEBUG]",
                    mode_name,
                    "merged file found:",
                    downloaded_file,
                    flush=True
                )

        # --------------------------------------------------
        # ID検索
        # --------------------------------------------------

        if downloaded_file is None:

            video_id = info.get(
                "id"
            )

            if video_id:

                matches = list(
                    output_dir.glob(
                        f"{video_id}.*"
                    )
                )

                matches = [

                    p

                    for p in matches

                    if p.is_file()

                    and

                    p.suffix.lower()
                    not in (
                        ".part",
                        ".ytdl",
                        ".temp"
                    )

                ]

                if matches:

                    matches.sort(
                        key=lambda p:
                            p.stat().st_mtime,
                        reverse=True
                    )

                    downloaded_file = (
                        matches[0]
                    )

        # --------------------------------------------------
        # 最終確認
        # --------------------------------------------------

        if downloaded_file is None:

            raise FileNotFoundError(
                f"{mode_name} "
                "ダウンロードファイルが見つかりません"
            )

        file_size = (
            downloaded_file.stat().st_size
        )

        if file_size <= 0:

            raise RuntimeError(
                f"{mode_name} "
                "ファイルサイズが0です"
            )

        print(
            "[DEBUG]",
            mode_name,
            "download COMPLETE:",
            downloaded_file,
            flush=True
        )

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "video_id":
                info.get("id"),

            "title":
                info.get("title")
                or
                "YouTube Video",

            "duration":
                info.get("duration"),

            "info":
                info

        }

    except Exception as e:

        print(
            "[DEBUG] _download_with_ytdlp ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

                    print(
                        "[DEBUG] 一時Cookieファイル削除OK:",
                        temporary_cookie_path,
                        flush=True
                    )

            except Exception as e:

                print(
                    "[DEBUG] 一時Cookie削除ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            "[DEBUG] _download_with_ytdlp END:",
            mode_name,
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )
