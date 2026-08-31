import os
import re
import subprocess
import traceback
from pathlib import Path


# ==========================================================
# DEBUG
# ==========================================================

print("==========================================", flush=True)
print("[DEBUG] media_extract.py loaded", flush=True)


# ==========================================================
# 時間 → 秒
# ==========================================================

def time_to_seconds(value):
    """
    以下の形式に対応

    00:00:05
    00:05
    5
    5.5
    """

    if value is None:
        return 0.0

    text = str(value).strip()

    if not text:
        return 0.0

    parts = text.split(":")

    try:

        if len(parts) == 3:

            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])

            return (
                hours * 3600
                + minutes * 60
                + seconds
            )

        if len(parts) == 2:

            minutes = float(parts[0])
            seconds = float(parts[1])

            return (
                minutes * 60
                + seconds
            )

        return float(text)

    except Exception as error:

        raise ValueError(
            f"時間形式が不正です: {value}"
        ) from error


# ==========================================================
# 時間指定なし判定
# ==========================================================

def is_full_download(
    start_time=None,
    end_time=None
):
    """
    以下の場合は全編扱い

    None / None
    00:00:00 / 00:00:00
    0 / 0
    """

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )

    return (
        start_seconds == 0
        and
        end_seconds == 0
    )


# ==========================================================
# 安全なファイル名
# ==========================================================

def sanitize_filename(
    title,
    fallback="YouTube Video"
):
    """
    動画タイトルをファイル名として安全にする。

    Windows/Linux等で問題になりやすい文字を除去。
    """

    if title is None:

        title = fallback

    title = str(title).strip()

    if not title:

        title = fallback

    # ------------------------------------------------------
    # 改行・タブ
    # ------------------------------------------------------

    title = re.sub(
        r"[\r\n\t]+",
        " ",
        title
    )

    # ------------------------------------------------------
    # ファイル名として使用できない文字
    # ------------------------------------------------------

    title = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        title
    )

    # ------------------------------------------------------
    # 制御文字
    # ------------------------------------------------------

    title = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
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

    title = title.strip()

    # ------------------------------------------------------
    # 末尾のドット・スペース
    # ------------------------------------------------------

    title = title.rstrip(
        " ."
    )

    if not title:

        title = fallback

    # ------------------------------------------------------
    # 長すぎるファイル名対策
    # ------------------------------------------------------

    max_length = 180

    if len(title) > max_length:

        title = title[:max_length].rstrip()

    return title


# ==========================================================
# 出力ファイル名
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

    mp3_path = (
        output_dir
        /
        f"{safe_title}.mp3"
    )

    mp4_path = (
        output_dir
        /
        f"{safe_title}.mp4"
    )

    return {
        "mp3": mp3_path,
        "mp4": mp4_path,
        "title": safe_title
    }


# ==========================================================
# FFmpeg存在確認
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

    except Exception:

        raise


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
# MP3作成
# ==========================================================

