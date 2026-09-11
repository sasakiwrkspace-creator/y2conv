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
# ローカルファイルをDownloadsへアップロード
# ==========================================================

def upload_file_to_downloads(
    source_file,
    destination_filename=None,
    overwrite=True
):
    """
    ローカルファイルをDOWNLOADS_DIRへコピーする。

    SRT作成時:
        MP3をDownloadsへコピー

    字幕MP4作成時:
        MP4とSRTをDownloadsへコピー

    Parameters
    ----------
    source_file:
        ローカルに存在する元ファイル

    destination_filename:
        Downloads内で使用するファイル名。
        Noneの場合は元ファイル名を使用。

    overwrite:
        Trueの場合、同名ファイルを上書きする。

    Returns
    -------
    Path
        Downloadsへコピーされたファイル
    """

    log_start(
        "ローカルファイルをDownloadsへアップロード開始"
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

    # ======================================================
    # 元ファイル確認
    # ======================================================

    try:

        source_path = (
            Path(
                source_file
            )
            .expanduser()
            .resolve()
        )

    except Exception as error:

        log_exception(
            "元ファイルのPath生成に失敗しました。",
            error
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

        source_size = (
            source_path.stat().st_size
        )

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

    # ======================================================
    # Downloadsフォルダ作成
    # ======================================================

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

        raise RuntimeError(
            "Downloadsフォルダを作成できません: "
            +
            str(error)
        ) from error

    log(
        f"DOWNLOADS_DIR確認OK: {DOWNLOADS_DIR}"
    )

    # ======================================================
    # 保存ファイル名決定
    # ======================================================

    if destination_filename:

        destination_name = (
            Path(
                destination_filename
            ).name
        )

    else:

        destination_name = (
            source_path.name
        )

    if not destination_name:

        raise ValueError(
            "Downloadsへ保存するファイル名を"
            "決定できません。"
        )

    destination_path = (
        DOWNLOADS_DIR
        /
        destination_name
    ).resolve()

    log(
        f"destination_path: {destination_path}"
    )

    # ======================================================
    # Downloads外への保存防止
    # ======================================================

    try:

        destination_path.relative_to(
            DOWNLOADS_DIR.resolve()
        )

    except ValueError as error:

        raise RuntimeError(
            "Downloadsフォルダ外へファイルを"
            "保存しようとしています。"
        ) from error

    # ======================================================
    # 元ファイルと保存先が同じ場合
    # ======================================================

    if source_path == destination_path:

        log(
            "元ファイルは既にDownloads内にあります。"
        )

        log(
            "コピーを行わず、そのまま使用します。"
        )

        return destination_path

    # ======================================================
    # 既存ファイル確認
    # ======================================================

    if destination_path.exists():

        log(
            f"既存ファイルあり: {destination_path}"
        )

        if not overwrite:

            raise FileExistsError(
                "Downloadsに同名ファイルが"
                "既に存在します: "
                +
                str(destination_path)
            )

        if not destination_path.is_file():

            raise RuntimeError(
                "Downloadsの保存先が"
                "通常ファイルではありません: "
                +
                str(destination_path)
            )

        try:

            destination_path.unlink()

        except OSError as error:

            raise RuntimeError(
                "既存ファイルを削除できません: "
                +
                str(error)
            ) from error

        log(
            "既存ファイル削除完了"
        )

    # ======================================================
    # ファイルコピー
    # ======================================================

    log(
        "ファイルコピー開始"
    )

    try:

        shutil.copy2(
            str(source_path),
            str(destination_path)
        )

    except OSError as error:

        log_exception(
            "Downloadsへのファイルコピーに失敗しました。",
            error
        )

        raise RuntimeError(
            "ファイルをDownloadsへコピーできません: "
            +
            str(error)
        ) from error

    log(
        "ファイルコピー完了"
    )

    # ======================================================
    # コピー後確認
    # ======================================================

    if not destination_path.exists():

        raise RuntimeError(
            "ファイルをDownloadsへコピーしましたが、"
            "保存先に存在しません。"
        )

    if not destination_path.is_file():

        raise RuntimeError(
            "Downloadsへのコピー先が"
            "通常ファイルではありません。"
        )

    try:

        destination_size = (
            destination_path.stat().st_size
        )

    except OSError as error:

        raise RuntimeError(
            "コピー後のファイルサイズを"
            "確認できません: "
            +
            str(error)
        ) from error

    log(
        f"コピー後サイズ: "
        f"{destination_size} bytes"
    )

    if destination_size <= 0:

        raise RuntimeError(
            "Downloadsへコピーされたファイルの"
            "サイズが0 bytesです。"
        )

    if destination_size != source_size:

        raise RuntimeError(
            "ファイルコピー後のサイズが一致しません。"
            f" source={source_size}"
            f" destination={destination_size}"
        )

    log(
        "ローカルファイルをDownloadsへ"
        "アップロード完了"
    )

    log(
        f"source: {source_path}"
    )

    log(
        f"destination: {destination_path}"
    )

    log(
        f"size: {destination_size} bytes"
    )

    log_separator()

    return destination_path


# ==========================================================
# SRT作成用MP3アップロード
# ==========================================================

def upload_mp3_to_downloads(
    mp3_file,
    overwrite=True
):
    """
    SRT作成時に使用するMP3をDownloadsへコピーする。
    """

    log_start(
        "SRT作成用MP3アップロード開始"
    )

    log(
        f"mp3_file: {mp3_file!r}"
    )

    mp3_path = upload_file_to_downloads(
        mp3_file,
        destination_filename=Path(
            mp3_file
        ).name,
        overwrite=overwrite
    )

    if mp3_path.suffix.lower() != ".mp3":

        raise ValueError(
            "SRT作成用ファイルはMP3である必要があります: "
            +
            str(mp3_path)
        )

    log(
        f"SRT作成用MP3: {mp3_path}"
    )

    log(
        "SRT作成用MP3アップロード完了"
    )

    return mp3_path


# ==========================================================
# 字幕MP4作成用 MP4 + SRT アップロード
# ==========================================================

def upload_subtitle_inputs_to_downloads(
    mp4_file,
    srt_file,
    overwrite=True
):
    """
    字幕MP4作成時に使用するMP4とSRTを
    Downloadsへコピーする。

    Returns
    -------
    tuple
        (mp4_path, srt_path)
    """

    log_start(
        "字幕MP4作成用ファイルアップロード開始"
    )

    log(
        f"mp4_file: {mp4_file!r}"
    )

    log(
        f"srt_file: {srt_file!r}"
    )

    # ======================================================
    # MP4
    # ======================================================

    mp4_path = upload_file_to_downloads(
        mp4_file,
        destination_filename=Path(
            mp4_file
        ).name,
        overwrite=overwrite
    )

    if mp4_path.suffix.lower() != ".mp4":

        raise ValueError(
            "字幕MP4作成用動画はMP4である必要があります: "
            +
            str(mp4_path)
        )

    log(
        f"字幕MP4作成用MP4: {mp4_path}"
    )

    # ======================================================
    # SRT
    # ======================================================

    srt_path = upload_file_to_downloads(
        srt_file,
        destination_filename=Path(
            srt_file
        ).name,
        overwrite=overwrite
    )

    if srt_path.suffix.lower() != ".srt":

        raise ValueError(
            "字幕MP4作成用字幕はSRTである必要があります: "
            +
            str(srt_path)
        )

    log(
        f"字幕MP4作成用SRT: {srt_path}"
    )

    # ======================================================
    # 完了
    # ======================================================

    log(
        "字幕MP4作成用"
        "MP4 + SRTアップロード完了"
    )

    log(
        f"MP4: {mp4_path}"
    )

    log(
        f"SRT: {srt_path}"
    )

    log_separator()

    return mp4_path, srt_path

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
    """
    字幕焼き込み後の出力パスを生成する。

    出力ファイルが既に存在する場合も、
    _2、_3などの別名は作成せず、
    常に同じパスを返す。

    実際の上書きは embed_subtitle() 内で
    一時ファイルを生成した後、
    os.replace() によって安全に行う。
    """

    log_start(
        "出力ファイル名生成開始"
    )

    mp4_path = (
        Path(
            mp4_path
        )
        .expanduser()
        .resolve()
    )

    stem = mp4_path.stem

    base_suffix = "_sub_embed"

    if stem.lower().endswith(
        base_suffix
    ):

        base_stem = stem

    else:

        base_stem = (
            f"{stem}{base_suffix}"
        )

    candidate = (
        mp4_path.parent
        /
        f"{base_stem}.mp4"
    )

    if candidate.exists():

        log(
            f"既存出力ファイルあり: {candidate}"
        )

        log(
            "既存ファイルを上書きします。"
        )

    else:

        log(
            f"新規出力ファイル: {candidate}"
        )

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
# FFmpeg存在・機能確認
# ==========================================================

def check_ffmpeg():

    log_start(
        "FFmpeg確認開始"
    )

    # ======================================================
    # STEP A
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
            "Render環境にFFmpegをインストールしてください。"
        )

    log(
        f"FFmpeg path: {ffmpeg_path}"
    )

    # ======================================================
    # STEP B
    # ======================================================

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

        raise RuntimeError(
            "FFmpeg実行ファイルが見つかりません。"
        ) from error

    except subprocess.TimeoutExpired as error:

        raise RuntimeError(
            "FFmpegの起動確認がタイムアウトしました。"
        ) from error

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
            "FFmpegを正常に起動できませんでした。"
        )

    version_lines = (
        result.stdout.splitlines()
    )

    first_line = (
        version_lines[0]
        if version_lines
        else "FFmpeg"
    )

    log(
        f"FFmpeg version: {first_line}"
    )

    log(
        "FFmpeg本体確認: OK"
    )

    # ======================================================
    # STEP C
    # ======================================================

    log(
        "libx264確認開始"
    )

    try:

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

    except subprocess.TimeoutExpired as error:

        raise RuntimeError(
            "FFmpegのlibx264確認がタイムアウトしました。"
        ) from error

    except OSError as error:

        raise RuntimeError(
            f"FFmpegのエンコーダー確認に失敗しました: {error}"
        ) from error

    encoder_text = (
        encoder_result.stdout
        +
        encoder_result.stderr
    )

    log(
        f"FFmpeg -encoders returncode: "
        f"{encoder_result.returncode}"
    )

    if encoder_result.returncode != 0:

        log(
            encoder_result.stderr[-2000:]
        )

        raise RuntimeError(
            "FFmpegのエンコーダー一覧を取得できませんでした。"
        )

    if "libx264" not in encoder_text:

        raise RuntimeError(
            "FFmpegにlibx264エンコーダーがありません。"
            "字幕焼き込みにはlibx264が必要です。"
        )

    log(
        "libx264: OK"
    )

    # ======================================================
    # STEP D
    # ======================================================

    log(
        "subtitlesフィルター確認開始"
    )

    try:

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

    except subprocess.TimeoutExpired as error:

        raise RuntimeError(
            "FFmpegのsubtitlesフィルター確認が"
            "タイムアウトしました。"
        ) from error

    except OSError as error:

        raise RuntimeError(
            f"FFmpegのフィルター確認に失敗しました: {error}"
        ) from error

    filter_text = (
        filter_result.stdout
        +
        filter_result.stderr
    )

    log(
        f"FFmpeg -filters returncode: "
        f"{filter_result.returncode}"
    )

    if filter_result.returncode != 0:

        log(
            filter_result.stderr[-2000:]
        )

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

    # ======================================================
    # STEP E
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

    except (
        subprocess.TimeoutExpired,
        OSError
    ) as error:

        log(
            f"WARNING: -buildconf確認失敗: {error}"
        )

        build_result = None

    if build_result:

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
                "WARNING: -buildconfから"
                "libassを確認できませんでした。"
            )

            log(
                "subtitlesフィルター自体は存在するため、"
                "処理を続行します。"
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

        return None

    fc_match = shutil.which(
        "fc-match"
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
                "日本語フォント検出:"
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

    path = str(
        Path(
            file_path
        ).resolve()
    )

    # FFmpeg filtergraph内では
    # Windows / Linux の双方を考慮する。

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

        if not isinstance(result, dict):

            raise RuntimeError(
                "subtitle_font.pyの標準設定がdictではありません。"
            )

        normalized = {}

        for key in SUBTITLE_SETTING_KEYS:

            normalized[key] = result.get(
                key
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
            "select_subtitle_font()の戻り値がdictではありません。"
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
    # FontName決定
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
# FFmpeg実行直前パラメータ診断
# ==========================================================

def log_ffmpeg_parameters(
    command,
    video_filter,
    mp4_path,
    srt_path,
    output_path,
    temp_output_path,
    font_info,
    subtitle_settings
):
    """
    FFmpeg subprocess.Popen()直前に、
    実際に渡すパラメータをRenderログへ詳細表示する。

    特に以下を重点的に確認する:
        - FFmpeg executable
        - MP4入力パス
        - SRT入力パス
        - output path
        - temp output path
        - font path
        - font family
        - fontsdir
        - video_filter
        - subtitle settings
        - FFmpeg command各要素
    """

    log_separator()

    log(
        "######## FFmpeg実行直前パラメータ診断 ########"
    )

    # ======================================================
    # 基本情報
    # ======================================================

    log(
        "----- BASIC PARAMETERS -----"
    )

    log(
        f"mp4_path       = {str(mp4_path)!r}"
    )

    log(
        f"srt_path       = {str(srt_path)!r}"
    )

    log(
        f"output_path    = {str(output_path)!r}"
    )

    log(
        f"temp_output    = {str(temp_output_path)!r}"
    )

    # ======================================================
    # フォント情報
    # ======================================================

    log(
        "----- FONT INFORMATION -----"
    )

    if font_info is None:

        log(
            "font_info = None"
        )

    else:

        log(
            f"font_info type = {type(font_info).__name__}"
        )

        log(
            f"font_info raw = {font_info!r}"
        )

        font_path = font_info.get(
            "path"
        )

        font_family = font_info.get(
            "family"
        )

        log(
            f"font_info.path   = {font_path!r}"
        )

        log(
            f"font_info.family = {font_family!r}"
        )

        if font_path:

            try:

                font_path_obj = Path(
                    font_path
                ).resolve()

                log(
                    f"font_path resolved = "
                    f"{font_path_obj!s}"
                )

                log(
                    f"font_path exists = "
                    f"{font_path_obj.exists()}"
                )

                log(
                    f"font_path is_file = "
                    f"{font_path_obj.is_file()}"
                )

                log(
                    f"font_path parent = "
                    f"{font_path_obj.parent!s}"
                )

                log(
                    f"font_path parent exists = "
                    f"{font_path_obj.parent.exists()}"
                )

            except Exception as error:

                log(
                    f"font_path確認失敗: {error}"
                )

    # ======================================================
    # subtitle_settings
    # ======================================================

    log(
        "----- SUBTITLE SETTINGS -----"
    )

    if subtitle_settings is None:

        log(
            "subtitle_settings = None"
        )

    else:

        log(
            f"subtitle_settings type = "
            f"{type(subtitle_settings).__name__}"
        )

        for key in SUBTITLE_SETTING_KEYS:

            value = subtitle_settings.get(
                key
            )

            log(
                f"subtitle_settings[{key!r}] = "
                f"{value!r}"
            )

    # ======================================================
    # video_filter
    # ======================================================

    log(
        "----- VIDEO FILTER -----"
    )

    log(
        f"video_filter type = "
        f"{type(video_filter).__name__}"
    )

    log(
        f"video_filter length = "
        f"{len(video_filter)}"
    )

    log(
        f"video_filter repr = "
        f"{video_filter!r}"
    )

    log(
        "video_filter raw:"
    )

    log(
        video_filter
    )

    # ======================================================
    # fontsdirをvideo_filterから確認
    # ======================================================

    log(
        "----- FONTDIR DIAGNOSTIC -----"
    )

    fontsdir_marker = ":fontsdir='"

    if fontsdir_marker in video_filter:

        fontsdir_start = (
            video_filter.find(
                fontsdir_marker
            )
            +
            len(fontsdir_marker)
        )

        fontsdir_end = (
            video_filter.find(
                "'",
                fontsdir_start
            )
        )

        if fontsdir_end >= 0:

            fontsdir_value = (
                video_filter[
                    fontsdir_start:
                    fontsdir_end
                ]
            )

            log(
                f"fontsdir extracted = "
                f"{fontsdir_value!r}"
            )

            log(
                f"fontsdir length = "
                f"{len(fontsdir_value)}"
            )

        else:

            log(
                "WARNING: fontsdirの終了'が"
                "見つかりません。"
            )

    else:

        log(
            "fontsdirはvideo_filterに"
            "含まれていません。"
        )

    # ======================================================
    # FFmpeg command
    # ======================================================

    log(
        "----- FFMPEG COMMAND -----"
    )

    log(
        f"command type = "
        f"{type(command).__name__}"
    )

    log(
        f"command length = "
        f"{len(command)}"
    )

    for index, item in enumerate(command):

        log(
            f"command[{index}] = {item!r}"
        )

    log(
        "----- FFMPEG COMMAND STRING -----"
    )

    log(
        command_to_string(
            command
        )
    )

    # ======================================================
    # subprocessに渡す値の型確認
    # ======================================================

    log(
        "----- COMMAND TYPE CHECK -----"
    )

    for index, item in enumerate(command):

        log(
            f"command[{index}] "
            f"type={type(item).__name__} "
            f"value={item!r}"
        )

    # ======================================================
    # 重要な引数を個別表示
    # ======================================================

    log(
        "----- IMPORTANT ARGUMENTS -----"
    )

    try:

        vf_index = command.index(
            "-vf"
        )

        vf_value = command[
            vf_index + 1
        ]

        log(
            f"-vf value = {vf_value!r}"
        )

    except (
        ValueError,
        IndexError
    ):

        log(
            "WARNING: -vf引数を取得できません。"
        )

    try:

        input_index = command.index(
            "-i"
        )

        input_value = command[
            input_index + 1
        ]

        log(
            f"-i value = {input_value!r}"
        )

    except (
        ValueError,
        IndexError
    ):

        log(
            "WARNING: -i引数を取得できません。"
        )

    # ======================================================
    # 最終診断
    # ======================================================

    log(
        "######## FFmpeg実行直前パラメータ診断 END ########"
    )

    log_separator()

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
# FFmpeg stderr取得
#
# 重要:
#   stdoutはDEVNULL。
#   stderrだけを逐次処理する。
#
#   deque(maxlen=100)なので、最後の100行だけを
#   メモリに保持する。
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
# FFmpegプロセス終了処理
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
                    "terminate()後も終了しないため "
                    "kill()します。"
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
            ".mp4"
        )

        log(
            f"MP4確認完了: {mp4_path}"
        )

        # ==================================================
        # STEP 2
        # ==================================================

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

        subtitle_settings = (
            normalize_subtitle_settings(
                subtitle_settings
            )
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
                Path(
                    output_path
                ).expanduser().resolve()
            )

        else:

            output_path = (
                make_output_path(
                    mp4_path
                ).resolve()
            )

        log(
            f"最終output_path: {output_path}"
        )

        # ==================================================
        # 入力と出力が同じにならないようにする
        # ==================================================

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

        # ==================================================
        # STEP 6
        # ==================================================

        log_start(
            "STEP 6: 出力フォルダ確認"
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

        # ==================================================
        # STEP 7
        # ==================================================

        log_start(
            "STEP 7: FFmpeg確認"
        )

        ffmpeg_path = check_ffmpeg()

        log(
            f"使用FFmpeg: {ffmpeg_path}"
        )

        # ==================================================
        # STEP 8
        # ==================================================

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

            raise RuntimeError(
                "日本語字幕フォントが見つかりません。"
                "Render環境に日本語フォントを"
                "インストールしてください。"
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

            subtitle_settings

        )

        log(
            "STEP 9完了: 字幕フィルター生成OK"
        )

        # ==================================================
        # STEP 10
        # ==================================================

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

        # ==================================================
        # STEP 11
        # ==================================================

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

        # ==================================================
        # FFmpeg開始情報
        # ==================================================

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

                bufsize=1

            )

        except OSError as error:

            log_exception(
                "FFmpeg subprocess.Popenに失敗しました。",
                error
            )

            raise RuntimeError(

                "FFmpeg実行中にエラーが発生しました: "
                +
                str(error)

            ) from error

        log(
            f"FFmpeg process started: PID={process.pid}"
        )

        # ==================================================
        # STEP 14
        # ==================================================

        log_start(
            "STEP 14: FFmpeg stderrログ取得開始"
        )

        collect_ffmpeg_output(
            process,
            ffmpeg_output_lines
        )

        log(
            "STEP 14完了: FFmpeg stderrログ取得終了"
        )

        log(
            f"保持しているFFmpegログ行数: "
            f"{len(ffmpeg_output_lines)}"
        )

        # ==================================================
        # STEP 15
        # ==================================================

        log_start(
            "STEP 15: FFmpeg終了状態確認"
        )

        return_code = process.wait()

        log(
            f"FFmpeg return code: {return_code}"
        )

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log(
            f"現在までの処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        # ==================================================
        # STEP 16
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

                "FFmpegの一時出力先が"
                "ファイルではありません。"

            )

        try:

            output_size = (
                temp_output_path.stat().st_size
            )

        except OSError as error:

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

            raise RuntimeError(
                "FFmpeg出力ファイルのサイズが0です。"
            )

        log(
            "一時出力ファイル確認OK"
        )

        # ==================================================
        # STEP 18
        # ==================================================

        log_start(
            "STEP 18: 正式出力ファイル確認"
        )

        if output_path.exists():

            log(
                "既存の正式出力があります。"
            )

            try:

                if output_path.is_file():

                    output_path.unlink()

                else:

                    raise RuntimeError(
                        "既存の正式出力パスが"
                        "通常ファイルではありません。"
                    )

            except OSError as error:

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

        # ==================================================
        # STEP 19
        # ==================================================

        log_start(
            "STEP 19: 一時ファイルを正式出力へ移動"
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

            raise RuntimeError(

                "字幕MP4を正式出力へ"
                "移動できませんでした: "
                +
                str(error)

            ) from error

        log(
            "os.replace()成功"
        )

        # ==================================================
        # STEP 20
        # ==================================================

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

        # ==================================================
        # STEP 21
        # ==================================================

        log_start(
            "STEP 21: 一時ファイル残存確認"
        )

        if temp_output_path.exists():

            remove_file_safely(
                temp_output_path
            )

        else:

            log(
                "一時ファイルは残っていません"
            )

        # ==================================================
        # 完了
        # ==================================================

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

    except Exception as error:

        # ==================================================
        # エラー時FFmpeg停止
        # ==================================================

        if process is not None:

            terminate_process_safely(
                process
            )

        # ==================================================
        # エラー時一時ファイル削除
        # ==================================================

        remove_file_safely(
            temp_output_path
        )

        log_exception(
            "embed_subtitle()で例外が発生しました。",
            error
        )

        raise


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

    log_separator()

    log(
        "embed_from_downloads開始"
    )

    log(
        f"mp4_filename input: {mp4_filename!r}"
    )

    log(
        f"srt_filename input: {srt_filename!r}"
    )

    # ======================================================
    # ファイル名だけを許可
    # ======================================================

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

    # ======================================================
    # DOWNLOADS_DIR確認
    # ======================================================

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
        f"downloads MP4: {mp4_path}"
    )

    log(
        f"downloads SRT: {srt_path}"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        subtitle_settings=subtitle_settings

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

    log(
        f"Python executable: {sys.executable}"
    )

    log(
        f"Python version: {sys.version}"
    )

    try:

        log(
            f"Current working directory: "
            f"{os.getcwd()}"
        )

    except Exception:

        pass

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


        // =====================================
        // ダウンロードボタン
        // =====================================

        function createDownloadButton(
            label,
            filename,
            downloadUrl
        ) {

            if (!downloadArea) {

                return;

            }


            downloadArea.innerHTML =
                "";


            if (!filename) {

                return;

            }


            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.textContent =
                label ||
                "ダウンロード";


            button.className =
                "test-button";


            button.addEventListener(
                "click",
                function () {

                    let url =
                        downloadUrl;


                    if (!url) {

                        url =
                            "/downloads/" +
                            encodeURIComponent(
                                filename
                            );

                    }


                    const link =
                        document.createElement(
                            "a"
                        );


                    link.href =
                        url;


                    link.download =
                        filename;


                    document.body.appendChild(
                        link
                    );


                    link.click();


                    link.remove();

                }
            );


            downloadArea.appendChild(
                button
            );

        }


        // =====================================
        // MP4転送
        // =====================================

        async function transferMp4() {

            if (
                subtitleState.isProcessing
            ) {

                return;

            }


            const file =
                mp4Input.files &&
                mp4Input.files.length
                    ? mp4Input.files[0]
                    : null;


            if (!file) {

                setStatus(
                    "MP4ファイルを選択してください。",
                    "error"
                );

                return;

            }


            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".mp4")
            ) {

                setStatus(
                    "MP4ファイルを選択してください。",
                    "error"
                );

                return;

            }


            subtitleState.isProcessing =
                true;


            if (mp4UploadButton) {

                mp4UploadButton.disabled =
                    true;

            }


            if (srtUploadButton) {

                srtUploadButton.disabled =
                    true;

            }


            setFontDisabled(
                true
            );


            startProcessing();


            try {

                startElapsedTimer(
                    "MP4を転送しています..."
                );


                const result =
                    await uploadMp4(
                        file
                    );


                subtitleState.mp4File =
                    file;


                subtitleState.mp4Filename =
                    result.mp4_file ||
                    result.filename ||
                    file.name;


                subtitleState.uploadedMp4Filename =
                    subtitleState.mp4Filename;


                stopElapsedTimer();


                setStatus(

                    "MP4の転送が完了しました。\n\n" +
                    "MP4: " +
                    subtitleState.uploadedMp4Filename +
                    "\n\n" +
                    getElapsedText(),

                    "success"

                );

            }
            catch (error) {

                stopElapsedTimer();


                console.error(
                    "[SUBTITLE] MP4転送エラー:",
                    error
                );


                setStatus(

                    "MP4転送中にエラーが発生しました。\n" +
                    (
                        error &&
                        error.message
                            ? error.message
                            : "不明なエラー"
                    ) +
                    "\n\n" +
                    getElapsedText(),

                    "error"

                );

            }
            finally {

                stopElapsedTimer();


                subtitleState.isProcessing =
                    false;


                processingStartTime =
                    null;


                setFontDisabled(
                    false
                );


                if (mp4UploadButton) {

                    mp4UploadButton.disabled =
                        false;

                }


                if (srtUploadButton) {

                    srtUploadButton.disabled =
                        false;

                }


                updateSubtitleMp4Button();

            }

        }


        // =====================================
        // SRT転送
        // =====================================

        async function transferSrt() {

            if (
                subtitleState.isProcessing
            ) {

                return;

            }


            const file =
                srtInput.files &&
                srtInput.files.length
                    ? srtInput.files[0]
                    : null;


            if (!file) {

                setStatus(
                    "SRTファイルを選択してください。",
                    "error"
                );

                return;

            }


            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".srt")
            ) {

                setStatus(
                    "SRTファイルを選択してください。",
                    "error"
                );

                return;

            }


            subtitleState.isProcessing =
                true;


            if (mp4UploadButton) {

                mp4UploadButton.disabled =
                    true;

            }


            if (srtUploadButton) {

                srtUploadButton.disabled =
                    true;

            }


            setFontDisabled(
                true
            );


            startProcessing();


            try {

                startElapsedTimer(
                    "SRTを転送しています..."
                );


                const result =
                    await uploadSrt(
                        file
                    );


                subtitleState.srtFile =
                    file;


                subtitleState.srtFilename =
                    result.srt_file ||
                    result.filename ||
                    file.name;


                subtitleState.uploadedSrtFilename =
                    subtitleState.srtFilename;


                stopElapsedTimer();


                setStatus(

                    "SRTの転送が完了しました。\n\n" +
                    "SRT: " +
                    subtitleState.uploadedSrtFilename +
                    "\n\n" +
                    getElapsedText(),

                    "success"

                );

            }
            catch (error) {

                stopElapsedTimer();


                console.error(
                    "[SUBTITLE] SRT転送エラー:",
                    error
                );


                setStatus(

                    "SRT転送中にエラーが発生しました。\n" +
                    (
                        error &&
                        error.message
                            ? error.message
                            : "不明なエラー"
                    ) +
                    "\n\n" +
                    getElapsedText(),

                    "error"

                );

            }
            finally {

                stopElapsedTimer();


                subtitleState.isProcessing =
                    false;


                processingStartTime =
                    null;


                setFontDisabled(
                    false
                );


                if (mp4UploadButton) {

                    mp4UploadButton.disabled =
                        false;

                }


                if (srtUploadButton) {

                    srtUploadButton.disabled =
                        false;

                }


                updateSubtitleMp4Button();

            }

        }


        // =====================================
        // 字幕MP4ボタン状態
        //
        // MP4 + SRTの両方が転送済みなら有効
        // =====================================

        function updateSubtitleMp4Button() {

            const hasMp4 =
                !!subtitleState.uploadedMp4Filename;


            const hasSrt =
                !!subtitleState.uploadedSrtFilename;


            subtitleMp4Button.disabled =
                !hasMp4 ||
                !hasSrt ||
                subtitleState.isProcessing;

        }


        // =====================================
        // MP3選択
        // =====================================

        mp3SelectButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                mp3Input.click();

            }
        );


        mp3Input.addEventListener(
            "change",
            function () {

                const file =
                    this.files &&
                    this.files.length
                        ? this.files[0]
                        : null;


                subtitleState.mp3File =
                    file;


                subtitleState.mp3Filename =
                    file
                        ? file.name
                        : "";


                updateFileDisplay(
                    mp3SelectButton,
                    file,
                    "ファイルが選択されていません → mp3ファイルを選択してください"
                );


                geminiButton.disabled =
                    !file ||
                    subtitleState.isProcessing;

            }
        );


        // =====================================
        // MP4選択
        //
        // 新しいMP4を選択したら
        // 古い転送済みMP4を無効化
        // =====================================

        mp4SelectButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                mp4Input.click();

            }
        );


        mp4Input.addEventListener(
            "change",
            function () {

                const file =
                    this.files &&
                    this.files.length
                        ? this.files[0]
                        : null;


                subtitleState.mp4File =
                    file;


                subtitleState.mp4Filename =
                    file
                        ? file.name
                        : "";


                ## ---------------------------------
                // 新しいMP4を選択したので、
                // 以前の転送済みMP4を無効化
                ## ---------------------------------

                subtitleState.uploadedMp4Filename =
                    "";


                ## ---------------------------------
                // ボタン表示
                ## ---------------------------------

                updateFileDisplay(
                    mp4SelectButton,
                    file,
                    "ファイルが選択されていません → mp4ファイルを選択してください"
                );


                updateSubtitleMp4Button();

            }
        );


        // =====================================
        // SRT選択
        //
        // 新しいSRTを選択したら
        // 古い転送済みSRTを無効化
        // =====================================

        srtSelectButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                srtInput.click();

            }
        );


        srtInput.addEventListener(
            "change",
            function () {

                const file =
                    this.files &&
                    this.files.length
                        ? this.files[0]
                        : null;


                subtitleState.srtFile =
                    file;


                subtitleState.srtFilename =
                    file
                        ? file.name
                        : "";


                ## ---------------------------------
                // 新しいSRTを選択したので、
                // 以前の転送済みSRTを無効化
                ## ---------------------------------

                subtitleState.uploadedSrtFilename =
                    "";


                ## ---------------------------------
                // ボタン表示
                ## ---------------------------------

                updateFileDisplay(
                    srtSelectButton,
                    file,
                    "ファイルが選択されていません → srtファイルを選択してください"
                );


                updateSubtitleMp4Button();

            }
        );


        // =====================================
        // MP4転送ボタン
        // =====================================

        if (mp4UploadButton) {

            mp4UploadButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    transferMp4();

                }
            );

        }


        // =====================================
        // SRT転送ボタン
        // =====================================

        if (srtUploadButton) {

            srtUploadButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    transferSrt();

                }
            );

        }


        // =====================================
        // Gemini
        // =====================================

        geminiButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                const file =
                    mp3Input.files &&
                    mp3Input.files.length
                        ? mp3Input.files[0]
                        : null;


                if (!file) {

                    setStatus(
                        "MP3ファイルを選択してください。",
                        "error"
                    );

                    return;

                }


                if (
                    !file.name
                        .toLowerCase()
                        .endsWith(".mp3")
                ) {

                    setStatus(
                        "MP3ファイルを選択してください。",
                        "error"
                    );

                    return;

                }


                subtitleState.isProcessing =
                    true;


                geminiButton.disabled =
                    true;


                setFontDisabled(
                    true
                );


                startProcessing();


                try {

                    startElapsedTimer(
                        "MP3をアップロードしています..."
                    );


                    const result =
                        await createSrtWithGemini(
                            file
                        );


                    subtitleState.mp3Filename =
                        result.mp3_file ||
                        result.filename ||
                        file.name;


                    subtitleState.generatedSrtFilename =
                        result.srt_file ||
                        "";


                    stopElapsedTimer();


                    if (!result.srt_file) {

                        throw new Error(
                            "作成されたSRTファイル名を取得できませんでした。"
                        );

                    }


                    setStatus(

                        "SRTファイルの作成が完了しました。\n\n" +
                        "SRT: " +
                        result.srt_file +
                        "\n\n" +
                        getElapsedText(),

                        "success"

                    );


                    createDownloadButton(
                        "SRTをダウンロード",
                        result.srt_file,
                        result.download_url
                    );

                }
                catch (error) {

                    stopElapsedTimer();


                    console.error(
                        "[SUBTITLE] SRT作成エラー:",
                        error
                    );


                    setStatus(

                        "SRT作成中にエラーが発生しました。\n" +
                        (
                            error &&
                            error.message
                                ? error.message
                                : "不明なエラー"
                        ) +
                        "\n\n" +
                        getElapsedText(),

                        "error"

                    );

                }
                finally {

                    stopElapsedTimer();


                    subtitleState.isProcessing =
                        false;


                    processingStartTime =
                        null;


                    setFontDisabled(
                        false
                    );


                    geminiButton.disabled =
                        !(
                            mp3Input.files &&
                            mp3Input.files.length
                        );

                }

            }
        );


        // =====================================
        // 字幕MP4作成
        //
        // ・ここではアップロードしない
        // ・転送済みMP4/SRTだけを使用
        // ・/subtitle-create-mp4 を呼び出す
        // =====================================

        subtitleMp4Button.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                const mp4Filename =
                    subtitleState.uploadedMp4Filename;


                const srtFilename =
                    subtitleState.uploadedSrtFilename;


                if (!mp4Filename) {

                    setStatus(
                        "先にMP4ファイルを転送してください。",
                        "error"
                    );

                    return;

                }


                if (!srtFilename) {

                    setStatus(
                        "先にSRTファイルを転送してください。",
                        "error"
                    );

                    return;

                }


                subtitleState.isProcessing =
                    true;


                subtitleMp4Button.disabled =
                    true;


                if (mp4UploadButton) {

                    mp4UploadButton.disabled =
                        true;

                }


                if (srtUploadButton) {

                    srtUploadButton.disabled =
                        true;

                }


                setFontDisabled(
                    true
                );


                startProcessing();


                try {

                    startElapsedTimer(

                        "字幕を動画に付けています...\n" +
                        "しばらくお待ちください。"

                    );


                    const embedResult =
                        await embedSubtitle(
                            mp4Filename,
                            srtFilename
                        );


                    subtitleState.generatedSubtitleMp4Filename =
                        embedResult.filename;


                    stopElapsedTimer();


                    setStatus(

                        "字幕mp4の作成が完了しました。\n\n" +
                        "ファイル: " +
                        embedResult.filename +
                        "\n\n" +
                        getElapsedText(),

                        "success"

                    );


                    createDownloadButton(

                        "字幕付きMP4をダウンロード",

                        embedResult.filename,

                        embedResult.download_url

                    );

                }
                catch (error) {

                    stopElapsedTimer();


                    console.error(
                        "[SUBTITLE] 字幕MP4作成エラー:",
                        error
                    );


                    setStatus(

                        "字幕mp4作成中にエラーが発生しました。\n" +
                        (
                            error &&
                            error.message
                                ? error.message
                                : "不明なエラー"
                    ) +
                        "\n\n" +
                        getElapsedText(),

                        "error"

                    );

                }
                finally {

                    stopElapsedTimer();


                    subtitleState.isProcessing =
                        false;


                    processingStartTime =
                        null;


                    setFontDisabled(
                        false
                    );


                    if (mp4UploadButton) {

                        mp4UploadButton.disabled =
                            false;

                    }


                    if (srtUploadButton) {

                        srtUploadButton.disabled =
                            false;

                    }


                    updateSubtitleMp4Button();

                }

            }
        );


        // =====================================
        // 外部公開
        // =====================================

        mainObject.createSrtWithGemini =
            createSrtWithGemini;


        mainObject.uploadMp4 =
            uploadMp4;


        mainObject.uploadSrt =
            uploadSrt;


        mainObject.transferMp4 =
            transferMp4;


        mainObject.transferSrt =
            transferSrt;


        mainObject.embedSubtitle =
            embedSubtitle;


        mainObject.createDownloadButton =
            createDownloadButton;


        mainObject.getState =
            function () {

                return subtitleState;

            };


        mainObject.getFontPreset =
            function () {

                return getFontPreset();

            };


        mainObject.getFontSettings =
            function () {

                return getFontSettings();

            };


        mainObject.clearResult =
            clearStatus;


        // =====================================
        // 初期表示
        // =====================================

        updateFileDisplay(
            mp3SelectButton,
            null,
            "mp3ファイルを選択してください"
        );


        ## -------------------------------------
        // MP4
        ## -------------------------------------

        updateFileDisplay(
            mp4SelectButton,
            null,
            "mp4ファイルを選択してください"
        );


        ## -------------------------------------
        // SRT
        ## -------------------------------------

        updateFileDisplay(
            srtSelectButton,
            null,
            "srtファイルを選択してください"
        );


        geminiButton.disabled =
            true;


        if (mp4UploadButton) {

            mp4UploadButton.disabled =
                false;

        }


        if (srtUploadButton) {

            srtUploadButton.disabled =
                false;

        }


        updateSubtitleMp4Button();


        console.log(
            "[SUBTITLE] initializeSubtitle() complete"
        );

    }


    // =====================================
    // DOMContentLoaded
    // =====================================

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializeSubtitle,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeSubtitle();

    }

})();# ==========================================================
# subtitle_test_fonts.py
#
# 字幕フォントFFmpegテスト
#
# 目的:
#
#   test.mp4
#       +
#   test.srt
#       ↓
#   subtitle_font.py
#       ↓
#   フォント・文字色・縁色・縁太さ
#       ↓
#   FFmpeg subtitles filter
#       ↓
#   test_embed_fonts.mp4
#
#
# 重要:
#
#   /app/downloads/fonts
#   が存在しない場合でもエラーにしない。
#
#   fontsdirが存在:
#       ↓
#       fontsdirをFFmpegへ渡す
#
#   fontsdirが存在しない:
#       ↓
#       警告を表示
#       ↓
#       規定フォントを使用
#       ↓
#       FFmpeg処理を継続
#
# ==========================================================


