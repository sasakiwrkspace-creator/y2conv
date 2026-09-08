# =====================================
# subtitle_test_ffmpeg.py
#
# FFmpeg字幕焼き込み単体テスト
#
# 固定入力:
#   downloads/test.mp4
#   downloads/test.srt
#
# 固定出力:
#   downloads/test_embed.mp4
#
# 役割:
# ・MP4存在確認
# ・SRT存在確認
# ・SRT UTF-8確認
# ・字幕フォント設定取得
# ・日本語フォント確認
# ・FFmpeg確認
# ・subtitlesフィルター生成
# ・FFmpeg実行
# ・test_embed.mp4生成
# ・生成結果確認
# =====================================


from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import time


# =====================================
# subtitle_font
# =====================================

import subtitle_font


# =====================================
# 設定
# =====================================

BASE_DIR = Path(
    os.environ.get(
        "BASE_DIR",
        "/app"
    )
).resolve()


DOWNLOAD_DIR = Path(
    os.environ.get(
        "DOWNLOAD_DIR",
        str(BASE_DIR / "downloads")
    )
).resolve()


TEST_MP4_FILENAME = "test.mp4"

TEST_SRT_FILENAME = "test.srt"

TEST_OUTPUT_FILENAME = "test_embed.mp4"


TEST_MP4 = (
    DOWNLOAD_DIR /
    TEST_MP4_FILENAME
)

TEST_SRT = (
    DOWNLOAD_DIR /
    TEST_SRT_FILENAME
)

TEST_OUTPUT = (
    DOWNLOAD_DIR /
    TEST_OUTPUT_FILENAME
)


# =====================================
# ログ
# =====================================

def log(message=""):
    print(
        f"[SUBTITLE TEST] {message}",
        flush=True
    )


# =====================================
# モジュールロード確認
# =====================================

log("==========================================")
log("subtitle_test_ffmpeg.py MODULE LOAD COMPLETE")
log(f"Current working directory: {Path.cwd()}")
log(f"BASE_DIR: {BASE_DIR}")
log(f"DOWNLOAD_DIR: {DOWNLOAD_DIR}")
log(f"TEST_MP4: {TEST_MP4}")
log(f"TEST_SRT: {TEST_SRT}")
log(f"TEST_OUTPUT: {TEST_OUTPUT}")
log(
    "SUBTITLE_FONT environment: "
    + str(os.environ.get("SUBTITLE_FONT"))
)
log("==========================================")


# =====================================
# 共通：入力ファイル確認
# =====================================

def check_input_file(
    file_path,
    expected_extension
):
    log("==========================================")
    log("入力ファイル確認開始")
    log("==========================================")

    file_path = Path(file_path).resolve()

    log(f"file_path: {file_path}")
    log(f"expected extension: {expected_extension}")
    log(f"resolved path: {file_path}")

    if not file_path.exists():

        raise FileNotFoundError(
            f"入力ファイルが存在しません: {file_path}"
        )

    if not file_path.is_file():

        raise RuntimeError(
            f"入力パスがファイルではありません: {file_path}"
        )

    actual_extension = (
        file_path.suffix.lower()
    )

    log(
        f"actual extension: "
        f"{actual_extension}"
    )

    if actual_extension != expected_extension:

        raise ValueError(
            "拡張子が正しくありません: "
            f"{file_path}"
        )

    file_size = file_path.stat().st_size

    log(
        f"file size: "
        f"{file_size} bytes"
    )

    if file_size <= 0:

        raise RuntimeError(
            f"ファイルサイズが0です: {file_path}"
        )

    log("入力ファイル確認OK")

    return file_path


# =====================================
# SRT UTF-8確認
# =====================================

def check_srt_utf8(
    srt_path
):
    log("==========================================")
    log("SRT UTF-8確認開始")
    log("==========================================")

    srt_path = Path(
        srt_path
    ).resolve()

    try:

        text = srt_path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError as error:

        raise RuntimeError(
            "SRTがUTF-8として読み込めません: "
            f"{error}"
        )

    except Exception as error:

        raise RuntimeError(
            "SRT読み込み失敗: "
            f"{error}"
        )

    log(
        f"SRT先頭文字数: "
        f"{len(text[:1000])}"
    )

    if not text.strip():

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    log("SRT UTF-8確認OK")

    return text


