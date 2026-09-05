# =====================================
# Subtitle - Low Memory Edition
# subtitle.py
#
# 512MB RAM環境向け
#
# MP4動画へSRT字幕を焼き込む
#
# 入力:
#   config.py の DOWNLOAD_DIR/xxx.mp4
#   config.py の DOWNLOAD_DIR/xxx.srt
#
# 出力:
#   入力MP4と同じディレクトリ
#   xxx_sub_embed.mp4
#
# FFmpegを使用
#
# 重要:
#   - 元動画の解像度を維持
#   - 日本語字幕対応
#   - subtitle_font.pyの設定を使用
#   - フォントを明示
#   - 文字色を反映
#   - 縁色を反映
#   - 縁の太さを反映
#   - 動画は再エンコード
#   - audioはcopy
#   - FFmpegを1スレッドに制限
#   - ultrafastでメモリ負荷を抑制
#   - FFmpegログを最大100行だけ保持
#   - downloadsの場所はconfig.pyで管理
#
# subtitle_font.py との連携:
#
#   settings = select_subtitle_font(...)
#
#   create_subtitle_mp4(
#       mp4_path,
#       srt_path,
#       subtitle_settings=settings
#   )
#
#   ↓
#
#   subtitle.py
#
#   ↓
#
#   FFmpeg force_style
#
#   ↓
#
#   字幕付きMP4
# =====================================

import os
import sys
import time
import shutil
import subprocess

from pathlib import Path
from collections import deque

from config import DOWNLOAD_DIR

from subtitle_font import (
    SUBTITLE_COLORS,
    get_default_subtitle_font_settings,
)


# =====================================
# 設定
# =====================================

DOWNLOADS_DIR = Path(
    DOWNLOAD_DIR
)

MAX_FFMPEG_LOG_LINES = 100

# 512MB環境向け
FFMPEG_THREADS = "1"

# CPU負荷・メモリ負荷を抑える
FFMPEG_PRESET = "ultrafast"

# 画質
FFMPEG_CRF = "23"


# =====================================
# ログ
# =====================================

def log(message):

    print(
        "[SUBTITLE]",
        message,
        flush=True
    )


# =====================================
# 入力ファイル確認
# =====================================

def validate_input_file(
    file_path,
    extension
):

    path = Path(
        file_path
    )

    if not path.exists():

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"ファイルではありません: {path}"
        )

    if path.suffix.lower() != extension.lower():

        raise ValueError(
            f"{extension} ファイルではありません: {path}"
        )

    try:

        size = path.stat().st_size

    except OSError as error:

        raise RuntimeError(
            f"ファイルサイズを確認できません: {error}"
        ) from error

    if size <= 0:

        raise ValueError(
            f"ファイルが0 bytesです: {path}"
        )

    return path


# =====================================
# 出力ファイル名
#
# 通常:
#
#   video.mp4
#       ↓
#   video_sub_embed.mp4
#
# すでに _sub_embed の場合:
#
#   video_sub_embed.mp4
#       ↓
#   video_sub_embed_2.mp4
#
# =====================================

def make_output_path(
    mp4_path
):

    mp4_path = Path(
        mp4_path
    )

    stem = mp4_path.stem

    if stem.lower().endswith(
        "_sub_embed"
    ):

        output_stem = (
            stem +
            "_2"
        )

    else:

        output_stem = (
            stem +
            "_sub_embed"
        )

    return (
        mp4_path.parent /
        (
            output_stem +
            ".mp4"
        )
    )


# =====================================
# FFmpeg存在確認
# =====================================

def check_ffmpeg():

    log(
        "FFmpeg確認開始"
    )

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    if not ffmpeg_path:

        raise RuntimeError(
            "FFmpegが見つかりません。"
            "Render側でFFmpegをインストールしてください。"
        )

    log(
        f"FFmpeg path: {ffmpeg_path}"
    )

    try:

        result = subprocess.run(

            [
                ffmpeg_path,
                "-version"
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=30

        )

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpegが見つかりません。"
        )

    except subprocess.TimeoutExpired:

        raise RuntimeError(
            "FFmpegの確認がタイムアウトしました。"
        )

    except OSError as error:

        raise RuntimeError(
            f"FFmpegを起動できません: {error}"
        ) from error

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpegを実行できませんでした。"
        )

    first_line = (

        result.stdout.splitlines()[0]

        if result.stdout

        else "FFmpeg"

    )

    log(
        first_line
    )

    return ffmpeg_path


