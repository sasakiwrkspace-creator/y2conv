import sys
import os
import traceback
import shutil
import subprocess
import tempfile
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

        if result.returncode != 0:

            print(
                "[DEBUG] Deno execution failed",
                flush=True
            )

    except Exception as e:

        print(
            "[DEBUG] deno execution ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()


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
        ["ffmpeg", "-version"],
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


print("==========================================", flush=True)


# ==========================================================
# 共通：Cookie準備
# ==========================================================

def _prepare_cookie_file():

    print(
        "==========================================",
        flush=True
    )

    print(
        "Cookieファイル準備開始",
        flush=True
    )

    cookies_source = "/etc/secrets/cookies.txt"

    print(
        "元Cookieファイル:",
        cookies_source,
        flush=True
    )

    print(
        "Cookie exists:",
        os.path.isfile(cookies_source),
        flush=True
    )

    if not os.path.isfile(cookies_source):

        raise FileNotFoundError(
            f"Cookieファイルが見つかりません: {cookies_source}"
        )

    temporary_cookie_path = None

    try:

        cookie_size = os.path.getsize(
            cookies_source
        )

        print(
            "元Cookieサイズ:",
            cookie_size,
            "bytes",
            flush=True
        )

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
            "一時Cookieファイル作成:",
            temporary_cookie_path,
            flush=True
        )

        temporary_size = os.path.getsize(
            temporary_cookie_path
        )

        print(
            "一時Cookieサイズ:",
            temporary_size,
            "bytes",
            flush=True
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
            temporary_cookie_path,
            flush=True
        )

        print(
            "サイズ:",
            temporary_size,
            "bytes",
            flush=True
        )

        print(
            "==========================================",
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


# ==========================================================
# 共通：yt-dlpオプション作成
# ==========================================================

def _build_ydl_options(
    output_dir,
    format_string,
    merge_output_format=None,
    temporary_cookie_path=None
):

    print(
        "yt-dlp共通設定開始",
        flush=True
    )

    download_template = str(
        Path(output_dir) / "%(id)s.%(ext)s"
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

    if merge_output_format:

        ydl_opts["merge_output_format"] = (
            merge_output_format
        )

    if temporary_cookie_path:

        ydl_opts["cookiefile"] = (
            temporary_cookie_path
        )

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
        os.path.isfile(DENO_PATH),
        flush=True
    )

    print(
        "[DEBUG] cookiefile:",
        temporary_cookie_path,
        flush=True
    )

    print(
        "[DEBUG] remote_components:",
        ydl_opts.get("remote_components"),
        flush=True
    )

    print(
        "[DEBUG] js_runtimes:",
        ydl_opts.get("js_runtimes"),
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return ydl_opts


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(
    url
):

    print("==========================================", flush=True)

    print(
        "YouTube情報取得開始",
        flush=True
    )

    print(
        "URL:",
        url,
        flush=True
    )

    print(
        "Python:",
        sys.version,
        flush=True
    )

    print(
        "yt-dlp:",
        yt_dlp.version.__version__,
        flush=True
    )

    print(
        "Deno PATH:",
        DENO_PATH,
        flush=True
    )

    print(
        "Deno exists:",
        os.path.isfile(DENO_PATH),
        flush=True
    )

    print(
        "ffmpeg:",
        shutil.which("ffmpeg"),
        flush=True
    )

    print("==========================================", flush=True)

    temporary_cookie_path = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        # ==================================================
        # Deno確認
        # ==================================================

        print(
            "Deno単体テスト開始",
            flush=True
        )

        print(
            "Deno PATH:",
            DENO_PATH,
            flush=True
        )

        if not os.path.isfile(DENO_PATH):

            print(
                "Denoが存在しません:",
                DENO_PATH,
                flush=True
            )

            raise Exception(
                "Denoが利用できません"
            )

        if not os.access(
            DENO_PATH,
            os.X_OK
        ):

            raise Exception(
                f"Denoに実行権限がありません: {DENO_PATH}"
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

        print(
            "Deno returncode:",
            deno_result.returncode,
            flush=True
        )

        print(
            "Deno stdout:",
            deno_result.stdout,
            flush=True
        )

        print(
            "Deno stderr:",
            deno_result.stderr,
            flush=True
        )

        if deno_result.returncode != 0:

            raise Exception(
                "Denoの実行に失敗しました"
            )

        print(
            "Deno単体テスト成功",
            flush=True
        )

        print("==========================================", flush=True)

        # ==================================================
        # Cookie
        # ==================================================

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        # ==================================================
        # output directory
        # ==================================================

        output_dir = Path(
            os.getcwd()
        ) / "downloads"

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ==================================================
        # yt-dlp options
        # ==================================================

        ydl_opts = _build_ydl_options(

            output_dir=output_dir,

            format_string="bestaudio/best",

            temporary_cookie_path=
                temporary_cookie_path

        )

        # ==================================================
        # 情報取得
        # ==================================================

        print(
            "yt-dlp extract_info開始",
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

            raise Exception(
                "YouTube情報を取得できませんでした"
            )

        print(
            "YouTube情報取得成功",
            flush=True
        )

        print(
            "Video ID:",
            info.get("id"),
            flush=True
        )

        print(
            "Title:",
            info.get("title"),
            flush=True
        )

        print(
            "Duration:",
            info.get("duration"),
            flush=True
        )

        print(
            "Uploader:",
            info.get("uploader"),
            flush=True
        )

        print(
            "Webpage URL:",
            info.get("webpage_url"),
            flush=True
        )

        print("==========================================", flush=True)

        return info

    except Exception as e:

        print("==========================================", flush=True)

        print(
            "get_youtube_info ERROR:",
            repr(e),
            flush=True
        )

        print(
            "ERROR TYPE:",
            type(e).__name__,
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
                        "一時Cookieファイル削除OK:",
                        temporary_cookie_path,
                        flush=True
                    )

            except Exception as e:

                print(
                    "Cookie削除ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            "get_youtube_info終了処理",
            flush=True
        )

        print("==========================================", flush=True)


# ==========================================================
# 共通：yt-dlpでダウンロード
# ==========================================================

def _download_with_ytdlp(
    url,
    output_dir,
    format_string,
    merge_output_format=None,
    mode_name="UNKNOWN"
):

    print("==========================================", flush=True)

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
            output_dir=output_dir,
            format_string=format_string,
            merge_output_format=merge_output_format,
            temporary_cookie_path=temporary_cookie_path
        )

        info = None
        expected_filename = None

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                f"[DEBUG] [{mode_name}] extract_info",
                flush=True
            )

            info = ydl.extract_info(
                url,
                download=False
            )

            if info is None:

                raise RuntimeError(
                    f"{mode_name} extract_info() returned None"
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

            try:

                expected_filename = (
                    ydl.prepare_filename(info)
                )

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] prepare_filename ERROR:",
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
            and merge_output_format
            and info
        ):

            video_id = info.get("id")

            if video_id:

                merged_path = (
                    output_dir
                    /
                    f"{video_id}.{merge_output_format}"
                )

                if merged_path.is_file():

                    downloaded_file = (
                        merged_path
                    )

        if downloaded_file is None and info:

            video_id = info.get("id")

            if video_id:

                possible_files = []

                for path in output_dir.glob(
                    video_id + ".*"
                ):

                    if not path.is_file():
                        continue

                    if path.suffix.lower() in [
                        ".part",
                        ".ytdl",
                        ".temp"
                    ]:

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
                        key=lambda p: p.stat().st_mtime,
                        reverse=True
                    )

                    downloaded_file = (
                        possible_files[0]
                    )

        if downloaded_file is None:

            raise FileNotFoundError(
                f"{mode_name}ダウンロードファイルを確認できませんでした"
            )

        file_size = (
            downloaded_file.stat().st_size
        )

        if file_size <= 0:

            raise RuntimeError(
                f"{mode_name}ファイルのサイズが0です"
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

            "info":
                info

        }

    except Exception as e:

        print(
            f"[DEBUG] _download_with_ytdlp ERROR [{mode_name}]:",
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
# 時間文字列 → 秒
# ==========================================================

def _time_to_seconds(value):

    parts = str(
        value
    ).split(":")

    if len(parts) == 3:

        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])

        return (
            h * 3600
            + m * 60
            + s
        )

    if len(parts) == 2:

        m = int(parts[0])
        s = float(parts[1])

        return (
            m * 60
            + s
        )

    return float(value)