from pathlib import Path
import subprocess


# ==========================================================
# パス
# ==========================================================

DOWNLOAD_DIR = Path(
"/app/downloads"
)


DEFAULT_INPUT_MP4 = (
DOWNLOAD_DIR /
"test.mp4"
)


DEFAULT_INPUT_SRT = (
DOWNLOAD_DIR /
"test.srt"
)


DEFAULT_OUTPUT_MP4 = (
DOWNLOAD_DIR /
"test_embed_fonts.mp4"
)


DEFAULT_FONTS_DIR = (
DOWNLOAD_DIR /
"fonts"
)


# ==========================================================
# デフォルト値
#
# subtitle_font.pyと合わせる。
# ==========================================================

DEFAULT_FONT = (
"Noto Sans CJK JP"
)


DEFAULT_TEXT_COLOR = (
"白"
)


DEFAULT_OUTLINE_COLOR = (
"青"
)


DEFAULT_OUTLINE_WIDTH = 5


# ==========================================================
# ログ
# ==========================================================

def _log(
message
):

print(
"[SUBTITLE_TEST_FONTS]",
message,
flush=True
)


# ==========================================================
# subtitle_font.pyから設定取得
# ==========================================================

def _get_font_settings(
font=None,
text_color=None,
outline_color=None,
outline_width=None
):

