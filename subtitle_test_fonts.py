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
#
# 重要:
#
#   /app/downloads/fonts
#   が存在しない場合でもエラーにしない。
#
#   fontsdirが存在:
#       ↓
#       fontsdirを使用
#
#   fontsdirが存在しない:
#       ↓
#       システムフォント検索を使用
#
#
# FFmpeg subtitles filter対策:
#
#   PythonからSRTが存在していても、
#   libass/subtitles filter側から
#   /app/downloads/*.srt を開けない環境がある。
#
#   そのためFFmpeg実行時にはSRTを
#   一時ディレクトリへコピーして使用する。
#
# ==========================================================


from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import uuid


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

FFMPEG_CANDIDATES = (
    "/usr/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
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

def _log(message):
    print(
        "[SUBTITLE_TEST_FONTS]",
        message,
        flush=True
    )


# ==========================================================
# FFmpeg検索
# ==========================================================

def _find_ffmpeg():

    _log(
        "FFmpeg検索 START"
    )

    # ------------------------------------------------------
    # shutil.which()
    # ------------------------------------------------------

    which_path = shutil.which(
        "ffmpeg"
    )

    if which_path:

        ffmpeg_path = Path(
            which_path
        )

        if (
            ffmpeg_path.exists()
            and
            ffmpeg_path.is_file()
        ):

            _log(
                f"FFmpeg path: {ffmpeg_path}"
            )

            return str(
                ffmpeg_path
            )

    # ------------------------------------------------------
    # 固定パス
    # ------------------------------------------------------

    for candidate in FFMPEG_CANDIDATES:

        path = Path(
            candidate
        )

        if (
            path.exists()
            and
            path.is_file()
        ):

            _log(
                f"FFmpeg path: {path}"
            )

            return str(
                path
            )

    raise FileNotFoundError(
        "FFmpegが見つかりません"
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

    # ------------------------------------------------------
    # 標準設定
    # ------------------------------------------------------

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
# SRT UTF-8確認
# ==========================================================

def _check_srt_utf8(
    srt_file
):

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
            f"{error}"
        )

    _log(
        "SRT UTF-8確認 OK"
    )


# ==========================================================
# FFmpeg用SRT作成
#
# /app/downloads を直接libassに読ませず、
# /tmp配下へコピーする。
# ==========================================================

def _prepare_ffmpeg_srt(
    source_srt
):

    _log(
        "FFmpeg用SRT準備 START"
    )

    source_srt = Path(
        source_srt
    )

    if not source_srt.exists():

        raise FileNotFoundError(
            "元SRTが存在しません: "
            f"{source_srt}"
        )

    if not source_srt.is_file():

        raise FileNotFoundError(
            "元SRTがファイルではありません: "
            f"{source_srt}"
        )

    # ------------------------------------------------------
    # UTF-8として読み込み、
    # UTF-8 BOMなしで一時SRTを作成
    # ------------------------------------------------------

    try:

        text = source_srt.read_text(
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError as error:

        raise RuntimeError(
            "SRTをUTF-8として読み込めません: "
            f"{error}"
        )

    # ------------------------------------------------------
    # /tmp/ffmpeg_subtitles
    # ------------------------------------------------------

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="subtitle_test_"
        )
    )

    # ------------------------------------------------------
    # ASCIIだけのファイル名にする。
    #
    # 日本語・空白・特殊文字を避ける。
    # ------------------------------------------------------

    temp_srt = (
        temp_dir /
        "subtitle.srt"
    )

    temp_srt.write_text(
        text,
        encoding="utf-8",
        newline=""
    )

    # ------------------------------------------------------
    # 確認
    # ------------------------------------------------------

    if not temp_srt.exists():

        raise RuntimeError(
            "FFmpeg用一時SRTの作成に失敗しました: "
            f"{temp_srt}"
        )

    if not temp_srt.is_file():

        raise RuntimeError(
            "FFmpeg用SRTがファイルではありません: "
            f"{temp_srt}"
        )

    size = (
        temp_srt.stat().st_size
    )

    _log(
        f"元SRT: {source_srt}"
    )

    _log(
        f"FFmpeg用SRT: {temp_srt}"
    )

    _log(
        "FFmpeg用SRT作成 OK"
    )

    _log(
        f"FFmpeg用SRTサイズ: {size} bytes"
    )

    return temp_dir, temp_srt


