# ==========================================================
# subtitle_mp4.py
#
# タブ1「字幕mp4」専用
#
# 処理順:
#
#   ① MP4
#       ↓
#   ② MP3
#       ↓
#   ③ SRT
#       ↓
#   ④ 字幕MP4
#
# ==========================================================

import os
import re
import traceback

from pathlib import Path


# ==========================================================
# MP4
# ==========================================================

from ytdlp_stream import (
    create_mp4_full,
    create_mp4_range
)


# ==========================================================
# MP3
# ==========================================================

from media_extract import (
    create_mp3_from_file
)


# ==========================================================
# Subtitle
# ==========================================================

from routes.subtitle_routes import (
    create_srt_from_mp3,
    create_subtitle_mp4 as create_subtitle_mp4_from_route
)


# ==========================================================
# LOG
# ==========================================================

def log(
    message
):

    print(
        "[SUBTITLE_MP4]",
        message,
        flush=True
    )


# ==========================================================
# 時間 → 秒
# ==========================================================

def time_to_seconds(
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
# 全体判定
# ==========================================================

def is_full_download(
    start_time=None,
    end_time=None
):

    return (

        time_to_seconds(
            start_time
        ) == 0

        and

        time_to_seconds(
            end_time
        ) == 0

    )


# ==========================================================
# ファイル名時間
# ==========================================================

def format_filename_time(
    value
):

    seconds = time_to_seconds(
        value
    )

    total_seconds = int(
        seconds
    )

    hours = (
        total_seconds // 3600
    )

    minutes = (
        total_seconds % 3600
    ) // 60

    secs = (
        total_seconds % 60
    )

    return (

        f"{hours:02d}"
        f"{minutes:02d}"
        f"{secs:02d}"

    )


# ==========================================================
# 時間suffix
# ==========================================================

def build_range_suffix(
    start_time=None,
    end_time=None
):

    if is_full_download(
        start_time,
        end_time
    ):

        return ""

    return (

        "_"
        +
        format_filename_time(
            start_time
        )
        +
        "_"
        +
        format_filename_time(
            end_time
        )

    )


# ==========================================================
# ファイル名安全化
# ==========================================================

def sanitize_filename(
    value
):

    text = str(
        value or "YouTube Video"
    ).strip()

    if not text:

        text = "YouTube Video"

    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    text = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        text
    )

    text = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.rstrip(
        " ."
    )

    if not text:

        text = "YouTube Video"

    text = text[:180]

    return text.rstrip(
        " ."
    ) or "YouTube Video"


# ==========================================================
# ファイル確認
# ==========================================================

def validate_file(
    file_path,
    extension,
    label
):

    if not file_path:

        raise RuntimeError(
            f"{label}のパスがありません。"
        )

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"{label}がありません: {path}"
        )

    if not path.is_file():

        raise RuntimeError(
            f"{label}のパスがファイルではありません: {path}"
        )

    if path.suffix.lower() != extension.lower():

        raise RuntimeError(
            f"{label}の拡張子が不正です: {path}"
        )

    if path.stat().st_size <= 0:

        raise RuntimeError(
            f"{label}のファイルサイズが0 bytesです: {path}"
        )

    return path


# ==========================================================
# MP4結果確認
# ==========================================================

def validate_mp4_result(
    result
):

    if not result:

        raise RuntimeError(
            "MP4作成結果が空です。"
        )

    path = result.get(
        "path"
    )

    return validate_file(
        path,
        ".mp4",
        "MP4"
    )


# ==========================================================
# MP3結果確認
# ==========================================================

def validate_mp3_result(
    result
):

    if not result:

        raise RuntimeError(
            "MP3作成結果が空です。"
        )

    path = result.get(
        "path"
    )

    return validate_file(
        path,
        ".mp3",
        "MP3"
    )


# ==========================================================
# SRT結果確認
# ==========================================================

def validate_srt_result(
    result,
    output_dir
):

    if not result:

        raise RuntimeError(
            "SRT作成結果が空です。"
        )

    srt_path_text = result.get(
        "srt_path"
    )

    if srt_path_text:

        return validate_file(
            srt_path_text,
            ".srt",
            "SRT"
        )

    srt_filename = result.get(
        "srt_file"
    )

    if not srt_filename:

        raise RuntimeError(
            "SRT作成結果にsrt_path / srt_fileがありません。"
        )

    srt_path = (
        Path(output_dir)
        /
        srt_filename
    )

    return validate_file(
        srt_path,
        ".srt",
        "SRT"
    )


# ==========================================================
# 字幕MP4結果確認
# ==========================================================

