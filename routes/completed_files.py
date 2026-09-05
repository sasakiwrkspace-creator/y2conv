# ==========================================================
# completed_files.py
#
# 完成ファイル判定専用
#
# 役割:
#
#   処理終了
#       ↓
#   completed_files.py
#       ↓
#   存在する完成ファイルだけを判定
#       ↓
#   フロントへダウンロードボタン情報を返す
#
#
# 重要:
#
#   タブ1とタブ2は完全に分離する。
#
#   タブ1:
#
#       ラジオボタン
#           ↓
#       タイトル
#           ↓
#       時間指定
#           ↓
#       ファイル存在確認
#
#   タブ2:
#
#       上側 / 下側
#           ↓
#       タイトル
#           ↓
#       時間指定
#           ↓
#       ファイル存在確認
#
#   タブ2の判定に
#   タブ1のラジオボタンは一切使用しない。
#
#
# 時間指定:
#
#   00:00:00 → 00:00:00
#
#       タイトル.mp4
#
#   指定時間あり:
#
#       タイトル_000600_000630.mp4
#
#
# タブ1 字幕MP4:
#
#       タイトル_字幕.mp4
#
#   指定時間あり:
#
#       タイトル_000600_000630_字幕.mp4
#
# ==========================================================


import os
import re

from pathlib import Path


# ==========================================================
# 出力ディレクトリ
# ==========================================================

DEFAULT_DOWNLOAD_DIR = (
    Path(os.getcwd())
    /
    "downloads"
)


# ==========================================================
# 時間 → 秒
# ==========================================================

def time_to_seconds(value):

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
# 全体ダウンロード判定
#
# 00:00:00 → 00:00:00
#       ↓
# 時間サフィックスなし
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
# ファイル名用時間
#
# 例:
#
#   0     → 000000
#   5     → 000005
#   65    → 000105
#   3665  → 010105
# ==========================================================

def format_filename_time(value):

    seconds = time_to_seconds(
        value
    )

    total_seconds = int(
        seconds
    )

    hours = total_seconds // 3600

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
# 時間サフィックス
#
# 全体:
#
#   ""
#
# 指定区間:
#
#   _000600_000630
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
        format_filename_time(start_time)
        +
        "_"
        +
        format_filename_time(end_time)
    )


# ==========================================================
# タイトル安全化
# ==========================================================

def sanitize_filename(value):

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

    return text


# ==========================================================
# 基本ファイル名
#
# 例:
#
#   タイトル.mp3
#   タイトル.mp4
#   タイトル.srt
#
#   タイトル_000600_000630.mp3
# ==========================================================

def build_filename(
    title,
    extension,
    start_time=None,
    end_time=None
):

    safe_title = sanitize_filename(
        title
    )

    suffix = build_range_suffix(
        start_time=start_time,
        end_time=end_time
    )

    return (
        safe_title
        +
        suffix
        +
        extension
    )


# ==========================================================
# 字幕MP4ファイル名
#
# 例:
#
#   タイトル_字幕.mp4
#
#   タイトル_000600_000630_字幕.mp4
# ==========================================================

def build_subtitle_mp4_filename(
    title,
    start_time=None,
    end_time=None
):

    safe_title = sanitize_filename(
        title
    )

    suffix = build_range_suffix(
        start_time=start_time,
        end_time=end_time
    )

    return (
        safe_title
        +
        suffix
        +
        "_字幕.mp4"
    )


# ==========================================================
# ファイル存在確認
# ==========================================================

def find_file(
    download_dir,
    filename
):

    path = (
        Path(download_dir)
        /
        filename
    )

    if not path.is_file():

        return None

    try:

        if path.stat().st_size <= 0:

            return None

    except OSError:

        return None

    return path


# ==========================================================
# ファイル情報
# ==========================================================

def make_file_info(
    path,
    file_type,
    label
):

    if not path:

        return None

    return {

        "type":
            file_type,

        "label":
            label,

        "filename":
            path.name,

        "path":
            str(path),

        "download":
            True

    }


# ==========================================================
# ==========================================================
# タブ1
# ==========================================================
#
# タブ1の判定
#
# ラジオボタン:
#
#   mp3
#   mp4
#   subtitle_mp4
#
# ただし字幕MP4の場合は、
#
#   MP4
#   MP3
#   SRT
#   字幕MP4
#
# の4種類が完成する。
#
# ==========================================================

