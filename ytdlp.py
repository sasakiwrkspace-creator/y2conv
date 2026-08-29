import sys
import os
import traceback
import shutil
import subprocess
import tempfile
from pathlib import Path


# ============================================================
# 起動時デバッグ
# ============================================================

print("==========================================", flush=True)
print("[DEBUG] ytdlp.py loaded", flush=True)

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
    "[DEBUG] ytdlp module loading...",
    flush=True
)


# ============================================================
# yt-dlp import
# ============================================================

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

    print(
        "[DEBUG] yt_dlp exception type:",
        type(e).__name__,
        flush=True
    )

    traceback.print_exc()

    raise


# ============================================================
# Deno確認
# ============================================================

print(
    "[DEBUG] deno path:",
    shutil.which("deno"),
    flush=True
)

try:

    deno_result = subprocess.run(
        ["deno", "--version"],
        capture_output=True,
        text=True,
        timeout=10
    )

    print(
        "[DEBUG] deno returncode:",
        deno_result.returncode,
        flush=True
    )

    print(
        "[DEBUG] deno stdout:",
        deno_result.stdout,
        flush=True
    )

    print(
        "[DEBUG] deno stderr:",
        deno_result.stderr,
        flush=True
    )

except Exception as e:

    print(
        "[DEBUG] deno execution ERROR:",
        repr(e),
        flush=True
    )

    print(
        "[DEBUG] deno exception type:",
        type(e).__name__,
        flush=True
    )

    traceback.print_exc()


# ============================================================
# yt-dlp-ejs確認
# ============================================================

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

    print(
        "[DEBUG] yt_dlp_ejs exception type:",
        type(e).__name__,
        flush=True
    )

    traceback.print_exc()


print("==========================================", flush=True)


# ============================================================
# 共通：YouTubeダウンロード
# ============================================================