def validate_subtitle_mp4_result(
    result
):

    if not result:

        raise RuntimeError(
            "字幕MP4作成結果が空です。"
        )

    path = result.get(
        "subtitle_mp4_path"
    )

    return validate_file(
        path,
        ".mp4",
        "字幕MP4"
    )


# ==========================================================
# リネーム
# ==========================================================

def rename_file(
    path,
    title,
    extension,
    start_time=None,
    end_time=None,
    suffix_text=""
):

    path = validate_file(
        path,
        extension,
        extension.upper()
    )

    safe_title = sanitize_filename(
        title
    )

    range_suffix = build_range_suffix(
        start_time,
        end_time
    )

    new_filename = (

        safe_title
        +
        range_suffix
        +
        suffix_text
        +
        extension

    )

    new_path = (
        path.parent
        /
        new_filename
    )

    log(
        f"RENAME: {path} -> {new_path}"
    )

    if path != new_path:

        if new_path.exists():

            new_path.unlink()

        path.rename(
            new_path
        )

    return validate_file(
        new_path,
        extension,
        extension.upper()
    )


# ==========================================================
# 連続処理
# ==========================================================

def create_subtitle_mp4_pipeline(
    url,
    start_time=None,
    end_time=None,
    output_dir=None
):

    log(
        "=========================================="
    )

    log(
        "字幕MP4連続処理 START"
    )

    log(
        "=========================================="
    )

    if not url:

        raise ValueError(
            "YouTube URLが指定されていません。"
        )

    if output_dir:

        output_dir = Path(
            output_dir
        )

    else:

        output_dir = (
            Path(os.getcwd())
            /
            "downloads"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
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

    if not is_full_download(
        start_time,
        end_time
    ):

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
            )

    full_download = is_full_download(
        start_time,
        end_time
    )

    title = "YouTube Video"

    duration = None

    mp4_path = None

    mp3_path = None

    srt_path = None

    subtitle_mp4_path = None


    # ======================================================
    # STEP 1
    # ======================================================

    log("------------------------------------------")
    log("STEP 1 / 4")
    log("MP4作成開始")
    log("------------------------------------------")

    try:

        if full_download:

            mp4_result = create_mp4_full(

                url=
                    url,

                output_dir=
                    output_dir

            )

        else:

            mp4_result = create_mp4_range(

                url=
                    url,

                output_dir=
                    output_dir,

                start_time=
                    start_time,

                end_time=
                    end_time

            )

        mp4_path = validate_mp4_result(
            mp4_result
        )

        title = str(
            mp4_result.get(
                "title"
            )
            or
            "YouTube Video"
        ).strip()

        if not title:

            title = "YouTube Video"

        duration = mp4_result.get(
            "duration"
        )

        mp4_path = rename_file(

            path=
                mp4_path,

            title=
                title,

            extension=
                ".mp4",

            start_time=
                start_time,

            end_time=
                end_time

        )

        log(
            f"STEP 1 COMPLETE: {mp4_path}"
        )

    except Exception as error:

        log(
            f"STEP 1 ERROR: {repr(error)}"
        )

        raise RuntimeError(
            "MP4作成に失敗しました: "
            +
            str(error)
        ) from error


    # ======================================================
    # STEP 2
    #
    # ★重要
    #
    # MP4はすでに①で指定区間に切られている。
    #
    # したがってここでは start/end を再指定しない。
    #
    # ======================================================

    log("------------------------------------------")
    log("STEP 2 / 4")
    log("MP3作成開始")
    log("------------------------------------------")

    try:

        log(
            "MP3 source: STEP 1で作成したMP4"
        )

        log(
            "時間指定は二重適用しません。"
        )

        mp3_result = create_mp3_from_file(

            input_file=
                str(mp4_path),

            output_dir=
                output_dir,

            title=
                title,

            start_time=
                None,

            end_time=
                None

        )

        mp3_path = validate_mp3_result(
            mp3_result
        )

        mp3_path = rename_file(

            path=
                mp3_path,

            title=
                title,

            extension=
                ".mp3",

            start_time=
                start_time,

            end_time=
                end_time

        )

        log(
            f"STEP 2 COMPLETE: {mp3_path}"
        )

    except Exception as error:

        log(
            f"STEP 2 ERROR: {repr(error)}"
        )

        raise RuntimeError(
            "MP3作成に失敗しました: "
            +
            str(error)
        ) from error


    # ======================================================
    # STEP 3
    # ======================================================

    log("------------------------------------------")
    log("STEP 3 / 4")
    log("SRT作成開始")
    log("------------------------------------------")

    try:

        srt_result = create_srt_from_mp3(
            str(mp3_path)
        )

        srt_path = validate_srt_result(
            srt_result,
            output_dir
        )

        # --------------------------------------------------
        # SRTもファイル名統一
        # --------------------------------------------------

        srt_path = rename_file(

            path=
                srt_path,

            title=
                title,

            extension=
                ".srt",

            start_time=
                start_time,

            end_time=
                end_time

        )

        log(
            f"STEP 3 COMPLETE: {srt_path}"
        )

    except Exception as error:

        log(
            f"STEP 3 ERROR: {repr(error)}"
        )

        raise RuntimeError(
            "SRT作成に失敗しました: "
            +
            str(error)
        ) from error


    # ======================================================
    # STEP 4
    # ======================================================

    log("------------------------------------------")
    log("STEP 4 / 4")
    log("字幕MP4作成開始")
    log("------------------------------------------")

    try:

        subtitle_result = create_subtitle_mp4_from_route(

            str(mp4_path),

            str(srt_path)

        )

        subtitle_mp4_path = (
            validate_subtitle_mp4_result(
                subtitle_result
            )
        )

        # --------------------------------------------------
        # 最終字幕MP4のファイル名
        # --------------------------------------------------

        subtitle_mp4_path = rename_file(

            path=
                subtitle_mp4_path,

            title=
                title,

            extension=
                ".mp4",

            start_time=
                start_time,

            end_time=
                end_time,

            suffix_text=
                "_字幕"

        )

        log(
            f"STEP 4 COMPLETE: {subtitle_mp4_path}"
        )

    except Exception as error:

        log(
            f"STEP 4 ERROR: {repr(error)}"
        )

        raise RuntimeError(
            "字幕MP4作成に失敗しました: "
            +
            str(error)

        ) from error


    # ======================================================
    # 最終確認
    # ======================================================

    validate_file(
        mp4_path,
        ".mp4",
        "MP4"
    )

    validate_file(
        mp3_path,
        ".mp3",
        "MP3"
    )

    validate_file(
        srt_path,
        ".srt",
        "SRT"
    )

    validate_file(
        subtitle_mp4_path,
        ".mp4",
        "字幕MP4"
    )

    log("==========================================")
    log("字幕MP4連続処理 COMPLETE")
    log("==========================================")

    return {

        "success":
            True,

        "title":
            title,

        "duration":
            duration,

        "mp4_path":
            str(mp4_path),

        "mp4_file":
            mp4_path.name,

        "mp3_path":
            str(mp3_path),

        "mp3_file":
            mp3_path.name,

        "srt_path":
            str(srt_path),

        "srt_file":
            srt_path.name,

        "subtitle_mp4_path":
            str(subtitle_mp4_path),

        "subtitle_mp4_file":
            subtitle_mp4_path.name

    }