def get_tab1_files(
    title,
    radio_value,
    start_time=None,
    end_time=None,
    download_dir=None,
    known_files=None
):

    if download_dir is None:

        download_dir = (
            DEFAULT_DOWNLOAD_DIR
        )

    download_dir = Path(
        download_dir
    )

    result = {

        "tab":
            1,

        "radio":
            radio_value,

        "files":
            [],

        "buttons":
            []

    }


    # ======================================================
    # 既にconvert.pyから取得しているファイル情報を
    # 優先して利用できるようにする。
    #
    # これによりSRTの実際のファイル名が
    # create_srt_from_mp3()側で決まっていても安全。
    # ======================================================

    known_files = (
        known_files
        or
        {}
    )


    # ======================================================
    # mp3
    # ======================================================

    if radio_value == "mp3":

        mp3_path = None

        if known_files.get("mp3"):

            mp3_path = Path(
                known_files["mp3"]
            )

        else:

            filename = build_filename(
                title,
                ".mp3",
                start_time,
                end_time
            )

            mp3_path = find_file(
                download_dir,
                filename
            )


        if mp3_path:

            result["files"].append(
                make_file_info(
                    mp3_path,
                    "mp3",
                    "mp3"
                )
            )


            # ------------------------------------------------
            # ★重要
            #
            # mp3ボタンと▲展開ボタンは必ずセット
            # ------------------------------------------------

            result["buttons"].append({

                "type":
                    "mp3",

                "label":
                    "mp3",

                "filename":
                    mp3_path.name,

                "path":
                    str(mp3_path),

                "has_expand":
                    True,

                "expand_label":
                    "▲",

                "expand_type":
                    "subtitle_srt"

            })


    # ======================================================
    # mp4
    # ======================================================

    elif radio_value == "mp4":

        mp4_path = None

        if known_files.get("mp4"):

            mp4_path = Path(
                known_files["mp4"]
            )

        else:

            filename = build_filename(
                title,
                ".mp4",
                start_time,
                end_time
            )

            mp4_path = find_file(
                download_dir,
                filename
            )


        if mp4_path:

            result["files"].append(
                make_file_info(
                    mp4_path,
                    "mp4",
                    "mp4"
                )
            )

            result["buttons"].append({

                "type":
                    "mp4",

                "label":
                    "mp4",

                "filename":
                    mp4_path.name,

                "path":
                    str(mp4_path)

            })


    # ======================================================
    # 字幕mp4
    #
    # ★ここだけ4種類
    #
    #   字幕mp4
    #   mp4
    #   mp3
    #   srt
    #
    # ======================================================

    elif radio_value == "subtitle_mp4":

        # --------------------------------------------------
        # 字幕MP4
        # --------------------------------------------------

        subtitle_mp4_path = None

        if known_files.get(
            "subtitle_mp4"
        ):

            subtitle_mp4_path = Path(
                known_files["subtitle_mp4"]
            )

        else:

            filename = (
                build_subtitle_mp4_filename(
                    title,
                    start_time,
                    end_time
                )
            )

            subtitle_mp4_path = find_file(
                download_dir,
                filename
            )


        if subtitle_mp4_path:

            result["files"].append(
                make_file_info(
                    subtitle_mp4_path,
                    "subtitle_mp4",
                    "字幕mp4"
                )
            )

            result["buttons"].append({

                "type":
                    "subtitle_mp4",

                "label":
                    "字幕mp4",

                "filename":
                    subtitle_mp4_path.name,

                "path":
                    str(subtitle_mp4_path)

            })


        # --------------------------------------------------
        # MP4
        # --------------------------------------------------

        mp4_path = None

        if known_files.get("mp4"):

            mp4_path = Path(
                known_files["mp4"]
            )

        else:

            filename = build_filename(
                title,
                ".mp4",
                start_time,
                end_time
            )

            mp4_path = find_file(
                download_dir,
                filename
            )


        if mp4_path:

            result["files"].append(
                make_file_info(
                    mp4_path,
                    "mp4",
                    "mp4"
                )
            )

            result["buttons"].append({

                "type":
                    "mp4",

                "label":
                    "mp4",

                "filename":
                    mp4_path.name,

                "path":
                    str(mp4_path)

            })


        # --------------------------------------------------
        # MP3
        # --------------------------------------------------

        mp3_path = None

        if known_files.get("mp3"):

            mp3_path = Path(
                known_files["mp3"]
            )

        else:

            filename = build_filename(
                title,
                ".mp3",
                start_time,
                end_time
            )

            mp3_path = find_file(
                download_dir,
                filename
            )


        if mp3_path:

            result["files"].append(
                make_file_info(
                    mp3_path,
                    "mp3",
                    "mp3"
                )
            )

            # ----------------------------------------------
            # ★mp3 + ▲ は必ずセット
            # ----------------------------------------------

            result["buttons"].append({

                "type":
                    "mp3",

                "label":
                    "mp3",

                "filename":
                    mp3_path.name,

                "path":
                    str(mp3_path),

                "has_expand":
                    True,

                "expand_label":
                    "▲",

                "expand_type":
                    "subtitle_srt"

            })


        # --------------------------------------------------
        # SRT
        #
        # ★SRTはリネームしない。
        #
        # known_files["srt"] があれば、それを最優先。
        # --------------------------------------------------

        srt_path = None

        if known_files.get("srt"):

            srt_path = Path(
                known_files["srt"]
            )

        else:

            filename = build_filename(
                title,
                ".srt",
                start_time,
                end_time
            )

            srt_path = find_file(
                download_dir,
                filename
            )


        if srt_path:

            result["files"].append(
                make_file_info(
                    srt_path,
                    "srt",
                    "srt"
                )
            )

            result["buttons"].append({

                "type":
                    "srt",

                "label":
                    "srt",

                "filename":
                    srt_path.name,

                "path":
                    str(srt_path),

                "gemini":
                    True

            })


    return result


# ==========================================================
# ==========================================================
# タブ2
# ==========================================================
#
# ★重要
#
# タブ2ではタブ1のラジオボタンを絶対に参照しない。
#
# tab2_mode:
#
#   "srt"
#
#       上側
#       SRTファイル
#
#
#   "subtitle_srt"
#
#       下側
#       字幕SRT
#
# ==========================================================

def get_tab2_files(
    title,
    tab2_mode,
    start_time=None,
    end_time=None,
    download_dir=None,
    known_files=None
):

    if download_dir is None:

        download_dir = (
            DEFAULT_DOWNLOAD_DIR
        )

    download_dir = Path(
        download_dir
    )

    known_files = (
        known_files
        or
        {}
    )

    result = {

        "tab":
            2,

        "mode":
            tab2_mode,

        "files":
            [],

        "buttons":
            []

    }


    # ======================================================
    # タブ2 上側
    #
    # SRT作成
    # ======================================================

    if tab2_mode == "srt":

        srt_path = None

        if known_files.get(
            "tab2_srt"
        ):

            srt_path = Path(
                known_files["tab2_srt"]
            )

        else:

            filename = build_filename(
                title,
                ".srt",
                start_time,
                end_time
            )

            srt_path = find_file(
                download_dir,
                filename
            )


        if srt_path:

            result["files"].append(
                make_file_info(
                    srt_path,
                    "tab2_srt",
                    "タブ2 SRT"
                )
            )

            result["buttons"].append({

                "type":
                    "tab2_srt",

                "label":
                    "タブ2 SRT",

                "filename":
                    srt_path.name,

                "path":
                    str(srt_path)

            })


    # ======================================================
    # タブ2 下側
    #
    # 字幕SRT作成
    # ======================================================

    elif tab2_mode == "subtitle_srt":

        subtitle_srt_path = None

        if known_files.get(
            "tab2_subtitle_srt"
        ):

            subtitle_srt_path = Path(
                known_files[
                    "tab2_subtitle_srt"
                ]
            )

        else:

            # ------------------------------------------------
            # タブ2字幕SRT専用ファイル名
            #
            # ★ここはタブ1ラジオボタンを使わない
            #
            # ------------------------------------------------

            filename = (
                build_filename(
                    title,
                    ".srt",
                    start_time,
                    end_time
                )
            )

            subtitle_srt_path = find_file(
                download_dir,
                filename
            )


        if subtitle_srt_path:

            result["files"].append(
                make_file_info(
                    subtitle_srt_path,
                    "tab2_subtitle_srt",
                    "タブ2 字幕SRT"
                )
            )

            result["buttons"].append({

                "type":
                    "tab2_subtitle_srt",

                "label":
                    "タブ2 字幕SRT",

                "filename":
                    subtitle_srt_path.name,

                "path":
                    str(subtitle_srt_path)

            })


    return result


# ==========================================================
# ==========================================================
# 統合判定
# ==========================================================
#
# フロント側は基本的にこの関数だけ呼べばよい。
#
# tab=1:
#
#   radio_value を使用
#
# tab=2:
#
#   tab2_mode を使用
#
# ★互いの判断は混ざらない。
#
# ==========================================================

def get_completed_files(
    tab,
    title,
    radio_value=None,
    tab2_mode=None,
    start_time=None,
    end_time=None,
    download_dir=None,
    known_files=None
):

    # ======================================================
    # タブ1
    # ======================================================

    if str(tab) == "1":

        return get_tab1_files(

            title=
                title,

            radio_value=
                radio_value,

            start_time=
                start_time,

            end_time=
                end_time,

            download_dir=
                download_dir,

            known_files=
                known_files

        )


    # ======================================================
    # タブ2
    # ======================================================

    if str(tab) == "2":

        return get_tab2_files(

            title=
                title,

            tab2_mode=
                tab2_mode,

            start_time=
                start_time,

            end_time=
                end_time,

            download_dir=
                download_dir,

            known_files=
                known_files

        )


    # ======================================================
    # 不正なタブ
    # ======================================================

    raise ValueError(
        f"不正なタブ番号です: {tab}"
    )


# ==========================================================
# Flask Route
#
# GET:
#
#   /completed-files
#
# 例:
#
#   /completed-files?tab=1
#       &title=テスト
#       &radio=subtitle_mp4
#
#
# タブ2:
#
#   /completed-files?tab=2
#       &title=テスト
#       &mode=srt
#
# ==========================================================

def register_completed_files(
    app
):

    @app.route(
        "/completed-files",
        methods=["GET"]
    )
    def completed_files():

        try:

            tab = request.args.get(
                "tab"
            )

            title = request.args.get(
                "title"
            )

            radio_value = request.args.get(
                "radio"
            )

            tab2_mode = request.args.get(
                "mode"
            )

            start_time = request.args.get(
                "start_time"
            )

            end_time = request.args.get(
                "end_time"
            )


            # ==================================================
            # 基本確認
            # ==================================================

            if not tab:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "tabが指定されていません。"

                }), 400


            if not title:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "titleが指定されていません。"

                }), 400


            # ==================================================
            # タブ1
            # ==================================================

            if str(tab) == "1":

                if radio_value not in (
                    "mp3",
                    "mp4",
                    "subtitle_mp4"
                ):

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "タブ1のラジオボタンが不正です。"

                    }), 400


                data = get_completed_files(

                    tab=
                        1,

                    title=
                        title,

                    radio_value=
                        radio_value,

                    start_time=
                        start_time,

                    end_time=
                        end_time

                )


            # ==================================================
            # タブ2
            # ==================================================

            elif str(tab) == "2":

                if tab2_mode not in (
                    "srt",
                    "subtitle_srt"
                ):

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "タブ2の処理区分が不正です。"

                    }), 400


                # ------------------------------------------------
                # ★ここではradio_valueを使用しない。
                # ------------------------------------------------

                data = get_completed_files(

                    tab=
                        2,

                    title=
                        title,

                    tab2_mode=
                        tab2_mode,

                    start_time=
                        start_time,

                    end_time=
                        end_time

                )


            else:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "tabは1または2を指定してください。"

                }), 400


            return jsonify({

                "success":
                    True,

                "data":
                    data

            })


        except Exception as error:

            print(
                "[COMPLETED_FILES] ERROR:",
                repr(error),
                flush=True
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(error)

            }), 500


# ==========================================================
# 単独テスト
# ==========================================================

if __name__ == "__main__":

    # ------------------------------------------------------
    # 例:
    #
    # タブ1 字幕MP4
    # ------------------------------------------------------

    result = get_completed_files(

        tab=1,

        title="テスト動画",

        radio_value="subtitle_mp4",

        start_time="00:06:00",

        end_time="00:06:30"

    )

    print()
    print(
        "=========================================="
    )
    print(
        "TAB 1"
    )
    print(
        "=========================================="
    )
    print(
        result
    )
    print()


    # ------------------------------------------------------
    # タブ2 上側 SRT
    # ------------------------------------------------------

    result = get_completed_files(

        tab=2,

        title="テスト動画",

        tab2_mode="srt",

        start_time="00:00:00",

        end_time="00:00:00"

    )

    print()
    print(
        "=========================================="
    )
    print(
        "TAB 2 SRT"
    )
    print(
        "=========================================="
    )
    print(
        result
    )
    print()


    # ------------------------------------------------------
    # タブ2 下側 字幕SRT
    # ------------------------------------------------------

    result = get_completed_files(

        tab=2,

        title="テスト動画",

        tab2_mode="subtitle_srt",

        start_time="00:06:00",

        end_time="00:06:30"

    )

    print()
    print(
        "=========================================="
    )
    print(
        "TAB 2 SUBTITLE SRT"
    )
    print(
        "=========================================="
    )
    print(
        result
    )
    print()
