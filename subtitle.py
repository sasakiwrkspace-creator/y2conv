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
#
# 重要:
#
# subtitle.pyでは
#
#   color
#   textColor
#   outlineColor
#   stroke_color
#   strokeColor
#   outlineWidth
#   strokeWidth
#
# などの別名を使用しない。
#
# それらの表記ゆれを吸収する責任は
# subtitle_routes.py側に限定する。
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

# Render低メモリ環境向け
FFMPEG_THREADS = "1"

# エンコード速度優先
FFMPEG_PRESET = "ultrafast"

# 画質
FFMPEG_CRF = "23"


# ==========================================================
# 共通設定キー
#
# subtitle_font.py / subtitle_routes.py / subtitle.py
# で使用する正式名称。
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
# 例外ログ
# ==========================================================

def log_exception(
    message,
    error=None
):

    log(
        f"ERROR: {message}"
    )

    if error is not None:

        log(
            f"ERROR TYPE: {type(error).__name__}"
        )

        log(
            f"ERROR MESSAGE: {error}"
        )

    try:

        traceback.print_exc()

    except Exception:

        pass


# ==========================================================
# 処理時間
# ==========================================================

def format_elapsed_time(seconds):

    log(
        f"format_elapsed_time開始: seconds={seconds!r}"
    )

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

        log(
            "format_elapsed_time: "
            "seconds変換失敗。0秒として処理します。"
        )

        seconds = 0

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = (
        seconds % 60
    )

    result = (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )

    log(
        f"format_elapsed_time完了: {result}"
    )

    return result


# ==========================================================
# 入力ファイル確認
# ==========================================================

def validate_input_file(
    file_path,
    extension
):

    log(
        "====================================="
    )

    log(
        "validate_input_file開始"
    )

    log(
        f"file_path: {file_path!r}"
    )

    log(
        f"expected extension: {extension!r}"
    )

    try:

        path = Path(
            file_path
        ).resolve()

    except Exception as error:

        log_exception(
            "Path生成・resolveに失敗しました。",
            error
        )

        raise

    log(
        f"resolved path: {path}"
    )

    if not path.exists():

        log(
            f"ファイル不存在: {path}"
        )

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    log(
        "ファイル存在確認OK"
    )

    if not path.is_file():

        log(
            f"ファイルではありません: {path}"
        )

        raise ValueError(
            f"ファイルではありません: {path}"
        )

    log(
        "通常ファイル確認OK"
    )

    actual_suffix = path.suffix.lower()

    log(
        f"actual suffix: {actual_suffix}"
    )

    if actual_suffix != extension.lower():

        log(
            "拡張子チェック失敗"
        )

        raise ValueError(
            f"{extension} ファイルではありません: {path}"
        )

    log(
        "拡張子チェックOK"
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
        f"ファイルサイズ: {size} bytes"
    )

    if size <= 0:

        log(
            "ファイルサイズが0 bytes以下です"
        )

        raise ValueError(
            f"ファイルが0 bytesです: {path}"
        )

    log(
        "validate_input_file完了"
    )

    log(
        "====================================="
    )

    return path


# ==========================================================
# 出力ファイル名
#
# video.mp4
#   -> video_sub_embed.mp4
#
# video_sub_embed.mp4
#   -> video_sub_embed_2.mp4
#
# ==========================================================

