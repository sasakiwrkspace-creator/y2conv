# ==========================================================
# Subtitle FFmpeg Test
# subtitle_test_ffmpeg.py
#
# FFmpeg字幕焼き込みテスト専用
#
# 目的:
#   downloads内に固定したMP4 + SRTを使用して、
#   現在のFFmpegパラメータで字幕付きMP4を作成できるか確認する。
#
# 入力:
#   downloads/TEST_MP4_FILENAME
#   downloads/TEST_SRT_FILENAME
#
# 出力:
#   入力MP4の名前 + "_embed.mp4"
#
# 例:
#   test.mp4
#   test.srt
#
#   ↓
#
#   test_embed.mp4
#
# 字幕設定の唯一の情報源:
#   subtitle_font.py
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
# テスト対象ファイル
# ==========================================================
#
# downloadsフォルダ内に、この2ファイルを置いてください。
#
# 例:
#
# downloads/
#   test.mp4
#   test.srt
#
# ==========================================================

TEST_MP4_FILENAME = "test.mp4"
TEST_SRT_FILENAME = "test.srt"


# ==========================================================
# downloads
# ==========================================================

DOWNLOADS_DIR = Path(
    DOWNLOAD_DIR
)


# ==========================================================
# FFmpegログ保持数
# ==========================================================

MAX_FFMPEG_LOG_LINES = 100


# ==========================================================
# 現在のsubtitle.pyと同じFFmpeg設定
# ==========================================================

FFMPEG_THREADS = "1"
FFMPEG_PRESET = "ultrafast"
FFMPEG_CRF = "23"


# ==========================================================
# subtitle_font.pyとの共通設定キー
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
    "[SUBTITLE TEST] ==========================================",
    flush=True
)

print(
    "[SUBTITLE TEST] subtitle_test_ffmpeg.py MODULE LOAD START",
    flush=True
)

try:

    print(
        f"[SUBTITLE TEST] __file__: "
        f"{Path(__file__).resolve()}",
        flush=True
    )

except Exception as error:

    print(
        f"[SUBTITLE TEST] __file__取得失敗: {error}",
        flush=True
    )


print(
    f"[SUBTITLE TEST] Python executable: "
    f"{sys.executable}",
    flush=True
)

print(
    f"[SUBTITLE TEST] Python version: "
    f"{sys.version}",
    flush=True
)

try:

    print(
        f"[SUBTITLE TEST] Current working directory: "
        f"{os.getcwd()}",
        flush=True
    )

except Exception as error:

    print(
        f"[SUBTITLE TEST] cwd取得失敗: {error}",
        flush=True
    )


print(
    f"[SUBTITLE TEST] DOWNLOAD_DIR: "
    f"{DOWNLOAD_DIR}",
    flush=True
)

print(
    f"[SUBTITLE TEST] DOWNLOADS_DIR: "
    f"{DOWNLOADS_DIR}",
    flush=True
)

print(
    f"[SUBTITLE TEST] TEST_MP4_FILENAME: "
    f"{TEST_MP4_FILENAME}",
    flush=True
)

print(
    f"[SUBTITLE TEST] TEST_SRT_FILENAME: "
    f"{TEST_SRT_FILENAME}",
    flush=True
)

print(
    f"[SUBTITLE TEST] SUBTITLE_FONT environment: "
    f"{os.environ.get('SUBTITLE_FONT')!r}",
    flush=True
)

print(
    "[SUBTITLE TEST] subtitle_test_ffmpeg.py MODULE LOAD COMPLETE",
    flush=True
)

print(
    "[SUBTITLE TEST] ==========================================",
    flush=True
)


# ==========================================================
# ログ
# ==========================================================

def log(message):

    try:

        print(
            "[SUBTITLE TEST]",
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


def log_exception(
    message,
    error
):

    log(message)

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
                "[SUBTITLE TEST] " + traceback_text,
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

def format_elapsed_time(
    seconds
):

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
        f"file_path: {file_path!r}"
    )

    log(
        f"expected extension: {extension}"
    )

    try:

        path = Path(
            file_path
        ).expanduser().resolve()

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

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"ファイルではありません: {path}"
        )

    actual_suffix = path.suffix.lower()

    log(
        f"actual extension: {actual_suffix}"
    )

    if actual_suffix != extension.lower():

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

        raise ValueError(
            f"ファイルが0 bytesです: {path}"
        )

    log(
        "入力ファイル確認OK"
    )

    return path


# ==========================================================
# 出力ファイル名
#
# 入力:
#   test.mp4
#
# 出力:
#   test_embed.mp4
#
# 既存の場合:
#   test_embed_2.mp4
#   test_embed_3.mp4
#   ...
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

    base_suffix = "_embed"

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
            f"{stem}{base_suffix}_{counter}.mp4"
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
            f".subtitle_test_{timestamp}.tmp.mp4"
        )
    )

    log(
        f"一時出力パス: {temp_path}"
    )

    return temp_path


# ==========================================================
# FFmpeg確認
# ==========================================================

def check_ffmpeg():

    log_start(
        "FFmpeg確認開始"
    )

    # ======================================================
    # FFmpeg本体
    # ======================================================

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    log(
        f"shutil.which(ffmpeg): {ffmpeg_path}"
    )

    if not ffmpeg_path:

        raise RuntimeError(
            "FFmpegがPATH上に見つかりません。"
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

    except Exception as error:

        raise RuntimeError(
            f"FFmpeg起動確認に失敗しました: {error}"
        ) from error

    log(
        f"FFmpeg version returncode: "
        f"{result.returncode}"
    )

    if result.returncode != 0:

        log(
            result.stderr[-2000:]
        )

        raise RuntimeError(
            "FFmpegを正常に起動できませんでした。"
        )

    version_lines = (
        result.stdout.splitlines()
    )

    if version_lines:

        log(
            f"FFmpeg version: "
            f"{version_lines[0]}"
        )

    # ======================================================
    # libx264
    # ======================================================

    log(
        "libx264確認開始"
    )

    encoder_result = subprocess.run(

        [
            ffmpeg_path,
            "-hide_banner",
            "-encoders"
        ],

        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,

        text=True,

        encoding="utf-8",
        errors="replace",

        timeout=30

    )

    encoder_text = (
        encoder_result.stdout
        +
        encoder_result.stderr
    )

    if encoder_result.returncode != 0:

        raise RuntimeError(
            "FFmpegのエンコーダー一覧を取得できませんでした。"
        )

    if "libx264" not in encoder_text:

        raise RuntimeError(
            "FFmpegにlibx264エンコーダーがありません。"
        )

    log(
        "libx264: OK"
    )

    # ======================================================
    # subtitles filter
    # ======================================================

    log(
        "subtitlesフィルター確認開始"
    )

    filter_result = subprocess.run(

        [
            ffmpeg_path,
            "-hide_banner",
            "-filters"
        ],

        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,

        text=True,

        encoding="utf-8",
        errors="replace",

        timeout=30

    )

    filter_text = (
        filter_result.stdout
        +
        filter_result.stderr
    )

    if filter_result.returncode != 0:

        raise RuntimeError(
            "FFmpegのフィルター一覧を取得できませんでした。"
        )

    if "subtitles" not in filter_text:

        raise RuntimeError(
            "FFmpegにsubtitlesフィルターがありません。"
        )

    log(
        "subtitles filter: OK"
    )

    # ======================================================
    # libass
    # ======================================================

    log(
        "libass確認開始"
    )

    try:

        build_result = subprocess.run(

            [
                ffmpeg_path,
                "-buildconf"
            ],

            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",
            errors="replace",

            timeout=30

        )

        build_text = (
            build_result.stdout
            +
            build_result.stderr
        )

        if "libass" in build_text.lower():

            log(
                "libass: OK"
            )

        else:

            log(
                "WARNING: -buildconfからlibassを"
                "確認できませんでした。"
            )

    except Exception as error:

        log(
            f"WARNING: libass確認失敗: {error}"
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

        raise RuntimeError(
            "SRTファイルをUTF-8として"
            "読み込めませんでした。"
        ) from error

    except OSError as error:

        raise RuntimeError(
            f"SRTファイルを読み込めませんでした: {error}"
        ) from error

    if not first_content.strip():

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    log(
        f"SRT先頭文字数: {len(first_content)}"
    )

    log(
        "SRT UTF-8確認OK"
    )

    return True


# ==========================================================
# フォントfamily取得
# ==========================================================

def get_font_family_from_path(
    font_path
):

    log(
        f"font family取得: {font_path}"
    )

    fc_scan = shutil.which(
        "fc-scan"
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

    if result.returncode != 0:

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
        f"fc-match requested_font: {requested_font}"
    )

    if not requested_font:

        return None

    fc_match = shutil.which(
        "fc-match"
    )

    if not fc_match:

        return None

    try:

        result = subprocess.run(

            [
                fc_match,
                "-f",
                "%{file}\n",
                str(requested_font)
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

    if result.returncode != 0:

        return None

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        font_path = Path(
            line
        )

        if not font_path.is_file():

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
    # 1. 環境変数
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

        if environment_font_path.is_file():

            family = (
                get_font_family_from_path(
                    environment_font_path
                )
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

            return {

                "path":
                    requested_path,

                "family":
                    family

            }

        matched = fc_match_font(
            requested_font
        )

        if matched:

            return matched

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

    for family_name in candidates:

        log(
            f"候補検索: {family_name}"
        )

        matched = fc_match_font(
            family_name
        )

        if matched:

            log(
                "日本語フォント検出"
            )

            log(
                f"requested family: {family_name}"
            )

            log(
                f"actual family: "
                f"{matched.get('family')}"
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

    for directory in font_directories:

        if not directory.exists():
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

    return None


# ==========================================================
# FFmpeg filter path escape
# ==========================================================

def escape_ffmpeg_filter_path(
    file_path
):

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

    return path


# ==========================================================
# FFmpeg force_style value escape
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
        f"ASSカラー取得: {color_name}"
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

    if not color_info:

        raise RuntimeError(
            f"字幕カラーが定義されていません: "
            f"{color_name}"
        )

    ass_color = color_info.get(
        "ass"
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

    if subtitle_settings is None:

        log(
            "設定未指定 -> "
            "subtitle_font.py標準設定を取得"
        )

        result = (
            get_default_subtitle_font_settings()
        )

        if not isinstance(
            result,
            dict
        ):

            raise RuntimeError(
                "subtitle_font.pyの標準設定が"
                "dictではありません。"
            )

        normalized = {}

        for key in SUBTITLE_SETTING_KEYS:

            normalized[key] = (
                result.get(
                    key
                )
            )

        log(
            f"default normalized settings: "
            f"{normalized!r}"
        )

        return normalized

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

    if not isinstance(
        normalized,
        dict
    ):

        raise RuntimeError(
            "select_subtitle_font()の戻り値が"
            "dictではありません。"
        )

    result = {}

    for key in SUBTITLE_SETTING_KEYS:

        result[key] = (
            normalized.get(
                key
            )
        )

    log(
        f"最終字幕設定: {result!r}"
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
    ) as error:

        raise RuntimeError(
            "字幕縁太さが不正です。"
        ) from error

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

    # ======================================================
    # FontName
    # ======================================================

    font_name = None

    if font_info:

        detected_family = (
            font_info.get(
                "family"
            )
        )

        if detected_family:

            detected_family = str(
                detected_family
            ).strip()

            if detected_family:

                font_name = (
                    detected_family
                )

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

    # ======================================================
    # fontsdir
    # ======================================================

    if font_info:

        font_path = font_info.get(
            "path"
        )

        if font_path:

            font_path = Path(
                font_path
            ).resolve()

            if font_path.is_file():

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

    # ======================================================
    # ASS style
    # ======================================================

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
# FFmpegコマンド文字列
# ==========================================================

def command_to_string(
    command
):

    return " ".join(
        str(item)
        for item in command
    )


# ==========================================================
# FFmpegエラー詳細
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
# ファイル安全削除
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
# FFmpeg stderr逐次取得
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
# FFmpeg終了処理
# ==========================================================

def terminate_process_safely(
    process
):

    if process is None:
        return

    try:

        if process.poll() is None:

            log(
                "FFmpeg process terminate()"
            )

            process.terminate()

            try:

                process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:

                log(
                    "terminate()後も終了しないためkill()"
                )

                process.kill()

                process.wait(
                    timeout=5
                )

    except Exception as error:

        log(
            f"FFmpeg終了処理失敗: {error}"
        )


# ==========================================================
# 字幕焼き込みテスト本体
# ==========================================================

def run_ffmpeg_subtitle_test():

    start_time = time.monotonic()

    process = None

    temp_output_path = None

    ffmpeg_output_lines = deque(
        maxlen=MAX_FFMPEG_LOG_LINES
    )

    try:

        log_start(
            "FFmpeg字幕焼き込みテスト START"
        )

        # ==================================================
        # STEP 1
        # 固定入力ファイル決定
        # ==================================================

        log_start(
            "STEP 1: 固定入力ファイル決定"
        )

        DOWNLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        mp4_path = (
            DOWNLOADS_DIR
            /
            TEST_MP4_FILENAME
        )

        srt_path = (
            DOWNLOADS_DIR
            /
            TEST_SRT_FILENAME
        )

        log(
            f"固定MP4: {mp4_path}"
        )

        log(
            f"固定SRT: {srt_path}"
        )

        # ==================================================
        # STEP 2
        # MP4確認
        # ==================================================

        log_start(
            "STEP 2: MP4確認"
        )

        mp4_path = validate_input_file(
            mp4_path,
            ".mp4"
        )

        # ==================================================
        # STEP 3
        # SRT確認
        # ==================================================

        log_start(
            "STEP 3: SRT確認"
        )

        srt_path = validate_input_file(
            srt_path,
            ".srt"
        )

        # ==================================================
        # STEP 4
        # SRT UTF-8
        # ==================================================

        log_start(
            "STEP 4: SRT UTF-8確認"
        )

        validate_srt_encoding(
            srt_path
        )

        # ==================================================
        # STEP 5
        # subtitle_font.py
        # ==================================================

        log_start(
            "STEP 5: subtitle_font.py設定取得"
        )

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

        if not isinstance(
            subtitle_settings,
            dict
        ):

            raise RuntimeError(
                "subtitle_font.pyの標準設定が"
                "dictではありません。"
            )

        subtitle_settings = (
            normalize_subtitle_settings(
                subtitle_settings
            )
        )

        log(
            f"preset_name: "
            f"{subtitle_settings.get('preset_name')}"
        )

        log(
            f"font: "
            f"{subtitle_settings.get('font')}"
        )

        log(
            f"text_color: "
            f"{subtitle_settings.get('text_color')}"
        )

        log(
            f"outline_color: "
            f"{subtitle_settings.get('outline_color')}"
        )

        log(
            f"outline_width: "
            f"{subtitle_settings.get('outline_width')}"
        )

        # ==================================================
        # STEP 6
        # 出力先
        # ==================================================

        log_start(
            "STEP 6: 出力先決定"
        )

        output_path = (
            make_output_path(
                mp4_path
            )
        )

        log(
            f"最終出力: {output_path}"
        )

        # ==================================================
        # STEP 7
        # FFmpeg
        # ==================================================

        log_start(
            "STEP 7: FFmpeg確認"
        )

        ffmpeg_path = (
            check_ffmpeg()
        )

        log(
            f"使用FFmpeg: {ffmpeg_path}"
        )

        # ==================================================
        # STEP 8
        # フォント
        # ==================================================

        log_start(
            "STEP 8: 日本語フォント確認"
        )

        font = (
            subtitle_settings.get(
                "font"
            )
        )

        font_info = (
            find_japanese_font(
                font
            )
        )

        if not font_info:

            raise RuntimeError(
                "日本語字幕フォントが見つかりません。"
            )

        log(
            f"font path: "
            f"{font_info.get('path')}"
        )

        log(
            f"font family: "
            f"{font_info.get('family')}"
        )

        # ==================================================
        # STEP 9
        # filter
        # ==================================================

        log_start(
            "STEP 9: 字幕フィルター生成"
        )

        video_filter = (
            make_subtitle_filter(

                srt_path,

                font_info,

                subtitle_settings

            )
        )

        # ==================================================
        # STEP 10
        # 入力サイズ
        # ==================================================

        try:

            input_mp4_size = (
                mp4_path.stat().st_size
            )

        except OSError:

            input_mp4_size = 0

        log(
            f"入力MP4サイズ: "
            f"{input_mp4_size} bytes"
        )

        # ==================================================
        # STEP 11
        # 一時出力
        # ==================================================

        log_start(
            "STEP 11: 一時出力パス生成"
        )

        temp_output_path = (
            make_temp_output_path(
                output_path
            )
        )

        # ==================================================
        # STEP 12
        # FFmpegコマンド
        # ==================================================

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
            "FFmpeg設定:"
        )

        log(
            f"threads: {FFMPEG_THREADS}"
        )

        log(
            f"preset: {FFMPEG_PRESET}"
        )

        log(
            f"crf: {FFMPEG_CRF}"
        )

        log(
            "video filter:"
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

        # ==================================================
        # STEP 13
        # FFmpeg開始
        # ==================================================

        log_start(
            "STEP 13: FFmpeg開始"
        )

        try:

            process = subprocess.Popen(

                command,

                stdout=subprocess.DEVNULL,

                stderr=subprocess.PIPE,

                stdin=subprocess.DEVNULL,

                text=True,

                encoding="utf-8",

                errors="replace",

                bufsize=1

            )

        except OSError as error:

            raise RuntimeError(
                f"FFmpeg実行開始に失敗しました: {error}"
            ) from error

        log(
            f"FFmpeg PID: {process.pid}"
        )

        # ==================================================
        # STEP 14
        # stderr
        # ==================================================

        log_start(
            "STEP 14: FFmpegログ取得"
        )

        collect_ffmpeg_output(
            process,
            ffmpeg_output_lines
        )

        # ==================================================
        # STEP 15
        # 終了コード
        # ==================================================

        log_start(
            "STEP 15: FFmpeg終了状態確認"
        )

        return_code = (
            process.wait()
        )

        log(
            f"FFmpeg return code: "
            f"{return_code}"
        )

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        # ==================================================
        # STEP 16
        # FFmpeg失敗
        # ==================================================

        if return_code != 0:

            log_start(
                "STEP 16: FFmpeg異常終了"
            )

            error_detail = (
                make_ffmpeg_error_detail(
                    ffmpeg_output_lines
                )
            )

            log(
                "FFmpeg最後のログ:"
            )

            log(
                error_detail
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

            )

        log(
            "FFmpeg正常終了"
        )

        # ==================================================
        # STEP 17
        # 一時ファイル確認
        # ==================================================

        log_start(
            "STEP 17: 一時出力ファイル確認"
        )

        if not temp_output_path.exists():

            raise RuntimeError(
                "FFmpegは正常終了しましたが、"
                "一時出力ファイルがありません。"
            )

        if not temp_output_path.is_file():

            raise RuntimeError(
                "一時出力パスがファイルではありません。"
            )

        output_size = (
            temp_output_path.stat().st_size
        )

        log(
            f"一時出力サイズ: "
            f"{output_size} bytes"
        )

        if output_size <= 0:

            raise RuntimeError(
                "FFmpeg出力ファイルのサイズが0です。"
            )

        # ==================================================
        # STEP 18
        # 正式出力
        # ==================================================

        log_start(
            "STEP 18: 正式出力作成"
        )

        if output_path.exists():

            log(
                f"既存出力を削除: {output_path}"
            )

            if not output_path.is_file():

                raise RuntimeError(
                    "既存の出力パスがファイルではありません。"
                )

            output_path.unlink()

        os.replace(

            str(
                temp_output_path
            ),

            str(
                output_path
            )

        )

        # ==================================================
        # STEP 19
        # 最終確認
        # ==================================================

        log_start(
            "STEP 19: 最終出力確認"
        )

        if not output_path.exists():

            raise RuntimeError(
                "正式出力ファイルが作成されていません。"
            )

        if not output_path.is_file():

            raise RuntimeError(
                "正式出力先がファイルではありません。"
            )

        final_size = (
            output_path.stat().st_size
        )

        log(
            f"正式出力サイズ: "
            f"{final_size} bytes"
        )

        if final_size <= 0:

            remove_file_safely(
                output_path
            )

            raise RuntimeError(
                "正式出力ファイルのサイズが0です。"
            )

        # ==================================================
        # STEP 20
        # 成功
        # ==================================================

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log_start(
            "字幕FFmpegテスト SUCCESS"
        )

        print()

        print(
            "===============================================",
            flush=True
        )

        print(
            "字幕焼き込みテスト成功",
            flush=True
        )

        print(
            "===============================================",
            flush=True
        )

        print(
            f"入力MP4: {mp4_path}",
            flush=True
        )

        print(
            f"入力SRT: {srt_path}",
            flush=True
        )

        print(
            f"出力MP4: {output_path}",
            flush=True
        )

        print(
            f"出力サイズ: {final_size} bytes",
            flush=True
        )

        print(
            "",
            flush=True
        )

        print(
            "FFmpeg parameters:",
            flush=True
        )

        print(
            f"  threads = {FFMPEG_THREADS}",
            flush=True
        )

        print(
            f"  preset  = {FFMPEG_PRESET}",
            flush=True
        )

        print(
            f"  crf     = {FFMPEG_CRF}",
            flush=True
        )

        print(
            "",
            flush=True
        )

        print(
            "Subtitle settings:",
            flush=True
        )

        print(
            f"  preset_name   = "
            f"{subtitle_settings.get('preset_name')}",
            flush=True
        )

        print(
            f"  font          = "
            f"{subtitle_settings.get('font')}",
            flush=True
        )

        print(
            f"  text_color    = "
            f"{subtitle_settings.get('text_color')}",
            flush=True
        )

        print(
            f"  outline_color = "
            f"{subtitle_settings.get('outline_color')}",
            flush=True
        )

        print(
            f"  outline_width = "
            f"{subtitle_settings.get('outline_width')}",
            flush=True
        )

        print(
            "",
            flush=True
        )

        print(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}",
            flush=True
        )

        print(
            "===============================================",
            flush=True
        )

        print(
            "",
            flush=True
        )

        log(
            "テスト正常終了"
        )

        return output_path

    except Exception as error:

        if process is not None:

            terminate_process_safely(
                process
            )

        remove_file_safely(
            temp_output_path
        )

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log_exception(
            "字幕FFmpegテスト失敗",
            error
        )

        print()

        print(
            "===============================================",
            flush=True
        )

        print(
            "字幕焼き込みテスト失敗",
            flush=True
        )

        print(
            "===============================================",
            flush=True
        )

        print(
            f"ERROR: {error}",
            file=sys.stderr,
            flush=True
        )

        print(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}",
            file=sys.stderr,
            flush=True
        )

        print(
            "===============================================",
            flush=True
        )

        print()

        raise


# ==========================================================
# main
# ==========================================================

def main():

    start_time = time.monotonic()

    log(
        "##################################################"
    )

    log(
        "subtitle_test_ffmpeg.py main()開始"
    )

    log(
        f"sys.argv: {sys.argv!r}"
    )

    log(
        f"Python executable: {sys.executable}"
    )

    log(
        f"DOWNLOAD_DIR: {DOWNLOAD_DIR}"
    )

    log(
        f"DOWNLOADS_DIR: {DOWNLOADS_DIR}"
    )

    log(
        f"固定MP4: {TEST_MP4_FILENAME}"
    )

    log(
        f"固定SRT: {TEST_SRT_FILENAME}"
    )

    log(
        "FFmpeg parameters:"
    )

    log(
        f"threads={FFMPEG_THREADS}"
    )

    log(
        f"preset={FFMPEG_PRESET}"
    )

    log(
        f"crf={FFMPEG_CRF}"
    )

    try:

        run_ffmpeg_subtitle_test()

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log(
            f"main()正常終了: "
            f"{format_elapsed_time(elapsed_time)}"
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

        log(
            f"main()異常終了: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        log(
            f"ERROR: {error}"
        )

        log(
            "##################################################"
        )

        return 1


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    exit_code = main()

    sys.exit(
        exit_code
    )
