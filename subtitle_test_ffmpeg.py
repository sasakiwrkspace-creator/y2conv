# =====================================
# subtitle_test_ffmpeg.py
#
# FFmpeg字幕焼き込み単体テスト
#
# 固定ファイル:
#   downloads/test.mp4
#   downloads/test.srt
#
# 出力:
#   downloads/test_embed.mp4
#
# 目的:
#   ・FFmpeg存在確認
#   ・libx264確認
#   ・subtitles filter確認
#   ・libass確認
#   ・日本語フォント確認
#   ・SRT UTF-8確認
#   ・字幕焼き込み実行
#   ・FFmpeg終了コード確認
#   ・出力ファイル確認
#
# テストでは負荷を抑えるため
# 640x360 に縮小してエンコードする。
# =====================================


from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import time


# =====================================
# config
# =====================================

try:
    import config

    DOWNLOAD_DIR = Path(
        config.DOWNLOAD_DIR
    )

except Exception:

    DOWNLOAD_DIR = Path(
        os.getcwd()
    ) / "downloads"


# =====================================
# 定数
# =====================================

TEST_MP4_FILENAME = "test.mp4"
TEST_SRT_FILENAME = "test.srt"
TEST_OUTPUT_FILENAME = "test_embed.mp4"

FFMPEG_TIMEOUT = 60

TEST_WIDTH = 640
TEST_HEIGHT = 360


# =====================================
# ログ
# =====================================

def log(message=""):

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

log(
    "subtitle_test_ffmpeg.py MODULE LOAD COMPLETE"
)

log(
    f"Current working directory: {Path.cwd()}"
)

log(
    f"DOWNLOAD_DIR: {DOWNLOAD_DIR}"
)

separator()


# =====================================
# 入力ファイル確認
# =====================================

def check_input_file(
    file_path,
    expected_extension
):

    separator()

    log("入力ファイル確認開始")

    path = Path(file_path)

    log(f"file_path: {path}")
    log(
        f"expected extension: {expected_extension}"
    )

    try:
        resolved = path.resolve()

    except Exception:
        resolved = path

    log(
        f"resolved path: {resolved}"
    )

    actual_extension = (
        resolved.suffix.lower()
    )

    log(
        f"actual extension: {actual_extension}"
    )

    if not resolved.exists():

        raise FileNotFoundError(
            f"入力ファイルが存在しません: {resolved}"
        )

    if not resolved.is_file():

        raise RuntimeError(
            f"入力パスがファイルではありません: {resolved}"
        )

    if actual_extension != expected_extension:

        raise ValueError(
            "拡張子が不正です: "
            f"{actual_extension} "
            f"(expected {expected_extension})"
        )

    size = resolved.stat().st_size

    log(
        f"file size: {size} bytes"
    )

    if size <= 0:

        raise RuntimeError(
            f"ファイルサイズが0です: {resolved}"
        )

    log("入力ファイル確認OK")

    separator()

    return resolved


# =====================================
# SRT UTF-8確認
# =====================================

def check_srt_utf8(
    srt_path
):

    separator()

    log("SRT UTF-8確認開始")

    path = Path(srt_path)

    try:

        text = path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError as e:

        raise RuntimeError(
            f"SRTがUTF-8ではありません: {e}"
        )

    except Exception as e:

        raise RuntimeError(
            f"SRT読み込み失敗: {e}"
        )

    log(
        f"SRT先頭文字数: {len(text[:500])}"
    )

    if not text.strip():

        raise RuntimeError(
            "SRTが空です"
        )

    log("SRT UTF-8確認OK")

    separator()

    return text


# =====================================
# FFmpeg取得
# =====================================

