import re
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
    "[DEBUG] media_extract.py loaded",
    flush=True
)


# ==========================================================
# 時間 → 秒
# ==========================================================

def time_to_seconds(value):

    if value is None:
        return 0.0

    text = str(value).strip()

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
# 全編判定
# ==========================================================

def is_full_download(
    start_time=None,
    end_time=None
):

    return (
        time_to_seconds(start_time) == 0
        and
        time_to_seconds(end_time) == 0
    )


# ==========================================================
# ファイル名安全化
# ==========================================================

def sanitize_filename(
    title,
    fallback="YouTube Video"
):

    if title is None:
        title = fallback

    title = str(title).strip()

    if not title:
        title = fallback

    title = re.sub(
        r"[\r\n\t]+",
        " ",
        title
    )

    title = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        title
    )

    title = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    title = title.rstrip(" .")

    if not title:
        title = fallback

    title = title[:180].rstrip(" .")

    if not title:
        title = fallback

    return title


# ==========================================================
# 出力パス
# ==========================================================

def build_output_paths(
    output_dir,
    title
):

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_title = sanitize_filename(
        title
    )

    return {

        "mp3":
            output_dir
            /
            f"{safe_title}.mp3",

        "mp4":
            output_dir
            /
            f"{safe_title}.mp4",

        "title":
            safe_title

    }


# ==========================================================
# FFmpeg確認
# ==========================================================

def check_ffmpeg():

    try:

        result = subprocess.run(

            [
                "ffmpeg",
                "-version"
            ],

            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,

            timeout=10

        )

        if result.returncode != 0:

            raise RuntimeError(
                "FFmpegを実行できません。"
            )

    except FileNotFoundError as error:

        raise RuntimeError(
            "FFmpegが見つかりません。"
        ) from error


# ==========================================================
# ファイル確認
# ==========================================================

def _validate_output_file(
    path,
    label
):

    path = Path(path)

    if not path.exists():

        raise FileNotFoundError(
            f"{label}ファイルが作成されませんでした: {path}"
        )

    if not path.is_file():

        raise RuntimeError(
            f"{label}がファイルではありません: {path}"
        )

    size = path.stat().st_size

    if size <= 0:

        raise RuntimeError(
            f"{label}ファイルのサイズが0です: {path}"
        )

    print(
        f"[MEDIA] {label} size:",
        size,
        "bytes",
        flush=True
    )

    return path


# ==========================================================
# 一時ファイル削除
# ==========================================================

def _remove_file(path):

    if not path:
        return

    try:

        path = Path(path)

        if path.exists():

            print(
                "[MEDIA] temporary delete:",
                path,
                flush=True
            )

            path.unlink()

    except Exception as error:

        print(
            "[MEDIA] temporary delete ERROR:",
            repr(error),
            flush=True
        )


# ==========================================================
# FFmpeg実行
#
# stderrをPythonメモリに保持し続けない。
# 一時ログファイルへ出力する。
# ==========================================================

def _run_ffmpeg(
    command,
    mode_name
):

    print(
        f"[MEDIA] {mode_name} FFmpeg:",
        " ".join(
            str(x)
            for x in command
        ),
        flush=True
    )

    log_file = None

    try:

        log_file = open(
            Path(
                command[-1]
            ).with_suffix(
                ".ffmpeg.log"
            ),
            "w",
            encoding="utf-8",
            errors="replace"
        )

        result = subprocess.run(

            command,

            stdout=subprocess.DEVNULL,

            stderr=log_file

        )

    finally:

        if log_file:

            log_file.close()

    print(
        f"[MEDIA] {mode_name} returncode:",
        result.returncode,
        flush=True
    )

    if result.returncode != 0:

        log_path = Path(
            command[-1]
        ).with_suffix(
            ".ffmpeg.log"
        )

        try:

            log_text = log_path.read_text(
                encoding="utf-8",
                errors="replace"
            )

        except Exception:

            log_text = ""

        print(
            f"[MEDIA] {mode_name} stderr:",
            log_text,
            flush=True
        )

        raise RuntimeError(
            f"{mode_name}変換に失敗しました。\n"
            +
            log_text
        )

    return result


# ==========================================================
# MP3
# ==========================================================

