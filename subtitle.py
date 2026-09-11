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
# 正式設定キー:
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# subtitle.pyでは字幕設定値を独自定義しない。
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
    select_subtitle_font,
)


# ==========================================================
# 設定
# ==========================================================

DOWNLOADS_DIR = Path(DOWNLOAD_DIR)

MAX_FFMPEG_LOG_LINES = 100

# ==========================================================
# 低メモリ設定
# ==========================================================

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
    flush=True,
)

print(
    "[SUBTITLE] subtitle.py MODULE LOAD START",
    flush=True,
)

try:
    print(
        f"[SUBTITLE] subtitle.py __file__: "
        f"{Path(__file__).resolve()}",
        flush=True,
    )
except Exception as error:
    print(
        f"[SUBTITLE] __file__取得失敗: {error}",
        flush=True,
    )

print(
    f"[SUBTITLE] Python executable: {sys.executable}",
    flush=True,
)

print(
    f"[SUBTITLE] Python version: {sys.version}",
    flush=True,
)

try:
    print(
        f"[SUBTITLE] Current working directory: "
        f"{os.getcwd()}",
        flush=True,
    )
except Exception as error:
    print(
        f"[SUBTITLE] cwd取得失敗: {error}",
        flush=True,
    )

print(
    f"[SUBTITLE] DOWNLOAD_DIR: {DOWNLOAD_DIR}",
    flush=True,
)

print(
    f"[SUBTITLE] DOWNLOADS_DIR: {DOWNLOADS_DIR}",
    flush=True,
)

print(
    f"[SUBTITLE] SUBTITLE_FONT environment: "
    f"{os.environ.get('SUBTITLE_FONT')!r}",
    flush=True,
)

print(
    "[SUBTITLE] subtitle.py MODULE LOAD COMPLETE",
    flush=True,
)

print(
    "[SUBTITLE] ==========================================",
    flush=True,
)


# ==========================================================
# ログ
# ==========================================================

def log(message):
    """
    Renderログへ字幕処理ログを出力する。
    """

    try:
        print(
            "[SUBTITLE]",
            message,
            flush=True,
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
                "[SUBTITLE] " + traceback_text,
                flush=True,
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
        TypeError,
    ):
        seconds = 0

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = seconds % 60

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ==========================================================
# ローカルファイルをDownloadsへコピー
# ==========================================================

