# ==========================================================
# Subtitle - Low Memory Edition
# subtitle.py
#
# MP4動画へSRT字幕を焼き込む
#
# ==========================================================
#
# 字幕設定の唯一の情報源:
#   subtitle_font.py
#
# 3ファイル共通の正式設定名:
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# ==========================================================

import os
import sys
import time
import shutil
import subprocess
import traceback

from pathlib import Path
from collections import deque

from config import DOWNLOAD_DIR

from subtitle_font import (
    SUBTITLE_COLORS,
    get_default_subtitle_font_settings,
)


# ==========================================================
# 設定
# ==========================================================

DOWNLOADS_DIR = Path(
    DOWNLOAD_DIR
)

MAX_FFMPEG_LOG_LINES = 100

FFMPEG_THREADS = "1"

FFMPEG_PRESET = "ultrafast"

FFMPEG_CRF = "23"


# ==========================================================
# 共通設定キー
# ==========================================================

SUBTITLE_SETTING_KEYS = (
    "preset_name",
    "font",
    "text_color",
    "outline_color",
    "outline_width",
)


# ==========================================================
# モジュール読み込みログ
# ==========================================================

print(
    "[SUBTITLE] ==========================================",
    flush=True
)

print(
    "[SUBTITLE] subtitle.py MODULE LOAD START",
    flush=True
)

try:
    print(
        f"[SUBTITLE] subtitle.py __file__: "
        f"{Path(__file__).resolve()}",
        flush=True
    )
except Exception as error:
    print(
        f"[SUBTITLE] __file__取得失敗: {error}",
        flush=True
    )

print(
    f"[SUBTITLE] Python executable: {sys.executable}",
    flush=True
)

print(
    f"[SUBTITLE] Python version: {sys.version}",
    flush=True
)

try:
    print(
        f"[SUBTITLE] Current working directory: "
        f"{os.getcwd()}",
        flush=True
    )
except Exception as error:
    print(
        f"[SUBTITLE] cwd取得失敗: {error}",
        flush=True
    )

print(
    f"[SUBTITLE] DOWNLOAD_DIR: {DOWNLOAD_DIR}",
    flush=True
)

print(
    f"[SUBTITLE] DOWNLOADS_DIR: {DOWNLOADS_DIR}",
    flush=True
)

print(
    f"[SUBTITLE] SUBTITLE_FONT environment: "
    f"{os.environ.get('SUBTITLE_FONT')!r}",
    flush=True
)

print(
    "[SUBTITLE] subtitle.py MODULE LOAD COMPLETE",
    flush=True
)

print(
    "[SUBTITLE] ==========================================",
    flush=True
)


# ==========================================================
# ログ
# ==========================================================

def log(message):
    """
    Renderログへ字幕処理ログを出力。
    """

    try:
        print(
            "[SUBTITLE]",
            message,
            flush=True
        )
    except Exception:
        pass


def log_separator():
    log(
        "=========================================="
    )


def log_start(message):
    log_separator()
    log(message)
    log_separator()


def log_exception(message, error):
    """
    例外メッセージと完全なtracebackをRenderログへ出す。
    """

    log(
        message
    )

    try:
        log(
            f"TYPE: {type(error).__name__}"
        )

        log(
            f"ERROR: {error}"
        )

        log(
            "TRACEBACK START"
        )

        traceback_text = traceback.format_exc()

        if traceback_text:
            print(
                "[SUBTITLE] " + traceback_text,
                flush=True
            )

        log(
            "TRACEBACK END"
        )

    except Exception as traceback_error:

        log(
            f"traceback取得失敗: {traceback_error}"
        )


# ==========================================================
# 処理時間
# ==========================================================

def format_elapsed_time(seconds):

    try:
        seconds = int(
            round(
                float(seconds)
            )
        )

    except (
        ValueError,
        TypeError
    ):

        seconds = 0

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = (
        seconds % 60
    )

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ==========================================================
# 入力ファイル確認
# ==========================================================

def validate_input_file(
    file_path,
    extension
):

    log_start(
        "入力ファイル確認開始"
    )

    log(
        f"file_path argument: {file_path!r}"
    )

    log(
        f"expected extension: {extension}"
    )

    try:

        path = Path(
            file_path
        ).resolve()

    except Exception as error:

        log_exception(
            "Path生成に失敗しました。",
            error
        )

        raise

    log(
        f"resolved path: {path}"
    )

    if not path.exists():

        log(
            f"ERROR: ファイルが存在しません: {path}"
        )

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    log(
        "ファイル存在確認: OK"
    )

    if not path.is_file():

        log(
            f"ERROR: ファイルではありません: {path}"
        )

        raise ValueError(
            f"ファイルではありません: {path}"
        )

    log(
        "ファイル形式確認: OK"
    )

    actual_suffix = path.suffix.lower()

    log(
        f"actual extension: {actual_suffix}"
    )

    if actual_suffix != extension.lower():

        log(
            f"ERROR: 拡張子不一致: {actual_suffix}"
        )

        raise ValueError(
            f"{extension} ファイルではありません: {path}"
        )

    try:

        size = path.stat().st_size

    except OSError as error:

        log_exception(
            "ファイルサイズ取得に失敗しました。",
            error
        )

        raise RuntimeError(
            f"ファイルサイズを確認できません: {error}"
        ) from error

    log(
        f"file size: {size} bytes"
    )

    if size <= 0:

        log(
            "ERROR: ファイルサイズが0 bytesです。"
        )

        raise ValueError(
            f"ファイルが0 bytesです: {path}"
        )

    log(
        "入力ファイル確認完了"
    )

    return path


# ==========================================================
# 出力ファイル名
# ==========================================================

def make_output_path(
    mp4_path
):

    log_start(
        "出力ファイル名生成開始"
    )

    mp4_path = Path(
        mp4_path
    ).resolve()

    stem = mp4_path.stem

    base_suffix = "_sub_embed"

    if stem.lower().endswith(
        base_suffix
    ):

        candidate = (
            mp4_path.parent
            /
            f"{stem}_2.mp4"
        )

    else:

        candidate = (
            mp4_path.parent
            /
            f"{stem}{base_suffix}.mp4"
        )

    counter = 2

    while candidate.exists():

        log(
            f"出力候補が既に存在: {candidate}"
        )

        candidate = (
            mp4_path.parent
            /
            f"{stem}_{counter}.mp4"
        )

        counter += 1

    log(
        f"決定出力パス: {candidate}"
    )

    return candidate