# ==========================================================
# 外部エントリーポイント
# ==========================================================

def create_subtitle_mp4(
    url,
    start_time=None,
    end_time=None,
    output_dir=None
):

    return create_subtitle_mp4_pipeline(

        url=
            url,

        start_time=
            start_time,

        end_time=
            end_time,

        output_dir=
            output_dir

    )


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print()
        print(
            "使用方法:"
        )
        print()
        print(
            "python subtitle_mp4.py YouTube_URL"
        )
        print()
        print(
            "時間指定:"
        )
        print()
        print(
            "python subtitle_mp4.py "
            "YouTube_URL "
            "00:00:05 "
            "00:00:10"
        )
        print()

        sys.exit(1)

    url = sys.argv[1]

    start_time = (
        sys.argv[2]
        if len(sys.argv) >= 3
        else None
    )

    end_time = (
        sys.argv[3]
        if len(sys.argv) >= 4
        else None
    )

    try:

        result = create_subtitle_mp4_pipeline(

            url=
                url,

            start_time=
                start_time,

            end_time=
                end_time

        )

        print()
        print(
            "=========================================="
        )
        print(
            "字幕MP4連続処理成功"
        )
        print(
            "=========================================="
        )

        print(
            "MP4:",
            result["mp4_file"]
        )

        print(
            "MP3:",
            result["mp3_file"]
        )

        print(
            "SRT:",
            result["srt_file"]
        )

        print(
            "字幕MP4:",
            result["subtitle_mp4_file"]
        )

        print(
            "=========================================="
        )
        print()

        sys.exit(0)

    except Exception as error:

        print()
        print(
            "=========================================="
        )
        print(
            "字幕MP4連続処理失敗"
        )
        print(
            "=========================================="
        )

        print(
            str(error)
        )

        print(
            "=========================================="
        )

        traceback.print_exc()

        print()

        sys.exit(1)
