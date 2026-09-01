import os
import re
import shutil
import subprocess
import traceback

from pathlib import Path


# ==========================================================
# DEBUG
# ==========================================================

print(
    "==========================================",
    flush=True
)

print(
    "[MEDIA] media_extract.py loaded",
    flush=True
)

print(
    "[MEDIA] Current working directory:",
    os.getcwd(),
    flush=True
)

print(
    "[MEDIA] ffmpeg:",
    shutil.which("ffmpeg"),
    flush=True
)

print(
    "[MEDIA] ffprobe:",
    shutil.which("ffprobe"),
    flush=True
)


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
# 時間 → 秒
#
# 対応:
#
# HH:MM:SS
# MM:SS
# 秒
# None
# 空文字
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
# ファイル名用時間文字列
#
# 例:
#
# 5秒
#   → 000005
#
# 65秒
#   → 000105
#
# 3663秒
#   → 010203
#
# 必ず HHMMSS 形式
# ==========================================================

def _format_filename_time(
    seconds
):

    try:

        total = int(
            float(seconds)
        )

    except Exception as error:

        raise ValueError(
            f"時間を数値に変換できません: {seconds}"
        ) from error

    if total < 0:

        total = 0

    hours = total // 3600

    minutes = (
        total % 3600
    ) // 60

    secs = (
        total % 60
    )

    return (
        f"{hours:02d}"
        f"{minutes:02d}"
        f"{secs:02d}"
    )


# ==========================================================
# 時間範囲のファイル名サフィックス
#
# 全体:
#   ""
#
# 5秒～10秒:
#   "_000005_000010"
#
# ==========================================================