_log(
"subtitle_font.py import START"
)


try:

from subtitle_font import (
    select_subtitle_font
)

except Exception as error:

_log(
    "subtitle_font.py import FAILED"
)

_log(
    f"{type(error).__name__}: {error}"
)

raise


_log(
"subtitle_font.py import OK"
)


# ======================================================
# 明示指定が無い場合は標準設定
# ======================================================

settings = select_subtitle_font(

preset_name="標準",

font=(
    font
    if font is not None
    else DEFAULT_FONT
),

text_color=(
    text_color
    if text_color is not None
    else DEFAULT_TEXT_COLOR
),

outline_color=(
    outline_color
    if outline_color is not None
    else DEFAULT_OUTLINE_COLOR
),

outline_width=(
    outline_width
    if outline_width is not None
    else DEFAULT_OUTLINE_WIDTH
)

)


_log(
f"subtitle settings: {settings}"
)


return settings


# ==========================================================
# SRTパスをFFmpeg filter用にエスケープ
# ==========================================================

def _escape_filter_path(
path
):

value = str(
Path(path)
)


# ======================================================
# FFmpeg filterで問題になりやすい文字を処理
# ======================================================

value = value.replace(
"\\",
"\\\\"
)


value = value.replace(
":",
"\\:"
)


value = value.replace(
"'",
"\\'"
)


