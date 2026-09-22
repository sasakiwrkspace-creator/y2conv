# =====================================
# YouTube時間指定ダウンロード
# routes/ytdown.py
#
# index.html
#     ↓
# /static/ytdown.js
#     ↓
# /ytdown
#     ↓
# ytdown.py
#     ↓
# yt-dlp
#     ↓
# FFmpeg
#
# 対応:
#
# mp3
# mp4
#
# 時間指定:
#
# start_time
# end_time
#
# =====================================

import os
import re
import shutil
import subprocess
import traceback
from pathlib import Path

from flask import request, jsonify

import config


# =====================================
# 設定
# =====================================

DOWNLOAD_DIR = Path(
    config.DOWNLOAD_DIR
).resolve()


print(
    "==========================================",
    flush=True
)

print(
    "[YTDOWN] ytdown.py loaded",
    flush=True
)

print(
    "[YTDOWN] DOWNLOAD_DIR:",
    DOWNLOAD_DIR,
    flush=True
)

print(
    "==========================================",
    flush=True
)


# =====================================
# register
# =====================================

def register_ytdown(app):

    print(
        "[YTDOWN] register_ytdown()",
        flush=True
    )


    # =====================================
    # /ytdown
    # =====================================

    @app.route(
        "/ytdown",
        methods=["POST"]
    )
    def ytdown_route():

        print(
            "==========================================",
            flush=True
        )

        print(
            "[YTDOWN] /ytdown START",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        temporary_directory = None


        try:

            # =================================
            # JSON取得
            # =================================

            data = request.get_json(
                silent=True
            )


            if not data:

                raise ValueError(
                    "リクエストJSONがありません。"
                )


            print(
                "[YTDOWN] request:",
                data,
                flush=True
            )


            # =================================
            # YouTube URL
            # =================================

            youtube_url = data.get(
                "url"
            )


            if youtube_url is None:

                youtube_url = data.get(
                    "youtube_url"
                )


            if youtube_url is None:

                raise ValueError(
                    "YouTube URLが指定されていません。"
                )


            youtube_url = str(
                youtube_url
            ).strip()


            if not youtube_url:

                raise ValueError(
                    "YouTube URLが空です。"
                )


            # =================================
            # URL確認
            # =================================

            if (
                "youtube.com" not in youtube_url
                and
                "youtu.be" not in youtube_url
            ):

                raise ValueError(
                    "YouTube URLを指定してください。"
                )


            # =================================
            # 出力形式
            # =================================

            output_format = data.get(
                "format"
            )


            if output_format is None:

                output_format = data.get(
                    "output_format"
                )


            if output_format is None:

                output_format = "mp3"


            output_format = str(
                output_format
            ).strip().lower()


            if output_format not in (
                "mp3",
                "mp4"
            ):

                raise ValueError(
                    "出力形式はmp3またはmp4です。"
                )


            # =================================
            # 開始時間
            # =================================

            start_time = data.get(
                "start_time"
            )


            if start_time is None:

                start_time = "00:00:00"


            start_time = str(
                start_time
            ).strip()


            # =================================
            # 終了時間
            # =================================

            end_time = data.get(
                "end_time"
            )


            if end_time is None:

                end_time = ""


            end_time = str(
                end_time
            ).strip()


            print(
                "[YTDOWN] URL:",
                youtube_url,
                flush=True
            )

            print(
                "[YTDOWN] format:",
                output_format,
                flush=True
            )

            print(
                "[YTDOWN] start_time:",
                start_time,
                flush=True
            )

            print(
                "[YTDOWN] end_time:",
                end_time,
                flush=True
            )


            # =================================
            # 時間変換
            # =================================

            start_seconds = parse_time(
                start_time
            )


            if end_time:

                end_seconds = parse_time(
                    end_time
                )

            else:

                end_seconds = None


            # =================================
            # 時間チェック
            # =================================

            if start_seconds < 0:

                raise ValueError(
                    "開始時間が不正です。"
                )


            if end_seconds is not None:

                if end_seconds <= start_seconds:

                    raise ValueError(
                        "終了時間は開始時間より後にしてください。"
                    )


            print(
                "[YTDOWN] start seconds:",
                start_seconds,
                flush=True
            )


            print(
                "[YTDOWN] end seconds:",
                end_seconds,
                flush=True
            )


            # =================================
            # downloadsディレクトリ
            # =================================

            DOWNLOAD_DIR.mkdir(
                parents=True,
                exist_ok=True
            )


            # =================================
            # yt-dlp確認
            # =================================

            yt_dlp_command = find_command(
                "yt-dlp"
            )


            if yt_dlp_command is None:

                raise RuntimeError(
                    "yt-dlpが見つかりません。"
                )


            print(
                "[YTDOWN] yt-dlp:",
                yt_dlp_command,
                flush=True
            )


            # =================================
            # FFmpeg確認
            # =================================

            ffmpeg_command = find_command(
                "ffmpeg"
            )


            if ffmpeg_command is None:

                raise RuntimeError(
                    "FFmpegが見つかりません。"
                )


            print(
                "[YTDOWN] ffmpeg:",
                ffmpeg_command,
                flush=True
            )


            # =================================
            # 一時ディレクトリ
            # =================================

            temporary_directory = (
                DOWNLOAD_DIR
                /
                ".ytdown_tmp"
            )


            # =================================
            # 古い一時ディレクトリ削除
            # =================================

            if temporary_directory.exists():

                print(
                    "[YTDOWN] removing old temp:",
                    temporary_directory,
                    flush=True
                )


                if temporary_directory.is_dir():

                    shutil.rmtree(
                        temporary_directory
                    )

                else:

                    temporary_directory.unlink()


            temporary_directory.mkdir(
                parents=True,
                exist_ok=True
            )


            # =================================
            # 出力テンプレート
            # =================================

            temporary_template = (
                temporary_directory
                /
                "%(title)s.%(ext)s"
            )


            # =================================
            # yt-dlp基本コマンド
            # =================================

            command = [

                yt_dlp_command,

                "--no-playlist",

                "--newline",

                "--restrict-filenames",

                "-o",
                str(
                    temporary_template
                )

            ]


            # =================================
            # 時間指定
            # =================================

            section_start = format_seconds(
                start_seconds
            )


            if end_seconds is None:

                section = (
                    "*"
                    +
                    section_start
                    +
                    "-"
                )

            else:

                section_end = format_seconds(
                    end_seconds
                )

                section = (
                    "*"
                    +
                    section_start
                    +
                    "-"
                    +
                    section_end
                )


            command.extend(
                [
                    "--download-sections",
                    section
                ]
            )


            # =================================
            # 出力形式
            # =================================

            if output_format == "mp3":

                command.extend(
                    [

                        "-x",

                        "--audio-format",
                        "mp3",

                        "--audio-quality",
                        "192K"

                    ]
                )

            else:

                command.extend(
                    [

                        "-f",
                        "bv*+ba/b",

                        "--merge-output-format",
                        "mp4"

                    ]
                )


            # =================================
            # URL
            # =================================

            command.append(
                youtube_url
            )


            # =================================
            # コマンド表示
            # =================================

            print(
                "==========================================",
                flush=True
            )

            print(
                "[YTDOWN] yt-dlp START",
                flush=True
            )

            print(
                "[YTDOWN] section:",
                section,
                flush=True
            )

            print(
                "[YTDOWN] command:",
                command,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            # =================================
            # yt-dlp実行
            # =================================

            process = subprocess.run(

                command,

                stdout=subprocess.PIPE,

                stderr=subprocess.STDOUT,

                text=True,

                encoding="utf-8",

                errors="replace"

            )


            # =================================
            # 結果表示
            # =================================

            print(
                "[YTDOWN] yt-dlp RETURN CODE:",
                process.returncode,
                flush=True
            )


            if process.stdout:

                print(
                    "[YTDOWN] yt-dlp OUTPUT:",
                    flush=True
                )

                print(
                    process.stdout,
                    flush=True
                )


            # =================================
            # エラー
            # =================================

            if process.returncode != 0:

                raise RuntimeError(
                    "yt-dlpでダウンロードに失敗しました。\n\n"
                    +
                    process.stdout[-5000:]
                )


            # =================================
            # 出力ファイル検索
            # =================================

            files = [

                path

                for path
                in temporary_directory.iterdir()

                if path.is_file()

            ]


            if not files:

                raise FileNotFoundError(
                    "yt-dlp終了後に出力ファイルが見つかりません。"
                )


            # =================================
            # 最新ファイル取得
            # =================================

            files.sort(

                key=lambda path:
                    path.stat().st_mtime,

                reverse=True

            )


            temporary_output = files[0]


            print(
                "[YTDOWN] temporary output:",
                temporary_output,
                flush=True
            )


            # =================================
            # サイズ確認
            # =================================

            temporary_size = (
                temporary_output.stat().st_size
            )


            if temporary_size <= 0:

                raise RuntimeError(
                    "ダウンロードされたファイルのサイズが0 bytesです。"
                )


            # =================================
            # 最終ファイル名
            # =================================

            safe_stem = sanitize_filename(
                temporary_output.stem
            )


            if output_format == "mp3":

                final_filename = (
                    safe_stem
                    +
                    ".mp3"
                )

            else:

                final_filename = (
                    safe_stem
                    +
                    ".mp4"
                )


            final_path = (
                DOWNLOAD_DIR
                /
                final_filename
            )


            # =================================
            # 同名ファイル回避
            # =================================

            final_path = unique_path(
                final_path
            )


            print(
                "[YTDOWN] final output:",
                final_path,
                flush=True
            )


            # =================================
            # 保存
            # =================================

            shutil.move(

                str(
                    temporary_output
                ),

                str(
                    final_path
                )

            )


            # =================================
            # 保存確認
            # =================================

            if not final_path.exists():

                raise FileNotFoundError(
                    "最終出力ファイルが作成されませんでした。"
                )


            if not final_path.is_file():

                raise RuntimeError(
                    "最終出力パスがファイルではありません。"
                )


            final_size = (
                final_path.stat().st_size
            )


            if final_size <= 0:

                raise RuntimeError(
                    "最終出力ファイルのサイズが0 bytesです。"
                )


            # =================================
            # 一時ディレクトリ削除
            # =================================

            try:

                shutil.rmtree(
                    temporary_directory
                )

                temporary_directory = None

            except Exception as cleanup_error:

                print(
                    "[YTDOWN] temp cleanup warning:",
                    cleanup_error,
                    flush=True
                )


            # =================================
            # 成功結果
            # =================================

            result = {

                "success":
                    True,

                "filename":
                    final_path.name,

                "file":
                    final_path.name,

                "path":
                    str(final_path),

                "format":
                    output_format,

                "start_time":
                    start_time,

                "end_time":
                    end_time,

                "start_seconds":
                    start_seconds,

                "end_seconds":
                    end_seconds,

                "size":
                    final_size

            }


            print(
                "==========================================",
                flush=True
            )

            print(
                "[YTDOWN] SUCCESS",
                flush=True
            )

            print(
                "[YTDOWN] file:",
                final_path,
                flush=True
            )

            print(
                "[YTDOWN] size:",
                final_size,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            return jsonify(
                result
            ), 200


        except Exception as error:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[YTDOWN] FAILED",
                flush=True
            )

            print(
                "[YTDOWN] ERROR TYPE:",
                type(error).__name__,
                flush=True
            )

            print(
                "[YTDOWN] ERROR:",
                str(error),
                flush=True
            )

            print(
                "[YTDOWN] TRACEBACK START",
                flush=True
            )

            traceback.print_exc()

            print(
                "[YTDOWN] TRACEBACK END",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            # =================================
            # エラー時の一時ファイル削除
            # =================================

            if (
                temporary_directory
                and
                temporary_directory.exists()
            ):

                try:

                    shutil.rmtree(
                        temporary_directory
                    )

                except Exception as cleanup_error:

                    print(
                        "[YTDOWN] cleanup failed:",
                        cleanup_error,
                        flush=True
                    )


            return jsonify({

                "success":
                    False,

                "message":
                    str(error),

                "error_type":
                    type(error).__name__

            }), 500


# =====================================
# 時間文字列 → 秒
#
# 対応:
#
# HH:MM:SS
# H:MM:SS
# MM:SS
# SS
#
# =====================================

def parse_time(
    value
):

    value = str(
        value
    ).strip()


    if not value:

        return 0


    # =====================================
    # 数字だけ
    # =====================================

    if value.isdigit():

        return int(
            value
        )


    # =====================================
    # : で分割
    # =====================================

    parts = value.split(
        ":"
    )


    if len(parts) == 3:

        hours = int(
            parts[0]
        )

        minutes = int(
            parts[1]
        )

        seconds = int(
            parts[2]
        )


    elif len(parts) == 2:

        hours = 0

        minutes = int(
            parts[0]
        )

        seconds = int(
            parts[1]
        )


    else:

        raise ValueError(
            "時間はHH:MM:SS形式で指定してください: "
            +
            value
        )


    # =====================================
    # 分チェック
    # =====================================

    if minutes < 0 or minutes >= 60:

        raise ValueError(
            "分は00～59で指定してください。"
        )


    # =====================================
    # 秒チェック
    # =====================================

    if seconds < 0 or seconds >= 60:

        raise ValueError(
            "秒は00～59で指定してください。"
        )


    # =====================================
    # 秒へ変換
    # =====================================

    return (

        hours * 3600

        +

        minutes * 60

        +

        seconds

    )


# =====================================
# 秒 → HH:MM:SS
# =====================================

def format_seconds(
    seconds
):

    seconds = int(
        seconds
    )


    hours = (
        seconds
        //
        3600
    )


    minutes = (
        seconds
        %
        3600
        //
        60
    )


    remaining_seconds = (
        seconds
        %
        60
    )


    return (

        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{remaining_seconds:02d}"

    )


# =====================================
# コマンド検索
# =====================================

def find_command(
    command
):

    # =====================================
    # PATHから検索
    # =====================================

    path = shutil.which(
        command
    )


    if path:

        return path


    # =====================================
    # よくある絶対パス
    # =====================================

    candidates = [

        f"/usr/bin/{command}",

        f"/usr/local/bin/{command}",

        f"/opt/homebrew/bin/{command}",

        f"/root/.local/bin/{command}"

    ]


    for candidate in candidates:

        if os.path.isfile(
            candidate
        ):

            if os.access(
                candidate,
                os.X_OK
            ):

                return candidate


    return None


# =====================================
# ファイル名安全化
# =====================================

def sanitize_filename(
    filename
):

    filename = str(
        filename
    )


    # =====================================
    # Windows / Unix禁止文字
    # =====================================

    filename = re.sub(

        r'[\\/:*?"<>|]',

        "_",

        filename

    )


    # =====================================
    # 制御文字
    # =====================================

    filename = re.sub(

        r"[\x00-\x1f]",

        "_",

        filename

    )


    # =====================================
    # 空白整理
    # =====================================

    filename = re.sub(

        r"\s+",

        " ",

        filename

    ).strip()


    # =====================================
    # 空の場合
    # =====================================

    if not filename:

        filename = "youtube"


    return filename


# =====================================
# 同名ファイル回避
# =====================================

def unique_path(
    path
):

    path = Path(
        path
    )


    if not path.exists():

        return path


    stem = path.stem

    suffix = path.suffix


    counter = 1


    while True:

        candidate = (

            path.parent
            /
            f"{stem}_{counter}{suffix}"

        )


        if not candidate.exists():

            return candidate


        counter += 1
