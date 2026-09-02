import os
import sys
import shutil
import subprocess
import tempfile
import traceback

from pathlib import Path

import yt_dlp


# ==========================================================
# DEBUG
# ==========================================================

print(
    "==========================================",
    flush=True
)

print(
    "[STREAM] ytdlp_stream.py loaded",
    flush=True
)

print(
    "[STREAM] Python:",
    sys.version,
    flush=True
)

print(
    "[STREAM] Python executable:",
    sys.executable,
    flush=True
)

print(
    "[STREAM] Current working directory:",
    os.getcwd(),
    flush=True
)


# ==========================================================
# Deno
# ==========================================================

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)

print(
    "[STREAM] DENO_PATH:",
    DENO_PATH,
    flush=True
)

print(
    "[STREAM] Deno exists:",
    os.path.isfile(DENO_PATH),
    flush=True
)

print(
    "[STREAM] Deno executable:",
    os.access(
        DENO_PATH,
        os.X_OK
    ),
    flush=True
)

print(
    "[STREAM] Deno which:",
    shutil.which("deno"),
    flush=True
)


# ==========================================================
# FFmpeg
#
# このファイルでは再エンコードには使用しない。
# ==========================================================

print(
    "[STREAM] ffmpeg:",
    shutil.which("ffmpeg"),
    flush=True
)

print(
    "[STREAM] ffprobe:",
    shutil.which("ffprobe"),
    flush=True
)


# ==========================================================
# Cookie
# ==========================================================

def _prepare_cookie_file():

    cookies_source = (
        "/etc/secrets/cookies.txt"
    )

    print(
        "[STREAM] Cookie source:",
        cookies_source,
        flush=True
    )

    if not os.path.isfile(
        cookies_source
    ):

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            +
            cookies_source
        )

    temporary_cookie_path = None

    try:

        temporary_cookie = tempfile.NamedTemporaryFile(

            mode="w",

            suffix=".txt",

            prefix="y2conv_stream_",

            delete=False

        )

        temporary_cookie_path = (
            temporary_cookie.name
        )

        temporary_cookie.close()

        shutil.copyfile(

            cookies_source,

            temporary_cookie_path

        )

        print(
            "[STREAM] Temporary cookie:",
            temporary_cookie_path,
            flush=True
        )

        return temporary_cookie_path

    except Exception:

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
# 時間 → 秒
# ==========================================================

def _time_to_seconds(
    value
):

    if value is None:

        return 0.0

    text = str(
        value
    ).strip()

    if not text:

        return 0.0

    parts = text.split(":")

    try:

        if len(parts) == 3:

            return (

                float(parts[0]) * 3600

                +

                float(parts[1]) * 60

                +

                float(parts[2])

            )

        if len(parts) == 2:

            return (

                float(parts[0]) * 60

                +

                float(parts[1])

            )

        return float(text)

    except Exception as error:

        raise ValueError(
            f"時間形式が不正です: {value}"
        ) from error


# ==========================================================
# 時間指定判定
# ==========================================================

def _has_time_range(
    start_time,
    end_time
):

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    if (
        start_seconds == 0
        and
        end_seconds == 0
    ):

        return False

    return True


# ==========================================================
# Deno確認
# ==========================================================