def make_output_path(
    mp4_path
):

    log(
        "make_output_path開始"
    )

    log(
        f"input mp4_path: {mp4_path!r}"
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
            "入力ファイル名が_sub_embedで終わっています"
        )

    else:

        candidate = (
            mp4_path.parent
            /
            f"{stem}{base_suffix}.mp4"
        )

        log(
            "通常の_sub_embed出力名を生成しました"
        )

    counter = 2

    log(
        f"初期候補: {candidate}"
    )

    while candidate.exists():

        log(
            f"出力候補が既に存在します: {candidate}"
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
        f"output_path: {output_path!r}"
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

    log(
        f"PATH: {os.environ.get('PATH', '')}"
    )

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    log(
        f"shutil.which('ffmpeg'): {ffmpeg_path!r}"
    )

    if not ffmpeg_path:

        log(
            "ERROR: FFmpegがPATH上に存在しません"
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

    except FileNotFoundError as error:

        log_exception(
            "FFmpeg起動時にFileNotFoundErrorが発生しました。",
            error
        )

        raise RuntimeError(
            "FFmpegが見つかりません。"
        ) from error

    except subprocess.TimeoutExpired as error:

        log_exception(
            "FFmpegバージョン確認がタイムアウトしました。",
            error
        )

        raise RuntimeError(
            "FFmpegの確認がタイムアウトしました。"
        ) from error

    except OSError as error:

        log_exception(
            "FFmpegバージョン確認でOSエラーが発生しました。",
            error
        )

        raise RuntimeError(
            f"FFmpegを起動できません: {error}"
        ) from error

    log(
        f"FFmpeg version returncode: {result.returncode}"
    )

    log(
        f"FFmpeg version stdout length: "
        f"{len(result.stdout or '')}"
    )

    log(
        f"FFmpeg version stderr length: "
        f"{len(result.stderr or '')}"
    )

    if result.returncode != 0:

        log(
            "FFmpeg -version が失敗しました"
        )

        if result.stderr:

            log(
                f"FFmpeg version stderr: {result.stderr[-2000:]}"
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

    log(
        "====================================="
    )

    return ffmpeg_path


# ==========================================================
# SRT UTF-8確認
#
# SRT全体はメモリへ読み込まない。
# ==========================================================

def validate_srt_encoding(
    srt_path
):

    log(
        "====================================="
    )

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
                "SRTファイルをUTF-8-sigで開きました"
            )

            first_content = file.read(
                4096
            )

            log(
                f"SRT先頭読み込み完了: "
                f"{len(first_content)} chars"
            )

    except UnicodeDecodeError as error:

        log_exception(
            "SRT UTF-8デコードに失敗しました。",
            error
        )

        raise RuntimeError(

            "SRTファイルをUTF-8として"
            "読み込めませんでした。"
            "SRTをUTF-8形式で保存してください。"

        ) from error

    except OSError as error:

        log_exception(
            "SRTファイルを開けませんでした。",
            error
        )

        raise RuntimeError(

            f"SRTファイルを読み込めませんでした: {error}"

        ) from error

    if not first_content.strip():

        log(
            "SRT先頭4096文字が空です"
        )

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    log(
        "SRT内容確認OK"
    )

    try:

        srt_size = (
            srt_path.stat().st_size
        )

    except OSError as error:

        log(
            f"SRTサイズ取得失敗: {error}"
        )

        srt_size = 0

    log(
        f"SRTサイズ: {srt_size} bytes"
    )

    log(
        "validate_srt_encoding完了"
    )

    log(
        "====================================="
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
        f"fc-scan: {fc_scan!r}"
    )

    if not fc_scan:

        log(
            "fc-scanが見つかりません"
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
            "fc-scan実行に失敗しました。",
            error
        )

        return None

    log(
        f"fc-scan returncode: {result.returncode}"
    )

    if result.stderr:

        log(
            f"fc-scan stderr: {result.stderr[-1000:]}"
        )

    if result.returncode != 0:

        log(
            "fc-scanが失敗しました"
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

        log(
            f"複数family形式を検出: {family}"
        )

        family = (
            family.split(
                ",",
                1
            )[0].strip()
        )

    family = family or None

    log(
        f"最終font family: {family!r}"
    )

    return family


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
        f"requested_font: {requested_font!r}"
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
        f"fc-match: {fc_match!r}"
    )

    if not fc_match:

        log(
            "fc-matchが見つかりません"
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
            "fc-match実行に失敗しました。",
            error
        )

        return None

    log(
        f"fc-match returncode: {result.returncode}"
    )

    if result.stderr:

        log(
            f"fc-match stderr: {result.stderr[-1000:]}"
        )

    if result.returncode != 0:

        log(
            "fc-matchが失敗しました"
        )

        return None

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:

            continue

        log(
            f"fc-match candidate: {line}"
        )

        font_path = Path(
            line
        )

        if not font_path.is_file():

            log(
                f"fc-match結果がファイルではありません: {font_path}"
            )

            continue

        family = (
            get_font_family_from_path(
                font_path
            )
        )

        log(
            f"fc-match最終選択: path={font_path}, family={family}"
        )

        return {

            "path":
                font_path.resolve(),

            "family":
                family

        }

    log(
        "fc-matchから有効なフォントファイルを取得できませんでした"
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
        f"requested_font: {requested_font!r}"
    )

    # ======================================================
    # 1. SUBTITLE_FONT
    # ======================================================

    log(
        "フォント検索[1]: SUBTITLE_FONT確認"
    )

    environment_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    log(
        f"SUBTITLE_FONT: {environment_font!r}"
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

        if environment_font_path.is_file():

            family = (
                get_font_family_from_path(
                    environment_font_path
                )
            )

            log(
                "環境変数指定フォントを使用します"
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
    #
    # 正式名称:
    #   font
    # ======================================================

    log(
        "フォント検索[2]: subtitle_font.pyのfont確認"
    )

    if requested_font:

        requested_font = str(
            requested_font
        ).strip()

        log(
            f"requested_font normalized: "
            f"{requested_font!r}"
        )

        requested_path = (
            Path(
                requested_font
            ).expanduser()
        )

        log(
            f"requested_path: {requested_path}"
        )

        # ファイルパス指定
        if requested_path.is_file():

            requested_path = (
                requested_path.resolve()
            )

            log(
                "指定フォントファイルが存在します"
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
            "指定されたfontは直接ファイルパスではありません"
        )

        # fc-match
        log(
            "fc-matchによるfont検索開始"
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
            "指定fontのfc-matchに失敗しました"
        )

    else:

        log(
            "requested_fontが指定されていません"
        )

    # ======================================================
    # 3. 日本語フォント候補
    # ======================================================

    log(
        "フォント検索[3]: 日本語フォント候補"
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
            f"日本語フォント候補検索: {family_name}"
        )

        matched = fc_match_font(
            family_name
        )

        if not matched:

            log(
                f"候補なし: {family_name}"
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
        "フォント検索[4]: fc-list"
    )

    fc_list = shutil.which(
        "fc-list"
    )

    log(
        f"fc-list: {fc_list!r}"
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
                "fc-list検索で例外が発生しました。",
                error
            )

            result = None

        if result and result.returncode == 0:

            log(
                "fc-list実行成功"
            )

            lines = result.stdout.splitlines()

            log(
                f"fc-list候補行数: {len(lines)}"
            )

            for line in lines:

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

        elif result:

            log(
                f"fc-list失敗: returncode={result.returncode}"
            )

            if result.stderr:

                log(
                    f"fc-list stderr: "
                    f"{result.stderr[-2000:]}"
                )

    else:

        log(
            "fc-listが見つかりません"
        )

    # ======================================================
    # 5. 手動検索
    # ======================================================

    log(
        "フォント検索[5]: 手動検索"
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

            log(
                f"手動フォント検索: "
                f"{directory} / {font_name}"
            )

            try:

                for match in directory.rglob(
                    font_name
                ):

                    if not match.is_file():

                        continue

                    log(
                        f"手動検索で候補発見: {match}"
                    )

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
                    f"手動フォント検索エラー: "
                    f"directory={directory}, "
                    f"font={font_name}, "
                    f"error={error}"
                )

                continue

    log(
        "日本語フォントが見つかりませんでした。"
    )

    log(
        "日本語フォント検索終了: None"
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
        f"original path: {file_path!r}"
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

    return value


# ==========================================================
# ASSカラー取得
#
# 色の定義はsubtitle_font.pyだけを見る。
#
# subtitle.pyでは
#   白
#   青
#   黒
# などのカラー設定値を定義しない。
# ==========================================================

def get_ass_color(
    color_name
):

    log(
        "get_ass_color開始"
    )

    log(
        f"color_name: {color_name!r}"
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
        f"color_info: {color_info!r}"
    )

    if not color_info:

        log(
            f"未定義カラー: {color_name}"
        )

        raise RuntimeError(
            f"字幕カラーが定義されていません: "
            f"{color_name}"
        )

    ass_color = color_info.get(
        "ass"
    )

    log(
        f"ASS color: {ass_color!r}"
    )

    if not ass_color:

        log(
            "ASSカラー値が空です"
        )

        raise RuntimeError(
            f"字幕カラーのASS値が定義されていません: "
            f"{color_name}"
        )

    result = str(
        ass_color
    )

    log(
        f"get_ass_color完了: {result}"
    )

    return result


# ==========================================================
# 字幕設定正規化
#
# ==========================================================
#
# subtitle.pyに入ってくる設定は、
# subtitle_routes.pyを経由する場合も、
# CLIから直接来る場合も、
# subtitle_font.pyを唯一の正規化元とする。
#
# 正式名称:
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
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
        f"input subtitle_settings: "
        f"{subtitle_settings!r}"
    )

    if subtitle_settings is None:

        log(
            "subtitle_settings=None"
        )

        log(
            "get_default_subtitle_font_settings()を呼び出します"
        )

        result = (
            get_default_subtitle_font_settings()
        )

        log(
            f"default settings result: {result!r}"
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
            f"subtitle_settings type error: "
            f"{type(subtitle_settings).__name__}"
        )

        raise TypeError(
            "subtitle_settingsはdictで指定してください。"
        )

    log(
        "subtitle_settingsはdictです"
    )

    # ======================================================
    # 正式名称だけを使用
    #
    # 別名はsubtitle_routes.pyで吸収済み。
    # ======================================================

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
                f"設定あり: {key}="
                f"{normalized[key]!r}"
            )

        else:

            log(
                f"設定なし: {key}"
            )

    log(
        f"subtitle_font.pyへ渡すnormalized: "
        f"{normalized!r}"
    )

    # ======================================================
    # subtitle_font.py側で正規化
    # ======================================================

    log(
        "subtitle_font.select_subtitle_font import開始"
    )

    from subtitle_font import select_subtitle_font

    log(
        "select_subtitle_font import完了"
    )

    log(
        "select_subtitle_font()呼び出し開始"
    )

    normalized = (
        select_subtitle_font(
            settings=normalized
        )
    )

    log(
        f"select_subtitle_font result: "
        f"{normalized!r}"
    )

    # ======================================================
    # 最終的に正式名称5つだけを保証
    # ======================================================

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
        "最終正規化設定:"
    )

    for key in SUBTITLE_SETTING_KEYS:

        log(
            f"  {key}: {result.get(key)!r}"
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
        f"font_info: {font_info!r}"
    )

    log(
        f"subtitle_settings input: "
        f"{subtitle_settings!r}"
    )

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
    )

    log(
        f"subtitle_settings normalized: "
        f"{subtitle_settings!r}"
    )

    subtitle_path = (
        escape_ffmpeg_filter_path(
            srt_path
        )
    )

    log(
        f"escaped subtitle path: {subtitle_path}"
    )

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )

    log(
        f"base video_filter: {video_filter}"
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
        f"preset_name: {preset_name!r}"
    )

    log(
        f"font: {font!r}"
    )

    log(
        f"text_color: {text_color_name!r}"
    )

    log(
        f"outline_color: {outline_color_name!r}"
    )

    log(
        f"outline_width: {outline_width!r}"
    )

    # ======================================================
    # 値確認
    # ======================================================

    log(
        "字幕設定値の検証開始"
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

    except (
        ValueError,
        TypeError
    ) as error:

        log_exception(
            "outline_widthをintへ変換できませんでした。",
            error
        )

        raise RuntimeError(
            "字幕縁太さが不正です。"
        ) from error

    log(
        f"outline_width int変換後: {outline_width}"
    )

    if outline_width < 0:

        log(
            "outline_widthが0未満です"
        )

        raise RuntimeError(
            "字幕縁太さが0未満です。"
        )

    if outline_width > 10:

        log(
            "outline_widthが10を超えています"
        )

        raise RuntimeError(
            "字幕縁太さが10を超えています。"
        )

    log(
        "字幕設定値の検証OK"
    )

    # ======================================================
    # ASSカラー
    #
    # デフォルト値はここでは設定しない。
    # ======================================================

    log(
        "文字色ASS値取得開始"
    )

    text_color = get_ass_color(
        text_color_name
    )

    log(
        f"text_color ASS: {text_color}"
    )

    log(
        "縁色ASS値取得開始"
    )

    outline_color = get_ass_color(
        outline_color_name
    )

    log(
        f"outline_color ASS: {outline_color}"
    )

    # ======================================================
    # FontName
    #
    # 実際に存在するフォントを検出した場合は、
    # そのfamilyを使用。
    # ======================================================

    log(
        "FontName決定開始"
    )

    font_name = None

    if font_info:

        log(
            "font_infoが存在します"
        )

        detected_family = (
            font_info.get(
                "family"
            )
        )

        log(
            f"detected_family: {detected_family!r}"
        )

        if detected_family:

            detected_family = str(
                detected_family
            ).strip()

            log(
                f"detected_family normalized: "
                f"{detected_family!r}"
            )

            # 明らかに複数familyが
            # 連結されている場合は使用しない。
            if (
                "Noto Sans CJK JP"
                in detected_family
                and
                len(detected_family)
                > 30
            ):

                log(
                    "検出familyが不自然に長いため"
                    "FontNameには使用しません"
                )

                font_name = None

            else:

                font_name = detected_family

        else:

            log(
                "font_info.familyが空です"
            )

    else:

        log(
            "font_infoがNoneです"
        )

    if not font_name:

        font_name = str(
            font
        ).strip()

        log(
            f"設定fontからFontNameを決定: "
            f"{font_name!r}"
        )

    if not font_name:

        log(
            "FontNameを決定できませんでした"
        )

        raise RuntimeError(
            "字幕フォント名を決定できませんでした。"
        )

    log(
        f"最終FontName: {font_name}"
    )

    # ======================================================
    # fontsdir
    #
    # 実際に検出したフォントのディレクトリのみ。
    # ======================================================

    if font_info:

        log(
            "fontsdir設定開始"
        )

        font_path = font_info.get(
            "path"
        )

        log(
            f"font_info.path: {font_path!r}"
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
                "font_info.pathがありません。"
                "fontsdirは追加しません"
            )

    else:

        log(
            "font_infoがNoneのためfontsdirは追加しません"
        )

    # ======================================================
    # ASS force_style
    # ======================================================

    log(
        "ASS force_style生成開始"
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

    log(
        f"style_parts: {style_parts!r}"
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
        f"FFmpeg retained log lines: {len(lines)}"
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
        f"FFmpeg error detail length: {len(result)}"
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
        f"file_path: {file_path!r}"
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

        log_exception(
            "一時ファイルパスのPath変換に失敗しました。",
            error
        )

        return

    log(
        f"path: {path}"
    )

    try:

        exists = path.exists()

        log(
            f"exists: {exists}"
        )

        if exists:

            path.unlink()

            log(
                f"一時ファイル削除: {path}"
            )

        else:

            log(
                "削除対象ファイルは存在しません"
            )

    except Exception as error:

        log_exception(
            "一時ファイル削除失敗",
            error
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
        f"mp4_path input: {mp4_path!r}"
    )

    log(
        f"srt_path input: {srt_path!r}"
    )

    log(
        f"output_path input: {output_path!r}"
    )

    log(
        f"subtitle_settings input: "
        f"{subtitle_settings!r}"
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
        "STEP 3: SRTエンコード確認開始"
    )

    validate_srt_encoding(
        srt_path
    )

    log(
        "STEP 3完了: SRTエンコードOK"
    )

    # ======================================================
    # 字幕設定
    #
    # subtitle_font.pyを唯一の設定元とする。
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
            "output_pathが明示指定されています"
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
            "output_pathが未指定です"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

        log(
            f"自動生成output_path: {output_path}"
        )

    # ======================================================
    # 入力と出力が同じにならないようにする
    # ======================================================

    log(
        "STEP 6: 入出力パス同一性確認"
    )

    log(
        f"mp4_path: {mp4_path}"
    )

    log(
        f"output_path: {output_path}"
    )

    if output_path == mp4_path:

        log(
            "WARNING: 入力と出力が同一です"
        )

        output_path = (
            make_output_path(
                mp4_path
            ).resolve()
        )

        log(
            f"出力パスを変更しました: {output_path}"
        )

    else:

        log(
            "入力と出力は異なります"
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

    except OSError as error:

        log_exception(
            "出力フォルダ作成に失敗しました。",
            error
        )

        raise RuntimeError(

            "出力フォルダを作成できません: "
            +
            str(error)

        ) from error

    log(
        "出力フォルダ作成・存在確認OK"
    )

    try:

        writable_test = (
            os.access(
                str(output_path.parent),
                os.W_OK
            )
        )

    except Exception:

        writable_test = None

    log(
        f"出力フォルダ書き込み可能性: "
        f"{writable_test}"
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
        "STEP 9: subtitle_settingsからfont取得"
    )

    font = (
        subtitle_settings.get(
            "font"
        )
    )

    log(
        f"選択フォント: {font!r}"
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

    if font_info:

        log(
            "STEP 10完了: 日本語フォント検出"
        )

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
            "STEP 10完了: 日本語フォントなし"
        )

        log(
            "WARNING: 日本語フォントが"
            "検出できませんでした。"
        )

        log(
            "WARNING: Render環境に"
            "日本語フォントをインストールしてください。"
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
        f"入力MP4サイズ: {input_mp4_size} bytes"
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

    if temp_output_path.exists():

        log(
            "WARNING: 生成した一時出力パスが既に存在します"
        )

    else:

        log(
            "一時出力パスは未使用です"
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

    # ======================================================
    # FFmpeg実行
    # ======================================================

    log(
        "STEP 15: FFmpeg subprocess.Popen開始"
    )

    log(
        "FFmpegを起動します..."
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
    # 最後の100行だけ保持
    # ======================================================

    ffmpeg_output_lines = deque(

        maxlen=MAX_FFMPEG_LOG_LINES

    )

    log(
        f"FFmpegログ保持数: "
        f"max={MAX_FFMPEG_LOG_LINES}"
    )

    # ======================================================
    # FFmpegログ取得
    # ======================================================

    log(
        "STEP 16: FFmpeg stderrログ取得開始"
    )

    try:

        if process.stderr:

            for line in process.stderr:

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

    except Exception as error:

        log_exception(
            "FFmpegログ取得中のエラー",
            error
        )

        try:

            log(
                "FFmpeg process.kill()を実行します"
            )

            process.kill()

        except Exception as kill_error:

            log(
                f"process.kill()失敗: {kill_error}"
            )

        try:

            log(
                "FFmpeg process.wait()を実行します"
            )

            process.wait()

        except Exception as wait_error:

            log(
                f"process.wait()失敗: {wait_error}"
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
            "FFmpeg stderrクローズ処理"
        )

        if process.stderr:

            try:

                process.stderr.close()

            except Exception as error:

                log(
                    f"stderr.close()失敗: {error}"
                )

    log(
        "STEP 16完了: FFmpeg stderrログ取得終了"
    )

    log(
        f"保持しているFFmpegログ行数: "
        f"{len(ffmpeg_output_lines)}"
    )

    # ======================================================
    # FFmpeg終了
    # ======================================================

    log(
        "STEP 17: FFmpeg終了状態確認開始"
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
    # FFmpegエラー
    # ======================================================

    if return_code != 0:

        log(
            "STEP 18: FFmpeg異常終了を検出"
        )

        log(
            f"FFmpegエラー: "
            f"return code={return_code}"
        )

        log(
            "FFmpeg最後のログを取得します"
        )

        error_detail = (
            make_ffmpeg_error_detail(
                ffmpeg_output_lines
            )
        )

        log(
            f"FFmpeg error detail:\n{error_detail}"
        )

        log(
            "FFmpeg異常終了のため一時ファイルを削除します"
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
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            )

        )

    log(
        "STEP 18完了: FFmpeg正常終了"
    )

    # ======================================================
    # 一時出力確認
    # ======================================================

    log(
        "STEP 19: 一時出力ファイル確認開始"
    )

    log(
        f"temp_output_path: {temp_output_path}"
    )

    temp_exists = temp_output_path.exists()

    log(
        f"temp exists: {temp_exists}"
    )

    if not temp_exists:

        log(
            "ERROR: FFmpeg正常終了後も一時出力が存在しません"
        )

        raise RuntimeError(

            "FFmpegは正常終了しましたが、"
            "一時出力ファイルが作成されていません。"

        )

    temp_is_file = temp_output_path.is_file()

    log(
        f"temp is_file: {temp_is_file}"
    )

    if not temp_is_file:

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

        log(
            "ERROR: 一時出力ファイルサイズが0以下です"
        )

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
    # 正式出力が存在する場合
    # ======================================================

    log(
        "STEP 20: 正式出力ファイル確認"
    )

    existing_output = output_path.exists()

    log(
        f"正式出力exists: {existing_output}"
    )

    if output_path.exists():

        log(
            "既存の正式出力を削除:"
        )

        log(
            str(
                output_path
            )
        )

        try:

            old_size = output_path.stat().st_size

            log(
                f"既存正式出力サイズ: {old_size} bytes"
            )

        except OSError:

            log(
                "既存正式出力のサイズ取得に失敗しました"
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
    # 一時ファイルを正式ファイルへ移動
    # ======================================================

    log(
        "STEP 21: 一時ファイルを正式出力へ移動開始"
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

        log(
            "os.replace失敗後、一時ファイルの存在を再確認します"
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

    log(
        f"正式出力作成完了候補: {output_path}"
    )

    # ======================================================
    # 最終確認
    # ======================================================

    log(
        "STEP 22: 最終出力ファイル確認開始"
    )

    final_exists = output_path.exists()

    log(
        f"final exists: {final_exists}"
    )

    if not final_exists:

        log(
            "ERROR: os.replace後も正式出力が存在しません"
        )

        raise RuntimeError(

            "正式な字幕MP4が"
            "作成されていません。"

        )

    final_is_file = output_path.is_file()

    log(
        f"final is_file: {final_is_file}"
    )

    if not final_is_file:

        log(
            "ERROR: 正式出力先が通常ファイルではありません"
        )

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
        f"正式出力ファイルサイズ: {final_size} bytes"
    )

    if final_size <= 0:

        log(
            "ERROR: 正式出力ファイルサイズが0以下です"
        )

        remove_file_safely(
            output_path
        )

        raise RuntimeError(
            "正式出力ファイルのサイズが0です。"
        )

    log(
        "STEP 22完了: 最終出力確認OK"
    )

    # ======================================================
    # 一時ファイルが残っていないか確認
    # ======================================================

    log(
        "STEP 23: 一時ファイル残存確認"
    )

    if temp_output_path.exists():

        log(
            "WARNING: 一時ファイルが残っています"
        )

        log(
            f"temp_output_path: {temp_output_path}"
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

    log(
        "STEP 24: 字幕焼き込み最終完了"
    )

    log(
        "字幕焼き込み完了"
    )

    log(
        f"入力MP4: {mp4_path}"
    )

    log(
        f"入力SRT: {srt_path}"
    )

    log(
        f"出力ファイル: "
        f"{output_path}"
    )

    log(
        f"サイズ: "
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
        "====================================="
    )

    log(
        "embed_subtitle正常終了"
    )

    log(
        "##################################################"
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
