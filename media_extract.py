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

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    if ffmpeg_path is None:

        raise RuntimeError(
            "FFmpegが見つかりません。"
        )

    return ffmpeg_path


# ==========================================================
# FFprobe確認
# ==========================================================

def _check_ffprobe():

    ffprobe_path = shutil.which(
        "ffprobe"
    )

    if ffprobe_path is None:

        raise RuntimeError(
            "FFprobeが見つかりません。"
        )

    return ffprobe_path


# ==========================================================
# 時間 → 秒
# ==========================================================

def _time_to_seconds(value):

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

            hours = float(
                parts[0]
            )

            minutes = float(
                parts[1]
            )

            seconds = float(
                parts[2]
            )

            return (
                hours * 3600
                +
                minutes * 60
                +
                seconds
            )

        if len(parts) == 2:

            minutes = float(
                parts[0]
            )

            seconds = float(
                parts[1]
            )

            return (
                minutes * 60
                +
                seconds
            )

        return float(
            text
        )

    except Exception as error:

        raise ValueError(
            f"時間形式が不正です: {value}"
        ) from error


# ==========================================================
# 時間範囲判定
#
# 00:00:00 ～ 00:00:00
# は全体変換。
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

    return not (
        start_seconds == 0
        and
        end_seconds == 0
    )


# ==========================================================
# 入力ファイル確認
# ==========================================================

def _validate_input_file(
    input_file
):

    if not input_file:

        raise ValueError(
            "入力ファイルが指定されていません。"
        )

    input_path = Path(
        input_file
    )

    print(
        "[MEDIA] Checking input:",
        input_path,
        flush=True
    )

    if not input_path.exists():

        raise FileNotFoundError(
            "入力ファイルがありません: "
            +
            str(input_path)
        )

    if not input_path.is_file():

        raise RuntimeError(
            "入力パスがファイルではありません: "
            +
            str(input_path)
        )

    size = input_path.stat().st_size

    if size <= 0:

        raise RuntimeError(
            "入力ファイルのサイズが0です: "
            +
            str(input_path)
        )

    print(
        "[MEDIA] Input file:",
        input_path,
        flush=True
    )

    print(
        "[MEDIA] Input size:",
        size,
        "bytes",
        flush=True
    )

    return input_path


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

    output_path = Path(
        output_dir
    )

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "[MEDIA] Output directory:",
        output_path,
        flush=True
    )

    return output_path


# ==========================================================
# MP3確認
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
            "MP3出力がファイルではありません: "
            +
            str(path)
        )

    size = path.stat().st_size

    if size <= 0:

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
        "[MEDIA] MP3 validated:",
        path,
        flush=True
    )

    print(
        "[MEDIA] MP3 size:",
        size,
        "bytes",
        flush=True
    )

    return path


# ==========================================================
# MP3をffprobeで検証
# ==========================================================

def _probe_mp3(
    path
):

    ffprobe_path = _check_ffprobe()

    command = [

        ffprobe_path,

        "-v",
        "error",

        "-select_streams",
        "a:0",

        "-show_entries",
        "stream=codec_name,duration",

        "-of",
        "default=noprint_wrappers=1",

        str(path)

    ]

    print(
        "[MEDIA] FFprobe:",
        " ".join(command),
        flush=True
    )

    result = subprocess.run(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )

    print(
        "[MEDIA] FFprobe returncode:",
        result.returncode,
        flush=True
    )

    if result.stdout:

        print(
            "[MEDIA] FFprobe stdout:",
            result.stdout,
            flush=True
        )

    if result.stderr:

        print(
            "[MEDIA] FFprobe stderr:",
            result.stderr,
            flush=True
        )

    if result.returncode != 0:

        raise RuntimeError(
            "生成されたMP3をFFprobeで確認できませんでした。\n"
            +
            result.stderr[-3000:]
        )

    if "codec_name=mp3" not in result.stdout:

        raise RuntimeError(
            "生成されたファイルにMP3音声ストリームがありません。"
        )

    return True


