import sys
import os
import traceback
import shutil
import subprocess
import tempfile
from pathlib import Path

print("==========================================", flush=True)
print("[DEBUG] ytdlp.py loaded", flush=True)
print("[DEBUG] Python:", sys.version, flush=True)
print("[DEBUG] yt-dlp module loading...", flush=True)

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
            "[DEBUG] start_time:",
            start_time,
            flush=True
        )

        print(
            "[DEBUG] end_time:",
            end_time,
            flush=True
        )

        if not url:
            raise ValueError(
                "YouTube URLが空です"
            )

        if output_dir is None:
            output_dir = os.path.join(
                os.getcwd(),
                "downloads"
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
            os.access(
                output_dir,
                os.W_OK
            ),
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
            os.path.isfile(
                cookies_source
            ),
            flush=True
        )

        temporary_cookie_file = None

        if os.path.isfile(cookies_source):
            print(
                "[DEBUG] cookies file detected",
                flush=True
            )

            print(
                "[DEBUG] creating temporary cookies file...",
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
                os.path.getsize(
                    temporary_cookie_path
                ),
                flush=True
            )

        else:
            print(
                "[DEBUG] WARNING: cookies file does not exist",
                flush=True
            )

            temporary_cookie_path = None

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
            "format": "bestaudio/best",
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

        if temporary_cookie_path:
            ydl_opts["cookiefile"] = (
                temporary_cookie_path
            )

            print(
                "[DEBUG] cookiefile option enabled",
                flush=True
            )

        else:
            print(
                "[DEBUG] cookiefile option NOT enabled",
                flush=True
            )

        print(
            "[DEBUG] yt-dlp options prepared",
            flush=True
        )

        print(
            "[DEBUG] format:",
            ydl_opts.get("format"),
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

        info = None
        downloaded_file = None

        try:
            print(
                "[DEBUG] Creating YoutubeDL instance...",
                flush=True
            )

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                print(
                    "[DEBUG] YoutubeDL instance created",
                    flush=True
                )

                print(
                    "[DEBUG] ==========================================",
                    flush=True
                )

                print(
                    "[DEBUG] Starting extract_info()",
                    flush=True
                )

                print(
                    "[DEBUG] Connecting to YouTube...",
                    flush=True
                )

                info = ydl.extract_info(
                    url,
                    download=False
                )

                print(
                    "[DEBUG] extract_info() SUCCESS",
                    flush=True
                )

                if info is None:
                    raise RuntimeError(
                        "extract_info() returned None"
                    )

                print(
                    "[DEBUG] video id:",
                    info.get("id"),
                    flush=True
                )

                print(
                    "[DEBUG] video title:",
                    info.get("title"),
                    flush=True
                )

                print(
                    "[DEBUG] duration:",
                    info.get("duration"),
                    flush=True
                )

                print(
                    "[DEBUG] webpage_url:",
                    info.get("webpage_url"),
                    flush=True
                )

                print(
                    "[DEBUG] extractor:",
                    info.get("extractor"),
                    flush=True
                )

                print(
                    "[DEBUG] ==========================================",
                    flush=True
                )

                print(
                    "[DEBUG] Starting download...",
                    flush=True
                )

                downloaded_info = ydl.extract_info(
                    url,
                    download=True
                )

                print(
                    "[DEBUG] download SUCCESS",
                    flush=True
                )

                if downloaded_info:
                    info = downloaded_info

                print(
                    "[DEBUG] downloaded info received:",
                    bool(info),
                    flush=True
                )

        except Exception as e:
            print(
                "[DEBUG] yt-dlp PROCESS ERROR:",
                repr(e),
                flush=True
            )

            print(
                "[DEBUG] yt-dlp exception type:",
                type(e).__name__,
                flush=True
            )

            print(
                "[DEBUG] traceback:",
                flush=True
            )

            traceback.print_exc()

            raise

        print(
            "[DEBUG] Searching downloaded files...",
            flush=True
        )

        video_id = None

        if info:
            video_id = info.get("id")

        print(
            "[DEBUG] video_id:",
            video_id,
            flush=True
        )

        if video_id:
            candidates = list(
                output_dir.glob(
                    video_id + ".*"
                )
            )

            print(
                "[DEBUG] candidate files:",
                len(candidates),
                flush=True
            )

            for candidate in candidates:
                print(
                    "[DEBUG] candidate:",
                    candidate,
                    "size=",
                    candidate.stat().st_size,
                    flush=True
                )

                if candidate.is_file():
                    downloaded_file = candidate
                    break

        if downloaded_file is None:
            print(
                "[DEBUG] No file found by video ID",
                flush=True
            )

            all_files = [
                p
                for p in output_dir.iterdir()
                if p.is_file()
            ]

            print(
                "[DEBUG] files in output directory:",
                len(all_files),
                flush=True
            )

            for p in all_files:
                print(
                    "[DEBUG] existing file:",
                    p,
                    "size=",
                    p.stat().st_size,
                    flush=True
                )

        if downloaded_file is None:
            raise FileNotFoundError(
                "yt-dlpでダウンロードしたファイルを確認できませんでした"
            )

        print(
            "[DEBUG] downloaded file:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] downloaded file size:",
            downloaded_file.stat().st_size,
            flush=True
        )

        mp3_file = downloaded_file.with_suffix(
            ".mp3"
        )

        print(
            "[DEBUG] target MP3:",
            mp3_file,
            flush=True
        )

        print(
            "[DEBUG] Starting FFmpeg conversion...",
            flush=True
        )

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i",
            str(downloaded_file),
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "2",
        ]

        if start_time:
            print(
                "[DEBUG] start_time detected:",
                start_time,
                flush=True
            )

        if end_time:
            print(
                "[DEBUG] end_time detected:",
                end_time,
                flush=True
            )

        ffmpeg_command.append(
            str(mp3_file)
        )

        print(
            "[DEBUG] FFmpeg command:",
            " ".join(ffmpeg_command),
            flush=True
        )

        try:
            ffmpeg_result = subprocess.run(
                ffmpeg_command,
                capture_output=True,
                text=True
            )

            print(
                "[DEBUG] FFmpeg returncode:",
                ffmpeg_result.returncode,
                flush=True
            )

            if ffmpeg_result.stdout:
                print(
                    "[DEBUG] FFmpeg stdout:",
                    ffmpeg_result.stdout,
                    flush=True
                )

            if ffmpeg_result.stderr:
                print(
                    "[DEBUG] FFmpeg stderr:",
                    ffmpeg_result.stderr,
                    flush=True
                )

            if ffmpeg_result.returncode != 0:
                raise RuntimeError(
                    "FFmpeg conversion failed"
                )

        except Exception as e:
            print(
                "[DEBUG] FFmpeg ERROR:",
                repr(e),
                flush=True
            )

            traceback.print_exc()
            raise

        print(
            "[DEBUG] FFmpeg conversion SUCCESS",
            flush=True
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

        if downloaded_file.exists():
            print(
                "[DEBUG] Removing source file:",
                downloaded_file,
                flush=True
            )

            try:
                downloaded_file.unlink()

                print(
                    "[DEBUG] Source file removed",
                    flush=True
                )

            except Exception as e:
                print(
                    "[DEBUG] Source file removal ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            "[DEBUG] Preparing return value...",
            flush=True
        )

        result_path = str(mp3_file)

        print(
            "[DEBUG] result:",
            result_path,
            flush=True
        )

        print(
            "[DEBUG] create_mp3 SUCCESS",
            flush=True
        )

        return result_path

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
            "[DEBUG] exception type:",
            type(e).__name__,
            flush=True
        )

        traceback.print_exc()

        raise

    finally:
        if "temporary_cookie_path" in locals():
            if temporary_cookie_path:
                print(
                    "[DEBUG] Removing temporary cookies...",
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
                            "[DEBUG] Temporary cookies removed",
                            flush=True
                        )
                    else:
                        print(
                            "[DEBUG] Temporary cookies already absent",
                            flush=True
                        )

                except Exception as e:
                    print(
                        "[DEBUG] Temporary cookies removal ERROR:",
                        repr(e),
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