# =====================================
# SRT文字コード確認
#
# ファイル全体をメモリに読み込まない
# =====================================

def validate_srt_encoding(
    srt_path
):

    srt_path = Path(
        srt_path
    )

    try:

        with open(

            srt_path,

            "r",

            encoding="utf-8-sig"

        ) as file:

            first_content = file.read(
                4096
            )

    except UnicodeDecodeError as error:

        raise RuntimeError(

            "SRTファイルをUTF-8として"
            "読み込めませんでした。\n"
            "SRTをUTF-8形式で保存してください。"

        ) from error

    except OSError as error:

        raise RuntimeError(

            f"SRTファイルを読み込めませんでした: {error}"

        ) from error

    if not first_content.strip():

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    try:

        srt_size = (
            srt_path.stat().st_size
        )

    except OSError:

        srt_size = 0

    log(
        f"SRTサイズ: {srt_size} bytes"
    )

    return True


# =====================================
# 日本語フォント検索
#
# subtitle_font.pyで選択された
# フォントを優先する。
#
# 選択フォントが実際に存在しない場合は
# 自動検出へフォールバックする。
# =====================================

def find_japanese_font(
    requested_font=None
):

    log(
        "日本語フォント検索開始"
    )

    # =================================
    # 環境変数
    # =================================

    environment_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    if environment_font:

        environment_font_path = Path(
            environment_font
        )

        if environment_font_path.is_file():

            log(
                "環境変数指定フォント:"
            )

            log(
                str(
                    environment_font_path
                )
            )

            return {

                "path":
                    environment_font_path,

                "family":
                    get_font_family_from_path(
                        environment_font_path
                    )

            }

        log(
            "SUBTITLE_FONTに指定された"
            "フォントが存在しません:"
        )

        log(
            str(
                environment_font_path
            )
        )

    # =================================
    # 指定フォントをfc-match
    # =================================

    fc_match = shutil.which(
        "fc-match"
    )

    if fc_match and requested_font:

        try:

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

                encoding="utf-8",

                errors="replace",

                timeout=30

            )

            if result.returncode == 0:

                for line in result.stdout.splitlines():

                    line = line.strip()

                    if not line:

                        continue

                    font_path = Path(
                        line
                    )

                    if not font_path.is_file():

                        continue

                    log(
                        "選択されたフォントを検出:"
                    )

                    log(
                        f"family: {requested_font}"
                    )

                    log(
                        f"path: {font_path}"
                    )

                    return {

                        "path":
                            font_path,

                        "family":
                            requested_font

                    }

        except Exception as error:

            log(
                f"指定フォントfc-matchエラー: {error}"
            )

    # =================================
    # fc-matchによる日本語フォント検索
    # =================================

    if fc_match:

        candidates = [

            "Noto Sans CJK JP",

            "Noto Sans JP",

            "Noto Serif CJK JP",

            "Noto Serif JP",

            "IPAexGothic",

            "IPAGothic",

            "IPAexMincho",

            "IPAMincho",

            "VL Gothic",

            "TakaoGothic",

        ]

        for family in candidates:

            try:

                result = subprocess.run(

                    [
                        fc_match,

                        "-f",
                        "%{file}\\n",

                        family

                    ],

                    stdout=subprocess.PIPE,

                    stderr=subprocess.PIPE,

                    text=True,

                    encoding="utf-8",

                    errors="replace",

                    timeout=30

                )

            except Exception as error:

                log(
                    f"fc-matchエラー: {error}"
                )

                continue

            if result.returncode != 0:

                continue

            font_file = ""

            for line in result.stdout.splitlines():

                line = line.strip()

                if line:

                    font_file = line

                    break

            if not font_file:

                continue

            font_path = Path(
                font_file
            )

            if not font_path.is_file():

                continue

            log(
                "日本語フォント検出:"
            )

            log(
                f"family: {family}"
            )

            log(
                f"path: {font_path}"
            )

            return {

                "path":
                    font_path,

                "family":
                    family

            }

    # =================================
    # fc-list
    # =================================

    fc_list = shutil.which(
        "fc-list"
    )

    if fc_list:

        try:

            result = subprocess.run(

                [
                    fc_list,

                    ":lang=ja",

                    "-f",

                    "%{file}|%{family}\\n"

                ],

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                text=True,

                encoding="utf-8",

                errors="replace",

                timeout=30

            )

            if result.returncode == 0:

                for line in result.stdout.splitlines():

                    line = line.strip()

                    if not line:

                        continue

                    parts = line.split(
                        "|",
                        1
                    )

                    font_file = (
                        parts[0].strip()
                    )

                    family = (

                        parts[1].strip()

                        if len(parts) > 1

                        else ""

                    )

                    if not font_file:

                        continue

                    font_path = Path(
                        font_file
                    )

                    if not font_path.is_file():

                        continue

                    log(
                        "fc-list日本語フォント検出:"
                    )

                    log(
                        f"path: {font_path}"
                    )

                    log(
                        f"family: {family}"
                    )

                    return {

                        "path":
                            font_path,

                        "family":
                            family

                    }

        except Exception as error:

            log(
                f"fc-list検索エラー: {error}"
            )

    # =================================
    # 手動検索
    # =================================

    preferred_fonts = [

        "NotoSansCJK-Regular.ttc",

        "NotoSansCJKJP-Regular.otf",

        "NotoSansJP-Regular.ttf",

        "NotoSerifCJK-Regular.ttc",

        "NotoSerifCJKJP-Regular.otf",

        "NotoSerifJP-Regular.ttf",

        "ipaexg.ttf",

        "ipaexm.ttf",

        "IPAGothic.ttf",

        "IPAPGothic.ttf",

        "IPAMincho.ttf",

        "IPAPMincho.ttf",

        "TakaoGothic.ttf",

        "TakaoPGothic.ttf",

        "TakaoMincho.ttf",

        "VL-Gothic-Regular.ttf",

    ]

    font_directories = [

        Path(
            "/usr/share/fonts"
        ),

        Path(
            "/usr/local/share/fonts"
        ),

        Path(
            "/opt/render/project/src/fonts"
        ),

        Path(
            "/app/fonts"
        ),

        Path(
            "fonts"
        ),

    ]

    for directory in font_directories:

        if not directory.exists():

            continue

        for font_name in preferred_fonts:

            try:

                for match in directory.rglob(
                    font_name
                ):

                    if not match.is_file():

                        continue

                    log(
                        "日本語フォント検出:"
                    )

                    log(
                        str(
                            match
                        )
                    )

                    return {

                        "path":
                            match,

                        "family":
                            get_font_family_from_path(
                                match
                            )

                    }

            except Exception:

                continue

    # =================================
    # 見つからない
    # =================================

    log(
        "日本語フォントが見つかりませんでした。"
    )

    return None


