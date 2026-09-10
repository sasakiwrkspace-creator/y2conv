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
# 今回の修正:
#
#   1. SRTをFFmpeg実行直前にUTF-8一時ファイルへコピー
#   2. FFmpeg実行直前にSRT存在・サイズを再確認
#   3. subtitles filter用パスを安全にエスケープ
#   4. fontsdir用パスも安全にエスケープ
#   5. FontName等のforce_style値をエスケープ
#   6. FFmpeg終了後に一時SRTを削除
#   7. ffmpeg実行ファイルを固定せずPATHから検出
#   8. FFmpegエラー時にstderrをそのまま表示
#   9. 入力・出力パスを絶対パス化
#  10. 既存出力をFFmpeg開始前に削除
#
# ==========================================================

from pathlib import Path
import os
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
# FFmpeg設定
# ==========================================================

FFMPEG_THREADS = "1"

FFMPEG_PRESET = "ultrafast"

FFMPEG_CRF = "28"

FFMPEG_AUDIO_BITRATE = "128k"

FFMPEG_TIMEOUT = 120


# ==========================================================
# ログ
# ==========================================================

def _log(
    message
):

    try:

        print(
            "[SUBTITLE_TEST_FONTS]",
            message,
            flush=True
        )

    except Exception:

        pass


# ==========================================================
# FFmpeg取得
# ==========================================================

def _find_ffmpeg():

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

        raise RuntimeError(
            "FFmpegがPATH上に見つかりません。"
        )

    ffmpeg_path = str(
        Path(
            ffmpeg_path
        ).resolve()
    )

    _log(
        f"FFmpeg path: {ffmpeg_path}"
    )

    return ffmpeg_path


# ==========================================================
# Path絶対化
# ==========================================================

def _resolve_path(
    path
):

    return (
        Path(path)
        .expanduser()
        .resolve()
    )


# ==========================================================
# ファイル確認
# ==========================================================

def _validate_file(
    path,
    label
):

    path = _resolve_path(
        path
    )

    _log(
        f"{label}確認: {path}"
    )

    if not path.exists():

        raise FileNotFoundError(
            f"{label}が存在しません: {path}"
        )

    if not path.is_file():

        raise FileNotFoundError(
            f"{label}がファイルではありません: {path}"
        )

    try:

        size = path.stat().st_size

    except OSError as error:

        raise RuntimeError(
            f"{label}のサイズを取得できません: "
            f"{error}"
        ) from error

    if size <= 0:

        raise RuntimeError(
            f"{label}が0 bytesです: {path}"
        )

    _log(
        f"{label}確認 OK"
    )

    _log(
        f"{label}サイズ: {size} bytes"
    )

    return path


# ==========================================================
# SRT UTF-8確認
# ==========================================================

def _validate_srt_utf8(
    srt_path
):

    srt_path = _resolve_path(
        srt_path
    )

    _log(
        "SRT UTF-8確認 START"
    )

    try:

        with open(
            srt_path,
            "r",
            encoding="utf-8-sig"
        ) as file:

            content = file.read(
                4096
            )

    except UnicodeDecodeError as error:

        raise RuntimeError(
            "SRTがUTF-8として読み込めません。"
        ) from error

    except OSError as error:

        raise RuntimeError(
            f"SRT読み込みに失敗しました: {error}"
        ) from error

    if not content.strip():

        raise RuntimeError(
            "SRTが空です。"
        )

    _log(
        "SRT UTF-8確認 OK"
    )

    return True


# ==========================================================
# FFmpeg filter path escape
#
# 重要:
#
# subtitles='/path/file.srt'
#
# の '/path/file.srt' はshellではなく
# FFmpeg filtergraphとして解釈される。
#
# ==========================================================

def _escape_filter_path(
    path
):

    value = str(
        _resolve_path(path)
    )

    # LinuxでもWindowsでもfiltergraph上は
    # forward slashへ統一する。
    value = value.replace(
        "\\",
        "/"
    )

    # filtergraph特殊文字
    value = value.replace(
        "'",
        r"\'"
    )

    value = value.replace(
        ":",
        r"\:"
    )

    value = value.replace(
        ";",
        r"\;"
    )

    value = value.replace(
        "[",
        r"\["
    )

    value = value.replace(
        "]",
        r"\]"
    )

    value = value.replace(
        "\n",
        r"\n"
    )

    return value


# ==========================================================
# force_style値 escape
# ==========================================================

def _escape_style_value(
    value
):

    value = str(
        value
    )

    value = value.replace(
        "\\",
        r"\\"
    )

    value = value.replace(
        "'",
        r"\'"
    )

    value = value.replace(
        ":",
        r"\:"
    )

    value = value.replace(
        ",",
        r"\,"
    )

    value = value.replace(
        ";",
        r"\;"
    )

    return value


# ==========================================================
# SRT FFmpeg専用一時ファイル作成
#
# 元のtest.srtを直接FFmpegへ渡さず、
# FFmpeg実行直前に同じディレクトリへコピーする。
#
# これにより:
#
#   - ファイル存在確認
#   - UTF-8確認
#   - FFmpegアクセス確認
#
# を確実に行う。
# ==========================================================

