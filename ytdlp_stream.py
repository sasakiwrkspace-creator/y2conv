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
# ファイル名用時間表記
#
# 例:
#
# 5秒
#   ↓
# 000005
#
# 10秒
#   ↓
# 000010
#
# 1分30秒
#   ↓
# 000130
#
# 1時間2分3秒
#   ↓
# 010203
# ==========================================================

def _format_filename_time(
    value
):

    seconds = _time_to_seconds(
        value
    )

    total_seconds = int(
        round(seconds)
    )

    hours = (
        total_seconds
        //
        3600
    )

    minutes = (
        total_seconds
        %
        3600
    ) // 60

    secs = (
        total_seconds
        %
        60
    )

    return (

        f"{hours:02d}"
        f"{minutes:02d}"
        f"{secs:02d}"

    )


# ==========================================================
# ファイル名安全化
#
# YouTubeタイトルに含まれる
# Windows / Linux等で問題になる文字を置換。
#
# yt-dlpにはタイトル名で保存させず、
# Python側でダウンロード後にリネームする。
# ==========================================================

def _sanitize_filename(
    title
):

    if not title:

        title = "YouTube Video"

    title = str(
        title
    ).strip()

    # ------------------------------------------------------
    # ファイル名として使用できない文字
    # ------------------------------------------------------

    invalid_chars = (
        '<>:"/\\|?*'
    )

    for char in invalid_chars:

        title = title.replace(
            char,
            "_"
        )

    # ------------------------------------------------------
    # 改行除去
    # ------------------------------------------------------

    title = title.replace(
        "\n",
        " "
    )

    title = title.replace(
        "\r",
        " "
    )

    # ------------------------------------------------------
    # 連続空白を整理
    # ------------------------------------------------------

    title = " ".join(
        title.split()
    )

    # ------------------------------------------------------
    # ファイル名先頭・末尾の
    # 空白・ドットを除去
    # ------------------------------------------------------

    title = title.strip(
        " ."
    )

    if not title:

        title = "YouTube Video"

    # ------------------------------------------------------
    # Windows予約名対策
    # ------------------------------------------------------

    reserved_names = {

        "CON",
        "PRN",
        "AUX",
        "NUL",

        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",

        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9"

    }

    if title.upper() in reserved_names:

        title = (
            "_"
            +
            title
        )

    return title


# ==========================================================
# MP4最終ファイル名
#
# 時間指定なし:
#
#   タイトル.mp4
#
# 時間指定あり:
#
#   タイトル_000005_000010.mp4
#
# 開始・終了が両方0の場合は
# 範囲表記を付けない。
# ==========================================================

def _build_mp4_filename(
    title,
    start_time=None,
    end_time=None
):

    safe_title = _sanitize_filename(
        title
    )

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    # ------------------------------------------------------
    # 範囲指定なし
    # ------------------------------------------------------

    if (

        start_seconds == 0

        and

        end_seconds == 0

    ):

        return (

            safe_title
            +
            ".mp4"

        )

    # ------------------------------------------------------
    # 範囲指定あり
    # ------------------------------------------------------

    start_text = _format_filename_time(
        start_time
    )

    end_text = _format_filename_time(
        end_time
    )

    return (

        safe_title
        +
        "_"
        +
        start_text
        +
        "_"
        +
        end_text
        +
        ".mp4"

    )


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

    # ------------------------------------------------------
    # 00:00:00 ～ 00:00:00
    #
    # → 全体
    # ------------------------------------------------------

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
#
# yt-dlpではタイトルをファイル名に使用しない。
#
# 一旦、
#
#     VIDEO_ID.ext
#
# として保存する。
#
# 最終ファイル名への変更は
# Python側でダウンロード後に行う。
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
# FFmpegによる結合を避ける。
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
# 映像＋音声を取得。
#
# 必要ならyt-dlp内部でFFmpegによる
# 映像＋音声結合を行う。
#
# その後、外側のFFmpegで
# 指定時間を切り出す。
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
# ★最速経路
#
# FFmpegを使用しない。
#
# YouTube
# ↓
# yt-dlp
# ↓
# VIDEO_ID.mp4
# ↓
# Pythonでタイトル.mp4へリネーム
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
            # yt-dlpが作る一時MP4
            #
            # 例:
            #
            # Wb11ihveUCk.mp4
            # --------------------------------------------------

            temporary_mp4 = (

                output_dir
                /
                f"{video_id}.mp4"

            )

            # --------------------------------------------------
            # 既存MP4削除
            # --------------------------------------------------

            if temporary_mp4.exists():

                print(
                    "[STREAM] Removing existing MP4:",
                    temporary_mp4,
                    flush=True
                )

                temporary_mp4.unlink()

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
        # ダウンロードファイル検索
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

        # ======================================================
        # ★ここでタイトル名へリネーム
        #
        # 全体の場合:
        #
        #     タイトル.mp4
        #
        # 時間指定はこの関数では行わない。
        # ======================================================

        final_filename = _build_mp4_filename(

            title=
                title,

            start_time=
                None,

            end_time=
                None

        )

        final_file = (

            output_dir
            /
            final_filename

        )

        print(
            "[STREAM] Final filename:",
            final_file.name,
            flush=True
        )

        # ------------------------------------------------------
        # 同名ファイルが存在する場合は削除
        # ------------------------------------------------------

        if (

            final_file.exists()

            and

            final_file != downloaded_file

        ):

            print(
                "[STREAM] Removing existing final file:",
                final_file,
                flush=True
            )

            final_file.unlink()

        # ------------------------------------------------------
        # VIDEO_ID.mp4 → タイトル.mp4
        # ------------------------------------------------------

        if downloaded_file != final_file:

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
# タイトル_000005_000010.mp4
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

                duration_source = info.get(
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
            # 最終出力ファイル名
            #
            # 例:
            #
            # タイトル_000005_000010.mp4
            # ==================================================

            output_filename = _build_mp4_filename(

                title=
                    title,

                start_time=
                    start_time,

                end_time=
                    end_time

            )

            output_file = (

                output_dir
                /
                output_filename

            )

            print(
                "[STREAM] Final filename:",
                output_file.name,
                flush=True
            )

            # ==================================================
            # FFmpeg一時出力
            # ==================================================

            temporary_output = (

                temp_dir
                /
                "converted.mp4"

            )

            # --------------------------------------------------
            # 既存ファイル削除
            # --------------------------------------------------

            if output_file.exists():

                print(
                    "[STREAM] Removing existing output:",
                    output_file,
                    flush=True
                )

                output_file.unlink()

            # ==================================================
            # FFmpeg
            #
            # 時間指定時だけ使用。
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
            # 出力確認
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
                    duration

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
#   → タイトル.mp4
#
# 時間指定：
#   → 一時ファイル
#   → FFmpeg切り出し
#   → タイトル_000005_000010.mp4
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
