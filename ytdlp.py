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
    os.access(
        DENO_PATH,
        os.X_OK
    ),
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
# Cookie準備
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

    if not os.path.isfile(
        COOKIES_SOURCE
    ):

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            +
            COOKIES_SOURCE
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

        print(
            "[DEBUG] 一時Cookie:",
            temporary_cookie_path,
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

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        "remote_components": {

            "ejs:github"

        }

    }

    if temporary_cookie_path:

        ydl_opts[
            "cookiefile"
        ] = temporary_cookie_path

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

    output_dir = _get_download_dir()

    temporary_cookie_path = None

    try:

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        ydl_opts = _build_ydl_options(

            output_dir=
                output_dir,

            format_string=
                "best",

            temporary_cookie_path=
                temporary_cookie_path

        )

        info = None

        expected_filename = None

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(

                url,

                download=False

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
                "[DEBUG] download_source download START",
                flush=True
            )

            ydl.download([
                url
            ])

            print(
                "[DEBUG] download_source download SUCCESS",
                flush=True
            )

        downloaded_file = None

        if expected_filename:

            expected_path = Path(
                expected_filename
            )

            if expected_path.is_file():

                downloaded_file = expected_path

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

        if downloaded_file is None:

            raise FileNotFoundError(
                "ダウンロードしたsourceファイルを確認できませんでした"
            )

        file_size = downloaded_file.stat().st_size

        if file_size <= 0:

            raise RuntimeError(
                "sourceファイルのサイズが0です"
            )

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "title":
                info.get("title")
                or "YouTube Video",

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

        if path.exists() and path.is_file():

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

            downloaded_file = prepared_path

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

                downloaded_file = merged_path

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

                downloaded_file = matches[0]

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

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "video_id":
                info.get("id"),

            "title":
                info.get("title")
                or "YouTube Video",

            "duration":
                info.get("duration"),

            "info":
                info

        }

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