# =====================================
# フォントファミリー取得
# =====================================

def get_font_family_from_path(
    font_path
):

    fc_scan = shutil.which(
        "fc-scan"
    )

    if not fc_scan:

        return None

    try:

        result = subprocess.run(

            [
                fc_scan,

                "--format=%{family}",

                str(font_path)

            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=30

        )

    except Exception:

        return None

    if result.returncode != 0:

        return None

    family = (
        result.stdout.strip()
    )

    if not family:

        return None

    if "," in family:

        family = family.split(
            ",",
            1
        )[0].strip()

    return family


# =====================================
# FFmpeg用パスエスケープ
# =====================================

def escape_ffmpeg_filter_path(
    file_path
):

    path = str(
        Path(file_path).resolve()
    )

    path = path.replace(
        "\\",
        "/"
    )

    path = path.replace(
        "'",
        "\\'"
    )

    path = path.replace(
        ":",
        "\\:"
    )

    return path


# =====================================
# FFmpeg字幕値エスケープ
# =====================================

def escape_ffmpeg_value(
    value
):

    value = str(
        value
    )

    value = value.replace(
        "\\",
        "\\\\"
    )

    value = value.replace(
        "'",
        "\\'"
    )

    value = value.replace(
        ":",
        "\\:"
    )

    value = value.replace(
        ",",
        "\\,"
    )

    return value


# =====================================
# 字幕フィルター作成
#
# subtitle_font.pyの設定:
#
#   font
#   text_color
#   outline_color
#   outline_width
#
# をFFmpeg ASS styleへ変換
# =====================================

def make_subtitle_filter(
    srt_path,
    font_info=None,
    subtitle_settings=None
):

    subtitle_path = (
        escape_ffmpeg_filter_path(
            srt_path
        )
    )

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )

    # =================================
    # 字幕設定
    # =================================

    if subtitle_settings is None:

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

    if not isinstance(
        subtitle_settings,
        dict
    ):

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

    # =================================
    # フォント
    # =================================

    selected_font = (
        subtitle_settings.get(
            "font"
        )
    )

    # =================================
    # 文字色
    # =================================

    text_color_name = (
        subtitle_settings.get(
            "text_color",
            "白"
        )
    )

    text_color_info = (
        SUBTITLE_COLORS.get(
            text_color_name,
            {}
        )
    )

    text_color = (
        text_color_info.get(
            "ass",
            "&H00FFFFFF"
        )
    )

    # =================================
    # 縁色
    # =================================

    outline_color_name = (
        subtitle_settings.get(
            "outline_color",
            "黒"
        )
    )

    outline_color_info = (
        SUBTITLE_COLORS.get(
            outline_color_name,
            {}
        )
    )

    outline_color = (
        outline_color_info.get(
            "ass",
            "&H00000000"
        )
    )

    # =================================
    # 縁太さ
    # =================================

    try:

        outline_width = int(
            subtitle_settings.get(
                "outline_width",
                2
            )
        )

    except (
        ValueError,
        TypeError
    ):

        outline_width = 2

    outline_width = max(
        0,
        min(
            outline_width,
            10
        )
    )

    # =================================
    # フォントディレクトリ
    # =================================

    if font_info:

        font_path = font_info.get(
            "path"
        )

        if font_path:

            font_directory = (
                Path(font_path).parent
            )

            font_directory_escaped = (
                escape_ffmpeg_filter_path(
                    font_directory
                )
            )

            video_filter += (
                ":fontsdir='"
                +
                font_directory_escaped
                +
                "'"
            )

            log(
                "字幕フォントディレクトリ:"
            )

            log(
                str(
                    font_directory
                )
            )

    # =================================
    # FontName
    #
    # subtitle_font.pyで選択したフォントを
    # 優先する。
    #
    # 実際に検出されたフォント名がある場合は
    # それをフォールバックとして使用する。
    # =================================

    font_name = selected_font

    if not font_name and font_info:

        font_name = font_info.get(
            "family"
        )

    if not font_name:

        font_name = "Noto Sans CJK JP"

    # =================================
    # ASS force_style
    # =================================

    style_parts = [

        "FontName="
        +
        escape_ffmpeg_value(
            font_name
        ),

        "PrimaryColour="
        +
        text_color,

        "OutlineColour="
        +
        outline_color,

        "Outline="
        +
        str(outline_width),

    ]

    force_style = ",".join(
        style_parts
    )

    video_filter += (
        ":force_style='"
        +
        force_style
        +
        "'"
    )

    # =================================
    # 設定ログ
    # =================================

    log(
        "字幕スタイル:"
    )

    log(
        f"FontName: {font_name}"
    )

    log(
        f"文字色: {text_color_name}"
    )

    log(
        f"文字色ASS: {text_color}"
    )

    log(
        f"縁色: {outline_color_name}"
    )

    log(
        f"縁色ASS: {outline_color}"
    )

    log(
        f"縁太さ: {outline_width}"
    )

    return video_filter


