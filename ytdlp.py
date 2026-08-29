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

except Exception as e:

    print(
        "[DEBUG] yt_dlp import ERROR:",
        repr(e),
        flush=True
    )

    traceback.print_exc()
    raise


# ==========================================================
# Deno確認
# ==========================================================

print(
    "[DEBUG] deno path:",
    shutil.which("deno"),
    flush=True
)

try:

    result = subprocess.run(
        ["deno", "--version"],
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


print("==========================================", flush=True)


# ==========================================================
# 共通：Cookie準備
# ==========================================================

def _prepare_cookie_file():

    print(
        "[DEBUG] Preparing cookie file...",
        flush=True
    )

    cookies_source = "/etc/secrets/cookies.txt"

    print(
        "[DEBUG] cookies source:",
        cookies_source,
        flush=True
    )

    print(
        "[DEBUG] cookies exists:",
        os.path.isfile(cookies_source),
        flush=True
    )

    temporary_cookie_path = None

    if not os.path.isfile(cookies_source):

        print(
            "[DEBUG] WARNING: cookies file does not exist",
            flush=True
        )

        return None

    try:

        print(
            "[DEBUG] cookies file detected",
            flush=True
        )

        print(
            "[DEBUG] cookies source size:",
            os.path.getsize(cookies_source),
            flush=True
        )

        temporary_cookie_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            prefix="y2conv_cookies_",
            delete=False
        )

        temporary_cookie_path = temporary_cookie_file.name

        temporary_cookie_file.close()

        shutil.copyfile(
            cookies_source,
            temporary_cookie_path
        )

        print(
            "[DEBUG] temporary cookies created:",
            temporary_cookie_path,
            flush=True
        )

        print(
            "[DEBUG] temporary cookies size:",
            os.path.getsize(temporary_cookie_path),
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
                if os.path.exists(temporary_cookie_path):
                    os.remove(temporary_cookie_path)
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
        "[DEBUG] Building yt-dlp options...",
        flush=True
    )

    download_template = str(
        output_dir / "%(id)s.%(ext)s"
    )

    print(
        "[DEBUG] download template:",
        download_template,
        flush=True
    )

    ydl_opts = {
        "outtmpl": download_template,

        "format": format_string,

        "noplaylist": True,

        "quiet": False,

        "no_warnings": False,

        "verbose": True,

        "js_runtimes": {
            "deno": {}
        },

        "remote_components": {
            "ejs:github"
        },
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
            "[DEBUG] cookiefile enabled:",
            temporary_cookie_path,
            flush=True
        )

    else:

        print(
            "[DEBUG] cookiefile NOT enabled",
            flush=True
        )

    print(
        "[DEBUG] yt-dlp options:",
        flush=True
    )

    print(
        "[DEBUG] format:",
        ydl_opts.get("format"),
        flush=True
    )

    print(
        "[DEBUG] merge_output_format:",
        ydl_opts.get("merge_output_format"),
        flush=True
    )

    print(
        "[DEBUG] noplaylist:",
        ydl_opts.get("noplaylist"),
        flush=True
    )

    print(
        "[DEBUG] js_runtimes:",
        ydl_opts.get("js_runtimes"),
        flush=True
    )

    print(
        "[DEBUG] remote_components:",
        ydl_opts.get("remote_components"),
        flush=True
    )

    print(
        "[DEBUG] cookiefile configured:",
        bool(ydl_opts.get("cookiefile")),
        flush=True
    )

    return ydl_opts


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

    print(
        "[DEBUG] URL:",
        url,
        flush=True
    )

    print(
        "[DEBUG] output_dir:",
        output_dir,
        flush=True
    )

    print(
        "[DEBUG] format_string:",
        format_string,
        flush=True
    )

    print(
        "[DEBUG] merge_output_format:",
        merge_output_format,
        flush=True
    )

    if not url:

        raise ValueError(
            "YouTube URLが空です"
        )

    output_dir = Path(output_dir)

    print(
        "[DEBUG] output directory:",
        output_dir,
        flush=True
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "[DEBUG] output directory exists:",
        output_dir.exists(),
        flush=True
    )

    print(
        "[DEBUG] output directory writable:",
        os.access(output_dir, os.W_OK),
        flush=True
    )

    temporary_cookie_path = None

    try:

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        print(
            f"[DEBUG] [{mode_name}] Preparing cookies...",
            flush=True
        )

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        # --------------------------------------------------
        # yt-dlp設定
        # --------------------------------------------------

        print(
            f"[DEBUG] [{mode_name}] Preparing yt-dlp options...",
            flush=True
        )

        ydl_opts = _build_ydl_options(
            output_dir=output_dir,
            format_string=format_string,
            merge_output_format=merge_output_format,
            temporary_cookie_path=temporary_cookie_path
        )

        # --------------------------------------------------
        # yt-dlp開始
        # --------------------------------------------------

        info = None

        print(
            "==========================================",
            flush=True
        )

        print(
            f"[DEBUG] [{mode_name}] Creating YoutubeDL instance...",
            flush=True
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            print(
                f"[DEBUG] [{mode_name}] YoutubeDL instance created",
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] Starting extract_info(download=True)...",
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] Connecting to YouTube...",
                flush=True
            )

            info = ydl.extract_info(
                url,
                download=True
            )

            print(
                f"[DEBUG] [{mode_name}] extract_info/download SUCCESS",
                flush=True
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
                f"[DEBUG] [{mode_name}] video title:",
                info.get("title"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] duration:",
                info.get("duration"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] webpage_url:",
                info.get("webpage_url"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] extractor:",
                info.get("extractor"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] ext:",
                info.get("ext"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] requested_formats:",
                info.get("requested_formats"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] format_id:",
                info.get("format_id"),
                flush=True
            )

        # --------------------------------------------------
        # ダウンロードファイル検索
        # --------------------------------------------------

        print(
            f"[DEBUG] [{mode_name}] Searching downloaded files...",
            flush=True
        )

        video_id = None

        if info:
            video_id = info.get("id")

        print(
            f"[DEBUG] [{mode_name}] video_id:",
            video_id,
            flush=True
        )

        downloaded_file = None

        if video_id:

            candidates = list(
                output_dir.glob(
                    video_id + ".*"
                )
            )

            print(
                f"[DEBUG] [{mode_name}] candidate files:",
                len(candidates),
                flush=True
            )

            for candidate in candidates:

                try:
                    candidate_size = candidate.stat().st_size
                except Exception:
                    candidate_size = -1

                print(
                    f"[DEBUG] [{mode_name}] candidate:",
                    candidate,
                    "size=",
                    candidate_size,
                    flush=True
                )

                if not candidate.is_file():
                    continue

                if candidate.suffix.lower() in [
                    ".part",
                    ".ytdl",
                    ".temp"
                ]:
                    print(
                        f"[DEBUG] [{mode_name}] temporary file skipped:",
                        candidate,
                        flush=True
                    )
                    continue

                downloaded_file = candidate

                print(
                    f"[DEBUG] [{mode_name}] candidate selected:",
                    downloaded_file,
                    flush=True
                )

                break

        # --------------------------------------------------
        # 見つからない場合
        # --------------------------------------------------

        if downloaded_file is None:

            print(
                f"[DEBUG] [{mode_name}] No file found by video ID",
                flush=True
            )

            all_files = [
                p
                for p in output_dir.iterdir()
                if p.is_file()
            ]

            print(
                f"[DEBUG] [{mode_name}] files in output directory:",
                len(all_files),
                flush=True
            )

            for p in all_files:

                try:
                    size = p.stat().st_size
                except Exception:
                    size = -1

                print(
                    f"[DEBUG] [{mode_name}] existing file:",
                    p,
                    "size=",
                    size,
                    flush=True
                )

        if downloaded_file is None:

            raise FileNotFoundError(
                f"yt-dlpでダウンロードした{mode_name}ファイルを確認できませんでした"
            )

        print(
            f"[DEBUG] [{mode_name}] downloaded file:",
            downloaded_file,
            flush=True
        )

        print(
            f"[DEBUG] [{mode_name}] downloaded file size:",
            downloaded_file.stat().st_size,
            flush=True
        )

        print(
            f"[DEBUG] _download_with_ytdlp SUCCESS [{mode_name}]",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return {
            "path": str(downloaded_file),
            "filename": downloaded_file.name,
            "video_id": video_id,
            "info": info
        }

    except Exception as e:

        print(
            "==========================================",
            flush=True
        )

        print(
            f"[DEBUG] _download_with_ytdlp ERROR [{mode_name}]:",
            repr(e),
            flush=True
        )

        print(
            f"[DEBUG] [{mode_name}] exception type:",
            type(e).__name__,
            flush=True
        )

        traceback.print_exc()

        print(
            "==========================================",
            flush=True
        )

        raise

    finally:

        # --------------------------------------------------
        # Cookie削除
        # --------------------------------------------------

        if temporary_cookie_path:

            print(
                f"[DEBUG] [{mode_name}] Removing temporary cookies...",
                flush=True
            )

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

                    print(
                        f"[DEBUG] [{mode_name}] Temporary cookies removed",
                        flush=True
                    )

                else:

                    print(
                        f"[DEBUG] [{mode_name}] Temporary cookies already absent",
                        flush=True
                    )

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] Temporary cookies removal ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            f"[DEBUG] _download_with_ytdlp END [{mode_name}]",
            flush=True
        )