value = value.replace(
"[",
"\\["
)


value = value.replace(
"]",
"\\]"
)


return value


# ==========================================================
# FFmpeg字幕filter生成
# ==========================================================

def _build_subtitles_filter(
srt_path,
fonts_dir,
settings
):

# ======================================================
# SRT
# ======================================================

escaped_srt = _escape_filter_path(
srt_path
)


# ======================================================
# フォント
# ======================================================

font_name = (
settings.get(
    "font"
)
or
DEFAULT_FONT
)


# ======================================================
# 文字色
#
# ASSカラーへ変換
# ======================================================

from subtitle_font import (
get_subtitle_color
)


text_color_info = (
get_subtitle_color(
    settings.get(
        "text_color",
        DEFAULT_TEXT_COLOR
    )
)
)


outline_color_info = (
get_subtitle_color(
    settings.get(
        "outline_color",
        DEFAULT_OUTLINE_COLOR
    )
)
)


text_color_ass = (
text_color_info[
    "ass"
]
)


outline_color_ass = (
outline_color_info[
    "ass"
]
)


# ======================================================
# 縁太さ
# ======================================================

try:

outline_width = int(
    settings.get(
        "outline_width",
        DEFAULT_OUTLINE_WIDTH
    )
)

except (
ValueError,
TypeError
):

