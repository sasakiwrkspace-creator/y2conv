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
import shutil
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

            content = file.read()

    except UnicodeDecodeError:

        raise RuntimeError(
            "SRTファイルをUTF-8として読み込めませんでした。\n"
            "SRTをUTF-8形式で保存してください。"
        )

    except OSError as error:

        raise RuntimeError(
            f"SRTファイルを読み込めませんでした: {error}"
        )

    if not content.strip():

        raise RuntimeError(
            "SRTファイルが空です。"
        )

    log(
        f"SRT文字数: {len(content)}"
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
    # 環境変数で指定されている場合
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
                f"環境変数指定フォント: {environment_font_path}"
            )

            return environment_font_path


    # ---------------------------------
    # 優先する日本語フォント
    # ---------------------------------

    preferred_fonts = [

        # Noto
        "NotoSansCJK-Regular.ttc",
        "NotoSansCJKJP-Regular.otf",
        "NotoSansJP-Regular.ttf",
        "NotoSerifCJK-Regular.ttc",
        "NotoSerifCJKJP-Regular.otf",
        "NotoSerifJP-Regular.ttf",

        # IPA
        "ipaexg.ttf",
        "ipaexm.ttf",
        "IPAGothic.ttf",
        "IPAPGothic.ttf",
        "IPAMincho.ttf",
        "IPAPMincho.ttf",

        # Takao
        "TakaoGothic.ttf",
        "TakaoPGothic.ttf",
        "TakaoMincho.ttf",

        # VL
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

        BASE_DIR / "fonts",

    ]


    # ---------------------------------
    # 優先フォントを検索
    # ---------------------------------

    for directory in font_directories:

        if not directory.exists():

            continue

        for font_name in preferred_fonts:

            try:

                matches = list(
                    directory.rglob(
                        font_name
                    )
                )

            except Exception:

                continue

            if matches:

                font_path = matches[0]

                log(
                    f"日本語フォント検出: {font_path}"
                )

                return font_path


    # ---------------------------------
    # ファイル名に日本語フォント名を
    # 含むものを検索
    # ---------------------------------

    japanese_keywords = [

        "noto",
        "ipa",
        "takao",
        "gothic",
        "mincho",
        "cjk",
        "japan",
        "jp",

    ]


    possible_fonts = []


    for directory in font_directories:

        if not directory.exists():

            continue

        try:

            for extension in (
                "*.ttf",
                "*.otf",
                "*.ttc"
            ):

                possible_fonts.extend(
                    directory.rglob(
                        extension
                    )
                )

        except Exception:

            continue


    for font_path in possible_fonts:

        lower_name = (
            font_path.name.lower()
        )

        for keyword in japanese_keywords:

            if keyword in lower_name:

                log(
                    f"候補日本語フォント検出: {font_path}"
                )

                return font_path


    # ---------------------------------
    # fc-listを使った検索
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
                            f"fc-list日本語フォント検出: {font_path}"
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

    # ---------------------------------
    # Linuxでは / に統一
    # ---------------------------------

    path = path.replace(
        "\\",
        "/"
    )

    # ---------------------------------
    # FFmpeg filter parser用
    # ---------------------------------

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
    # 基本字幕フィルター
    # ---------------------------------

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )


    # ---------------------------------
    # 日本語フォント指定
    #
    # fontsdirを使わずfontfileを直接
    # 指定する。
    #
    # libassの環境差を減らす。
    # ---------------------------------

    if font_path:

        font_path_escaped = (
            escape_ffmpeg_filter_path(
                font_path
            )
        )

        # subtitles filterでは
        # force_styleでFontNameを指定する
        #
        # フォントファイルそのものを
        # FontNameに指定できないため、
        # fontsdir方式を利用する。
        #
        # ただしfontsdirにはディレクトリを
        # 指定する必要がある。

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
            f"字幕フォントディレクトリ: {font_directory}"
        )

    return video_filter


# =====================================
# FFmpegコマンド表示用
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
    # 既存出力削除
    # =================================

    if output_path.exists():

        log(
            f"既存出力ファイルを削除: {output_path}"
        )

        try:

            output_path.unlink()

        except Exception as error:

            raise RuntimeError(
                "既存の出力ファイルを削除できませんでした: "
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
    # フィルター作成
    # =================================

    video_filter = make_subtitle_filter(
        srt_path,
        font_path
    )


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
    # サイズ
    # =================================

    try:

        input_mp4_size = (
            mp4_path.stat().st_size
        )

    except Exception:

        input_mp4_size = 0


    try:

        input_srt_size = (
            srt_path.stat().st_size
        )

    except Exception:

        input_srt_size = 0


    log(
        f"入力MP4サイズ: {input_mp4_size} bytes"
    )

    log(
        f"入力SRTサイズ: {input_srt_size} bytes"
    )


    # =================================
    # FFmpegコマンド
    # =================================

    command = [

        ffmpeg_path,

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

        "-movflags",
        "+faststart",

        str(output_path)

    ]


    # =================================
    # コマンドログ
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
    #
    # stderrをリアルタイム表示
    # =================================

    try:

        process = subprocess.Popen(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.STDOUT,

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


    ffmpeg_output_lines = []


    # =================================
    # FFmpegログ取得
    # =================================

    try:

        if process.stdout:

            for line in process.stdout:

                line = line.rstrip()

                if line:

                    ffmpeg_output_lines.append(
                        line
                    )

                    print(
                        "[FFMPEG]",
                        line,
                        flush=True
                    )

    except Exception as error:

        process.kill()

        process.wait()

        raise RuntimeError(
            "FFmpegログ取得中にエラーが発生しました: "
            +
            str(error)
        )


    # =================================
    # FFmpeg終了待機
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
            f"FFmpegエラー: return code={return_code}"
        )


        error_detail = (
            "\n".join(
                ffmpeg_output_lines[-100:]
            )
            if ffmpeg_output_lines
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

            "FFmpegは正常終了しましたが、"
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
    # 実行
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
