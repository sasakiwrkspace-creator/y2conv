# ==========================================================
# Subtitle - Test Compatible Edition
# subtitle.py
#
# MP4動画へSRT字幕を焼き込む
#
# subtitle_test.py と同じ条件で動作確認するための版
#
# テスト入力:
#   /app/downloads/test.mp4
#   /app/downloads/test.srt
#
# テスト出力:
#   /app/downloads/test_sub_embed.mp4
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

DOWNLOADS_DIR = Path(
    DOWNLOAD_DIR
).resolve()

MAX_FFMPEG_LOG_LINES = 100

FFMPEG_THREADS = "1"
FFMPEG_PRESET = "ultrafast"
FFMPEG_CRF = "23"

SUBTITLE_SETTING_KEYS = (
    "preset_name",
    "font",
    "text_color",
    "outline_color",
    "outline_width",
)


# ==========================================================
# 初期ログ
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
            round(float(seconds))
        )
    except (
        ValueError,
        TypeError,
    ):
        seconds = 0

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ==========================================================
# Downloads確認
# ==========================================================

def ensure_downloads_directory():

    log(
        "downloadsフォルダ確認開始"
    )

    try:

        DOWNLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    except OSError as error:

        log_exception(
            "downloadsフォルダ作成失敗",
            error,
        )

        raise RuntimeError(
            "downloadsフォルダを作成できませんでした: "
            + str(error)
        ) from error

    log(
        f"downloadsフォルダ確認OK: "
        f"{DOWNLOADS_DIR}"
    )

    return DOWNLOADS_DIR


# ==========================================================
# ファイル入力確認
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

    path = (
        Path(file_path)
        .expanduser()
        .resolve()
    )

    if not path.exists():

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"ファイルではありません: {path}"
        )

    if path.suffix.lower() != extension.lower():

        raise ValueError(
            f"{extension}ファイルではありません: {path}"
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
# SRT UTF-8確認
# ==========================================================

def validate_srt_encoding(srt_path):

    log_start(
        "SRT UTF-8確認開始"
    )

    try:

        with open(
            srt_path,
            "r",
            encoding="utf-8-sig",
        ) as file:

            content = file.read(4096)

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

    if not content.strip():

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    try:
        size = srt_path.stat().st_size
    except OSError:
        size = 0

    log(
        f"SRTサイズ: {size} bytes"
    )

    log(
        "SRT UTF-8確認完了"
    )


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
        )

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

    lines = result.stdout.splitlines()

    if lines:

        log(
            f"FFmpeg version: {lines[0]}"
        )

    # ------------------------------------------------------
    # libx264
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

    encoder_text = (
        encoder_result.stdout
        +
        encoder_result.stderr
    )

    if (
        encoder_result.returncode != 0
        or
        "libx264" not in encoder_text
    ):

        raise RuntimeError(
            "FFmpegにlibx264エンコーダーがありません。"
        )

    log(
        "libx264: OK"
    )

    # ------------------------------------------------------
    # subtitles filter
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

    filter_text = (
        filter_result.stdout
        +
        filter_result.stderr
    )

    if (
        filter_result.returncode != 0
        or
        "subtitles" not in filter_text
    ):

        raise RuntimeError(
            "FFmpegにsubtitlesフィルターがありません。"
        )

    log(
        "subtitles filter: OK"
    )

    log(
        "FFmpeg確認完了"
    )

    return ffmpeg_path


# ==========================================================
# フォントfamily
# ==========================================================

def get_font_family_from_path(font_path):

    fc_scan = shutil.which(
        "fc-scan"
    )

    if not fc_scan:
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

        return {
            "path": font_path.resolve(),
            "family": family,
        }

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

    environment_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    if environment_font:

        path = (
            Path(environment_font)
            .expanduser()
            .resolve()
        )

        if path.is_file():

            return {
                "path": path,
                "family": get_font_family_from_path(
                    path
                ),
            }

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

            return {
                "path": requested_path,
                "family": get_font_family_from_path(
                    requested_path
                ),
            }

        matched = fc_match_font(
            requested_font
        )

        if matched:
            return matched

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
                f"日本語フォント検出: {matched}"
            )

            return matched

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

                font_path = Path(
                    font_file
                )

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

                for match in directory.rglob(
                    font_name
                ):

                    if not match.is_file():
                        continue

                    return {
                        "path": match.resolve(),
                        "family":
                            get_font_family_from_path(
                                match
                            ),
                    }

            except Exception as error:

                log_exception(
                    f"フォント検索エラー: {directory}",
                    error,
                )

    return None


# ==========================================================
# FFmpeg filter path
# ==========================================================

def escape_ffmpeg_filter_path(
    file_path
):

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
# FFmpeg value
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
# ASSカラー
# ==========================================================

def get_ass_color(color_name):

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
# 字幕設定
# ==========================================================

def normalize_subtitle_settings(
    subtitle_settings=None
):

    log_start(
        "字幕設定正規化開始"
    )

    if subtitle_settings is None:

        settings = (
            get_default_subtitle_font_settings()
        )

        if not isinstance(
            settings,
            dict,
        ):

            raise RuntimeError(
                "subtitle_font.pyの標準設定がdictではありません。"
            )

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

        settings = select_subtitle_font(
            settings=subtitle_settings
        )

    if not isinstance(
        settings,
        dict,
    ):

        raise RuntimeError(
            "select_subtitle_font()の戻り値がdictではありません。"
        )

    normalized = {}

    for key in SUBTITLE_SETTING_KEYS:

        normalized[key] = settings.get(
            key
        )

    log(
        f"最終字幕設定: {normalized!r}"
    )

    return normalized


