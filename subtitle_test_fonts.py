# ==========================================================
# subtitle_test_fonts.py
#
# 字幕フォント FFmpeg テスト
#
# 使用ファイル:
#   /app/downloads/test.mp4
#   /app/downloads/test.srt
#
# 出力:
#   /app/downloads/test_embed.mp4
#
# 使用設定:
#   subtitle_font.py
#
# テスト内容:
#
#   1. test.mp4 の存在確認
#   2. test.srt の存在確認
#   3. subtitle_font.py からフォント設定取得
#   4. fontsdir の存在確認
#   5. fontsdir があれば FFmpeg に指定
#   6. fontsdir がなければ警告を表示して処理継続
#   7. FontName を FFmpeg に渡す
#   8. test.srt を映像へ焼き込む
#   9. FFmpeg終了確認
#  10. 出力ファイル確認
#
# ==========================================================

from pathlib import Path
import subprocess


# ==========================================================
# subtitle_font.py
# ==========================================================

try:

    from subtitle_font import (
        get_default_subtitle_font_settings
    )

except ImportError as error:

    raise ImportError(
        "subtitle_font.py を読み込めません: "
        f"{error}"
    )


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


DEFAULT_SRT = (
    DOWNLOAD_DIR /
    "test.srt"
)


DEFAULT_OUTPUT_MP4 = (
    DOWNLOAD_DIR /
    "test_embed.mp4"
)


# ==========================================================
# FFmpeg
# ==========================================================

FFMPEG_PATH = (
    "/usr/bin/ffmpeg"
)


# ==========================================================
# fontsdir
#
# ★ここは「候補ディレクトリ」です。
#
# 存在しない場合はエラーにしません。
#
# 実際に存在する場合だけFFmpegへ渡します。
# ==========================================================

DEFAULT_FONT_DIR = (
    DOWNLOAD_DIR /
    "fonts"
)


# ==========================================================
# ログ
# ==========================================================

def log(
    message
):

    print(
        f"[SUBTITLE FONT TEST] {message}",
        flush=True
    )


# ==========================================================
# 区切り
# ==========================================================

def separator():

    print(
        "==========================================",
        flush=True
    )


# ==========================================================
# ファイル確認
# ==========================================================

def check_file(
    file_path,
    description
):

    log(
        f"{description}確認 START"
    )

    if not file_path.exists():

        raise FileNotFoundError(
            f"{description}が存在しません: "
            f"{file_path}"
        )

    if not file_path.is_file():

        raise FileNotFoundError(
            f"{description}ではありません: "
            f"{file_path}"
        )

    size = file_path.stat().st_size

    log(
        f"{description}確認 OK"
    )

    log(
        f"{description}: "
        f"{file_path}"
    )

    log(
        f"{description}サイズ: "
        f"{size} bytes"
    )

    return size


# ==========================================================
# フォント設定取得
# ==========================================================