def upload_file_to_downloads(
    source_file,
    destination_filename=None,
    overwrite=True,
):
    """
    ローカルファイルをDOWNLOADS_DIRへコピーする。
    """

    log_start(
        "ローカルファイルをDownloadsへコピー開始"
    )

    log(
        f"source_file: {source_file!r}"
    )

    log(
        f"destination_filename: "
        f"{destination_filename!r}"
    )

    log(
        f"overwrite: {overwrite}"
    )

    try:
        source_path = (
            Path(source_file)
            .expanduser()
            .resolve()
        )
    except Exception as error:
        log_exception(
            "元ファイルのPath生成に失敗しました。",
            error,
        )
        raise

    log(
        f"source_path: {source_path}"
    )

    if not source_path.exists():
        raise FileNotFoundError(
            f"アップロード元ファイルが存在しません: "
            f"{source_path}"
        )

    if not source_path.is_file():
        raise ValueError(
            f"アップロード元がファイルではありません: "
            f"{source_path}"
        )

    try:
        source_size = source_path.stat().st_size
    except OSError as error:
        raise RuntimeError(
            f"元ファイルのサイズを取得できません: "
            f"{error}"
        ) from error

    log(
        f"アップロード元サイズ: "
        f"{source_size} bytes"
    )

    if source_size <= 0:
        raise ValueError(
            f"アップロード元ファイルが0 bytesです: "
            f"{source_path}"
        )

    try:
        DOWNLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as error:
        log_exception(
            "DOWNLOADS_DIR作成に失敗しました。",
            error,
        )
        raise RuntimeError(
            "Downloadsフォルダを作成できません: "
            + str(error)
        ) from error

    log(
        f"DOWNLOADS_DIR確認OK: {DOWNLOADS_DIR}"
    )

    if destination_filename:
        destination_name = Path(
            destination_filename
        ).name
    else:
        destination_name = source_path.name

    if not destination_name:
        raise ValueError(
            "Downloadsへ保存するファイル名を決定できません。"
        )

    destination_path = (
        DOWNLOADS_DIR / destination_name
    ).resolve()

    log(
        f"destination_path: {destination_path}"
    )

    try:
        destination_path.relative_to(
            DOWNLOADS_DIR.resolve()
        )
    except ValueError as error:
        raise RuntimeError(
            "Downloadsフォルダ外へファイルを保存しようとしています。"
        ) from error

    if source_path == destination_path:
        log(
            "元ファイルは既にDownloads内にあります。"
        )
        return destination_path

    if destination_path.exists():

        log(
            f"既存ファイルあり: {destination_path}"
        )

        if not overwrite:
            raise FileExistsError(
                "Downloadsに同名ファイルが既に存在します: "
                + str(destination_path)
            )

        if not destination_path.is_file():
            raise RuntimeError(
                "Downloadsの保存先が通常ファイルではありません: "
                + str(destination_path)
            )

        try:
            destination_path.unlink()
        except OSError as error:
            raise RuntimeError(
                "既存ファイルを削除できません: "
                + str(error)
            ) from error

    log(
        "ファイルコピー開始"
    )

    try:
        shutil.copy2(
            str(source_path),
            str(destination_path),
        )
    except OSError as error:
        log_exception(
            "Downloadsへのファイルコピーに失敗しました。",
            error,
        )
        raise RuntimeError(
            "ファイルをDownloadsへコピーできません: "
            + str(error)
        ) from error

    if not destination_path.exists():
        raise RuntimeError(
            "コピー後のファイルが存在しません。"
        )

    if not destination_path.is_file():
        raise RuntimeError(
            "コピー先が通常ファイルではありません。"
        )

    try:
        destination_size = destination_path.stat().st_size
    except OSError as error:
        raise RuntimeError(
            "コピー後のファイルサイズを確認できません: "
            + str(error)
        ) from error

    log(
        f"コピー後サイズ: {destination_size} bytes"
    )

    if destination_size <= 0:
        raise RuntimeError(
            "Downloadsへコピーされたファイルのサイズが0 bytesです。"
        )

    if destination_size != source_size:
        raise RuntimeError(
            "ファイルコピー後のサイズが一致しません。"
            f" source={source_size}"
            f" destination={destination_size}"
        )

    log(
        "ローカルファイルをDownloadsへコピー完了"
    )

    log_separator()

    return destination_path


# ==========================================================
# SRT作成用MP3アップロード
# ==========================================================

def upload_mp3_to_downloads(
    mp3_file,
    overwrite=True,
):
    """
    SRT作成時に使用するMP3をDownloadsへコピーする。
    """

    log_start(
        "SRT作成用MP3アップロード開始"
    )

    mp3_path = upload_file_to_downloads(
        mp3_file,
        destination_filename=Path(mp3_file).name,
        overwrite=overwrite,
    )

    if mp3_path.suffix.lower() != ".mp3":
        raise ValueError(
            "SRT作成用ファイルはMP3である必要があります: "
            + str(mp3_path)
        )

    log(
        f"SRT作成用MP3: {mp3_path}"
    )

    return mp3_path


# ==========================================================
# 字幕MP4作成用 MP4 + SRT アップロード
# ==========================================================

def upload_subtitle_inputs_to_downloads(
    mp4_file,
    srt_file,
    overwrite=True,
):
    """
    字幕MP4作成時に使用するMP4とSRTをDownloadsへコピーする。

    Returns
    -------
    tuple
        (mp4_path, srt_path)
    """

    log_start(
        "字幕MP4作成用ファイルアップロード開始"
    )

    mp4_path = upload_file_to_downloads(
        mp4_file,
        destination_filename=Path(mp4_file).name,
        overwrite=overwrite,
    )

    if mp4_path.suffix.lower() != ".mp4":
        raise ValueError(
            "字幕MP4作成用動画はMP4である必要があります: "
            + str(mp4_path)
        )

    srt_path = upload_file_to_downloads(
        srt_file,
        destination_filename=Path(srt_file).name,
        overwrite=overwrite,
    )

    if srt_path.suffix.lower() != ".srt":
        raise ValueError(
            "字幕MP4作成用字幕はSRTである必要があります: "
            + str(srt_path)
        )

    log(
        f"MP4: {mp4_path}"
    )

    log(
        f"SRT: {srt_path}"
    )

    log(
        "字幕MP4作成用MP4 + SRTアップロード完了"
    )

    log_separator()

    return mp4_path, srt_path


