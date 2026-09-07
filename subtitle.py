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

# Render低メモリ環境向け
FFMPEG_THREADS = "1"

# エンコード速度優先
FFMPEG_PRESET = "ultrafast"

# 画質
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
        f"path exists: {path.exists()}"
    )

    if not path.exists():

        log(
            "ERROR: ファイルが存在しません"
        )

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    log(
        f"path is_file: {path.is_file()}"
    )

    if not path.is_file():

        log(
            "ERROR: パスがファイルではありません"
        )

        raise ValueError(
            f"ファイルではありません: {path}"
        )

    log(
        f"actual suffix: {path.suffix.lower()}"
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
            "ERROR: ファイルサイズが0 bytesです"
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

        log(
            "入力ファイル名が既に_sub_embedで終わっています"
        )

    else:

        candidate = (
            mp4_path.parent
            /
            f"{stem}{base_suffix}.mp4"
        )

    log(
        f"初期候補出力: {candidate}"
    )

    counter = 2

    while candidate.exists():

        log(
            f"候補出力が既に存在します: {candidate}"
        )

        candidate = (
            mp4_path.parent
            /
            f"{stem}_{counter}.mp4"
        )

        log(
            f"次の候補: {candidate}"
        )

        counter += 1

    log(
        f"最終出力パス: {candidate}"
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
        f"一時出力パスexists: {temp_path.exists()}"
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
        "check_ffmpeg開始"
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

        log(
            "FFmpeg -version実行開始"
        )

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

        log(
            f"FFmpeg -version returncode: "
            f"{result.returncode}"
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
            "ERROR: FFmpeg確認タイムアウト"
        )

        raise RuntimeError(
            "FFmpegの確認がタイムアウトしました。"
        )

    except OSError as error:

        log(
            f"ERROR: FFmpeg起動OSエラー: {error}"
        )

        raise RuntimeError(
            f"FFmpegを起動できません: {error}"
        ) from error

    if result.returncode != 0:

        log(
            "ERROR: FFmpeg -version失敗"
        )

        log(
            f"stdout: {result.stdout[-1000:]}"
        )

        log(
            f"stderr: {result.stderr[-1000:]}"
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
        "check_ffmpeg完了"
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

        log(
            "SRT UTF-8読み込み開始"
        )

        with open(

            srt_path,

            "r",

            encoding="utf-8-sig"

        ) as file:

            first_content = file.read(
                4096
            )

        log(
            f"SRT先頭4096 bytes相当読み込み完了"
        )

        log(
            f"SRT先頭内容空白除去後empty: "
            f"{not bool(first_content.strip())}"
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
            f"ERROR: SRT読み込みOSエラー: {error}"
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

        log(
            "fc-scan実行開始"
        )

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

        log(
            f"fc-scan returncode: {result.returncode}"
        )

    except Exception as error:

        log(
            f"fc-scan例外: {error}"
        )

        return None

    if result.returncode != 0:

        log(
            "fc-scan失敗"
        )

        if result.stderr:

            log(
                f"fc-scan stderr: {result.stderr[-1000:]}"
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
            "familyが検出できませんでした"
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
        f"font family: {family}"
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

        log(
            "fc-matchがありません"
        )

        return None

    try:

        log(
            "fc-match実行開始"
        )

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

        log(
            f"fc-match returncode: {result.returncode}"
        )

    except Exception as error:

        log(
            f"fc-matchエラー: {error}"
        )

        return None

    if result.returncode != 0:

        log(
            "fc-matchが正常終了しませんでした"
        )

        if result.stderr:

            log(
                f"fc-match stderr: {result.stderr[-1000:]}"
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
            f"fc-match font path: {font_path}"
        )

        if not font_path.is_file():

            log(
                f"font pathがファイルではありません: "
                f"{font_path}"
            )

            continue

        family = (
            get_font_family_from_path(
                font_path
            )
        )

        result_info = {

            "path":
                font_path.resolve(),

            "family":
                family

        }

        log(
            f"fc-match結果: {result_info}"
        )

        log(
            "fc_match_font完了"
        )

        return result_info

    log(
        "fc-matchから有効なフォントが取得できませんでした"
    )

    return None


# ==========================================================
# 日本語フォント検索
# ==========================================================

def find_japanese_font(
    requested_font=None
):

    log(
        "find_japanese_font開始"
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

    log(
        "STEP FONT-1: SUBTITLE_FONT確認"
    )

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
            f"SUBTITLE_FONT resolved path: "
            f"{environment_font_path}"
        )

        log(
            f"SUBTITLE_FONT exists: "
            f"{environment_font_path.exists()}"
        )

        log(
            f"SUBTITLE_FONT is_file: "
            f"{environment_font_path.is_file()}"
        )

        if environment_font_path.is_file():

            family = (
                get_font_family_from_path(
                    environment_font_path
                )
            )

            log(
                "環境変数指定フォント:"
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
            "フォントが存在しません:"
        )

        log(
            str(
                environment_font_path
            )
        )

    # ======================================================
    # 2. subtitle_font.pyの指定フォント
    # ======================================================

    log(
        "STEP FONT-2: subtitle_font.py指定フォント確認"
    )

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

        log(
            f"requested_path exists: "
            f"{requested_path.exists()}"
        )

        log(
            f"requested_path is_file: "
            f"{requested_path.is_file()}"
        )

        # ファイルパス指定
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

        # fc-match
        log(
            "指定フォントをfc-matchで検索開始"
        )

        matched = fc_match_font(
            requested_font
        )

        if matched:

            log(
                "選択されたフォントを検出:"
            )

            log(
                f"font: {requested_font}"
            )

            log(
                f"actual family: {matched.get('family')}"
            )

            log(
                f"path: {matched.get('path')}"
            )

            return matched

        log(
            "requested_fontのfc-match結果なし"
        )

    # ======================================================
    # 3. 日本語フォント候補
    # ======================================================

    log(
        "STEP FONT-3: 日本語フォント候補検索"
    )

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

    log(
        "STEP FONT-4: fc-list日本語フォント検索"
    )

    fc_list = shutil.which(
        "fc-list"
    )

    log(
        f"fc-list: {fc_list}"
    )

    if fc_list:

        try:

            log(
                "fc-list実行開始"
            )

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

            log(
                f"fc-list returncode: {result.returncode}"
            )

        except Exception as error:

            log(
                f"fc-list検索エラー: {error}"
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

    log(
        "STEP FONT-5: 手動フォント検索"
    )

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

        log(
            f"フォントディレクトリ確認: {directory}"
        )

        log(
            f"directory exists: {directory.exists()}"
        )

        if not directory.exists():

            continue

        for font_name in preferred_fonts:

            log(
                f"手動フォント検索: {font_name}"
            )

            try:

                for match in directory.rglob(
                    font_name
                ):

                    log(
                        f"候補発見: {match}"
                    )

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

                log(
                    f"手動フォント検索エラー: {error}"
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
            "ERROR: color_nameがNone"
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
            "ERROR: 字幕カラーが未定義"
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
            "ERROR: ASSカラー値が未定義"
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
        "normalize_subtitle_settings開始"
    )

    log(
        f"input subtitle_settings: "
        f"{subtitle_settings}"
    )

    if subtitle_settings is None:

        log(
            "subtitle_settings=None"
        )

        log(
            "subtitle_font.pyからデフォルト設定取得開始"
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

    for key in SUBTITLE_SETTING_KEYS:

        log(
            f"正式設定キー確認: {key}"
        )

        if key in subtitle_settings:

            normalized[key] = (
                subtitle_settings.get(
                    key
                )
            )

            log(
                f"{key}: {normalized[key]}"
            )

        else:

            log(
                f"{key}: 入力設定にはありません"
            )

    log(
        f"正規化前: {normalized}"
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
        f"select_subtitle_font結果: {normalized}"
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
        f"最終subtitle_settings: {result}"
    )

    log(
        "normalize_subtitle_settings完了"
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
        "make_subtitle_filter開始"
    )

    log(
        f"srt_path: {srt_path}"
    )

    log(
        f"font_info: {font_info}"
    )

    log(
        f"subtitle_settings: {subtitle_settings}"
    )

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
    )

    log(
        f"normalized subtitle_settings: "
        f"{subtitle_settings}"
    )

    log(
        "字幕SRTパスエスケープ開始"
    )

    subtitle_path = (
        escape_ffmpeg_filter_path(
            srt_path
        )
    )

    log(
        f"escaped subtitle_path: {subtitle_path}"
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

    log(
        "字幕設定値取得開始"
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

    # ======================================================
    # 値確認
    # ======================================================

    log(
        "字幕設定値バリデーション開始"
    )

    if font is None:

        log(
            "ERROR: font=None"
        )

        raise RuntimeError(
            "字幕フォントが設定されていません。"
        )

    if text_color_name is None:

        log(
            "ERROR: text_color=None"
        )

        raise RuntimeError(
            "字幕文字色が設定されていません。"
        )

    if outline_color_name is None:

        log(
            "ERROR: outline_color=None"
        )

        raise RuntimeError(
            "字幕縁色が設定されていません。"
        )

    try:

        outline_width = int(
            outline_width
        )

        log(
            f"outline_width int変換後: {outline_width}"
        )

    except (
        ValueError,
        TypeError
    ) as error:

        log(
            f"ERROR: outline_width変換失敗: {error}"
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

        log(
            f"font_info.path: "
            f"{font_info.get('path')}"
        )

        log(
            f"font_info.family: "
            f"{font_info.get('family')}"
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

            log(
                f"detected_family: {detected_family}"
            )

            if (
                "Noto Sans CJK JP"
                in detected_family
                and
                len(detected_family)
                > 30
            ):

                log(
                    "検出familyが長すぎるためFontNameには使用しません"
                )

                font_name = None

            else:

                font_name = detected_family

    if not font_name:

        log(
            "検出familyを使用できないため設定fontを使用"
        )

        font_name = str(
            font
        ).strip()

    log(
        f"最終FontName: {font_name}"
    )

    if not font_name:

        log(
            "ERROR: FontName決定失敗"
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
                "WARNING: font_infoにpathがありません"
            )

    else:

        log(
            "font_infoなし。fontsdirは設定しません"
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
        f"escaped_font_name: {escaped_font_name}"
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
        "最終video_filter:"
    )

    log(
        video_filter
    )

    log(
        "make_subtitle_filter完了"
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
        f"保持ログ行数: {len(lines)}"
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
        f"resolved candidate path: {path}"
    )

    try:

        exists = path.exists()

        log(
            f"file exists: {exists}"
        )

        if exists:

            log(
                "ファイル削除開始"
            )

            path.unlink()

            log(
                f"ファイル削除完了: {path}"
            )

            log(
                f"削除後exists: {path.exists()}"
            )

        else:

            log(
                "削除対象ファイルは存在しません"
            )

    except Exception as error:

        log(
            f"一時ファイル削除失敗: {error}"
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
        "====================================="
    )

    log(
        "embed_subtitle開始"
    )

    log(
        f"raw mp4_path: {mp4_path}"
    )

    log(
        f"raw srt_path: {srt_path}"
    )

    log(
        f"raw output_path: {output_path}"
    )

    log(
        f"raw subtitle_settings: {subtitle_settings}"
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
        f"STEP 1完了: MP4={mp4_path}"
    )

    log(
        "STEP 2: SRT入力ファイル確認開始"
    )

    srt_path = validate_input_file(
        srt_path,
        ".srt"
    )

    log(
        f"STEP 2完了: SRT={srt_path}"
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
        "STEP 3完了: SRT UTF-8 OK"
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
        "STEP 4完了: 字幕設定正規化OK"
    )

    log(
        "字幕設定:"
    )

    log(
        str(
            subtitle_settings
        )
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
            f"raw output_path: {output_path}"
        )

        output_path = (
            Path(
                output_path
            ).resolve()
        )

        log(
            f"resolved output_path: {output_path}"
        )

    else:

        log(
            "output_path未指定"
        )

        log(
            "make_output_pathで自動生成します"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

        log(
            f"自動生成output_path: {output_path}"
        )

    log(
        "STEP 5完了: 出力先決定OK"
    )

    # ======================================================
    # 入力と出力が同じにならないようにする
    # ======================================================

    log(
        "STEP 6: 入力/出力パス同一性確認"
    )

    log(
        f"mp4_path: {mp4_path}"
    )

    log(
        f"output_path: {output_path}"
    )

    log(
        f"same path: {output_path == mp4_path}"
    )

    if output_path == mp4_path:

        log(
            "WARNING: 入力と出力が同じです"
        )

        log(
            "別の出力パスを生成します"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

        log(
            f"変更後output_path: {output_path}"
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

    log(
        f"parent exists before mkdir: "
        f"{output_path.parent.exists()}"
    )

    try:

        output_path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        log(
            "出力フォルダmkdir完了"
        )

        log(
            f"parent exists after mkdir: "
            f"{output_path.parent.exists()}"
        )

        log(
            f"parent is_dir: "
            f"{output_path.parent.is_dir()}"
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
        "STEP 7完了: 出力フォルダOK"
    )

    # ======================================================
    # FFmpeg確認
    # ======================================================

    log(
        "STEP 8: FFmpeg確認開始"
    )

    ffmpeg_path = check_ffmpeg()

    log(
        f"STEP 8完了: FFmpeg={ffmpeg_path}"
    )

    # ======================================================
    # 正式名称:
    #   font
    # ======================================================

    log(
        "STEP 9: 字幕フォント設定取得"
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
        f"font_info検索結果: {font_info}"
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
        "STEP 10完了: フォント検索処理終了"
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

        log(
            f"入力MP4サイズ: "
            f"{input_mp4_size} bytes"
        )

    except OSError as error:

        log(
            f"WARNING: 入力MP4サイズ取得失敗: {error}"
        )

        input_mp4_size = 0

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
            "WARNING: 生成した一時出力パスが既に存在します"
        )

    else:

        log(
            "一時出力パスは未使用です"
        )

    log(
        "STEP 13完了"
    )

    # ======================================================
    # ログ
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
        f"FFmpeg command item count: {len(command)}"
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

    log(
        command_to_string(
            command
        )
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
        f"stderr=PIPE: True"
    )

    log(
        f"stdout=DEVNULL: True"
    )

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

    except OSError as error:

        log(
            f"ERROR: FFmpeg Popen失敗: {error}"
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
        "STEP 15完了: FFmpeg subprocess起動OK"
    )

    # ======================================================
    # 最後の100行だけ保持
    # ======================================================

    ffmpeg_output_lines = deque(

        maxlen=MAX_FFMPEG_LOG_LINES

    )

    log(
        f"FFmpegログ保持数: max={MAX_FFMPEG_LOG_LINES}"
    )

    # ======================================================
    # FFmpegログ取得
    # ======================================================

    log(
        "STEP 16: FFmpeg stderrログ取得開始"
    )

    stderr_line_count = 0

    stderr_read_start = time.monotonic()

    try:

        if process.stderr:

            log(
                "process.stderrが存在します"
            )

            log(
                "FFmpeg stderr for-loop開始"
            )

            for line in process.stderr:

                stderr_line_count += 1

                line = line.rstrip()

                if not line:

                    continue

                ffmpeg_output_lines.append(
                    line
                )

                print(
                    "[FFMPEG]",
                    line,
                    flush=True
                )

                # 進行監視用。
                # 大量ログによる負荷を抑えるため、
                # 100行ごとにSUBTITLEログを出す。
                if stderr_line_count % 100 == 0:

                    log(
                        f"FFmpeg stderr読み込み中: "
                        f"{stderr_line_count} lines"
                    )

                    log(
                        f"FFmpeg poll: "
                        f"{process.poll()}"
                    )

                    log(
                        f"temp output exists: "
                        f"{temp_output_path.exists()}"
                    )

        else:

            log(
                "WARNING: process.stderrがNoneです"
            )

        stderr_read_elapsed = (
            time.monotonic()
            -
            stderr_read_start
        )

        log(
            "FFmpeg stderr EOF"
        )

        log(
            f"FFmpeg stderr総読み込み行数: "
            f"{stderr_line_count}"
        )

        log(
            f"stderr読み込み経過時間: "
            f"{format_elapsed_time(stderr_read_elapsed)}"
        )

        log(
            f"FFmpeg poll after stderr EOF: "
            f"{process.poll()}"
        )

        log(
            f"temp output exists after stderr EOF: "
            f"{temp_output_path.exists()}"
        )

    except Exception as error:

        log(
            "ERROR: FFmpegログ取得中に例外発生"
        )

        log(
            f"exception type: {type(error).__name__}"
        )

        log(
            f"exception: {error}"
        )

        log(
            f"stderr line count: {stderr_line_count}"
        )

        try:

            log(
                "FFmpeg kill開始"
            )

            process.kill()

            log(
                "FFmpeg kill完了"
            )

        except Exception as kill_error:

            log(
                f"FFmpeg kill失敗: {kill_error}"
            )

        try:

            log(
                "FFmpeg wait開始"
            )

            wait_result = process.wait()

            log(
                f"FFmpeg wait完了: {wait_result}"
            )

        except Exception as wait_error:

            log(
                f"FFmpeg wait失敗: {wait_error}"
            )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "FFmpegログ取得中のエラー: "
            +
            str(error)

        ) from error

    finally:

        log(
            "STEP 16 finally開始"
        )

        if process.stderr:

            try:

                log(
                    "process.stderr.close()開始"
                )

                process.stderr.close()

                log(
                    "process.stderr.close()完了"
                )

            except Exception as error:

                log(
                    f"process.stderr.close()失敗: {error}"
                )

        log(
            "STEP 16 finally完了"
        )

    log(
        "STEP 16完了: FFmpeg stderrログ取得終了"
    )

    # ======================================================
    # FFmpeg終了
    # ======================================================

    log(
        "STEP 17: FFmpeg終了状態確認開始"
    )

    log(
        f"FFmpeg PID: {process.pid}"
    )

    log(
        f"process.poll() before wait: "
        f"{process.poll()}"
    )

    wait_start = time.monotonic()

    try:

        log(
            "process.wait()開始"
        )

        return_code = process.wait()

        wait_elapsed = (
            time.monotonic()
            -
            wait_start
        )

        log(
            "process.wait()完了"
        )

        log(
            f"FFmpeg return code: {return_code}"
        )

        log(
            f"wait経過時間: "
            f"{format_elapsed_time(wait_elapsed)}"
        )

        log(
            f"process.poll() after wait: "
            f"{process.poll()}"
        )

    except Exception as error:

        log(
            "ERROR: FFmpeg wait失敗"
        )

        log(
            f"exception type: {type(error).__name__}"
        )

        log(
            f"exception: {error}"
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
        "STEP 17完了"
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
        "STEP 18: 処理時間計算"
    )

    log(
        "FFmpeg処理を含む現在までの経過時間: "
        +
        format_elapsed_time(
            elapsed_time
        )
    )

    # ======================================================
    # FFmpegエラー
    # ======================================================

    log(
        "STEP 19: FFmpeg return code確認"
    )

    log(
        f"return_code: {return_code}"
    )

    if return_code != 0:

        log(
            f"FFmpegエラー: "
            f"return code={return_code}"
        )

        log(
            "FFmpeg保持ログからエラー詳細生成開始"
        )

        error_detail = (
            make_ffmpeg_error_detail(
                ffmpeg_output_lines
            )
        )

        log(
            "FFmpegエラー詳細生成完了"
        )

        log(
            f"error detail length: "
            f"{len(error_detail)}"
        )

        log(
            "一時出力削除開始"
        )

        remove_file_safely(
            temp_output_path
        )

        log(
            "一時出力削除処理完了"
        )

        raise RuntimeError(

            "字幕焼き込みに失敗しました。"
            "\n\n"
            +
            error_detail
            +
            "\n\n"
            +
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            )

        )

    log(
        "STEP 19完了: FFmpeg正常終了"
    )

    # ======================================================
    # 一時出力確認
    # ======================================================

    log(
        "STEP 20: 一時出力ファイル確認開始"
    )

    log(
        f"temp_output_path: {temp_output_path}"
    )

    log(
        f"temp exists: {temp_output_path.exists()}"
    )

    log(
        f"temp is_file: {temp_output_path.is_file()}"
    )

    if not temp_output_path.exists():

        log(
            "ERROR: FFmpeg正常終了したが一時出力が存在しません"
        )

        log(
            f"parent directory exists: "
            f"{temp_output_path.parent.exists()}"
        )

        try:

            log(
                "出力フォルダ一覧確認開始"
            )

            if temp_output_path.parent.exists():

                for item in temp_output_path.parent.iterdir():

                    log(
                        f"OUTPUT DIR ITEM: {item}"
                    )

            log(
                "出力フォルダ一覧確認完了"
            )

        except Exception as error:

            log(
                f"出力フォルダ一覧取得失敗: {error}"
            )

        raise RuntimeError(

            "FFmpegは正常終了しましたが、"
            "一時出力ファイルが作成されていません。"

        )

    if not temp_output_path.is_file():

        log(
            "ERROR: 一時出力パスがファイルではありません"
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(

            "FFmpegの一時出力先が"
            "ファイルではありません。"

        )

    log(
        "一時出力ファイル存在確認OK"
    )

    # ======================================================
    # 一時ファイルサイズ
    # ======================================================

    log(
        "STEP 21: 一時出力ファイルサイズ確認開始"
    )

    try:

        output_size = (
            temp_output_path.stat().st_size
        )

        log(
            f"一時出力サイズ: {output_size} bytes"
        )

    except OSError as error:

        log(
            f"ERROR: 一時出力stat失敗: {error}"
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

    if output_size <= 0:

        log(
            "ERROR: 一時出力サイズが0です"
        )

        remove_file_safely(
            temp_output_path
        )

        raise RuntimeError(
            "FFmpeg出力ファイルのサイズが0です。"
        )

    log(
        "一時出力サイズ確認OK"
    )

    log(
        f"入力サイズ: {input_mp4_size} bytes"
    )

    log(
        f"一時出力サイズ: {output_size} bytes"
    )

    if input_mp4_size > 0:

        size_ratio = (
            output_size
            /
            input_mp4_size
        )

        log(
            f"出力/入力サイズ比: "
            f"{size_ratio:.3f}"
        )

    log(
        "STEP 21完了"
    )

    # ======================================================
    # 正式出力が存在する場合
    # ======================================================

    log(
        "STEP 22: 既存正式出力確認開始"
    )

    log(
        f"output_path: {output_path}"
    )

    log(
        f"output exists: {output_path.exists()}"
    )

    log(
        f"output is_file: {output_path.is_file()}"
    )

    if output_path.exists():

        log(
            "既存の正式出力があります"
        )

        try:

            existing_size = (
                output_path.stat().st_size
            )

            log(
                f"既存正式出力サイズ: "
                f"{existing_size} bytes"
            )

        except OSError as error:

            log(
                f"既存正式出力サイズ取得失敗: {error}"
            )

        log(
            "既存の正式出力を削除:"
        )

        log(
            str(
                output_path
            )
        )

        try:

            log(
                "output_path.unlink()開始"
            )

            output_path.unlink()

            log(
                "output_path.unlink()完了"
            )

            log(
                f"削除後output exists: "
                f"{output_path.exists()}"
            )

        except OSError as error:

            log(
                f"ERROR: 既存出力削除失敗: {error}"
            )

            log(
                "一時出力削除開始"
            )

            remove_file_safely(
                temp_output_path
            )

            log(
                "一時出力削除完了"
            )

            raise RuntimeError(

                "既存の出力ファイルを"
                "削除できませんでした: "
                +
                str(error)

            ) from error

    else:

        log(
            "既存の正式出力はありません"
        )

    log(
        "STEP 22完了"
    )

    # ======================================================
    # 一時ファイルを正式ファイルへ移動
    # ======================================================

    log(
        "STEP 23: 一時ファイル→正式ファイル移動開始"
    )

    log(
        f"source temp: {temp_output_path}"
    )

    log(
        f"source exists before replace: "
        f"{temp_output_path.exists()}"
    )

    log(
        f"destination: {output_path}"
    )

    log(
        f"destination exists before replace: "
        f"{output_path.exists()}"
    )

    log(
        "os.replace()開始"
    )

    replace_start = time.monotonic()

    try:

        os.replace(

            str(
                temp_output_path
            ),

            str(
                output_path
            )

        )

        replace_elapsed = (
            time.monotonic()
            -
            replace_start
        )

        log(
            "os.replace()完了"
        )

        log(
            f"os.replace()経過時間: "
            f"{format_elapsed_time(replace_elapsed)}"
        )

        log(
            f"source exists after replace: "
            f"{temp_output_path.exists()}"
        )

        log(
            f"destination exists after replace: "
            f"{output_path.exists()}"
        )

    except OSError as error:

        replace_elapsed = (
            time.monotonic()
            -
            replace_start
        )

        log(
            "ERROR: os.replace()失敗"
        )

        log(
            f"replace error type: "
            f"{type(error).__name__}"
        )

        log(
            f"replace error: {error}"
        )

        log(
            f"os.replace()失敗までの時間: "
            f"{format_elapsed_time(replace_elapsed)}"
        )

        log(
            f"temp exists after replace failure: "
            f"{temp_output_path.exists()}"
        )

        log(
            f"output exists after replace failure: "
            f"{output_path.exists()}"
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
        "STEP 23完了: 正式ファイル移動OK"
    )

    # ======================================================
    # 最終確認
    # ======================================================

    log(
        "STEP 24: 正式出力ファイル最終確認開始"
    )

    log(
        f"final output_path: {output_path}"
    )

    log(
        f"final exists: {output_path.exists()}"
    )

    log(
        f"final is_file: {output_path.is_file()}"
    )

    log(
        f"temp exists: {temp_output_path.exists()}"
    )

    if not output_path.exists():

        log(
            "ERROR: os.replace後も正式出力が存在しません"
        )

        raise RuntimeError(

            "正式な字幕MP4が"
            "作成されていません。"

        )

    if not output_path.is_file():

        log(
            "ERROR: 正式出力パスがファイルではありません"
        )

        raise RuntimeError(

            "正式出力先がファイルではありません。"

        )

    log(
        "正式出力ファイル存在確認OK"
    )

    # ======================================================
    # 最終サイズ確認
    # ======================================================

    log(
        "STEP 25: 正式出力ファイルサイズ確認開始"
    )

    try:

        final_size = (
            output_path.stat().st_size
        )

        log(
            f"正式出力サイズ: {final_size} bytes"
        )

    except OSError as error:

        log(
            f"ERROR: 正式出力stat失敗: {error}"
        )

        raise RuntimeError(

            "正式出力ファイルを"
            "確認できませんでした: "
            +
            str(error)

        ) from error

    if final_size <= 0:

        log(
            "ERROR: 正式出力ファイルサイズが0です"
        )

        remove_file_safely(
            output_path
        )

        raise RuntimeError(
            "正式出力ファイルのサイズが0です。"
        )

    log(
        "正式出力ファイルサイズ確認OK"
    )

    if final_size != output_size:

        log(
            "WARNING: 一時出力と正式出力のサイズが異なります"
        )

        log(
            f"temp size: {output_size}"
        )

        log(
            f"final size: {final_size}"
        )

    else:

        log(
            "一時出力と正式出力のサイズ一致"
        )

    log(
        "STEP 25完了"
    )

    # ======================================================
    # 最終パス確認
    # ======================================================

    log(
        "STEP 26: 最終ファイルパス確認"
    )

    try:

        final_resolved = (
            output_path.resolve()
        )

        log(
            f"final resolved path: {final_resolved}"
        )

    except Exception as error:

        log(
            f"WARNING: final resolve失敗: {error}"
        )

        final_resolved = output_path

    log(
        f"final parent: {output_path.parent}"
    )

    log(
        f"final filename: {output_path.name}"
    )

    # ======================================================
    # 完了
    # ======================================================

    elapsed_time = (

        time.monotonic()
        -
        start_time

    )

    log(
        "STEP 27: 字幕焼き込み完了処理"
    )

    log(
        "字幕焼き込み完了"
    )

    log(
        f"出力ファイル: "
        f"{output_path}"
    )

    log(
        f"出力ファイル存在: "
        f"{output_path.exists()}"
    )

    log(
        f"出力ファイルサイズ: "
        f"{final_size} bytes"
    )

    log(
        "処理時間: "
        +
        format_elapsed_time(
            elapsed_time
        )
    )

    log(
        "一時ファイル残存確認:"
    )

    log(
        f"{temp_output_path} "
        f"exists={temp_output_path.exists()}"
    )

    log(
        "====================================="
    )

    log(
        "embed_subtitle完了"
    )

    log(
        "====================================="
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
        f"mp4_path: {mp4_path}"
    )

    log(
        f"srt_path: {srt_path}"
    )

    log(
        f"output_path: {output_path}"
    )

    log(
        f"subtitle_settings: {subtitle_settings}"
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
        "embed_from_downloads開始"
    )

    log(
        f"raw mp4_filename: {mp4_filename}"
    )

    log(
        f"raw srt_filename: {srt_filename}"
    )

    log(
        f"subtitle_settings: {subtitle_settings}"
    )

    mp4_filename = Path(
        mp4_filename
    ).name

    srt_filename = Path(
        srt_filename
    ).name

    log(
        f"sanitized mp4_filename: {mp4_filename}"
    )

    log(
        f"sanitized srt_filename: {srt_filename}"
    )

    log(
        f"DOWNLOADS_DIR: {DOWNLOADS_DIR}"
    )

    log(
        f"DOWNLOADS_DIR exists before mkdir: "
        f"{DOWNLOADS_DIR.exists()}"
    )

    DOWNLOADS_DIR.mkdir(

        parents=True,

        exist_ok=True

    )

    log(
        f"DOWNLOADS_DIR exists after mkdir: "
        f"{DOWNLOADS_DIR.exists()}"
    )

    log(
        f"DOWNLOADS_DIR is_dir: "
        f"{DOWNLOADS_DIR.is_dir()}"
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
        f"MP4 exists: {mp4_path.exists()}"
    )

    log(
        f"SRT exists: {srt_path.exists()}"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        subtitle_settings=subtitle_settings

    )

    log(
        f"embed_from_downloads完了: {result}"
    )

    return result


# ==========================================================
# コマンドライン
# ==========================================================

def main():

    log(
        "main開始"
    )

    log(
        f"sys.argv: {sys.argv}"
    )

    log(
        f"argc: {len(sys.argv)}"
    )

    if len(sys.argv) < 3:

        log(
            "ERROR: 引数不足"
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
        f"CLI MP4: {mp4_filename}"
    )

    log(
        f"CLI SRT: {srt_filename}"
    )

    start_time = time.monotonic()

    try:

        # ==================================================
        # subtitle_font.pyから標準設定を取得
        # ==================================================

        log(
            "CLI STEP 1: subtitle_font.py標準設定取得開始"
        )

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

        log(
            "CLI STEP 1完了"
        )

        log(
            f"subtitle_settings: {subtitle_settings}"
        )

        log(
            "CLI STEP 2: embed_from_downloads開始"
        )

        output_path = (
            embed_from_downloads(

                mp4_filename,

                srt_filename,

                subtitle_settings

            )
        )

        log(
            "CLI STEP 2完了"
        )

        log(
            f"output_path: {output_path}"
        )

        elapsed_time = (

            time.monotonic()
            -
            start_time

        )

        log(
            f"CLI総処理時間: "
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
            f"出力ファイル存在: "
            f"{output_path.exists()}"
        )

        try:

            print(
                f"出力ファイルサイズ: "
                f"{output_path.stat().st_size} bytes"
            )

        except Exception as error:

            print(
                f"出力ファイルサイズ取得失敗: {error}"
            )

        print(
            "====================================="
        )

        print()

        log(
            "main正常終了: return 0"
        )

        return 0

    except Exception as error:

        elapsed_time = (

            time.monotonic()
            -
            start_time

        )

        log(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )

        log(
            "mainで例外発生"
        )

        log(
            f"exception type: {type(error).__name__}"
        )

        log(
            f"exception: {error}"
        )

        log(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        log(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
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
            "main異常終了: return 1"
        )

        return 1


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    log(
        "subtitle.py __main__開始"
    )

    result = main()

    log(
        f"subtitle.py __main__終了: exit_code={result}"
    )

    sys.exit(
        result
    )
