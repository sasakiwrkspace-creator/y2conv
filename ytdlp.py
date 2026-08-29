import sys
import os
import traceback
import shutil
import tempfile
from pathlib import Path

import yt_dlp


# ==========================================================
# 起動時 DEBUG
# ==========================================================

print("==========================================", flush=True)
print("[DEBUG] ytdlp.py loaded", flush=True)
print("[DEBUG] Python:", sys.version, flush=True)
print("[DEBUG] Python executable:", sys.executable, flush=True)
print("[DEBUG] Current working directory:", os.getcwd(), flush=True)

try:
    print(
        "[DEBUG] yt-dlp version:",
        yt_dlp.version.__version__,
        flush=True
    )
except Exception:
    pass

print(
    "[DEBUG] yt-dlp location:",
    yt_dlp.__file__,
    flush=True
)


# ==========================================================
# Deno確認
# ==========================================================

print(
    "[DEBUG] deno path:",
    shutil.which("deno"),
    flush=True
)

try:

    result = shutil.which("deno")

    if result:

        import subprocess

        deno_result = subprocess.run(
            ["deno", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(
            "[DEBUG] deno version:",
            deno_result.stdout,
            flush=True
        )

    else:

        print(
            "[DEBUG] deno is not installed",
            flush=True
        )

except Exception as e:

    print(
        "[DEBUG] deno check ERROR:",
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

    if not os.path.isfile(cookies_source):

        print(
            "[DEBUG] cookies file does not exist",
            flush=True
        )

        return None

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
            "[DEBUG] temporary cookies created:",
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


# ==========================================================
# 共通：yt-dlpオプション
# ==========================================================

def _build_ydl_options(
    output_dir,
    format_string,
    merge_output_format=None,
    temporary_cookie_path=None,
    postprocessors=None
):

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    download_template = str(
        output_dir / "%(id)s.%(ext)s"
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

        # JavaScript challenge対策
        "js_runtimes": {
            "deno": {}
        },

        "remote_components": {
            "ejs:github"
        },

        # メタデータ
        "writethumbnail":
            False,

        "addmetadata":
            True,

    }

    if merge_output_format:

        ydl_opts[
            "merge_output_format"
        ] = merge_output_format

    if temporary_cookie_path:

        ydl_opts[
            "cookiefile"
        ] = temporary_cookie_path

    if postprocessors:

        ydl_opts[
            "postprocessors"
        ] = postprocessors

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
        ydl_opts.get(
            "merge_output_format"
        ),
        flush=True
    )

    print(
        "[DEBUG] postprocessors:",
        ydl_opts.get(
            "postprocessors"
        ),
        flush=True
    )

    print(
        "[DEBUG] cookiefile enabled:",
        bool(
            ydl_opts.get("cookiefile")
        ),
        flush=True
    )

    return ydl_opts


# ==========================================================
# 共通：yt-dlp実行
# ==========================================================

def _download_with_ytdlp(
    url,
    output_dir,
    format_string,
    merge_output_format=None,
    mode_name="UNKNOWN",
    postprocessors=None
):

    print("==========================================", flush=True)

    print(
        f"[DEBUG] _download_with_ytdlp START [{mode_name}]",
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
            temporary_cookie_path=temporary_cookie_path,
            postprocessors=postprocessors
        )

        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

        info = None

        print(
            f"[DEBUG] [{mode_name}] Creating YoutubeDL...",
            flush=True
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                f"[DEBUG] [{mode_name}] extract_info START",
                flush=True
            )

            info = ydl.extract_info(
                url,
                download=True
            )

            print(
                f"[DEBUG] [{mode_name}] extract_info SUCCESS",
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
                f"[DEBUG] [{mode_name}] title:",
                info.get("title"),
                flush=True
            )

            print(
                f"[DEBUG] [{mode_name}] ext:",
                info.get("ext"),
                flush=True
            )

        # --------------------------------------------------
        # video ID
        # --------------------------------------------------

        video_id = info.get("id")

        if not video_id:

            raise RuntimeError(
                f"{mode_name}: YouTube video IDを取得できませんでした"
            )

        # --------------------------------------------------
        # ファイル検索
        # --------------------------------------------------

        print(
            f"[DEBUG] [{mode_name}] Searching files...",
            flush=True
        )

        candidates = []

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

                if path.stat().st_size <= 0:
                    continue

            except Exception:
                continue

            candidates.append(
                path
            )

        # 新しいものを優先
        candidates.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        print(
            f"[DEBUG] [{mode_name}] candidates:",
            candidates,
            flush=True
        )

        downloaded_file = None

        if candidates:

            downloaded_file = candidates[0]

        # --------------------------------------------------
        # 見つからない場合
        # --------------------------------------------------

        if downloaded_file is None:

            print(
                f"[DEBUG] [{mode_name}] No file found by video ID",
                flush=True
            )

            for path in output_dir.iterdir():

                if not path.is_file():
                    continue

                print(
                    f"[DEBUG] [{mode_name}] existing:",
                    path,
                    "size=",
                    path.stat().st_size,
                    flush=True
                )

            raise FileNotFoundError(
                f"{mode_name}ファイルを確認できませんでした"
            )

        print(
            f"[DEBUG] [{mode_name}] selected:",
            downloaded_file,
            flush=True
        )

        print(
            f"[DEBUG] [{mode_name}] size:",
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
                        f"[DEBUG] [{mode_name}] temporary cookie removed",
                        flush=True
                    )

            except Exception as e:

                print(
                    f"[DEBUG] [{mode_name}] cookie cleanup ERROR:",
                    repr(e),
                    flush=True
                )

        print(
            f"[DEBUG] _download_with_ytdlp END [{mode_name}]",
            flush=True
        )

        print(
            "==========================================",
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
        # MP3用PostProcessor
        #
        # yt-dlpにMP3変換を任せる
        # --------------------------------------------------

        postprocessors = [

            {
                "key":
                    "FFmpegExtractAudio",

                "preferredcodec":
                    "mp3",

                "preferredquality":
                    "192",
            },

            {
                "key":
                    "FFmpegMetadata",
            }

        ]

        print(
            "[DEBUG] MP3 postprocessors:",
            postprocessors,
            flush=True
        )

        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

        result = _download_with_ytdlp(
            url=url,
            output_dir=output_dir,
            format_string="bestaudio/best",
            merge_output_format=None,
            mode_name="MP3",
            postprocessors=postprocessors
        )

        info = result.get(
            "info"
        ) or {}

        video_id = (
            info.get("id")
            or result.get("video_id")
        )

        video_title = (
            info.get("title")
            or "YouTube Audio"
        )

        print(
            "[DEBUG] MP3 video_id:",
            video_id,
            flush=True
        )

        print(
            "[DEBUG] MP3 title:",
            video_title,
            flush=True
        )

        # --------------------------------------------------
        # MP3ファイルを再検索
        #
        # FFmpegExtractAudio後に拡張子がmp3になるため
        # 最終的なファイルを取得する
        # --------------------------------------------------

        mp3_file = None

        if video_id:

            mp3_candidates = list(
                output_dir.glob(
                    video_id + ".mp3"
                )
            )

            if mp3_candidates:

                mp3_candidates.sort(
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )

                mp3_file = (
                    mp3_candidates[0]
                )

        # --------------------------------------------------
        # 念のためresultのファイルも確認
        # --------------------------------------------------

        if mp3_file is None:

            result_file = Path(
                result["path"]
            )

            if (
                result_file.exists()
                and result_file.suffix.lower()
                == ".mp3"
            ):

                mp3_file = result_file

        # --------------------------------------------------
        # 最終検索
        # --------------------------------------------------

        if mp3_file is None:

            all_mp3 = list(
                output_dir.glob(
                    "*.mp3"
                )
            )

            all_mp3 = [
                p
                for p in all_mp3
                if p.is_file()
                and p.stat().st_size > 0
            ]

            all_mp3.sort(
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if all_mp3:

                mp3_file = all_mp3[0]

        # --------------------------------------------------
        # MP3がない
        # --------------------------------------------------

        if mp3_file is None:

            raise FileNotFoundError(
                "yt-dlpでMP3ファイルを作成できませんでした"
            )

        # --------------------------------------------------
        # サイズ確認
        # --------------------------------------------------

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
        # 時間指定について
        # --------------------------------------------------

        if start_time or end_time:

            print(
                "[DEBUG] MP3 time range requested:",
                start_time,
                "~",
                end_time,
                flush=True
            )

            print(
                "[DEBUG] 現在のテスト段階ではMP3ダウンロードを優先します。",
                flush=True
            )

        # --------------------------------------------------
        # 結果
        # --------------------------------------------------

        final_result = {

            "path":
                str(mp3_file),

            "filename":
                mp3_file.name
        }

        print(
            "[DEBUG] MP3 result:",
            final_result,
            flush=True
        )

        print(
            "[DEBUG] create_mp3 SUCCESS",
            flush=True
        )

        return final_result

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
        # MP4用PostProcessor
        # --------------------------------------------------

        postprocessors = [

            {
                "key":
                    "FFmpegMetadata"
            }

        ]

        # --------------------------------------------------
        # yt-dlp
        # --------------------------------------------------

        result = _download_with_ytdlp(
            url=url,
            output_dir=output_dir,
            format_string="bv*+ba/b",
            merge_output_format="mp4",
            mode_name="MP4",
            postprocessors=postprocessors
        )

        info = result.get(
            "info"
        ) or {}

        video_id = (
            info.get("id")
            or result.get("video_id")
        )

        # --------------------------------------------------
        # MP4再検索
        # --------------------------------------------------

        mp4_file = None

        if video_id:

            candidates = list(
                output_dir.glob(
                    video_id + ".mp4"
                )
            )

            candidates = [
                p
                for p in candidates
                if p.is_file()
                and p.stat().st_size > 0
            ]

            candidates.sort(
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if candidates:

                mp4_file = (
                    candidates[0]
                )

        # --------------------------------------------------
        # resultのファイル
        # --------------------------------------------------

        if mp4_file is None:

            result_file = Path(
                result["path"]
            )

            if (
                result_file.exists()
                and result_file.suffix.lower()
                == ".mp4"
            ):

                mp4_file = result_file

        # --------------------------------------------------
        # 最終検索
        # --------------------------------------------------

        if mp4_file is None:

            all_mp4 = list(
                output_dir.glob(
                    "*.mp4"
                )
            )

            all_mp4 = [
                p
                for p in all_mp4
                if p.is_file()
                and p.stat().st_size > 0
            ]

            all_mp4.sort(
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if all_mp4:

                mp4_file = all_mp4[0]

        # --------------------------------------------------
        # MP4がない
        # --------------------------------------------------

        if mp4_file is None:

            raise FileNotFoundError(
                "yt-dlpでMP4ファイルを作成できませんでした"
            )

        # --------------------------------------------------
        # サイズ確認
        # --------------------------------------------------

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
        # 結果
        # --------------------------------------------------

        final_result = {

            "path":
                str(mp4_file),

            "filename":
                mp4_file.name
        }

        print(
            "[DEBUG] MP4 result:",
            final_result,
            flush=True
        )

        print(
            "[DEBUG] create_mp4 SUCCESS",
            flush=True
        )

        return final_result

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