# ==========================================================
# MP3
# ==========================================================

def create_mp3(
    url,
    output_dir=None,
    start_time=None,
    end_time=None
):

    print("==========================================", flush=True)
    print("[DEBUG] create_mp3 START", flush=True)

    try:

        print(
            "[DEBUG] MP3 URL:",
            url,
            flush=True
        )

        print(
            "[DEBUG] MP3 output_dir:",
            output_dir,
            flush=True
        )

        print(
            "[DEBUG] MP3 start_time:",
            start_time,
            flush=True
        )

        print(
            "[DEBUG] MP3 end_time:",
            end_time,
            flush=True
        )

        if output_dir is None:

            output_dir = os.path.join(
                os.getcwd(),
                "downloads"
            )

        # --------------------------------------------------
        # yt-dlpで音声ダウンロード
        # --------------------------------------------------

        print(
            "[DEBUG] MP3: starting yt-dlp...",
            flush=True
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

        print(
            "[DEBUG] MP3 source file:",
            downloaded_file,
            flush=True
        )

        # --------------------------------------------------
        # FFmpeg
        # --------------------------------------------------

        mp3_file = downloaded_file.with_suffix(
            ".mp3"
        )

        print(
            "[DEBUG] MP3 target:",
            mp3_file,
            flush=True
        )

        ffmpeg_command = [
            "ffmpeg",
            "-y"
        ]

        # start_time
        if start_time:

            print(
                "[DEBUG] MP3 start_time detected:",
                start_time,
                flush=True
            )

            ffmpeg_command.extend([
                "-ss",
                str(start_time)
            ])

        ffmpeg_command.extend([
            "-i",
            str(downloaded_file)
        ])

        # end_timeはduration計算をせず、
        # 現段階では従来通り受け取るだけにしておく
        if end_time:

            print(
                "[DEBUG] MP3 end_time detected:",
                end_time,
                flush=True
            )

        ffmpeg_command.extend([
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "2"
        ])

        if end_time and start_time:

            print(
                "[DEBUG] MP3: calculating duration from start/end...",
                flush=True
            )

            # HH:MM:SS形式を秒へ変換
            def time_to_seconds(value):

                parts = str(value).split(":")

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

            try:

                start_seconds = time_to_seconds(
                    start_time
                )

                end_seconds = time_to_seconds(
                    end_time
                )

                duration = (
                    end_seconds
                    - start_seconds
                )

                print(
                    "[DEBUG] MP3 start seconds:",
                    start_seconds,
                    flush=True
                )

                print(
                    "[DEBUG] MP3 end seconds:",
                    end_seconds,
                    flush=True
                )

                print(
                    "[DEBUG] MP3 duration:",
                    duration,
                    flush=True
                )

                if duration > 0:

                    ffmpeg_command.extend([
                        "-t",
                        str(duration)
                    ])

            except Exception as e:

                print(
                    "[DEBUG] MP3 time calculation ERROR:",
                    repr(e),
                    flush=True
                )

                raise

        elif end_time:

            print(
                "[DEBUG] MP3: end_time specified without start_time",
                flush=True
            )

            ffmpeg_command.extend([
                "-to",
                str(end_time)
            ])

        ffmpeg_command.append(
            str(mp3_file)
        )

        print(
            "[DEBUG] MP3 FFmpeg command:",
            " ".join(ffmpeg_command),
            flush=True
        )

        print(
            "[DEBUG] MP3 Starting FFmpeg...",
            flush=True
        )

        ffmpeg_result = subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True
        )

        print(
            "[DEBUG] MP3 FFmpeg returncode:",
            ffmpeg_result.returncode,
            flush=True
        )

        if ffmpeg_result.stdout:

            print(
                "[DEBUG] MP3 FFmpeg stdout:",
                ffmpeg_result.stdout,
                flush=True
            )

        if ffmpeg_result.stderr:

            print(
                "[DEBUG] MP3 FFmpeg stderr:",
                ffmpeg_result.stderr,
                flush=True
            )

        if ffmpeg_result.returncode != 0:

            raise RuntimeError(
                "FFmpeg conversion failed"
            )

        if not mp3_file.exists():

            raise FileNotFoundError(
                "MP3ファイルが作成されませんでした"
            )

        print(
            "[DEBUG] MP3 exists:",
            mp3_file.exists(),
            flush=True
        )

        print(
            "[DEBUG] MP3 size:",
            mp3_file.stat().st_size,
            flush=True
        )

        # --------------------------------------------------
        # 元ファイル削除
        # --------------------------------------------------

        if downloaded_file.exists():

            print(
                "[DEBUG] Removing MP3 source file:",
                downloaded_file,
                flush=True
            )

            downloaded_file.unlink()

            print(
                "[DEBUG] MP3 source file removed",
                flush=True
            )

        result = {
            "path": str(mp3_file),
            "filename": mp3_file.name
        }

        print(
            "[DEBUG] MP3 result:",
            result,
            flush=True
        )

        print(
            "[DEBUG] create_mp3 SUCCESS",
            flush=True
        )

        return result

    except Exception as e:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[DEBUG] create_mp3 ERROR:",
            repr(e),
            flush=True
        )

        print(
            "[DEBUG] MP3 exception type:",
            type(e).__name__,
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        print(
            "[DEBUG] create_mp3 END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# MP4
# ==========================================================

def create_mp4(
    url,
    output_dir=None
):

    print("==========================================", flush=True)
    print("[DEBUG] create_mp4 START", flush=True)

    try:

        print(
            "[DEBUG] MP4 URL:",
            url,
            flush=True
        )

        print(
            "[DEBUG] MP4 output_dir:",
            output_dir,
            flush=True
        )

        if output_dir is None:

            output_dir = os.path.join(
                os.getcwd(),
                "downloads"
            )

        # --------------------------------------------------
        # yt-dlpで動画＋音声ダウンロード
        # --------------------------------------------------

        print(
            "[DEBUG] MP4: starting yt-dlp...",
            flush=True
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

        print(
            "[DEBUG] MP4 downloaded file:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] MP4 downloaded file size:",
            downloaded_file.stat().st_size,
            flush=True
        )

        # --------------------------------------------------
        # MP4確認
        # --------------------------------------------------

        if downloaded_file.suffix.lower() != ".mp4":

            print(
                "[DEBUG] WARNING: MP4 file is not .mp4:",
                downloaded_file.suffix,
                flush=True
            )

        else:

            print(
                "[DEBUG] MP4 extension confirmed",
                flush=True
            )

        result = {
            "path": str(downloaded_file),
            "filename": downloaded_file.name
        }

        print(
            "[DEBUG] MP4 result:",
            result,
            flush=True
        )

        print(
            "[DEBUG] create_mp4 SUCCESS",
            flush=True
        )

        return result

    except Exception as e:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[DEBUG] create_mp4 ERROR:",
            repr(e),
            flush=True
        )

        print(
            "[DEBUG] MP4 exception type:",
            type(e).__name__,
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        print(
            "[DEBUG] create_mp4 END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )
