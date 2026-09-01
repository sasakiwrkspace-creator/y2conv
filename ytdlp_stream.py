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
# FFmpeg確認
# ==========================================================

def _check_ffmpeg():

    if shutil.which(
        "ffmpeg"
    ) is None:

        raise RuntimeError(
            "FFmpegが見つかりません。"
        )


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

        # ==================================================
        # YouTube JavaScript challenge
        # ==================================================

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        "remote_components": {

            "ejs:github"

        },

        # ==================================================
        # Cookie
        # ==================================================

        "cookiefile":
            temporary_cookie_path

    }

    return options


# ==========================================================
# 全体MP4用 yt-dlp オプション
#
# MP4単一ファイルを優先。
#
# 生成時のファイル名は
#
#     VIDEO_ID.mp4
#
# のままにする。
#
# 時間範囲の名前付けは convert.py 側で
# 完成後に行う。
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
        "best[ext=mp4]"
    )

    return options


# ==========================================================
# 時間指定用 yt-dlp オプション
#
# 時間指定の場合は映像＋音声を取得して、
# 後段のFFmpegで切り出す。
# ==========================================================

def _build_range_options(
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
        "bv*+ba/b"
    )

    options["merge_output_format"] = (
        "mp4"
    )

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
# MP4ファイル確認
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
# YouTube情報取得
# ==========================================================

def _extract_info(
    url,
    output_dir,
    cookie_path
):

    options = _build_full_mp4_options(

        output_dir=
            output_dir,

        temporary_cookie_path=
            cookie_path

    )

    options["skip_download"] = True

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

    return info


