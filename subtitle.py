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
#   config.py の DOWNLOAD_DIR/xxx_sub_embed.mp4
#
# FFmpegを使用
#
# 重要:
#   - 1080pを維持
#   - 日本語字幕対応
#   - 動画は再エンコード
#   - audioはcopy
#   - FFmpegを1スレッドに制限
#   - ultrafastでメモリ負荷を抑制
#   - FFmpegログを最大100行だけ保持
#   - downloadsの場所はconfig.pyで管理
# =====================================

import os
import sys
import time
import shutil
import subprocess

from pathlib import Path
from collections import deque

from config import DOWNLOAD_DIR


# =====================================
# 設定
# =====================================

DOWNLOADS_DIR = Path(
    DOWNLOAD_DIR
)

# FFmpegログを保持する最大行数
MAX_FFMPEG_LOG_LINES = 100

# 512MB環境では1スレッドを推奨
FFMPEG_THREADS = "1"

# メモリ負荷を最小化
FFMPEG_PRESET = "ultrafast"

# 画質
#
# 18 = 高画質
# 20 = 高画質
# 23 = 標準的
#
# 512MB環境では23を推奨
FFMPEG_CRF = "23"


# =====================================
# ログ
# =====================================

def log(
    message
):

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

    if path.suffix.lower() != extension:

        raise ValueError(
            f"{extension} ファイルではありません: {path}"
        )

    return path


# =====================================
# 出力ファイル名
# =====================================

def make_output_path(
    mp4_path
):

    mp4_path = Path(
        mp4_path
    )

    stem = mp4_path.stem

    # =================================
    # すでに字幕付きMP4の場合
    # =================================

    if stem.lower().endswith(
        "_sub_embed"
    ):

        output_stem = stem

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
# 512MB対策:
# ファイル全体をread()しない
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

            # ---------------------------------
            # 先頭だけ確認
            #
            # SRT全体をメモリに読み込まない
            # ---------------------------------

            first_content = file.read(
                4096
            )

    except UnicodeDecodeError:

        raise RuntimeError(
            "SRTファイルをUTF-8として"
            "読み込めませんでした。\n"
            "SRTをUTF-8形式で保存してください。"
        )

    except OSError as error:

        raise RuntimeError(
            f"SRTファイルを読み込めませんでした: {error}"
        )

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
# フォント検索
# =====================================