# ==========================================================
# 入力ファイル確認
# ==========================================================

def validate_input_file(
    file_path,
    extension,
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
        path = (
            Path(file_path)
            .expanduser()
            .resolve()
        )
    except Exception as error:
        log_exception(
            "Path生成に失敗しました。",
            error,
        )
        raise

    if not path.exists():
        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"ファイルではありません: {path}"
        )

    actual_suffix = path.suffix.lower()

    if actual_suffix != extension.lower():
        raise ValueError(
            f"{extension} ファイルではありません: {path}"
        )

    try:
        size = path.stat().st_size
    except OSError as error:
        raise RuntimeError(
            f"ファイルサイズを確認できません: {error}"
        ) from error

    if size <= 0:
        raise ValueError(
            f"ファイルが0 bytesです: {path}"
        )

    log(
        f"入力ファイル確認完了: {path}"
    )

    log(
        f"file size: {size} bytes"
    )

    return path


# ==========================================================
# 出力ファイル名
# ==========================================================

def make_output_path(mp4_path):
    """
    字幕焼き込み後の出力パスを生成する。

    既存ファイルがあっても _2 等は作成しない。
    """

    mp4_path = (
        Path(mp4_path)
        .expanduser()
        .resolve()
    )

    stem = mp4_path.stem
    base_suffix = "_sub_embed"

    if stem.lower().endswith(base_suffix):
        base_stem = stem
    else:
        base_stem = f"{stem}{base_suffix}"

    candidate = (
        mp4_path.parent
        / f"{base_stem}.mp4"
    )

    log(
        f"決定出力パス: {candidate}"
    )

    return candidate


# ==========================================================
# 一時出力パス
# ==========================================================

def make_temp_output_path(output_path):

    output_path = (
        Path(output_path)
        .resolve()
    )

    timestamp = time.time_ns()

    temp_path = (
        output_path.parent
        /
        (
            "."
            + output_path.stem
            + f".subtitle_{timestamp}.tmp.mp4"
        )
    )

    log(
        f"一時出力パス生成: {temp_path}"
    )

    return temp_path