# =====================================
# FFmpegコマンド表示
# =====================================

def command_to_string(
    command
):

    return " ".join(

        str(item)

        for item in command

    )


# =====================================
# 字幕焼き込み
# =====================================

def embed_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    start_time = time.monotonic()

    # =================================
    # 入力確認
    # =================================

    mp4_path = validate_input_file(

        mp4_path,

        ".mp4"

    )

    srt_path = validate_input_file(

        srt_path,

        ".srt"

    )

    # =================================
    # SRT確認
    # =================================

    validate_srt_encoding(
        srt_path
    )

    # =================================
    # 字幕設定
    # =================================

    if subtitle_settings is None:

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

    if not isinstance(
        subtitle_settings,
        dict
    ):

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

    log(
        "字幕設定:"
    )

    log(
        str(
            subtitle_settings
        )
    )

    # =================================
    # 出力先
    # =================================

    if output_path:

        output_path = Path(
            output_path
        )

    else:

        output_path = make_output_path(
            mp4_path
        )

    # =================================
    # 絶対パス化
    # =================================

    output_path = Path(
        output_path
    ).resolve()

    # =================================
    # 入力と出力が同じにならないようにする
    # =================================

    try:

        if (
            output_path.resolve()
            ==
            mp4_path.resolve()
        ):

            output_path = make_output_path(
                mp4_path
            )

    except Exception:

        pass

    # =================================
    # 出力フォルダ
    # =================================

    output_path.parent.mkdir(

        parents=True,

        exist_ok=True

    )

    # =================================
    # 既存出力削除
    # =================================

    if output_path.exists():

        log(
            f"既存出力ファイルを削除: "
            f"{output_path}"
        )

        try:

            output_path.unlink()

        except OSError as error:

            raise RuntimeError(

                "既存の出力ファイルを"
                "削除できませんでした: "
                +
                str(error)

            ) from error

    # =================================
    # FFmpeg確認
    # =================================

    ffmpeg_path = check_ffmpeg()

    # =================================
    # 選択フォント
    # =================================

    requested_font = (
        subtitle_settings.get(
            "font"
        )
    )

    log(
        "選択フォント:"
    )

    log(
        str(
            requested_font
        )
    )

    # =================================
    # 日本語フォント検索
    # =================================

    font_info = find_japanese_font(
        requested_font
    )

    if font_info:

        log(
            "日本語字幕フォント:"
        )

        log(
            str(
                font_info.get("path")
            )
        )

        log(
            "検出フォント名:"
        )

        log(
            str(
                font_info.get("family")
            )
        )

    else:

        log(
            "WARNING: 日本語フォントが"
            "検出できませんでした。"
        )

        log(
            "WARNING: Render環境に"
            "日本語フォントをインストールしてください。"
        )

    # =================================
    # フィルター
    # =================================

    video_filter = make_subtitle_filter(

        srt_path,

        font_info,

        subtitle_settings

    )

    # =================================
    # 入力サイズ
    # =================================

    try:

        input_mp4_size = (
            mp4_path.stat().st_size
        )

    except OSError:

        input_mp4_size = 0

    log(
        "====================================="
    )

    log(
        "字幕焼き込み開始"
    )

    log(
        f"MP4: {mp4_path}"
    )

    log(
        f"SRT: {srt_path}"
    )

    log(
        f"出力: {output_path}"
    )

    log(
        f"入力MP4サイズ: "
        f"{input_mp4_size} bytes"
    )

    log(
        f"FFmpeg threads: "
        f"{FFMPEG_THREADS}"
    )

    log(
        f"FFmpeg preset: "
        f"{FFMPEG_PRESET}"
    )

    log(
        f"FFmpeg CRF: "
        f"{FFMPEG_CRF}"
    )

    # =================================
    # FFmpegコマンド
    # =================================

    command = [

        ffmpeg_path,

        "-y",

        "-nostdin",

        # ---------------------------------
        # 入力
        # ---------------------------------

        "-i",
        str(mp4_path),

        # ---------------------------------
        # 字幕
        # ---------------------------------

        "-vf",
        video_filter,

        # ---------------------------------
        # Video
        # ---------------------------------

        "-c:v",
        "libx264",

        # ---------------------------------
        # 512MB対策
        # ---------------------------------

        "-threads",
        FFMPEG_THREADS,

        # ---------------------------------
        # 高速・低メモリ
        # ---------------------------------

        "-preset",
        FFMPEG_PRESET,

        # ---------------------------------
        # 画質
        # ---------------------------------

        "-crf",
        FFMPEG_CRF,

        # ---------------------------------
        # Audioは再エンコードしない
        # ---------------------------------

        "-c:a",
        "copy",

        # ---------------------------------
        # MP4
        # ---------------------------------

        "-movflags",
        "+faststart",

        # ---------------------------------
        # 出力
        # ---------------------------------

        str(output_path)

    ]

    # =================================
    # コマンドログ
    # =================================

    log(
        "FFmpeg video filter:"
    )

    log(
        video_filter
    )

    log(
        "FFmpeg command:"
    )

    log(
        command_to_string(
            command
        )
    )

    # =================================
    # FFmpeg実行
    # =================================

    try:

        process = subprocess.Popen(

            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            bufsize=1

        )

    except OSError as error:

        raise RuntimeError(

            "FFmpeg実行中にエラーが発生しました: "
            +
            str(error)

        ) from error

    # =================================
    # 最後の100行だけ保存
    # =================================

    ffmpeg_output_lines = deque(

        maxlen=MAX_FFMPEG_LOG_LINES

    )

    # =================================
    # FFmpegログ取得
    # =================================

    try:

        if process.stderr:

            for line in process.stderr:

                line = line.rstrip()

                if not line:

                    continue

                ffmpeg_output_lines.append(
                    line
                )

                print(
                    "[FFMPEG]",
                    line,
                    flush=True
                )

    except Exception as error:

        try:

            process.kill()

        except Exception:

            pass

        try:

            process.wait()

        except Exception:

            pass

        raise RuntimeError(

            "FFmpegログ取得中にエラーが発生しました: "
            +
            str(error)

        ) from error

    finally:

        if process.stderr:

            try:

                process.stderr.close()

            except Exception:

                pass

    # =================================
    # 終了
    # =================================

    return_code = process.wait()

    # =================================
    # 処理時間
    # =================================

    elapsed_time = (

        time.monotonic()
        -
        start_time

    )

    # =================================
    # FFmpegエラー
    # =================================

    if return_code != 0:

        log(
            f"FFmpegエラー: "
            f"return code={return_code}"
        )

        if ffmpeg_output_lines:

            error_detail = "\n".join(
                ffmpeg_output_lines
            )

        else:

            error_detail = (
                "FFmpegからエラー内容が"
                "返されませんでした。"
            )

        if output_path.exists():

            try:

                output_path.unlink()

            except Exception:

                pass

        raise RuntimeError(

            "字幕焼き込みに失敗しました。"
            "\n\n"
            +
            error_detail
            +
            "\n\n"
            +
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            )

        )

    # =================================
    # 出力確認
    # =================================

    if not output_path.exists():

        raise RuntimeError(

            "FFmpegは正常終了しましたが、"
            "出力ファイルが作成されていません。"

        )

    # =================================
    # サイズ確認
    # =================================

    try:

        output_size = (
            output_path.stat().st_size
        )

    except OSError as error:

        raise RuntimeError(

            f"出力ファイルを確認できませんでした: "
            f"{error}"

        ) from error

    if output_size <= 0:

        raise RuntimeError(
            "出力ファイルのサイズが0です。"
        )

    # =================================
    # 完了
    # =================================

    log(
        "字幕焼き込み完了"
    )

    log(
        f"出力ファイル: "
        f"{output_path}"
    )

    log(
        f"サイズ: "
        f"{output_size} bytes"
    )

    log(
        "処理時間: "
        +
        format_elapsed_time(
            elapsed_time
        )
    )

    log(
        "====================================="
    )

    return output_path


