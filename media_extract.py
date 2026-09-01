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
#
# HH:MM:SS
# MM:SS
# 秒
# に対応
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
#
# 00:00:00 ～ 00:00:00
# → 全体
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

    if not input_path.exists():

        raise FileNotFoundError(
            f"入力ファイルがありません: {input_path}"
        )

    if not input_path.is_file():

        raise RuntimeError(
            f"入力パスがファイルではありません: {input_path}"
        )

    if input_path.stat().st_size <= 0:

        raise RuntimeError(
            f"入力ファイルのサイズが0です: {input_path}"
        )

    print(
        "[MEDIA] Input:",
        input_path,
        flush=True
    )

    print(
        "[MEDIA] Input size:",
        input_path.stat().st_size,
        "bytes",
        flush=True
    )

    return input_path


# ==========================================================
# 出力先確認
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

    return output_path


# ==========================================================
# MP3出力確認
# ==========================================================

def _validate_mp3(
    path
):

    path = Path(
        path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"MP3ファイルがありません: {path}"
        )

    if not path.is_file():

        raise RuntimeError(
            f"MP3ファイルではありません: {path}"
        )

    if path.stat().st_size <= 0:

        raise RuntimeError(
            f"MP3ファイルのサイズが0です: {path}"
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
# 重要：
#
# この関数では時間範囲をファイル名に付けない。
#
# 完成ファイルは必ず
#
#     VIDEO_ID.mp3
#
# とする。
#
# 時間指定がある場合も、
# まず完成MP3を作り、
# convert.py側で完成後に
#
#     VIDEO_ID_000005_000010.mp3
#
# のようにリネームする。
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

    input_path = _validate_input_file(
        input_file
    )

    output_path = _prepare_output_dir(
        output_dir
    )

    ffmpeg_path = _check_ffmpeg()

    # ======================================================
    # 入力ファイル名からvideo IDを取得
    #
    # download_source()が
    #
    #     VIDEO_ID.ext
    #
    # を作る前提。
    #
    # そのためstemをvideo IDとして使用する。
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

    full_conversion = not _has_time_range(

        start_time,

        end_time

    )

    print(
        "[MEDIA] full_conversion:",
        full_conversion,
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

    if not full_conversion:

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )

    # ======================================================
    # 出力ファイル
    #
    # 時間指定の有無に関係なく、
    # ここではVIDEO_ID.mp3。
    # ======================================================

    final_output = (

        output_path
        /
        f"{video_id}.mp3"

    )

    # ======================================================
    # 一時出力
    #
    # 完成前に最終ファイルを作らない。
    #
    # これにより、
    # 変換途中の壊れたMP3が
    # 完成ファイルとして残ることを防ぐ。
    # ======================================================

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

        # ==================================================
        # 既存ファイル削除
        # ==================================================

        if final_output.exists():

            print(
                "[MEDIA] Removing existing MP3:",
                final_output,
                flush=True
            )

            final_output.unlink()

        # ==================================================
        # FFmpegコマンド
        # ==================================================

        ffmpeg_command = [

            ffmpeg_path,

            "-y"

        ]

        # --------------------------------------------------
        # 時間指定あり
        # --------------------------------------------------

        if not full_conversion:

            ffmpeg_command.extend([

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

        # --------------------------------------------------
        # 全体
        # --------------------------------------------------

        else:

            ffmpeg_command.extend([

                "-i",
                str(input_path)

            ])

        # ==================================================
        # MP3エンコード
        # ==================================================

        ffmpeg_command.extend([

            "-vn",

            "-codec:a",
            "libmp3lame",

            "-b:a",
            "192k",

            "-id3v2_version",
            "3",

            "-metadata",
            "title=" + str(
                title or "YouTube Video"
            ),

            "-metadata",
            "comment=YouTube Converter",

            str(temporary_output)

        ])

        print(
            "[MEDIA] FFmpeg:",
            " ".join(
                ffmpeg_command
            ),
            flush=True
        )

        # ==================================================
        # FFmpeg実行
        #
        # stderrはファイルへ。
        # ==================================================

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
            "[MEDIA] FFmpeg returncode:",
            result.returncode,
            flush=True
        )

        # ==================================================
        # FFmpegエラー
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
                "MP3変換に失敗しました\n"
                +
                log_text
            )

        # ==================================================
        # 一時出力確認
        # ==================================================

        if not temporary_output.exists():

            raise FileNotFoundError(
                "FFmpegのMP3出力ファイルがありません"
            )

        if temporary_output.stat().st_size <= 0:

            raise RuntimeError(
                "FFmpegのMP3出力ファイルのサイズが0です"
            )

        # ==================================================
        # 完成ファイルへ移動
        #
        # ここで初めてVIDEO_ID.mp3が完成。
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

        # ==================================================
        # 結果
        #
        # convert.pyがこの直後にリネームする。
        # ==================================================

        return {

            "path":
                str(final_output),

            "filename":
                final_output.name,

            "video_id":
                video_id,

            "title":
                title or "YouTube Video"

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