outline_width = (
    DEFAULT_OUTLINE_WIDTH
)


outline_width = max(
0,
min(
    outline_width,
    10
)
)


# ======================================================
# force_style
#
# FontName:
#   subtitle_font.pyのfont
#
# PrimaryColour:
#   文字色
#
# OutlineColour:
#   縁色
#
# Outline:
#   縁太さ
#
# ======================================================

force_style = (
f"FontName={font_name},"
f"PrimaryColour={text_color_ass},"
f"OutlineColour={outline_color_ass},"
f"Outline={outline_width}"
)


# ======================================================
# subtitles filter
# ======================================================

filter_value = (
"subtitles="
f"'{escaped_srt}'"
)


# ======================================================
# fontsdir
#
# 存在する場合のみ追加。
# ======================================================

if fonts_dir is not None:

escaped_fonts_dir = (
    _escape_filter_path(
        fonts_dir
    )
)


filter_value += (
    f":fontsdir='{escaped_fonts_dir}'"
)


# ======================================================
# force_style追加
# ======================================================

filter_value += (
f":force_style='{force_style}'"
)


return filter_value


# ==========================================================
# メイン
# ==========================================================

def run_font_test(
input_path=None,
output_path=None,
srt_path=None,
fonts_dir=None,
font=None,
text_color=None,
outline_color=None,
outline_width=None
):

