# ==========================================================
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
