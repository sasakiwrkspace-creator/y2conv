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
import subprocess
from pathlib import Path


# =====================================
# 設定
# =====================================

BASE_DIR = Path(__file__).resolve().parent

DOWNLOADS_DIR = BASE_DIR / "downloads"


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

    path = Path(file_path)


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

    mp4_path = Path(mp4_path)


    # ---------------------------------
    # すでに _sub_embed が付いている場合
    # ---------------------------------

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
# SRTパスをFFmpeg用に変換
#
# Windowsなどで日本語ファイル名を
# 使用する場合のための処理
# =====================================

def escape_subtitle_path(
    srt_path
):

    path = str(
        Path(srt_path).resolve()
    )


    # FFmpeg filter用
    #
    # Windows:
    # C:\xxx\test.srt
    #
    # ↓
    # C\:/xxx/test.srt
    #

    path = path.replace(
        "\\",
        "/"
    )


    path = path.replace(
        ":",
        "\\:"
    )


    path = path.replace(
        "'",
        "\\'"
    )


    return path


# =====================================
# FFmpeg存在確認
# =====================================

def check_ffmpeg():

    try:

        result = subprocess.run(
            [
                "ffmpeg",
                "-version"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpegが見つかりません。"
            "FFmpegをインストールしてPATHを設定してください。"
        )


    if result.returncode != 0:

        raise RuntimeError(
            "FFmpegを実行できませんでした。"
        )


    return True


# =====================================
# 字幕焼き込み
# =====================================

def embed_subtitle(
    mp4_path,
    srt_path,
    output_path=None
):

    # ---------------------------------
    # 入力確認
    # ---------------------------------

    mp4_path =
        validate_input_file(
            mp4_path,
            ".mp4"
        )

    srt_path =
        validate_input_file(
            srt_path,
            ".srt"
        )


    # ---------------------------------
    # 出力先
    # ---------------------------------

    if output_path:

        output_path = Path(
            output_path
        )

    else:

        output_path =
            make_output_path(
                mp4_path
            )


    # ---------------------------------
    # downloads作成
    # ---------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # ---------------------------------
    # FFmpeg確認
    # ---------------------------------

    check_ffmpeg()


    # ---------------------------------
    # SRTパス
    # ---------------------------------

    subtitle_path =
        escape_subtitle_path(
            srt_path
        )


    # ---------------------------------
    # FFmpegコマンド
    #
    # 字幕を映像へ焼き込むため、
    # video filter の subtitles を使用
    #
    # 音声はそのままコピー
    # ---------------------------------

    command = [

        "ffmpeg",

        "-y",

        "-i",
        str(mp4_path),

        "-vf",
        (
            "subtitles="
            + subtitle_path
        ),

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


    # ---------------------------------
    # FFmpeg実行
    # ---------------------------------

    try:

        result =
            subprocess.run(
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


    # ---------------------------------
    # エラー
    # ---------------------------------

    if result.returncode != 0:

        log(
            "FFmpegエラー"
        )

        print(
            result.stderr,
            file=sys.stderr
        )


        raise RuntimeError(
            "字幕焼き込みに失敗しました。"
            "\n"
            +
            result.stderr[-3000:]
        )


    # ---------------------------------
    # 出力確認
    # ---------------------------------

    if not output_path.exists():

        raise RuntimeError(
            "FFmpegは終了しましたが、"
            "出力ファイルが作成されていません。"
        )


    if output_path.stat().st_size <= 0:

        raise RuntimeError(
            "出力ファイルのサイズが0です。"
        )


    log(
        "字幕焼き込み完了"
    )

    log(
        f"出力ファイル: {output_path}"
    )

    log(
        f"サイズ: {output_path.stat().st_size} bytes"
    )


    return output_path


# =====================================
# downloads内のファイルを指定して実行
# =====================================

def embed_from_downloads(
    mp4_filename,
    srt_filename
):

    mp4_path =
        DOWNLOADS_DIR /
        Path(mp4_filename).name


    srt_path =
        DOWNLOADS_DIR /
        Path(srt_filename).name


    return embed_subtitle(
        mp4_path,
        srt_path
    )


# =====================================
# コマンドライン実行
#
# 例:
#
# python sub_embed.py test.mp4 test.srt
#
# =====================================

def main():

    if len(sys.argv) < 3:

        print(
            ""
        )

        print(
            "使用方法:"
        )

        print(
            "python sub_embed.py "
            "動画.mp4 字幕.srt"
        )

        print(
            ""
        )

        print(
            "例:"
        )

        print(
            "python sub_embed.py "
            "test.mp4 test.srt"
        )

        print(
            ""
        )

        print(
            "入力ファイルは downloads/ "
            "に置いてください。"
        )

        return 1


    mp4_filename =
        sys.argv[1]


    srt_filename =
        sys.argv[2]


    try:

        output_path =
            embed_from_downloads(
                mp4_filename,
                srt_filename
            )


        print(
            ""
        )

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
            "====================================="
        )

        print(
            ""
        )


        return 0


    except Exception as error:

        print(
            ""
        )

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
            "====================================="
        )

        print(
            ""
        )


        return 1


# =====================================
# 実行
# =====================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
