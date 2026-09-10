# ==========================================================
# subtitle_test_fonts.py
#
# 字幕フォントFFmpegテスト
#
# test.mp4
#     +
# test.srt
#     ↓
# subtitle_font.py
#     ↓
# フォント・文字色・縁色・縁太さ
#     ↓
# FFmpeg subtitles filter
#     ↓
# test_embed_fonts.mp4
#
# ==========================================================

from pathlib import Path
import shutil
import subprocess


# ==========================================================
# パス
# ==========================================================

DOWNLOAD_DIR = Path("/app/downloads")

DEFAULT_INPUT_MP4 = DOWNLOAD_DIR / "test.mp4"
DEFAULT_INPUT_SRT = DOWNLOAD_DIR / "test.srt"
DEFAULT_OUTPUT_MP4 = DOWNLOAD_DIR / "test_embed_fonts.mp4"
DEFAULT_FONTS_DIR = DOWNLOAD_DIR / "fonts"


# ==========================================================
# デフォルト値
# ==========================================================

DEFAULT_FONT = "Noto Sans CJK JP"
DEFAULT_TEXT_COLOR = "白"
DEFAULT_OUTLINE_COLOR = "青"
DEFAULT_OUTLINE_WIDTH = 5


# ==========================================================
# FFmpeg
# ==========================================================

DEFAULT_FFMPEG = "/usr/bin/ffmpeg"


# ==========================================================
# ログ
# ==========================================================

def _log(message):
    print(
        "[SUBTITLE_TEST_FONTS]",
        message,
        flush=True
    )


# ==========================================================
# パスを絶対パスへ
# ==========================================================

def _absolute_path(path):
    return Path(path).expanduser().resolve()


# ==========================================================
# FFmpeg filter用パスエスケープ
#
# 重要:
#
# subprocess.run() は shell=False なので、
# shell用の quoting はしない。
#
# ここで必要なのは FFmpeg filtergraph 用の
# エスケープだけ。
#
# Linux:
#   /app/downloads/test.srt
#
# Windows:
#   C:\xxx\test.srt
#
# FFmpeg filtergraphでは以下をエスケープする。
#
#   \
#   :
#   '
#   [
#   ]
#   ,
#   ;
#
# ==========================================================

def _escape_filter_path(path):

    value = str(
        _absolute_path(path)
    )

    # バックスラッシュを最初に処理
    value = value.replace(
        "\\",
        "\\\\"
    )

    # FFmpeg filtergraph の特殊文字
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
# force_style用エスケープ
#
# フォント名などにカンマや特殊文字が入っても
# filtergraphを壊しにくくする。
# ==========================================================

def _escape_style_value(value):

    if value is None:
        return ""

    value = str(value)

    value = value.replace(
        "\\",
        "\\\\"
    )

    value = value.replace(
        "'",
        "\\'"
    )

    value = value.replace(
        ",",
        "\\,"
    )

    value = value.replace(
        ":",
        "\\:"
    )

    return value


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
# ASSカラー取得
# ==========================================================

def _get_colors(settings):

    from subtitle_font import (
        get_subtitle_color
    )

    text_color_name = (
        settings.get(
            "text_color",
            DEFAULT_TEXT_COLOR
        )
    )

    outline_color_name = (
        settings.get(
            "outline_color",
            DEFAULT_OUTLINE_COLOR
        )
    )

    text_color_info = (
        get_subtitle_color(
            text_color_name
        )
    )

    outline_color_info = (
        get_subtitle_color(
            outline_color_name
        )
    )

    text_color_ass = (
        text_color_info["ass"]
    )

    outline_color_ass = (
        outline_color_info["ass"]
    )

    return (
        text_color_ass,
        outline_color_ass
    )


# ==========================================================
# 縁太さ
# ==========================================================

def _get_outline_width(settings):

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

    return outline_width


# ==========================================================
# FFmpeg subtitles filter生成
#
# ★重要
#
# 以下の形式を使用する。
#
# subtitles='/app/downloads/test.srt'
#
# filename= を使わない。
#
# ==========================================================