print(
"==========================================",
flush=True
)


print(
"[SUBTITLE_TEST_FONTS] START",
flush=True
)


print(
"==========================================",
flush=True
)


# ======================================================
# パス
# ======================================================

if input_path is None:

input_file = (
    DEFAULT_INPUT_MP4
)

else:

input_file = Path(
    input_path
)


if output_path is None:

output_file = (
    DEFAULT_OUTPUT_MP4
)

else:

output_file = Path(
    output_path
)


if srt_path is None:

srt_file = (
    DEFAULT_INPUT_SRT
)

else:

srt_file = Path(
    srt_path
)


if fonts_dir is None:

fonts_directory = (
    DEFAULT_FONTS_DIR
)

else:

fonts_directory = Path(
    fonts_dir
)


# ======================================================
# パス表示
# ======================================================

_log(
f"input: {input_file}"
)


_log(
f"srt: {srt_file}"
)


_log(
f"output: {output_file}"
)


_log(
f"fonts: {fonts_directory}"
)


# ======================================================
# MP4確認
# ======================================================

_log(
"MP4存在確認 START"
)


if not input_file.exists():

raise FileNotFoundError(
    "入力ファイルが存在しません: "
    f"{input_file}"
)


if not input_file.is_file():

raise FileNotFoundError(
    "入力パスがファイルではありません: "
    f"{input_file}"
)


