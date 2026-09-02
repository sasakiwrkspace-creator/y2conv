import os
import shutil
import subprocess
import tempfile
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
# FFmpeg
# ==========================================================

def _check_ffmpeg():

    path = shutil.which(
        "ffmpeg"
    )

    if path is None:

        raise RuntimeError(
            "FFmpegが見つかりません。"
        )

    return path


# ==========================================================
# FFprobe
# ==========================================================

def _check_ffprobe():

    path = shutil.which(
        "ffprobe"
    )

    if path is None:

        raise RuntimeError(
            "FFprobeが見つかりません。"
        )

    return path


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

    return not (

        _time_to_seconds(
            start_time
        ) == 0

        and

        _time_to_seconds(
            end_time
        ) == 0

    )


# ==========================================================
# 入力確認
# ==========================================================

def _validate_input_file(
    input_file
):

    if not input_file:

        raise ValueError(
            "入力ファイルが指定されていません。"
        )

    path = Path(
        input_file
    )

    if not path.is_file():

        raise FileNotFoundError(
            f"入力ファイルがありません: {path}"
        )

    size = path.stat().st_size

    if size <= 0:

        raise RuntimeError(
            f"入力ファイルサイズが0です: {path}"
        )

    print(
        "[MEDIA] Input:",
        path,
        flush=True
    )

    print(
        "[MEDIA] Input size:",
        size,
        "bytes",
        flush=True
    )

    return path


# ==========================================================
# 出力ディレクトリ
# ==========================================================

def _prepare_output_dir(
    output_dir
):

    if not output_dir:

        raise ValueError(
            "出力先が指定されていません。"
        )

    path = Path(
        output_dir
    )

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    return path


# ==========================================================
# MP3検証
# ==========================================================

def _validate_mp3(
    path
):

    path = Path(
        path
    )

    if not path.is_file():

        raise FileNotFoundError(
            f"MP3ファイルがありません: {path}"
        )

    if path.stat().st_size <= 0:

        raise RuntimeError(
            f"MP3ファイルサイズが0です: {path}"
        )

    if path.suffix.lower() != ".mp3":

        raise RuntimeError(
            f"MP3ではないファイルです: {path}"
        )

    ffprobe = _check_ffprobe()

    command = [

        ffprobe,

        "-v",
        "error",

        "-select_streams",
        "a:0",

        "-show_entries",
        "stream=codec_name,sample_rate,channels,duration",

        "-of",
        "default=noprint_wrappers=1:nokey=0",

        str(path)

    ]

    result = subprocess.run(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )

    print(
        "[MEDIA] ffprobe returncode:",
        result.returncode,
        flush=True
    )

    print(
        "[MEDIA] ffprobe stdout:",
        result.stdout,
        flush=True
    )

    if result.returncode != 0:

        print(
            "[MEDIA] ffprobe stderr:",
            result.stderr,
            flush=True
        )

        raise RuntimeError(
            "生成されたMP3をFFprobeで検証できませんでした。\n"
            +
            result.stderr[-3000:]
        )

    if not result.stdout.strip():

        raise RuntimeError(
            "生成されたMP3に音声ストリームがありません。"
        )

    if "codec_name=mp3" not in result.stdout:

        raise RuntimeError(
            "生成されたファイルがMP3音声として認識されません。"
        )

    print(
        "[MEDIA] MP3 validation SUCCESS",
        flush=True
    )

    return path


# ==========================================================
# MP3作成
# ==========================================================

def create_mp3_from_file(
    input_file,
    output_dir,
    title=None,
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

    input_path = _validate_input_file(
        input_file
    )

    output_path = _prepare_output_dir(
        output_dir
    )

    ffmpeg_path = _check_ffmpeg()

    video_id = input_path.stem

    if not video_id:

        raise RuntimeError(
            "動画IDを取得できませんでした。"
        )

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    full_conversion = not _has_time_range(

        start_time,

        end_time

    )

    if start_seconds < 0:

        raise ValueError(
            "開始時間は0秒以上にしてください。"
        )

    if end_seconds < 0:

        raise ValueError(
            "終了時間は0秒以上にしてください。"
        )

    if not full_conversion:

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )

    title_text = str(
        title or "YouTube Video"
    )

    final_output = (

        output_path
        /
        f"{video_id}.mp3"

    )

    temporary_directory = tempfile.mkdtemp(
        prefix="y2conv_mp3_"
    )

    temporary_output = (

        Path(temporary_directory)
        /
        "converted.mp3"

    )

    log_path = (

        Path(temporary_directory)
        /
        "ffmpeg.log"

    )

    try:

        if final_output.exists():

            final_output.unlink()

        command = [

            ffmpeg_path,

            "-hide_banner",

            "-loglevel",
            "warning",

            "-y"

        ]

        # ==================================================
        # 時間指定
        # ==================================================

        if not full_conversion:

            command.extend([

                "-ss",
                str(start_seconds),

                "-i",
                str(input_path),

                "-t",
                str(
                    end_seconds
                    -
                    start_seconds
                )

            ])

        else:

            command.extend([

                "-i",
                str(input_path)

            ])

        # ==================================================
        # MP3
        # ==================================================

        command.extend([

            "-vn",

            "-map",
            "0:a:0",

            "-codec:a",
            "libmp3lame",

            "-b:a",
            "192k",

            "-ar",
            "44100",

            "-ac",
            "2",

            "-id3v2_version",
            "3",

            "-write_id3v1",
            "1",

            "-metadata",
            "title=" + title_text,

            "-metadata",
            "artist=YouTube",

            "-metadata",
            "comment=YouTube Converter",

            str(temporary_output)

        ])

        print(
            "[MEDIA] FFmpeg:",
            " ".join(command),
            flush=True
        )

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

        print(
            "[MEDIA] FFmpeg returncode:",
            result.returncode,
            flush=True
        )

        if result.returncode != 0:

            log_text = ""

            try:

                log_text = log_path.read_text(
                    encoding="utf-8",
                    errors="replace"
                )

            except Exception:

                pass

            print(
                "[MEDIA] FFmpeg ERROR:",
                log_text,
                flush=True
            )

            raise RuntimeError(

                "MP3変換に失敗しました。\n"
                +
                log_text[-5000:]

            )

        if not temporary_output.is_file():

            raise RuntimeError(
                "FFmpegのMP3出力ファイルがありません。"
            )

        if temporary_output.stat().st_size <= 0:

            raise RuntimeError(
                "FFmpegのMP3出力ファイルサイズが0です。"
            )

        # ==================================================
        # まず一時MP3をFFprobe検証
        # ==================================================

        _validate_mp3(
            temporary_output
        )

        # ==================================================
        # 完成ファイルへ移動
        # ==================================================

        shutil.move(

            str(temporary_output),

            str(final_output)

        )

        final_output = _validate_mp3(
            final_output
        )

        print(
            "[MEDIA] MP3 COMPLETE:",
            final_output,
            flush=True
        )

        return {

            "path":
                str(final_output),

            "filename":
                final_output.name,

            "video_id":
                video_id,

            "title":
                title_text

        }

    except Exception as error:

        print(
            "[MEDIA] create_mp3_from_file ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        try:

            if os.path.isdir(
                temporary_directory
            ):

                shutil.rmtree(
                    temporary_directory,
                    ignore_errors=True
                )

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