# ==========================================================
# 一時出力パス
# ==========================================================

def make_temp_output_path(
    output_path
):

    output_path = Path(
        output_path
    ).resolve()

    timestamp = time.time_ns()

    temp_path = (
        output_path.parent
        /
        (
            "."
            +
            output_path.stem
            +
            f".subtitle_{timestamp}.tmp.mp4"
        )
    )

    log(
        f"一時出力パス生成: {temp_path}"
    )

    return temp_path


# ==========================================================
# FFmpeg存在確認
# ==========================================================

def check_ffmpeg():

    log_start(
        "FFmpeg確認開始"
    )

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    log(
        f"shutil.which(ffmpeg): {ffmpeg_path}"
    )

    if not ffmpeg_path:

        raise RuntimeError(
            "FFmpegが見つかりません。"
            "Render側にFFmpegをインストールしてください。"
        )

    log(
        f"FFmpeg path: {ffmpeg_path}"
    )

    try:

        result = subprocess.run(

            [
                ffmpeg_path,
                "-version"
            ],

            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",
            errors="replace",

            timeout=30
        )

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpegが見つかりません。"
        )

    except subprocess.TimeoutExpired:

        raise RuntimeError(
            "FFmpegの確認がタイムアウトしました。"
        )

    except OSError as error:

        raise RuntimeError(
            f"FFmpegを起動できません: {error}"
        ) from error

    log(
        f"FFmpeg version returncode: "
        f"{result.returncode}"
    )

    if result.returncode != 0:

        log(
            "FFmpeg version stderr:"
        )

        log(
            result.stderr[-2000:]
        )

        raise RuntimeError(
            "FFmpegを実行できませんでした。"
        )

    first_line = (

        result.stdout.splitlines()[0]

        if result.stdout

        else "FFmpeg"

    )

    log(
        f"FFmpeg version: {first_line}"
    )

    log(
        "FFmpeg確認完了"
    )

    return ffmpeg_path


# ==========================================================
# SRT UTF-8確認
# ==========================================================

def validate_srt_encoding(
    srt_path
):

    log_start(
        "SRT UTF-8確認開始"
    )

    srt_path = Path(
        srt_path
    )

    log(
        f"SRT path: {srt_path}"
    )

    try:

        with open(

            srt_path,

            "r",

            encoding="utf-8-sig"

        ) as file:

            first_content = file.read(
                4096
            )

    except UnicodeDecodeError as error:

        log_exception(
            "SRT UTF-8 decode error",
            error
        )

        raise RuntimeError(

            "SRTファイルをUTF-8として"
            "読み込めませんでした。"
            "SRTをUTF-8形式で保存してください。"

        ) from error

    except OSError as error:

        log_exception(
            "SRT read error",
            error
        )

        raise RuntimeError(

            f"SRTファイルを読み込めませんでした: {error}"

        ) from error

    if not first_content.strip():

        log(
            "ERROR: SRTが空です。"
        )

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    try:

        srt_size = (
            srt_path.stat().st_size
        )

    except OSError:

        srt_size = 0

    log(
        f"SRTサイズ: {srt_size} bytes"
    )

    log(
        f"SRT先頭文字数: {len(first_content)}"
    )

    log(
        "SRT UTF-8確認完了"
    )

    return True


# ==========================================================
# フォントfamily取得
# ==========================================================