def create_mp3_from_file(
    input_file,
    output_dir,
    title,
    start_time=None,
    end_time=None
):

    print(
        "[MEDIA] MP3 START",
        flush=True
    )

    check_ffmpeg()

    input_file = Path(
        input_file
    )

    if not input_file.is_file():

        raise FileNotFoundError(
            f"入力ファイルが見つかりません: {input_file}"
        )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    paths = build_output_paths(
        output_dir,
        title
    )

    mp3_file = paths["mp3"]

    temporary_mp3_file = (
        output_dir
        /
        f".{paths['title']}.mp3.tmp"
    )

    _remove_file(
        temporary_mp3_file
    )

    _remove_file(
        mp3_file
    )

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )

    full_download = is_full_download(
        start_time,
        end_time
    )

    command = [
        "ffmpeg",
        "-y"
    ]

    if not full_download and start_seconds > 0:

        command.extend([
            "-ss",
            str(start_seconds)
        ])

    command.extend([
        "-i",
        str(input_file)
    ])

    if not full_download:

        if end_seconds > start_seconds:

            command.extend([
                "-t",
                str(
                    end_seconds - start_seconds
                )
            ])

        elif end_time is not None and end_seconds == 0:

            pass

    command.extend([

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-q:a",
        "2",

        "-metadata",
        "title=" + str(title),

        "-metadata",
        "comment=YouTube Converter",

        str(temporary_mp3_file)

    ])

    _run_ffmpeg(
        command,
        "MP3"
    )

    _validate_output_file(
        temporary_mp3_file,
        "MP3一時"
    )

    temporary_mp3_file.replace(
        mp3_file
    )

    _validate_output_file(
        mp3_file,
        "MP3"
    )

    print(
        "[MEDIA] MP3 COMPLETE:",
        mp3_file,
        flush=True
    )

    return {

        "path":
            str(mp3_file),

        "filename":
            mp3_file.name,

        "title":
            str(title)

    }


# ==========================================================
# MP4
# ==========================================================

def create_mp4_from_file(
    input_file,
    output_dir,
    title,
    start_time=None,
    end_time=None
):

    print(
        "[MEDIA] MP4 START",
        flush=True
    )

    check_ffmpeg()

    input_file = Path(
        input_file
    )

    if not input_file.is_file():

        raise FileNotFoundError(
            f"入力ファイルが見つかりません: {input_file}"
        )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    paths = build_output_paths(
        output_dir,
        title
    )

    mp4_file = paths["mp4"]

    temporary_mp4_file = (
        output_dir
        /
        f".{paths['title']}.mp4.tmp"
    )

    _remove_file(
        temporary_mp4_file
    )

    _remove_file(
        mp4_file
    )

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )

    full_download = is_full_download(
        start_time,
        end_time
    )

    command = [
        "ffmpeg",
        "-y"
    ]

    # ------------------------------------------------------
    # 時間指定
    # ------------------------------------------------------

    if not full_download and start_seconds > 0:

        command.extend([
            "-ss",
            str(start_seconds)
        ])

    command.extend([
        "-i",
        str(input_file)
    ])

    if not full_download:

        if end_seconds > start_seconds:

            command.extend([
                "-t",
                str(
                    end_seconds - start_seconds
                )
            ])

        elif end_time is not None and end_seconds == 0:

            pass

    # ------------------------------------------------------
    # 再エンコードなし
    #
    # メモリ使用量・CPU使用量を抑える。
    # ------------------------------------------------------

    command.extend([

        "-map",
        "0:v:0",

        "-map",
        "0:a:0?",

        "-c",
        "copy",

        "-movflags",
        "+faststart",

        "-metadata",
        "title=" + str(title),

        "-metadata",
        "comment=YouTube Converter",

        str(temporary_mp4_file)

    ])

    _run_ffmpeg(
        command,
        "MP4"
    )

    _validate_output_file(
        temporary_mp4_file,
        "MP4一時"
    )

    temporary_mp4_file.replace(
        mp4_file
    )

    _validate_output_file(
        mp4_file,
        "MP4"
    )

    print(
        "[MEDIA] MP4 COMPLETE:",
        mp4_file,
        flush=True
    )

    return {

        "path":
            str(mp4_file),

        "filename":
            mp4_file.name,

        "title":
            str(title)

    }


# ==========================================================
# MP3 + MP4
# ==========================================================

def create_media_files(
    input_file,
    output_dir,
    title,
    outputs,
    start_time=None,
    end_time=None
):

    print(
        "[MEDIA] create_media_files START",
        flush=True
    )

    results = {}

    try:

        if "mp3" in outputs:

            results["mp3"] = create_mp3_from_file(

                input_file=
                    input_file,

                output_dir=
                    output_dir,

                title=
                    title,

                start_time=
                    start_time,

                end_time=
                    end_time

            )

        if "mp4" in outputs:

            results["mp4"] = create_mp4_from_file(

                input_file=
                    input_file,

                output_dir=
                    output_dir,

                title=
                    title,

                start_time=
                    start_time,

                end_time=
                    end_time

            )

        return results

    except Exception as error:

        print(
            "[MEDIA] create_media_files ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        print(
            "[MEDIA] create_media_files END",
            flush=True
        )
