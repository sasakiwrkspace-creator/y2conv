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


    # ---------------------------------
    # 存在確認
    # ---------------------------------

    if not path.exists():

        raise FileNotFoundError(
            f"ファイルがありません: {path}"
        )


    # ---------------------------------
    # ファイル確認
    # ---------------------------------

    if not path.is_file():

        raise ValueError(
            f"ファイルではありません: {path}"
        )


    # ---------------------------------
    # 拡張子確認
    # ---------------------------------

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


    # ---------------------------------
    # すでに _sub_embed の場合
    # ---------------------------------

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
# subtitles filter用
#
# Linux:
#   /opt/render/project/src/downloads/test.srt
#
# Windows:
#   C:/xxx/test.srt
# =====================================

def escape_subtitle_path(
    srt_path
):

    path = str(
        Path(srt_path).resolve()
    )


    # ---------------------------------
    # バックスラッシュをスラッシュへ
    # ---------------------------------

    path = path.replace(
        "\\",
        "/"
    )


    # ---------------------------------
    # Windowsのドライブレター対応
    #
    # C:/xxx
    # ↓
    # C\:/xxx
    # ---------------------------------

    path = path.replace(
        ":",
        "\\:"
    )


    # ---------------------------------
    # シングルクォート対応
    # ---------------------------------

    path = path.replace(
        "'",
        "\\'"
    )


    return path


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
            "FFmpegをインストールしてPATHを設定してください。"
        )


    except subprocess.TimeoutExpired:

        raise RuntimeError(
            "FFmpegの確認がタイムアウトしました。"
        )


    if result.returncode != 0:

        raise RuntimeError(
            "FFmpegを実行できませんでした。"
        )


    # ---------------------------------
    # バージョン表示
    # ---------------------------------

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
# 字幕焼き込み
# =====================================

def embed_subtitle(
    mp4_path,
    srt_path,
    output_path=None
):

    # =================================
    # 入力MP4確認
    # =================================

    mp4_path = validate_input_file(
        mp4_path,
        ".mp4"
    )


    # =================================
    # 入力SRT確認
    # =================================

    srt_path = validate_input_file(
        srt_path,
        ".srt"
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
    # 出力フォルダ作成
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
    # SRTパス
    # =================================

    subtitle_path = (
        escape_subtitle_path(
            srt_path
        )
    )


    # =================================
    # FFmpegコマンド
    #
    # 字幕:
    #   subtitles filter
    #
    # 映像:
    #   libx264で再エンコード
    #
    # 音声:
    #   そのままコピー
    # =================================

    command = [

        "ffmpeg",

        "-y",

        "-i",
        str(mp4_path),

        "-vf",
        "subtitles=" + subtitle_path,

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


    log(
        "FFmpeg実行"
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
            result.stderr[-3000:]
            if result.stderr
            else "FFmpegからエラー内容が返されませんでした。"
        )


        raise RuntimeError(
            "字幕焼き込みに失敗しました。"
            "\n"
            +
            error_detail
        )


    # =================================
    # 出力ファイル確認
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


    return output_path


# =====================================
# downloads内のファイルを指定して実行
# =====================================

def embed_from_downloads(
    mp4_filename,
    srt_filename
):

    # ---------------------------------
    # ファイル名からパス部分を除去
    # ---------------------------------

    mp4_filename = Path(
        mp4_filename
    ).name


    srt_filename = Path(
        srt_filename
    ).name


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


    log(
        f"downloads MP4: {mp4_path}"
    )

    log(
        f"downloads SRT: {srt_path}"
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
#
# 例:
#
# python sub_embed.py test.mp4 test.srt
#
# =====================================

def main():

    # =================================
    # 引数確認
    # =================================

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

        print(
            "例:"
        )

        print(
            "python sub_embed.py "
            "test.mp4 test.srt"
        )

        print()

        print(
            "入力ファイルは downloads/ "
            "に置いてください。"
        )

        print()

        return 1


    # =================================
    # 引数取得
    # =================================

    mp4_filename = (
        sys.argv[1]
    )


    srt_filename = (
        sys.argv[2]
    )


    # =================================
    # 実行
    # =================================

    try:

        output_path = (
            embed_from_downloads(
                mp4_filename,
                srt_filename
            )
        )


        # =================================
        # 成功表示
        # =================================

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
            "====================================="
        )

        print()


        return 0


    # =================================
    # エラー
    # =================================

    except Exception as error:

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