def get_ffmpeg():

    separator()

    log("FFmpeg確認開始")

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    log(
        f"shutil.which(ffmpeg): {ffmpeg_path}"
    )

    if not ffmpeg_path:

        raise RuntimeError(
            "ffmpeg がPATHに存在しません"
        )

    result = subprocess.run(
        [
            ffmpeg_path,
            "-version"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10
    )

    log(
        f"FFmpeg version returncode: "
        f"{result.returncode}"
    )

    first_line = (
        result.stdout.strip().splitlines()
    )

    if first_line:

        log(
            f"FFmpeg version: {first_line[0]}"
        )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg起動確認に失敗しました"
        )

    log("FFmpeg確認完了")

    separator()

    return ffmpeg_path


# =====================================
# FFmpeg機能確認
# =====================================

def check_ffmpeg_features(
    ffmpeg_path
):

    separator()

    log("FFmpeg機能確認")

    # ---------------------------------
    # libx264
    # ---------------------------------

    log("libx264確認開始")

    result = subprocess.run(
        [
            ffmpeg_path,
            "-hide_banner",
            "-encoders"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10
    )

    encoder_text = (
        result.stdout +
        "\n" +
        result.stderr
    )

    if "libx264" not in encoder_text:

        raise RuntimeError(
            "libx264 がFFmpegに存在しません"
        )

    log("libx264: OK")

    # ---------------------------------
    # subtitles
    # ---------------------------------

    log("subtitlesフィルター確認開始")

    result = subprocess.run(
        [
            ffmpeg_path,
            "-hide_banner",
            "-filters"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10
    )

    filter_text = (
        result.stdout +
        "\n" +
        result.stderr
    )

    if "subtitles" not in filter_text:

        raise RuntimeError(
            "subtitles filter が存在しません"
        )

    log("subtitles filter: OK")

    # ---------------------------------
    # libass
    # ---------------------------------

    log("libass確認開始")

    result = subprocess.run(
        [
            ffmpeg_path,
            "-hide_banner",
            "-filters"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10
    )

    # subtitles filterが存在していれば
    # 通常libass対応済み。
    # 念のためffmpeg configurationも確認する。

    version_result = subprocess.run(
        [
            ffmpeg_path,
            "-version"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10
    )

    configuration = (
        version_result.stdout +
        "\n" +
        version_result.stderr
    )

    if (
        "libass" not in configuration
        and "subtitles" not in filter_text
    ):

        raise RuntimeError(
            "libass対応を確認できません"
        )

    log("libass: OK")

    log("FFmpeg機能確認完了")

    separator()


# =====================================
# 日本語フォント確認
# =====================================

def find_japanese_font(
    requested_font
):

    separator()

    log("日本語フォント検索開始")

    log(
        f"requested_font: {requested_font}"
    )

    env_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    log(
        f"SUBTITLE_FONT: {env_font}"
    )

    fc_match = shutil.which(
        "fc-match"
    )

    if not fc_match:

        raise RuntimeError(
            "fc-match が存在しません"
        )

    result = subprocess.run(
        [
            fc_match,
            "-f",
            "%{file}\\n",
            requested_font
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10
    )

    font_path_text = (
        result.stdout.strip()
    )

    log(
        f"fc-match: {font_path_text}"
    )

    if not font_path_text:

        raise RuntimeError(
            "日本語フォントを取得できません"
        )

    font_path = Path(
        font_path_text.splitlines()[0]
    )

    if not font_path.exists():

        raise RuntimeError(
            f"フォントファイルが存在しません: "
            f"{font_path}"
        )

    # family取得

    result = subprocess.run(
        [
            fc_match,
            "-f",
            "%{family}\\n",
            requested_font
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=10
    )

    family = (
        result.stdout.strip()
    )

    log(
        f"font path: {font_path}"
    )

    log(
        f"font family: {family}"
    )

    separator()

    return font_path, family


# =====================================
# 字幕設定取得
# =====================================

def get_subtitle_settings():

    separator()

    log("字幕設定取得開始")

    try:

        import subtitle_font

    except Exception as e:

        raise RuntimeError(
            "subtitle_font.py のimportに失敗しました: "
            f"{e}"
        )

    default_settings = (
        subtitle_font
        .get_default_subtitle_font_settings()
    )

    log(
        f"default: {default_settings}"
    )

    settings = (
        subtitle_font
        .select_subtitle_font(
            default_settings
        )
    )

    log(
        f"最終字幕設定: {settings}"
    )

    separator()

    return settings


# =====================================
# ASSカラー
# =====================================

def get_ass_color(
    color_name
):

    colors = {

        "白": "&H00FFFFFF",

        "黒": "&H00000000",

        "赤": "&H000000FF",

        "青": "&H00FF0000",

        "緑": "&H0000FF00",

        "黄": "&H0000FFFF",

    }

    if color_name not in colors:

        log(
            f"未知の色です。白を使用: "
            f"{color_name}"
        )

        return colors["白"]

    return colors[
        color_name
    ]


# =====================================
# 字幕フィルター生成
# =====================================

def create_subtitle_filter(
    srt_path,
    settings,
    font_path
):

    separator()

    log("字幕フィルター作成開始")

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

    font_name = settings.get(
        "font",
        "Noto Sans CJK JP"
    )

    text_color_ass = get_ass_color(
        text_color
    )

    outline_color_ass = get_ass_color(
        outline_color
    )

    font_dir = font_path.parent

    log(
        f"ASSカラー取得: {text_color}"
    )

    log(
        f"ASSカラー取得: {outline_color}"
    )

    log(
        f"最終FontName: {font_name}"
    )

    log(
        f"字幕フォントディレクトリ: "
        f"{font_dir}"
    )

    # ---------------------------------
    # Windows / Linux 共通のため
    # SRTパス内の特殊文字を最低限
    # エスケープ
    # ---------------------------------

    srt_string = str(
        srt_path
    ).replace(
        "\\",
        "/"
    )

    font_dir_string = str(
        font_dir
    ).replace(
        "\\",
        "/"
    )

    force_style = (
        f"FontName={font_name},"
        f"PrimaryColour={text_color_ass},"
        f"OutlineColour={outline_color_ass},"
        f"Outline={outline_width}"
    )

    video_filter = (
        f"subtitles='{srt_string}'"
        f":fontsdir='{font_dir_string}'"
        f":force_style='{force_style}'"
    )

    log("字幕スタイル:")

    log(
        f"preset_name: "
        f"{settings.get('preset_name')}"
    )

    log(
        f"font: {font_name}"
    )

    log(
        f"text_color: {text_color}"
    )

    log(
        f"text_color ASS: {text_color_ass}"
    )

    log(
        f"outline_color: {outline_color}"
    )

    log(
        f"outline_color ASS: "
        f"{outline_color_ass}"
    )

    log(
        f"outline_width: {outline_width}"
    )

    log(
        f"完成video_filter: {video_filter}"
    )

    log("字幕フィルター作成完了")

    separator()

    return video_filter


# =====================================
# FFmpeg実行
# =====================================

def run_ffmpeg(
    ffmpeg_path,
    input_mp4,
    output_tmp,
    video_filter
):

    separator()

    log("FFmpegコマンド生成")

    log(
        f"TEST解像度: "
        f"{TEST_WIDTH}x{TEST_HEIGHT}"
    )

    log(
        f"FFmpeg timeout: "
        f"{FFMPEG_TIMEOUT}秒"
    )

    command = [

        ffmpeg_path,

        "-y",

        "-nostdin",

        "-hide_banner",

        "-loglevel",

        "info",

        "-i",

        str(input_mp4),

        "-vf",

        video_filter,

        # ---------------------------------
        # テストなので軽量化
        # ---------------------------------

        "-vf",

        (
            f"scale="
            f"{TEST_WIDTH}:"
            f"{TEST_HEIGHT},"
            f"{video_filter}"
        ),

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

        "96k",

        "-movflags",

        "+faststart",

        str(output_tmp)

    ]

    log(
        "FFmpeg command:"
    )

    log(
        " ".join(
            command
        )
    )

    separator()

    log("FFmpeg開始")

    start_time = time.monotonic()

    try:

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

    except Exception as e:

        raise RuntimeError(
            f"FFmpeg起動失敗: {e}"
        )

    log(
        f"FFmpeg PID: {process.pid}"
    )

    separator()

    log("FFmpegログ取得")

    try:

        while True:

            line = process.stdout.readline()

            if line:

                print(
                    f"[FFMPEG] "
                    f"{line.rstrip()}",
                    flush=True
                )

            elif process.poll() is not None:

                break

            # ---------------------------------
            # timeout
            # ---------------------------------

            elapsed = (
                time.monotonic()
                - start_time
            )

            if elapsed > FFMPEG_TIMEOUT:

                log(
                    "FFmpeg TIMEOUT"
                )

                try:

                    process.kill()

                except Exception:
                    pass

                process.wait(
                    timeout=5
                )

                raise TimeoutError(
                    "FFmpeg字幕焼き込みが"
                    f"{FFMPEG_TIMEOUT}秒を超えました"
                )

        return_code = (
            process.returncode
        )

    except TimeoutError:

        raise

    except Exception as e:

        try:

            process.kill()

        except Exception:
            pass

        try:

            process.wait(
                timeout=5
            )

        except Exception:
            pass

        raise RuntimeError(
            f"FFmpegログ取得中にエラー: {e}"
        )

    elapsed = (
        time.monotonic()
        - start_time
    )

    separator()

    log(
        f"FFmpeg終了 returncode: "
        f"{return_code}"
    )

    log(
        f"FFmpeg実行時間: "
        f"{elapsed:.2f} 秒"
    )

    # ---------------------------------
    # returncode解析
    # ---------------------------------

    if return_code != 0:

        if return_code < 0:

            signal_number = (
                -return_code
            )

            raise RuntimeError(
                "FFmpegがシグナルによって"
                "終了しました。"
                f"signal={signal_number}"
            )

        raise RuntimeError(
            "FFmpeg字幕焼き込み失敗。"
            f"returncode={return_code}"
        )

    log(
        "FFmpeg正常終了"
    )

    separator()


# =====================================
# メイン
# =====================================

def run_ffmpeg_subtitle_test():

    separator()

    log(
        "FFmpeg字幕焼き込みテスト START"
    )

    separator()

    try:

        # =================================
        # STEP 1
        # =================================

        log(
            "STEP 1: 固定入力ファイル決定"
        )

        input_mp4 = (
            DOWNLOAD_DIR /
            TEST_MP4_FILENAME
        )

        input_srt = (
            DOWNLOAD_DIR /
            TEST_SRT_FILENAME
        )

        output_mp4 = (
            DOWNLOAD_DIR /
            TEST_OUTPUT_FILENAME
        )

        log(
            f"固定MP4: {input_mp4}"
        )

        log(
            f"固定SRT: {input_srt}"
        )

        # =================================
        # STEP 2
        # =================================

        log(
            "STEP 2: MP4確認"
        )

        input_mp4 = check_input_file(
            input_mp4,
            ".mp4"
        )

        # =================================
        # STEP 3
        # =================================

        log(
            "STEP 3: SRT確認"
        )

        input_srt = check_input_file(
            input_srt,
            ".srt"
        )

        # =================================
        # STEP 4
        # =================================

        log(
            "STEP 4: SRT UTF-8確認"
        )

        check_srt_utf8(
            input_srt
        )

        # =================================
        # STEP 5
        # =================================

        log(
            "STEP 5: subtitle_font.py設定取得"
        )

        settings = (
            get_subtitle_settings()
        )

        # =================================
        # STEP 6
        # =================================

        log(
            "STEP 6: 出力先決定"
        )

        output_mp4 = (
            output_mp4.resolve()
        )

        log(
            f"最終出力: {output_mp4}"
        )

        # =================================
        # STEP 7
        # =================================

        log(
            "STEP 7: FFmpeg確認"
        )

        ffmpeg_path = get_ffmpeg()

        check_ffmpeg_features(
            ffmpeg_path
        )

        log(
            f"使用FFmpeg: {ffmpeg_path}"
        )

        # =================================
        # STEP 8
        # =================================

        log(
            "STEP 8: 日本語フォント確認"
        )

        requested_font = settings.get(
            "font",
            "Noto Sans CJK JP"
        )

        font_path, font_family = (
            find_japanese_font(
                requested_font
            )
        )

        # =================================
        # STEP 9
        # =================================

        log(
            "STEP 9: 字幕フィルター生成"
        )

        video_filter = (
            create_subtitle_filter(
                input_srt,
                settings,
                font_path
            )
        )

        # =================================
        # STEP 10
        # =================================

        log(
            "STEP 10: 入力サイズ確認"
        )

        input_size = (
            input_mp4.stat().st_size
        )

        log(
            f"入力MP4サイズ: "
            f"{input_size} bytes"
        )

        # =================================
        # STEP 11
        # =================================

        log(
            "STEP 11: 一時出力パス生成"
        )

        DOWNLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        fd, tmp_name = tempfile.mkstemp(
            prefix=".test_embed.",
            suffix=".tmp.mp4",
            dir=str(DOWNLOAD_DIR)
        )

        os.close(fd)

        output_tmp = Path(
            tmp_name
        )

        log(
            f"一時出力パス: "
            f"{output_tmp}"
        )

        # =================================
        # STEP 12
        # =================================

        try:

            log(
                "STEP 12: FFmpeg実行"
            )

            run_ffmpeg(
                ffmpeg_path,
                input_mp4,
                output_tmp,
                video_filter
            )

            # =============================
            # 出力確認
            # =============================

            log(
                "STEP 13: 出力ファイル確認"
            )

            if not output_tmp.exists():

                raise RuntimeError(
                    "FFmpeg終了後も"
                    "一時出力ファイルがありません"
                )

            tmp_size = (
                output_tmp.stat().st_size
            )

            log(
                f"一時出力サイズ: "
                f"{tmp_size} bytes"
            )

            if tmp_size <= 0:

                raise RuntimeError(
                    "出力ファイルサイズが0です"
                )

            # =============================
            # 最終ファイル置換
            # =============================

            log(
                "STEP 14: 最終ファイル確定"
            )

            os.replace(
                output_tmp,
                output_mp4
            )

            log(
                f"最終出力: {output_mp4}"
            )

            if not output_mp4.exists():

                raise RuntimeError(
                    "最終出力ファイルが"
                    "存在しません"
                )

            final_size = (
                output_mp4.stat().st_size
            )

            log(
                f"最終出力サイズ: "
                f"{final_size} bytes"
            )

            # =============================
            # 完了
            # =============================

            separator()

            log(
                "FFmpeg字幕焼き込みテスト SUCCESS"
            )

            separator()

            return {

                "success": True,

                "message":
                    "FFmpeg字幕焼き込みテスト成功",

                "output":
                    str(output_mp4),

                "output_size":
                    final_size,

                "font":
                    font_family,

                "resolution":
                    f"{TEST_WIDTH}x{TEST_HEIGHT}"

            }

        finally:

            # =============================
            # 一時ファイル削除
            # =============================

            if output_tmp.exists():

                try:

                    output_tmp.unlink()

                    log(
                        "一時ファイル削除OK"
                    )

                except Exception as e:

                    log(
                        f"一時ファイル削除失敗: {e}"
                    )

    except Exception as e:

        separator()

        log(
            "FFmpeg字幕焼き込みテスト FAILED"
        )

        log(
            f"ERROR TYPE: "
            f"{type(e).__name__}"
        )

        log(
            f"ERROR: {e}"
        )

        separator()

        raise


# =====================================
# 直接実行
# =====================================

if __name__ == "__main__":

    try:

        result = (
            run_ffmpeg_subtitle_test()
        )

        print(
            result,
            flush=True
        )

    except Exception as e:

        print(
            {
                "success": False,
                "error_type":
                    type(e).__name__,
                "error":
                    str(e)
            },
            flush=True
        )

        raise