# ==========================================================
# MP4全体ダウンロード
#
# FFmpegを使用しない。
#
# 完成ファイル：
#
#     VIDEO_ID.mp4
#
# 時間サフィックスは convert.py 側で
# 完成後に追加する。
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
        "[STREAM] FFmpeg: NOT USED",
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

            # --------------------------------------------------
            # 情報取得
            # --------------------------------------------------

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
            # ダウンロード前の既存MP4を削除
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

        # ------------------------------------------------------
        # ファイル検索
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # 念のため検索
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # MP4確認
        # ------------------------------------------------------

        downloaded_file = _validate_mp4(
            downloaded_file
        )

        # ------------------------------------------------------
        # ファイル名をvideo IDからMP4に統一
        #
        # 時間範囲はここでは付けない。
        # ------------------------------------------------------

        final_file = (

            output_dir
            /
            f"{video_id}.mp4"

        )

        if (
            downloaded_file != final_file
        ):

            if final_file.exists():

                final_file.unlink()

            shutil.move(

                str(downloaded_file),

                str(final_file)

            )

            downloaded_file = (
                final_file
            )

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
# MP4指定時間抽出
#
# 時間指定ありの場合のみFFmpegを使用。
#
# YouTube
# ↓
# 一時ファイル
# ↓
# FFmpeg
# ↓
# VIDEO_ID.mp4
#
# 完成後の時間範囲リネームは
# convert.py側で行う。
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

    duration = (

        end_seconds
        -
        start_seconds

    )

    _check_deno()

    _check_ffmpeg()

    cookie_path = None

    try:

        cookie_path = (
            _prepare_cookie_file()
        )

        with tempfile.TemporaryDirectory(

            prefix="y2conv_mp4_"

        ) as temp_dir:

            temp_dir = Path(
                temp_dir
            )

            print(
                "[STREAM] Temporary directory:",
                temp_dir,
                flush=True
            )

            # ==================================================
            # YouTube → 一時ファイル
            # ==================================================

            options = _build_range_options(

                output_dir=
                    temp_dir,

                temporary_cookie_path=
                    cookie_path

            )

            with yt_dlp.YoutubeDL(
                options
            ) as ydl:

                print(
                    "[STREAM] source download START",
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
                    "[STREAM] source download COMPLETE",
                    flush=True
                )

            # --------------------------------------------------
            # 一時ファイル検索
            # --------------------------------------------------

            source_file = (
                _find_downloaded_file(
                    temp_dir,
                    video_id
                )
            )

            if source_file is None:

                raise FileNotFoundError(
                    "一時動画ファイルを確認できませんでした"
                )

            print(
                "[STREAM] source:",
                source_file,
                flush=True
            )

            print(
                "[STREAM] source size:",
                source_file.stat().st_size,
                "bytes",
                flush=True
            )

            # ==================================================
            # 出力
            #
            # 時間指定はここではファイル名に含めない。
            # ==================================================

            output_file = (

                output_dir
                /
                f"{video_id}.mp4"

            )

            temporary_output = (

                temp_dir
                /
                "converted.mp4"

            )

            # --------------------------------------------------
            # 既存ファイル削除
            # --------------------------------------------------

            if output_file.exists():

                output_file.unlink()

            # ==================================================
            # FFmpeg
            #
            # 再エンコード方式。
            # ==================================================

            ffmpeg_command = [

                "ffmpeg",

                "-y",

                "-ss",
                str(start_seconds),

                "-i",
                str(source_file),

                "-t",
                str(duration),

                "-c:v",
                "libx264",

                "-preset",
                "veryfast",

                "-crf",
                "23",

                "-c:a",
                "aac",

                "-b:a",
                "128k",

                "-movflags",
                "+faststart",

                "-metadata",
                "title=" + str(title),

                "-metadata",
                "comment=YouTube Converter",

                str(temporary_output)

            ]

            print(
                "[STREAM] FFmpeg:",
                " ".join(
                    ffmpeg_command
                ),
                flush=True
            )

            # --------------------------------------------------
            # stderrをメモリに大量保持しない
            # --------------------------------------------------

            log_path = (

                temp_dir
                /
                "ffmpeg.log"

            )

            with open(

                log_path,

                "w",

                encoding="utf-8",

                errors="replace"

            ) as log_file:

                result = subprocess.run(

                    ffmpeg_command,

                    stdout=subprocess.DEVNULL,

                    stderr=log_file

                )

            print(
                "[STREAM] FFmpeg returncode:",
                result.returncode,
                flush=True
            )

            if result.returncode != 0:

                try:

                    log_text = (
                        log_path.read_text(
                            encoding="utf-8",
                            errors="replace"
                        )
                    )

                except Exception:

                    log_text = ""

                print(
                    "[STREAM] FFmpeg ERROR:",
                    log_text,
                    flush=True
                )

                raise RuntimeError(
                    "FFmpeg指定時間変換に失敗しました\n"
                    +
                    log_text
                )

            # ==================================================
            # FFmpeg出力確認
            # ==================================================

            if not temporary_output.exists():

                raise FileNotFoundError(
                    "FFmpeg出力ファイルがありません"
                )

            if temporary_output.stat().st_size <= 0:

                raise RuntimeError(
                    "FFmpeg出力ファイルのサイズが0です"
                )

            # ==================================================
            # 完成ファイルへ移動
            #
            # ここではVIDEO_ID.mp4。
            # 時間サフィックスはconvert.pyで追加。
            # ==================================================

            shutil.move(

                str(temporary_output),

                str(output_file)

            )

            output_file = _validate_mp4(
                output_file
            )

            print(
                "[STREAM] MP4 COMPLETE:",
                output_file,
                flush=True
            )

            return {

                "path":
                    str(output_file),

                "filename":
                    output_file.name,

                "video_id":
                    video_id,

                "title":
                    title,

                "duration":
                    duration_info

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
# 全体：
#   → 直接MP4ダウンロード
#   → FFmpegなし
#   → VIDEO_ID.mp4
#
# 時間指定：
#   → 一時ファイル
#   → FFmpeg切り出し
#   → VIDEO_ID.mp4
#
# 時間範囲付きファイル名への変更は
# convert.py側で完成後に行う。
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
            "[STREAM] MODE: FULL",
            flush=True
        )

        print(
            "[STREAM] FFmpeg: SKIP",
            flush=True
        )

        return create_mp4_full(

            url,

            output_dir

        )

    # ======================================================
    # 時間指定あり
    # ======================================================

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

    print(
        "[STREAM] MODE: RANGE",
        flush=True
    )

    print(
        "[STREAM] FFmpeg: USE",
        flush=True
    )

    return create_mp4_range(

        url,

        output_dir,

        start_time,

        end_time

    )
