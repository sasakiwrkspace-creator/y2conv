# ==========================================================
# subtitle_test_fonts.py
#
# 字幕フォントFFmpegテスト
#
# test.mp4 + test.srt
#       ↓
# FFmpeg subtitles filter
#       ↓
# test_embed_fonts.mp4
#
# 重要:
#
#   /app/downloads/fonts が存在しない場合でもエラーにしない。
#
#   また、FFmpeg subtitles filter に絶対パスを直接渡すと
#   環境によって libass のファイルオープンに失敗する場合があるため、
#   FFmpegのcwdを /app/downloads に固定し、
#   subtitles filterには字幕ファイル名だけを渡す。
#
# ==========================================================


from pathlib import Path
import shutil
import subprocess
import time


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

def _log(message):
    print(
        "[SUBTITLE_TEST_FONTS]",
        message,
        flush=True
    )


# ==========================================================
# ファイル名をFFmpeg filter用にエスケープ
#
# 今回はFFmpegのcwdをDOWNLOAD_DIRに固定するため、
# 絶対パスではなくファイル名を渡す。
#
# それでもfilter parser上問題になる文字はエスケープする。
# ==========================================================

def _escape_filter_filename(filename):
    value = str(filename)

    value = value.replace(
        "\\",
        "\\\\"
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
# 字幕filter生成
#
# ★重要
#
# 絶対パス:
#
#   subtitles='/app/downloads/test.srt'
#
# ではなく、
#
#   subtitles=filename='test.srt'
#
# を使用する。
#
# FFmpegのcwdを /app/downloads にしているため、
# test.srt は確実に /app/downloads/test.srt として解決される。
# ==========================================================

def _build_subtitles_filter(
    srt_filename,
    fonts_dir,
    settings
):

    _log(
        "字幕filter生成 START"
    )

    # ======================================================
    # subtitle_font.py
    # ======================================================

    from subtitle_font import (
        get_subtitle_color
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
    # ======================================================

    text_color_info = (
        get_subtitle_color(
            settings.get(
                "text_color",
                DEFAULT_TEXT_COLOR
            )
        )
    )

    # ======================================================
    # 縁色
    # ======================================================

    outline_color_info = (
        get_subtitle_color(
            settings.get(
                "outline_color",
                DEFAULT_OUTLINE_COLOR
            )
        )
    )

    text_color_ass = (
        text_color_info["ass"]
    )

    outline_color_ass = (
        outline_color_info["ass"]
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
    # filter用SRTファイル名
    # ======================================================

    escaped_filename = (
        _escape_filter_filename(
            srt_filename
        )
    )

    # ======================================================
    # force_style
    # ======================================================

    force_style = (
        f"FontName={font_name},"
        f"PrimaryColour={text_color_ass},"
        f"OutlineColour={outline_color_ass},"
        f"Outline={outline_width}"
    )

    # ======================================================
    # subtitles filter
    #
    # filename= を明示する。
    # ======================================================

    filter_value = (
        "subtitles="
        f"filename='{escaped_filename}'"
    )

    # ======================================================
    # fontsdir
    # ======================================================

    if fonts_dir is not None:

        fonts_dir_name = Path(
            fonts_dir
        ).name

        escaped_fonts_dir = (
            _escape_filter_filename(
                fonts_dir_name
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

    # ======================================================
    # ログ
    # ======================================================

    _log(
        f"FontName: {font_name}"
    )

    _log(
        f"PrimaryColour: {text_color_ass}"
    )

    _log(
        f"OutlineColour: {outline_color_ass}"
    )

    _log(
        f"Outline: {outline_width}"
    )

    _log(
        f"完成字幕filter: {filter_value}"
    )

    _log(
        "字幕filter生成 COMPLETE"
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

    input_file = (
        DEFAULT_INPUT_MP4
        if input_path is None
        else Path(input_path)
    )

    output_file = (
        DEFAULT_OUTPUT_MP4
        if output_path is None
        else Path(output_path)
    )

    srt_file = (
        DEFAULT_INPUT_SRT
        if srt_path is None
        else Path(srt_path)
    )

    fonts_directory = (
        DEFAULT_FONTS_DIR
        if fonts_dir is None
        else Path(fonts_dir)
    )

    # ======================================================
    # 絶対パス化
    # ======================================================

    input_file = input_file.resolve()
    output_file = output_file.resolve()
    srt_file = srt_file.resolve()
    fonts_directory = fonts_directory.resolve()

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
        f"MP4確認: {input_file}"
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
        f"SRT確認: {srt_file}"
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

    _log(
        "SRT UTF-8確認 START"
    )

    try:

        srt_file.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError as error:

        _log(
            "SRT UTF-8確認 FAILED"
        )

        raise RuntimeError(
            "SRTがUTF-8として読み込めません: "
            f"{error}"
        )

    _log(
        "SRT UTF-8確認 OK"
    )

    # ======================================================
    # SRT読み取り権限確認
    # ======================================================

    _log(
        "SRT読み取り確認 START"
    )

    try:

        with srt_file.open(
            "rb"
        ) as file:

            file.read(1)

    except Exception as error:

        raise RuntimeError(
            "SRTを読み取れません: "
            f"{srt_file} / {error}"
        )

    _log(
        "SRT読み取り確認 OK"
    )

    # ======================================================
    # 出力ディレクトリ
    # ======================================================

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ======================================================
    # FFmpeg確認
    # ======================================================

    _log(
        "FFmpeg検索 START"
    )

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    _log(
        f"shutil.which(ffmpeg): {ffmpeg_path}"
    )

    if not ffmpeg_path:

        raise FileNotFoundError(
            "ffmpegが見つかりません"
        )

    ffmpeg_path = str(
        Path(ffmpeg_path).resolve()
    )

    _log(
        f"FFmpeg path: {ffmpeg_path}"
    )

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
            "WARNING: システムフォント検索を使用します"
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
    # FFmpeg用SRT
    #
    # ★重要
    #
    # 元SRTをそのまま使わず、DOWNLOAD_DIR内にコピーする。
    #
    # FFmpegのcwdもDOWNLOAD_DIRに固定する。
    #
    # filterには絶対パスを渡さず、
    #
    #   filename='.test.ffmpeg_xxx.srt'
    #
    # とする。
    # ======================================================

    _log(
        "FFmpeg用SRT準備 START"
    )

    temp_srt_name = (
        f".{srt_file.stem}."
        f"ffmpeg_{time.time_ns()}.srt"
    )

    temp_srt_file = (
        DOWNLOAD_DIR /
        temp_srt_name
    )

    _log(
        f"元SRT: {srt_file}"
    )

    _log(
        f"FFmpeg用SRT: {temp_srt_file}"
    )

    try:

        temp_srt_file.write_bytes(
            srt_file.read_bytes()
        )

    except Exception as error:

        raise RuntimeError(
            "FFmpeg用SRTを作成できません: "
            f"{error}"
        )

    # ======================================================
    # 一時SRT確認
    # ======================================================

    if not temp_srt_file.exists():

        raise RuntimeError(
            "FFmpeg用SRT作成後もファイルが存在しません: "
            f"{temp_srt_file}"
        )

    if not temp_srt_file.is_file():

        raise RuntimeError(
            "FFmpeg用SRTがファイルではありません: "
            f"{temp_srt_file}"
        )

    temp_srt_size = (
        temp_srt_file.stat().st_size
    )

    _log(
        "FFmpeg用SRT作成 OK"
    )

    _log(
        f"FFmpeg用SRTサイズ: {temp_srt_size} bytes"
    )

    # ======================================================
    # FFmpeg実行直前確認
    # ======================================================

    _log(
        "FFmpeg実行直前SRT確認 START"
    )

    _log(
        f"FFmpeg実行直前SRT: {temp_srt_file}"
    )

    _log(
        f"FFmpeg実行直前SRT存在: "
        f"{temp_srt_file.exists()}"
    )

    _log(
        f"FFmpeg実行直前SRTサイズ: "
        f"{temp_srt_file.stat().st_size}"
    )

    # ======================================================
    # 字幕filter
    # ======================================================

    subtitles_filter = (
        _build_subtitles_filter(

            srt_filename=temp_srt_name,

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
    # 出力ファイル削除
    # ======================================================

    if output_file.exists():

        _log(
            "既存出力削除"
        )

        output_file.unlink()

    # ======================================================
    # FFmpeg command
    #
    # ★重要
    #
    # cwd=DOWNLOAD_DIR で実行する。
    #
    # 入力・出力は絶対パス。
    # 字幕だけはfilter内部で相対ファイル名。
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

    _log(
        f"FFmpeg cwd: {DOWNLOAD_DIR}"
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

    result = None

    try:

        result = subprocess.run(

            command,

            cwd=str(
                DOWNLOAD_DIR
            ),

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

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

    finally:

        # ==================================================
        # 一時SRT削除
        # ==================================================

        if temp_srt_file.exists():

            try:

                temp_srt_file.unlink()

                _log(
                    f"一時ファイル削除: "
                    f"{temp_srt_file}"
                )

            except Exception as error:

                _log(
                    "WARNING: 一時SRT削除失敗: "
                    f"{error}"
                )

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
            "FFmpeg出力ファイルのサイズが0です: "
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
