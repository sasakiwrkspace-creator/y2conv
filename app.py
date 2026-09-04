# =====================================
# 完成ファイル確認
#
# タイトル + 時間指定 + ラジオボタン
# から完成済みファイルを検索する。
#
# 判定:
#
# mp3
#   -> MP3のみ
#
# mp4
#   -> MP4のみ
#
# subtitle_mp4
#   -> 字幕MP4
#   -> MP4
#   -> MP3
#   -> SRT
#
# =====================================


import re
from pathlib import Path


# =====================================
# ファイル名安全化
# =====================================

def _find_sanitize_filename(value):

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

    text = text.rstrip(
        " ."
    )

    if not text:

        text = "YouTube Video"

    return text


# =====================================
# 時間 → 秒
# =====================================

def _find_time_to_seconds(value):

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


# =====================================
# ファイル名用時間
#
# 例:
#
# 00:00:00 -> 000000
# 00:00:05 -> 000005
# 00:06:00 -> 000600
# 01:02:03 -> 010203
#
# =====================================

def _find_format_filename_time(value):

    seconds = _find_time_to_seconds(
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


# =====================================
# 時間サフィックス
# =====================================

def _find_build_range_suffix(
    start_time=None,
    end_time=None
):

    start_seconds = _find_time_to_seconds(
        start_time
    )

    end_seconds = _find_time_to_seconds(
        end_time
    )

    # ---------------------------------
    # 00:00:00 ～ 00:00:00
    # ---------------------------------

    if (
        start_seconds == 0
        and
        end_seconds == 0
    ):

        return ""

    return (

        "_"
        +
        _find_format_filename_time(
            start_time
        )
        +
        "_"
        +
        _find_format_filename_time(
            end_time
        )

    )


# =====================================
# ファイル情報
# =====================================

def _find_file_info(
    path
):

    if not path.is_file():

        return {

            "exists":
                False,

            "filename":
                None,

            "path":
                None

        }

    return {

        "exists":
            True,

        "filename":
            path.name,

        "path":
            str(path)

    }


# =====================================
# 完成ファイル検索
#
# タイトル:
#   YouTube Video
#
# 時間指定なし:
#
#   YouTube Video.mp4
#   YouTube Video.mp3
#   YouTube Video.srt
#   YouTube Video_字幕.mp4
#
# 時間指定あり:
#
#   YouTube Video_000600_000630.mp4
#   YouTube Video_000600_000630.mp3
#   YouTube Video_000600_000630.srt
#   YouTube Video_000600_000630_字幕.mp4
#
# =====================================

def _find_completed_files(
    title,
    output_type,
    start_time=None,
    end_time=None
):

    safe_title = _find_sanitize_filename(
        title
    )

    range_suffix = _find_build_range_suffix(
        start_time=start_time,
        end_time=end_time
    )

    base_name = (
        safe_title
        +
        range_suffix
    )

    output_dir = Path(
        DOWNLOAD_DIR
    )

    # =================================
    # 通常ファイル
    # =================================

    mp3_path = (
        output_dir
        /
        f"{base_name}.mp3"
    )

    mp4_path = (
        output_dir
        /
        f"{base_name}.mp4"
    )

    srt_path = (
        output_dir
        /
        f"{base_name}.srt"
    )

    subtitle_mp4_path = (
        output_dir
        /
        f"{base_name}_字幕.mp4"
    )

    # =================================
    # ラジオボタン別判定
    # =================================

    result = {

        "title":
            title,

        "output_type":
            output_type,

        "base_name":
            base_name,

        "files": {

            "mp3":
                _find_file_info(
                    mp3_path
                ),

            "mp4":
                _find_file_info(
                    mp4_path
                ),

            "srt":
                _find_file_info(
                    srt_path
                ),

            "subtitle_mp4":
                _find_file_info(
                    subtitle_mp4_path
                )

        },

        "buttons": []

    }

    # =================================
    # mp3
    #
    # MP3ボタンのみ
    # =================================

    if output_type == "mp3":

        if mp3_path.is_file():

            result["buttons"] = [

                {

                    "type":
                        "mp3",

                    "label":
                        "[MP3]",

                    "filename":
                        mp3_path.name,

                    "path":
                        str(mp3_path)

                }

            ]

    # =================================
    # mp4
    #
    # MP4ボタンのみ
    # =================================

    elif output_type == "mp4":

        if mp4_path.is_file():

            result["buttons"] = [

                {

                    "type":
                        "mp4",

                    "label":
                        "[MP4]",

                    "filename":
                        mp4_path.name,

                    "path":
                        str(mp4_path)

                }

            ]

    # =================================
    # 字幕mp4
    #
    # 字幕MP4
    #
    # [字幕MP4]
    #
    # 通常ファイル
    #
    # [MP4] [MP3] [SRT]
    #
    # =================================

    elif output_type == "subtitle_mp4":

        if subtitle_mp4_path.is_file():

            result["buttons"].append(

                {

                    "type":
                        "subtitle_mp4",

                    "label":
                        "[字幕MP4]",

                    "filename":
                        subtitle_mp4_path.name,

                    "path":
                        str(subtitle_mp4_path)

                }

            )

        if mp4_path.is_file():

            result["buttons"].append(

                {

                    "type":
                        "mp4",

                    "label":
                        "[MP4]",

                    "filename":
                        mp4_path.name,

                    "path":
                        str(mp4_path)

                }

            )

        if mp3_path.is_file():

            result["buttons"].append(

                {

                    "type":
                        "mp3",

                    "label":
                        "[MP3]",

                    "filename":
                        mp3_path.name,

                    "path":
                        str(mp3_path)

                }

            )

        if srt_path.is_file():

            result["buttons"].append(

                {

                    "type":
                        "srt",

                    "label":
                        "[SRT]",

                    "filename":
                        srt_path.name,

                    "path":
                        str(srt_path)

                }

            )

    return result


# =====================================
# 完成ファイル確認API
#
# POST /find-completed-files
#
# JSON:
#
# {
#   "title": "動画タイトル",
#   "output_type": "mp3",
#   "start_time": "00:00:00",
#   "end_time": "00:00:00"
# }
#
# =====================================

@app.route(
    "/find-completed-files",
    methods=["POST"]
)
def find_completed_files():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or
            {}
        )

        title = data.get(
            "title"
        )

        output_type = data.get(
            "output_type"
        )

        start_time = data.get(
            "start_time"
        )

        end_time = data.get(
            "end_time"
        )

        # =================================
        # タイトル確認
        # =================================

        if not title:

            return jsonify({

                "success":
                    False,

                "message":
                    "タイトルが指定されていません。"

            }), 400

        # =================================
        # ラジオボタン確認
        # =================================

        if output_type not in (
            "mp3",
            "mp4",
            "subtitle_mp4"
        ):

            return jsonify({

                "success":
                    False,

                "message":
                    "出力形式が不正です。"

            }), 400

        # =================================
        # 時間確認
        # =================================

        try:

            start_seconds = (
                _find_time_to_seconds(
                    start_time
                )
            )

            end_seconds = (
                _find_time_to_seconds(
                    end_time
                )
            )

            if start_seconds < 0:

                raise ValueError(
                    "開始時間は0秒以上にしてください。"
                )

            if end_seconds < 0:

                raise ValueError(
                    "終了時間は0秒以上にしてください。"
                )

            if not (
                start_seconds == 0
                and
                end_seconds == 0
            ):

                if end_seconds <= start_seconds:

                    raise ValueError(
                        "終了時間は開始時間より後にしてください。"
                    )

        except Exception as error:

            return jsonify({

                "success":
                    False,

                "message":
                    str(error)

            }), 400

        # =================================
        # 検索
        # =================================

        result = _find_completed_files(

            title=
                title,

            output_type=
                output_type,

            start_time=
                start_time,

            end_time=
                end_time

        )

        return jsonify({

            "success":
                True,

            **result

        })

    except Exception as error:

        print(
            "[APP] /find-completed-files ERROR:",
            repr(error),
            flush=True
        )

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 500
