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
# FFmpeg確認
# ==========================================================

print(
    "[DEBUG] ffmpeg path:",
    shutil.which("ffmpeg"),
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

        first_line = result.stdout.splitlines()[0]

        print(
            "[DEBUG] ffmpeg version:",
            first_line,
            flush=True
        )

    if result.stderr:

        print(
            "[DEBUG] ffmpeg stderr:",
            result.stderr,
            flush=True
        )

except Exception as e:

    print(
        "[DEBUG] ffmpeg execution ERROR:",
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

        temporary_cookie_path = (
            temporary_cookie_file.name
        )

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
        bool(
            ydl_opts.get("cookiefile")
        ),
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

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "[DEBUG] output directory:",
        output_dir,
        flush=True
    )

    print(
        "[DEBUG] output directory exists:",
        output_dir.exists(),
        flush=True
    )

    print(
        "[DEBUG] output directory writable:",
        os.access(
            output_dir,
            os.W_OK
        ),
        flush=True
    )

    temporary_cookie_path = None

    try:

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        # --------------------------------------------------
        # yt-dlp設定
        # --------------------------------------------------

        ydl_opts = _build_ydl_options(
            output_dir=output_dir,
            format_string=format_string,
            merge_output_format=merge_output_format,
            temporary_cookie_path=temporary_cookie_path
        )

        # --------------------------------------------------
        # yt-dlp実行
        # --------------------------------------------------

        info = None

        print(
            f"[DEBUG] [{mode_name}] Creating YoutubeDL instance...",
            flush=True
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                f"[DEBUG] [{mode_name}] YoutubeDL instance created",
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] Starting extract_info(download=True)...",
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
                f"[DEBUG] [{mode_name}] ext:",
                info.get("ext"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] format_id:",
                info.get("format_id"),
                flush=True
            )

        # --------------------------------------------------
        # ファイル検索
        # --------------------------------------------------

        video_id = (
            info.get("id")
            if info
            else None
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

            # 一時ファイルを除外
            candidates = [
                p
                for p in candidates
                if p.is_file()
                and p.suffix.lower() not in [
                    ".part",
                    ".ytdl",
                    ".temp"
                ]
            ]

            # サイズのあるファイルを優先
            candidates.sort(
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if candidates:

                downloaded_file = (
                    candidates[0]
                )

                print(
                    f"[DEBUG] [{mode_name}] selected file:",
                    downloaded_file,
                    flush=True
                )

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

            for p in all_files:

                print(
                    f"[DEBUG] [{mode_name}] existing file:",
                    p,
                    "size=",
                    p.stat().st_size,
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

        return {
            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "video_id":
                video_id,

            "info":
                info
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

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] Cookie removal ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            f"[DEBUG] _download_with_ytdlp END [{mode_name}]",
            flush=True
        )


# ==========================================================
# 時間文字列 → 秒
# ==========================================================

def _time_to_seconds(value):

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

    downloaded_file = None

    temporary_mp3_file = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        if output_dir is None:

            output_dir = os.path.join(
                os.getcwd(),
                "downloads"
            )

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

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

        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

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

        info = download_result.get(
            "info"
        ) or {}

        video_id = (
            info.get("id")
            or download_result.get("video_id")
        )

        video_title = (
            info.get("title")
            or "YouTube Audio"
        )

        print(
            "[DEBUG] MP3 source:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] MP3 YouTube title:",
            video_title,
            flush=True
        )

        print(
            "[DEBUG] MP3 video id:",
            video_id,
            flush=True
        )

        # --------------------------------------------------
        # 完成MP3のパス
        # --------------------------------------------------

        if video_id:

            mp3_file = (
                output_dir
                / f"{video_id}.mp3"
            )

        else:

            mp3_file = (
                downloaded_file.with_suffix(
                    ".mp3"
                )
            )

        # --------------------------------------------------
        # 入力と出力が同じ場合
        # --------------------------------------------------

        if (
            downloaded_file.resolve()
            == mp3_file.resolve()
        ):

            print(
                "[DEBUG] MP3 source and target are identical",
                flush=True
            )

            temporary_mp3_file = (
                output_dir
                / f"{video_id or 'audio'}_converted.mp3"
            )

            ffmpeg_output = (
                temporary_mp3_file
            )

        else:

            ffmpeg_output = (
                mp3_file
            )

        print(
            "[DEBUG] MP3 FFmpeg output:",
            ffmpeg_output,
            flush=True
        )

        # --------------------------------------------------
        # FFmpeg
        # --------------------------------------------------

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

        # --------------------------------------------------
        # MP3 + 日本語タイトル
        # --------------------------------------------------

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
            "[DEBUG] MP3 FFmpeg command:",
            " ".join(
                ffmpeg_command
            ),
            flush=True
        )

        # --------------------------------------------------
        # FFmpeg実行
        # --------------------------------------------------

        ffmpeg_result = subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
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

            error_detail = (
                ffmpeg_result.stderr.strip()
                if ffmpeg_result.stderr
                else "FFmpegからエラー内容が返されませんでした。"
            )

            raise RuntimeError(
                "FFmpeg conversion failed\n"
                + error_detail
            )

        # --------------------------------------------------
        # 一時MP3 → 最終MP3
        # --------------------------------------------------

        if temporary_mp3_file:

            print(
                "[DEBUG] Replacing original MP3 with converted MP3",
                flush=True
            )

            if mp3_file.exists():

                mp3_file.unlink()

            temporary_mp3_file.replace(
                mp3_file
            )

            temporary_mp3_file = None

        # --------------------------------------------------
        # 完成確認
        # --------------------------------------------------

        if not mp3_file.exists():

            raise FileNotFoundError(
                "MP3ファイルが作成されませんでした"
            )

        mp3_size = (
            mp3_file.stat().st_size
        )

        print(
            "[DEBUG] MP3 final file:",
            mp3_file,
            flush=True
        )

        print(
            "[DEBUG] MP3 final size:",
            mp3_size,
            flush=True
        )

        if mp3_size <= 0:

            raise RuntimeError(
                "MP3ファイルのサイズが0です"
            )

        # --------------------------------------------------
        # 元ファイル削除
        # --------------------------------------------------

        if (
            downloaded_file.exists()
            and downloaded_file.resolve()
            != mp3_file.resolve()
        ):

            print(
                "[DEBUG] Removing MP3 source:",
                downloaded_file,
                flush=True
            )

            downloaded_file.unlink()

            print(
                "[DEBUG] MP3 source removed",
                flush=True
            )

        result = {
            "path":
                str(mp3_file),

            "filename":
                mp3_file.name
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

        # --------------------------------------------------
        # 失敗時の一時ファイル削除
        # --------------------------------------------------

        if temporary_mp3_file:

            try:

                if temporary_mp3_file.exists():

                    temporary_mp3_file.unlink()

                    print(
                        "[DEBUG] temporary MP3 removed",
                        flush=True
                    )

            except Exception as cleanup_error:

                print(
                    "[DEBUG] temporary MP3 cleanup ERROR:",
                    repr(cleanup_error),
                    flush=True
                )

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

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        if output_dir is None:

            output_dir = os.path.join(
                os.getcwd(),
                "downloads"
            )

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

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

        # --------------------------------------------------
        # yt-dlpで動画＋音声
        # --------------------------------------------------

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
            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name
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