# ==========================================================
# FFmpeg filter用エスケープ
#
# FFmpeg filtergraph用。
#
# Linux絶対パス:
#
# /tmp/abc/subtitle.srt
#
# はそのまま使用できるようにする。
# ==========================================================

def _escape_filter_path(
    path
):

    value = str(
        Path(path).resolve()
    )

    # ------------------------------------------------------
    # バックスラッシュ
    # ------------------------------------------------------

    value = value.replace(
        "\\",
        "\\\\"
    )

    # ------------------------------------------------------
    # filtergraphで特殊な : をエスケープ
    # ------------------------------------------------------

    value = value.replace(
        ":",
        "\\:"
    )

    # ------------------------------------------------------
    # カンマ
    # ------------------------------------------------------

    value = value.replace(
        ",",
        "\\,"
    )

    # ------------------------------------------------------
    # セミコロン
    # ------------------------------------------------------

    value = value.replace(
        ";",
        "\\;"
    )

    # ------------------------------------------------------
    # シングルクォート
    # ------------------------------------------------------

    value = value.replace(
        "'",
        "\\'"
    )

    # ------------------------------------------------------
    # [ ]
    # ------------------------------------------------------

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
# ASSスタイル値エスケープ
# ==========================================================

def _escape_style_value(
    value
):

    value = str(
        value
        if value is not None
        else ""
    )

    # ------------------------------------------------------
    # force_styleの区切りに使われる文字を処理
    # ------------------------------------------------------

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

    return value


# ==========================================================
# FFmpeg字幕filter生成
# ==========================================================

def _build_subtitles_filter(
    srt_path,
    fonts_dir,
    settings
):

    _log(
        "字幕filter生成 START"
    )

    # ------------------------------------------------------
    # 絶対パス化
    # ------------------------------------------------------

    srt_path = Path(
        srt_path
    ).resolve()

    _log(
        f"字幕filter用SRT絶対パス: {srt_path}"
    )

    escaped_srt = _escape_filter_path(
        srt_path
    )

    _log(
        f"字幕filter用SRTエスケープ後: {escaped_srt}"
    )

    # ------------------------------------------------------
    # フォント
    # ------------------------------------------------------

    font_name = (
        settings.get(
            "font"
        )
        or
        DEFAULT_FONT
    )

    font_name = _escape_style_value(
        font_name
    )

    # ------------------------------------------------------
    # 色
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # 縁太さ
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # ログ
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # force_style
    # ------------------------------------------------------

    force_style = (
        f"FontName={font_name},"
        f"PrimaryColour={text_color_ass},"
        f"OutlineColour={outline_color_ass},"
        f"Outline={outline_width}"
    )

    # ------------------------------------------------------
    # subtitles filter
    #
    # 重要:
    #
    # filename= を使わず、
    # subtitles='PATH'
    # とする。
    # ------------------------------------------------------

    filter_value = (
        "subtitles="
        f"'{escaped_srt}'"
    )

    # ------------------------------------------------------
    # fontsdir
    # ------------------------------------------------------

    if fonts_dir is not None:

        fonts_dir = Path(
            fonts_dir
        ).resolve()

        escaped_fonts_dir = (
            _escape_filter_path(
                fonts_dir
            )
        )

        filter_value += (
            f":fontsdir='{escaped_fonts_dir}'"
        )

    # ------------------------------------------------------
    # force_style
    # ------------------------------------------------------

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
# FFmpeg実行前SRT確認
# ==========================================================

