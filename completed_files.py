# ==========================================================
# completed_files.py
#
# 完成済みファイル確認専用
#
# 役割:
#
#   ・タイトル
#   ・ラジオボタンの選択
#   ・開始時間
#   ・終了時間
#
# を基準に downloads フォルダを検索する。
#
# ==========================================================
#
# 判定ルール
#
# ----------------------------------------------------------
#
# ラジオボタン:
#
#   mp3
#       ↓
#   タイトル.mp3
#       ↓
#   [MP3]
#
#
#   mp4
#       ↓
#   タイトル.mp4
#       ↓
#   [MP4]
#
#
#   subtitle_mp4
#       ↓
#   タイトル_字幕.mp4
#   タイトル.mp4
#   タイトル.mp3
#   タイトル.srt
#       ↓
#   [字幕MP4] [MP4] [MP3] [SRT]
#
# ----------------------------------------------------------
#
# 時間指定あり:
#
#   タイトル_000600_000630.mp4
#   タイトル_000600_000630.mp3
#   タイトル_000600_000630.srt
#   タイトル_000600_000630_字幕.mp4
#
# ----------------------------------------------------------
#
# 重要:
#
#   ・実際にファイルが存在するものだけ返す。
#   ・ファイルが存在しない場合はボタンを返さない。
#   ・ラジオボタンの種類も必ず確認する。
#   ・SRTはリネームしない。
#   ・字幕MP4は "_字幕.mp4" を使用する。
#
# ==========================================================


import re

from pathlib import Path


# ==========================================================
# デフォルト出力先
# ==========================================================

DEFAULT_DOWNLOAD_DIR = (
    Path.cwd()
    /
    "downloads"
)


# ==========================================================
# ファイル名安全化
#
# routes.convert.py / subtitle_mp4.py と同じルール
# ==========================================================

def sanitize_filename(
    value
):

    text = str(
        value or "YouTube Video"
    ).strip()

    if not text:

        text = "YouTube Video"

    # ------------------------------------------------------
    # 改行・タブ
    # ------------------------------------------------------

    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    # ------------------------------------------------------
    # Windowsで使用できない文字
    # ------------------------------------------------------

    text = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        text
    )

    # ------------------------------------------------------
    # 制御文字
    # ------------------------------------------------------

    text = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
        text
    )

    # ------------------------------------------------------
    # 連続スペース
    # ------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # ------------------------------------------------------
    # ファイル名末尾の
    # スペース / ドット
    # ------------------------------------------------------

    text = text.rstrip(
        " ."
    )

    if not text:

        text = "YouTube Video"

    # ------------------------------------------------------
    # 長すぎるタイトルを制限
    # ------------------------------------------------------

    text = text[:180]

    text = text.rstrip(
        " ."
    )

    if not text:

        text = "YouTube Video"

    return text


# ==========================================================
# 時間 → 秒
#
# 対応:
#
#   00:00:00
#   00:01:30
#   01:02:03
#   90
#   90.5
#
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

        # --------------------------------------------------
        # HH:MM:SS
        # --------------------------------------------------

        if len(parts) == 3:

            return (

                float(parts[0]) * 3600

                +

                float(parts[1]) * 60

                +

                float(parts[2])

            )

        # --------------------------------------------------
        # MM:SS
        # --------------------------------------------------

        if len(parts) == 2:

            return (

                float(parts[0]) * 60

                +

                float(parts[1])

            )

        # --------------------------------------------------
        # 秒
        # --------------------------------------------------

        return float(
            text
        )

    except Exception as error:

        raise ValueError(
            f"時間形式が不正です: {value}"
        ) from error


# ==========================================================
# 時間 → ファイル名用6桁
#
# 例:
#
#   0
#       -> 000000
#
#   5
#       -> 000005
#
#   65
#       -> 000105
#
#   3600
#       -> 010000
#
#   3665
#       -> 010105
#
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
# 全体ダウンロード判定
#
# 00:00:00 ～ 00:00:00
#       ↓
# 全体
#
# ==========================================================

def is_full_download(
    start_time=None,
    end_time=None
):

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
# 時間サフィックス
#
# 全体:
#
#   ""
#
# 指定区間:
#
#   _000600_000630
#
# ==========================================================

