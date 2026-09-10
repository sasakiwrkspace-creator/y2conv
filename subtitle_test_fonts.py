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
#       システムフォント検索を使用
#       ↓
#       FFmpeg処理を継続
#
#
# 今回の重要修正:
#
#   1. 一時SRTファイルを作成しない
#   2. 元のSRTファイルを直接使用する
#   3. subtitles filterには絶対パスを渡す
#   4. cwdに依存しない
#   5. FFmpeg filter用にパスをエスケープする
#   6. ffmpegの存在を事前確認する
#   7. SRTをUTF-8として事前確認する
#
# ==========================================================


from pathlib import Path
import shutil
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
# FFmpeg
# ==========================================================

DEFAULT_FFMPEG = (
    "/usr/bin/ffmpeg"
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
# FFmpeg timeout
# ==========================================================

FFMPEG_TIMEOUT = 120


# ==========================================================
# ログ
# ==========================================================

def _log(
    message
):
    """
    共通ログ。
    """

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
    """
    subtitle_font.pyから字幕設定を取得する。
    """

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

    # ======================================================
    # settingsがdictでない場合
    # ======================================================

    if not isinstance(
        settings,
        dict
    ):

        raise RuntimeError(
            "subtitle_font.pyの"
            "select_subtitle_font()が"
            "dictを返しませんでした"
        )

    _log(
        f"subtitle settings: {settings}"
    )

    return settings


# ==========================================================
# FFmpeg filter用パスエスケープ
# ==========================================================

def _escape_filter_path(
    path
):
    """
    FFmpeg subtitles filter 用のファイルパスを
    filtergraphで安全に扱える形へ変換する。

    重要:
        subprocessへ渡す引数全体をshell用に
        エスケープするのではない。

        ここではFFmpegのfiltergraph内部で
        特殊文字として扱われる文字だけを処理する。
    """

    value = str(
        Path(path).resolve()
    )

    # ======================================================
    # バックスラッシュ
    #
    # 最初に処理する。
    # ======================================================

    value = value.replace(
        "\\",
        "\\\\"
    )

    # ======================================================
    # FFmpeg filtergraphで特殊な文字
    # ======================================================

    value = value.replace(
        ":",
        "\\:"
    )

    value = value.replace(
        ",",
        "\\,"
    )

    value = value.replace(
        "[",
        "\\["
    )

    value = value.replace(
        "]",
        "\\]"
    )

    # ======================================================
    # シングルクォート
    # ======================================================

    value = value.replace(
        "'",
        "\\'"
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
    """
    FFmpeg subtitles filterを生成する。

    SRTは必ず絶対パスを使用する。

    相対パスやFFmpegのcwdには依存しない。
    """

    _log(
        "字幕filter生成 START"
    )

    # ======================================================
    # SRT
    # ======================================================

    srt_file = Path(
        srt_path
    ).resolve()

    # ======================================================
    # 最終確認
    # ======================================================

    if not srt_file.exists():

        raise FileNotFoundError(
            "字幕filter用SRTが存在しません: "
            f"{srt_file}"
        )

    if not srt_file.is_file():

        raise FileNotFoundError(
            "字幕filter用SRTがファイルではありません: "
            f"{srt_file}"
        )

    escaped_srt = _escape_filter_path(
        srt_file
    )

    _log(
        f"字幕filter用SRT絶対パス: {srt_file}"
    )

    _log(
        f"字幕filter用SRTエスケープ後: "
        f"{escaped_srt}"
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
    # subtitle_font.pyから色取得
    # ======================================================

    from subtitle_font import (
        get_subtitle_color
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

    # ======================================================
    # ASSカラー
    # ======================================================

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

    # ======================================================
    # 範囲制限
    # ======================================================

    outline_width = max(
        0,
        min(
            outline_width,
            10
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
    # filename=に絶対パスを渡す。
    # ======================================================

    filter_value = (
        "subtitles="
        f"filename='{escaped_srt}'"
    )

    # ======================================================
    # fontsdir
    #
    # 存在する場合のみ追加。
    # ======================================================

    if fonts_dir is not None:

        fonts_directory = (
            Path(
                fonts_dir
            ).resolve()
        )

        if (
            fonts_directory.exists()
            and
            fonts_directory.is_dir()
        ):

            escaped_fonts_dir = (
                _escape_filter_path(
                    fonts_directory
                )
            )

            filter_value += (
                f":fontsdir='{escaped_fonts_dir}'"
            )

            _log(
                f"fontsdir追加: "
                f"{fonts_directory}"
            )

    # ======================================================
    # force_style
    # ======================================================

    filter_value += (
        f":force_style='{force_style}'"
    )

    # ======================================================
    # 設定ログ
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
# FFmpeg存在確認
# ==========================================================

def _find_ffmpeg():
    """
    FFmpegの実行ファイルを取得する。
    """

    _log(
        "FFmpeg検索 START"
    )

    # ======================================================
    # 標準パス
    # ======================================================

    if Path(
        DEFAULT_FFMPEG
    ).is_file():

        ffmpeg_path = (
            DEFAULT_FFMPEG
        )

        _log(
            f"FFmpeg path: {ffmpeg_path}"
        )

        return ffmpeg_path

    # ======================================================
    # PATH検索
    # ======================================================

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    _log(
        f"shutil.which(ffmpeg): "
        f"{ffmpeg_path}"
    )

    if ffmpeg_path is None:

        raise FileNotFoundError(
            "FFmpegが見つかりません"
        )

    _log(
        f"FFmpeg path: {ffmpeg_path}"
    )

    return ffmpeg_path


# ==========================================================
# SRT UTF-8確認
# ==========================================================

def _validate_srt_utf8(
    srt_file
):
    """
    SRTをUTF-8として読めることを確認する。

    FFmpeg実行前にPython側で確認することで、
    字幕文字コードによる失敗を早期発見する。
    """

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
            f"{srt_file}"
        ) from error

    except OSError as error:

        _log(
            "SRT読み込み FAILED"
        )

        raise RuntimeError(
            "SRTを読み込めません: "
            f"{srt_file}"
        ) from error

    _log(
        "SRT UTF-8確認 OK"
    )


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
    """
    MP4 + SRTをFFmpeg subtitles filterで処理する。

    戻り値:
        Path
            出力MP4のパス
    """

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
    # 絶対パス化
    #
    # FFmpegには絶対パスを渡す。
    # ======================================================

    input_file = (
        input_file.resolve()
    )

    output_file = (
        output_file.resolve()
    )

    srt_file = (
        srt_file.resolve()
    )

    fonts_directory = (
        fonts_directory.resolve()
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

    if input_size <= 0:

        raise RuntimeError(
            "入力MP4が空です: "
            f"{input_file}"
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

    if srt_size <= 0:

        raise RuntimeError(
            "SRTファイルが空です: "
            f"{srt_file}"
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

    _validate_srt_utf8(
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
    # 既存出力削除
    # ======================================================

    if output_file.exists():

        _log(
            "既存出力削除"
        )

        try:

            output_file.unlink()

        except OSError as error:

            raise RuntimeError(
                "既存出力ファイルを削除できません: "
                f"{output_file}"
            ) from error

    # ======================================================
    # フォントディレクトリ確認
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
                f"fontsdir使用: "
                f"{fonts_directory}"
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
    # subtitle_font.pyから字幕設定取得
    # ======================================================

    settings = _get_font_settings(

        font=font,

        text_color=text_color,

        outline_color=outline_color,

        outline_width=outline_width

    )

    # ======================================================
    # フォントフォールバック
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
            f"font: "
            f"{settings.get('font', DEFAULT_FONT)}"
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
    # 一時SRTは作らない。
    # 元のSRTを直接使用する。
    # ======================================================

    _log(
        "FFmpeg実行直前SRT確認 START"
    )

    _log(
        f"FFmpeg実行直前SRT: "
        f"{srt_file}"
    )

    _log(
        f"FFmpeg実行直前SRT存在: "
        f"{srt_file.exists()}"
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
    # 字幕filter生成
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

    # ======================================================
    # FFmpeg開始
    #
    # ★重要
    #
    # cwdは指定しない。
    # SRTもMP4もすべて絶対パス。
    # ======================================================

    _log(
        "FFmpeg cwd: 使用しません"
    )

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

            timeout=FFMPEG_TIMEOUT

        )

    except subprocess.TimeoutExpired as error:

        _log(
            "FFmpeg TIMEOUT"
        )

        raise RuntimeError(
            "FFmpegが"
            f"{FFMPEG_TIMEOUT}秒以内に"
            "終了しませんでした"
        ) from error

    except FileNotFoundError as error:

        _log(
            "FFmpeg実行ファイルが見つかりません"
        )

        raise RuntimeError(
            "FFmpegを起動できません: "
            f"{ffmpeg_path}"
        ) from error

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
    # stdout
    # ======================================================

    if result.stdout:

        _log(
            "FFmpeg stdout:"
        )

        print(
            result.stdout,
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
            "FFmpegからエラー詳細がありません"
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
        f"出力サイズ: "
        f"{output_size} bytes"
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

    _log(
        f"output: {output_file}"
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
            f"ERROR TYPE: "
            f"{type(error).__name__}"
        )

        print(
            f"ERROR: {error}"
        )

        print(
            "=========================================="
        )

        raise
