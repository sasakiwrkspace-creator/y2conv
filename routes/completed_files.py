# =====================================
# completed_files.py
#
# 完了ファイル判定
#
# 役割:
# ・タブ1 / タブ2を完全に分離
# ・タイトルを基準に完成ファイルを検索
# ・時間指定6桁をファイル名判定に使用
# ・00:00:00 ～ 00:00:00 の場合は数字なし
# ・存在するファイルだけを返す
# ・MP3は「MP3本体 + Gemini SRT作成ボタン」の
#   1セットとして扱う
#
# タブ1:
#   MP3
#   MP4
#   SRT
#   字幕MP4
#
# タブ2:
#   SRT
#   字幕SRT
#
# 注意:
# ・タブ1のラジオボタン情報をタブ2では使用しない
# ・タブ2の判定にタブ1のoutput-formatを混ぜない
# =====================================

from __future__ import annotations

from pathlib import Path
from typing import Any
import re


# =====================================
# 設定
# =====================================

# completed_files.py から見た
# 完成ファイル保存ディレクトリ。
#
# 必要に応じて既存プロジェクトの
# 保存先に変更してください。
#
# 環境変数などで変更できる構成にする場合は
# ここを差し替えます。
# =====================================

BASE_DIR = Path(__file__).resolve().parent

DOWNLOAD_DIR = BASE_DIR / "downloads"


# =====================================
# 共通
# =====================================

def normalize_title(title: str) -> str:
    """
    タイトルをファイル名検索用に正規化する。

    実際のファイル名を壊さないため、
    ここでは前後空白の除去を中心に行う。
    """

    if title is None:
        return ""

    return str(title).strip()


def normalize_time(value: Any) -> int:
    """
    時間を秒に変換する。

    None / 空文字 / 不正値
    → 0
    """

    if value is None:
        return 0

    if isinstance(value, bool):
        return 0

    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return 0


def make_time_suffix(
    start_time: Any = 0,
    end_time: Any = 0,
) -> str:
    """
    時間指定用6桁文字列を作る。

    00:00:00 ～ 00:00:00
        → ""

    01:02:03 ～ 04:05:06
        → "_010203_040506"

    秒数を HHMMSS に変換する。
    """

    start = normalize_time(start_time)
    end = normalize_time(end_time)

    # ---------------------------------
    # 両方00:00:00の場合
    # 数字なし
    # ---------------------------------

    if start == 0 and end == 0:
        return ""

    return (
        "_"
        + seconds_to_hhmmss(start)
        + "_"
        + seconds_to_hhmmss(end)
    )


def seconds_to_hhmmss(seconds: int) -> str:
    """
    秒数を6桁 HHMMSS にする。

    例:
        0     → 000000
        3661  → 010101
        5430  → 013030
    """

    seconds = max(0, int(seconds))

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return (
        f"{hours:02d}"
        f"{minutes:02d}"
        f"{secs:02d}"
    )


def build_base_name(
    title: str,
    start_time: Any = 0,
    end_time: Any = 0,
) -> str:
    """
    タイトル + 時間指定から
    共通ファイル名部分を作る。

    例:

    タイトル:
        sample

    時間なし:
        sample

    時間あり:
        sample_013045_021530
    """

    title = normalize_title(title)

    if not title:
        return ""

    suffix = make_time_suffix(
        start_time,
        end_time,
    )

    return title + suffix


# =====================================
# ファイル名安全処理
# =====================================

def is_safe_filename(filename: str) -> bool:
    """
    filenameが保存ディレクトリ外を
    指せないことを確認する。

    ファイル名検索では基本的にbasenameのみ
    使用する。
    """

    if not filename:
        return False

    filename = str(filename)

    if "/" in filename:
        return False

    if "\\" in filename:
        return False

    if filename in (".", ".."):
        return False

    return True


# =====================================
# ファイル検索
# =====================================

def find_exact_file(
    directory: Path,
    filename: str,
) -> Path | None:
    """
    完全一致でファイルを検索する。
    """

    if not filename:
        return None

    if not is_safe_filename(filename):
        return None

    path = directory / filename

    if path.is_file():
        return path

    return None


def find_by_base_name(
    directory: Path,
    base_name: str,
    extensions: list[str],
) -> Path | None:
    """
    base_name + 拡張子で検索する。

    例:
        sample_010203_020304.mp3
    """

    if not base_name:
        return None

    for extension in extensions:

        if not extension.startswith("."):
            extension = "." + extension

        filename = (
            base_name +
            extension
        )

        path = find_exact_file(
            directory,
            filename,
        )

        if path:
            return path

    return None


# =====================================
# ファイル情報
# =====================================

def file_info(
    path: Path | None,
) -> dict[str, Any]:
    """
    フロントエンドへ返すファイル情報。
    """

    if path is None:
        return {
            "exists": False,
            "filename": "",
        }

    return {
        "exists": True,
        "filename": path.name,
    }


# =====================================
# タブ1
# =====================================

def find_tab1_files(
    title: str,
    start_time: Any = 0,
    end_time: Any = 0,
    selected_outputs: list[str] | None = None,
) -> dict[str, Any]:
    """
    タブ1の完成ファイルを判定する。

    selected_outputs:
        タブ1のラジオボタン選択状態。

    重要:
        この値はタブ1だけで使用する。

    タブ2の判定には絶対に渡さない。
    """

    base_name = build_base_name(
        title,
        start_time,
        end_time,
    )

    if not base_name:
        return {
            "tab": 1,
            "title": normalize_title(title),
            "time_suffix": "",
            "files": {},
        }

    selected = {
        str(value).lower()
        for value in (
            selected_outputs or []
        )
    }

    result = {
        "tab": 1,
        "title": normalize_title(title),
        "time_suffix": make_time_suffix(
            start_time,
            end_time,
        ),
        "files": {},
    }

    # ---------------------------------
    # MP3
    #
    # MP3が存在した場合、
    # MP3ボタン + Gemini SRTボタン
    # を表示できるようにする。
    # ---------------------------------

    if (
        not selected
        or "mp3" in selected
    ):

        mp3 = find_by_base_name(
            DOWNLOAD_DIR,
            base_name,
            [".mp3"],
        )

        result["files"]["mp3"] = \
            file_info(mp3)

        if mp3:
            result["files"]["mp3"][
                "show_gemini_srt"
            ] = True
        else:
            result["files"]["mp3"][
                "show_gemini_srt"
            ] = False

    # ---------------------------------
    # MP4
    # ---------------------------------

    if (
        not selected
        or "mp4" in selected
    ):

        mp4 = find_by_base_name(
            DOWNLOAD_DIR,
            base_name,
            [".mp4"],
        )

        result["files"]["mp4"] = \
            file_info(mp4)

    # ---------------------------------
    # 字幕MP4
    # ---------------------------------

    if (
        not selected
        or "subtitle_mp4" in selected
    ):

        subtitle_mp4 = find_by_base_name(
            DOWNLOAD_DIR,
            base_name,
            [
                "_subtitle.mp4",
            ],
        )

        # ---------------------------------
        # 上記形式で見つからない場合、
        # subtitle_mp4を含む候補も確認する。
        # ---------------------------------

        if subtitle_mp4 is None:

            subtitle_mp4 = find_subtitle_mp4(
                DOWNLOAD_DIR,
                base_name,
            )

        result["files"]["subtitle_mp4"] = \
            file_info(subtitle_mp4)

    # ---------------------------------
    # SRT
    #
    # タブ1のGemini SRT。
    # ---------------------------------

    if (
        not selected
        or "srt" in selected
        or "mp3" in selected
    ):

        srt = find_by_base_name(
            DOWNLOAD_DIR,
            base_name,
            [".srt"],
        )

        result["files"]["srt"] = \
            file_info(srt)

    return result


# =====================================
# 字幕MP4検索
# =====================================

def find_subtitle_mp4(
    directory: Path,
    base_name: str,
) -> Path | None:
    """
    字幕MP4を検索する。

    想定候補:

        title_subtitle.mp4
        title_subtitle_mp4.mp4

    実際のsubtitle_mp4.pyの命名規則に
    合わせてここを一本化できます。
    """

    candidates = [
        f"{base_name}_subtitle.mp4",
        f"{base_name}_subtitle_mp4.mp4",
    ]

    for filename in candidates:

        path = find_exact_file(
            directory,
            filename,
        )

        if path:
            return path

    return None


# =====================================
# タブ2
# =====================================

def find_tab2_files(
    title: str,
    start_time: Any = 0,
    end_time: Any = 0,
) -> dict[str, Any]:
    """
    タブ2の完成ファイルを判定する。

    重要:

    ・タブ1のselected_outputsを受け取らない
    ・タブ1のラジオボタンを見ない
    ・タブ1のoutput-formatに影響されない

    タブ2は、

        上側 → SRT
        下側 → 字幕SRT

    として独立して判定する。
    """

    base_name = build_base_name(
        title,
        start_time,
        end_time,
    )

    result = {
        "tab": 2,
        "title": normalize_title(title),
        "time_suffix": make_time_suffix(
            start_time,
            end_time,
        ),
        "files": {},
    }

    if not base_name:
        return result

    # ---------------------------------
    # タブ2 上側
    # SRT
    # ---------------------------------

    srt = find_tab2_srt(
        DOWNLOAD_DIR,
        base_name,
    )

    result["files"]["srt"] = \
        file_info(srt)

    # ---------------------------------
    # タブ2 下側
    # 字幕SRT
    # ---------------------------------

    subtitle_srt = find_tab2_subtitle_srt(
        DOWNLOAD_DIR,
        base_name,
    )

    result["files"]["subtitle_srt"] = \
        file_info(subtitle_srt)

    return result


# =====================================
# タブ2 SRT
# =====================================

def find_tab2_srt(
    directory: Path,
    base_name: str,
) -> Path | None:
    """
    タブ2上側のSRTを検索する。

    タブ1のSRTとは別の命名規則を
    想定できるよう関数を分離している。
    """

    candidates = [
        f"{base_name}_tab2.srt",
        f"{base_name}_srt.srt",
    ]

    for filename in candidates:

        path = find_exact_file(
            directory,
            filename,
        )

        if path:
            return path

    return None


# =====================================
# タブ2 字幕SRT
# =====================================

def find_tab2_subtitle_srt(
    directory: Path,
    base_name: str,
) -> Path | None:
    """
    タブ2下側の字幕SRTを検索する。
    """

    candidates = [
        f"{base_name}_subtitle.srt",
        f"{base_name}_subtitle_srt.srt",
    ]

    for filename in candidates:

        path = find_exact_file(
            directory,
            filename,
        )

        if path:
            return path

    return None


# =====================================
# 完了ファイル統合
# =====================================

def get_completed_files(
    tab1_title: str = "",
    tab1_start_time: Any = 0,
    tab1_end_time: Any = 0,
    tab1_outputs: list[str] | None = None,

    tab2_title: str = "",
    tab2_start_time: Any = 0,
    tab2_end_time: Any = 0,
) -> dict[str, Any]:
    """
    タブ1 + タブ2の完成ファイルを取得する。

    ここでも重要なのは、

        tab1_outputs
            ↓
        タブ1だけ

    という完全分離。
    """

    tab1 = find_tab1_files(
        title=tab1_title,
        start_time=tab1_start_time,
        end_time=tab1_end_time,
        selected_outputs=tab1_outputs,
    )

    tab2 = find_tab2_files(
        title=tab2_title,
        start_time=tab2_start_time,
        end_time=tab2_end_time,
    )

    return {
        "success": True,

        "tab1": tab1,

        "tab2": tab2,
    }


# =====================================
# ダウンロード表示用
# =====================================

