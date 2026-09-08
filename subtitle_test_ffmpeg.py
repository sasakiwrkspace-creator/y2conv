# =====================================
# subtitle_test_ffmpeg.py
#
# FFmpeg字幕焼き込み単体テスト
#
# 固定入力:
#   /app/downloads/test.mp4
#   /app/downloads/test.srt
#
# 出力:
#   /app/downloads/test_embed.mp4
#
# 目的:
#   Render環境で
#   FFmpeg + libass + 日本語フォント + SRT
#   による字幕焼き込みが最後まで完了するか確認する。
#
# =====================================

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


# =====================================
# 設定
# =====================================

BASE_DIR = Path(
    os.environ.get(
        "BASE_DIR",
        "/app"
    )
)

DOWNLOAD_DIR = Path(
    os.environ.get(
        "DOWNLOAD_DIR",
        str(BASE_DIR / "downloads")
    )
)

TEST_MP4_FILENAME = "test.mp4"
TEST_SRT_FILENAME = "test.srt"
OUTPUT_FILENAME = "test_embed.mp4"

TEST_MP4 = DOWNLOAD_DIR / TEST_MP4_FILENAME
TEST_SRT = DOWNLOAD_DIR / TEST_SRT_FILENAME
OUTPUT_MP4 = DOWNLOAD_DIR / OUTPUT_FILENAME


# =====================================
# FFmpeg設定
#
# まず一度通すことを優先して
# 解像度を640x360へ縮小する。
#
# 字幕焼き込み自体の確認が目的なので、
# 本番品質のエンコード設定ではない。
# =====================================

FFMPEG_TIMEOUT = 120

VIDEO_WIDTH = 640
VIDEO_HEIGHT = 360

VIDEO_THREADS = 1
VIDEO_PRESET = "ultrafast"
VIDEO_CRF = "28"


# =====================================
# ログ
# =====================================

def log(message: str = ""):
    print(
        f"[SUBTITLE TEST] {message}",
        flush=True
    )


def separator():
    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )


# =====================================
# モジュールロード確認
# =====================================

separator()
log("subtitle_test_ffmpeg.py MODULE LOAD COMPLETE")
log(f"Current working directory: {Path.cwd()}")
log(f"BASE_DIR: {BASE_DIR}")
log(f"DOWNLOAD_DIR: {DOWNLOAD_DIR}")
log(f"TEST_MP4: {TEST_MP4}")
log(f"TEST_SRT: {TEST_SRT}")
log(f"OUTPUT_MP4: {OUTPUT_MP4}")
separator()


# =====================================
# subtitle_font
# =====================================

try:

    import subtitle_font

    log("subtitle_font import OK")

except Exception as e:

    log("subtitle_font import FAILED")

    raise


# =====================================
# ファイル確認
# =====================================

def check_input_file(
    file_path: Path,
    expected_extension: str
):

    separator()
    log("入力ファイル確認開始")

    log(f"file_path: {file_path}")
    log(
        f"expected extension: "
        f"{expected_extension}"
    )

    resolved = file_path.resolve()

    log(f"resolved path: {resolved}")
    log(
        f"actual extension: "
        f"{resolved.suffix}"
    )

    if not resolved.exists():

        raise FileNotFoundError(
            f"入力ファイルが存在しません: "
            f"{resolved}"
        )

    if not resolved.is_file():

        raise RuntimeError(
            f"入力パスがファイルではありません: "
            f"{resolved}"
        )

    if resolved.suffix.lower() != expected_extension:

        raise ValueError(
            f"拡張子が不正です: "
            f"{resolved.suffix}"
        )

    size = resolved.stat().st_size

    log(f"file size: {size} bytes")

    if size <= 0:

        raise RuntimeError(
            f"ファイルサイズが0です: "
            f"{resolved}"
        )

    log("入力ファイル確認OK")

    return resolved


# =====================================
# SRT UTF-8確認
# =====================================

def check_srt_utf8(
    srt_path: Path
):

    separator()
    log("SRT UTF-8確認開始")

    try:

        text = srt_path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError as e:

        raise RuntimeError(
            f"SRTがUTF-8ではありません: {e}"
        )

    log(
        f"SRT先頭文字数: "
        f"{len(text[:100])}"
    )

    if not text.strip():

        raise RuntimeError(
            "SRTが空です"
        )

    log("SRT UTF-8確認OK")

    return text