def _verify_ffmpeg_srt(
    srt_file
):

    _log(
        "FFmpeg実行直前SRT確認 START"
    )

    srt_file = Path(
        srt_file
    ).resolve()

    _log(
        f"FFmpeg実行直前SRT: {srt_file}"
    )

    exists = (
        srt_file.exists()
    )

    _log(
        f"FFmpeg実行直前SRT存在: {exists}"
    )

    if not exists:

        raise FileNotFoundError(
            "FFmpeg用SRTが存在しません: "
            f"{srt_file}"
        )

    if not srt_file.is_file():

        raise FileNotFoundError(
            "FFmpeg用SRTがファイルではありません: "
            f"{srt_file}"
        )

    size = (
        srt_file.stat().st_size
    )

    _log(
        f"FFmpeg実行直前SRTサイズ: {size} bytes"
    )

    if size <= 0:

        raise RuntimeError(
            "FFmpeg用SRTが空です: "
            f"{srt_file}"
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

    if input_size <= 0:

        raise RuntimeError(
            "入力MP4が空です: "
            f"{input_file}"
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

    if srt_size <= 0:

        raise RuntimeError(
            "SRTが空です: "
            f"{srt_file}"
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

    _check_srt_utf8(
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
    # 出力ディレクトリ書き込み確認
    # ======================================================

    _log(
        "出力ディレクトリ確認 START"
    )

    if not os.access(
        output_file.parent,
        os.W_OK
    ):

        raise PermissionError(
            "出力ディレクトリに書き込み権限がありません: "
            f"{output_file.parent}"
        )

    _log(
        "出力ディレクトリ確認 OK"
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
    # フォントフォールバックログ
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
    # FFmpeg用SRT準備
    #
    # ここが重要。
    #
    # /app/downloads/test.srt
    #
    # を直接libassに渡さない。
    #
    # /tmp/subtitle_test_xxx/subtitle.srt
    #
    # を使用する。
    # ======================================================

    temp_dir = None
    ffmpeg_srt = None

    try:

        temp_dir, ffmpeg_srt = (
            _prepare_ffmpeg_srt(
                srt_file
            )
        )

        # ==================================================
        # 実行直前確認
        # ==================================================

        _verify_ffmpeg_srt(
            ffmpeg_srt
        )

        # ==================================================
        # 字幕filter
        # ==================================================

        subtitles_filter = (
            _build_subtitles_filter(

                srt_path=ffmpeg_srt,

                fonts_dir=(
                    fonts_directory
                    if use_fonts_dir
                    else None
                ),

                settings=settings

            )
        )

        # ==================================================
        # filter表示
        # ==================================================

        _log(
            "字幕filter:"
        )

        _log(
            subtitles_filter
        )

        # ==================================================
        # FFmpeg command
        # ==================================================

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

        # ==================================================
        # コマンド表示
        # ==================================================

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
            f"FFmpeg cwd: {temp_dir}"
        )

        # ==================================================
        # FFmpeg起動
        # ==================================================

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

                timeout=120,

                cwd=str(
                    temp_dir
                )

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

        # ==================================================
        # FFmpeg終了
        # ==================================================

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

        # ==================================================
        # stderr
        # ==================================================

        if result.stderr:

            _log(
                "FFmpeg stderr:"
            )

            print(
                result.stderr,
                flush=True
            )

        # ==================================================
        # FFmpeg失敗
        # ==================================================

        if result.returncode != 0:

            error_message = (
                "FFmpeg処理失敗 "
                f"(returncode={result.returncode})"
            )

            if result.stderr:

                error_message += (
                    "\n"
                    +
                    result.stderr.strip()
                )

            raise RuntimeError(
                error_message
            )

        # ==================================================
        # 出力確認
        # ==================================================

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

        # ==================================================
        # 完了
        # ==================================================

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

    finally:

        # ==================================================
        # 一時SRTディレクトリ削除
        # ==================================================

        if temp_dir is not None:

            try:

                if temp_dir.exists():

                    shutil.rmtree(
                        temp_dir,
                        ignore_errors=True
                    )

                    _log(
                        f"一時ファイル削除: {temp_dir}"
                    )

            except Exception as error:

                _log(
                    "WARNING: 一時ファイル削除失敗"
                )

                _log(
                    f"{type(error).__name__}: {error}"
                )


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