input_size = (
input_file.stat().st_size
)


_log(
"MP4存在確認 OK"
)


_log(
f"入力サイズ: {input_size} bytes"
)


# ======================================================
# SRT確認
# ======================================================

_log(
"SRT存在確認 START"
)


if not srt_file.exists():

raise FileNotFoundError(
    "字幕ファイルが存在しません: "
    f"{srt_file}"
)


if not srt_file.is_file():

raise FileNotFoundError(
    "字幕パスがファイルではありません: "
    f"{srt_file}"
)


srt_size = (
srt_file.stat().st_size
)


_log(
"SRT存在確認 OK"
)


_log(
f"SRTサイズ: {srt_size} bytes"
)


# ======================================================
# 出力ディレクトリ
# ======================================================

output_file.parent.mkdir(
parents=True,
exist_ok=True
)


# ======================================================
# 既存出力削除
# ======================================================

if output_file.exists():

_log(
    "既存出力削除"
)


output_file.unlink()


# ======================================================
# fontsdir確認
#
# ★ここが今回の重要ポイント
#
# fontsが無くてもエラーにしない。
# ======================================================

_log(
"フォントディレクトリ確認 START"
)


use_fonts_dir = False


if fonts_directory.exists():

if fonts_directory.is_dir():

    use_fonts_dir = True


    _log(
        "フォントディレクトリ確認 OK"
    )


    _log(
        f"fontsdir使用: {fonts_directory}"
    )