def build_range_suffix(
    start_time=None,
    end_time=None
):

    if is_full_download(
        start_time=start_time,
        end_time=end_time
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
# ファイル存在確認
#
# 戻り値:
#
# {
#     "exists": True,
#     "filename": "...",
#     "path": "..."
# }
#
# ==========================================================

def get_file_info(
    path
):

    path = Path(
        path
    )

    # ------------------------------------------------------
    # ファイルがない
    # ------------------------------------------------------

    if not path.is_file():

        return {

            "exists":
                False,

            "filename":
                None,

            "path":
                None

        }

    # ------------------------------------------------------
    # ファイルサイズ確認
    #
    # 0 bytesのファイルは完成ファイルとして扱わない。
    # ------------------------------------------------------

    try:

        size = path.stat().st_size

    except OSError:

        return {

            "exists":
                False,

            "filename":
                None,

            "path":
                None

        }

    if size <= 0:

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


# ==========================================================
# 完成ファイル検索
#
# この関数が本体。
#
# ==========================================================

def find_completed_files(
    title,
    output_type,
    start_time=None,
    end_time=None,
    output_dir=None
):

    # ======================================================
    # タイトル確認
    # ======================================================

    if not title:

        raise ValueError(
            "タイトルが指定されていません。"
        )

    # ======================================================
    # ラジオボタン確認
    # ======================================================

    if output_type not in (
        "mp3",
        "mp4",
        "subtitle_mp4"
    ):

        raise ValueError(
            "出力形式が不正です: "
            +
            str(output_type)
        )

    # ======================================================
    # 時間確認
    # ======================================================

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

    # ------------------------------------------------------
    # 全体ではない場合
    # ------------------------------------------------------

    if not (
        start_seconds == 0
        and
        end_seconds == 0
    ):

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後にしてください。"
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
            DEFAULT_DOWNLOAD_DIR
        )

    # ======================================================
    # タイトル
    # ======================================================

    safe_title = sanitize_filename(
        title
    )

    # ======================================================
    # 時間サフィックス
    # ======================================================

    range_suffix = build_range_suffix(

        start_time=
            start_time,

        end_time=
            end_time

    )

    # ======================================================
    # 基本ファイル名
    # ======================================================

    base_name = (

        safe_title

        +

        range_suffix

    )

    # ======================================================
    # ファイルパス
    # ======================================================

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

    # ======================================================
    # 全ファイル情報
    #
    # 実際の存在状況をここで確認する。
    # ======================================================

    files = {

        "mp3":
            get_file_info(
                mp3_path
            ),

        "mp4":
            get_file_info(
                mp4_path
            ),

        "srt":
            get_file_info(
                srt_path
            ),

        "subtitle_mp4":
            get_file_info(
                subtitle_mp4_path
            )

    }

    # ======================================================
    # ボタン
    # ======================================================

    buttons = []

    # ======================================================
    # MP3ラジオボタン
    #
    # MP3だけ表示
    # ======================================================

    if output_type == "mp3":

        if files["mp3"]["exists"]:

            buttons.append({

                "type":
                    "mp3",

                "label":
                    "[MP3]",

                "filename":
                    files["mp3"]["filename"],

                "path":
                    files["mp3"]["path"]

            })

    # ======================================================
    # MP4ラジオボタン
    #
    # MP4だけ表示
    # ======================================================

    elif output_type == "mp4":

        if files["mp4"]["exists"]:

            buttons.append({

                "type":
                    "mp4",

                "label":
                    "[MP4]",

                "filename":
                    files["mp4"]["filename"],

                "path":
                    files["mp4"]["path"]

            })

    # ======================================================
    # 字幕MP4ラジオボタン
    #
    # 表示順:
    #
    #   [字幕MP4]
    #   [MP4]
    #   [MP3]
    #   [SRT]
    #
    # 実際に存在するものだけ。
    # ======================================================

    elif output_type == "subtitle_mp4":

        # --------------------------------------------------
        # 字幕MP4
        # --------------------------------------------------

        if files["subtitle_mp4"]["exists"]:

            buttons.append({

                "type":
                    "subtitle_mp4",

                "label":
                    "[字幕MP4]",

                "filename":
                    files["subtitle_mp4"]["filename"],

                "path":
                    files["subtitle_mp4"]["path"]

            })

        # --------------------------------------------------
        # MP4
        # --------------------------------------------------

        if files["mp4"]["exists"]:

            buttons.append({

                "type":
                    "mp4",

                "label":
                    "[MP4]",

                "filename":
                    files["mp4"]["filename"],

                "path":
                    files["mp4"]["path"]

            })

        # --------------------------------------------------
        # MP3
        # --------------------------------------------------

        if files["mp3"]["exists"]:

            buttons.append({

                "type":
                    "mp3",

                "label":
                    "[MP3]",

                "filename":
                    files["mp3"]["filename"],

                "path":
                    files["mp3"]["path"]

            })

        # --------------------------------------------------
        # SRT
        # --------------------------------------------------

        if files["srt"]["exists"]:

            buttons.append({

                "type":
                    "srt",

                "label":
                    "[SRT]",

                "filename":
                    files["srt"]["filename"],

                "path":
                    files["srt"]["path"]

            })

    # ======================================================
    # 結果
    # ======================================================

    return {

        "success":
            True,

        "title":
            title,

        "safe_title":
            safe_title,

        "output_type":
            output_type,

        "start_time":
            start_time,

        "end_time":
            end_time,

        "full_download":
            is_full_download(
                start_time=start_time,
                end_time=end_time
            ),

        "range_suffix":
            range_suffix,

        "base_name":
            base_name,

        "output_dir":
            str(output_dir),

        "files":
            files,

        "buttons":
            buttons

    }