# ==========================================================
# MP3
# ==========================================================

def create_mp3(
    url,
    output_dir=None,
    start_time=None,
    end_time=None
):

    print(
        "[DEBUG] create_mp3 START",
        flush=True
    )

    if output_dir is None:

        output_dir = (
            Path(os.getcwd())
            / "downloads"
        )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    download_result = _download_with_ytdlp(

        url=url,

        output_dir=output_dir,

        format_string="bestaudio/best",

        merge_output_format=None,

        mode_name="MP3"

    )

    downloaded_file = Path(
        download_result["path"]
    )

    info = (
        download_result.get("info")
        or {}
    )

    video_id = (
        info.get("id")
        or download_result.get("video_id")
    )

    video_title = (
        info.get("title")
        or "YouTube Audio"
    )

    if video_id:

        mp3_file = (
            output_dir
            /
            f"{video_id}.mp3"
        )

    else:

        mp3_file = (
            downloaded_file.with_suffix(
                ".mp3"
            )
        )

    temporary_mp3_file = None

    if (
        downloaded_file.resolve()
        ==
        mp3_file.resolve()
    ):

        temporary_mp3_file = (
            output_dir
            /
            f"{video_id or 'audio'}_converted_temp.mp3"
        )

        ffmpeg_output = (
            temporary_mp3_file
        )

    else:

        ffmpeg_output = mp3_file

    ffmpeg_command = [
        "ffmpeg",
        "-y"
    ]

    if start_time:

        ffmpeg_command.extend([
            "-ss",
            str(start_time)
        ])

    ffmpeg_command.extend([
        "-i",
        str(downloaded_file)
    ])

    if end_time and start_time:

        start_seconds = (
            _time_to_seconds(
                start_time
            )
        )

        end_seconds = (
            _time_to_seconds(
                end_time
            )
        )

        duration = (
            end_seconds
            - start_seconds
        )

        if duration <= 0:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )

        ffmpeg_command.extend([
            "-t",
            str(duration)
        ])

    elif end_time:

        ffmpeg_command.extend([
            "-to",
            str(end_time)
        ])

    ffmpeg_command.extend([

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-q:a",
        "2",

        "-metadata",
        "title=" + str(video_title),

        "-metadata",
        "comment=YouTube Converter",

        str(ffmpeg_output)

    ])

    print(
        "[DEBUG] MP3 FFmpeg:",
        " ".join(ffmpeg_command),
        flush=True
    )

    result = subprocess.run(
        ffmpeg_command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    print(
        "[DEBUG] MP3 FFmpeg returncode:",
        result.returncode,
        flush=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg conversion failed\n"
            + result.stderr
        )

    if temporary_mp3_file:

        if mp3_file.exists():

            mp3_file.unlink()

        temporary_mp3_file.replace(
            mp3_file
        )

        temporary_mp3_file = None

    if not mp3_file.exists():

        raise FileNotFoundError(
            "MP3ファイルが作成されませんでした"
        )

    if mp3_file.stat().st_size <= 0:

        raise RuntimeError(
            "MP3ファイルのサイズが0です"
        )

    if (
        downloaded_file.exists()
        and
        downloaded_file.resolve()
        !=
        mp3_file.resolve()
    ):

        downloaded_file.unlink()

    return {

        "path":
            str(mp3_file),

        "filename":
            mp3_file.name

    }


# ==========================================================
# MP4
# ==========================================================

def create_mp4(
    url,
    output_dir=None,
    start_time=None,
    end_time=None
):

    print(
        "[DEBUG] create_mp4 START",
        flush=True
    )

    if output_dir is None:

        output_dir = (
            Path(os.getcwd())
            / "downloads"
        )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    download_result = _download_with_ytdlp(

        url=url,

        output_dir=output_dir,

        format_string="bv*+ba/b",

        merge_output_format="mp4",

        mode_name="MP4"

    )

    downloaded_file = Path(
        download_result["path"]
    )

    info = (
        download_result.get("info")
        or {}
    )

    video_id = (
        info.get("id")
        or download_result.get("video_id")
    )

    video_title = (
        info.get("title")
        or "YouTube Video"
    )

    if (
        start_time is None
        and end_time is None
    ):

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name

        }

    start_seconds = 0

    if start_time is not None:

        start_seconds = (
            _time_to_seconds(
                start_time
            )
        )

    if start_seconds < 0:

        raise ValueError(
            "開始時間は0秒以上にしてください。"
        )

    duration = None

    if end_time is not None:

        end_seconds = (
            _time_to_seconds(
                end_time
            )
        )

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )

        duration = (
            end_seconds
            - start_seconds
        )

    if video_id:

        mp4_file = (
            output_dir
            /
            f"{video_id}.mp4"
        )

    else:

        mp4_file = (
            downloaded_file.with_suffix(
                ".mp4"
            )
        )

    temporary_mp4_file = None

    if (
        downloaded_file.resolve()
        ==
        mp4_file.resolve()
    ):

        temporary_mp4_file = (
            output_dir
            /
            f"{video_id or 'video'}_trim_temp.mp4"
        )

        ffmpeg_output = (
            temporary_mp4_file
        )

    else:

        ffmpeg_output = (
            mp4_file
        )

    ffmpeg_command = [
        "ffmpeg",
        "-y"
    ]

    if start_seconds > 0:

        ffmpeg_command.extend([
            "-ss",
            str(start_seconds)
        ])

    ffmpeg_command.extend([
        "-i",
        str(downloaded_file)
    ])

    if duration is not None:

        ffmpeg_command.extend([
            "-t",
            str(duration)
        ])

    ffmpeg_command.extend([

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "23",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-movflags",
        "+faststart",

        "-metadata",
        "title=" + str(video_title),

        "-metadata",
        "comment=YouTube Converter",

        str(ffmpeg_output)

    ])

    print(
        "[DEBUG] MP4 FFmpeg:",
        " ".join(ffmpeg_command),
        flush=True
    )

    result = subprocess.run(
        ffmpeg_command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    print(
        "[DEBUG] MP4 FFmpeg returncode:",
        result.returncode,
        flush=True
    )

    if result.stderr:

        print(
            "[DEBUG] MP4 FFmpeg stderr:",
            result.stderr,
            flush=True
        )

    if result.returncode != 0:

        raise RuntimeError(
            "MP4 FFmpeg conversion failed\n"
            + result.stderr
        )

    if temporary_mp4_file:

        if mp4_file.exists():

            mp4_file.unlink()

        temporary_mp4_file.replace(
            mp4_file
        )

        temporary_mp4_file = None

    if not mp4_file.exists():

        raise FileNotFoundError(
            "MP4ファイルが作成されませんでした"
        )

    if mp4_file.stat().st_size <= 0:

        raise RuntimeError(
            "MP4ファイルのサイズが0です"
        )

    if (
        downloaded_file.exists()
        and
        downloaded_file.resolve()
        !=
        mp4_file.resolve()
    ):

        downloaded_file.unlink()

    return {

        "path":
            str(mp4_file),

        "filename":
            mp4_file.name

    }