# =====================================
# 外部向け正式関数
#
# subtitle_routes.py から使用
#
# =====================================

def create_subtitle_mp4(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    return embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )


# =====================================
# 互換用別名
# =====================================

def create_burned_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    return embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )


def burn_subtitles(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    return embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )


# =====================================
# 処理時間表示
# =====================================

def format_elapsed_time(
    seconds
):

    seconds = int(
        round(seconds)
    )

    hours = (
        seconds // 3600
    )

    minutes = (
        seconds % 3600
    ) // 60

    secs = (
        seconds % 60
    )

    return (

        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"

    )


# =====================================
# downloads内から実行
#
# コマンドライン実行時は
# subtitle_font.pyの標準設定を使用。
# =====================================

def embed_from_downloads(
    mp4_filename,
    srt_filename,
    subtitle_settings=None
):

    mp4_filename = Path(
        mp4_filename
    ).name

    srt_filename = Path(
        srt_filename
    ).name

    DOWNLOADS_DIR.mkdir(

        parents=True,

        exist_ok=True

    )

    mp4_path = (
        DOWNLOADS_DIR /
        mp4_filename
    )

    srt_path = (
        DOWNLOADS_DIR /
        srt_filename
    )

    log(
        f"DOWNLOAD_DIR: "
        f"{DOWNLOADS_DIR}"
    )

    log(
        f"downloads MP4: "
        f"{mp4_path}"
    )

    log(
        f"downloads SRT: "
        f"{srt_path}"
    )

    return embed_subtitle(

        mp4_path,

        srt_path,

        subtitle_settings=subtitle_settings

    )