# =====================================
# FFmpeg確認
# =====================================

def check_ffmpeg():

    log("==========================================")
    log("FFmpeg確認開始")
    log("==========================================")

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    log(
        f"shutil.which(ffmpeg): "
        f"{ffmpeg_path}"
    )

    if not ffmpeg_path:

        raise RuntimeError(
            "ffmpeg が見つかりません。"
        )

    try:

        result = subprocess.run(
            [
                ffmpeg_path,
                "-version"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15
        )

    except Exception as error:

        raise RuntimeError(
            "FFmpeg確認に失敗しました: "
            f"{error}"
        )

    log(
        "FFmpeg version returncode: "
        f"{result.returncode}"
    )

    version_text = (
        result.stdout.strip()
    )

    if version_text:

        first_line = (
            version_text.splitlines()[0]
        )

        log(
            f"FFmpeg version: "
            f"{first_line}"
        )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpegが正常に実行できません。"
        )

    log("FFmpeg確認完了")

    return ffmpeg_path


# =====================================
# FFmpeg機能確認
# =====================================

def check_ffmpeg_features(
    ffmpeg_path
):

    log("==========================================")
    log("FFmpeg機能確認")
    log("==========================================")

    # ---------------------------------
    # libx264
    # ---------------------------------

    log("libx264確認開始")

    encoders = subprocess.run(
        [
            ffmpeg_path,
            "-hide_banner",
            "-encoders"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    encoder_text = (
        encoders.stdout +
        encoders.stderr
    )

    if "libx264" not in encoder_text:

        raise RuntimeError(
            "FFmpegにlibx264がありません。"
        )

    log("libx264: OK")

    # ---------------------------------
    # subtitles filter
    # ---------------------------------

    log("subtitlesフィルター確認開始")

    filters = subprocess.run(
        [
            ffmpeg_path,
            "-hide_banner",
            "-filters"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30
    )

    filter_text = (
        filters.stdout +
        filters.stderr
    )

    if "subtitles" not in filter_text:

        raise RuntimeError(
            "FFmpegにsubtitlesフィルターがありません。"
        )

    log("subtitles filter: OK")

    # ---------------------------------
    # libass
    # ---------------------------------

    log("libass確認開始")

    if "libass" in filter_text:

        log("libass: OK")

    else:

        log(
            "libass: filter一覧では明示確認できません"
        )

    log("FFmpeg機能確認完了")


# =====================================
# 日本語フォント確認
# =====================================

def find_japanese_font(
    requested_font
):

    log("==========================================")
    log("日本語フォント検索開始")
    log("==========================================")

    log(
        f"requested_font: "
        f"{requested_font}"
    )

    subtitle_font_env = (
        os.environ.get(
            "SUBTITLE_FONT"
        )
    )

    log(
        "SUBTITLE_FONT: "
        f"{subtitle_font_env}"
    )

    # ---------------------------------
    # fc-match
    # ---------------------------------

    fc_match = shutil.which(
        "fc-match"
    )

    if not fc_match:

        raise RuntimeError(
            "fc-match が見つかりません。"
        )

    try:

        result = subprocess.run(
            [
                fc_match,
                "-f",
                "%{file}\n",
                requested_font
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15
        )

    except Exception as error:

        raise RuntimeError(
            "fc-match実行失敗: "
            f"{error}"
        )

    font_path_text = (
        result.stdout.strip()
    )

    log(
        f"fc-match: "
        f"{font_path_text}"
    )

    if not font_path_text:

        raise RuntimeError(
            "指定フォントが見つかりません: "
            f"{requested_font}"
        )

    font_path = Path(
        font_path_text.splitlines()[0]
    ).resolve()

    if not font_path.exists():

        raise RuntimeError(
            "fc-matchが返したフォントファイルが"
            "存在しません: "
            f"{font_path}"
        )

    # ---------------------------------
    # family
    # ---------------------------------

    try:

        family_result = subprocess.run(
            [
                fc_match,
                "-f",
                "%{family}\n",
                requested_font
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15
        )

        family = (
            family_result.stdout
            .strip()
            .splitlines()[0]
        )

    except Exception:

        family = requested_font

    log(
        f"font path: "
        f"{font_path}"
    )

    log(
        f"font family: "
        f"{family}"
    )

    return {
        "path": font_path,
        "family": family
    }


# =====================================
# ASSカラー
# =====================================

def get_ass_color(
    color_name
):

    # ASSカラー:
    #
    # &HAABBGGRR
    #
    # 白:
    # &H00FFFFFF
    #
    # 青:
    # &H00FF0000
    #

    colors = {

        "白":
            "&H00FFFFFF",

        "黒":
            "&H00000000",

        "赤":
            "&H000000FF",

        "緑":
            "&H0000FF00",

        "青":
            "&H00FF0000",

        "黄":
            "&H0000FFFF",

        "水色":
            "&H00FFFF00",

        "紫":
            "&H00FF00FF",

    }

    if color_name in colors:

        return colors[color_name]

    # ---------------------------------
    # 直接ASSカラーが指定されている場合
    # ---------------------------------

    if isinstance(
        color_name,
        str
    ):

        value = color_name.strip()

        if value.upper().startswith(
            "&H"
        ):

            return value

    # ---------------------------------
    # 不明なら白
    # ---------------------------------

    log(
        "不明な色です。白を使用します: "
        f"{color_name}"
    )

    return "&H00FFFFFF"


# =====================================
# 字幕設定取得
# =====================================

def get_subtitle_settings():

    log("==========================================")
    log("字幕設定取得開始")
    log("==========================================")

    try:

        default_settings = (
            subtitle_font
            .get_default_subtitle_font_settings()
        )

    except Exception as error:

        log(
            "get_default_subtitle_font_settings "
            "取得失敗"
        )

        log(
            f"error: {error}"
        )

        default_settings = {

            "preset_name": "標準",

            "font":
                "Noto Sans CJK JP",

            "text_color":
                "白",

            "outline_color":
                "青",

            "outline_width":
                5

        }

    log(
        f"default: "
        f"{default_settings}"
    )

    try:

        settings = (
            subtitle_font
            .select_subtitle_font(
                default_settings
            )
        )

    except TypeError:

        try:

            settings = (
                subtitle_font
                .select_subtitle_font()
            )

        except Exception as error:

            log(
                "select_subtitle_font() 失敗: "
                f"{error}"
            )

            settings = default_settings

    except Exception as error:

        log(
            "select_subtitle_font() 失敗: "
            f"{error}"
        )

        settings = default_settings

    if not isinstance(
        settings,
        dict
    ):

        settings = default_settings

    # ---------------------------------
    # 値を安全に取得
    # ---------------------------------

    preset_name = (
        settings.get(
            "preset_name",
            "標準"
        )
    )

    font = (
        settings.get(
            "font",
            "Noto Sans CJK JP"
        )
    )

    text_color = (
        settings.get(
            "text_color",
            "白"
        )
    )

    outline_color = (
        settings.get(
            "outline_color",
            "青"
        )
    )

    outline_width = (
        settings.get(
            "outline_width",
            5
        )
    )

    try:

        outline_width = int(
            outline_width
        )

    except Exception:

        outline_width = 5

    if outline_width < 0:

        outline_width = 0

    normalized = {

        "preset_name":
            str(preset_name),

        "font":
            str(font),

        "text_color":
            str(text_color),

        "outline_color":
            str(outline_color),

        "outline_width":
            outline_width

    }

    log(
        f"最終字幕設定: "
        f"{normalized}"
    )

    return normalized


# =====================================
# 字幕フィルター生成
# =====================================

def build_subtitle_filter(
    srt_path,
    subtitle_settings,
    font_path
):

    log("==========================================")
    log("字幕フィルター作成開始")
    log("==========================================")

    srt_path = Path(
        srt_path
    ).resolve()

    font_path = Path(
        font_path
    ).resolve()

    settings = subtitle_settings

    font_name = (
        settings["font"]
    )

    text_color = (
        settings["text_color"]
    )

    outline_color = (
        settings["outline_color"]
    )

    outline_width = (
        settings["outline_width"]
    )

    text_ass_color = get_ass_color(
        text_color
    )

    outline_ass_color = get_ass_color(
        outline_color
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

    font_dir = font_path.parent

    log(
        f"最終FontName: "
        f"{font_name}"
    )

    log(
        f"字幕フォントディレクトリ: "
        f"{font_dir}"
    )

    log("字幕スタイル:")
    log(
        f"preset_name: "
        f"{settings['preset_name']}"
    )
    log(
        f"font: "
        f"{font_name}"
    )
    log(
        f"text_color: "
        f"{text_color}"
    )
    log(
        f"text_color ASS: "
        f"{text_ass_color}"
    )
    log(
        f"outline_color: "
        f"{outline_color}"
    )
    log(
        f"outline_color ASS: "
        f"{outline_ass_color}"
    )
    log(
        f"outline_width: "
        f"{outline_width}"
    )

    # =================================
    # FFmpeg subtitles filter
    #
    # SRTパスに特殊文字があっても
    # なるべく安全に処理する。
    # =================================

    srt_filter_path = (
        str(srt_path)
        .replace(
            "\\",
            "/"
        )
        .replace(
            ":",
            "\\:"
        )
        .replace(
            "'",
            "\\'"
        )
    )

    font_dir_filter_path = (
        str(font_dir)
        .replace(
            "\\",
            "/"
        )
        .replace(
            ":",
            "\\:"
        )
        .replace(
            "'",
            "\\'"
        )
    )

    # =================================
    # 注意
    #
    # subprocessにはshell=Falseで渡すため、
    # この文字列をシェル用に二重引用しない。
    # =================================

    video_filter = (
        "subtitles="
        "'"
        + srt_filter_path
        + "'"
        ":fontsdir="
        "'"
        + font_dir_filter_path
        + "'"
        ":force_style="
        "'"
        + "FontName="
        + font_name
        + ","
        + "PrimaryColour="
        + text_ass_color
        + ","
        + "OutlineColour="
        + outline_ass_color
        + ","
        + "Outline="
        + str(outline_width)
        + "'"
    )

    log(
        f"完成video_filter: "
        f"{video_filter}"
    )

    log("字幕フィルター作成完了")

    return video_filter


# =====================================
# FFmpeg実行
# =====================================

def run_ffmpeg(
    ffmpeg_path,
    input_mp4,
    output_mp4,
    video_filter
):

    log("==========================================")
    log("FFmpegコマンド生成")
    log("==========================================")

    input_mp4 = Path(
        input_mp4
    ).resolve()

    output_mp4 = Path(
        output_mp4
    ).resolve()

    output_mp4.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # =================================
    # 一時ファイル
    #
    # 最終ファイルへ直接書き込まず、
    # 成功後にrenameする。
    # =================================

    fd, temp_name = tempfile.mkstemp(
        prefix=".test_embed.",
        suffix=".tmp.mp4",
        dir=str(output_mp4.parent)
    )

    os.close(fd)

    temp_output = Path(
        temp_name
    ).resolve()

    log(
        f"一時出力パス: "
        f"{temp_output}"
    )

    # =================================
    # FFmpeg設定
    # =================================

    threads = "1"

    preset = "ultrafast"

    crf = "23"

    log("FFmpeg設定:")
    log(
        f"threads: {threads}"
    )
    log(
        f"preset: {preset}"
    )
    log(
        f"crf: {crf}"
    )
    log(
        "video filter:"
    )
    log(
        video_filter
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

        "-c:v",
        "libx264",

        "-threads",
        threads,

        "-preset",
        preset,

        "-crf",
        crf,

        "-c:a",
        "copy",

        "-movflags",
        "+faststart",

        str(temp_output)

    ]

    log("FFmpeg command:")

    log(
        " ".join(
            str(x)
            for x in command
        )
    )

    log("==========================================")
    log("FFmpeg開始")
    log("==========================================")

    process = None

    start_time = time.time()

    try:

        process = subprocess.Popen(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            bufsize=1

        )

        log(
            f"FFmpeg PID: "
            f"{process.pid}"
        )

        log("==========================================")
        log("FFmpegログ取得")
        log("==========================================")

        # ---------------------------------
        # stderrをリアルタイム表示
        # ---------------------------------

        if process.stderr:

            for line in process.stderr:

                line = line.rstrip()

                if line:

                    print(
                        f"[FFMPEG] {line}",
                        flush=True
                    )

        return_code = (
            process.wait()
        )

        elapsed = (
            time.time()
            - start_time
        )

        log(
            f"FFmpeg returncode: "
            f"{return_code}"
        )

        log(
            f"FFmpeg elapsed: "
            f"{elapsed:.2f} sec"
        )

        # =================================
        # 失敗
        # =================================

        if return_code != 0:

            if temp_output.exists():

                try:
                    temp_output.unlink()
                except Exception:
                    pass

            raise RuntimeError(
                "FFmpeg字幕焼き込みに失敗しました。"
                f" returncode={return_code}"
            )

        # =================================
        # 出力確認
        # =================================

        log("==========================================")
        log("FFmpeg出力確認")
        log("==========================================")

        if not temp_output.exists():

            raise RuntimeError(
                "FFmpegは成功しましたが、"
                "一時出力ファイルがありません。"
            )

        temp_size = (
            temp_output.stat().st_size
        )

        log(
            f"一時出力サイズ: "
            f"{temp_size} bytes"
        )

        if temp_size <= 0:

            raise RuntimeError(
                "FFmpeg出力ファイルのサイズが0です。"
            )

        # =================================
        # 既存ファイル削除
        # =================================

        if output_mp4.exists():

            log(
                "既存test_embed.mp4を削除します。"
            )

            output_mp4.unlink()

        # =================================
        # rename
        # =================================

        temp_output.replace(
            output_mp4
        )

        log(
            f"最終出力生成完了: "
            f"{output_mp4}"
        )

        # =================================
        # 最終確認
        # =================================

        if not output_mp4.exists():

            raise RuntimeError(
                "最終出力ファイルが存在しません。"
            )

        final_size = (
            output_mp4.stat().st_size
        )

        log(
            f"最終出力サイズ: "
            f"{final_size} bytes"
        )

        if final_size <= 0:

            raise RuntimeError(
                "最終出力ファイルのサイズが0です。"
            )

        log("FFmpeg字幕焼き込み成功")

        return output_mp4

    except Exception:

        # ---------------------------------
        # 一時ファイル削除
        # ---------------------------------

        if temp_output.exists():

            try:

                temp_output.unlink()

            except Exception:

                pass

        raise

    finally:

        # ---------------------------------
        # 念のためプロセス終了確認
        # ---------------------------------

        if process is not None:

            try:

                if process.poll() is None:

                    process.kill()

                    process.wait()

            except Exception:

                pass


# =====================================
# メイン
# =====================================

def run_ffmpeg_subtitle_test():

    log("==========================================")
    log("FFmpeg字幕焼き込みテスト START")
    log("==========================================")

    try:

        # =================================
        # STEP 1
        # 固定入力ファイル決定
        # =================================

        log("==========================================")
        log("STEP 1: 固定入力ファイル決定")
        log("==========================================")

        input_mp4 = TEST_MP4

        input_srt = TEST_SRT

        output_mp4 = TEST_OUTPUT

        log(
            f"固定MP4: "
            f"{input_mp4}"
        )

        log(
            f"固定SRT: "
            f"{input_srt}"
        )

        # =================================
        # STEP 2
        # MP4確認
        # =================================

        log("==========================================")
        log("STEP 2: MP4確認")
        log("==========================================")

        input_mp4 = check_input_file(
            input_mp4,
            ".mp4"
        )

        # =================================
        # STEP 3
        # SRT確認
        # =================================

        log("==========================================")
        log("STEP 3: SRT確認")
        log("==========================================")

        input_srt = check_input_file(
            input_srt,
            ".srt"
        )

        # =================================
        # STEP 4
        # SRT UTF-8
        # =================================

        log("==========================================")
        log("STEP 4: SRT UTF-8確認")
        log("==========================================")

        check_srt_utf8(
            input_srt
        )

        # =================================
        # STEP 5
        # subtitle_font設定取得
        # =================================

        log("==========================================")
        log("STEP 5: subtitle_font.py設定取得")
        log("==========================================")

        settings = (
            get_subtitle_settings()
        )

        # =================================
        # STEP 6
        # 出力先決定
        # =================================

        log("==========================================")
        log("STEP 6: 出力先決定")
        log("==========================================")

        log(
            f"最終出力: "
            f"{output_mp4}"
        )

        # =================================
        # STEP 7
        # FFmpeg確認
        # =================================

        log("==========================================")
        log("STEP 7: FFmpeg確認")
        log("==========================================")

        ffmpeg_path = check_ffmpeg()

        check_ffmpeg_features(
            ffmpeg_path
        )

        log(
            f"使用FFmpeg: "
            f"{ffmpeg_path}"
        )

        # =================================
        # STEP 8
        # 日本語フォント確認
        # =================================

        log("==========================================")
        log("STEP 8: 日本語フォント確認")
        log("==========================================")

        font_info = find_japanese_font(
            settings["font"]
        )

        font_path = font_info["path"]

        # =================================
        # STEP 9
        # 字幕フィルター生成
        # =================================

        log("==========================================")
        log("STEP 9: 字幕フィルター生成")
        log("==========================================")

        video_filter = build_subtitle_filter(

            input_srt,

            settings,

            font_path

        )

        # =================================
        # STEP 10
        # 入力サイズ確認
        # =================================

        log("==========================================")
        log("STEP 10: 入力サイズ確認")
        log("==========================================")

        input_size = (
            input_mp4.stat().st_size
        )

        log(
            f"入力MP4サイズ: "
            f"{input_size} bytes"
        )

        # =================================
        # STEP 11〜
        # FFmpeg実行
        # =================================

        result_path = run_ffmpeg(

            ffmpeg_path,

            input_mp4,

            output_mp4,

            video_filter

        )

        # =================================
        # 成功
        # =================================

        log("==========================================")
        log("FFmpeg字幕焼き込みテスト SUCCESS")
        log("==========================================")

        result_size = (
            result_path.stat().st_size
        )

        return {

            "success":
                True,

            "message":
                "字幕FFmpegテスト成功",

            "input_mp4":
                str(input_mp4),

            "input_srt":
                str(input_srt),

            "output_mp4":
                str(result_path),

            "output_size":
                result_size,

            "font":
                settings["font"],

            "text_color":
                settings["text_color"],

            "outline_color":
                settings["outline_color"],

            "outline_width":
                settings["outline_width"]

        }

    except Exception as error:

        # =================================
        # エラー
        # =================================

        log("==========================================")
        log("FFmpeg字幕焼き込みテスト FAILED")
        log("==========================================")

        log(
            f"ERROR TYPE: "
            f"{type(error).__name__}"
        )

        log(
            f"ERROR: "
            f"{error}"
        )

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
            "=========================================="
        )

        print(
            "SUCCESS"
        )

        print(
            result
        )

        print(
            "=========================================="
        )

    except Exception as error:

        print(
            "=========================================="
        )

        print(
            "FAILED"
        )

        print(
            f"ERROR TYPE: "
            f"{type(error).__name__}"
        )

        print(
            f"ERROR: "
            f"{error}"
        )

        print(
            "=========================================="
        )

        raise