def _download_youtube(
    url,
    output_dir,
    format_selector,
    merge_output_format=None
):

    print("==========================================", flush=True)
    print("[DEBUG] _download_youtube START", flush=True)

    temporary_cookie_path = None

    try:

        # ----------------------------------------------------
        # 引数確認
        # ----------------------------------------------------

        print(
            "[DEBUG] download URL:",
            url,
            flush=True
        )

        print(
            "[DEBUG] download output_dir:",
            output_dir,
            flush=True
        )

        print(
            "[DEBUG] download format:",
            format_selector,
            flush=True
        )

        print(
            "[DEBUG] download merge_output_format:",
            merge_output_format,
            flush=True
        )

        if not url:

            print(
                "[DEBUG] ERROR: URL is empty",
                flush=True
            )

            raise ValueError(
                "YouTube URLが空です"
            )

        # ----------------------------------------------------
        # 出力ディレクトリ
        # ----------------------------------------------------

        if output_dir is None:

            output_dir = os.path.join(
                os.getcwd(),
                "downloads"
            )

            print(
                "[DEBUG] output_dir was None",
                flush=True
            )

            print(
                "[DEBUG] using default output_dir:",
                output_dir,
                flush=True
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
            "[DEBUG] output directory created/exists:",
            output_dir.exists(),
            flush=True
        )

        print(
            "[DEBUG] output directory is directory:",
            output_dir.is_dir(),
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

        # ----------------------------------------------------
        # Cookie
        # ----------------------------------------------------

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

        if os.path.isfile(cookies_source):

            print(
                "[DEBUG] cookies file detected",
                flush=True
            )

            print(
                "[DEBUG] cookies source size:",
                os.path.getsize(
                    cookies_source
                ),
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

            print(
                "[DEBUG] temporary cookie path:",
                temporary_cookie_path,
                flush=True
            )

            shutil.copyfile(
                cookies_source,
                temporary_cookie_path
            )

            print(
                "[DEBUG] temporary cookies copied",
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

        # ----------------------------------------------------
        # yt-dlp設定
        # ----------------------------------------------------

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

            "format": format_selector,

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

            print(
                "[DEBUG] merge_output_format enabled:",
                merge_output_format,
                flush=True
            )

        else:

            print(
                "[DEBUG] merge_output_format NOT enabled",
                flush=True
            )

        if temporary_cookie_path:

            ydl_opts["cookiefile"] = (
                temporary_cookie_path
            )

            print(
                "[DEBUG] cookiefile option enabled",
                flush=True
            )

            print(
                "[DEBUG] cookiefile:",
                temporary_cookie_path,
                flush=True
            )

        else:

            print(
                "[DEBUG] cookiefile option NOT enabled",
                flush=True
            )

        # ----------------------------------------------------
        # yt-dlp設定確認
        # ----------------------------------------------------

        print(
            "[DEBUG] ==========================================",
            flush=True
        )

        print(
            "[DEBUG] yt-dlp options prepared",
            flush=True
        )

        print(
            "[DEBUG] outtmpl:",
            ydl_opts.get("outtmpl"),
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
            "[DEBUG] quiet:",
            ydl_opts.get("quiet"),
            flush=True
        )

        print(
            "[DEBUG] verbose:",
            ydl_opts.get("verbose"),
            flush=True
        )

        print(
            "[DEBUG] merge_output_format:",
            ydl_opts.get("merge_output_format"),
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

        print(
            "[DEBUG] ==========================================",
            flush=True
        )

        # ----------------------------------------------------
        # yt-dlp実行
        # ----------------------------------------------------

        info = None

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
                    "[DEBUG] Starting extract_info()",
                    flush=True
                )

                print(
                    "[DEBUG] Connecting to YouTube...",
                    flush=True
                )

                print(
                    "[DEBUG] URL passed to yt-dlp:",
                    url,
                    flush=True
                )

                # --------------------------------------------
                # YouTubeアクセス開始
                # --------------------------------------------

                info = ydl.extract_info(
                    url,
                    download=True
                )

                # --------------------------------------------
                # YouTubeアクセス成功
                # --------------------------------------------

                print(
                    "[DEBUG] extract_info(download=True) SUCCESS",
                    flush=True
                )

                if info is None:

                    print(
                        "[DEBUG] ERROR: extract_info returned None",
                        flush=True
                    )

                    raise RuntimeError(
                        "extract_info() returned None"
                    )

                print(
                    "[DEBUG] info received:",
                    bool(info),
                    flush=True
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
                    "[DEBUG] original ext:",
                    info.get("ext"),
                    flush=True
                )

                print(
                    "[DEBUG] requested formats:",
                    info.get("requested_formats"),
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
                "[DEBUG] yt-dlp traceback:",
                flush=True
            )

            traceback.print_exc()

            raise

        # ----------------------------------------------------
        # ダウンロードファイル検索
        # ----------------------------------------------------

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

        downloaded_file = None

        if video_id:

            print(
                "[DEBUG] Searching files by video ID...",
                flush=True
            )

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

                try:

                    candidate_size = (
                        candidate.stat().st_size
                    )

                except Exception:

                    candidate_size = "UNKNOWN"

                print(
                    "[DEBUG] candidate:",
                    candidate,
                    "size=",
                    candidate_size,
                    flush=True
                )

                if not candidate.is_file():

                    print(
                        "[DEBUG] candidate skipped: not a file",
                        flush=True
                    )

                    continue

                if candidate.suffix.lower() in [
                    ".part",
                    ".ytdl",
                    ".temp"
                ]:

                    print(
                        "[DEBUG] candidate skipped: temporary file",
                        flush=True
                    )

                    continue

                downloaded_file = candidate

                print(
                    "[DEBUG] candidate selected:",
                    candidate,
                    flush=True
                )

                break

        # ----------------------------------------------------
        # video IDで見つからなかった場合
        # ----------------------------------------------------

        if downloaded_file is None:

            print(
                "[DEBUG] No file found by video ID",
                flush=True
            )

            print(
                "[DEBUG] Listing all files in output directory...",
                flush=True
            )

            try:

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

                    try:

                        file_size = (
                            p.stat().st_size
                        )

                    except Exception:

                        file_size = "UNKNOWN"

                    print(
                        "[DEBUG] existing file:",
                        p,
                        "size=",
                        file_size,
                        flush=True
                    )

            except Exception as e:

                print(
                    "[DEBUG] Failed to list output directory:",
                    repr(e),
                    flush=True
                )

        # ----------------------------------------------------
        # ファイルが見つからない
        # ----------------------------------------------------

        if downloaded_file is None:

            print(
                "[DEBUG] ERROR: downloaded file not found",
                flush=True
            )

            raise FileNotFoundError(
                "yt-dlpでダウンロードしたファイルを確認できませんでした"
            )

        # ----------------------------------------------------
        # ダウンロードファイル確認
        # ----------------------------------------------------

        print(
            "[DEBUG] downloaded file:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] downloaded file exists:",
            downloaded_file.exists(),
            flush=True
        )

        print(
            "[DEBUG] downloaded file suffix:",
            downloaded_file.suffix,
            flush=True
        )

        print(
            "[DEBUG] downloaded file size:",
            downloaded_file.stat().st_size,
            flush=True
        )

        print(
            "[DEBUG] _download_youtube SUCCESS",
            flush=True
        )

        return downloaded_file

    except Exception as e:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[DEBUG] _download_youtube ERROR:",
            repr(e),
            flush=True
        )

        print(
            "[DEBUG] _download_youtube exception type:",
            type(e).__name__,
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        # ----------------------------------------------------
        # 一時Cookie削除
        # ----------------------------------------------------

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
            "[DEBUG] _download_youtube END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ============================================================
# MP3作成
# ============================================================

def create_mp3(
    url,
    output_dir=None,
    start_time=None,
    end_time=None
):

    print("==========================================", flush=True)
    print("[DEBUG] create_mp3 START", flush=True)

    temporary_downloaded_file = None

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

        # ----------------------------------------------------
        # YouTubeから音声取得
        # ----------------------------------------------------

        print(
            "[DEBUG] MP3: starting common YouTube download",
            flush=True
        )

        downloaded_file = _download_youtube(
            url=url,
            output_dir=output_dir,
            format_selector="bestaudio/best",
            merge_output_format=None
        )

        temporary_downloaded_file = downloaded_file

        print(
            "[DEBUG] MP3: common YouTube download SUCCESS",
            flush=True
        )

        print(
            "[DEBUG] MP3 source file:",
            downloaded_file,
            flush=True
        )

        # ----------------------------------------------------
        # MP3出力先
        # ----------------------------------------------------

        mp3_file = downloaded_file.with_suffix(
            ".mp3"
        )

        print(
            "[DEBUG] MP3 target:",
            mp3_file,
            flush=True
        )

        # ----------------------------------------------------
        # FFmpeg
        # ----------------------------------------------------

        print(
            "[DEBUG] MP3 Starting FFmpeg conversion...",
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

        # ----------------------------------------------------
        # 時間指定
        # ----------------------------------------------------

        if start_time:

            print(
                "[DEBUG] MP3 start_time detected:",
                start_time,
                flush=True
            )

        if end_time:

            print(
                "[DEBUG] MP3 end_time detected:",
                end_time,
                flush=True
            )

        # 現段階では元コードと同様、
        # start_time / end_time はログ確認のみ。
        #
        # 時間切り出し処理を追加する場合は、
        # ここでFFmpegオプションを追加します。

        ffmpeg_command.append(
            str(mp3_file)
        )

        print(
            "[DEBUG] MP3 FFmpeg command:",
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

        except Exception as e:

            print(
                "[DEBUG] MP3 FFmpeg ERROR:",
                repr(e),
                flush=True
            )

            print(
                "[DEBUG] MP3 FFmpeg exception type:",
                type(e).__name__,
                flush=True
            )

            traceback.print_exc()

            raise

        # ----------------------------------------------------
        # MP3確認
        # ----------------------------------------------------

        print(
            "[DEBUG] MP3 FFmpeg conversion SUCCESS",
            flush=True
        )

        print(
            "[DEBUG] MP3 exists:",
            mp3_file.exists(),
            flush=True
        )

        if not mp3_file.exists():

            raise FileNotFoundError(
                "MP3ファイルが作成されませんでした"
            )

        print(
            "[DEBUG] MP3 size:",
            mp3_file.stat().st_size,
            flush=True
        )

        # ----------------------------------------------------
        # 元ファイル削除
        # ----------------------------------------------------

        if downloaded_file.exists():

            print(
                "[DEBUG] MP3 removing source file:",
                downloaded_file,
                flush=True
            )

            try:

                downloaded_file.unlink()

                print(
                    "[DEBUG] MP3 source file removed",
                    flush=True
                )

            except Exception as e:

                print(
                    "[DEBUG] MP3 source file removal ERROR:",
                    repr(e),
                    flush=True
                )

        # ----------------------------------------------------
        # 戻り値
        # ----------------------------------------------------

        result_path = str(
            mp3_file
        )

        print(
            "[DEBUG] MP3 result:",
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
            "[DEBUG] create_mp3 exception type:",
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


# ============================================================
# MP4作成
# ============================================================

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

        if not url:

            print(
                "[DEBUG] MP4 ERROR: URL is empty",
                flush=True
            )

            raise ValueError(
                "YouTube URLが空です"
            )

        # ----------------------------------------------------
        # YouTubeから動画+音声取得
        # ----------------------------------------------------

        print(
            "[DEBUG] MP4: starting common YouTube download",
            flush=True
        )

        downloaded_file = _download_youtube(
            url=url,
            output_dir=output_dir,
            format_selector="bv*+ba/b",
            merge_output_format="mp4"
        )

        print(
            "[DEBUG] MP4: common YouTube download SUCCESS",
            flush=True
        )

        print(
            "[DEBUG] MP4 downloaded file:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] MP4 downloaded file exists:",
            downloaded_file.exists(),
            flush=True
        )

        print(
            "[DEBUG] MP4 downloaded file size:",
            downloaded_file.stat().st_size,
            flush=True
        )

        # ----------------------------------------------------
        # MP4確認
        # ----------------------------------------------------

        if downloaded_file.suffix.lower() != ".mp4":

            print(
                "[DEBUG] WARNING: downloaded file is not .mp4:",
                downloaded_file.suffix,
                flush=True
            )

        else:

            print(
                "[DEBUG] MP4 extension confirmed",
                flush=True
            )

        print(
            "[DEBUG] MP4 create SUCCESS",
            flush=True
        )

        return str(
            downloaded_file
        )

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
            "[DEBUG] create_mp4 exception type:",
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