# =====================================
# コマンドライン
# =====================================

def main():

    if len(sys.argv) < 3:

        print()

        print(
            "使用方法:"
        )

        print(
            "python subtitle.py "
            "動画.mp4 字幕.srt"
        )

        print()

        return 1

    mp4_filename = (
        sys.argv[1]
    )

    srt_filename = (
        sys.argv[2]
    )

    start_time = time.monotonic()

    try:

        # ---------------------------------
        # コマンドラインでは
        # subtitle_font.pyの標準設定を使用
        # ---------------------------------

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

        output_path = (
            embed_from_downloads(

                mp4_filename,

                srt_filename,

                subtitle_settings

            )
        )

        elapsed_time = (

            time.monotonic()
            -
            start_time

        )

        print()

        print(
            "====================================="
        )

        print(
            "字幕焼き込み成功"
        )

        print(
            "====================================="
        )

        print(
            f"入力MP4: "
            f"{mp4_filename}"
        )

        print(
            f"入力SRT: "
            f"{srt_filename}"
        )

        print(
            f"プリセット: "
            f"{subtitle_settings.get('preset')}"
        )

        print(
            f"フォント: "
            f"{subtitle_settings.get('font')}"
        )

        print(
            f"文字色: "
            f"{subtitle_settings.get('text_color')}"
        )

        print(
            f"縁色: "
            f"{subtitle_settings.get('outline_color')}"
        )

        print(
            f"縁太さ: "
            f"{subtitle_settings.get('outline_width')}"
        )

        print(
            f"出力: "
            f"{output_path.name}"
        )

        print(
            f"出力パス: "
            f"{output_path}"
        )

        print(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        print(
            "====================================="
        )

        print()

        return 0

    except Exception as error:

        elapsed_time = (

            time.monotonic()
            -
            start_time

        )

        print()

        print(
            "====================================="
        )

        print(
            "字幕焼き込み失敗"
        )

        print(
            "====================================="
        )

        print(
            str(error),
            file=sys.stderr
        )

        print(

            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            ),

            file=sys.stderr

        )

        print(
            "====================================="
        )

        print()

        return 1


# =====================================
# 実行
# =====================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
