# ==========================================================
# subtitle_mp4.py
#
# タブ1「字幕mp4」専用
# 連続処理管理
#
# 処理順:
#
#   ① MP4作成
#       ↓
#   ② MP3作成
#       ↓
#   ③ SRT作成
#       ↓
#   ④ 字幕MP4作成
#
# 役割:
#
#   routes/convert.py
#          ↓
#   subtitle_mp4.py
#          ↓
#   ytdlp_stream.py
#   media_extract.py
#   routes/subtitle_routes.py
#          ↓
#   subtitle.py
#
# 注意:
#
#   ・このファイルではFlask Routeを登録しない
#   ・Job管理もしない
#   ・タブ1の連続処理だけを担当する
#   ・各工程が成功した場合のみ次の工程へ進む
#   ・途中で失敗した場合は例外を返す
#
# ==========================================================


import os
import traceback

from pathlib import Path


# ==========================================================
# MP4作成
# ==========================================================

from ytdlp_stream import (
    create_mp4_full,
    create_mp4_range
)


# ==========================================================
# MP3作成
# ==========================================================

from media_extract import (
    create_mp3_from_file
)


# ==========================================================
# 字幕関連
#
# routes/subtitle_routes.py にある共通関数を使用する。
#
# create_srt_from_mp3()
#     ↓
# Gemini
#     ↓
# SRT
#
# create_subtitle_mp4()
#     ↓
# subtitle.py
#     ↓
# 字幕MP4
#
# ==========================================================

from routes.subtitle_routes import (
    create_srt_from_mp3,
    create_subtitle_mp4
)


