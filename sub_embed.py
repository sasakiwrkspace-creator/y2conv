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

import sys
import time
import subprocess
from pathlib import Path


# =====================================
# 設定
# =====================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

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

            encoding="utf-8",

            errors="replace",

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

    except Exception as error:

        raise RuntimeError(
            "FFmpeg確認中にエラーが発生しました: "
            +
            str(error)
        )

    if result.returncode != 0:

        error_detail = (
            result.stderr
            if result.stderr
            else
            "FFmpegからエラー内容が返されませんでした。"
        )

        raise RuntimeError(
            "FFmpegを実行できませんでした。\n"
            +
            error_detail
        )

    first_line = (
        result.stdout.splitlines()[0]
        if result.stdout
        else
        "FFmpeg"
    )

    log(
        first_line
    )

    return True


# =====================================
# SRT文字コード確認
#
# UTF-8 / UTF-8 BOMを許可
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
# SRT内容確認
# =====================================

def validate_srt_content(
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

            content = file.read()

    except Exception as error:

        raise RuntimeError(
            "SRTファイルの読み込みに失敗しました: "
            +
            str(error)
        )

    if not content.strip():

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    log(
        f"SRT文字数: {len(content)}"
    )


# =====================================
# FFmpeg subtitles filter用パス
# =====================================

def make_ffmpeg_subtitle_path(
    srt_path
):

    srt_path = (
        Path(srt_path)
        .resolve()
    )

    subtitle_path = str(
        srt_path
    )

    # ---------------------------------
    # Linux / Windows両対応
    # ---------------------------------

    subtitle_path = (
        subtitle_path
        .replace(
            "\\",
            "/"
        )
    )

    # ---------------------------------
    # FFmpeg filter parser用
    # ---------------------------------

    subtitle_path = (
        subtitle_path
        .replace(
            "'",
            "\\'"
        )
    )

    subtitle_path = (
        subtitle_path
        .replace(
            ":",
            "\\:"
        )
    )

    return subtitle_path


# =====================================
# FFmpegコマンド表示
#
# subprocess.runへ渡す実際の引数を
# 1個ずつ確認できるようにする
# =====================================

def log_ffmpeg_command(
    command
):

    log(
        "FFmpeg command arguments:"
    )

    for index, argument in enumerate(
        command
    ):

        log(
            f"  [{index}] {argument}"
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

    start_time = (
        time.monotonic()
    )

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
    # 絶対パス化
    # =================================

    mp4_path = (
        mp4_path
        .resolve()
    )

    srt_path = (
        srt_path
        .resolve()
    )

    # =================================
    # SRT確認
    # =================================

    validate_srt_encoding(
        srt_path
    )

    validate_srt_content(
        srt_path
    )

    # =================================
    # 出力先
    # =================================

    if output_path:

        output_path = (
            Path(output_path)
            .resolve()
        )

    else:

        output_path = (
            make_output_path(
                mp4_path
            )
            .resolve()
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
    # ファイル情報ログ
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
    # サイズ確認
    # =================================

    mp4_size = (
        mp4_path
        .stat()
        .st_size
    )

    srt_size = (
        srt_path
        .stat()
        .st_size
    )

    log(
        f"入力MP4サイズ: {mp4_size} bytes"
    )

    log(
        f"入力SRTサイズ: {srt_size} bytes"
    )

    # =================================
    # FFmpeg字幕パス
    # =================================

    subtitle_path = (
        make_ffmpeg_subtitle_path(
            srt_path
        )
    )

    # =================================
    # Video Filter
    # =================================

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )

    # =================================
    # FFmpegコマンド
    # =================================

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

    # =================================
    # 実行ログ
    # =================================

    log(
        "FFmpeg実行"
    )

    log(
        "FFmpeg video filter:"
    )

    log(
        video_filter
    )

    log_ffmpeg_command(
        command
    )

    # =================================
    # FFmpeg実行
    #
    # stderrをリアルタイムで取得する。
    #
    # FFmpegは通常、処理情報をstderrへ
    # 出力するため、ここを監視する。
    # =================================

    process = None

    stderr_lines = []

    stdout_lines = []

    try:

        process = subprocess.Popen(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace",

            bufsize=1

        )

        log(
            "FFmpegプロセス開始"
        )

        # ---------------------------------
        # stderrをリアルタイム取得
        # ---------------------------------

        if process.stderr:

            for line in process.stderr:

                line = (
                    line.rstrip()
                )

                if line:

                    stderr_lines.append(
                        line
                    )

                    print(
                        "[FFMPEG]",
                        line,
                        flush=True
                    )

        # ---------------------------------
        # stdout取得
        # ---------------------------------

        if process.stdout:

            for line in process.stdout:

                line = (
                    line.rstrip()
                )

                if line:

                    stdout_lines.append(
                        line
                    )

                    print(
                        "[FFMPEG-OUT]",
                        line,
                        flush=True
                    )

        # ---------------------------------
        # FFmpeg終了待ち
        # ---------------------------------

        return_code = (
            process.wait()
        )

    except Exception as error:

        if process is not None:

            try:

                process.kill()

            except Exception:

                pass

        raise RuntimeError(
            "FFmpeg実行中にエラーが発生しました: "
            +
            str(error)
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
    # 終了情報
    # =================================

    log(
        "FFmpegプロセス終了"
    )

    log(
        f"FFmpeg return code: {return_code}"
    )

    # =================================
    # stderr最終確認
    # =================================

    if stderr_lines:

        log(
            f"FFmpeg stderr lines: {len(stderr_lines)}"
        )

    else:

        log(
            "FFmpeg stderr: なし"
        )

    # =================================
    # stdout最終確認
    # =================================

    if stdout_lines:

        log(
            f"FFmpeg stdout lines: {len(stdout_lines)}"
        )

    else:

        log(
            "FFmpeg stdout: なし"
        )

    # =================================
    # FFmpegエラー
    # =================================

    if return_code != 0:

        log(
            "FFmpegエラー"
        )

        if stderr_lines:

            error_detail = (
                "\n"
                .join(
                    stderr_lines[-100:]
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
    # 出力サイズ
    # =================================

    output_size = (
        output_path
        .stat()
        .st_size
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

    # ---------------------------------
    # ファイル名だけ取得
    # ---------------------------------

    mp4_filename = (
        Path(
            mp4_filename
        )
        .name
    )

    srt_filename = (
        Path(
            srt_filename
        )
        .name
    )

    # ---------------------------------
    # downloadsパス
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
        f"downloads MP4: {mp4_path}"
    )

    log(
        f"downloads SRT: {srt_path}"
    )

    # ---------------------------------
    # 存在確認
    # ---------------------------------

    if not mp4_path.exists():

        raise FileNotFoundError(
            "downloadsにMP4がありません: "
            +
            str(mp4_path)
        )

    if not srt_path.exists():

        raise FileNotFoundError(
            "downloadsにSRTがありません: "
            +
            str(srt_path)
        )

    # ---------------------------------
    # 字幕焼き込み
    # ---------------------------------

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

    start_time = (
        time.monotonic()
    )

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
            file=sys.stderr,
            flush=True
        )

        print(
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            ),
            file=sys.stderr,
            flush=True
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