# ==========================================================
# FFmpeg確認
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
            "FFmpegがPATH上に見つかりません。"
            "Render環境にFFmpegをインストールしてください。"
        )

    # ------------------------------------------------------
    # version
    # ------------------------------------------------------

    try:
        result = subprocess.run(
            [
                ffmpeg_path,
                "-version",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            "FFmpegの起動確認がタイムアウトしました。"
        ) from error
    except OSError as error:
        raise RuntimeError(
            f"FFmpegを起動できません: {error}"
        ) from error

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpegを正常に起動できませんでした。"
        )

    version_lines = result.stdout.splitlines()

    if version_lines:
        log(
            f"FFmpeg version: {version_lines[0]}"
        )

    # ------------------------------------------------------
    # encoders
    # ------------------------------------------------------

    try:
        encoder_result = subprocess.run(
            [
                ffmpeg_path,
                "-hide_banner",
                "-encoders",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            "FFmpegのエンコーダー確認がタイムアウトしました。"
        ) from error
    except OSError as error:
        raise RuntimeError(
            f"FFmpegのエンコーダー確認に失敗しました: {error}"
        ) from error

    encoder_text = (
        encoder_result.stdout
        + encoder_result.stderr
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

    # ------------------------------------------------------
    # filters
    # ------------------------------------------------------

    try:
        filter_result = subprocess.run(
            [
                ffmpeg_path,
                "-hide_banner",
                "-filters",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            "FFmpegのsubtitlesフィルター確認がタイムアウトしました。"
        ) from error
    except OSError as error:
        raise RuntimeError(
            f"FFmpegのフィルター確認に失敗しました: {error}"
        ) from error

    filter_text = (
        filter_result.stdout
        + filter_result.stderr
    )

    if filter_result.returncode != 0:
        raise RuntimeError(
            "FFmpegのフィルター一覧を取得できませんでした。"
        )

    if "subtitles" not in filter_text:
        raise RuntimeError(
            "FFmpegにsubtitlesフィルターがありません。"
            "libass対応のFFmpegが必要です。"
        )

    log(
        "subtitles filter: OK"
    )

    log(
        "FFmpeg確認完了"
    )

    return ffmpeg_path


# ==========================================================
# SRT UTF-8確認
# ==========================================================

def validate_srt_encoding(srt_path):

    log_start(
        "SRT UTF-8確認開始"
    )

    srt_path = Path(srt_path)

    try:
        with open(
            srt_path,
            "r",
            encoding="utf-8-sig",
        ) as file:
            first_content = file.read(4096)

    except UnicodeDecodeError as error:
        log_exception(
            "SRT UTF-8 decode error",
            error,
        )

        raise RuntimeError(
            "SRTファイルをUTF-8として読み込めませんでした。"
            "SRTをUTF-8形式で保存してください。"
        ) from error

    except OSError as error:
        raise RuntimeError(
            f"SRTファイルを読み込めませんでした: {error}"
        ) from error

    if not first_content.strip():
        raise RuntimeError(
            "SRTファイルが空です。"
        )

    try:
        srt_size = srt_path.stat().st_size
    except OSError:
        srt_size = 0

    log(
        f"SRTサイズ: {srt_size} bytes"
    )

    log(
        "SRT UTF-8確認完了"
    )

    return True


# ==========================================================
# フォントfamily取得
# ==========================================================

def get_font_family_from_path(font_path):

    log(
        f"font_path: {font_path}"
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
                str(font_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except Exception as error:
        log_exception(
            "fc-scanエラー",
            error,
        )
        return None

    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        if "," in line:
            line = line.split(
                ",",
                1,
            )[0].strip()

        if line:
            log(
                f"検出family: {line}"
            )
            return line

    return None


# ==========================================================
# fc-match
# ==========================================================

def fc_match_font(requested_font):

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
                str(requested_font),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except Exception as error:
        log_exception(
            "fc-matchエラー",
            error,
        )
        return None

    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():

        line = line.strip()

        if not line:
            continue

        font_path = Path(line)

        if not font_path.is_file():
            continue

        family = get_font_family_from_path(
            font_path
        )

        result_data = {
            "path": font_path.resolve(),
            "family": family,
        }

        log(
            f"fc-match selected: {result_data}"
        )

        return result_data

    return None


# ==========================================================
# 日本語フォント検索
# ==========================================================

def find_japanese_font(requested_font=None):

    log_start(
        "日本語フォント検索開始"
    )

    log(
        f"requested_font: {requested_font}"
    )

    # ------------------------------------------------------
    # 1. 環境変数
    # ------------------------------------------------------

    environment_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    if environment_font:

        environment_font_path = (
            Path(environment_font)
            .expanduser()
            .resolve()
        )

        if environment_font_path.is_file():

            family = get_font_family_from_path(
                environment_font_path
            )

            return {
                "path": environment_font_path,
                "family": family,
            }

        log(
            "SUBTITLE_FONT指定フォントが存在しません。"
        )

    # ------------------------------------------------------
    # 2. subtitle_font.py
    # ------------------------------------------------------

    if requested_font:

        requested_font = str(
            requested_font
        ).strip()

        requested_path = (
            Path(requested_font)
            .expanduser()
        )

        if requested_path.is_file():

            requested_path = (
                requested_path.resolve()
            )

            family = get_font_family_from_path(
                requested_path
            )

            return {
                "path": requested_path,
                "family": family,
            }

        matched = fc_match_font(
            requested_font
        )

        if matched:
            return matched

    # ------------------------------------------------------
    # 3. 日本語フォント候補
    # ------------------------------------------------------

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
                f"日本語フォント検出: "
                f"{matched}"
            )

            return matched

    # ------------------------------------------------------
    # 4. fc-list
    # ------------------------------------------------------

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
                    "%{file}|%{family}\n",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except Exception as error:
            log_exception(
                "fc-list検索エラー",
                error,
            )
            result = None

        if result and result.returncode == 0:

            for line in result.stdout.splitlines():

                line = line.strip()

                if not line:
                    continue

                parts = line.split(
                    "|",
                    1,
                )

                font_file = parts[0].strip()

                family = (
                    parts[1].strip()
                    if len(parts) > 1
                    else ""
                )

                if not font_file:
                    continue

                font_path = Path(font_file)

                if not font_path.is_file():
                    continue

                if "," in family:
                    family = family.split(
                        ",",
                        1,
                    )[0].strip()

                return {
                    "path": font_path.resolve(),
                    "family": family,
                }

    # ------------------------------------------------------
    # 5. 手動検索
    # ------------------------------------------------------

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
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path("/opt/render/project/src/fonts"),
        Path("/app/fonts"),
        Path("fonts").resolve(),
    ]

    for directory in font_directories:

        if not directory.exists():
            continue

        for font_name in preferred_fonts:

            try:
                for match in directory.rglob(font_name):

                    if not match.is_file():
                        continue

                    family = get_font_family_from_path(
                        match
                    )

                    return {
                        "path": match.resolve(),
                        "family": family,
                    }

            except Exception as error:
                log_exception(
                    f"フォント検索エラー: {directory}",
                    error,
                )

    log(
        "日本語フォントが見つかりませんでした。"
    )

    return None


# ==========================================================
# FFmpeg filtergraph用パスエスケープ
# ==========================================================

def escape_ffmpeg_filter_path(file_path):

    path = str(
        Path(file_path).resolve()
    )

    path = path.replace(
        "\\",
        "/",
    )

    path = path.replace(
        "'",
        "\\'",
    )

    path = path.replace(
        ":",
        "\\:",
    )

    path = path.replace(
        ";",
        "\\;",
    )

    path = path.replace(
        "\n",
        "\\n",
    )

    return path


# ==========================================================
# FFmpeg force_style値エスケープ
# ==========================================================

def escape_ffmpeg_value(value):

    value = str(value)

    value = value.replace(
        "\\",
        "\\\\",
    )

    value = value.replace(
        "'",
        "\\'",
    )

    value = value.replace(
        ":",
        "\\:",
    )

    value = value.replace(
        ",",
        "\\,",
    )

    value = value.replace(
        ";",
        "\\;",
    )

    return value


# ==========================================================
# ASSカラー取得
# ==========================================================

def get_ass_color(color_name):

    log(
        f"ASSカラー取得: {color_name}"
    )

    if color_name is None:
        raise RuntimeError(
            "字幕カラーが指定されていません。"
        )

    color_info = SUBTITLE_COLORS.get(
        color_name
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

    return str(ass_color)


# ==========================================================
# 字幕設定正規化
#
# ★設定処理はsubtitle_font.pyへ完全委譲
# ==========================================================

def normalize_subtitle_settings(
    subtitle_settings=None,
):
    """
    subtitle_font.pyを唯一の設定管理元として、
    字幕設定を正規化する。
    """

    log_start(
        "字幕設定正規化開始"
    )

    if subtitle_settings is None:

        log(
            "設定未指定 -> subtitle_font.py標準設定"
        )

        settings = (
            get_default_subtitle_font_settings()
        )

        if not isinstance(settings, dict):
            raise RuntimeError(
                "subtitle_font.pyの標準設定がdictではありません。"
            )

        # 標準設定もselect_subtitle_font()を通す
        settings = select_subtitle_font(
            settings=settings
        )

    else:

        if not isinstance(
            subtitle_settings,
            dict,
        ):
            raise TypeError(
                "subtitle_settingsはdictで指定してください。"
            )

        log(
            f"入力設定: {subtitle_settings!r}"
        )

        settings = select_subtitle_font(
            settings=subtitle_settings
        )

    if not isinstance(settings, dict):
        raise RuntimeError(
            "subtitle_font.select_subtitle_font()の戻り値がdictではありません。"
        )

    normalized = {}

    for key in SUBTITLE_SETTING_KEYS:
        normalized[key] = settings.get(key)

    log(
        f"最終字幕設定: {normalized!r}"
    )

    return normalized


# ==========================================================
# 字幕フィルター作成
# ==========================================================

def make_subtitle_filter(
    srt_path,
    font_info=None,
    subtitle_settings=None,
):

    log_start(
        "字幕フィルター作成開始"
    )

    subtitle_settings = normalize_subtitle_settings(
        subtitle_settings
    )

    subtitle_path = escape_ffmpeg_filter_path(
        srt_path
    )

    video_filter = (
        "subtitles='"
        + subtitle_path
        + "'"
    )

    preset_name = subtitle_settings.get(
        "preset_name"
    )

    font = subtitle_settings.get(
        "font"
    )

    text_color_name = subtitle_settings.get(
        "text_color"
    )

    outline_color_name = subtitle_settings.get(
        "outline_color"
    )

    outline_width = subtitle_settings.get(
        "outline_width"
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
        TypeError,
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

    # ------------------------------------------------------
    # FontName
    # ------------------------------------------------------

    font_name = None

    if font_info:

        detected_family = font_info.get(
            "family"
        )

        if detected_family:

            detected_family = str(
                detected_family
            ).strip()

            if detected_family:
                font_name = detected_family

    if not font_name:
        font_name = str(font).strip()

    if not font_name:
        raise RuntimeError(
            "字幕フォント名を決定できませんでした。"
        )

    log(
        f"最終FontName: {font_name}"
    )

    # ------------------------------------------------------
    # fontsdir
    # ------------------------------------------------------

    if font_info:

        font_path = font_info.get(
            "path"
        )

        if font_path:

            font_path = Path(
                font_path
            ).resolve()

            if font_path.is_file():

                font_directory = font_path.parent

                font_directory_escaped = (
                    escape_ffmpeg_filter_path(
                        font_directory
                    )
                )

                video_filter += (
                    ":fontsdir='"
                    + font_directory_escaped
                    + "'"
                )

                log(
                    f"字幕フォントディレクトリ: "
                    f"{font_directory}"
                )

    # ------------------------------------------------------
    # ASS style
    # ------------------------------------------------------

    style_parts = [
        "FontName="
        + escape_ffmpeg_value(
            font_name
        ),

        "PrimaryColour="
        + text_color,

        "OutlineColour="
        + outline_color,

        "Outline="
        + str(outline_width),
    ]

    force_style = ",".join(
        style_parts
    )

    video_filter += (
        ":force_style='"
        + force_style
        + "'"
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

def command_to_string(command):

    return " ".join(
        str(item)
        for item in command
    )


# ==========================================================
# FFmpegログ整形
# ==========================================================

def make_ffmpeg_error_detail(lines):

    if not lines:
        return (
            "FFmpegからエラー内容が返されませんでした。"
        )

    return "\n".join(lines)


# ==========================================================
# ファイル削除
# ==========================================================

def remove_file_safely(file_path):

    if not file_path:
        return

    try:
        path = Path(file_path)
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
# FFmpegプロセス終了処理
# ==========================================================

def terminate_process_safely(process):

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
                    "terminate()後も終了しないためkill()します。"
                )

                process.kill()

                process.wait(
                    timeout=5
                )

    except Exception as error:

        log(
            f"FFmpegプロセス終了処理失敗: {error}"
        )


# ==========================================================
# FFmpeg stderr逐次取得
# ==========================================================

def collect_ffmpeg_output(
    process,
    output_lines,
):
    """
    FFmpeg stderrを1行ずつ読み込む。

    deque(maxlen=100)により、
    最後の100行だけをメモリ保持する。
    """

    if process.stderr is None:
        return

    log(
        "FFmpeg stderr読み取り開始"
    )

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
                flush=True,
            )

    except Exception as error:

        log_exception(
            "FFmpeg stderr読み取り中に例外",
            error,
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
    subtitle_settings=None,
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
    process = None

    ffmpeg_output_lines = deque(
        maxlen=MAX_FFMPEG_LOG_LINES
    )

    try:

        # ==================================================
        # STEP 1
        # ==================================================

        log_start(
            "STEP 1: MP4入力確認"
        )

        mp4_path = validate_input_file(
            mp4_path,
            ".mp4",
        )

        # ==================================================
        # STEP 2
        # ==================================================

        log_start(
            "STEP 2: SRT入力確認"
        )

        srt_path = validate_input_file(
            srt_path,
            ".srt",
        )

        # ==================================================
        # STEP 3
        # ==================================================

        log_start(
            "STEP 3: SRT UTF-8確認"
        )

        validate_srt_encoding(
            srt_path
        )

        # ==================================================
        # STEP 4
        # ==================================================

        log_start(
            "STEP 4: 字幕設定正規化"
        )

        subtitle_settings = normalize_subtitle_settings(
            subtitle_settings
        )

        log(
            f"normalized subtitle settings: "
            f"{subtitle_settings!r}"
        )

        # ==================================================
        # STEP 5
        # ==================================================

        log_start(
            "STEP 5: 出力先決定"
        )

        if output_path:

            output_path = (
                Path(output_path)
                .expanduser()
                .resolve()
            )

        else:

            output_path = make_output_path(
                mp4_path
            ).resolve()

        if output_path == mp4_path:

            log(
                "WARNING: 入力と出力が同じです。"
            )

            output_path = make_output_path(
                mp4_path
            ).resolve()

        # ==================================================
        # STEP 6
        # ==================================================

        log_start(
            "STEP 6: 出力フォルダ確認"
        )

        try:

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        except OSError as error:

            raise RuntimeError(
                "出力フォルダを作成できません: "
                + str(error)
            ) from error

        # ==================================================
        # STEP 7
        # ==================================================

        log_start(
            "STEP 7: FFmpeg確認"
        )

        ffmpeg_path = check_ffmpeg()

        # ==================================================
        # STEP 8
        # ==================================================

        log_start(
            "STEP 8: フォント確認"
        )

        font = subtitle_settings.get(
            "font"
        )

        font_info = find_japanese_font(
            font
        )

        if not font_info:

            raise RuntimeError(
                "日本語字幕フォントが見つかりません。"
                "Render環境に日本語フォントをインストールしてください。"
            )

        log(
            f"font path: {font_info.get('path')}"
        )

        log(
            f"font family: {font_info.get('family')}"
        )

        # ==================================================
        # STEP 9
        # ==================================================

        log_start(
            "STEP 9: 字幕フィルター生成"
        )

        video_filter = make_subtitle_filter(
            srt_path,
            font_info,
            subtitle_settings,
        )

        # ==================================================
        # STEP 10
        # ==================================================

        log_start(
            "STEP 10: 入力MP4サイズ確認"
        )

        try:
            input_mp4_size = mp4_path.stat().st_size
        except OSError:
            input_mp4_size = 0

        log(
            f"入力MP4サイズ: {input_mp4_size} bytes"
        )

        # ==================================================
        # STEP 11
        # ==================================================

        log_start(
            "STEP 11: 一時出力パス生成"
        )

        temp_output_path = make_temp_output_path(
            output_path
        )

        # ==================================================
        # STEP 12
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

            str(temp_output_path),
        ]

        log(
            "FFmpeg command:"
        )

        log(
            command_to_string(command)
        )

        # ==================================================
        # STEP 13
        # ==================================================

        log_start(
            "STEP 13: FFmpeg subprocess.Popen開始"
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

                bufsize=1,
            )

        except OSError as error:

            raise RuntimeError(
                "FFmpeg実行中にエラーが発生しました: "
                + str(error)
            ) from error

        log(
            f"FFmpeg process started: PID={process.pid}"
        )

        # ==================================================
        # STEP 14
        # ==================================================

        log_start(
            "STEP 14: FFmpeg stderrログ取得"
        )

        collect_ffmpeg_output(
            process,
            ffmpeg_output_lines,
        )

        # ==================================================
        # STEP 15
        # ==================================================

        log_start(
            "STEP 15: FFmpeg終了状態確認"
        )

        return_code = process.wait()

        elapsed_time = (
            time.monotonic()
            - start_time
        )

        log(
            f"FFmpeg return code: {return_code}"
        )

        log(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        # ==================================================
        # STEP 16
        # ==================================================

        if return_code != 0:

            error_detail = make_ffmpeg_error_detail(
                ffmpeg_output_lines
            )

            raise RuntimeError(

                "字幕焼き込みに失敗しました。"
                "\n\n"
                + error_detail
                + "\n\n"
                "FFmpeg return code: "
                + str(return_code)

            )

        # ==================================================
        # STEP 17
        # ==================================================

        log_start(
            "STEP 17: 一時出力ファイル確認"
        )

        if not temp_output_path.exists():
            raise RuntimeError(
                "FFmpegは正常終了しましたが、"
                "一時出力ファイルが作成されていません。"
            )

        if not temp_output_path.is_file():
            raise RuntimeError(
                "FFmpegの一時出力先がファイルではありません。"
            )

        try:
            output_size = (
                temp_output_path.stat().st_size
            )
        except OSError as error:
            raise RuntimeError(
                "一時出力ファイルを確認できませんでした: "
                + str(error)
            ) from error

        if output_size <= 0:
            raise RuntimeError(
                "FFmpeg出力ファイルのサイズが0です。"
            )

        log(
            f"一時出力ファイルサイズ: "
            f"{output_size} bytes"
        )

        # ==================================================
        # STEP 18
        # ==================================================

        log_start(
            "STEP 18: 正式出力へ置換"
        )

        try:

            os.replace(
                str(temp_output_path),
                str(output_path),
            )

        except OSError as error:

            raise RuntimeError(
                "字幕MP4を正式出力へ移動できませんでした: "
                + str(error)
            ) from error

        # ==================================================
        # STEP 19
        # ==================================================

        log_start(
            "STEP 19: 最終出力ファイル確認"
        )

        if not output_path.exists():
            raise RuntimeError(
                "正式な字幕MP4が作成されていません。"
            )

        if not output_path.is_file():
            raise RuntimeError(
                "正式出力先がファイルではありません。"
            )

        try:
            final_size = output_path.stat().st_size
        except OSError as error:
            raise RuntimeError(
                "正式出力ファイルを確認できませんでした: "
                + str(error)
            ) from error

        if final_size <= 0:

            remove_file_safely(
                output_path
            )

            raise RuntimeError(
                "正式出力ファイルのサイズが0です。"
            )

        # ==================================================
        # 完了
        # ==================================================

        elapsed_time = (
            time.monotonic()
            - start_time
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

        return output_path

    except Exception as error:

        if process is not None:
            terminate_process_safely(
                process
            )

        remove_file_safely(
            temp_output_path
        )

        log_exception(
            "embed_subtitle()で例外が発生しました。",
            error,
        )

        raise


# ==========================================================
# 外部向け正式関数
# ==========================================================

def create_subtitle_mp4(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None,
):

    log(
        "create_subtitle_mp4開始"
    )

    result = embed_subtitle(
        mp4_path,
        srt_path,
        output_path,
        subtitle_settings,
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
    subtitle_settings=None,
):

    log(
        "create_burned_subtitle開始"
    )

    result = embed_subtitle(
        mp4_path,
        srt_path,
        output_path,
        subtitle_settings,
    )

    log(
        f"create_burned_subtitle完了: {result}"
    )

    return result


def burn_subtitles(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None,
):

    log(
        "burn_subtitles開始"
    )

    result = embed_subtitle(
        mp4_path,
        srt_path,
        output_path,
        subtitle_settings,
    )

    log(
        f"burn_subtitles完了: {result}"
    )

    return result


# ==========================================================
# Downloads内から実行
# ==========================================================

def embed_from_downloads(
    mp4_filename,
    srt_filename,
    subtitle_settings=None,
):

    log_separator()

    log(
        "embed_from_downloads開始"
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

    try:

        DOWNLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    except OSError as error:

        log_exception(
            "DOWNLOADS_DIR作成に失敗しました。",
            error,
        )

        raise

    mp4_path = (
        DOWNLOADS_DIR
        / mp4_filename
    )

    srt_path = (
        DOWNLOADS_DIR
        / srt_filename
    )

    log(
        f"downloads MP4: {mp4_path}"
    )

    log(
        f"downloads SRT: {srt_path}"
    )

    result = embed_subtitle(
        mp4_path,
        srt_path,
        subtitle_settings=subtitle_settings,
    )

    log(
        f"embed_from_downloads完了: {result}"
    )

    log_separator()

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

    if len(sys.argv) < 3:

        print()
        print(
            "使用方法:"
        )
        print(
            "python subtitle.py 動画.mp4 字幕.srt"
        )
        print()

        return 1

    mp4_filename = sys.argv[1]
    srt_filename = sys.argv[2]

    start_time = time.monotonic()

    try:

        # ==================================================
        # subtitle_font.pyから標準設定取得
        # ==================================================

        log(
            "STEP MAIN-1: "
            "subtitle_font.pyから標準設定取得開始"
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