def get_font_family_from_path(
    font_path
):

    log(
        "フォントfamily取得開始"
    )

    log(
        f"font_path: {font_path}"
    )

    fc_scan = shutil.which(
        "fc-scan"
    )

    log(
        f"fc-scan: {fc_scan}"
    )

    if not fc_scan:

        log(
            "fc-scanがありません。"
        )

        return None

    try:

        result = subprocess.run(

            [
                fc_scan,
                "--format=%{family}\n",
                str(font_path)
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=30
        )

    except Exception as error:

        log_exception(
            "fc-scanエラー",
            error
        )

        return None

    log(
        f"fc-scan returncode: "
        f"{result.returncode}"
    )

    if result.returncode != 0:

        log(
            f"fc-scan stderr: "
            f"{result.stderr[-1000:]}"
        )

        return None

    families = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        if line not in families:
            families.append(
                line
            )

    if not families:

        log(
            "font familyが取得できませんでした。"
        )

        return None

    family = families[0]

    if "," in family:

        family = (
            family.split(
                ",",
                1
            )[0].strip()
        )

    log(
        f"検出family: {family}"
    )

    return family or None


# ==========================================================
# fc-match
# ==========================================================

def fc_match_font(
    requested_font
):

    log(
        "fc-match開始"
    )

    log(
        f"requested_font: {requested_font}"
    )

    if not requested_font:

        log(
            "requested_fontが空です。"
        )

        return None

    fc_match = shutil.which(
        "fc-match"
    )

    log(
        f"fc-match: {fc_match}"
    )

    if not fc_match:

        log(
            "fc-matchがありません。"
        )

        return None

    try:

        result = subprocess.run(

            [
                fc_match,

                "-f",
                "%{file}\n",

                str(
                    requested_font
                )
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=30
        )

    except Exception as error:

        log_exception(
            "fc-matchエラー",
            error
        )

        return None

    log(
        f"fc-match returncode: "
        f"{result.returncode}"
    )

    if result.returncode != 0:

        log(
            f"fc-match stderr: "
            f"{result.stderr[-1000:]}"
        )

        return None

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        font_path = Path(
            line
        )

        log(
            f"fc-match result path: {font_path}"
        )

        if not font_path.is_file():

            log(
                "fc-matchの結果が実ファイルではありません。"
            )

            continue

        family = (
            get_font_family_from_path(
                font_path
            )
        )

        result_data = {

            "path":
                font_path.resolve(),

            "family":
                family

        }

        log(
            f"fc-match selected: {result_data}"
        )

        return result_data

    log(
        "fc-matchでフォントを検出できませんでした。"
    )

    return None


# ==========================================================
# 日本語フォント検索
# ==========================================================

def find_japanese_font(
    requested_font=None
):

    log_start(
        "日本語フォント検索開始"
    )

    log(
        f"requested_font: {requested_font}"
    )

    # ======================================================
    # 1. SUBTITLE_FONT
    # ======================================================

    environment_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    log(
        f"SUBTITLE_FONT: {environment_font}"
    )

    if environment_font:

        environment_font_path = (
            Path(
                environment_font
            ).expanduser().resolve()
        )

        log(
            f"SUBTITLE_FONT resolved: "
            f"{environment_font_path}"
        )

        if environment_font_path.is_file():

            family = (
                get_font_family_from_path(
                    environment_font_path
                )
            )

            log(
                "環境変数指定フォントを使用"
            )

            log(
                f"path: {environment_font_path}"
            )

            log(
                f"family: {family}"
            )

            return {

                "path":
                    environment_font_path,

                "family":
                    family

            }

        log(
            "SUBTITLE_FONT指定フォントが存在しません。"
        )

    # ======================================================
    # 2. subtitle_font.py指定
    # ======================================================

    if requested_font:

        requested_font = str(
            requested_font
        ).strip()

        log(
            f"requested font normalized: "
            f"{requested_font}"
        )

        requested_path = (
            Path(
                requested_font
            ).expanduser()
        )

        if requested_path.is_file():

            requested_path = (
                requested_path.resolve()
            )

            family = (
                get_font_family_from_path(
                    requested_path
                )
            )

            log(
                "指定フォントファイルを使用:"
            )

            log(
                f"path: {requested_path}"
            )

            log(
                f"family: {family}"
            )

            return {

                "path":
                    requested_path,

                "family":
                    family

            }

        log(
            "指定フォントはファイルパスではありません。"
        )

        matched = fc_match_font(
            requested_font
        )

        if matched:

            log(
                "指定フォントをfc-matchで検出しました。"
            )

            return matched

        log(
            "指定フォントをfc-matchで検出できませんでした。"
        )

    # ======================================================
    # 3. 日本語フォント候補
    # ======================================================

    candidates = [

        "Noto Sans CJK JP",

        "Noto Sans JP",

        "Noto Serif CJK JP",

        "Noto Serif JP",

        "IPAexGothic",

        "IPAGothic",

        "IPAexMincho",

        "IPAMincho",

        "VL Gothic",

        "TakaoGothic",

    ]

    log(
        f"日本語フォント候補数: {len(candidates)}"
    )

    for family_name in candidates:

        log(
            f"候補検索: {family_name}"
        )

        matched = fc_match_font(
            family_name
        )

        if not matched:
            continue

        log(
            "日本語フォント検出:"
        )

        log(
            f"requested family: {family_name}"
        )

        log(
            f"actual family: {matched.get('family')}"
        )

        log(
            f"path: {matched.get('path')}"
        )

        return matched

    # ======================================================
    # 4. fc-list
    # ======================================================

    fc_list = shutil.which(
        "fc-list"
    )

    log(
        f"fc-list: {fc_list}"
    )

    if fc_list:

        try:

            result = subprocess.run(

                [
                    fc_list,

                    ":lang=ja",

                    "-f",

                    "%{file}|%{family}\n"

                ],

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                text=True,

                encoding="utf-8",

                errors="replace",

                timeout=30
            )

        except Exception as error:

            log_exception(
                "fc-list検索エラー",
                error
            )

            result = None

        if result and result.returncode == 0:

            for line in result.stdout.splitlines():

                line = line.strip()

                if not line:
                    continue

                parts = line.split(
                    "|",
                    1
                )

                font_file = (
                    parts[0].strip()
                )

                family = (

                    parts[1].strip()

                    if len(parts) > 1

                    else ""

                )

                if not font_file:
                    continue

                font_path = Path(
                    font_file
                )

                if not font_path.is_file():
                    continue

                if "," in family:

                    family = (
                        family.split(
                            ",",
                            1
                        )[0].strip()
                    )

                log(
                    "fc-list日本語フォント検出:"
                )

                log(
                    f"path: {font_path}"
                )

                log(
                    f"family: {family}"
                )

                return {

                    "path":
                        font_path.resolve(),

                    "family":
                        family

                }

    # ======================================================
    # 5. 手動検索
    # ======================================================

    preferred_fonts = [

        "NotoSansCJK-Regular.ttc",

        "NotoSansCJKJP-Regular.otf",

        "NotoSansJP-Regular.ttf",

        "NotoSerifCJK-Regular.ttc",

        "NotoSerifCJKJP-Regular.otf",

        "NotoSerifJP-Regular.ttf",

        "ipaexg.ttf",

        "ipaexm.ttf",

        "IPAGothic.ttf",

        "IPAPGothic.ttf",

        "IPAMincho.ttf",

        "IPAPMincho.ttf",

        "TakaoGothic.ttf",

        "TakaoPGothic.ttf",

        "TakaoMincho.ttf",

        "VL-Gothic-Regular.ttf",

    ]

    font_directories = [

        Path(
            "/usr/share/fonts"
        ),

        Path(
            "/usr/local/share/fonts"
        ),

        Path(
            "/opt/render/project/src/fonts"
        ),

        Path(
            "/app/fonts"
        ),

        Path(
            "fonts"
        ).resolve(),

    ]

    log(
        f"手動フォント検索ディレクトリ数: "
        f"{len(font_directories)}"
    )

    for directory in font_directories:

        log(
            f"フォントディレクトリ確認: {directory}"
        )

        if not directory.exists():

            log(
                "ディレクトリが存在しません。"
            )

            continue

        for font_name in preferred_fonts:

            try:

                for match in directory.rglob(
                    font_name
                ):

                    if not match.is_file():
                        continue

                    family = (
                        get_font_family_from_path(
                            match
                        )
                    )

                    log(
                        "日本語フォント検出:"
                    )

                    log(
                        f"path: {match}"
                    )

                    log(
                        f"family: {family}"
                    )

                    return {

                        "path":
                            match.resolve(),

                        "family":
                            family

                    }

            except Exception as error:

                log_exception(
                    f"フォント検索エラー: {directory}",
                    error
                )

                continue

    log(
        "日本語フォントが見つかりませんでした。"
    )

    return None


# ==========================================================
# FFmpegフィルターパスエスケープ
# ==========================================================

def escape_ffmpeg_filter_path(
    file_path
):

    log(
        "FFmpeg filter path escape開始"
    )

    path = str(
        Path(
            file_path
        ).resolve()
    )

    path = path.replace(
        "\\",
        "/"
    )

    path = path.replace(
        "'",
        "\\'"
    )

    path = path.replace(
        ":",
        "\\:"
    )

    path = path.replace(
        ";",
        "\\;"
    )

    path = path.replace(
        "\n",
        "\\n"
    )

    log(
        f"escaped path: {path}"
    )

    return path


# ==========================================================
# FFmpeg force_style値エスケープ
# ==========================================================

def escape_ffmpeg_value(
    value
):

    value = str(
        value
    )

    value = value.replace(
        "\\",
        "\\\\"
    )

    value = value.replace(
        "'",
        "\\'"
    )

    value = value.replace(
        ":",
        "\\:"
    )

    value = value.replace(
        ",",
        "\\,"
    )

    value = value.replace(
        ";",
        "\\;"
    )

    return value


# ==========================================================
# ASSカラー取得
# ==========================================================

def get_ass_color(
    color_name
):

    log(
        "ASSカラー取得"
    )

    log(
        f"color_name: {color_name}"
    )

    if color_name is None:

        raise RuntimeError(
            "字幕カラーが指定されていません。"
        )

    color_info = (
        SUBTITLE_COLORS.get(
            color_name
        )
    )

    log(
        f"color_info: {color_info}"
    )

    if not color_info:

        raise RuntimeError(
            f"字幕カラーが定義されていません: "
            f"{color_name}"
        )

    ass_color = color_info.get(
        "ass"
    )

    log(
        f"ASS color: {ass_color}"
    )

    if not ass_color:

        raise RuntimeError(
            f"字幕カラーのASS値が定義されていません: "
            f"{color_name}"
        )

    return str(
        ass_color
    )


# ==========================================================
# 字幕設定正規化
# ==========================================================

def normalize_subtitle_settings(
    subtitle_settings=None
):

    log_start(
        "字幕設定正規化開始"
    )

    log(
        f"input subtitle_settings: "
        f"{subtitle_settings!r}"
    )

    if subtitle_settings is None:

        log(
            "設定未指定 -> "
            "subtitle_font.py標準設定を取得"
        )

        result = (
            get_default_subtitle_font_settings()
        )

        log(
            f"default settings: {result!r}"
        )

        return result

    if not isinstance(
        subtitle_settings,
        dict
    ):

        raise TypeError(
            "subtitle_settingsはdictで指定してください。"
        )

    normalized = {}

    for key in SUBTITLE_SETTING_KEYS:

        if key in subtitle_settings:

            normalized[key] = (
                subtitle_settings.get(
                    key
                )
            )

    log(
        f"正式キーのみ抽出: {normalized!r}"
    )

    from subtitle_font import (
        select_subtitle_font
    )

    log(
        "subtitle_font.select_subtitle_font() "
        "呼び出し"
    )

    normalized = (
        select_subtitle_font(
            settings=normalized
        )
    )

    log(
        f"select_subtitle_font結果: "
        f"{normalized!r}"
    )

    result = {

        "preset_name":
            normalized.get(
                "preset_name"
            ),

        "font":
            normalized.get(
                "font"
            ),

        "text_color":
            normalized.get(
                "text_color"
            ),

        "outline_color":
            normalized.get(
                "outline_color"
            ),

        "outline_width":
            normalized.get(
                "outline_width"
            ),

    }

    log(
        f"最終字幕設定: {result!r}"
    )

    log(
        "字幕設定正規化完了"
    )

    return result


# ==========================================================
# 字幕フィルター作成
# ==========================================================

def make_subtitle_filter(
    srt_path,
    font_info=None,
    subtitle_settings=None
):

    log_start(
        "字幕フィルター作成開始"
    )

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
    )

    log(
        f"subtitle_settings: "
        f"{subtitle_settings!r}"
    )

    subtitle_path = (
        escape_ffmpeg_filter_path(
            srt_path
        )
    )

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )

    preset_name = (
        subtitle_settings.get(
            "preset_name"
        )
    )

    font = (
        subtitle_settings.get(
            "font"
        )
    )

    text_color_name = (
        subtitle_settings.get(
            "text_color"
        )
    )

    outline_color_name = (
        subtitle_settings.get(
            "outline_color"
        )
    )

    outline_width = (
        subtitle_settings.get(
            "outline_width"
        )
    )

    log(
        f"preset_name: {preset_name}"
    )

    log(
        f"font: {font}"
    )

    log(
        f"text_color: {text_color_name}"
    )

    log(
        f"outline_color: {outline_color_name}"
    )

    log(
        f"outline_width: {outline_width}"
    )

    if font is None:

        raise RuntimeError(
            "字幕フォントが設定されていません。"
        )

    if text_color_name is None:

        raise RuntimeError(
            "字幕文字色が設定されていません。"
        )

    if outline_color_name is None:

        raise RuntimeError(
            "字幕縁色が設定されていません。"
        )

    try:

        outline_width = int(
            outline_width
        )

    except (
        ValueError,
        TypeError
    ):

        raise RuntimeError(
            "字幕縁太さが不正です。"
        )

    if outline_width < 0:

        raise RuntimeError(
            "字幕縁太さが0未満です。"
        )

    if outline_width > 10:

        raise RuntimeError(
            "字幕縁太さが10を超えています。"
        )

    text_color = get_ass_color(
        text_color_name
    )

    outline_color = get_ass_color(
        outline_color_name
    )

    font_name = None

    if font_info:

        log(
            f"font_info: {font_info!r}"
        )

        detected_family = (
            font_info.get(
                "family"
            )
        )

        if detected_family:

            detected_family = str(
                detected_family
            ).strip()

            if (
                "Noto Sans CJK JP"
                in detected_family
                and
                len(detected_family)
                > 30
            ):

                font_name = None

            else:

                font_name = detected_family

    if not font_name:

        font_name = str(
            font
        ).strip()

    if not font_name:

        raise RuntimeError(
            "字幕フォント名を決定できませんでした。"
        )

    log(
        f"最終FontName: {font_name}"
    )

    if font_info:

        font_path = font_info.get(
            "path"
        )

        if font_path:

            font_path = Path(
                font_path
            ).resolve()

            font_directory = (
                font_path.parent
            )

            font_directory_escaped = (
                escape_ffmpeg_filter_path(
                    font_directory
                )
            )

            video_filter += (
                ":fontsdir='"
                +
                font_directory_escaped
                +
                "'"
            )

            log(
                f"字幕フォントディレクトリ: "
                f"{font_directory}"
            )

    style_parts = [

        "FontName="
        +
        escape_ffmpeg_value(
            font_name
        ),

        "PrimaryColour="
        +
        text_color,

        "OutlineColour="
        +
        outline_color,

        "Outline="
        +
        str(
            outline_width
        ),

    ]

    force_style = ",".join(
        style_parts
    )

    video_filter += (
        ":force_style='"
        +
        force_style
        +
        "'"
    )

    log(
        "字幕スタイル:"
    )

    log(
        f"preset_name: {preset_name}"
    )

    log(
        f"font: {font_name}"
    )

    log(
        f"text_color: {text_color_name}"
    )

    log(
        f"text_color ASS: {text_color}"
    )

    log(
        f"outline_color: {outline_color_name}"
    )

    log(
        f"outline_color ASS: {outline_color}"
    )

    log(
        f"outline_width: {outline_width}"
    )

    log(
        f"完成video_filter: {video_filter}"
    )

    log(
        "字幕フィルター作成完了"
    )

    return video_filter


# ==========================================================
# FFmpegコマンド表示
# ==========================================================

def command_to_string(
    command
):

    return " ".join(
        str(item)
        for item in command
    )


# ==========================================================
# FFmpegログ整形
# ==========================================================

def make_ffmpeg_error_detail(
    lines
):

    if not lines:

        return (
            "FFmpegからエラー内容が"
            "返されませんでした。"
        )

    return "\n".join(
        lines
    )


# ==========================================================
# 一時ファイル削除
# ==========================================================

def remove_file_safely(
    file_path
):

    if not file_path:
        return

    try:

        path = Path(
            file_path
        )

    except Exception:

        return

    try:

        if path.exists():

            path.unlink()

            log(
                f"ファイル削除: {path}"
            )

    except Exception as error:

        log(
            f"ファイル削除失敗: {error}"
        )


# ==========================================================
# FFmpeg stderrを安全に取得
# ==========================================================

def collect_ffmpeg_output(
    process,
    output_lines
):

    log(
        "FFmpeg stderr読み取り開始"
    )

    if process.stderr is None:

        log(
            "FFmpeg stderrがNoneです。"
        )

        return

    try:

        for raw_line in process.stderr:

            line = raw_line.rstrip()

            if not line:
                continue

            output_lines.append(
                line
            )

            print(
                "[FFMPEG]",
                line,
                flush=True
            )

    except Exception as error:

        log_exception(
            "FFmpeg stderr読み取り中に例外",
            error
        )

        raise

    finally:

        try:

            process.stderr.close()

        except Exception as error:

            log(
                f"stderr.close()失敗: {error}"
            )

    log(
        "FFmpeg stderr読み取り終了"
    )


# ==========================================================
# 字幕焼き込み本体
# ==========================================================

def embed_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    start_time = time.monotonic()

    log_start(
        "embed_subtitle() START"
    )

    log(
        f"mp4_path argument: {mp4_path!r}"
    )

    log(
        f"srt_path argument: {srt_path!r}"
    )

    log(
        f"output_path argument: {output_path!r}"
    )

    log(
        f"subtitle_settings argument: "
        f"{subtitle_settings!r}"
    )

    temp_output_path = None

    # ======================================================
    # STEP 1
    # ======================================================

    log_start(
        "STEP 1: MP4入力確認"
    )

    mp4_path = validate_input_file(
        mp4_path,
        ".mp4"
    )

    log(
        f"MP4確認完了: {mp4_path}"
    )

    # ======================================================
    # STEP 2
    # ======================================================

    log_start(
        "STEP 2: SRT入力確認"
    )

    srt_path = validate_input_file(
        srt_path,
        ".srt"
    )

    log(
        f"SRT確認完了: {srt_path}"
    )

    # ======================================================
    # STEP 3
    # ======================================================

    log_start(
        "STEP 3: SRT UTF-8確認"
    )

    validate_srt_encoding(
        srt_path
    )

    # ======================================================
    # STEP 4
    # ======================================================

    log_start(
        "STEP 4: 字幕設定正規化"
    )

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
    )

    log(
        f"normalized subtitle settings: "
        f"{subtitle_settings!r}"
    )

    # ======================================================
    # STEP 5
    # ======================================================

    log_start(
        "STEP 5: 出力先決定"
    )

    if output_path:

        log(
            f"指定output_pathあり: {output_path}"
        )

        output_path = (
            Path(
                output_path
            ).resolve()
        )

    else:

        log(
            "output_path未指定 -> 自動生成"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

    log(
        f"最終output_path: {output_path}"
    )

    # ======================================================
    # 入力と出力が同じにならないようにする
    # ======================================================

    if output_path == mp4_path:

        log(
            "WARNING: 入力と出力が同じです。"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

        log(
            f"変更後output_path: {output_path}"
        )

    # ======================================================
    # STEP 6
    # ======================================================

    log_start(
        "STEP 6: 出力フォルダ確認"
    )

    log(
        f"output directory: "
        f"{output_path.parent}"
    )

    try:

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    except OSError as error:

        log_exception(
            "出力フォルダ作成失敗",
            error
        )

        raise RuntimeError(
            "出力フォルダを作成できません: "
            +
            str(error)
        ) from error

    log(
        "出力フォルダ確認完了"
    )

    # ======================================================
    # STEP 7
    # ======================================================

    log_start(
        "STEP 7: FFmpeg確認"
    )

    ffmpeg_path = check_ffmpeg()

    log(
        f"使用FFmpeg: {ffmpeg_path}"
    )

    # ======================================================
    # STEP 8
    # ======================================================

    log_start(
        "STEP 8: フォント確認"
    )

    font = (
        subtitle_settings.get(
            "font"
        )
    )

    log(
        f"選択フォント: {font}"
    )

    font_info = find_japanese_font(
        font
    )

    if font_info:

        log(
            "日本語字幕フォント:"
        )

        log(
            f"path: {font_info.get('path')}"
        )

        log(
            f"family: {font_info.get('family')}"
        )

    else:

        log(
            "WARNING: 日本語フォントが"
            "検出できませんでした。"
        )

        log(
            "WARNING: Render環境に"
            "日本語フォントをインストールしてください。"
        )

    # ======================================================
    # STEP 9
    # ======================================================

    log_start(
        "STEP 9: 字幕フィルター生成"
    )

    video_filter = make_subtitle_filter(

        srt_path,

        font_info,

        subtitle_settings

    )

    log(
        "STEP 9完了: 字幕フィルター生成OK"
    )

    log(
        f"video_filter: {video_filter}"
    )

    # ======================================================
    # STEP 10
    # ======================================================

    log_start(
        "STEP 10: 入力MP4サイズ確認"
    )

    try:

        input_mp4_size = (
            mp4_path.stat().st_size
        )

    except OSError as error:

        log_exception(
            "入力MP4サイズ取得失敗",
            error
        )

        input_mp4_size = 0

    log(
        f"入力MP4サイズ: {input_mp4_size} bytes"
    )

    # ======================================================
    # STEP 11
    # ======================================================

    log_start(
        "STEP 11: 一時出力パス生成"
    )

    temp_output_path = (
        make_temp_output_path(
            output_path
        )
    )

    log(
        f"一時出力: {temp_output_path}"
    )

    # ======================================================
    # FFmpeg開始情報
    # ======================================================

    log_separator()

    log(
        "字幕焼き込み開始"
    )

    log(
        f"MP4: {mp4_path}"
    )

    log(
        f"SRT: {srt_path}"
    )

    log(
        f"出力: {output_path}"
    )

    log(
        f"一時出力: {temp_output_path}"
    )

    log(
        f"入力MP4サイズ: "
        f"{input_mp4_size} bytes"
    )

    log(
        f"FFmpeg threads: "
        f"{FFMPEG_THREADS}"
    )

    log(
        f"FFmpeg preset: "
        f"{FFMPEG_PRESET}"
    )

    log(
        f"FFmpeg CRF: "
        f"{FFMPEG_CRF}"
    )

    # ======================================================
    # STEP 12
    # ======================================================

    log_start(
        "STEP 12: FFmpegコマンド生成"
    )

    command = [

        ffmpeg_path,

        "-y",

        "-nostdin",

        "-hide_banner",

        "-loglevel",
        "info",

        "-i",
        str(mp4_path),

        "-vf",
        video_filter,

        "-c:v",
        "libx264",

        "-threads",
        FFMPEG_THREADS,

        "-preset",
        FFMPEG_PRESET,

        "-crf",
        FFMPEG_CRF,

        "-c:a",
        "copy",

        "-movflags",
        "+faststart",

        str(
            temp_output_path
        )

    ]

    log(
        f"FFmpeg command item count: "
        f"{len(command)}"
    )

    log(
        "FFmpeg video filter:"
    )

    log(
        video_filter
    )

    log(
        "FFmpeg command:"
    )

    log(
        command_to_string(
            command
        )
    )

    # ======================================================
    # STEP 13
    # ======================================================

    log_start(
        "STEP 13: FFmpeg subprocess.Popen開始"
    )

    process = None

    ffmpeg_output_lines = deque(
        maxlen=MAX_FFMPEG_LOG_LINES
    )

    log(
        f"FFmpegログ保持数: "
        f"max={MAX_FFMPEG_LOG_LINES}"
    )

    try:

        log(
            "FFmpegを起動します..."
        )

        process = subprocess.Popen(

            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            bufsize=1

        )

    except OSError as error:

        log_exception(
            "FFmpeg subprocess.Popenに失敗しました。",
            error
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "FFmpeg実行中にエラーが発生しました: "
            +
            str(error)

        ) from error

    log(
        f"FFmpeg process started: PID={process.pid}"
    )

    # ======================================================
    # STEP 14
    # ======================================================

    log_start(
        "STEP 14: FFmpeg stderrログ取得開始"
    )

    try:

        collect_ffmpeg_output(
            process,
            ffmpeg_output_lines
        )

    except Exception as error:

        log_exception(
            "FFmpegログ取得中のエラー",
            error
        )

        if process:

            try:
                log(
                    "FFmpeg process.kill()を実行します"
                )

                process.kill()

            except Exception as kill_error:

                log(
                    f"process.kill()失敗: "
                    f"{kill_error}"
                )

            try:
                process.wait(
                    timeout=10
                )

            except Exception as wait_error:

                log(
                    f"process.wait()失敗: "
                    f"{wait_error}"
                )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "FFmpegログ取得中のエラー: "
            +
            str(error)

        ) from error

    log(
        "STEP 14完了: FFmpeg stderrログ取得終了"
    )

    log(
        f"保持しているFFmpegログ行数: "
        f"{len(ffmpeg_output_lines)}"
    )

    # ======================================================
    # STEP 15
    # ======================================================

    log_start(
        "STEP 15: FFmpeg終了状態確認"
    )

    try:

        return_code = process.wait()

    except Exception as error:

        log_exception(
            "FFmpegの終了状態確認に失敗しました。",
            error
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "FFmpegの終了状態を"
            "確認できませんでした: "
            +
            str(error)

        ) from error

    log(
        f"FFmpeg return code: {return_code}"
    )

    # ======================================================
    # 処理時間
    # ======================================================

    elapsed_time = (
        time.monotonic()
        -
        start_time
    )

    log(
        f"現在までの処理時間: "
        f"{format_elapsed_time(elapsed_time)}"
    )

    # ======================================================
    # STEP 16
    # ======================================================

    if return_code != 0:

        log_start(
            "STEP 16: FFmpeg異常終了"
        )

        log(
            f"FFmpegエラー: "
            f"return code={return_code}"
        )

        error_detail = (
            make_ffmpeg_error_detail(
                ffmpeg_output_lines
            )
        )

        log(
            "FFmpeg最後のログ100行:"
        )

        log(
            error_detail
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "字幕焼き込みに失敗しました。"
            "\n\n"
            +
            error_detail
            +
            "\n\n"
            +
            "FFmpeg return code: "
            +
            str(return_code)
            +
            "\n"
            +
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            )

        )

    log(
        "STEP 16完了: FFmpeg正常終了"
    )

    # ======================================================
    # STEP 17
    # ======================================================

    log_start(
        "STEP 17: 一時出力ファイル確認"
    )

    log(
        f"temp_output_path: {temp_output_path}"
    )

    if not temp_output_path.exists():

        log(
            "ERROR: FFmpeg正常終了後も"
            "一時出力が存在しません"
        )

        raise RuntimeError(

            "FFmpegは正常終了しましたが、"
            "一時出力ファイルが作成されていません。"

        )

    if not temp_output_path.is_file():

        log(
            "ERROR: 一時出力パスが通常ファイルではありません"
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "FFmpegの一時出力先が"
            "ファイルではありません。"

        )

    try:

        output_size = (
            temp_output_path.stat().st_size
        )

    except OSError as error:

        log_exception(
            "一時出力ファイルのサイズ取得に失敗しました。",
            error
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "一時出力ファイルを"
            "確認できませんでした: "
            +
            str(error)

        ) from error

    log(
        f"一時出力ファイルサイズ: "
        f"{output_size} bytes"
    )

    if output_size <= 0:

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(
            "FFmpeg出力ファイルのサイズが0です。"
        )

    log(
        "一時出力ファイル確認OK"
    )

    # ======================================================
    # STEP 18
    # ======================================================

    log_start(
        "STEP 18: 正式出力ファイル確認"
    )

    if output_path.exists():

        log(
            "既存の正式出力があります。"
        )

        try:

            old_size = (
                output_path.stat().st_size
            )

            log(
                f"既存正式出力サイズ: "
                f"{old_size} bytes"
            )

        except OSError as error:

            log(
                f"既存正式出力のサイズ取得失敗: "
                f"{error}"
            )

        try:

            output_path.unlink()

        except OSError as error:

            log_exception(
                "既存の正式出力削除に失敗しました。",
                error
            )

            remove_file_safely(
                temp_output_path
            )

            raise RuntimeError(

                "既存の出力ファイルを"
                "削除できませんでした: "
                +
                str(error)

            ) from error

        log(
            "既存の正式出力削除完了"
        )

    else:

        log(
            "既存の正式出力はありません"
        )

    # ======================================================
    # STEP 19
    # ======================================================

    log_start(
        "STEP 19: 一時ファイルを正式出力へ移動"
    )

    log(
        f"source temp: {temp_output_path}"
    )

    log(
        f"destination: {output_path}"
    )

    try:

        os.replace(

            str(
                temp_output_path
            ),

            str(
                output_path
            )

        )

    except OSError as error:

        log_exception(
            "os.replace()に失敗しました。",
            error
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "字幕MP4を正式出力へ"
            "移動できませんでした: "
            +
            str(error)

        ) from error

    log(
        "os.replace()成功"
    )

    # ======================================================
    # STEP 20
    # ======================================================

    log_start(
        "STEP 20: 最終出力ファイル確認"
    )

    if not output_path.exists():

        raise RuntimeError(

            "正式な字幕MP4が"
            "作成されていません。"

        )

    if not output_path.is_file():

        raise RuntimeError(

            "正式出力先がファイルではありません。"

        )

    try:

        final_size = (
            output_path.stat().st_size
        )

    except OSError as error:

        log_exception(
            "正式出力ファイルのサイズ取得に失敗しました。",
            error
        )

        raise RuntimeError(

            "正式出力ファイルを"
            "確認できませんでした: "
            +
            str(error)

        ) from error

    log(
        f"正式出力ファイルサイズ: "
        f"{final_size} bytes"
    )

    if final_size <= 0:

        remove_file_safely(
            output_path
        )

        raise RuntimeError(
            "正式出力ファイルのサイズが0です。"
        )

    # ======================================================
    # STEP 21
    # ======================================================

    log_start(
        "STEP 21: 一時ファイル残存確認"
    )

    if temp_output_path.exists():

        log(
            "WARNING: 一時ファイルが残っています"
        )

        remove_file_safely(
            temp_output_path
        )

    else:

        log(
            "一時ファイルは残っていません"
        )

    # ======================================================
    # 完了
    # ======================================================

    elapsed_time = (
        time.monotonic()
        -
        start_time
    )

    log_start(
        "字幕焼き込み最終完了"
    )

    log(
        f"入力MP4: {mp4_path}"
    )

    log(
        f"入力SRT: {srt_path}"
    )

    log(
        f"出力ファイル: {output_path}"
    )

    log(
        f"サイズ: {final_size} bytes"
    )

    log(
        f"処理時間: "
        f"{format_elapsed_time(elapsed_time)}"
    )

    log(
        "embed_subtitle正常終了"
    )

    return output_path


# ==========================================================
# 外部向け正式関数
# ==========================================================

def create_subtitle_mp4(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    log(
        "create_subtitle_mp4開始"
    )

    log(
        f"mp4_path: {mp4_path!r}"
    )

    log(
        f"srt_path: {srt_path!r}"
    )

    log(
        f"output_path: {output_path!r}"
    )

    log(
        f"subtitle_settings: {subtitle_settings!r}"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )

    log(
        f"create_subtitle_mp4完了: {result}"
    )

    return result


# ==========================================================
# 互換用別名
# ==========================================================

def create_burned_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    log(
        "create_burned_subtitle開始"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )

    log(
        f"create_burned_subtitle完了: {result}"
    )

    return result


def burn_subtitles(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    log(
        "burn_subtitles開始"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )

    log(
        f"burn_subtitles完了: {result}"
    )

    return result


# ==========================================================
# downloads内から実行
# ==========================================================

def embed_from_downloads(
    mp4_filename,
    srt_filename,
    subtitle_settings=None
):

    log(
        "====================================="
    )

    log(
        "embed_from_downloads開始"
    )

    log(
        f"mp4_filename input: {mp4_filename!r}"
    )

    log(
        f"srt_filename input: {srt_filename!r}"
    )

    log(
        f"subtitle_settings: {subtitle_settings!r}"
    )

    mp4_filename = Path(
        mp4_filename
    ).name

    srt_filename = Path(
        srt_filename
    ).name

    log(
        f"安全化後mp4_filename: {mp4_filename}"
    )

    log(
        f"安全化後srt_filename: {srt_filename}"
    )

    log(
        f"DOWNLOADS_DIR: {DOWNLOADS_DIR}"
    )

    log(
        "DOWNLOADS_DIR作成開始"
    )

    try:

        DOWNLOADS_DIR.mkdir(

            parents=True,

            exist_ok=True

        )

    except OSError as error:

        log_exception(
            "DOWNLOADS_DIR作成に失敗しました。",
            error
        )

        raise

    log(
        "DOWNLOADS_DIR作成・確認OK"
    )

    mp4_path = (
        DOWNLOADS_DIR
        /
        mp4_filename
    )

    srt_path = (
        DOWNLOADS_DIR
        /
        srt_filename
    )

    log(
        f"DOWNLOAD_DIR: "
        f"{DOWNLOADS_DIR}"
    )

    log(
        f"downloads MP4: "
        f"{mp4_path}"
    )

    log(
        f"downloads SRT: "
        f"{srt_path}"
    )

    log(
        "embed_subtitleへ処理を渡します"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        subtitle_settings=subtitle_settings

    )

    log(
        f"embed_from_downloads完了: {result}"
    )

    log(
        "====================================="
    )

    return result


# ==========================================================
# コマンドライン
# ==========================================================

def main():

    log(
        "##################################################"
    )

    log(
        "subtitle.py main()開始"
    )

    log(
        f"sys.argv: {sys.argv!r}"
    )

    log(
        f"Python executable: {sys.executable}"
    )

    log(
        f"Python version: {sys.version}"
    )

    log(
        f"Current working directory: {os.getcwd()}"
    )

    log(
        f"DOWNLOAD_DIR config: {DOWNLOAD_DIR!r}"
    )

    log(
        f"DOWNLOADS_DIR: {DOWNLOADS_DIR}"
    )

    log(
        f"Environment SUBTITLE_FONT: "
        f"{os.environ.get('SUBTITLE_FONT')!r}"
    )

    if len(sys.argv) < 3:

        log(
            "コマンドライン引数不足"
        )

        print()

        print(
            "使用方法:"
        )

        print(
            "python subtitle.py "
            "動画.mp4 字幕.srt"
        )

        print()

        return 1

    mp4_filename = (
        sys.argv[1]
    )

    srt_filename = (
        sys.argv[2]
    )

    log(
        f"CLI MP4: {mp4_filename!r}"
    )

    log(
        f"CLI SRT: {srt_filename!r}"
    )

    start_time = time.monotonic()

    log(
        "main処理タイマー開始"
    )

    try:

        # ==================================================
        # subtitle_font.pyから標準設定を取得
        # ==================================================

        log(
            "STEP MAIN-1: "
            "subtitle_font.pyから標準設定取得開始"
        )

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

        log(
            "標準設定取得完了"
        )

        log(
            f"subtitle_settings: "
            f"{subtitle_settings!r}"
        )

        # ==================================================
        # 字幕焼き込み
        # ==================================================

        log(
            "STEP MAIN-2: embed_from_downloads開始"
        )

        output_path = (
            embed_from_downloads(

                mp4_filename,

                srt_filename,

                subtitle_settings

            )
        )

        log(
            "STEP MAIN-2完了"
        )

        log(
            f"output_path returned: {output_path}"
        )

        elapsed_time = (

            time.monotonic()
            -
            start_time

        )

        log(
            f"main総処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        print()

        print(
            "====================================="
        )

        print(
            "字幕焼き込み成功"
        )

        print(
            "====================================="
        )

        print(
            f"入力MP4: "
            f"{mp4_filename}"
        )

        print(
            f"入力SRT: "
            f"{srt_filename}"
        )

        print(
            f"preset_name: "
            f"{subtitle_settings.get('preset_name')}"
        )

        print(
            f"font: "
            f"{subtitle_settings.get('font')}"
        )

        print(
            f"text_color: "
            f"{subtitle_settings.get('text_color')}"
        )

        print(
            f"outline_color: "
            f"{subtitle_settings.get('outline_color')}"
        )

        print(
            f"outline_width: "
            f"{subtitle_settings.get('outline_width')}"
        )

        print(
            f"出力: "
            f"{output_path.name}"
        )

        print(
            f"出力パス: "
            f"{output_path}"
        )

        print(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        print(
            "====================================="
        )

        print()

        log(
            "subtitle.py main()正常終了"
        )

        log(
            "##################################################"
        )

        return 0

    except Exception as error:

        elapsed_time = (

            time.monotonic()
            -
            start_time

        )

        log_exception(
            "main()で例外が発生しました。",
            error
        )

        log(
            f"例外発生時の処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        print()

        print(
            "====================================="
        )

        print(
            "字幕焼き込み失敗"
        )

        print(
            "====================================="
        )

        print(
            str(error),
            file=sys.stderr
        )

        print(

            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            ),

            file=sys.stderr

        )

        print(
            "====================================="
        )

        print()

        log(
            "subtitle.py main()異常終了"
        )

        log(
            "##################################################"
        )

        return 1


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    log(
        "=================================================="
    )

    log(
        "__main__実行開始"
    )

    log(
        f"PID: {os.getpid()}"
    )

    log(
        f"argv: {sys.argv!r}"
    )

    log(
        "=================================================="
    )

    exit_code = main()

    log(
        f"main() returned exit_code={exit_code}"
    )

    log(
        "__main__終了"
    )

    sys.exit(
        exit_code
    )
)