def _prepare_ffmpeg_srt(
    srt_path
):

    srt_path = _resolve_path(
        srt_path
    )

    _log(
        "FFmpeg用SRT準備 START"
    )

    _log(
        f"元SRT: {srt_path}"
    )

    # timestampを使って毎回別名にする。
    timestamp = time.time_ns()

    temp_srt = (
        srt_path.parent
        /
        (
            "."
            +
            srt_path.stem
            +
            f".ffmpeg_{timestamp}.srt"
        )
    )

    _log(
        f"FFmpeg用SRT: {temp_srt}"
    )

    # ------------------------------------------------------
    # UTF-8として読み込み
    # ------------------------------------------------------

    try:

        with open(
            srt_path,
            "r",
            encoding="utf-8-sig"
        ) as source:

            content = source.read()

    except UnicodeDecodeError as error:

        raise RuntimeError(
            "SRTをUTF-8として読み込めません。"
        ) from error

    except OSError as error:

        raise RuntimeError(
            f"SRT読み込みに失敗しました: {error}"
        ) from error

    if not content.strip():

        raise RuntimeError(
            "SRTの内容が空です。"
        )

    # ------------------------------------------------------
    # UTF-8 BOMなしで保存
    # ------------------------------------------------------

    try:

        with open(
            temp_srt,
            "w",
            encoding="utf-8",
            newline="\n"
        ) as target:

            target.write(
                content
            )

    except OSError as error:

        raise RuntimeError(
            f"FFmpeg用SRTを作成できません: {error}"
        ) from error

    # ------------------------------------------------------
    # 作成確認
    # ------------------------------------------------------

    if not temp_srt.exists():

        raise RuntimeError(
            "FFmpeg用SRTが作成されていません。"
        )

    if not temp_srt.is_file():

        raise RuntimeError(
            "FFmpeg用SRTが通常ファイルではありません。"
        )

    try:

        temp_size = (
            temp_srt.stat().st_size
        )

    except OSError as error:

        raise RuntimeError(
            f"FFmpeg用SRTのサイズ取得に失敗しました: {error}"
        ) from error

    if temp_size <= 0:

        raise RuntimeError(
            "FFmpeg用SRTが0 bytesです。"
        )

    _log(
        "FFmpeg用SRT作成 OK"
    )

    _log(
        f"FFmpeg用SRTサイズ: {temp_size} bytes"
    )

    return temp_srt


# ==========================================================
# FFmpeg用SRT削除
# ==========================================================

def _remove_file(
    path
):

    if path is None:
        return

    try:

        path = Path(
            path
        )

    except Exception:

        return

    try:

        if path.exists():

            path.unlink()

            _log(
                f"一時ファイル削除: {path}"
            )

    except Exception as error:

        _log(
            f"一時ファイル削除失敗: {error}"
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

    if not isinstance(
        settings,
        dict
    ):

        raise RuntimeError(
            "subtitle_font.select_subtitle_font() "
            "の戻り値がdictではありません。"
        )

    _log(
        f"subtitle settings: {settings}"
    )

    return settings


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

    font_name = str(
        font_name
    ).strip()

    if not font_name:

        font_name = DEFAULT_FONT

    escaped_font_name = (
        _escape_style_value(
            font_name
        )
    )

    # ======================================================
    # subtitle_font.pyからカラー取得
    # ======================================================

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

    if not text_color_info:

        raise RuntimeError(
            f"文字色が取得できません: "
            f"{text_color_name}"
        )

    if not outline_color_info:

        raise RuntimeError(
            f"縁色が取得できません: "
            f"{outline_color_name}"
        )

    text_color_ass = (
        text_color_info.get(
            "ass"
        )
    )

    outline_color_ass = (
        outline_color_info.get(
            "ass"
        )
    )

    if not text_color_ass:

        raise RuntimeError(
            f"文字色ASS値がありません: "
            f"{text_color_name}"
        )

    if not outline_color_ass:

        raise RuntimeError(
            f"縁色ASS値がありません: "
            f"{outline_color_name}"
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
    # ======================================================

    force_style = (
        "FontName="
        +
        escaped_font_name
        +
        ",PrimaryColour="
        +
        str(
            text_color_ass
        )
        +
        ",OutlineColour="
        +
        str(
            outline_color_ass
        )
        +
        ",Outline="
        +
        str(
            outline_width
        )
    )

    # ======================================================
    # subtitles filter
    # ======================================================

    filter_value = (
        "subtitles='"
        +
        escaped_srt
        +
        "'"
    )

    # ======================================================
    # fontsdir
    # ======================================================

    if fonts_dir is not None:

        fonts_dir = _resolve_path(
            fonts_dir
        )

        if fonts_dir.is_dir():

            escaped_fonts_dir = (
                _escape_filter_path(
                    fonts_dir
                )
            )

            filter_value += (
                ":fontsdir='"
                +
                escaped_fonts_dir
                +
                "'"
            )

            _log(
                f"fontsdir使用: {fonts_dir}"
            )

    # ======================================================
    # force_style
    # ======================================================

    filter_value += (
        ":force_style='"
        +
        force_style
        +
        "'"
    )

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

    temp_srt_file = None

    try:

        # ==================================================
        # パス
        # ==================================================

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

        input_file = _resolve_path(
            input_file
        )

        output_file = _resolve_path(
            output_file
        )

        srt_file = _resolve_path(
            srt_file
        )

        fonts_directory = _resolve_path(
            fonts_directory
        )

        # ==================================================
        # パス表示
        # ==================================================

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

        # ==================================================
        # MP4確認
        # ==================================================

        _log(
            "MP4存在確認 START"
        )

        input_file = _validate_file(
            input_file,
            "MP4"
        )

        # ==================================================
        # SRT確認
        # ==================================================

        _log(
            "SRT存在確認 START"
        )

        srt_file = _validate_file(
            srt_file,
            "SRT"
        )

        # ==================================================
        # SRT UTF-8確認
        # ==================================================

        _validate_srt_utf8(
            srt_file
        )

        # ==================================================
        # 出力ディレクトリ
        # ==================================================

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # ==================================================
        # 入力と出力が同じ場合を禁止
        # ==================================================

        if input_file == output_file:

            raise RuntimeError(
                "入力MP4と出力MP4が同じです。"
            )

        # ==================================================
        # 既存出力削除
        # ==================================================

        if output_file.exists():

            _log(
                "既存出力削除"
            )

            if not output_file.is_file():

                raise RuntimeError(
                    "既存出力パスがファイルではありません: "
                    f"{output_file}"
                )

            output_file.unlink()

            _log(
                "既存出力削除 OK"
            )

        # ==================================================
        # fontsdir確認
        # ==================================================

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
                f"WARNING: システムフォント検索を使用します"
            )

        # ==================================================
        # subtitle_font.py設定
        # ==================================================

        settings = _get_font_settings(

            font=font,

            text_color=text_color,

            outline_color=outline_color,

            outline_width=outline_width

        )

        # ==================================================
        # FONT FALLBACK MODE
        # ==================================================

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
                f"font: {settings.get('font')}"
            )

            _log(
                "=========================================="
            )

        # ==================================================
        # FFmpeg確認
        # ==================================================

        ffmpeg_path = _find_ffmpeg()

        # ==================================================
        # ★重要
        # FFmpeg用SRTを作成
        # ==================================================

        temp_srt_file = _prepare_ffmpeg_srt(
            srt_file
        )

        # ==================================================
        # FFmpeg実行直前SRT確認
        # ==================================================

        _log(
            "FFmpeg実行直前SRT確認 START"
        )

        if not temp_srt_file.exists():

            raise RuntimeError(
                "FFmpeg実行直前にSRTが存在しません: "
                f"{temp_srt_file}"
            )

        if not temp_srt_file.is_file():

            raise RuntimeError(
                "FFmpeg実行直前のSRTがファイルではありません: "
                f"{temp_srt_file}"
            )

        temp_srt_size = (
            temp_srt_file.stat().st_size
        )

        if temp_srt_size <= 0:

            raise RuntimeError(
                "FFmpeg実行直前のSRTが0 bytesです。"
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
            f"{temp_srt_size} bytes"
        )

        # ==================================================
        # subtitles filter
        # ==================================================

        subtitles_filter = (
            _build_subtitles_filter(

                srt_path=temp_srt_file,

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
        # FFmpegコマンド
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
            FFMPEG_THREADS,

            "-preset",
            FFMPEG_PRESET,

            "-crf",
            FFMPEG_CRF,

            "-c:a",
            "aac",

            "-b:a",
            FFMPEG_AUDIO_BITRATE,

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
            " ".join(
                str(item)
                for item in command
            ),
            flush=True
        )

        print(
            "==========================================",
            flush=True
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

                stdout=subprocess.DEVNULL,

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
                f"FFmpegが{FFMPEG_TIMEOUT}秒以内に"
                "終了しませんでした"
            ) from error

        except OSError as error:

            _log(
                "FFmpeg起動 ERROR"
            )

            _log(
                f"{type(error).__name__}: {error}"
            )

            raise RuntimeError(
                f"FFmpegを起動できません: {error}"
            ) from error

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

            stderr_text = (
                result.stderr.strip()
                if result.stderr
                else
                "FFmpegからエラー内容が返されませんでした。"
            )

            raise RuntimeError(
                "FFmpeg処理失敗 "
                f"(returncode={result.returncode})\n"
                +
                stderr_text
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
                "FFmpeg出力ファイルが0 bytesです。"
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

        _log(
            f"output: {output_file}"
        )

        _log(
            f"output size: {output_size} bytes"
        )

        print(
            "==========================================",
            flush=True
        )

        return output_file

    finally:

        # ==================================================
        # FFmpeg用SRT削除
        # ==================================================

        _remove_file(
            temp_srt_file
        )


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
