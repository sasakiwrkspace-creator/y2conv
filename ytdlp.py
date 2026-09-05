import sys
import os
import traceback
import shutil
import subprocess
import tempfile
import re

from pathlib import Path


# ==========================================================
# config
# ==========================================================

try:

    from config import (
        COOKIES_FILE,
        DENO_PATH as CONFIG_DENO_PATH
    )

except Exception as e:

    print(
        "[DEBUG] config import ERROR:",
        repr(e),
        flush=True
    )

    traceback.print_exc()

    raise


# ==========================================================
# 起動時 DEBUG
# ==========================================================

print(
    "==========================================",
    flush=True
)

print(
    "[DEBUG] ytdlp.py loaded",
    flush=True
)

print(
    "[DEBUG] Python:",
    sys.version,
    flush=True
)

print(
    "[DEBUG] Python executable:",
    sys.executable,
    flush=True
)

print(
    "[DEBUG] Current working directory:",
    os.getcwd(),
    flush=True
)

print(
    "[DEBUG] yt-dlp module loading...",
    flush=True
)


# ==========================================================
# Deno PATH
#
# config.py の設定を使用。
#
# config.py 側で shutil.which("deno") を使用しているため、
# Render環境のPATHに存在するDenoを利用する。
# ==========================================================

DENO_PATH = (
    CONFIG_DENO_PATH
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
#
# config.py の COOKIES_FILE を使用。
# ==========================================================

COOKIES_SOURCE = (
    COOKIES_FILE
)

print(
    "[DEBUG] COOKIES_SOURCE:",
    COOKIES_SOURCE,
    flush=True
)

print(
    "[DEBUG] COOKIES_SOURCE exists:",
    os.path.isfile(
        COOKIES_SOURCE
    ),
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
    bool(
        DENO_PATH
        and
        os.path.isfile(
            DENO_PATH
        )
    ),
    flush=True
)

print(
    "[DEBUG] Deno executable:",
    bool(
        DENO_PATH
        and
        os.access(
            DENO_PATH,
            os.X_OK
        )
    ),
    flush=True
)

print(
    "[DEBUG] Deno which:",
    shutil.which("deno"),
    flush=True
)


if (
    DENO_PATH
    and
    os.path.isfile(DENO_PATH)
):

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


print(
    "==========================================",
    flush=True
)


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

def _sanitize_filename(
    title
):

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
# Cookie準備
#
# Render Secret File:
#
# /etc/secrets/cookies.txt
#
# を一時ファイルへコピーしてyt-dlpへ渡す。
#
# Cookieの内容そのものはログへ出さない。
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

    print(
        "[DEBUG] 元Cookieファイル:",
        COOKIES_SOURCE,
        flush=True
    )

    if not COOKIES_SOURCE:

        raise RuntimeError(
            "COOKIES_FILE が設定されていません。"
        )

    if not os.path.isfile(
        COOKIES_SOURCE
    ):

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            +
            str(COOKIES_SOURCE)
        )

    temporary_cookie_path = None

    try:

        source_size = os.path.getsize(
            COOKIES_SOURCE
        )

        print(
            "[DEBUG] 元Cookieサイズ:",
            source_size,
            "bytes",
            flush=True
        )

        if source_size <= 0:

            raise RuntimeError(
                "Cookieファイルのサイズが0です: "
                +
                str(COOKIES_SOURCE)
            )

        # ==================================================
        # Cookieのデータ行数確認
        #
        # 内容そのものは出力しない。
        # ==================================================

        cookie_data_lines = 0

        try:

            with open(
                COOKIES_SOURCE,
                "r",
                encoding="utf-8",
                errors="replace"
            ) as cookie_file:

                for line in cookie_file:

                    stripped = line.strip()

                    if not stripped:
                        continue

                    if stripped.startswith("#"):
                        continue

                    cookie_data_lines += 1

        except Exception as e:

            print(
                "[DEBUG] Cookie line check ERROR:",
                repr(e),
                flush=True
            )

        print(
            "[DEBUG] Cookie data lines:",
            cookie_data_lines,
            flush=True
        )

        if cookie_data_lines <= 0:

            raise RuntimeError(
                "CookieファイルにCookieデータがありません。"
            )

        # ==================================================
        # 一時Cookie
        # ==================================================

        temporary_cookie_file = (
            tempfile.NamedTemporaryFile(
                mode="w",
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
            COOKIES_SOURCE,
            temporary_cookie_path
        )

        copied_size = os.path.getsize(
            temporary_cookie_path
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

        # ==================================================
        # 権限確認
        # ==================================================

        if not os.access(
            temporary_cookie_path,
            os.R_OK
        ):

            raise RuntimeError(
                "一時Cookieファイルを読み込めません。"
            )

        print(
            "[DEBUG] Cookie準備完了",
            flush=True
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

    download_template = str(
        Path(output_dir)
        /
        "%(id)s.%(ext)s"
    )

    ydl_opts = {

        "outtmpl":
            download_template,

        "format":
            format_string,

        "noplaylist":
            True,

        "quiet":
            False,

        "no_warnings":
            False,

        "verbose":
            True,

        # ==================================================
        # YouTube JavaScript challenge
        # ==================================================

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        "remote_components": {

            "ejs:github"

        },

        # ==================================================
        # YouTube HTTP headers
        # ==================================================

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

        }

    }

    # ======================================================
    # Cookie
    # ======================================================

    if temporary_cookie_path:

        ydl_opts[
            "cookiefile"
        ] = temporary_cookie_path

    else:

        print(
            "[DEBUG] WARNING: cookiefile is NOT configured",
            flush=True
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
        DENO_PATH,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp cookie:",
        temporary_cookie_path,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp cookie exists:",
        bool(
            temporary_cookie_path
            and
            os.path.isfile(
                temporary_cookie_path
            )
        ),
        flush=True
    )

    return ydl_opts


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(
    url
):

    temporary_cookie_path = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

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

            except Exception:

                pass


# ==========================================================
# YouTube → source
#
# MP3用途なので、
# bestaudio/best を使用。
#
# extract_info()を1回だけ実行して
# download=Trueで取得する。
# ==========================================================

def download_source(
    url
):

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

    output_dir = (
        _get_download_dir()
    )

    temporary_cookie_path = None

    try:

        # ==================================================
        # Cookie
        # ==================================================

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        # ==================================================
        # yt-dlp options
        # ==================================================

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

        # ==================================================
        # yt-dlp
        # ==================================================

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                "[DEBUG] download_source extract/download START",
                flush=True
            )

            # ==================================================
            # 1回だけextract_info
            # ==================================================

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

        # ==================================================
        # ダウンロード済みファイル確認
        # ==================================================

        downloaded_file = None

        if expected_filename:

            expected_path = Path(
                expected_filename
            )

            if expected_path.is_file():

                downloaded_file = (
                    expected_path
                )

        # ==================================================
        # IDから検索
        # ==================================================

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

        # ==================================================
        # 見つからない
        # ==================================================

        if downloaded_file is None:

            raise FileNotFoundError(
                "ダウンロードしたsourceファイルを確認できませんでした"
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

        return {

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

            except Exception:

                pass

        print(
            "[DEBUG] download_source END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# source削除
# ==========================================================

def cleanup_download(
    download_result
):

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

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                "[DEBUG] _download_with_ytdlp START:",
                mode_name,
                flush=True
            )

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

        if prepared_path.is_file():

            downloaded_file = (
                prepared_path
            )

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

        if downloaded_file is None:

            video_id = info.get(
                "id"
            )

            matches = list(
                output_dir.glob(
                    f"{video_id}.*"
                )
            )

            matches = [

                p for p in matches

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

        if downloaded_file is None:

            raise FileNotFoundError(
                f"{mode_name} "
                "ダウンロードファイルが見つかりません"
            )

        if downloaded_file.stat().st_size <= 0:

            raise RuntimeError(
                f"{mode_name} "
                "ファイルサイズが0です"
            )

        print(
            "[DEBUG] _download_with_ytdlp COMPLETE:",
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

            except Exception:

                pass