def find_japanese_font():

    log(
        "日本語フォント検索開始"
    )

    # ---------------------------------
    # 環境変数
    # ---------------------------------

    environment_font = os.environ.get(
        "SUBTITLE_FONT"
    )

    if environment_font:

        environment_font_path = Path(
            environment_font
        )

        if environment_font_path.exists():

            log(
                f"環境変数指定フォント: "
                f"{environment_font_path}"
            )

            return environment_font_path


    # ---------------------------------
    # 優先フォント
    # ---------------------------------

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


    # ---------------------------------
    # 検索ディレクトリ
    # ---------------------------------

    font_directories = [

        Path(
            "/usr/share/fonts"
        ),

        Path(
            "/usr/local/share/fonts"
        ),

        Path(
            "/usr/share/fonts/truetype"
        ),

        Path(
            "/usr/share/fonts/opentype"
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


    # ---------------------------------
    # 優先フォント検索
    # ---------------------------------

    for directory in font_directories:

        if not directory.exists():

            continue

        for font_name in preferred_fonts:

            try:

                for match in directory.rglob(
                    font_name
                ):

                    if match.is_file():

                        log(
                            f"日本語フォント検出: "
                            f"{match}"
                        )

                        return match

            except Exception:

                continue


    # ---------------------------------
    # fc-list
    # ---------------------------------

    fc_list = shutil.which(
        "fc-list"
    )

    if fc_list:

        try:

            result = subprocess.run(

                [
                    fc_list,
                    ":lang=ja",
                    "file",
                ],

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                text=True,

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

                    if font_path.exists():

                        log(
                            f"fc-list日本語フォント検出: "
                            f"{font_path}"
                        )

                        return font_path

        except Exception as error:

            log(
                f"fc-list検索エラー: {error}"
            )


    # ---------------------------------
    # 見つからない
    # ---------------------------------

    log(
        "日本語フォントが見つかりませんでした。"
    )

    return None


# =====================================
# FFmpeg用パスエスケープ
# =====================================

def escape_ffmpeg_filter_path(
    file_path
):

    path = str(
        Path(file_path).resolve()
    )

    # Linux
    path = path.replace(
        "\\",
        "/"
    )

    # シングルクォート
    path = path.replace(
        "'",
        "\\'"
    )

    # Windows等のコロン対策
    path = path.replace(
        ":",
        "\\:"
    )

    return path


# =====================================
# 字幕フィルター作成
# =====================================

def make_subtitle_filter(
    srt_path,
    font_path=None
):

    subtitle_path = (
        escape_ffmpeg_filter_path(
            srt_path
        )
    )

    # ---------------------------------
    # 基本
    # ---------------------------------

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )


    # ---------------------------------
    # 日本語フォント
    # ---------------------------------

    if font_path:

        font_directory = (
            Path(font_path).parent
        )

        font_directory_escaped = (
            escape_ffmpeg_filter_path(
                font_directory
            )
        )

        video_filter = (
            "subtitles='"
            +
            subtitle_path
            +
            "':"
            +
            "fontsdir='"
            +
            font_directory_escaped
            +
            "'"
        )

        log(
            f"字幕フォントディレクトリ: "
            f"{font_directory}"
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
    output_path=None
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

        except Exception as error:

            raise RuntimeError(

                "既存の出力ファイルを"
                "削除できませんでした: "
                +
                str(error)

            )


    # =================================
    # FFmpeg確認
    # =================================

    ffmpeg_path = check_ffmpeg()


    # =================================
    # 日本語フォント検索
    # =================================

    font_path = find_japanese_font()


    # =================================
    # フィルター
    # =================================

    video_filter = make_subtitle_filter(

        srt_path,

        font_path

    )


    # =================================
    # 入力サイズ
    # =================================

    try:

        input_mp4_size = (
            mp4_path.stat().st_size
        )

    except Exception:

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
    #
    # 512MB対策
    #
    # -threads 1
    #   メモリピークを抑える
    #
    # -preset ultrafast
    #   エンコード負荷を抑える
    #
    # -c:a copy
    #   音声を再エンコードしない
    # =================================

    command = [

        ffmpeg_path,

        # 既存ファイル上書き
        "-y",

        # stdinを使わない
        "-nostdin",

        # 入力
        "-i",
        str(mp4_path),

        # 字幕
        "-vf",
        video_filter,

        # Video
        "-c:v",
        "libx264",

        # 512MB対策
        "-threads",
        FFMPEG_THREADS,

        # 低メモリ・高速
        "-preset",
        FFMPEG_PRESET,

        # 画質
        "-crf",
        FFMPEG_CRF,

        # Audioはコピー
        "-c:a",
        "copy",

        # MP4
        "-movflags",
        "+faststart",

        # 出力
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

    except Exception as error:

        raise RuntimeError(

            "FFmpeg実行中にエラーが発生しました: "
            +
            str(error)

        )


    # =================================
    # 最後の100行だけ保存
    #
    # 重要:
    # FFmpegログ全体をメモリに保持しない
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

        )


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

            error_detail = (

                "\n".join(
                    ffmpeg_output_lines
                )

            )

        else:

            error_detail = (

                "FFmpegからエラー内容が"
                "返されませんでした。"

            )

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

        )


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
# config.py の DOWNLOAD_DIR を使用
# =====================================

def embed_from_downloads(
    mp4_filename,
    srt_filename
):

    # ---------------------------------
    # ファイル名だけにする
    # ---------------------------------

    mp4_filename = Path(
        mp4_filename
    ).name

    srt_filename = Path(
        srt_filename
    ).name


    # ---------------------------------
    # downloadsディレクトリ確認
    # ---------------------------------

    DOWNLOADS_DIR.mkdir(

        parents=True,

        exist_ok=True

    )


    # ---------------------------------
    # パス
    # ---------------------------------

    mp4_path = (

        DOWNLOADS_DIR /

        mp4_filename

    )

    srt_path = (

        DOWNLOADS_DIR /

        srt_filename

    )


    # ---------------------------------
    # ログ
    # ---------------------------------

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


    # ---------------------------------
    # 実行
    # ---------------------------------

    return embed_subtitle(

        mp4_path,

        srt_path

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

        output_path = (

            embed_from_downloads(

                mp4_filename,

                srt_filename

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