def make_download_display(
    completed: dict[str, Any],
) -> dict[str, Any]:
    """
    フロントエンドがそのまま
    ダウンロードエリアを作れる形式にする。

    表示順:

        [字幕mp4]
        [mp4]
        [mp3] ▲Geminiへ(字幕srt)
        [srt]

    ただし、存在するものだけ。
    """

    display = []

    tab1 = (
        completed.get("tab1", {})
        .get("files", {})
    )

    tab2 = (
        completed.get("tab2", {})
        .get("files", {})
    )

    # ---------------------------------
    # タブ1 字幕MP4
    # ---------------------------------

    subtitle_mp4 = tab1.get(
        "subtitle_mp4",
        {},
    )

    if subtitle_mp4.get("exists"):

        display.append({
            "tab": 1,
            "type": "subtitle_mp4",
            "filename":
                subtitle_mp4["filename"],
            "label": "[字幕mp4]",
        })

    # ---------------------------------
    # タブ1 MP4
    # ---------------------------------

    mp4 = tab1.get(
        "mp4",
        {},
    )

    if mp4.get("exists"):

        display.append({
            "tab": 1,
            "type": "mp4",
            "filename":
                mp4["filename"],
            "label": "[mp4]",
        })

    # ---------------------------------
    # タブ1 MP3
    #
    # MP3本体とGeminiボタンは
    # 必ずセット。
    # ---------------------------------

    mp3 = tab1.get(
        "mp3",
        {},
    )

    if mp3.get("exists"):

        display.append({
            "tab": 1,
            "type": "mp3_group",
            "filename":
                mp3["filename"],
            "label": "[mp3]",
            "show_gemini_srt": True,
            "gemini_label":
                "▲geminiへ(字幕srt)",
        })

    # ---------------------------------
    # タブ1 SRT
    # ---------------------------------

    srt = tab1.get(
        "srt",
        {},
    )

    if srt.get("exists"):

        display.append({
            "tab": 1,
            "type": "srt",
            "filename":
                srt["filename"],
            "label": "[srt]",
        })

    # ---------------------------------
    # タブ2 SRT
    #
    # タブ1とは完全に別。
    # ---------------------------------

    tab2_srt = tab2.get(
        "srt",
        {},
    )

    if tab2_srt.get("exists"):

        display.append({
            "tab": 2,
            "type": "tab2_srt",
            "filename":
                tab2_srt["filename"],
            "label": "[タブ2 srt]",
        })

    # ---------------------------------
    # タブ2 字幕SRT
    # ---------------------------------

    tab2_subtitle_srt = tab2.get(
        "subtitle_srt",
        {},
    )

    if tab2_subtitle_srt.get("exists"):

        display.append({
            "tab": 2,
            "type": "tab2_subtitle_srt",
            "filename":
                tab2_subtitle_srt["filename"],
            "label": "[タブ2 字幕srt]",
        })

    return {
        "success": True,
        "items": display,
    }


# =====================================
# 一括処理
# =====================================

def check_completed_files(
    tab1_title: str = "",
    tab1_start_time: Any = 0,
    tab1_end_time: Any = 0,
    tab1_outputs: list[str] | None = None,

    tab2_title: str = "",
    tab2_start_time: Any = 0,
    tab2_end_time: Any = 0,
) -> dict[str, Any]:
    """
    外部から呼び出すメイン関数。

    1.
        完成ファイルを確認

    2.
        ダウンロード表示情報を作成

    3.
        JSON化しやすい辞書を返す。
    """

    completed = get_completed_files(

        tab1_title=tab1_title,

        tab1_start_time=tab1_start_time,

        tab1_end_time=tab1_end_time,

        tab1_outputs=tab1_outputs,

        tab2_title=tab2_title,

        tab2_start_time=tab2_start_time,

        tab2_end_time=tab2_end_time,

    )

    display = make_download_display(
        completed
    )

    return {
        "success": True,

        "completed": completed,

        "download_display": display[
            "items"
        ],
    }


# =====================================
# テスト
# =====================================

if __name__ == "__main__":

    result = check_completed_files(

        # -----------------------------
        # タブ1
        # -----------------------------

        tab1_title="テスト動画",

        tab1_start_time=0,

        tab1_end_time=0,

        tab1_outputs=[
            "mp3",
            "mp4",
            "subtitle_mp4",
        ],

        # -----------------------------
        # タブ2
        # -----------------------------

        tab2_title="テスト動画",

        tab2_start_time=0,

        tab2_end_time=0,

    )

    import json

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )
