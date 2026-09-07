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
#
# 役割:
#
#   subtitle_font.py
#       ↓
#   字幕設定の定義・標準値・正規化
#
#   subtitle_routes.py
#       ↓
#   HTTP入力の受付・入力名の吸収
#
#   subtitle.py
#       ↓
#   FFmpegによる字幕焼き込み
#
# ==========================================================

import os
import sys
import time
import shutil
import subprocess

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
# ログ
# ==========================================================

def log(message):

    print(
        "[SUBTITLE]",
        message,
        flush=True
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

    log(
        "validate_input_file開始"
    )

    log(
        f"file_path: {file_path}"
    )

    log(
        f"expected extension: {extension}"
    )

    path = Path(
        file_path
    ).resolve()

    log(
        f"resolved path: {path}"
    )

    log(
        f"path.exists(): {path.exists()}"
    )

    if not path.exists():

        log(
            "ERROR: ファイルが存在しません"
        )

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    log(
        f"path.is_file(): {path.is_file()}"
    )

    if not path.is_file():

        log(
            "ERROR: ファイルではありません"
        )

        raise ValueError(
            f"ファイルではありません: {path}"
        )

    log(
        f"path.suffix: {path.suffix}"
    )

    if path.suffix.lower() != extension.lower():

        log(
            "ERROR: 拡張子が一致しません"
        )

        raise ValueError(
            f"{extension} ファイルではありません: {path}"
        )

    try:

        size = path.stat().st_size

        log(
            f"file size: {size} bytes"
        )

    except OSError as error:

        log(
            f"ERROR: ファイルサイズ取得失敗: {error}"
        )

        raise RuntimeError(
            f"ファイルサイズを確認できません: {error}"
        ) from error

    if size <= 0:

        log(
            "ERROR: ファイルサイズが0以下です"
        )

        raise ValueError(
            f"ファイルが0 bytesです: {path}"
        )

    log(
        "validate_input_file完了"
    )

    return path


# ==========================================================
# 出力ファイル名
# ==========================================================

def make_output_path(
    mp4_path
):

    log(
        "make_output_path開始"
    )

    log(
        f"input mp4_path: {mp4_path}"
    )

    mp4_path = Path(
        mp4_path
    ).resolve()

    log(
        f"resolved mp4_path: {mp4_path}"
    )

    stem = mp4_path.stem

    log(
        f"stem: {stem}"
    )

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

    log(
        f"初期candidate: {candidate}"
    )

    counter = 2

    while candidate.exists():

        log(
            f"candidate exists: {candidate}"
        )

        candidate = (
            mp4_path.parent
            /
            f"{stem}_{counter}.mp4"
        )

        log(
            f"次のcandidate: {candidate}"
        )

        counter += 1

    log(
        f"最終output candidate: {candidate}"
    )

    log(
        "make_output_path完了"
    )

    return candidate


# ==========================================================
# 一時出力パス
# ==========================================================

def make_temp_output_path(
    output_path
):

    log(
        "make_temp_output_path開始"
    )

    log(
        f"output_path: {output_path}"
    )

    output_path = Path(
        output_path
    ).resolve()

    log(
        f"resolved output_path: {output_path}"
    )

    timestamp = time.time_ns()

    log(
        f"time_ns: {timestamp}"
    )

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
        f"生成された一時出力パス: {temp_path}"
    )

    log(
        f"一時出力親フォルダ: {temp_path.parent}"
    )

    log(
        f"一時出力親フォルダexists: "
        f"{temp_path.parent.exists()}"
    )

    log(
        f"一時出力パスexists: "
        f"{temp_path.exists()}"
    )

    log(
        "make_temp_output_path完了"
    )

    return temp_path


# ==========================================================
# FFmpeg存在確認
# ==========================================================

def check_ffmpeg():

    log(
        "====================================="
    )

    log(
        "FFmpeg確認開始"
    )

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    log(
        f"shutil.which('ffmpeg'): {ffmpeg_path}"
    )

    if not ffmpeg_path:

        log(
            "ERROR: FFmpegが見つかりません"
        )

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

        log(
            "ERROR: FFmpeg FileNotFoundError"
        )

        raise RuntimeError(
            "FFmpegが見つかりません。"
        )

    except subprocess.TimeoutExpired:

        log(
            "ERROR: FFmpeg version確認timeout"
        )

        raise RuntimeError(
            "FFmpegの確認がタイムアウトしました。"
        )

    except OSError as error:

        log(
            f"ERROR: FFmpeg起動失敗: {error}"
        )

        raise RuntimeError(
            f"FFmpegを起動できません: {error}"
        ) from error

    log(
        f"FFmpeg version returncode: "
        f"{result.returncode}"
    )

    if result.returncode != 0:

        log(
            f"FFmpeg version stderr: "
            f"{result.stderr}"
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
        first_line
    )

    log(
        "FFmpeg確認完了"
    )

    log(
        "====================================="
    )

    return ffmpeg_path


# ==========================================================
# SRT UTF-8確認
# ==========================================================

def validate_srt_encoding(
    srt_path
):

    log(
        "validate_srt_encoding開始"
    )

    log(
        f"SRT path: {srt_path}"
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

            log(
                "SRT open成功"
            )

            first_content = file.read(
                4096
            )

            log(
                f"SRT先頭4096 bytes相当の"
                f"文字数: {len(first_content)}"
            )

    except UnicodeDecodeError as error:

        log(
            f"ERROR: SRT UTF-8 decode失敗: {error}"
        )

        raise RuntimeError(

            "SRTファイルをUTF-8として"
            "読み込めませんでした。"
            "SRTをUTF-8形式で保存してください。"

        ) from error

    except OSError as error:

        log(
            f"ERROR: SRT open/read失敗: {error}"
        )

        raise RuntimeError(

            f"SRTファイルを読み込めませんでした: {error}"

        ) from error

    if not first_content.strip():

        log(
            "ERROR: SRTが空です"
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
        "validate_srt_encoding完了"
    )

    return True


# ==========================================================
# フォントfamily取得
# ==========================================================

def get_font_family_from_path(
    font_path
):

    log(
        "get_font_family_from_path開始"
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
            "fc-scanがありません"
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

        log(
            f"fc-scan exception: {error}"
        )

        return None

    log(
        f"fc-scan returncode: {result.returncode}"
    )

    if result.returncode != 0:

        log(
            f"fc-scan stderr: {result.stderr}"
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

    log(
        f"検出family数: {len(families)}"
    )

    if not families:

        log(
            "familyがありません"
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
        f"最終family: {family}"
    )

    log(
        "get_font_family_from_path完了"
    )

    return family or None


# ==========================================================
# fc-match
# ==========================================================

def fc_match_font(
    requested_font
):

    log(
        "fc_match_font開始"
    )

    log(
        f"requested_font: {requested_font}"
    )

    if not requested_font:

        log(
            "requested_fontが空です"
        )

        return None

    fc_match = shutil.which(
        "fc-match"
    )

    log(
        f"fc-match: {fc_match}"
    )

    if not fc_match:

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

        log(
            f"fc-matchエラー: {error}"
        )

        return None

    log(
        f"fc-match returncode: {result.returncode}"
    )

    if result.returncode != 0:

        log(
            f"fc-match stderr: {result.stderr}"
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
            f"fc-match font candidate: {font_path}"
        )

        if not font_path.is_file():

            log(
                "candidateはファイルではありません"
            )

            continue

        family = (
            get_font_family_from_path(
                font_path
            )
        )

        log(
            f"fc-match detected family: {family}"
        )

        result_data = {

            "path":
                font_path.resolve(),

            "family":
                family

        }

        log(
            f"fc_match_font result: {result_data}"
        )

        log(
            "fc_match_font完了"
        )

        return result_data

    log(
        "fc-matchでフォントが見つかりませんでした"
    )

    return None


# ==========================================================
# 日本語フォント検索
# ==========================================================

def find_japanese_font(
    requested_font=None
):

    log(
        "====================================="
    )

    log(
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
        f"環境変数SUBTITLE_FONT: "
        f"{environment_font}"
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
            "SUBTITLE_FONTに指定された"
            "フォントが存在しません"
        )

        log(
            str(
                environment_font_path
            )
        )

    # ======================================================
    # 2. subtitle_font.pyの指定フォント
    # ======================================================

    if requested_font:

        requested_font = str(
            requested_font
        ).strip()

        log(
            f"requested_font normalized: "
            f"{requested_font}"
        )

        requested_path = (
            Path(
                requested_font
            ).expanduser()
        )

        log(
            f"requested_path: {requested_path}"
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
                "指定フォントファイルを使用"
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
            "requested_fontは直接ファイルではありません"
        )

        matched = fc_match_font(
            requested_font
        )

        if matched:

            log(
                "fc-matchで指定フォントを検出"
            )

            log(
                f"font: {requested_font}"
            )

            log(
                f"actual family: "
                f"{matched.get('family')}"
            )

            log(
                f"path: "
                f"{matched.get('path')}"
            )

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

    log(
        f"日本語フォント候補数: {len(candidates)}"
    )

    for family_name in candidates:

        log(
            f"フォント候補検索: {family_name}"
        )

        matched = fc_match_font(
            family_name
        )

        if not matched:

            log(
                f"未検出: {family_name}"
            )

            continue

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
            f"path: "
            f"{matched.get('path')}"
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

            log(
                f"fc-list検索エラー: {error}"
            )

            result = None

        if result:

            log(
                f"fc-list returncode: "
                f"{result.returncode}"
            )

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
                    "fc-list日本語フォント検出"
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
        f"手動検索対象ディレクトリ数: "
        f"{len(font_directories)}"
    )

    for directory in font_directories:

        log(
            f"フォントディレクトリ確認: {directory}"
        )

        if not directory.exists():

            log(
                f"ディレクトリ不存在: {directory}"
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
                        "日本語フォント検出"
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

                log(
                    f"手動フォント検索エラー: "
                    f"{error}"
                )

                continue

    log(
        "日本語フォントが見つかりませんでした"
    )

    log(
        "====================================="
    )

    return None


# ==========================================================
# FFmpegフィルターパスエスケープ
# ==========================================================

def escape_ffmpeg_filter_path(
    file_path
):

    log(
        "escape_ffmpeg_filter_path開始"
    )

    log(
        f"original path: {file_path}"
    )

    path = str(
        Path(
            file_path
        ).resolve()
    )

    log(
        f"resolved path: {path}"
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

    log(
        "escape_ffmpeg_filter_path完了"
    )

    return path


# ==========================================================
# FFmpeg force_style値エスケープ
# ==========================================================

def escape_ffmpeg_value(
    value
):

    log(
        "escape_ffmpeg_value開始"
    )

    log(
        f"original value: {value!r}"
    )

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

    log(
        f"escaped value: {value!r}"
    )

    log(
        "escape_ffmpeg_value完了"
    )

    return value


# ==========================================================
# ASSカラー取得
# ==========================================================

def get_ass_color(
    color_name
):

    log(
        "get_ass_color開始"
    )

    log(
        f"color_name: {color_name}"
    )

    if color_name is None:

        log(
            "ERROR: color_name is None"
        )

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

        log(
            "ERROR: color_infoが存在しません"
        )

        raise RuntimeError(
            f"字幕カラーが定義されていません: "
            f"{color_name}"
        )

    ass_color = color_info.get(
        "ass"
    )

    log(
        f"ass_color: {ass_color}"
    )

    if not ass_color:

        log(
            "ERROR: ass_colorがありません"
        )

        raise RuntimeError(
            f"字幕カラーのASS値が定義されていません: "
            f"{color_name}"
        )

    log(
        "get_ass_color完了"
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

    log(
        "====================================="
    )

    log(
        "normalize_subtitle_settings開始"
    )

    log(
        f"subtitle_settings input: "
        f"{subtitle_settings}"
    )

    if subtitle_settings is None:

        log(
            "subtitle_settings is None"
        )

        result = (
            get_default_subtitle_font_settings()
        )

        log(
            f"default settings: {result}"
        )

        log(
            "normalize_subtitle_settings完了"
        )

        return result

    if not isinstance(
        subtitle_settings,
        dict
    ):

        log(
            "ERROR: subtitle_settingsがdictではありません"
        )

        raise TypeError(
            "subtitle_settingsはdictで指定してください。"
        )

    normalized = {}

    log(
        "正式設定キー抽出開始"
    )

    for key in SUBTITLE_SETTING_KEYS:

        if key in subtitle_settings:

            normalized[key] = (
                subtitle_settings.get(
                    key
                )
            )

            log(
                f"設定取得: {key} = "
                f"{normalized[key]!r}"
            )

        else:

            log(
                f"設定キーなし: {key}"
            )

    log(
        f"抽出後normalized: {normalized}"
    )

    from subtitle_font import select_subtitle_font

    log(
        "subtitle_font.select_subtitle_font開始"
    )

    normalized = (
        select_subtitle_font(
            settings=normalized
        )
    )

    log(
        f"select_subtitle_font結果: "
        f"{normalized}"
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
        f"最終正規化設定: {result}"
    )

    log(
        "normalize_subtitle_settings完了"
    )

    log(
        "====================================="
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

    log(
        "====================================="
    )

    log(
        "make_subtitle_filter開始"
    )

    log(
        f"srt_path: {srt_path}"
    )

    log(
        f"font_info: {font_info}"
    )

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
    )

    log(
        f"normalize後subtitle_settings: "
        f"{subtitle_settings}"
    )

    subtitle_path = (
        escape_ffmpeg_filter_path(
            srt_path
        )
    )

    log(
        f"escaped subtitle_path: "
        f"{subtitle_path}"
    )

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )

    log(
        f"初期video_filter: {video_filter}"
    )

    # ======================================================
    # 正式名称5つから取得
    # ======================================================

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
        "字幕設定値:"
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

    # ======================================================
    # 値確認
    # ======================================================

    log(
        "字幕設定値バリデーション開始"
    )

    if font is None:

        log(
            "ERROR: font is None"
        )

        raise RuntimeError(
            "字幕フォントが設定されていません。"
        )

    if text_color_name is None:

        log(
            "ERROR: text_color is None"
        )

        raise RuntimeError(
            "字幕文字色が設定されていません。"
        )

    if outline_color_name is None:

        log(
            "ERROR: outline_color is None"
        )

        raise RuntimeError(
            "字幕縁色が設定されていません。"
        )

    try:

        outline_width = int(
            outline_width
        )

        log(
            f"outline_width int変換後: "
            f"{outline_width}"
        )

    except (
        ValueError,
        TypeError
    ):

        log(
            f"ERROR: outline_width int変換失敗: "
            f"{outline_width!r}"
        )

        raise RuntimeError(
            "字幕縁太さが不正です。"
        )

    if outline_width < 0:

        log(
            "ERROR: outline_width < 0"
        )

        raise RuntimeError(
            "字幕縁太さが0未満です。"
        )

    if outline_width > 10:

        log(
            "ERROR: outline_width > 10"
        )

        raise RuntimeError(
            "字幕縁太さが10を超えています。"
        )

    log(
        "字幕設定値バリデーション完了"
    )

    # ======================================================
    # ASSカラー
    # ======================================================

    log(
        "ASSカラー取得開始"
    )

    text_color = get_ass_color(
        text_color_name
    )

    log(
        f"text_color ASS: {text_color}"
    )

    outline_color = get_ass_color(
        outline_color_name
    )

    log(
        f"outline_color ASS: {outline_color}"
    )

    # ======================================================
    # FontName
    # ======================================================

    log(
        "FontName決定開始"
    )

    font_name = None

    if font_info:

        log(
            "font_infoあり"
        )

        detected_path = font_info.get(
            "path"
        )

        detected_family = (
            font_info.get(
                "family"
            )
        )

        log(
            f"font_info.path: {detected_path}"
        )

        log(
            f"font_info.family: {detected_family}"
        )

        if detected_family:

            detected_family = str(
                detected_family
            ).strip()

            log(
                f"detected_family: "
                f"{detected_family}"
            )

            if (
                "Noto Sans CJK JP"
                in detected_family
                and
                len(detected_family)
                > 30
            ):

                log(
                    "familyが異常に長いためFontNameには使用しません"
                )

                font_name = None

            else:

                font_name = detected_family

    else:

        log(
            "font_infoなし"
        )

    if not font_name:

        log(
            "font_infoからFontNameを決定できないため"
            "設定値fontを使用します"
        )

        font_name = str(
            font
        ).strip()

    log(
        f"最終FontName: {font_name}"
    )

    if not font_name:

        log(
            "ERROR: FontNameが空です"
        )

        raise RuntimeError(
            "字幕フォント名を決定できませんでした。"
        )

    # ======================================================
    # fontsdir
    # ======================================================

    if font_info:

        log(
            "fontsdir設定開始"
        )

        font_path = font_info.get(
            "path"
        )

        log(
            f"font_info.path: {font_path}"
        )

        if font_path:

            font_path = Path(
                font_path
            ).resolve()

            log(
                f"resolved font_path: {font_path}"
            )

            font_directory = (
                font_path.parent
            )

            log(
                f"font_directory: {font_directory}"
            )

            font_directory_escaped = (
                escape_ffmpeg_filter_path(
                    font_directory
                )
            )

            log(
                f"escaped font_directory: "
                f"{font_directory_escaped}"
            )

            video_filter += (
                ":fontsdir='"
                +
                font_directory_escaped
                +
                "'"
            )

            log(
                "fontsdirをvideo_filterへ追加しました"
            )

            log(
                "字幕フォントディレクトリ:"
            )

            log(
                str(
                    font_directory
                )
            )

    else:

        log(
            "font_infoがないためfontsdirは設定しません"
        )

    # ======================================================
    # ASS force_style
    # ======================================================

    log(
        "ASS force_style生成開始"
    )

    escaped_font_name = (
        escape_ffmpeg_value(
            font_name
        )
    )

    log(
        f"escaped_font_name: "
        f"{escaped_font_name}"
    )

    style_parts = [

        "FontName="
        +
        escaped_font_name,

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

    log(
        f"style_parts: {style_parts}"
    )

    force_style = ",".join(
        style_parts
    )

    log(
        f"force_style: {force_style}"
    )

    video_filter += (
        ":force_style='"
        +
        force_style
        +
        "'"
    )

    log(
        "force_styleをvideo_filterへ追加しました"
    )

    # ======================================================
    # ログ
    # ======================================================

    log(
        "字幕スタイル:"
    )

    log(
        f"preset_name: "
        f"{preset_name}"
    )

    log(
        f"font: "
        f"{font_name}"
    )

    log(
        f"text_color: "
        f"{text_color_name}"
    )

    log(
        f"text_color ASS: "
        f"{text_color}"
    )

    log(
        f"outline_color: "
        f"{outline_color_name}"
    )

    log(
        f"outline_color ASS: "
        f"{outline_color}"
    )

    log(
        f"outline_width: "
        f"{outline_width}"
    )

    log(
        "最終video_filter:"
    )

    log(
        video_filter
    )

    log(
        "make_subtitle_filter完了"
    )

    log(
        "====================================="
    )

    return video_filter


# ==========================================================
# FFmpegコマンド表示
# ==========================================================

def command_to_string(
    command
):

    log(
        "command_to_string開始"
    )

    log(
        f"command item count: {len(command)}"
    )

    result = " ".join(

        str(item)

        for item in command

    )

    log(
        f"command string length: {len(result)}"
    )

    log(
        "command_to_string完了"
    )

    return result


# ==========================================================
# FFmpegログ整形
# ==========================================================

def make_ffmpeg_error_detail(
    lines
):

    log(
        "make_ffmpeg_error_detail開始"
    )

    log(
        f"保持FFmpegログ行数: {len(lines)}"
    )

    if not lines:

        log(
            "FFmpegログがありません"
        )

        return (
            "FFmpegからエラー内容が"
            "返されませんでした。"
        )

    result = "\n".join(
        lines
    )

    log(
        f"エラー詳細文字数: {len(result)}"
    )

    log(
        "make_ffmpeg_error_detail完了"
    )

    return result


# ==========================================================
# 一時ファイル削除
# ==========================================================

def remove_file_safely(
    file_path
):

    log(
        "remove_file_safely開始"
    )

    log(
        f"file_path: {file_path}"
    )

    if not file_path:

        log(
            "file_pathが空です"
        )

        return

    try:

        path = Path(
            file_path
        )

    except Exception as error:

        log(
            f"Path変換失敗: {error}"
        )

        return

    log(
        f"path: {path}"
    )

    try:

        exists = path.exists()

        log(
            f"path.exists(): {exists}"
        )

        if exists:

            path.unlink()

            log(
                f"ファイル削除成功: {path}"
            )

        else:

            log(
                "削除対象ファイルは存在しません"
            )

    except Exception as error:

        log(
            f"ファイル削除失敗: {error}"
        )

    log(
        "remove_file_safely完了"
    )


# ==========================================================
# 字幕焼き込み
# ==========================================================

def embed_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    start_time = time.monotonic()

    log(
        "##################################################"
    )

    log(
        "embed_subtitle開始"
    )

    log(
        f"引数 mp4_path: {mp4_path}"
    )

    log(
        f"引数 srt_path: {srt_path}"
    )

    log(
        f"引数 output_path: {output_path}"
    )

    log(
        f"引数 subtitle_settings: "
        f"{subtitle_settings}"
    )

    # ======================================================
    # 入力確認
    # ======================================================

    log(
        "STEP 1: MP4入力ファイル確認開始"
    )

    mp4_path = validate_input_file(
        mp4_path,
        ".mp4"
    )

    log(
        f"MP4 resolved: {mp4_path}"
    )

    log(
        "STEP 1完了"
    )

    log(
        "STEP 2: SRT入力ファイル確認開始"
    )

    srt_path = validate_input_file(
        srt_path,
        ".srt"
    )

    log(
        f"SRT resolved: {srt_path}"
    )

    log(
        "STEP 2完了"
    )

    # ======================================================
    # SRT確認
    # ======================================================

    log(
        "STEP 3: SRT UTF-8確認開始"
    )

    validate_srt_encoding(
        srt_path
    )

    log(
        "STEP 3完了"
    )

    # ======================================================
    # 字幕設定
    # ======================================================

    log(
        "STEP 4: 字幕設定正規化開始"
    )

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
    )

    log(
        "字幕設定:"
    )

    log(
        str(
            subtitle_settings
        )
    )

    log(
        "STEP 4完了"
    )

    # ======================================================
    # 出力先
    # ======================================================

    log(
        "STEP 5: 出力先決定開始"
    )

    if output_path:

        log(
            "output_pathが指定されています"
        )

        log(
            f"指定output_path: {output_path}"
        )

        output_path = (
            Path(
                output_path
            ).resolve()
        )

        log(
            f"resolved output_path: "
            f"{output_path}"
        )

    else:

        log(
            "output_path未指定"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

        log(
            f"自動生成output_path: "
            f"{output_path}"
        )

    # ======================================================
    # 入力と出力が同じにならないようにする
    # ======================================================

    log(
        "STEP 6: 入出力パス重複確認"
    )

    log(
        f"mp4_path: {mp4_path}"
    )

    log(
        f"output_path: {output_path}"
    )

    log(
        f"paths equal: "
        f"{output_path == mp4_path}"
    )

    if output_path == mp4_path:

        log(
            "入力と出力が同一です"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

        log(
            f"重複回避後output_path: "
            f"{output_path}"
        )

    log(
        "STEP 6完了"
    )

    # ======================================================
    # 出力フォルダ
    # ======================================================

    log(
        "STEP 7: 出力フォルダ確認開始"
    )

    log(
        f"output parent: {output_path.parent}"
    )

    try:

        output_path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        log(
            "出力フォルダmkdir成功"
        )

    except OSError as error:

        log(
            f"ERROR: 出力フォルダ作成失敗: {error}"
        )

        raise RuntimeError(

            "出力フォルダを作成できません: "
            +
            str(error)

        ) from error

    log(
        f"output parent exists: "
        f"{output_path.parent.exists()}"
    )

    log(
        f"output parent is_dir: "
        f"{output_path.parent.is_dir()}"
    )

    log(
        "STEP 7完了"
    )

    # ======================================================
    # FFmpeg確認
    # ======================================================

    log(
        "STEP 8: FFmpeg確認開始"
    )

    ffmpeg_path = check_ffmpeg()

    log(
        f"使用FFmpeg: {ffmpeg_path}"
    )

    log(
        "STEP 8完了"
    )

    # ======================================================
    # 正式名称:
    #   font
    # ======================================================

    log(
        "STEP 9: 選択フォント取得"
    )

    font = (
        subtitle_settings.get(
            "font"
        )
    )

    log(
        "選択フォント:"
    )

    log(
        str(
            font
        )
    )

    log(
        "STEP 9完了"
    )

    # ======================================================
    # 日本語フォント検索
    # ======================================================

    log(
        "STEP 10: 日本語フォント検索開始"
    )

    font_info = find_japanese_font(
        font
    )

    log(
        f"find_japanese_font result: "
        f"{font_info}"
    )

    if font_info:

        log(
            "日本語字幕フォント:"
        )

        log(
            str(
                font_info.get(
                    "path"
                )
            )
        )

        log(
            "検出フォント名:"
        )

        log(
            str(
                font_info.get(
                    "family"
                )
            )
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

    log(
        "STEP 10完了"
    )

    # ======================================================
    # 字幕フィルター
    # ======================================================

    log(
        "STEP 11: 字幕フィルター生成開始"
    )

    video_filter = make_subtitle_filter(

        srt_path,

        font_info,

        subtitle_settings

    )

    log(
        "STEP 11完了: 字幕フィルター生成OK"
    )

    log(
        f"video_filter: {video_filter}"
    )

    # ======================================================
    # 入力サイズ
    # ======================================================

    log(
        "STEP 12: 入力MP4サイズ確認"
    )

    try:

        input_mp4_size = (
            mp4_path.stat().st_size
        )

    except OSError as error:

        log(
            f"入力MP4サイズ取得失敗: {error}"
        )

        input_mp4_size = 0

    log(
        f"入力MP4サイズ: "
        f"{input_mp4_size} bytes"
    )

    log(
        "STEP 12完了"
    )

    # ======================================================
    # 一時出力
    # ======================================================

    log(
        "STEP 13: 一時出力パス生成"
    )

    temp_output_path = (
        make_temp_output_path(
            output_path
        )
    )

    log(
        f"一時出力: {temp_output_path}"
    )

    log(
        f"一時出力exists: "
        f"{temp_output_path.exists()}"
    )

    if temp_output_path.exists():

        log(
            "WARNING: 一時出力パスが既に存在します"
        )

        try:

            existing_temp_size = (
                temp_output_path.stat().st_size
            )

            log(
                f"既存一時出力サイズ: "
                f"{existing_temp_size} bytes"
            )

        except OSError as error:

            log(
                f"既存一時出力サイズ取得失敗: "
                f"{error}"
            )

    else:

        log(
            "一時出力パスは未使用です"
        )

    log(
        "STEP 13完了"
    )

    # ======================================================
    # 開始ログ
    # ======================================================

    log(
        "====================================="
    )

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
    # FFmpegコマンド
    # ======================================================

    log(
        "STEP 14: FFmpegコマンド生成開始"
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

    # ======================================================
    # コマンドログ
    # ======================================================

    log(
        "FFmpeg video filter:"
    )

    log(
        video_filter
    )

    log(
        "FFmpeg command:"
    )

    command_string = command_to_string(
        command
    )

    log(
        command_string
    )

    log(
        "STEP 14完了: FFmpegコマンド生成OK"
    )

    # ======================================================
    # FFmpeg実行
    # ======================================================

    log(
        "STEP 15: FFmpeg subprocess.Popen開始"
    )

    log(
        "FFmpegを起動します..."
    )

    log(
        f"Popen command length: {len(command)}"
    )

    log(
        "stderr=PIPE: True"
    )

    log(
        "stdout=DEVNULL: True"
    )

    process_start_time = time.monotonic()

    try:

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

        log(
            f"ERROR: Popen OSError: {error}"
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
        "FFmpeg process started"
    )

    log(
        f"PID={process.pid}"
    )

    log(
        f"poll immediately after start: "
        f"{process.poll()}"
    )

    log(
        f"returncode immediately after start: "
        f"{process.returncode}"
    )

    log(
        "STEP 15完了: FFmpeg subprocess起動OK"
    )

    # ======================================================
    # 最後の100行だけ保持
    # ======================================================

    ffmpeg_output_lines = deque(

        maxlen=MAX_FFMPEG_LOG_LINES

    )