def _check_deno():

    if not os.path.isfile(
        DENO_PATH
    ):

        raise RuntimeError(
            "Denoが見つかりません: "
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

        if result.returncode != 0:

            raise RuntimeError(
                "Denoの実行に失敗しました"
            )

    except FileNotFoundError as error:

        raise RuntimeError(
            "Denoが実行できません: "
            +
            DENO_PATH
        ) from error


# ==========================================================
# 共通 yt-dlp オプション
# ==========================================================

def _build_common_options(
    output_dir,
    temporary_cookie_path
):

    output_template = str(

        Path(output_dir)
        /
        "%(id)s.%(ext)s"

    )

    options = {

        "outtmpl":
            output_template,

        "noplaylist":
            True,

        "quiet":
            False,

        "no_warnings":
            False,

        "verbose":
            True,

        # --------------------------------------------------
        # YouTube JavaScript challenge
        # --------------------------------------------------

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        # --------------------------------------------------
        # EJS challenge scripts
        # --------------------------------------------------

        "remote_components": {

            "ejs:github"

        },

        # --------------------------------------------------
        # Cookie
        # --------------------------------------------------

        "cookiefile":
            temporary_cookie_path,

        # --------------------------------------------------
        # メモリ使用量を抑える
        #
        # Python側で巨大データを保持しない。
        # --------------------------------------------------

        "continuedl":
            True

    }

    return options


# ==========================================================
# 全体MP4
#
# 可能な限り既存MP4をそのまま取得。
#
# FFmpegによる再エンコードは行わない。
# ==========================================================

def _build_full_mp4_options(
    output_dir,
    temporary_cookie_path
):

    options = _build_common_options(

        output_dir=
            output_dir,

        temporary_cookie_path=
            temporary_cookie_path

    )

    options["format"] = (
        "best[ext=mp4]/best"
    )

    # ------------------------------------------------------
    # 重要：
    #
    # yt-dlp側でのMP4再エンコードを要求しない。
    # ------------------------------------------------------

    options["merge_output_format"] = "mp4"

    return options


# ==========================================================
# 時間範囲MP4
#
# FFmpegで再エンコードしない。
#
# yt-dlpに区間を指定してダウンロードさせる。
# ==========================================================

def _build_range_options(
    output_dir,
    temporary_cookie_path,
    start_seconds,
    end_seconds
):

    options = _build_common_options(

        output_dir=
            output_dir,

        temporary_cookie_path=
            temporary_cookie_path

    )

    # ------------------------------------------------------
    # まずMP4を優先。
    #
    # 音声＋映像が単一MP4で存在する場合は、
    # そのまま取得する。
    # ------------------------------------------------------

    options["format"] = (
        "best[ext=mp4]/best"
    )

    # ------------------------------------------------------
    # 指定時間範囲
    #
    # yt-dlp側でダウンロード範囲を指定。
    # ------------------------------------------------------

    options["download_ranges"] = (
        lambda info, ydl:
            [{
                "start_time": start_seconds,
                "end_time": end_seconds
            }]
    )

    # ------------------------------------------------------
    # 範囲ダウンロードを使用する。
    # ------------------------------------------------------

    options["force_keyframes_at_cuts"] = False

    return options


# ==========================================================
# ダウンロードファイル検索
# ==========================================================

def _find_downloaded_file(
    output_dir,
    video_id
):

    output_dir = Path(
        output_dir
    )

    if not video_id:

        return None

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

            size = 0

        if size <= 0:

            continue

        candidates.append(
            path
        )

    if not candidates:

        return None

    candidates.sort(

        key=lambda p:
            p.stat().st_mtime,

        reverse=True

    )

    return candidates[0]


# ==========================================================
# MP4確認
# ==========================================================

def _validate_mp4(
    path
):

    path = Path(
        path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"MP4ファイルがありません: {path}"
        )

    if not path.is_file():

        raise RuntimeError(
            f"MP4ファイルではありません: {path}"
        )

    if path.stat().st_size <= 0:

        raise RuntimeError(
            f"MP4ファイルのサイズが0です: {path}"
        )

    if path.suffix.lower() != ".mp4":

        raise RuntimeError(
            "MP4ではないファイルが生成されました: "
            +
            str(path)
        )

    print(
        "[STREAM] MP4 size:",
        path.stat().st_size,
        "bytes",
        flush=True
    )

    return path


# ==========================================================
# MP4全体ダウンロード
#
# FFmpeg再エンコードなし。
# ==========================================================

def create_mp4_full(
    url,
    output_dir
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[STREAM] create_mp4_full START",
        flush=True
    )

    print(
        "[STREAM] MODE: DIRECT MP4 DOWNLOAD",
        flush=True
    )

    print(
        "[STREAM] RE-ENCODE: NONE",
        flush=True
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(

        parents=True,

        exist_ok=True

    )

    cookie_path = None

    try:

        _check_deno()

        cookie_path = (
            _prepare_cookie_file()
        )

        options = _build_full_mp4_options(

            output_dir=
                output_dir,

            temporary_cookie_path=
                cookie_path

        )

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            info = ydl.extract_info(

                url,

                download=False

            )

            if not info:

                raise RuntimeError(
                    "YouTube情報を取得できませんでした"
                )

            video_id = info.get(
                "id"
            )

            title = (
                info.get("title")
                or
                "YouTube Video"
            )

            duration = info.get(
                "duration"
            )

            print(
                "[STREAM] Video ID:",
                video_id,
                flush=True
            )

            print(
                "[STREAM] Title:",
                title,
                flush=True
            )

            print(
                "[STREAM] Duration:",
                duration,
                flush=True
            )

            # --------------------------------------------------
            # 既存MP4削除
            # --------------------------------------------------

            if video_id:

                existing_mp4 = (

                    output_dir
                    /
                    f"{video_id}.mp4"

                )

                if existing_mp4.exists():

                    print(
                        "[STREAM] Removing existing MP4:",
                        existing_mp4,
                        flush=True
                    )

                    existing_mp4.unlink()

            # --------------------------------------------------
            # ダウンロード
            # --------------------------------------------------

            print(
                "[STREAM] Direct MP4 download START",
                flush=True
            )

            ydl.download([
                url
            ])

            print(
                "[STREAM] Direct MP4 download COMPLETE",
                flush=True
            )

        downloaded_file = None

        if video_id:

            mp4_path = (

                output_dir
                /
                f"{video_id}.mp4"

            )

            if mp4_path.is_file():

                downloaded_file = (
                    mp4_path
                )

        if downloaded_file is None:

            downloaded_file = (
                _find_downloaded_file(
                    output_dir,
                    video_id
                )
            )

        if downloaded_file is None:

            raise FileNotFoundError(
                "MP4ファイルを確認できませんでした"
            )

        downloaded_file = _validate_mp4(
            downloaded_file
        )

        final_file = (

            output_dir
            /
            f"{video_id}.mp4"

        )

        if downloaded_file != final_file:

            if final_file.exists():

                final_file.unlink()

            shutil.move(

                str(downloaded_file),

                str(final_file)

            )

            downloaded_file = final_file

        print(
            "[STREAM] MP4 COMPLETE:",
            downloaded_file,
            flush=True
        )

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "video_id":
                video_id,

            "title":
                title,

            "duration":
                duration

        }

    except Exception as error:

        print(
            "[STREAM] create_mp4_full ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if cookie_path:

            try:

                if os.path.exists(
                    cookie_path
                ):

                    os.remove(
                        cookie_path
                    )

            except Exception:

                pass

        print(
            "[STREAM] create_mp4_full END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# 指定範囲ダウンロード
#
# 重要：
#
# FFmpegによる
#
#     libx264
#     aac
#
# の再エンコードは行わない。
#
# yt-dlpへ指定範囲を渡して取得する。
# ==========================================================

def create_mp4_range(
    url,
    output_dir,
    start_time,
    end_time
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[STREAM] create_mp4_range START",
        flush=True
    )

    print(
        "[STREAM] start_time:",
        start_time,
        flush=True
    )

    print(
        "[STREAM] end_time:",
        end_time,
        flush=True
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(

        parents=True,

        exist_ok=True

    )

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    if end_seconds <= start_seconds:

        raise ValueError(
            "終了時間は開始時間より後にしてください。"
        )

    _check_deno()

    cookie_path = None

    try:

        cookie_path = (
            _prepare_cookie_file()
        )

        options = _build_range_options(

            output_dir=
                output_dir,

            temporary_cookie_path=
                cookie_path,

            start_seconds=
                start_seconds,

            end_seconds=
                end_seconds

        )

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            print(
                "[STREAM] Range download START",
                flush=True
            )

            info = ydl.extract_info(

                url,

                download=True

            )

            if not info:

                raise RuntimeError(
                    "YouTube動画を取得できませんでした"
                )

            video_id = info.get(
                "id"
            )

            title = (
                info.get("title")
                or
                "YouTube Video"
            )

            duration_info = info.get(
                "duration"
            )

            print(
                "[STREAM] Range download COMPLETE",
                flush=True
            )

        downloaded_file = (
            _find_downloaded_file(
                output_dir,
                video_id
            )
        )

        if downloaded_file is None:

            raise FileNotFoundError(
                "指定範囲のダウンロードファイルを"
                "確認できませんでした"
            )

        # --------------------------------------------------
        # MP4優先
        # --------------------------------------------------

        if downloaded_file.suffix.lower() != ".mp4":

            raise RuntimeError(
                "指定範囲ダウンロードでMP4を取得できませんでした: "
                +
                str(downloaded_file)
            )

        downloaded_file = _validate_mp4(
            downloaded_file
        )

        # --------------------------------------------------
        # VIDEO_ID.mp4へ統一
        # --------------------------------------------------

        final_file = (

            output_dir
            /
            f"{video_id}.mp4"

        )

        if downloaded_file != final_file:

            if final_file.exists():

                final_file.unlink()

            shutil.move(

                str(downloaded_file),

                str(final_file)

            )

            downloaded_file = final_file

        print(
            "[STREAM] MP4 RANGE COMPLETE:",
            downloaded_file,
            flush=True
        )

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "video_id":
                video_id,

            "title":
                title,

            "duration":
                duration_info,

            "start_time":
                start_time,

            "end_time":
                end_time

        }

    except Exception as error:

        print(
            "[STREAM] create_mp4_range ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if cookie_path:

            try:

                if os.path.exists(
                    cookie_path
                ):

                    os.remove(
                        cookie_path
                    )

            except Exception:

                pass

        print(
            "[STREAM] create_mp4_range END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# メイン
#
# 時間指定なし
#   → 直接MP4
#
# 時間指定あり
#   → yt-dlpの範囲ダウンロード
#   → 再エンコードなし
# ==========================================================

def create_mp4_memory_safe(
    url,
    output_dir,
    start_time=None,
    end_time=None
):

    print(
        "[STREAM] create_mp4_memory_safe START",
        flush=True
    )

    print(
        "[STREAM] start_time:",
        start_time,
        flush=True
    )

    print(
        "[STREAM] end_time:",
        end_time,
        flush=True
    )

    # ======================================================
    # 時間指定なし
    # ======================================================

    if not _has_time_range(

        start_time,

        end_time

    ):

        print(
            "[STREAM] MODE: FULL DIRECT DOWNLOAD",
            flush=True
        )

        print(
            "[STREAM] RE-ENCODE: NONE",
            flush=True
        )

        return create_mp4_full(

            url,

            output_dir

        )

    # ======================================================
    # 時間指定あり
    # ======================================================

    print(
        "[STREAM] MODE: RANGE DIRECT DOWNLOAD",
        flush=True
    )

    print(
        "[STREAM] RE-ENCODE: NONE",
        flush=True
    )

    return create_mp4_range(

        url,

        output_dir,

        start_time,

        end_time

    )