# ==========================================================
# 共通ログ
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

            f"{label}がありません: "
            +
            str(path)

        )


    if not path.is_file():

        raise RuntimeError(

            f"{label}のパスがファイルではありません: "
            +
            str(path)

        )


    if path.suffix.lower() != extension.lower():

        raise RuntimeError(

            f"{label}の拡張子が不正です: "
            +
            str(path)

        )


    try:

        size = path.stat().st_size

    except OSError as error:

        raise RuntimeError(

            f"{label}のサイズを確認できません: "
            +
            str(error)

        )


    if size <= 0:

        raise RuntimeError(

            f"{label}のファイルサイズが0 bytesです: "
            +
            str(path)

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


    result_path = result.get(
        "path"
    )


    if not result_path:

        raise RuntimeError(
            "MP4作成結果にpathがありません。"
        )


    mp4_path = validate_file(

        result_path,

        ".mp4",

        "MP4"

    )


    return mp4_path


# ==========================================================
# MP4タイトル取得
# ==========================================================

def get_title_from_result(
    result
):

    if not result:

        return "YouTube Video"


    title = (

        result.get(
            "title"
        )

        or

        "YouTube Video"

    )


    return str(
        title
    ).strip() or "YouTube Video"


# ==========================================================
# MP4 duration取得
# ==========================================================

def get_duration_from_result(
    result
):

    if not result:

        return None


    return result.get(
        "duration"
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


    result_path = result.get(
        "path"
    )


    if not result_path:

        raise RuntimeError(
            "MP3作成結果にpathがありません。"
        )


    mp3_path = validate_file(

        result_path,

        ".mp3",

        "MP3"

    )


    return mp3_path


# ==========================================================
# タイトル安全化
#
# subtitle_mp4.py単体でも使用できるようにする。
#
# ==========================================================

def sanitize_filename(
    value
):

    import re


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


    return text[:180].rstrip(
        " ."
    )


# ==========================================================
# 完成MP4 / MP3のタイトルリネーム
#
# create_mp4_full / create_mp4_range
# create_mp3_from_file
# が生成した一時的な名前を、
# YouTubeタイトル + 時間範囲に統一する。
#
# ==========================================================

def rename_output_file(
    result,
    output_type,
    title,
    start_time=None,
    end_time=None
):

    if not result:

        raise RuntimeError(

            f"{output_type}作成結果がありません。"

        )


    original_path_text = result.get(
        "path"
    )


    if not original_path_text:

        raise RuntimeError(

            f"{output_type}作成結果にpathがありません。"

        )


    original_path = validate_file(

        original_path_text,

        "." + output_type,

        output_type.upper()

    )


    safe_title = sanitize_filename(
        title
    )


    # ------------------------------------------------------
    # 時間範囲
    # ------------------------------------------------------

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


    start_seconds = time_to_seconds(
        start_time
    )


    end_seconds = time_to_seconds(
        end_time
    )


    # ------------------------------------------------------
    # ファイル名用時間
    # ------------------------------------------------------

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


    # ------------------------------------------------------
    # suffix
    # ------------------------------------------------------

    if (

        start_seconds == 0

        and

        end_seconds == 0

    ):

        range_suffix = ""


    else:

        range_suffix = (

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


    extension = original_path.suffix.lower()


    new_filename = (

        safe_title
        +
        range_suffix
        +
        extension

    )


    new_path = (

        original_path.parent
        /
        new_filename

    )


    log(
        f"{output_type.upper()} rename:"
    )


    log(
        f"  {original_path}"
    )


    log(
        f"  -> {new_path}"
    )


    if original_path != new_path:

        if new_path.exists():

            log(
                f"既存ファイル削除: {new_path}"
            )

            new_path.unlink()


        original_path.rename(
            new_path
        )


    return validate_file(

        new_path,

        extension,

        output_type.upper()

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


    result_path = result.get(
        "subtitle_mp4_path"
    )


    if not result_path:

        raise RuntimeError(

            "字幕MP4作成結果に"
            "subtitle_mp4_pathがありません。"

        )


    subtitle_mp4_path = validate_file(

        result_path,

        ".mp4",

        "字幕MP4"

    )


    return subtitle_mp4_path


# ==========================================================
# 連続処理本体
#
# ==========================================================
#
# 処理順:
#
#   ① MP4
#   ② MP3
#   ③ SRT
#   ④ 字幕MP4
#
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


    # ======================================================
    # 出力先
    # ======================================================

    if output_dir:

        output_dir = Path(
            output_dir
        )

    else:

        output_dir = (

            Path(
                os.getcwd()
            )
            /
            "downloads"

        )


    output_dir.mkdir(

        parents=True,

        exist_ok=True

    )


    log(
        f"OUTPUT_DIR: {output_dir}"
    )


    # ======================================================
    # URL確認
    # ======================================================

    if not url:

        raise ValueError(
            "YouTube URLが指定されていません。"
        )


    # ======================================================
    # 全体判定
    # ======================================================

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


    full_download = (

        time_to_seconds(
            start_time
        ) == 0

        and

        time_to_seconds(
            end_time
        ) == 0

    )


    title = "YouTube Video"

    duration = None


    mp4_path = None

    mp3_path = None

    srt_path = None

    subtitle_mp4_path = None


    # ======================================================
    # ① MP4作成
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 1 / 4"
    )

    log(
        "MP4作成開始"
    )

    log(
        "------------------------------------------"
    )


    try:

        if full_download:

            log(
                "MP4 full download"
            )


            mp4_result = create_mp4_full(

                url=
                    url,

                output_dir=
                    output_dir

            )


        else:

            log(
                "MP4 range download"
            )


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


        title = get_title_from_result(
            mp4_result
        )


        duration = get_duration_from_result(
            mp4_result
        )


        # --------------------------------------------------
        # MP4をタイトル名へ変更
        # --------------------------------------------------

        mp4_path = rename_output_file(

            result={
                "path":
                    str(mp4_path)
            },

            output_type=
                "mp4",

            title=
                title,

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
            "STEP 1 ERROR"
        )

        log(
            repr(error)
        )

        raise RuntimeError(

            "MP4作成に失敗しました: "
            +
            str(error)

        ) from error


    # ======================================================
    # ② MP3作成
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 2 / 4"
    )

    log(
        "MP3作成開始"
    )

    log(
        "------------------------------------------"
    )


    try:

        mp3_result = create_mp3_from_file(

            input_file=
                str(mp4_path),

            output_dir=
                output_dir,

            title=
                title,

            start_time=
                start_time,

            end_time=
                end_time

        )


        mp3_path = validate_mp3_result(
            mp3_result
        )


        # --------------------------------------------------
        # MP3をタイトル名へ変更
        # --------------------------------------------------

        mp3_path = rename_output_file(

            result={
                "path":
                    str(mp3_path)
            },

            output_type=
                "mp3",

            title=
                title,

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
            "STEP 2 ERROR"
        )

        log(
            repr(error)
        )

        raise RuntimeError(

            "MP3作成に失敗しました: "
            +
            str(error)

        ) from error


    # ======================================================
    # ③ SRT作成
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 3 / 4"
    )

    log(
        "SRT作成開始"
    )

    log(
        "------------------------------------------"
    )


    try:

        srt_result = create_srt_from_mp3(

            str(mp3_path)

        )


        if not srt_result:

            raise RuntimeError(
                "SRT作成結果が空です。"
            )


        srt_path_text = srt_result.get(
            "srt_path"
        )


        if not srt_path_text:

            srt_filename = srt_result.get(
                "srt_file"
            )


            if not srt_filename:

                raise RuntimeError(

                    "SRT作成結果に"
                    "srt_path / srt_fileがありません。"

                )


            srt_path = (

                output_dir
                /
                srt_filename

            )


        else:

            srt_path = Path(
                srt_path_text
            )


        srt_path = validate_file(

            srt_path,

            ".srt",

            "SRT"

        )


        log(
            f"STEP 3 COMPLETE: {srt_path}"
        )


    except Exception as error:

        log(
            "STEP 3 ERROR"
        )

        log(
            repr(error)
        )

        raise RuntimeError(

            "SRT作成に失敗しました: "
            +
            str(error)

        ) from error


    # ======================================================
    # ④ 字幕MP4作成
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 4 / 4"
    )

    log(
        "字幕MP4作成開始"
    )

    log(
        "------------------------------------------"


    )


    try:

        subtitle_result = create_subtitle_mp4(

            str(mp4_path),

            str(srt_path)

        )


        subtitle_mp4_path = (
            validate_subtitle_mp4_result(
                subtitle_result
            )
        )


        log(
            f"STEP 4 COMPLETE: {subtitle_mp4_path}"
        )


    except Exception as error:

        log(
            "STEP 4 ERROR"
        )

        log(
            repr(error)
        )

        raise RuntimeError(

            "字幕MP4作成に失敗しました: "
            +
            str(error)

        ) from error


    # ======================================================
    # 最終確認
    # ======================================================

    log(
        "=========================================="
    )

    log(
        "字幕MP4連続処理 COMPLETE"
    )

    log(
        "=========================================="
    )

    log(
        f"MP4: {mp4_path}"
    )

    log(
        f"MP3: {mp3_path}"
    )

    log(
        f"SRT: {srt_path}"
    )

    log(
        f"字幕MP4: {subtitle_mp4_path}"
    )

    log(
        "=========================================="
    )


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
# 別名
#
# convert.py側から呼びやすくする。
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
# テスト用
#
# python subtitle_mp4.py
#
# では実行せず、
# URLを指定した場合のみ実行する。
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
            "python subtitle_mp4.py "
            "YouTube_URL"
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
