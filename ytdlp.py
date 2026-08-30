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

        # YouTube JavaScript challenge対応
        "js_runtimes": {
            "deno": {}
        },

        # EJS challenge scripts取得
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
        expected_filename = None

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

            # --------------------------------------------------
            # 情報取得
            # --------------------------------------------------

            print(
                f"[DEBUG] [{mode_name}] Extracting video information...",
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
                f"[DEBUG] [{mode_name}] format_id:",
                info.get("format_id"),
                flush=True
            )

            # --------------------------------------------------
            # 今回のダウンロード予定ファイル
            # --------------------------------------------------

            try:

                expected_filename = (
                    ydl.prepare_filename(info)
                )

                print(
                    f"[DEBUG] [{mode_name}] prepare_filename:",
                    expected_filename,
                    flush=True
                )

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] prepare_filename ERROR:",
                    repr(e),
                    flush=True
                )

            # --------------------------------------------------
            # ダウンロード
            # --------------------------------------------------

            print(
                f"[DEBUG] [{mode_name}] Starting download...",
                flush=True
            )

            ydl.download([
                url
            ])

            print(
                f"[DEBUG] [{mode_name}] download SUCCESS",
                flush=True
            )

            # --------------------------------------------------
            # download後の情報
            # --------------------------------------------------

            try:

                post_info = (
                    ydl.extract_info(
                        url,
                        download=False
                    )
                )

                if post_info:

                    info = post_info

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] post-download info ERROR:",
                    repr(e),
                    flush=True
                )

        # --------------------------------------------------
        # 今回作成されたファイルを確認
        # --------------------------------------------------

        downloaded_file = None

        # ==================================================
        # 1. prepare_filename() で特定
        # ==================================================

        if expected_filename:

            expected_path = Path(
                expected_filename
            )

            print(
                f"[DEBUG] [{mode_name}] expected path:",
                expected_path,
                flush=True
            )

            if expected_path.is_file():

                downloaded_file = (
                    expected_path
                )

                print(
                    f"[DEBUG] [{mode_name}] expected file found:",
                    downloaded_file,
                    flush=True
                )

        # ==================================================
        # 2. merge_output_format がある場合
        # ==================================================

        if (
            downloaded_file is None
            and merge_output_format
            and info
        ):

            video_id = info.get("id")

            if video_id:

                merged_path = (
                    output_dir
                    / f"{video_id}.{merge_output_format}"
                )

                print(
                    f"[DEBUG] [{mode_name}] checking merged file:",
                    merged_path,
                    flush=True
                )

                if merged_path.is_file():

                    downloaded_file = (
                        merged_path
                    )

                    print(
                        f"[DEBUG] [{mode_name}] merged file found:",
                        downloaded_file,
                        flush=True
                    )

        # ==================================================
        # 3. 最終手段
        # ==================================================

        if downloaded_file is None:

            print(
                f"[DEBUG] [{mode_name}] Expected file not found.",
                flush=True
            )

            video_id = (
                info.get("id")
                if info
                else None
            )

            possible_files = []

            if video_id:

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

                print(
                    f"[DEBUG] [{mode_name}] fallback selected:",
                    downloaded_file,
                    flush=True
                )

        # --------------------------------------------------
        # ファイルが見つからない
        # --------------------------------------------------

        if downloaded_file is None:

            print(
                f"[DEBUG] [{mode_name}] Files in output directory:",
                flush=True
            )

            try:

                for p in output_dir.iterdir():

                    if not p.is_file():
                        continue

                    try:

                        size = (
                            p.stat().st_size
                        )

                    except Exception:

                        size = -1

                    print(
                        f"[DEBUG] [{mode_name}] existing file:",
                        p,
                        "size=",
                        size,
                        flush=True
                    )

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] directory listing ERROR:",
                    repr(e),
                    flush=True
                )

            raise FileNotFoundError(
                f"yt-dlpでダウンロードした{mode_name}ファイルを確認できませんでした"
            )

        # --------------------------------------------------
        # 最終確認
        # --------------------------------------------------

        file_size = (
            downloaded_file.stat().st_size
        )

        print(
            f"[DEBUG] [{mode_name}] downloaded file:",
            downloaded_file,
            flush=True
        )

        print(
            f"[DEBUG] [{mode_name}] downloaded file size:",
            file_size,
            flush=True
        )

        if file_size <= 0:

            raise RuntimeError(
                f"{mode_name}ダウンロードファイルのサイズが0です"
            )

        video_id = (
            info.get("id")
            if info
            else None
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

    parts = str(
        value
    ).split(":")

    if len(parts) == 3:

        h = int(
            parts[0]
        )

        m = int(
            parts[1]
        )

        s = float(
            parts[2]
        )

        return (
            h * 3600
            + m * 60
            + s
        )

    if len(parts) == 2:

        m = int(
            parts[0]
        )

        s = float(
            parts[1]
        )

        return (
            m * 60
            + s
        )

    return float(
        value
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

        print(
            "[DEBUG] MP3 source:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] MP3 source suffix:",
            downloaded_file.suffix,
            flush=True
        )

        print(
            "[DEBUG] MP3 source size:",
            downloaded_file.stat().st_size,
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
        # 最終MP3
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

        print(
            "[DEBUG] MP3 target:",
            mp3_file,
            flush=True
        )

        # --------------------------------------------------
        # 入力と出力が同じ場合
        # --------------------------------------------------

        if (
            downloaded_file.resolve()
            == mp3_file.resolve()
        ):

            temporary_mp3_file = (
                output_dir
                / (
                    f"{video_id or 'audio'}"
                    "_converted_temp.mp3"
                )
            )

            ffmpeg_output = (
                temporary_mp3_file
            )

            print(
                "[DEBUG] MP3 source == target",
                flush=True
            )

            print(
                "[DEBUG] MP3 using temporary output:",
                ffmpeg_output,
                flush=True
            )

        else:

            ffmpeg_output = mp3_file

        # --------------------------------------------------
        # FFmpeg
        # --------------------------------------------------

        ffmpeg_command = [
            "ffmpeg",
            "-y"
        ]

        # --------------------------------------------------
        # 開始時間
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 入力
        # --------------------------------------------------

        ffmpeg_command.extend([
            "-i",
            str(downloaded_file)
        ])

        # --------------------------------------------------
        # 終了時間
        # --------------------------------------------------

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

            print(
                "[DEBUG] MP3 end_time specified:",
                end_time,
                flush=True
            )

            ffmpeg_command.extend([
                "-to",
                str(end_time)
            ])

        # --------------------------------------------------
        # MP3
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

        print(
            "[DEBUG] MP3 Starting FFmpeg...",
            flush=True
        )

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

        # --------------------------------------------------
        # FFmpegエラー
        # --------------------------------------------------

        if ffmpeg_result.returncode != 0:

            error_detail = (
                ffmpeg_result.stderr.strip()
                if ffmpeg_result.stderr
                else
                "FFmpegからエラー内容が返されませんでした。"
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
                "[DEBUG] Moving temporary MP3 to final MP3...",
                flush=True
            )

            if mp3_file.exists():

                print(
                    "[DEBUG] Removing old MP3:",
                    mp3_file,
                    flush=True
                )

                mp3_file.unlink()

            temporary_mp3_file.replace(
                mp3_file
            )

            temporary_mp3_file = None

            print(
                "[DEBUG] Temporary MP3 moved successfully",
                flush=True
            )

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
        # 一時MP3削除
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
    output_dir=None,
    start_time=None,
    end_time=None
):

    print("==========================================", flush=True)
    print("[DEBUG] create_mp4 START", flush=True)

    downloaded_file = None
    temporary_mp4_file = None

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

        print(
            "[DEBUG] MP4 start_time:",
            start_time,
            flush=True
        )

        print(
            "[DEBUG] MP4 end_time:",
            end_time,
            flush=True
        )

        # --------------------------------------------------
        # yt-dlp
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

        print(
            "[DEBUG] MP4 video id:",
            video_id,
            flush=True
        )

        print(
            "[DEBUG] MP4 title:",
            video_title,
            flush=True
        )

        # ==================================================
        # 時間指定なし
        # ==================================================

        if (
            start_time is None
            and end_time is None
        ):

            print(
                "[DEBUG] MP4 no time range specified",
                flush=True
            )

            if not downloaded_file.exists():

                raise FileNotFoundError(
                    "MP4ファイルが作成されませんでした"
                )

            file_size = (
                downloaded_file.stat().st_size
            )

            if file_size <= 0:

                raise RuntimeError(
                    "MP4ファイルのサイズが0です"
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

        # ==================================================
        # 時間指定あり
        # ==================================================

        start_seconds = 0

        if start_time is not None:

            start_seconds = _time_to_seconds(
                start_time
            )

        if start_seconds < 0:

            raise ValueError(
                "開始時間は0秒以上にしてください。"
            )

        duration = None

        if end_time is not None:

            end_seconds = _time_to_seconds(
                end_time
            )

            if end_seconds <= start_seconds:

                raise ValueError(
                    "終了時間は開始時間より後にしてください。"
                )

            duration = (
                end_seconds
                - start_seconds
            )

        print(
            "[DEBUG] MP4 start seconds:",
            start_seconds,
            flush=True
        )

        print(
            "[DEBUG] MP4 duration:",
            duration,
            flush=True
        )

        # --------------------------------------------------
        # 最終MP4
        # --------------------------------------------------

        if video_id:

            mp4_file = (
                output_dir
                / f"{video_id}.mp4"
            )

        else:

            mp4_file = (
                downloaded_file.with_suffix(
                    ".mp4"
                )
            )

        print(
            "[DEBUG] MP4 target:",
            mp4_file,
            flush=True
        )

        # --------------------------------------------------
        # 入力と出力が同じ場合
        # --------------------------------------------------

        if (
            downloaded_file.resolve()
            ==
            mp4_file.resolve()
        ):

            temporary_mp4_file = (
                output_dir
                /
                (
                    f"{video_id or 'video'}"
                    "_trim_temp.mp4"
                )
            )

            ffmpeg_output = (
                temporary_mp4_file
            )

            print(
                "[DEBUG] MP4 source == target",
                flush=True
            )

            print(
                "[DEBUG] MP4 using temporary output:",
                ffmpeg_output,
                flush=True
            )

        else:

            ffmpeg_output = (
                mp4_file
            )

        # ==================================================
        # FFmpeg
        # ==================================================

        ffmpeg_command = [
            "ffmpeg",
            "-y"
        ]

        # --------------------------------------------------
        # 開始位置
        # --------------------------------------------------

        if start_seconds > 0:

            ffmpeg_command.extend([
                "-ss",
                str(start_seconds)
            ])

        # --------------------------------------------------
        # 入力
        # --------------------------------------------------

        ffmpeg_command.extend([
            "-i",
            str(downloaded_file)
        ])

        # --------------------------------------------------
        # 長さ
        # --------------------------------------------------

        if duration is not None:

            ffmpeg_command.extend([
                "-t",
                str(duration)
            ])

        # --------------------------------------------------
        # MP4出力設定
        # --------------------------------------------------

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
            "[DEBUG] MP4 FFmpeg command:",
            " ".join(
                ffmpeg_command
            ),
            flush=True
        )

        print(
            "[DEBUG] MP4 Starting FFmpeg...",
            flush=True
        )

        ffmpeg_result = subprocess.run(
            ffmpeg_command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        print(
            "[DEBUG] MP4 FFmpeg returncode:",
            ffmpeg_result.returncode,
            flush=True
        )

        if ffmpeg_result.stdout:

            print(
                "[DEBUG] MP4 FFmpeg stdout:",
                ffmpeg_result.stdout,
                flush=True
            )

        if ffmpeg_result.stderr:

            print(
                "[DEBUG] MP4 FFmpeg stderr:",
                ffmpeg_result.stderr,
                flush=True
            )

        # --------------------------------------------------
        # FFmpegエラー
        # --------------------------------------------------

        if ffmpeg_result.returncode != 0:

            error_detail = (
                ffmpeg_result.stderr.strip()
                if ffmpeg_result.stderr
                else
                "FFmpegからエラー内容が返されませんでした。"
            )

            raise RuntimeError(
                "MP4 FFmpeg conversion failed\n"
                + error_detail
            )

        # --------------------------------------------------
        # 一時ファイル → 最終ファイル
        # --------------------------------------------------

        if temporary_mp4_file:

            print(
                "[DEBUG] Moving temporary MP4 to final MP4...",
                flush=True
            )

            if mp4_file.exists():

                print(
                    "[DEBUG] Removing old MP4:",
                    mp4_file,
                    flush=True
                )

                mp4_file.unlink()

            temporary_mp4_file.replace(
                mp4_file
            )

            temporary_mp4_file = None

            print(
                "[DEBUG] Temporary MP4 moved successfully",
                flush=True
            )

        # --------------------------------------------------
        # 完成確認
        # --------------------------------------------------

        if not mp4_file.exists():

            raise FileNotFoundError(
                "MP4ファイルが作成されませんでした"
            )

        mp4_size = (
            mp4_file.stat().st_size
        )

        print(
            "[DEBUG] MP4 final file:",
            mp4_file,
            flush=True
        )

        print(
            "[DEBUG] MP4 final size:",
            mp4_size,
            flush=True
        )

        if mp4_size <= 0:

            raise RuntimeError(
                "MP4ファイルのサイズが0です"
            )

        # --------------------------------------------------
        # 元ファイル削除
        # --------------------------------------------------

        if (
            downloaded_file.exists()
            and
            downloaded_file.resolve()
            !=
            mp4_file.resolve()
        ):

            print(
                "[DEBUG] Removing MP4 source:",
                downloaded_file,
                flush=True
            )

            downloaded_file.unlink()

            print(
                "[DEBUG] MP4 source removed",
                flush=True
            )

        result = {
            "path":
                str(mp4_file),

            "filename":
                mp4_file.name
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

        # --------------------------------------------------
        # 一時MP4削除
        # --------------------------------------------------

        if temporary_mp4_file:

            try:

                if temporary_mp4_file.exists():

                    temporary_mp4_file.unlink()

                    print(
                        "[DEBUG] temporary MP4 removed",
                        flush=True
                    )

            except Exception as cleanup_error:

                print(
                    "[DEBUG] temporary MP4 cleanup ERROR:",
                    repr(cleanup_error),
                    flush=True
                )

        print(
            "[DEBUG] create_mp4 END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )
