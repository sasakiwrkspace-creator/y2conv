# =====================================
# Subtitle Embed
# sub_embed.py
#
# MP4動画へSRT字幕を焼き込む
#
# 入力:
#   downloads/xxx.mp4
#   downloads/xxx.srt
#
# 出力:
#   downloads/xxx_sub_embed.mp4
#
# FFmpegを使用
# =====================================

import os
import sys
import time
import subprocess
from pathlib import Path


# =====================================
# 設定
# =====================================

BASE_DIR = Path(
    __file__
).resolve().parent


DOWNLOADS_DIR = (
    BASE_DIR /
    "downloads"
)


# =====================================
# ログ
# =====================================

def log(message):

    print(
        "[SUB EMBED]",
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


    try:

        result = subprocess.run(

            [
                "ffmpeg",
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
            "Render側でFFmpegをインストールしてください。"
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


    return True


# =====================================
# 字幕ファイルの文字コード確認
#
# SRTは基本UTF-8を想定
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

            file.read()


    except UnicodeDecodeError:

        raise RuntimeError(
            "SRTファイルをUTF-8として読み込めませんでした。"
            "\n"
            "SRTをUTF-8形式で保存してください。"
        )


# =====================================
# 字幕焼き込み
# =====================================

def embed_subtitle(
    mp4_path,
    srt_path,
    output_path=None
):

    # =================================
    # 開始時刻
    # =================================

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
    # FFmpeg確認
    # =================================

    check_ffmpeg()


    # =================================
    # ログ
    # =================================

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


    # =================================
    # FFmpegコマンド
    #
    # filter_complexではなく
    # subtitles=filename の形を使用
    #
    # filename部分をシングルクォートで
    # 囲んでFFmpegのfilter parserへ渡す
    # =================================

    subtitle_path = (
        str(
            srt_path.resolve()
        )
        .replace(
            "\\",
            "/"
        )
        .replace(
            "'",
            "\\'"
        )
        .replace(
            ":",
            "\\:"
        )
    )


    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )


    command = [

        "ffmpeg",

        "-y",

        "-i",
        str(mp4_path),

        "-vf",
        video_filter,

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-c:a",
        "copy",

        str(output_path)

    ]


    log(
        "FFmpeg実行"
    )


    # =================================
    # コマンド確認
    # =================================

    log(
        "FFmpeg video filter:"
    )

    log(
        video_filter
    )


    # =================================
    # FFmpeg実行
    # =================================

    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True

        )

    except Exception as error:

        raise RuntimeError(
            "FFmpeg実行中にエラーが発生しました: "
            + str(error)
        )


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

    if result.returncode != 0:

        log(
            "FFmpegエラー"
        )


        if result.stderr:

            print(
                result.stderr,
                file=sys.stderr,
                flush=True
            )


        error_detail = (
            result.stderr[-5000:]
            if result.stderr
            else
            "FFmpegからエラー内容が返されませんでした。"
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

            "FFmpegは終了しましたが、"
            "出力ファイルが作成されていません。"

        )


    # =================================
    # サイズ確認
    # =================================

    output_size = (
        output_path.stat().st_size
    )


    if output_size <= 0:

        raise RuntimeError(
            "出力ファイルのサイズが0です。"
        )


    # =================================
    # 完了ログ
    # =================================

    log(
        "字幕焼き込み完了"
    )


    log(
        f"出力ファイル: {output_path}"
    )


    log(
        f"サイズ: {output_size} bytes"
    )


    log(
        "処理時間: "
        +
        format_elapsed_time(
            elapsed_time
        )
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
# downloads内のファイルを指定して実行
# =====================================

def embed_from_downloads(
    mp4_filename,
    srt_filename
):

    mp4_filename = Path(
        mp4_filename
    ).name


    srt_filename = Path(
        srt_filename
    ).name


    mp4_path = (
        DOWNLOADS_DIR /
        mp4_filename
    )


    srt_path = (
        DOWNLOADS_DIR /
        srt_filename
    )


    log(
        f"downloads MP4: {mp4_path}"
    )


    log(
        f"downloads SRT: {srt_path}"
    )


    return embed_subtitle(
        mp4_path,
        srt_path
    )


# =====================================
# コマンドライン実行
# =====================================

def main():

    if len(sys.argv) < 3:

        print()

        print(
            "使用方法:"
        )

        print(
            "python sub_embed.py "
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
            f"入力MP4: {mp4_filename}"
        )

        print(
            f"入力SRT: {srt_filename}"
        )

        print(
            f"出力: {output_path.name}"
        )

        print(
            f"出力パス: {output_path}"
        )

        print(
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            )
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
