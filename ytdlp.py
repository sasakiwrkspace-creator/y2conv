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

        first_line = (
            result.stdout.splitlines()[0]
        )

        print(
            "[DEBUG] ffmpeg version:",
            first_line,
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
# 共通：downloadsフォルダ
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
# 共通：ファイル名安全化
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
# 共通：動画タイトルからファイル名生成
# ==========================================================

def _make_output_filename(
    title,
    extension
):

    safe_title = _sanitize_filename(
        title
    )

    return (
        f"{safe_title}.{extension}"
    )


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

    cookies_source = COOKIES_SOURCE

    print(
        "[DEBUG] 元Cookieファイル:",
        cookies_source,
        flush=True
    )

    exists = os.path.isfile(
        cookies_source
    )

    print(
        "[DEBUG] Cookie exists:",
        exists,
        flush=True
    )

    if not exists:

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            +
            cookies_source
        )

    temporary_cookie_path = None

    try:

        cookie_size = os.path.getsize(
            cookies_source
        )

        print(
            "[DEBUG] 元Cookieサイズ:",
            cookie_size,
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

            cookies_source,

            temporary_cookie_path

        )

        temporary_size = os.path.getsize(
            temporary_cookie_path
        )

        print(
            "[DEBUG] 一時Cookieファイル作成:",
            temporary_cookie_path,
            flush=True
        )

        print(
            "[DEBUG] 一時Cookieサイズ:",
            temporary_size,
            "bytes",
            flush=True
        )

        if temporary_size <= 0:

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
# yt-dlp共通オプション作成
#
# 重要：
#
# ytdlp.py / ytdlp_stream.py の両方で
# この設定を利用する。
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

        # ==================================================
        # EJS challenge scripts
        # ==================================================

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
        "[DEBUG] Deno exists:",
        os.path.isfile(
            DENO_PATH
        ),
        flush=True
    )

    print(
        "[DEBUG] cookiefile:",
        temporary_cookie_path,
        flush=True
    )

    print(
        "[DEBUG] remote_components:",
        ydl_opts.get(
            "remote_components"
        ),
        flush=True
    )

    print(
        "[DEBUG] js_runtimes:",
        ydl_opts.get(
            "js_runtimes"
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

    print(
        "==========================================",
        flush=True
    )

    print(
        "[DEBUG] YouTube情報取得開始",
        flush=True
    )

    print(
        "[DEBUG] URL:",
        url,
        flush=True
    )

    temporary_cookie_path = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        if not os.path.isfile(
            DENO_PATH
        ):

            raise RuntimeError(
                "Denoが利用できません: "
                +
                DENO_PATH
            )

        if not os.access(
            DENO_PATH,
            os.X_OK
        ):

            raise RuntimeError(
                "Denoに実行権限がありません: "
                +
                DENO_PATH
            )

        deno_result = subprocess.run(

            [
                DENO_PATH,
                "--version"
            ],

            capture_output=True,

            text=True,

            timeout=10

        )

        if deno_result.returncode != 0:

            raise RuntimeError(
                "Denoの実行に失敗しました"
            )

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        output_dir = (
            _get_download_dir()
        )

        ydl_opts = _build_ydl_options(

            output_dir=
                output_dir,

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

        print(
            "[DEBUG] get_youtube_info終了",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# YouTube → 一時ファイル
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

            print(
                "[DEBUG] download_source extract_info",
                flush=True
            )

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

            try:

                expected_filename = (
                    ydl.prepare_filename(
                        info
                    )
                )

            except Exception as e:

                print(
                    "[DEBUG] prepare_filename ERROR:",
                    repr(e),
                    flush=True
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

                downloaded_file = (
                    expected_path
                )

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

                        size = (
                            path.stat().st_size
                        )

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
                "YouTubeからダウンロードした"
                "sourceファイルを確認できませんでした"
            )

        file_size = (
            downloaded_file.stat().st_size
        )

        if file_size <= 0:

            raise RuntimeError(
                "ダウンロードされたsourceファイル"
                "のサイズが0です"
            )

        title = (
            info.get("title")
            or "YouTube Video"
        )

        duration = (
            info.get("duration")
        )

        result = {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "title":
                title,

            "duration":
                duration,

            "video_id":
                info.get("id"),

            "info":
                info

        }

        print(
            "[DEBUG] download_source COMPLETE",
            flush=True
        )

        print(
            "[DEBUG] source path:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] source size:",
            file_size,
            "bytes",
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
                        "[DEBUG] temporary cookie removed",
                        flush=True
                    )

            except Exception as e:

                print(
                    "[DEBUG] temporary cookie remove ERROR:",
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
# 一時ダウンロードファイル削除
# ==========================================================

def cleanup_download(
    download_result
):

    print(
        "[DEBUG] cleanup_download START",
        flush=True
    )

    if not download_result:

        print(
            "[DEBUG] cleanup_download: result empty",
            flush=True
        )

        return

    source_path = (
        download_result.get(
            "path"
        )
        if isinstance(
            download_result,
            dict
        )
        else None
    )

    if not source_path:

        print(
            "[DEBUG] cleanup_download: path empty",
            flush=True
        )

        return

    try:

        path = Path(
            source_path
        )

        if path.exists() and path.is_file():

            print(
                "[DEBUG] removing source:",
                path,
                flush=True
            )

            path.unlink()

            print(
                "[DEBUG] source removed",
                flush=True
            )

    except Exception as e:

        print(
            "[DEBUG] cleanup_download ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

    print(
        "[DEBUG] cleanup_download END",
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

    print(
        "==========================================",
        flush=True
    )

    print(
        f"[DEBUG] _download_with_ytdlp START [{mode_name}]",
        flush=True
    )

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
                    f"{mode_name} "
                    "extract_info() returned None"
                )

            print(
                f"[DEBUG] [{mode_name}] video id:",
                info.get("id"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] title:",
                info.get("title"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] duration:",
                info.get("duration"),
                flush=True
            )

            try:

                expected_filename = (
                    ydl.prepare_filename(
                        info
                    )
                )

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] "
                    "prepare_filename ERROR:",
                    repr(e),
                    flush=True
                )

            print(
                f"[DEBUG] [{mode_name}] download START",
                flush=True
            )

            ydl.download([
                url
            ])

            print(
                f"[DEBUG] [{mode_name}] download SUCCESS",
                flush=True
            )

        downloaded_file = None

        if expected_filename:

            expected_path = Path(
                expected_filename
            )

            if expected_path.is_file():

                downloaded_file = (
                    expected_path
                )

        if (
            downloaded_file is None
            and
            merge_output_format
            and
            info
        ):

            video_id = info.get(
                "id"
            )

            if video_id:

                merged_path = (

                    output_dir
                    /
                    f"{video_id}."
                    f"{merge_output_format}"

                )

                if merged_path.is_file():

                    downloaded_file = (
                        merged_path
                    )

        if (
            downloaded_file is None
            and
            info
        ):

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

                        size = (
                            path.stat().st_size
                        )

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
                f"{mode_name}"
                "ダウンロードファイルを"
                "確認できませんでした"
            )

        file_size = (
            downloaded_file.stat().st_size
        )

        if file_size <= 0:

            raise RuntimeError(
                f"{mode_name}"
                "ファイルのサイズが0です"
            )

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "video_id":
                info.get("id")
                if info
                else None,

            "title":
                info.get("title")
                if info
                else "",

            "duration":
                info.get("duration")
                if info
                else None,

            "info":
                info

        }

    except Exception as e:

        print(
            f"[DEBUG] "
            f"_download_with_ytdlp ERROR "
            f"[{mode_name}]:",
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
