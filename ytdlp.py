import sys
import os
import traceback
import shutil
import subprocess
import tempfile
import re
import uuid

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
# Deno PATH
# ==========================================================

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)

print("[DEBUG] DENO_PATH:", DENO_PATH, flush=True)
print("[DEBUG] PATH:", os.environ.get("PATH"), flush=True)


# ==========================================================
# yt-dlp import
# ==========================================================

try:

    import yt_dlp

    print("[DEBUG] yt_dlp imported", flush=True)
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

except Exception as error:

    print(
        "[DEBUG] yt_dlp import ERROR:",
        repr(error),
        flush=True
    )

    traceback.print_exc()

    raise


# ==========================================================
# yt-dlp-ejs確認
# ==========================================================

try:

    import yt_dlp_ejs

    print("[DEBUG] yt_dlp_ejs imported", flush=True)
    print(
        "[DEBUG] yt_dlp_ejs location:",
        yt_dlp_ejs.__file__,
        flush=True
    )

except Exception as error:

    print(
        "[DEBUG] yt_dlp_ejs import ERROR:",
        repr(error),
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


if not os.path.isfile(DENO_PATH):

    print(
        "[DEBUG] Deno NOT FOUND:",
        DENO_PATH,
        flush=True
    )

else:

    try:

        result = subprocess.run(
            [
                DENO_PATH,
                "--version"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10
        )

        print(
            "[DEBUG] deno returncode:",
            result.returncode,
            flush=True
        )

    except Exception as error:

        print(
            "[DEBUG] deno execution ERROR:",
            repr(error),
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
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10
    )

    print(
        "[DEBUG] ffmpeg returncode:",
        result.returncode,
        flush=True
    )

except Exception as error:

    print(
        "[DEBUG] ffmpeg execution ERROR:",
        repr(error),
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

    title = str(title).strip()

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

    title = title.rstrip(" .")

    if not title:
        title = "YouTube Video"

    title = title[:180].rstrip(" .")

    if not title:
        title = "YouTube Video"

    return title


# ==========================================================
# 出力ファイル名
# ==========================================================

def _make_output_filename(title, extension):

    return (
        f"{_sanitize_filename(title)}.{extension}"
    )


# ==========================================================
# Cookie準備
# ==========================================================

def _prepare_cookie_file():

    cookies_source = "/etc/secrets/cookies.txt"

    print(
        "[YTDLP] Cookie source:",
        cookies_source,
        flush=True
    )

    if not os.path.isfile(cookies_source):

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            + cookies_source
        )

    temporary_cookie_path = None

    try:

        temporary_cookie_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            prefix="y2conv_cookies_",
            delete=False
        )

        temporary_cookie_path = (
            temporary_cookie_file.name
        )

        temporary_cookie_file.close()

        shutil.copyfile(
            cookies_source,
            temporary_cookie_path
        )

        print(
            "[YTDLP] temporary cookie:",
            temporary_cookie_path,
            flush=True
        )

        return temporary_cookie_path

    except Exception:

        if temporary_cookie_path:

            try:

                os.remove(
                    temporary_cookie_path
                )

            except Exception:
                pass

        raise


# ==========================================================
# yt-dlp options
# ==========================================================

def _build_ydl_options(
    output_dir,
    format_string,
    merge_output_format=None,
    temporary_cookie_path=None,
    output_template=None
):

    output_dir = Path(output_dir)

    if output_template is None:

        output_template = (
            str(output_dir)
            /
            "%(id)s.%(ext)s"
        )

    ydl_opts = {

        "outtmpl":
            output_template,

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

        # --------------------------------------------------
        # Deno
        # --------------------------------------------------

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        # --------------------------------------------------
        # EJS
        # --------------------------------------------------

        "remote_components": {

            "ejs:github"

        }

    }

    if merge_output_format:

        ydl_opts[
            "merge_output_format"
        ] = merge_output_format

    if temporary_cookie_path:

        ydl_opts[
            "cookiefile"
        ] = temporary_cookie_path

    return ydl_opts


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(url):

    print(
        "[YTDLP] get_youtube_info START",
        flush=True
    )

    temporary_cookie_path = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        output_dir = _get_download_dir()

        ydl_opts = _build_ydl_options(

            output_dir=output_dir,

            format_string="bestaudio/best",

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

        return info

    except Exception as error:

        print(
            "[YTDLP] get_youtube_info ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if temporary_cookie_path:

            try:

                os.remove(
                    temporary_cookie_path
                )

            except Exception:
                pass

        print(
            "[YTDLP] get_youtube_info END",
            flush=True
        )


# ==========================================================
# 一時ダウンロードディレクトリ作成
# ==========================================================

def _create_job_download_dir():

    base_dir = _get_download_dir()

    job_dir = (
        base_dir
        /
        f".job_{uuid.uuid4().hex}"
    )

    job_dir.mkdir(
        parents=True,
        exist_ok=False
    )

    return job_dir


# ==========================================================
# ダウンロードファイル検索
# ==========================================================

def _find_downloaded_file(
    output_dir,
    info,
    merge_output_format=None
):

    output_dir = Path(output_dir)

    video_id = (
        info.get("id")
        if info
        else None
    )

    if not video_id:

        return None

    # ------------------------------------------------------
    # MP4など、期待される拡張子
    # ------------------------------------------------------

    if merge_output_format:

        expected = (
            output_dir
            /
            f"{video_id}.{merge_output_format}"
        )

        if expected.is_file():

            return expected

    # ------------------------------------------------------
    # IDベースで検索
    # ------------------------------------------------------

    candidates = []

    for path in output_dir.glob(
        f"{video_id}.*"
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

            continue

        if size <= 0:
            continue

        candidates.append(path)

    if not candidates:

        return None

    candidates.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    return candidates[0]


# ==========================================================
# URL → 一時ファイル
# ==========================================================

def download_source(
    url,
    output_dir=None
):

    print("==========================================", flush=True)

    print(
        "[YTDLP] download_source START",
        flush=True
    )

    print(
        "[YTDLP] URL:",
        url,
        flush=True
    )

    temporary_cookie_path = None
    job_dir = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        # --------------------------------------------------
        # 出力先
        # --------------------------------------------------

        if output_dir is None:

            job_dir = _create_job_download_dir()

        else:

            job_dir = Path(output_dir)

            job_dir.mkdir(
                parents=True,
                exist_ok=True
            )

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        # --------------------------------------------------
        # MP4用フォーマット
        #
        # video + audio を選択。
        # yt-dlp / FFmpeg側でMP4へmerge。
        # --------------------------------------------------

        format_string = (
            "bv*+ba/b"
        )

        ydl_opts = _build_ydl_options(

            output_dir=job_dir,

            format_string=format_string,

            merge_output_format="mp4",

            temporary_cookie_path=
                temporary_cookie_path

        )

        info = None

        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

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
                "[YTDLP] video id:",
                info.get("id"),
                flush=True
            )

            print(
                "[YTDLP] title:",
                info.get("title"),
                flush=True
            )

            print(
                "[YTDLP] duration:",
                info.get("duration"),
                flush=True
            )

            print(
                "[YTDLP] download START",
                flush=True
            )

            # --------------------------------------------------
            # ここが重要
            #
            # ydl.download() はファイルへ直接保存する。
            # Python側で動画全体をread()しない。
            # --------------------------------------------------

            ydl.download([
                url
            ])

            print(
                "[YTDLP] download SUCCESS",
                flush=True
            )

        # --------------------------------------------------
        # ダウンロード結果確認
        # --------------------------------------------------

        downloaded_file = (
            _find_downloaded_file(
                job_dir,
                info,
                merge_output_format="mp4"
            )
        )

        if downloaded_file is None:

            raise FileNotFoundError(
                "ダウンロードされた動画ファイルを確認できませんでした"
            )

        file_size = (
            downloaded_file.stat().st_size
        )

        if file_size <= 0:

            raise RuntimeError(
                "ダウンロードファイルのサイズが0です"
            )

        print(
            "[YTDLP] source file:",
            downloaded_file,
            flush=True
        )

        print(
            "[YTDLP] source size:",
            file_size,
            "bytes",
            flush=True
        )

        # --------------------------------------------------
        # 戻り値
        # --------------------------------------------------

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
                info,

            "temporary_dir":
                str(job_dir)

        }

    except Exception as error:

        print(
            "[YTDLP] download_source ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        # --------------------------------------------------
        # エラー時はJobディレクトリを残す
        #
        # デバッグできるようにする。
        # --------------------------------------------------

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
            "[YTDLP] download_source END",
            flush=True
        )

        print("==========================================", flush=True)


# ==========================================================
# 一時ディレクトリ削除
# ==========================================================

def cleanup_download(
    download_result
):

    if not download_result:
        return

    temporary_dir = (
        download_result.get(
            "temporary_dir"
        )
    )

    if not temporary_dir:
        return

    temporary_dir = Path(
        temporary_dir
    )

    try:

        if temporary_dir.exists():

            print(
                "[YTDLP] cleanup:",
                temporary_dir,
                flush=True
            )

            shutil.rmtree(
                temporary_dir
            )

    except Exception as error:

        print(
            "[YTDLP] cleanup ERROR:",
            repr(error),
            flush=True
        )


# ==========================================================
# 後方互換：create_mp3
#
# 外部から直接呼ばれても動くように残す。
# 新しいconvert.pyでは使用しない。
# ==========================================================

def create_mp3(
    url,
    output_dir=None,
    start_time=None,
    end_time=None
):

    from media_extract import create_mp3_from_file

    if output_dir is None:

        output_dir = _get_download_dir()

    download_result = None

    try:

        download_result = download_source(
            url
        )

        result = create_mp3_from_file(

            input_file=
                download_result["path"],

            output_dir=
                output_dir,

            title=
                download_result["title"],

            start_time=
                start_time,

            end_time=
                end_time

        )

        result.update({

            "duration":
                download_result.get(
                    "duration"
                ),

            "video_id":
                download_result.get(
                    "video_id"
                )

        })

        return result

    finally:

        cleanup_download(
            download_result
        )


# ==========================================================
# 後方互換：create_mp4
#
# 外部から直接呼ばれても動くように残す。
# 新しいconvert.pyでは使用しない。
# ==========================================================

def create_mp4(
    url,
    output_dir=None,
    start_time=None,
    end_time=None
):

    from media_extract import create_mp4_from_file

    if output_dir is None:

        output_dir = _get_download_dir()

    download_result = None

    try:

        download_result = download_source(
            url
        )

        result = create_mp4_from_file(

            input_file=
                download_result["path"],

            output_dir=
                output_dir,

            title=
                download_result["title"],

            start_time=
                start_time,

            end_time=
                end_time

        )

        result.update({

            "duration":
                download_result.get(
                    "duration"
                ),

            "video_id":
                download_result.get(
                    "video_id"
                )

        })

        return result

    finally:

        cleanup_download(
            download_result
        )