# =====================================
# 字幕設定取得
# =====================================

def get_subtitle_settings():

    separator()
    log("字幕設定取得開始")

    default_settings = (
        subtitle_font
        .get_default_subtitle_font_settings()
    )

    log(
        f"default: "
        f"{default_settings}"
    )

    settings = (
        subtitle_font
        .select_subtitle_font(
            default_settings
        )
    )

    log(
        f"最終字幕設定: "
        f"{settings}"
    )

    return settings


# =====================================
# ASSカラー取得
# =====================================

def get_ass_color(
    color_name,
    default_color
):

    # subtitle_font.py 側に
    # カラー変換関数が存在する場合は使用する。

    candidates = [
        "get_ass_color",
        "color_to_ass",
        "convert_color_to_ass",
    ]

    for name in candidates:

        func = getattr(
            subtitle_font,
            name,
            None
        )

        if callable(func):

            try:

                result = func(
                    color_name
                )

                if result:

                    return result

            except Exception:

                pass

    return default_color


# =====================================
# 字幕フィルター生成
# =====================================

def create_subtitle_filter(
    srt_path: Path,
    settings: dict,
    font_path: Path | None
):

    separator()
    log("字幕フィルター作成開始")

    font_name = settings.get(
        "font",
        "Noto Sans CJK JP"
    )

    text_color = settings.get(
        "text_color",
        "白"
    )

    outline_color = settings.get(
        "outline_color",
        "青"
    )

    outline_width = settings.get(
        "outline_width",
        5
    )

    preset_name = settings.get(
        "preset_name",
        "標準"
    )

    # ---------------------------------
    # ASSカラー
    # ---------------------------------

    text_ass = get_ass_color(
        text_color,
        "&H00FFFFFF"
    )

    outline_ass = get_ass_color(
        outline_color,
        "&H00FF0000"
    )

    log(
        f"ASSカラー取得: "
        f"{text_color}"
    )

    log(
        f"ASSカラー取得: "
        f"{outline_color}"
    )

    # ---------------------------------
    # フォントディレクトリ
    # ---------------------------------

    if font_path is not None:

        font_dir = font_path.parent

    else:

        font_dir = Path(
            "/usr/share/fonts/opentype/noto"
        )

    log(
        f"最終FontName: {font_name}"
    )

    log(
        f"字幕フォントディレクトリ: "
        f"{font_dir}"
    )

    log("字幕スタイル:")
    log(f"preset_name: {preset_name}")
    log(f"font: {font_name}")
    log(f"text_color: {text_color}")
    log(f"text_color ASS: {text_ass}")
    log(f"outline_color: {outline_color}")
    log(
        f"outline_color ASS: "
        f"{outline_ass}"
    )
    log(
        f"outline_width: "
        f"{outline_width}"
    )

    # ---------------------------------
    # FFmpeg subtitles filter
    #
    # Pathはsubprocessへ渡すので
    # shellエスケープは不要。
    # ---------------------------------

    srt_for_filter = (
        str(srt_path)
        .replace("\\", "/")
        .replace("'", r"\'")
        .replace(":", r"\:")
    )

    font_dir_for_filter = (
        str(font_dir)
        .replace("\\", "/")
        .replace("'", r"\'")
        .replace(":", r"\:")
    )

    force_style = (
        f"FontName={font_name},"
        f"PrimaryColour={text_ass},"
        f"OutlineColour={outline_ass},"
        f"Outline={outline_width}"
    )

    video_filter = (
        f"subtitles='{srt_for_filter}'"
        f":fontsdir='{font_dir_for_filter}'"
        f":force_style='{force_style}'"
    )

    log(
        f"完成video_filter: "
        f"{video_filter}"
    )

    log("字幕フィルター作成完了")

    return video_filter


# =====================================
# FFmpeg確認
# =====================================