# ==========================================================
# MP3作成
#
# 入力:
#     ダウンロード済み動画ファイル
#
# 出力:
#     VIDEO_ID.mp3
#
# 時間指定あり:
#     指定区間だけMP3化
#
# 時間指定なし:
#     動画全体をMP3化
#
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

    # ======================================================
    # 実行ファイル
    # ======================================================

    ffmpeg_path = _check_ffmpeg()

    ffprobe_path = _check_ffprobe()

    print(
        "[MEDIA] FFmpeg path:",
        ffmpeg_path,
        flush=True
    )

    print(
        "[MEDIA] FFprobe path:",
        ffprobe_path,
        flush=True
    )

    # ======================================================
    # 入力
    # ======================================================

    input_path = _validate_input_file(
        input_file
    )

    output_path = _prepare_output_dir(
        output_dir
    )

    # ======================================================
    # video ID
    #
    # 例:
    #
    # Wb11ihveUCk.mp4
    #
    # →
    #
    # Wb11ihveUCk
    # ======================================================

    video_id = input_path.stem

    if not video_id:

        raise RuntimeError(
            "動画IDを取得できませんでした。"
        )

    print(
        "[MEDIA] Video ID:",
        video_id,
        flush=True
    )

    # ======================================================
    # 時間
    # ======================================================

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    has_range = _has_time_range(

        start_time,

        end_time

    )

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

    if start_seconds < 0:

        raise ValueError(
            "開始時間は0秒以上にしてください。"
        )

    if end_seconds < 0:

        raise ValueError(
            "終了時間は0秒以上にしてください。"
        )

    if has_range:

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )

    # ======================================================
    # タイトル
    # ======================================================

    mp3_title = str(
        title or "YouTube Video"
    ).strip()

    if not mp3_title:

        mp3_title = "YouTube Video"

    print(
        "[MEDIA] MP3 title:",
        mp3_title,
        flush=True
    )

    # ======================================================
    # 最終ファイル
    #
    # ここでは必ずVIDEO_ID.mp3
    #
    # 時間指定の場合もconvert.py側で
    #
    # VIDEO_ID_000005_000010.mp3
    #
    # に変更する。
    # ======================================================

    final_output = (

        output_path
        /
        f"{video_id}.mp3"

    )

    print(
        "[MEDIA] Final MP3:",
        final_output,
        flush=True
    )

    # ======================================================
    # 一時ディレクトリ
    # ======================================================

    temporary_directory = tempfile.mkdtemp(
        prefix="y2conv_mp3_"
    )

    temporary_output = (

        Path(
            temporary_directory
        )
        /
        "converted.mp3"

    )

    log_path = (

        Path(
            temporary_directory
        )
        /
        "ffmpeg.log"

    )

    try:

        # ==================================================
        # 既存MP3削除
        # ==================================================

        if final_output.exists():

            print(
                "[MEDIA] Removing existing MP3:",
                final_output,
                flush=True
            )

            final_output.unlink()

        # ==================================================
        # FFmpeg
        # ==================================================

        command = [

            ffmpeg_path,

            "-hide_banner",

            "-loglevel",
            "warning",

            "-y"

        ]

        # ==================================================
        # 時間指定
        #
        # 入力側 -ss
        # できるだけ高速にシーク。
        # MP3は再エンコードするため、
        # ここでは問題ない。
        # ==================================================

        if has_range:

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
        # 音声のみMP3
        # ==================================================

        command.extend([

            "-map",
            "0:a:0",

            "-vn",

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

            "-metadata",
            "title=" + mp3_title,

            "-metadata",
            "comment=YouTube Converter",

            str(temporary_output)

        ])

        print(
            "[MEDIA] FFmpeg command:",
            " ".join(command),
            flush=True
        )

        # ==================================================
        # FFmpeg実行
        # ==================================================

        with open(

            log_path,

            "w",

            encoding="utf-8",

            errors="replace"

        ) as log_file:

            result = subprocess.run(

                command,

                stdout=subprocess.DEVNULL,

                stderr=log_file,

                text=True

            )

        print(
            "[MEDIA] FFmpeg returncode:",
            result.returncode,
            flush=True
        )

        # ==================================================
        # FFmpeg失敗
        # ==================================================

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
                "[MEDIA] FFmpeg ERROR:",
                log_text,
                flush=True
            )

            raise RuntimeError(

                "MP3変換に失敗しました。\n"
                +
                log_text[-5000:]

            )

        # ==================================================
        # 一時ファイル確認
        # ==================================================

        if not temporary_output.exists():

            raise FileNotFoundError(
                "FFmpegのMP3出力ファイルがありません。"
            )

        temporary_size = (
            temporary_output.stat().st_size
        )

        print(
            "[MEDIA] Temporary MP3 size:",
            temporary_size,
            "bytes",
            flush=True
        )

        if temporary_size <= 0:

            raise RuntimeError(
                "FFmpegのMP3出力サイズが0です。"
            )

        # ==================================================
        # 一時MP3をFFprobe
        # ==================================================

        _probe_mp3(
            temporary_output
        )

        # ==================================================
        # 完成ファイルへ移動
        # ==================================================

        shutil.move(

            str(temporary_output),

            str(final_output)

        )

        print(
            "[MEDIA] MP3 moved to final:",
            final_output,
            flush=True
        )

        # ==================================================
        # 完成MP3確認
        # ==================================================

        final_output = _validate_mp3(
            final_output
        )

        # ==================================================
        # 完成MP3を再度probe
        # ==================================================

        _probe_mp3(
            final_output
        )

        print(
            "[MEDIA] MP3 COMPLETE:",
            final_output,
            flush=True
        )

        # ==================================================
        # 戻り値
        # ==================================================

        return {

            "path":
                str(final_output),

            "filename":
                final_output.name,

            "video_id":
                video_id,

            "title":
                mp3_title

        }

    except Exception as error:

        print(
            "[MEDIA] create_mp3_from_file ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        # ==================================================
        # 失敗時の完成ファイル削除
        # ==================================================

        try:

            if final_output.exists():

                final_output.unlink()

        except Exception:

            pass

        raise

    finally:

        # ==================================================
        # 一時ディレクトリ削除
        # ==================================================

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