def create_mp3_from_file(
    input_file,
    output_dir,
    title,
    start_time=None,
    end_time=None
):

    print("==========================================", flush=True)

    print(
        "[MEDIA] MP3 START",
        flush=True
    )

    print(
        "[MEDIA] input:",
        input_file,
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

    check_ffmpeg()

    input_file = Path(
        input_file
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

    # ------------------------------------------------------
    # 既存ファイル削除
    # ------------------------------------------------------

    if mp3_file.exists():

        try:

            mp3_file.unlink()

        except Exception as error:

            raise RuntimeError(
                f"既存MP3ファイルを削除できません: {mp3_file}"
            ) from error

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

    # ------------------------------------------------------
    # FFmpeg
    # ------------------------------------------------------

    command = [
        "ffmpeg",
        "-y"
    ]

    # ------------------------------------------------------
    # 時間指定
    # ------------------------------------------------------

    if not full_download:

        if start_seconds > 0:

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

            duration = (
                end_seconds
                -
                start_seconds
            )

            command.extend([
                "-t",
                str(duration)
            ])

        elif end_time is not None and end_seconds == 0:

            # 終了時間0は「最後まで」
            pass

    # ------------------------------------------------------
    # 音声
    # ------------------------------------------------------

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

        str(mp3_file)

    ])

    print(
        "[MEDIA] MP3 FFmpeg:",
        " ".join(
            str(x)
            for x in command
        ),
        flush=True
    )

    try:

        result = subprocess.run(

            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace"

        )

    except Exception as error:

        print(
            "[MEDIA] MP3 FFmpeg exception:",
            repr(error),
            flush=True
        )

        raise

    print(
        "[MEDIA] MP3 returncode:",
        result.returncode,
        flush=True
    )

    if result.returncode != 0:

        print(
            "[MEDIA] MP3 stderr:",
            result.stderr,
            flush=True
        )

        raise RuntimeError(
            "MP3変換に失敗しました。\n"
            + result.stderr
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

    print("==========================================", flush=True)

    return {

        "path":
            str(mp3_file),

        "filename":
            mp3_file.name,

        "title":
            str(title)

    }


# ==========================================================
# MP4作成
# ==========================================================

def create_mp4_from_file(
    input_file,
    output_dir,
    title,
    start_time=None,
    end_time=None
):

    print("==========================================", flush=True)

    print(
        "[MEDIA] MP4 START",
        flush=True
    )

    print(
        "[MEDIA] input:",
        input_file,
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

    check_ffmpeg()

    input_file = Path(
        input_file
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

    if mp4_file.exists():

        try:

            mp4_file.unlink()

        except Exception as error:

            raise RuntimeError(
                f"既存MP4ファイルを削除できません: {mp4_file}"
            ) from error

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

    # ======================================================
    # 全編
    # ======================================================

    if full_download:

        print(
            "[MEDIA] MP4: full video",
            flush=True
        )

        # --------------------------------------------------
        # 再エンコードなし
        # --------------------------------------------------

        command = [

            "ffmpeg",

            "-y",

            "-i",
            str(input_file),

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

            str(mp4_file)

        ]

    # ======================================================
    # 時間指定
    # ======================================================

    else:

        print(
            "[MEDIA] MP4: selected section",
            flush=True
        )

        command = [
            "ffmpeg",
            "-y"
        ]

        # --------------------------------------------------
        # 入力シーク
        # --------------------------------------------------

        if start_seconds > 0:

            command.extend([
                "-ss",
                str(start_seconds)
            ])

        command.extend([
            "-i",
            str(input_file)
        ])

        # --------------------------------------------------
        # 抽出時間
        # --------------------------------------------------

        if end_seconds > start_seconds:

            duration = (
                end_seconds
                -
                start_seconds
            )

            command.extend([
                "-t",
                str(duration)
            ])

        # --------------------------------------------------
        # 再エンコードなし
        # --------------------------------------------------

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

            str(mp4_file)

        ])

    print(
        "[MEDIA] MP4 FFmpeg:",
        " ".join(
            str(x)
            for x in command
        ),
        flush=True
    )

    try:

        result = subprocess.run(

            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace"

        )

    except Exception as error:

        print(
            "[MEDIA] MP4 FFmpeg exception:",
            repr(error),
            flush=True
        )

        raise

    print(
        "[MEDIA] MP4 returncode:",
        result.returncode,
        flush=True
    )

    if result.returncode != 0:

        print(
            "[MEDIA] MP4 stderr:",
            result.stderr,
            flush=True
        )

        raise RuntimeError(
            "MP4変換に失敗しました。\n"
            + result.stderr
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

    print("==========================================", flush=True)

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

    print("==========================================", flush=True)

    print(
        "[MEDIA] create_media_files START",
        flush=True
    )

    results = {}

    try:

        if "mp3" in outputs:

            results["mp3"] = (
                create_mp3_from_file(

                    input_file=input_file,

                    output_dir=output_dir,

                    title=title,

                    start_time=start_time,

                    end_time=end_time

                )
            )

        if "mp4" in outputs:

            results["mp4"] = (
                create_mp4_from_file(

                    input_file=input_file,

                    output_dir=output_dir,

                    title=title,

                    start_time=start_time,

                    end_time=end_time

                )
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

        print("==========================================", flush=True)