def _build_subtitles_filter(
    srt_path,
    fonts_dir,
    settings
):

    _log(
        "字幕filter生成 START"
    )

    # ======================================================
    # SRT絶対パス
    # ======================================================

    srt_absolute = _absolute_path(
        srt_path
    )

    _log(
        f"字幕filter用SRT絶対パス: {srt_absolute}"
    )

    escaped_srt = _escape_filter_path(
        srt_absolute
    )

    _log(
        f"字幕filter用SRTエスケープ後: {escaped_srt}"
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

    _log(
        f"FontName: {font_name}"
    )

    escaped_font_name = (
        _escape_style_value(
            font_name
        )
    )

    # ======================================================
    # 色
    # ======================================================

    (
        text_color_ass,
        outline_color_ass
    ) = _get_colors(
        settings
    )

    _log(
        f"PrimaryColour: {text_color_ass}"
    )

    _log(
        f"OutlineColour: {outline_color_ass}"
    )

    # ======================================================
    # 縁太さ
    # ======================================================

    outline_width = _get_outline_width(
        settings
    )

    _log(
        f"Outline: {outline_width}"
    )

    # ======================================================
    # force_style
    #
    # ここでは force_style 全体を
    # シングルクォートで囲む。
    # ======================================================

    force_style = (
        f"FontName={escaped_font_name},"
        f"PrimaryColour={text_color_ass},"
        f"OutlineColour={outline_color_ass},"
        f"Outline={outline_width}"
    )

    # ======================================================
    # subtitles filter
    #
    # ★ filename= は使わない
    #
    # ★ SRTパスを直接指定
    # ======================================================

    filter_value = (
        "subtitles="
        f"'{escaped_srt}'"
    )

    # ======================================================
    # fontsdir
    # ======================================================

    if fonts_dir is not None:

        fonts_absolute = _absolute_path(
            fonts_dir
        )

        escaped_fonts_dir = (
            _escape_filter_path(
                fonts_absolute
            )
        )

        filter_value += (
            f":fontsdir='{escaped_fonts_dir}'"
        )

    # ======================================================
    # force_style
    # ======================================================

    filter_value += (
        f":force_style='{force_style}'"
    )

    _log(
        f"完成字幕filter: {filter_value}"
    )

    _log(
        "字幕filter生成 COMPLETE"
    )

    return filter_value


# ==========================================================
# FFmpeg存在確認
# ==========================================================

def _find_ffmpeg():

    _log(
        "FFmpeg検索 START"
    )

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    if not ffmpeg_path:

        if Path(DEFAULT_FFMPEG).exists():

            ffmpeg_path = DEFAULT_FFMPEG

    if not ffmpeg_path:

        raise FileNotFoundError(
            "FFmpegが見つかりません"
        )

    _log(
        f"FFmpeg path: {ffmpeg_path}"
    )

    return ffmpeg_path


# ==========================================================
# SRT UTF-8確認
#
# FFmpeg/libassに渡すSRTはUTF-8として読めることを
# 事前に確認する。
# ==========================================================

def _verify_srt_utf8(srt_file):

    _log(
        "SRT UTF-8確認 START"
    )

    try:

        data = srt_file.read_bytes()

        data.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError as error:

        _log(
            "SRT UTF-8確認 FAILED"
        )

        raise RuntimeError(
            "SRTがUTF-8として読み込めません: "
            f"{srt_file}"
        ) from error

    _log(
        "SRT UTF-8確認 OK"
    )


# ==========================================================
# FFmpeg実行
# ==========================================================

def _run_ffmpeg(
    command,
    timeout=120
):

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

            encoding="utf-8",

            errors="replace",

            timeout=timeout,

            shell=False

        )

    except subprocess.TimeoutExpired as error:

        _log(
            "FFmpeg TIMEOUT"
        )

        raise RuntimeError(
            f"FFmpegが{timeout}秒以内に終了しませんでした"
        ) from error

    except Exception as error:

        _log(
            "subprocess.run ERROR"
        )

        _log(
            f"{type(error).__name__}: {error}"
        )

        raise

    _log(
        "FFmpeg終了"
    )

    _log(
        f"returncode: {result.returncode}"
    )

    return result


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

    input_file = (
        _absolute_path(
            input_path
        )
        if input_path is not None
        else DEFAULT_INPUT_MP4
    )

    output_file = (
        _absolute_path(
            output_path
        )
        if output_path is not None
        else DEFAULT_OUTPUT_MP4
    )

    srt_file = (
        _absolute_path(
            srt_path
        )
        if srt_path is not None
        else DEFAULT_INPUT_SRT
    )

    fonts_directory = (
        _absolute_path(
            fonts_dir
        )
        if fonts_dir is not None
        else DEFAULT_FONTS_DIR
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

    _log(
        f"MP4確認: {input_file}"
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
        "MP4確認 OK"
    )

    _log(
        f"MP4サイズ: {input_size} bytes"
    )

    # ======================================================
    # SRT確認
    # ======================================================

    _log(
        "SRT存在確認 START"
    )

    _log(
        f"SRT確認: {srt_file}"
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
        "SRT確認 OK"
    )

    _log(
        f"SRTサイズ: {srt_size} bytes"
    )

    # ======================================================
    # SRT UTF-8確認
    # ======================================================

    _verify_srt_utf8(
        srt_file
    )

    # ======================================================
    # 出力ディレクトリ
    # ======================================================

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ======================================================
    # 出力先が入力と同じ場合は拒否
    # ======================================================

    try:

        if input_file.samefile(
            output_file
        ):

            raise RuntimeError(
                "入力MP4と出力MP4が同じファイルです"
            )

    except FileNotFoundError:

        # outputがまだ存在しない場合は問題なし
        pass

    # ======================================================
    # 既存出力削除
    # ======================================================

    if output_file.exists():

        _log(
            "既存出力削除"
        )

        output_file.unlink()

    # ======================================================
    # フォントディレクトリ確認
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
            "WARNING: フォントディレクトリが存在しません"
        )

        _log(
            f"WARNING: {fonts_directory}"
        )

        _log(
            "WARNING: fontsdirなしで処理を継続します"
        )

        _log(
            "WARNING: システムフォント検索を使用します"
        )

    # ======================================================
    # subtitle_font.py設定
    # ======================================================

    settings = _get_font_settings(

        font=font,

        text_color=text_color,

        outline_color=outline_color,

        outline_width=outline_width

    )

    # ======================================================
    # fallback mode
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
            f"font: {settings.get('font', DEFAULT_FONT)}"
        )

        _log(
            "=========================================="
        )

    # ======================================================
    # FFmpeg検索
    # ======================================================

    ffmpeg_path = _find_ffmpeg()

    # ======================================================
    # FFmpeg実行直前SRT確認
    #
    # ★一時SRTは使用しない
    # ★元の test.srt を直接使用
    # ======================================================

    _log(
        "FFmpeg実行直前SRT確認 START"
    )

    _log(
        f"FFmpeg実行直前SRT: {srt_file}"
    )

    _log(
        f"FFmpeg実行直前SRT存在: {srt_file.exists()}"
    )

    if not srt_file.exists():

        raise FileNotFoundError(
            "FFmpeg実行直前にSRTが存在しません: "
            f"{srt_file}"
        )

    _log(
        f"FFmpeg実行直前SRTサイズ: "
        f"{srt_file.stat().st_size} bytes"
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
    # FFmpeg command
    # ======================================================

    command = [

        ffmpeg_path,

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

    _log(
        "FFmpeg cwd: 使用しません"
    )

    # ======================================================
    # FFmpeg実行
    # ======================================================

    result = _run_ffmpeg(
        command,
        timeout=120
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

        error_detail = (
            result.stderr.strip()
            if result.stderr
            else
            "stderrなし"
        )

        raise RuntimeError(
            "FFmpeg処理失敗 "
            f"(returncode={result.returncode})\n"
            f"{error_detail}"
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

    if output_size <= 0:

        raise RuntimeError(
            "FFmpeg出力ファイルが空です: "
            f"{output_file}"
        )

    _log(
        "出力ファイル確認 OK"
    )

    _log(
        f"出力サイズ: {output_size} bytes"
    )

    # ======================================================
    # 完了
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