# ==========================================================
# 字幕フィルター
# ==========================================================

def make_subtitle_filter(
    srt_path,
    font_info=None,
    subtitle_settings=None,
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
        + subtitle_path
        + "'"
    )

    font = subtitle_settings.get(
        "font"
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

        font_name = str(
            font
        ).strip()

    if not font_name:

        raise RuntimeError(
            "字幕フォント名を決定できませんでした。"
        )

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
        str(outline_width),

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
        f"完成video_filter: {video_filter}"
    )

    return video_filter


# ==========================================================
# コマンド表示
# ==========================================================

def command_to_string(command):

    return " ".join(
        str(item)
        for item in command
    )


# ==========================================================
# FFmpegエラー
# ==========================================================

def make_ffmpeg_error_detail(lines):

    if not lines:

        return (
            "FFmpegからエラー内容が返されませんでした。"
        )

    return "\n".join(
        lines
    )


# ==========================================================
# ファイル削除
# ==========================================================

def remove_file_safely(file_path):

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
# FFmpeg終了
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
# FFmpeg stderr
# ==========================================================

def collect_ffmpeg_output(
    process,
    output_lines,
):

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
                Path(output_path)
                .expanduser()
                .resolve()
            )

        else:

            output_path = (
                mp4_path.parent
                /
                "test_sub_embed.mp4"
            ).resolve()

        log(
            f"出力パス: {output_path}"
        )

        # ==================================================
        # STEP 6 f"{mp4_path.stem}_sub_embed.mp4"
        # ==================================================

        log_start(
            "STEP 6: 出力フォルダ確認"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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

        input_mp4_size = (
            mp4_path.stat().st_size
        )

        log(
            f"入力MP4サイズ: "
            f"{input_mp4_size} bytes"
        )

        # ==================================================
        # STEP 11
        # ==================================================

        log_start(
            "STEP 11: 一時出力パス生成"
        )

        timestamp = time.time_ns()

        temp_output_path = (
            output_path.parent
            /
            (
                "."
                + output_path.stem
                + f".subtitle_{timestamp}.tmp.mp4"
            )
        )

        log(
            f"一時出力パス: "
            f"{temp_output_path}"
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
            -
            start_time
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

            error_detail = (
                make_ffmpeg_error_detail(
                    ffmpeg_output_lines
                )
            )

            raise RuntimeError(
                "字幕焼き込みに失敗しました。"
                "\n\n"
                +
                error_detail
                +
                "\n\n"
                "FFmpeg return code: "
                +
                str(return_code)
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

        output_size = (
            temp_output_path.stat().st_size
        )

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

        os.replace(
            str(temp_output_path),
            str(output_path),
        )

        temp_output_path = None

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

        final_size = (
            output_path.stat().st_size
        )

        if final_size <= 0:

            remove_file_safely(
                output_path
            )

            raise RuntimeError(
                "正式出力ファイルのサイズが0です。"
            )

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
# subtitle_test.py から呼ばれる正式関数
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
# 互換関数
# ==========================================================

def create_burned_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None,
):

    return create_subtitle_mp4(
        mp4_path,
        srt_path,
        output_path,
        subtitle_settings,
    )


def burn_subtitles(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None,
):

    return create_subtitle_mp4(
        mp4_path,
        srt_path,
        output_path,
        subtitle_settings,
    )


# ==========================================================
# Downloads内から実行
# ==========================================================

def embed_from_downloads(
    mp4_filename,
    srt_filename,
    subtitle_settings=None,
):

    mp4_filename = Path(
        mp4_filename
    ).name

    srt_filename = Path(
        srt_filename
    ).name

    ensure_downloads_directory()

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

    return embed_subtitle(
        mp4_path,
        srt_path,
        subtitle_settings=subtitle_settings,
    )


# ==========================================================
# CLI
# ==========================================================

def main():

    log(
        "subtitle.py main()開始"
    )

    log(
        f"sys.argv: {sys.argv!r}"
    )

    # ------------------------------------------------------
    # 引数なしの場合
    #
    # 今回のテストでは test.mp4 / test.srt を使用
    # ------------------------------------------------------

    if len(sys.argv) < 3:

        mp4_filename = "test.mp4"
        srt_filename = "test.srt"

        log(
            "引数未指定"
        )

        log(
            "テスト用デフォルト:"
        )

        log(
            f"MP4: {mp4_filename}"
        )

        log(
            f"SRT: {srt_filename}"
        )

    else:

        mp4_filename = sys.argv[1]
        srt_filename = sys.argv[2]

    start_time = time.monotonic()

    try:

        log(
            "STEP MAIN-1: "
            "subtitle_font.pyから標準設定取得開始"
        )

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

        if not isinstance(
            subtitle_settings,
            dict,
        ):

            raise RuntimeError(
                "subtitle_font.pyの標準設定がdictではありません。"
            )

        log(
            f"subtitle_settings: "
            f"{subtitle_settings!r}"
        )

        log(
            "STEP MAIN-2: embed_from_downloads開始"
        )

        output_path = embed_from_downloads(

            mp4_filename,

            srt_filename,

            subtitle_settings,

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
            f"入力MP4: {mp4_filename}"
        )

        print(
            f"入力SRT: {srt_filename}"
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
            f"出力: {output_path.name}"
        )

        print(
            f"出力パス: {output_path}"
        )

        print(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        print(
            "====================================="
        )

        print()

        return 0

    except Exception as error:

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log_exception(
            "main()で例外が発生しました。",
            error,
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
            file=sys.stderr,
        )

        print(
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            ),
            file=sys.stderr,
        )

        print(
            "====================================="
        )

        print()

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