def check_ffmpeg():

    separator()
    log("FFmpeg確認開始")

    ffmpeg = shutil.which(
        "ffmpeg"
    )

    log(
        f"shutil.which(ffmpeg): "
        f"{ffmpeg}"
    )

    if not ffmpeg:

        raise RuntimeError(
            "FFmpegが見つかりません"
        )

    result = subprocess.run(
        [
            ffmpeg,
            "-version",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    log(
        f"FFmpeg version returncode: "
        f"{result.returncode}"
    )

    first_line = (
        result.stdout
        .splitlines()[0]
        if result.stdout
        else ""
    )

    log(
        f"FFmpeg version: "
        f"{first_line}"
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg version確認失敗"
        )

    log("FFmpeg確認完了")

    return ffmpeg


# =====================================
# FFmpeg機能確認
# =====================================

def check_ffmpeg_features(
    ffmpeg: str
):

    separator()
    log("FFmpeg機能確認")

    # ---------------------------------
    # libx264
    # ---------------------------------

    log("libx264確認開始")

    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-encoders",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )

    if (
        "libx264" not in
        result.stdout
    ):

        raise RuntimeError(
            "libx264が利用できません"
        )

    log("libx264: OK")

    # ---------------------------------
    # subtitles
    # ---------------------------------

    log(
        "subtitlesフィルター確認開始"
    )

    result = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-filters",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )

    if (
        "subtitles" not in
        result.stdout
    ):

        raise RuntimeError(
            "subtitlesフィルターが利用できません"
        )

    log(
        "subtitles filter: OK"
    )

    # ---------------------------------
    # libass
    # ---------------------------------

    log("libass確認開始")

    if (
        "libass" not in
        result.stdout
    ):

        log(
            "libass文字列をfilters一覧から"
            "確認できませんでした"
        )

    else:

        log("libass: OK")

    log(
        "FFmpeg機能確認完了"
    )


# =====================================
# 日本語フォント確認
# =====================================

def find_font(
    requested_font: str
):

    separator()
    log("日本語フォント検索開始")

    log(
        f"requested_font: "
        f"{requested_font}"
    )

    env_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    log(
        f"SUBTITLE_FONT: "
        f"{env_font}"
    )

    # ---------------------------------
    # 環境変数指定
    # ---------------------------------

    if env_font:

        candidate = Path(
            env_font
        )

        if candidate.exists():

            log(
                f"SUBTITLE_FONT使用: "
                f"{candidate}"
            )

            return candidate

    # ---------------------------------
    # fc-match
    # ---------------------------------

    fc_match = shutil.which(
        "fc-match"
    )

    if fc_match:

        result = subprocess.run(
            [
                fc_match,
                "-f",
                "%{file}\\n",
                requested_font,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        font_file = (
            result.stdout.strip()
        )

        log(
            f"fc-match: "
            f"{font_file}"
        )

        if font_file:

            path = Path(
                font_file
            )

            if path.exists():

                log(
                    f"font path: "
                    f"{path}"
                )

                return path

    # ---------------------------------
    # fallback
    # ---------------------------------

    candidates = [

        Path(
            "/usr/share/fonts/opentype/noto/"
            "NotoSansCJK-Regular.ttc"
        ),

        Path(
            "/usr/share/fonts/"
            "NotoSansCJK-Regular.ttc"
        ),

    ]

    for candidate in candidates:

        if candidate.exists():

            log(
                f"fallback font: "
                f"{candidate}"
            )

            return candidate

    raise RuntimeError(
        "日本語フォントが見つかりません"
    )


# =====================================
# ffprobeによる出力確認
# =====================================

def verify_output(
    ffprobe: str,
    output_path: Path
):

    separator()
    log("出力ファイル確認開始")

    if not output_path.exists():

        raise RuntimeError(
            "FFmpeg出力ファイルが存在しません"
        )

    size = output_path.stat().st_size

    log(
        f"出力ファイルサイズ: "
        f"{size} bytes"
    )

    if size <= 0:

        raise RuntimeError(
            "出力ファイルサイズが0です"
        )

    # ---------------------------------
    # ffprobe
    # ---------------------------------

    log("ffprobe確認開始")

    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-of",
            "default=noprint_wrappers=1",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )

    log(
        f"ffprobe returncode: "
        f"{result.returncode}"
    )

    if result.stdout:

        for line in result.stdout.splitlines():

            log(
                f"ffprobe: {line}"
            )

    if result.stderr:

        for line in result.stderr.splitlines():

            log(
                f"ffprobe stderr: {line}"
            )

    if result.returncode != 0:

        raise RuntimeError(
            "出力MP4のffprobe確認に失敗しました"
        )

    log(
        "出力ファイル確認OK"
    )


# =====================================
# FFmpeg実行
# =====================================
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

def run_ffmpeg(
    ffmpeg: str,
    command: list[str],
    temporary_output: Path
):

    separator()
    log("FFmpeg開始")
    separator()

    log("FFmpeg command:")
    log(
        " ".join(
            str(x)
            for x in command
        )
    )

    start_time = time.monotonic()

    process = None
    output_lines = []

    try:

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        log(
            f"FFmpeg PID: {process.pid}"
        )

        assert process.stdout is not None

        # =====================================
        # FFmpegログ取得
        # =====================================

        while True:

            line = process.stdout.readline()

            if line:

                line = line.rstrip()

                output_lines.append(line)

                print(
                    f"[FFMPEG] {line}",
                    flush=True
                )

                continue

            # =================================
            # stdout EOF
            # =================================

            returncode = process.poll()

            if returncode is not None:

                break

            # =================================
            # timeout確認
            # =================================

            elapsed = (
                time.monotonic()
                - start_time
            )

            if elapsed > FFMPEG_TIMEOUT:

                log(
                    "FFmpeg TIMEOUT"
                )

                log(
                    f"経過時間: "
                    f"{elapsed:.2f}秒"
                )

                log(
                    f"FFmpeg poll: "
                    f"{process.poll()}"
                )

                try:

                    process.kill()

                    log(
                        "FFmpeg kill() 実行"
                    )

                except Exception as e:

                    log(
                        f"kill失敗: {e}"
                    )

                try:

                    process.wait(
                        timeout=10
                    )

                except Exception as e:

                    log(
                        f"wait失敗: {e}"
                    )

                raise TimeoutError(
                    f"FFmpegが"
                    f"{FFMPEG_TIMEOUT}秒以内に"
                    f"終了しませんでした"
                )

        # =====================================
        # 終了情報
        # =====================================

        elapsed = (
            time.monotonic()
            - start_time
        )

        separator()

        log(
            "FFmpegプロセス終了を検出"
        )

        log(
            f"FFmpeg returncode: "
            f"{returncode}"
        )

        log(
            f"FFmpeg経過時間: "
            f"{elapsed:.3f}秒"
        )

        # =====================================
        # 負のreturncode
        # =====================================

        if returncode < 0:

            signal_number = -returncode

            log(
                "FFmpegがシグナルによって"
                "終了しました"
            )

            log(
                f"signal: "
                f"{signal_number}"
            )

            if signal_number == 9:

                log(
                    "SIGKILL (9) で終了しています"
                )

            elif signal_number == 15:

                log(
                    "SIGTERM (15) で終了しています"
                )

            raise RuntimeError(
                "FFmpegがシグナルによって"
                f"終了しました "
                f"(returncode={returncode}, "
                f"signal={signal_number})"
            )

        # =====================================
        # returncode != 0
        # =====================================

        if returncode != 0:

            log(
                "FFmpeg FAILED"
            )

            log(
                "FFmpeg最後のログ:"
            )

            for line in output_lines[-50:]:

                log(
                    f"  {line}"
                )

            raise RuntimeError(
                "FFmpeg字幕焼き込みに失敗しました "
                f"(returncode={returncode})"
            )

        # =====================================
        # 成功
        # =====================================

        log(
            "FFmpeg returncode=0"
        )

        if not temporary_output.exists():

            raise RuntimeError(
                "FFmpegは成功しましたが、"
                "一時出力ファイルがありません"
            )

        temporary_size = (
            temporary_output.stat().st_size
        )

        log(
            f"一時出力サイズ: "
            f"{temporary_size} bytes"
        )

        if temporary_size <= 0:

            raise RuntimeError(
                "FFmpeg一時出力サイズが0です"
            )

        log(
            "FFmpeg字幕焼き込み成功"
        )

        return returncode

    except Exception as e:

        separator()

        log(
            "run_ffmpeg EXCEPTION"
        )

        log(
            f"ERROR TYPE: "
            f"{type(e).__name__}"
        )

        log(
            f"ERROR: "
            f"{e}"
        )

        if process is not None:

            try:

                current_returncode = (
                    process.poll()
                )

                log(
                    f"FFmpeg poll: "
                    f"{current_returncode}"
                )

            except Exception as poll_error:

                log(
                    f"poll失敗: "
                    f"{poll_error}"
                )

        raise

# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# =====================================
# メイン処理
# =====================================

def run_ffmpeg_subtitle_test():

    separator()
    log(
        "FFmpeg字幕焼き込みテスト START"
    )
    separator()

    temporary_output = None

    try:

        # =================================
        # STEP 1
        # =================================

        separator()
        log("STEP 1: 固定入力ファイル決定")
        separator()

        log(
            f"固定MP4: {TEST_MP4}"
        )

        log(
            f"固定SRT: {TEST_SRT}"
        )

        # =================================
        # STEP 2
        # =================================

        separator()
        log("STEP 2: MP4確認")
        separator()

        mp4_path = check_input_file(
            TEST_MP4,
            ".mp4"
        )

        # =================================
        # STEP 3
        # =================================

        separator()
        log("STEP 3: SRT確認")
        separator()

        srt_path = check_input_file(
            TEST_SRT,
            ".srt"
        )

        # =================================
        # STEP 4
        # =================================

        separator()
        log("STEP 4: SRT UTF-8確認")
        separator()

        check_srt_utf8(
            srt_path
        )

        # =================================
        # STEP 5
        # =================================

        separator()
        log(
            "STEP 5: subtitle_font.py設定取得"
        )
        separator()

        settings = (
            get_subtitle_settings()
        )

        # =================================
        # STEP 6
        # =================================

        separator()
        log("STEP 6: 出力先決定")
        separator()

        log(
            f"最終出力: "
            f"{OUTPUT_MP4}"
        )

        # =================================
        # STEP 7
        # =================================

        separator()
        log("STEP 7: FFmpeg確認")
        separator()

        ffmpeg = check_ffmpeg()

        check_ffmpeg_features(
            ffmpeg
        )

        log(
            f"使用FFmpeg: "
            f"{ffmpeg}"
        )

        # =================================
        # STEP 8
        # =================================

        separator()
        log("STEP 8: 日本語フォント確認")
        separator()

        requested_font = settings.get(
            "font",
            "Noto Sans CJK JP"
        )

        font_path = find_font(
            requested_font
        )

        log(
            f"font path: "
            f"{font_path}"
        )

        # =================================
        # STEP 9
        # =================================

        separator()
        log("STEP 9: 字幕フィルター生成")
        separator()

        video_filter = (
            create_subtitle_filter(
                srt_path,
                settings,
                font_path
            )
        )

        # =================================
        # STEP 10
        # =================================

        separator()
        log("STEP 10: 入力サイズ確認")
        separator()

        input_size = (
            mp4_path.stat().st_size
        )

        log(
            f"入力MP4サイズ: "
            f"{input_size} bytes"
        )

        # =================================
        # STEP 11
        # 一時ファイル
        # =================================

        separator()
        log("STEP 11: 一時出力パス生成")
        separator()

        DOWNLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        temp_file = tempfile.NamedTemporaryFile(
            prefix=".test_embed.",
            suffix=".tmp.mp4",
            dir=str(DOWNLOAD_DIR),
            delete=False,
        )

        temporary_output = Path(
            temp_file.name
        )

        temp_file.close()

        log(
            f"一時出力パス: "
            f"{temporary_output}"
        )

        # =================================
        # 既存出力削除
        # =================================

        if OUTPUT_MP4.exists():

            log(
                "既存test_embed.mp4を削除"
            )

            OUTPUT_MP4.unlink()

        # =================================
        # STEP 12
        # FFmpegコマンド
        # =================================

        separator()
        log("STEP 12: FFmpegコマンド生成")
        separator()

        log(
            "FFmpeg設定:"
        )

        log(
            f"width: {VIDEO_WIDTH}"
        )

        log(
            f"height: {VIDEO_HEIGHT}"
        )

        log(
            f"threads: {VIDEO_THREADS}"
        )

        log(
            f"preset: {VIDEO_PRESET}"
        )

        log(
            f"crf: {VIDEO_CRF}"
        )

        log(
            f"timeout: {FFMPEG_TIMEOUT}"
        )

        log(
            "video filter:"
        )

        log(
            video_filter
        )

        # ---------------------------------
        # 軽量テスト
        #
        # 640x360へ縮小して字幕焼き込み。
        # ---------------------------------

        command = [

            ffmpeg,

            "-y",

            "-nostdin",

            "-hide_banner",

            "-loglevel",
            "info",

            "-i",
            str(mp4_path),

            "-vf",
            (
                f"scale="
                f"{VIDEO_WIDTH}:"
                f"{VIDEO_HEIGHT},"
                f"{video_filter}"
            ),

            "-c:v",
            "libx264",

            "-threads",
            str(VIDEO_THREADS),

            "-preset",
            VIDEO_PRESET,

            "-crf",
            VIDEO_CRF,

            "-c:a",
            "copy",

            "-movflags",
            "+faststart",

            str(temporary_output),
        ]

        log(
            "FFmpeg command:"
        )

        log(
            " ".join(
                str(x)
                for x in command
            )
        )

        # =================================
        # STEP 13
        # FFmpeg開始
        # =================================

        separator()
        log("STEP 13: FFmpeg開始")
        separator()

        run_ffmpeg(
            ffmpeg,
            command,
            temporary_output
        )

        # =================================
        # STEP 14
        # 完成ファイル移動
        # =================================

        separator()
        log("STEP 14: 完成ファイル確定")
        separator()

        if OUTPUT_MP4.exists():

            OUTPUT_MP4.unlink()

        temporary_output.replace(
            OUTPUT_MP4
        )

        temporary_output = None

        log(
            f"完成ファイル: "
            f"{OUTPUT_MP4}"
        )

        # =================================
        # STEP 15
        # 出力確認
        # =================================

        separator()
        log("STEP 15: 出力MP4確認")
        separator()

        ffprobe = shutil.which(
            "ffprobe"
        )

        if not ffprobe:

            raise RuntimeError(
                "ffprobeが見つかりません"
            )

        verify_output(
            ffprobe,
            OUTPUT_MP4
        )

        # =================================
        # SUCCESS
        # =================================

        separator()
        separator()

        log(
            "FFmpeg字幕焼き込みテスト SUCCESS"
        )

        log(
            f"OUTPUT: {OUTPUT_MP4}"
        )

        log(
            f"OUTPUT SIZE: "
            f"{OUTPUT_MP4.stat().st_size} bytes"
        )

        separator()
        separator()

        return {
            "success": True,
            "message": (
                "FFmpeg字幕焼き込みテスト成功"
            ),
            "output": str(
                OUTPUT_MP4
            ),
            "size": OUTPUT_MP4.stat().st_size,
        }

    except Exception as e:

        # =================================
        # ERROR
        # =================================

        separator()
        log(
            "FFmpeg字幕焼き込みテスト FAILED"
        )
        separator()

        log(
            f"ERROR TYPE: "
            f"{type(e).__name__}"
        )

        log(
            f"ERROR: "
            f"{e}"
        )

        # ---------------------------------
        # 一時ファイル削除
        # ---------------------------------

        if (
            temporary_output is not None
            and temporary_output.exists()
        ):

            try:

                log(
                    "一時ファイル削除"
                )

                temporary_output.unlink()

            except Exception as cleanup_error:

                log(
                    f"一時ファイル削除失敗: "
                    f"{cleanup_error}"
                )

        separator()

        # ルート側でJSONエラーへ変換できるよう
        # 例外をそのまま投げる。

        raise


# =====================================
# 直接実行
# =====================================

if __name__ == "__main__":

    log(
        "直接実行モード"
    )

    result = run_ffmpeg_subtitle_test()

    print(
        result,
        flush=True
    )