else:

    _log(
        "WARNING: fontsパスは存在しますが"
        "ディレクトリではありません"
    )


    _log(
        "WARNING: fontsdirを使用しません"
    )


else:

_log(
    "WARNING: フォントディレクトリが"
    "存在しません"
)


_log(
    f"WARNING: {fonts_directory}"
)


_log(
    "WARNING: fontsdirなしで処理を継続します"
)


_log(
    f"WARNING: 規定フォントを使用します: "
    f"{DEFAULT_FONT}"
)


# ======================================================
# 字幕フォント設定
# ======================================================

settings = _get_font_settings(

font=font,

text_color=text_color,

outline_color=outline_color,

outline_width=outline_width

)


# ======================================================
# fontsdirなしの場合
#
# 指定フォントが無い可能性があるため、
# ログに明示する。
#
# 実際のフォント解決はFFmpeg/libassに任せる。
# ======================================================

if not use_fonts_dir:

_log(
    "=========================================="
)


_log(
    "FONT FALLBACK MODE"
)


_log(
    "fontsdir: 使用しません"
)


_log(
    "FFmpeg/libassのシステムフォント検索を使用"
)


_log(
    f"font: {settings['font']}"
)


_log(
    "=========================================="
)


# ======================================================
# subtitles filter
# ======================================================

subtitles_filter = (
_build_subtitles_filter(

    srt_path=srt_file,

    fonts_dir=(
        fonts_directory
        if use_fonts_dir
        else None
    ),

    settings=settings

)
)


# ======================================================
# filter表示
# ======================================================

_log(
"字幕filter:"
)


_log(
subtitles_filter
)


# ======================================================
# FFmpegコマンド
# ======================================================

command = [

"/usr/bin/ffmpeg",

"-y",

"-nostdin",

"-hide_banner",

"-loglevel",
"error",

"-i",
str(input_file),

"-map",
"0:v:0",

"-map",
"0:a:0?",

"-vf",
subtitles_filter,

"-c:v",
"libx264",

"-threads",
"1",

"-preset",
"ultrafast",

"-crf",
"28",

"-c:a",
"aac",

"-b:a",
"128k",

"-movflags",
"+faststart",

str(output_file)

]


# ======================================================
# コマンド表示
# ======================================================

print(
"==========================================",
flush=True
)


_log(
"FFmpeg command"
)


print(
" ".join(command),
flush=True
)


print(
"==========================================",
flush=True
)


# ======================================================
# FFmpeg開始
# ======================================================

_log(
"FFmpeg起動【1回だけ】"
)


_log(
"subprocess.run BEFORE"
)


try:

result = subprocess.run(

    command,

    stdout=subprocess.PIPE,

    stderr=subprocess.PIPE,

    text=True,

    timeout=120

)


except subprocess.TimeoutExpired:

_log(
    "FFmpeg TIMEOUT"
)


raise RuntimeError(
    "FFmpegが120秒以内に終了しませんでした"
)


except Exception as error:

_log(
    "subprocess.run ERROR"
)


_log(
    f"{type(error).__name__}: {error}"
)


raise


# ======================================================
# FFmpeg終了
# ======================================================

print(
"==========================================",
flush=True
)


_log(
"FFmpeg終了"
)


_log(
f"returncode: {result.returncode}"
)


print(
"==========================================",
flush=True
)


# ======================================================
# stderr
# ======================================================

if result.stderr:

_log(
    "FFmpeg stderr:"
)


print(
    result.stderr,
    flush=True
)


# ======================================================
# FFmpeg失敗
# ======================================================

if result.returncode != 0:

raise RuntimeError(
    "FFmpeg処理失敗 "
    f"(returncode={result.returncode})"
)


# ======================================================
# 出力確認
# ======================================================

_log(
"出力ファイル確認 START"
)


if not output_file.exists():

raise FileNotFoundError(
    "FFmpeg終了後も出力ファイルがありません: "
    f"{output_file}"
)


if not output_file.is_file():

raise FileNotFoundError(
    "FFmpeg出力がファイルではありません: "
    f"{output_file}"
)


output_size = (
output_file.stat().st_size
)


_log(
"出力ファイル確認 OK"
)


_log(
f"出力サイズ: {output_size} bytes"
)


# ======================================================
# 完了ログ
# ======================================================

print(
"==========================================",
flush=True
)


_log(
"COMPLETE"
)


print(
"==========================================",
flush=True
)


return output_file


# ==========================================================
# 単体テスト
#
# python subtitle_test_fonts.py
#
# ==========================================================

if __name__ == "__main__":

print(
"=========================================="
)


print(
"subtitle_test_fonts.py test"
)


print(
"=========================================="
)


try:

result = run_font_test()


print(
    "=========================================="
)


print(
    "TEST SUCCESS"
)


print(
    f"output: {result}"
)


print(
    "=========================================="
)


except Exception as error:

print(
    "=========================================="
)


print(
    "TEST FAILED"
)


print(
    f"ERROR TYPE: {type(error).__name__}"
)


print(
    f"ERROR: {error}"
)


print(
    "=========================================="
)


raise