# ==========================================================
# 互換用関数
#
# find_completed_files() を使用するだけでもよいが、
# 外部から確認しやすいように用意。
# ==========================================================

def has_completed_file(
    title,
    output_type,
    start_time=None,
    end_time=None,
    output_dir=None
):

    result = find_completed_files(

        title=
            title,

        output_type=
            output_type,

        start_time=
            start_time,

        end_time=
            end_time,

        output_dir=
            output_dir

    )

    return len(
        result["buttons"]
    ) > 0


# ==========================================================
# デバッグ表示
# ==========================================================

def print_completed_files(
    result
):

    print(
        "=========================================="
    )

    print(
        "[COMPLETED_FILES]"
    )

    print(
        "=========================================="
    )

    print(
        "title:",
        result.get("title")
    )

    print(
        "output_type:",
        result.get("output_type")
    )

    print(
        "start_time:",
        result.get("start_time")
    )

    print(
        "end_time:",
        result.get("end_time")
    )

    print(
        "full_download:",
        result.get("full_download")
    )

    print(
        "base_name:",
        result.get("base_name")
    )

    print(
        "------------------------------------------"
    )

    print(
        "files:"
    )

    files = result.get(
        "files",
        {}
    )

    for key, info in files.items():

        print(
            f"  {key}:",
            info
        )

    print(
        "------------------------------------------"
    )

    print(
        "buttons:"
    )

    for button in result.get(
        "buttons",
        []
    ):

        print(
            " ",
            button
        )

    print(
        "=========================================="
    )


# ==========================================================
# 単体テスト
#
# python completed_files.py
#
# ==========================================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        "completed_files.py TEST"
    )

    print(
        "=========================================="
    )

    # ======================================================
    # テスト1
    # ======================================================

    print()
    print(
        "[TEST 1] MP3"
    )

    try:

        result = find_completed_files(

            title=
                "YouTube Video",

            output_type=
                "mp3",

            start_time=
                "00:00:00",

            end_time=
                "00:00:00"

        )

        print_completed_files(
            result
        )

    except Exception as error:

        print(
            "[TEST 1 ERROR]",
            error
        )

    # ======================================================
    # テスト2
    # ======================================================

    print()
    print(
        "[TEST 2] MP4"
    )

    try:

        result = find_completed_files(

            title=
                "YouTube Video",

            output_type=
                "mp4",

            start_time=
                "00:00:00",

            end_time=
                "00:00:00"

        )

        print_completed_files(
            result
        )

    except Exception as error:

        print(
            "[TEST 2 ERROR]",
            error
        )

    # ======================================================
    # テスト3
    # ======================================================

    print()
    print(
        "[TEST 3] 字幕MP4"
    )

    try:

        result = find_completed_files(

            title=
                "YouTube Video",

            output_type=
                "subtitle_mp4",

            start_time=
                "00:00:00",

            end_time=
                "00:00:00"

        )

        print_completed_files(
            result
        )

    except Exception as error:

        print(
            "[TEST 3 ERROR]",
            error
        )

    # ======================================================
    # テスト4
    # ======================================================

    print()
    print(
        "[TEST 4] 字幕MP4 + 時間指定"
    )

    try:

        result = find_completed_files(

            title=
                "YouTube Video",

            output_type=
                "subtitle_mp4",

            start_time=
                "00:06:00",

            end_time=
                "00:06:30"

        )

        print_completed_files(
            result
        )

    except Exception as error:

        print(
            "[TEST 4 ERROR]",
            error
        )

    print()

    print(
        "completed_files.py TEST END"
    )

    print()