def get_font_settings():

    separator()

    log(
        "subtitle_font.py 読み込み"
    )

    separator()

    settings = (
        get_default_subtitle_font_settings()
    )

    if not isinstance(
        settings,
        dict
    ):

        raise RuntimeError(
            "subtitle_font.py から取得した設定がdictではありません"
        )

    font = settings.get(
        "font"
    )

    if not font:

        raise RuntimeError(
            "字幕フォント設定にfontがありません"
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

    log(
        f"preset_name: "
        f"{settings.get('preset_name')}"
    )

    log(
        f"font: "
        f"{font}"
    )

    log(
        f"text_color: "
        f"{text_color}"
    )

    log(
        f"outline_color: "
        f"{outline_color}"
    )

    log(
        f"outline_width: "
        f"{outline_width}"
    )

    return settings


# ==========================================================
# ASSカラー変換
#
# subtitle_font.py の
#
#   &HAABBGGRR
#
# 形式を使用する。
# ==========================================================

def get_ass_color(
    settings,
    key,
    default
):

    # ------------------------------------------------------
    # subtitle_font.py にカラー取得関数がある場合
    # ------------------------------------------------------

    try:

        from subtitle_font import (
            get_subtitle_color
        )

        color_name = settings.get(
            key,
            default
        )

        color_info = get_subtitle_color(
            color_name
        )

        ass_color = color_info.get(
            "ass"
        )

        if ass_color:

            return ass_color

    except Exception as error:

        log(
            f"カラー取得関数を使用できません: "
            f"{type(error).__name__}: {error}"
        )

    # ------------------------------------------------------
    # フォールバック
    # ------------------------------------------------------

    fallback_colors = {

        "白":
            "&H00FFFFFF",

        "黒":
            "&H00000000",

        "青":
            "&H00FF0000",

        "赤":
            "&H000000FF",

        "緑":
            "&H0000FF00",

        "黄色":
            "&H0000FFFF",

        "黄":
            "&H0000FFFF",

    }

    return fallback_colors.get(
        settings.get(
            key,
            default
        ),
        fallback_colors.get(
            default,
            "&H00FFFFFF"
        )
    )


# ==========================================================
# fontsdir確認
#
# ★重要
#
# 存在しなくてもエラーにしない。
# ==========================================================

def detect_font_dir(
    font_dir=None
):

    if font_dir is None:

        font_dir = DEFAULT_FONT_DIR

    else:

        font_dir = Path(
            font_dir
        )

    separator()

    log(
        "fontsdir確認 START"
    )

    log(
        f"fontsdir候補: "
        f"{font_dir}"
    )

    # ------------------------------------------------------
    # 存在確認
    # ------------------------------------------------------

    if not font_dir.exists():

        log(
            "fontsdir STATUS: NOT FOUND"
        )

        log(
            "fontsdirが存在しません。"
        )

        log(
            "FFmpegへfontsdirを指定せず、"
            "システムフォント検索を使用します。"
        )

        return None

    # ------------------------------------------------------
    # ディレクトリ確認
    # ------------------------------------------------------

    if not font_dir.is_dir():

        log(
            "fontsdir STATUS: NOT DIRECTORY"
        )

        log(
            "指定されたfontsdirはディレクトリではありません。"
        )

        log(
            "FFmpegへfontsdirを指定せず、"
            "システムフォント検索を使用します。"
        )

        return None

    # ------------------------------------------------------
    # OK
    # ------------------------------------------------------

    log(
        "fontsdir STATUS: OK"
    )

    log(
        f"使用fontsdir: "
        f"{font_dir}"
    )

    return font_dir


# ==========================================================
# FFmpeg subtitles filter生成
# ==========================================================

def build_subtitles_filter(
    srt_file,
    settings,
    font_dir=None
):

    font = str(
        settings.get(
            "font",
            "Noto Sans CJK JP"
        )
    ).strip()

    text_color = get_ass_color(
        settings,
        "text_color",
        "白"
    )

    outline_color = get_ass_color(
        settings,
        "outline_color",
        "青"
    )

    try:

        outline_width = int(
            settings.get(
                "outline_width",
                5
            )
        )

    except (
        ValueError,
        TypeError
    ):

        outline_width = 5

    outline_width = max(
        0,
        min(
            outline_width,
            10
        )
    )

    # ======================================================
    # subtitlesフィルター
    # ======================================================

    subtitle_filter = (
        "subtitles="
        + str(srt_file)
    )

    # ======================================================
    # fontsdir
    #
    # 存在するときだけ追加。
    # ======================================================

    if font_dir is not None:

        subtitle_filter += (
            ":fontsdir="
            + str(font_dir)
        )

    # ======================================================
    # force_style
    # ======================================================

    force_style = (
        "FontName="
        + font
        + ","
        + "PrimaryColour="
        + text_color
        + ","
        + "OutlineColour="
        + outline_color
        + ","
        + "Outline="
        + str(outline_width)
    )

    subtitle_filter += (
        ":force_style="
        + "'"
        + force_style
        + "'"
    )

    return subtitle_filter


# ==========================================================
# FFmpegコマンド作成
# ==========================================================

def build_ffmpeg_command(
    input_file,
    srt_file,
    output_file,
    settings,
    font_dir
):

    subtitle_filter = (
        build_subtitles_filter(
            srt_file,
            settings,
            font_dir
        )
    )

    command = [

        FFMPEG_PATH,

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
        subtitle_filter,

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

    return command


# ==========================================================
# FFmpeg実行
# ==========================================================

def run_ffmpeg(
    command
):

    separator()

    log(
        "FFmpeg command"
    )

    separator()

    log(
        " ".join(
            command
        )
    )

    separator()

    log(
        "FFmpeg起動【1回だけ】"
    )

    log(
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

        log(
            "FFmpeg TIMEOUT"
        )

        raise RuntimeError(
            "FFmpegが120秒以内に終了しませんでした"
        )

    except Exception as error:

        log(
            "subprocess.run ERROR"
        )

        log(
            f"{type(error).__name__}: "
            f"{error}"
        )

        raise

    # ======================================================
    # FFmpeg終了
    # ======================================================

    separator()

    log(
        "FFmpeg終了"
    )

    log(
        f"returncode: "
        f"{result.returncode}"
    )

    separator()

    # ======================================================
    # stderr
    # ======================================================

    if result.stderr:

        log(
            "FFmpeg stderr:"
        )

        print(
            result.stderr,
            flush=True
        )

    # ======================================================
    # stdout
    # ======================================================

    if result.stdout:

        log(
            "FFmpeg stdout:"
        )

        print(
            result.stdout,
            flush=True
        )

    # ======================================================
    # エラー
    # ======================================================

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg処理失敗 "
            f"(returncode={result.returncode})"
        )

    return result


# ==========================================================
# 出力確認
# ==========================================================

def check_output(
    output_file
):

    separator()

    log(
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

    output_size = output_file.stat().st_size

    if output_size <= 0:

        raise RuntimeError(
            "FFmpeg出力ファイルのサイズが0 bytesです"
        )

    log(
        "出力ファイル確認 OK"
    )

    log(
        f"出力ファイル: "
        f"{output_file}"
    )

    log(
        f"出力サイズ: "
        f"{output_size} bytes"
    )

    return output_size


# ==========================================================
# メイン
# ==========================================================

def run_font_test(
    input_path=None,
    srt_path=None,
    output_path=None,
    font_dir=None
):

    separator()

    log(
        "SUBTITLE FONT TEST START"
    )

    separator()

    # ======================================================
    # パス
    # ======================================================

    input_file = (

        Path(input_path)

        if input_path is not None

        else DEFAULT_INPUT_MP4

    )

    srt_file = (

        Path(srt_path)

        if srt_path is not None

        else DEFAULT_SRT

    )

    output_file = (

        Path(output_path)

        if output_path is not None

        else DEFAULT_OUTPUT_MP4

    )

    # ======================================================
    # パス表示
    # ======================================================

    log(
        f"input: "
        f"{input_file}"
    )

    log(
        f"srt: "
        f"{srt_file}"
    )

    log(
        f"output: "
        f"{output_file}"
    )

    # ======================================================
    # 入力確認
    # ======================================================

    check_file(
        input_file,
        "入力MP4"
    )

    check_file(
        srt_file,
        "字幕SRT"
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

        log(
            "既存出力削除"
        )

        output_file.unlink()

    # ======================================================
    # subtitle_font.py
    # ======================================================

    settings = get_font_settings()

    # ======================================================
    # fontsdir
    # ======================================================

    detected_font_dir = detect_font_dir(
        font_dir
    )

    # ======================================================
    # FFmpegコマンド
    # ======================================================

    command = build_ffmpeg_command(

        input_file,

        srt_file,

        output_file,

        settings,

        detected_font_dir

    )

    # ======================================================
    # 設定表示
    # ======================================================

    separator()

    log(
        "字幕フォント設定"
    )

    separator()

    log(
        f"font: "
        f"{settings.get('font')}"
    )

    log(
        f"text_color: "
        f"{settings.get('text_color')}"
    )

    log(
        f"outline_color: "
        f"{settings.get('outline_color')}"
    )

    log(
        f"outline_width: "
        f"{settings.get('outline_width')}"
    )

    if detected_font_dir:

        log(
            f"fontsdir: "
            f"{detected_font_dir}"
        )

    else:

        log(
            "fontsdir: 使用しません"
        )

    # ======================================================
    # FFmpeg
    # ======================================================

    run_ffmpeg(
        command
    )

    # ======================================================
    # 出力確認
    # ======================================================

    output_size = check_output(
        output_file
    )

    # ======================================================
    # 完了
    # ======================================================

    separator()

    log(
        "SUBTITLE FONT TEST COMPLETE"
    )

    separator()

    return output_file


# ==========================================================
# 直接実行
# ==========================================================

if __name__ == "__main__":

    try:

        output = run_font_test()

        separator()

        print(
            "【字幕フォントFFmpegテスト完了】",
            flush=True
        )

        print(
            flush=True
        )

        print(
            f"入力ファイル:",
            flush=True
        )

        print(
            DEFAULT_INPUT_MP4,
            flush=True
        )

        print(
            flush=True
        )

        print(
            f"字幕ファイル:",
            flush=True
        )

        print(
            DEFAULT_SRT,
            flush=True
        )

        print(
            flush=True
        )

        print(
            f"出力ファイル:",
            flush=True
        )

        print(
            output,
            flush=True
        )

        print(
            flush=True
        )

        print(
            f"出力サイズ:",
            flush=True
        )

        print(
            output.stat().st_size,
            "bytes",
            flush=True
        )

        separator()

    except Exception as error:

        separator()

        print(
            "【字幕フォントFFmpegテスト失敗】",
            flush=True
        )

        print(
            flush=True
        )

        print(
            "ERROR TYPE:",
            flush=True
        )

        print(
            type(error).__name__,
            flush=True
        )

        print(
            flush=True
        )

        print(
            "ERROR:",
            flush=True
        )

        print(
            str(error),
            flush=True
        )

        separator()

        raise