def _build_time_suffix(
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
    # 両方0なら全体指定
    #
    # ファイル名に時間を付けない
    # ------------------------------------------------------

    if (
        start_seconds == 0
        and
        end_seconds == 0
    ):

        return ""

    # ------------------------------------------------------
    # 時間指定あり
    # ------------------------------------------------------

    start_text = _format_filename_time(
        start_seconds
    )

    end_text = _format_filename_time(
        end_seconds
    )

    return (
        "_"
        +
        start_text
        +
        "_"
        +
        end_text
    )


# ==========================================================
# ファイル名サニタイズ
#
# YouTubeタイトルにはファイル名として使用できない
# 文字が含まれる場合があるため除去・置換する。
#
# 日本語タイトル自体は保持する。
# ==========================================================

def _sanitize_filename(
    title
):

    if title is None:

        title = "YouTube Video"

    title = str(
        title
    ).strip()

    if not title:

        title = "YouTube Video"

    # ------------------------------------------------------
    # Windowsでも問題になりやすい文字
    # ------------------------------------------------------

    title = re.sub(

        r'[<>:"/\\|?*\x00-\x1f]',

        "_",

        title

    )

    # ------------------------------------------------------
    # 改行・タブ
    # ------------------------------------------------------

    title = re.sub(

        r"[\r\n\t]+",

        " ",

        title

    )

    # ------------------------------------------------------
    # 連続スペース
    # ------------------------------------------------------

    title = re.sub(

        r"\s+",

        " ",

        title

    )

    # ------------------------------------------------------
    # 末尾の空白・ドット
    # ------------------------------------------------------

    title = title.strip(
        " ."
    )

    # ------------------------------------------------------
    # 空になった場合
    # ------------------------------------------------------

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
# FFmpeg実行
# ==========================================================

def _run_ffmpeg(
    command,
    log_path=None
):

    print(
        "[MEDIA] FFmpeg command:",
        " ".join(
            command
        ),
        flush=True
    )

    if log_path is None:

        result = subprocess.run(

            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace"

        )

        if result.returncode != 0:

            raise RuntimeError(

                "FFmpeg実行に失敗しました\n"
                +
                result.stderr

            )

        return result

    # ------------------------------------------------------
    # ログファイルへ出力
    # ------------------------------------------------------

    with open(

        log_path,

        "w",

        encoding="utf-8",

        errors="replace"

    ) as log_file:

        result = subprocess.run(

            command,

            stdout=subprocess.DEVNULL,

            stderr=log_file

        )

    if result.returncode != 0:

        try:

            log_text = Path(
                log_path
            ).read_text(

                encoding="utf-8",

                errors="replace"

            )

        except Exception:

            log_text = ""

        raise RuntimeError(

            "FFmpeg実行に失敗しました\n"
            +
            log_text

        )

    return result


# ==========================================================
# MP3出力ファイル確認
# ==========================================================

def _validate_mp3(
    path
):

    path = Path(
        path
    )

    if not path.exists():

        raise FileNotFoundError(

            "MP3ファイルがありません: "
            +
            str(path)

        )

    if not path.is_file():

        raise RuntimeError(

            "MP3ファイルではありません: "
            +
            str(path)

        )

    if path.stat().st_size <= 0:

        raise RuntimeError(

            "MP3ファイルのサイズが0です: "
            +
            str(path)

        )

    if path.suffix.lower() != ".mp3":

        raise RuntimeError(

            "MP3ではないファイルが生成されました: "
            +
            str(path)

        )

    print(
        "[MEDIA] MP3 size:",
        path.stat().st_size,
        "bytes",
        flush=True
    )

    return path


# ==========================================================
# MP3作成
#
# input_file:
#   yt-dlpで取得済みの動画ファイル
#
# output_dir:
#   downloads
#
# title:
#   YouTubeタイトル
#
# start_time / end_time:
#   時間指定
#
# 全体:
#   タイトル.mp3
#
# 時間指定:
#   タイトル_000005_000010.mp3
# ==========================================================

def create_mp3_from_file(
    input_file,
    output_dir,
    title="YouTube Video",
    start_time=None,
    end_time=None
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[MEDIA] create_mp3_from_file START",
        flush=True
    )

    print(
        "[MEDIA] input_file:",
        input_file,
        flush=True
    )

    print(
        "[MEDIA] output_dir:",
        output_dir,
        flush=True
    )

    print(
        "[MEDIA] title:",
        title,
        flush=True
    )

    print(
        "[MEDIA] start_time:",
        start_time,
        flush=True
    )

    print(
        "[MEDIA] end_time:",
        end_time,
        flush=True
    )

    input_path = Path(
        input_file
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(

        parents=True,

        exist_ok=True

    )

    # ======================================================
    # 入力ファイル確認
    # ======================================================

    if not input_path.exists():

        raise FileNotFoundError(

            "入力動画ファイルがありません: "
            +
            str(input_path)

        )

    if not input_path.is_file():

        raise RuntimeError(

            "入力動画ファイルではありません: "
            +
            str(input_path)

        )

    if input_path.stat().st_size <= 0:

        raise RuntimeError(

            "入力動画ファイルのサイズが0です: "
            +
            str(input_path)

        )

    print(
        "[MEDIA] input size:",
        input_path.stat().st_size,
        "bytes",
        flush=True
    )

    # ======================================================
    # FFmpeg確認
    # ======================================================

    _check_ffmpeg()

    # ======================================================
    # 時間
    # ======================================================

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    # ======================================================
    # 時間指定判定
    # ======================================================

    has_range = not (

        start_seconds == 0
        and
        end_seconds == 0

    )

    if has_range:

        if start_seconds < 0:

            raise ValueError(
                "開始時間は0秒以上にしてください。"
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

    else:

        duration = None

    print(
        "[MEDIA] has_range:",
        has_range,
        flush=True
    )

    print(
        "[MEDIA] start_seconds:",
        start_seconds,
        flush=True
    )

    print(
        "[MEDIA] end_seconds:",
        end_seconds,
        flush=True
    )

    print(
        "[MEDIA] duration:",
        duration,
        flush=True
    )

    # ======================================================
    # ファイル名作成
    # ======================================================

    safe_title = _sanitize_filename(
        title
    )

    time_suffix = _build_time_suffix(

        start_time=
            start_time,

        end_time=
            end_time

    )

    final_filename = (

        safe_title
        +
        time_suffix
        +
        ".mp3"

    )

    output_file = (

        output_dir
        /
        final_filename

    )

    print(
        "[MEDIA] safe_title:",
        safe_title,
        flush=True
    )

    print(
        "[MEDIA] time_suffix:",
        time_suffix,
        flush=True
    )

    print(
        "[MEDIA] final filename:",
        final_filename,
        flush=True
    )

    print(
        "[MEDIA] final path:",
        output_file,
        flush=True
    )

    # ======================================================
    # 一時ファイル
    #
    # 直接完成ファイルへ書かず、
    # converted.mp3 を作ってから完成ファイルへ移動する。
    # ======================================================

    temporary_output = (

        output_dir
        /
        (
            "."
            +
            input_path.stem
            +
            "_converted.mp3"
        )

    )

    # ------------------------------------------------------
    # 同名一時ファイル削除
    # ------------------------------------------------------

    if temporary_output.exists():

        try:

            temporary_output.unlink()

        except Exception:

            pass

    # ======================================================
    # FFmpegコマンド
    # ======================================================

    ffmpeg_command = [

        "ffmpeg",

        "-y"

    ]

    # ------------------------------------------------------
    # 時間指定あり
    #
    # -ss は入力前に置いて高速シーク
    # ------------------------------------------------------

    if has_range:

        ffmpeg_command.extend([

            "-ss",
            str(start_seconds)

        ])

    # ------------------------------------------------------
    # 入力
    # ------------------------------------------------------

    ffmpeg_command.extend([

        "-i",
        str(input_path)

    ])

    # ------------------------------------------------------
    # 時間指定あり
    # ------------------------------------------------------

    if has_range:

        ffmpeg_command.extend([

            "-t",
            str(duration)

        ])

    # ------------------------------------------------------
    # MP3
    #
    # libmp3lame
    # ------------------------------------------------------

    ffmpeg_command.extend([

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-b:a",
        "192k",

        "-metadata",
        "title=" + str(title),

        "-metadata",
        "comment=YouTube Converter",

        str(temporary_output)

    ])

    # ======================================================
    # ログ
    # ======================================================

    log_path = (

        output_dir
        /
        (
            "."
            +
            input_path.stem
            +
            "_mp3.log"
        )

    )

    try:

        # ==================================================
        # FFmpeg実行
        # ==================================================

        print(
            "[MEDIA] MP3 FFmpeg START",
            flush=True
        )

        _run_ffmpeg(

            command=
                ffmpeg_command,

            log_path=
                log_path

        )

        print(
            "[MEDIA] MP3 FFmpeg COMPLETE",
            flush=True
        )

        # ==================================================
        # 一時出力確認
        # ==================================================

        if not temporary_output.exists():

            raise FileNotFoundError(

                "FFmpeg出力MP3がありません: "
                +
                str(temporary_output)

            )

        if temporary_output.stat().st_size <= 0:

            raise RuntimeError(

                "FFmpeg出力MP3のサイズが0です: "
                +
                str(temporary_output)

            )

        # ==================================================
        # 既存完成ファイル削除
        # ==================================================

        if output_file.exists():

            print(
                "[MEDIA] Removing existing MP3:",
                output_file,
                flush=True
            )

            output_file.unlink()

        # ==================================================
        # 完成ファイルへリネーム
        # ==================================================

        shutil.move(

            str(temporary_output),

            str(output_file)

        )

        # ==================================================
        # MP3確認
        # ==================================================

        output_file = _validate_mp3(
            output_file
        )

        print(
            "[MEDIA] MP3 COMPLETE:",
            output_file,
            flush=True
        )

        # ==================================================
        # 結果
        # ==================================================

        return {

            "path":
                str(output_file),

            "filename":
                output_file.name,

            "title":
                title,

            "start_time":
                start_time,

            "end_time":
                end_time

        }

    except Exception as error:

        print(
            "[MEDIA] create_mp3_from_file ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        # --------------------------------------------------
        # 一時ファイル削除
        # --------------------------------------------------

        try:

            if temporary_output.exists():

                temporary_output.unlink()

        except Exception:

            pass

        raise

    finally:

        # ==================================================
        # ログ削除
        #
        # エラー時の原因調査をしたい場合は残すことも可能。
        # ==================================================

        try:

            if log_path.exists():

                log_path.unlink()

        except Exception:

            pass

        print(
            "[MEDIA] create_mp3_from_file END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )
