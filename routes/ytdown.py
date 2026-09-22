# =====================================
# YouTube時間指定ダウンロード
# routes/ytdown.py
#
# index.html
#     ↓
# /static/ytdown.js
#     ↓
# POST /ytdown
#     ↓
# ytdown.py
#     ↓
# yt-dlp
#     ↓
# FFmpeg
#
# 対応:
#   mp3
#   mp4
#
# 時間指定:
#   start_time
#   end_time
#
# Cookie:
#   使用しない
#
# Render:
#   Deno
#   yt-dlp-ejs
#   FFmpeg
# =====================================


import os
import re
import shutil
import subprocess
import traceback
import uuid

from pathlib import Path

from flask import request, jsonify

import config


# =====================================
# 設定
# =====================================

DOWNLOAD_DIR = Path(
    config.DOWNLOAD_DIR
).resolve()


# =====================================
# ログ
# =====================================

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
            # JSON
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
            # URL
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
            # YouTube URL確認
            # =================================

            if not is_youtube_url(
                youtube_url
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

                end_time = "00:00:00"


            end_time = str(
                end_time
            ).strip()


            # =================================
            # 時間変換
            # =================================

            start_seconds = parse_time(
                start_time
            )


            end_seconds = parse_time(
                end_time
            )


            # =================================
            # 時間チェック
            # =================================

            if start_seconds < 0:

                raise ValueError(
                    "開始時間が不正です。"
                )


            if end_seconds < 0:

                raise ValueError(
                    "終了時間が不正です。"
                )


            # =================================
            # 終了時間
            #
            # 00:00:00
            # ↓
            # 終了時間なし
            # =================================

            if end_seconds == 0:

                clip_duration = None

            else:

                if end_seconds <= start_seconds:

                    raise ValueError(
                        "終了時間は開始時間より後にしてください。"
                    )


                clip_duration = (
                    end_seconds
                    -
                    start_seconds
                )


            # =================================
            # ログ
            # =================================

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

            print(
                "[YTDOWN] start_seconds:",
                start_seconds,
                flush=True
            )

            print(
                "[YTDOWN] end_seconds:",
                end_seconds,
                flush=True
            )

            print(
                "[YTDOWN] duration:",
                clip_duration,
                flush=True
            )


            # =================================
            # DOWNLOAD_DIR
            # =================================

            DOWNLOAD_DIR.mkdir(
                parents=True,
                exist_ok=True
            )


            # =================================
            # yt-dlp
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
            # FFmpeg
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
            # Deno
            # =================================

            deno_command = find_command(
                "deno"
            )


            if deno_command is None:

                raise RuntimeError(
                    "Denoが見つかりません。"
                    "DockerfileでDenoをインストールしてください。"
                )


            print(
                "[YTDOWN] deno:",
                deno_command,
                flush=True
            )


            # =================================
            # Deno version
            # =================================

            deno_version = get_command_version(
                deno_command,
                "--version"
            )


            print(
                "[YTDOWN] Deno version:",
                deno_version,
                flush=True
            )


            # =================================
            # yt-dlp version
            # =================================

            yt_dlp_version = get_command_version(
                yt_dlp_command,
                "--version"
            )


            print(
                "[YTDOWN] yt-dlp version:",
                yt_dlp_version,
                flush=True
            )


            # =================================
            # 一時ディレクトリ
            #
            # リクエストごとにUUIDを使用。
            #
            # 同時アクセスしても
            # ファイルが混ざらないようにする。
            # =================================

            job_id = uuid.uuid4().hex


            temporary_directory = (
                DOWNLOAD_DIR
                /
                ".ytdown_tmp_"
                +
                Path(job_id)
            )


            # Path同士の結合を安全にする
            temporary_directory = (
                DOWNLOAD_DIR
                /
                f".ytdown_tmp_{job_id}"
            )


            temporary_directory.mkdir(
                parents=True,
                exist_ok=True
            )


            print(
                "[YTDOWN] temp directory:",
                temporary_directory,
                flush=True
            )


            # =================================
            # 一時ファイル
            # =================================

            temporary_template = (
                temporary_directory
                /
                "download_%(id)s.%(ext)s"
            )


            # =================================
            # 時間指定
            # =================================

            section_start = format_seconds(
                start_seconds
            )


            if clip_duration is None:

                section_end = ""

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


            print(
                "[YTDOWN] download section:",
                section,
                flush=True
            )


            # =================================
            # 基本コマンド
            #
            # ローカル版を参考にする。
            # =================================

            command = [

                yt_dlp_command,

                "--no-update",

                "--no-playlist",

                "--newline",

                "--restrict-filenames",

                "--ffmpeg-location",
                ffmpeg_command,

                "--js-runtimes",
                f"deno:{deno_command}",

                "-o",
                str(
                    temporary_template
                )

            ]


            # =================================
            # EJS
            #
            # PyPI版yt-dlp-ejsを使用する。
            #
            # GitHub/npmから追加取得するのではなく、
            # インストール済みのyt-dlp-ejsを使う。
            # =================================


            # =================================
            # 時間指定
            # =================================

            command.extend(
                [
                    "--download-sections",
                    section
                ]
            )


            # =================================
            # MP3
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


            # =================================
            # MP4
            #
            # ローカルで成功している
            # format selectorを使用。
            # =================================

            else:

                command.extend(
                    [

                        "-f",

                        (
                            "bestvideo[ext=mp4]"
                            "+"
                            "bestaudio[ext=m4a]"
                            "/"
                            "best[ext=mp4]"
                            "/"
                            "best"
                        ),

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

                cwd=str(
                    temporary_directory
                ),

                stdout=subprocess.PIPE,

                stderr=subprocess.STDOUT,

                text=True,

                encoding="utf-8",

                errors="replace",

                timeout=1800

            )


            # =================================
            # ログ
            # =================================

            output = (
                process.stdout
                or
                ""
            )


            print(
                "[YTDOWN] yt-dlp RETURN CODE:",
                process.returncode,
                flush=True
            )


            print(
                "[YTDOWN] yt-dlp OUTPUT:",
                flush=True
            )


            print(
                output,
                flush=True
            )


            # =================================
            # yt-dlp失敗
            # =================================

            if process.returncode != 0:

                error_message = (
                    build_ytdlp_error_message(
                        output
                    )
                )


                raise RuntimeError(
                    error_message
                )


            # =================================
            # 出力ファイル検索
            # =================================

            files = [

                path

                for path
                in temporary_directory.iterdir()

                if path.is_file()

                and
                not path.name.endswith(
                    ".part"
                )

                and
                not path.name.endswith(
                    ".ytdl"
                )

            ]


            if not files:

                raise FileNotFoundError(
                    "yt-dlp終了後に出力ファイルが見つかりません。"
                )


            # =================================
            # 目的の拡張子を優先
            # =================================

            if output_format == "mp3":

                preferred_files = [

                    path

                    for path
                    in files

                    if path.suffix.lower()
                    ==
                    ".mp3"

                ]

            else:

                preferred_files = [

                    path

                    for path
                    in files

                    if path.suffix.lower()
                    ==
                    ".mp4"

                ]


            if preferred_files:

                files = preferred_files


            # =================================
            # 最新ファイル
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
            # ファイル名
            # =================================

            safe_stem = sanitize_filename(
                temporary_output.stem
            )


            # =================================
            # 拡張子
            # =================================

            if output_format == "mp3":

                final_suffix = ".mp3"

            else:

                final_suffix = ".mp4"


            # =================================
            # 最終パス
            # =================================

            final_path = (
                DOWNLOAD_DIR
                /
                (
                    safe_stem
                    +
                    final_suffix
                )
            )


            # =================================
            # 同名対策
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
            # 移動
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
            # 最終確認
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

            cleanup_directory(
                temporary_directory
            )


            temporary_directory = None


            # =================================
            # ダウンロードURL
            #
            # 現在のytdown.jsは
            # download_url / url
            # を確認する。
            #
            # /downloads/<filename>
            # がapp.py側で公開されている場合に使用。
            # =================================

            download_url = (
                "/downloads/"
                +
                final_path.name
            )


            # =================================
            # 成功
            # =================================

            result = {

                "success":
                    True,

                "message":
                    "ダウンロードが完了しました。",

                "filename":
                    final_path.name,

                "file":
                    final_path.name,

                "path":
                    str(final_path),

                "download_url":
                    download_url,

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


        except subprocess.TimeoutExpired:

            print(
                "[YTDOWN] TIMEOUT",
                flush=True
            )


            if temporary_directory:

                cleanup_directory(
                    temporary_directory
                )


            return jsonify({

                "success":
                    False,

                "message":
                    "yt-dlpの処理がタイムアウトしました。",

                "error_type":
                    "TimeoutExpired"

            }), 500


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


            if temporary_directory:

                cleanup_directory(
                    temporary_directory
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
# YouTube URL確認
# =====================================

def is_youtube_url(
    url
):

    url = str(
        url
    ).lower()


    allowed_hosts = [

        "youtube.com",

        "www.youtube.com",

        "m.youtube.com",

        "youtu.be",

        "www.youtu.be"

    ]


    for host in allowed_hosts:

        if (
            host
            in
            url
        ):

            return True


    return False


# =====================================
# 時間文字列 → 秒
#
# 対応:
#
# HH:MM:SS
# H:MM:SS
# MM:SS
# SS
# =====================================

def parse_time(
    value
):

    value = str(
        value
    ).strip()


    if not value:

        return 0


    # -------------------------------------
    # 数字のみ
    # -------------------------------------

    if value.isdigit():

        return int(
            value
        )


    parts = value.split(
        ":"
    )


    try:

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

            raise ValueError


    except ValueError:

        raise ValueError(
            "時間はHH:MM:SS形式で指定してください: "
            +
            value
        )


    if hours < 0:

        raise ValueError(
            "時間は0以上で指定してください。"
        )


    if minutes < 0 or minutes >= 60:

        raise ValueError(
            "分は00～59で指定してください。"
        )


    if seconds < 0 or seconds >= 60:

        raise ValueError(
            "秒は00～59で指定してください。"
        )


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


    if seconds < 0:

        seconds = 0


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

    # -------------------------------------
    # PATH
    # -------------------------------------

    path = shutil.which(
        command
    )


    if path:

        return path


    # -------------------------------------
    # よくある絶対パス
    # -------------------------------------

    candidates = [

        f"/usr/bin/{command}",

        f"/usr/local/bin/{command}",

        f"/opt/homebrew/bin/{command}",

        f"/root/.local/bin/{command}",

        f"/app/.deno/bin/{command}"

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
# コマンドバージョン
# =====================================

def get_command_version(
    command,
    argument
):

    try:

        result = subprocess.run(

            [
                command,
                argument
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.STDOUT,

            text=True,

            encoding="utf-8",

            errors="replace",

            timeout=30

        )


        return (
            result.stdout
            or
            ""
        ).strip()


    except Exception as error:

        return (
            "version取得失敗: "
            +
            str(error)
        )


# =====================================
# yt-dlpエラーメッセージ
# =====================================

def build_ytdlp_error_message(
    output
):

    output = (
        output
        or
        ""
    )


    # -------------------------------------
    # Bot / 429
    # -------------------------------------

    if (
        "Sign in to confirm you're not a bot"
        in output
        or
        "Sign in to confirm you’re not a bot"
        in output
        or
        "HTTP Error 429"
        in output
    ):

        return (
            "YouTubeからbot判定またはHTTP 429が返されました。\n\n"
            "yt-dlpの設定処理は完了していますが、"
            "YouTube側でこのアクセス元からの取得が制限されています。\n\n"
            +
            output[-8000:]
        )


    # -------------------------------------
    # 403
    # -------------------------------------

    if (
        "403 Forbidden"
        in output
    ):

        return (
            "YouTubeからHTTP 403 Forbiddenが返されました。\n\n"
            +
            output[-8000:]
        )


    # -------------------------------------
    # 一般エラー
    # -------------------------------------

    return (
        "yt-dlpでダウンロードに失敗しました。\n\n"
        +
        output[-8000:]
    )


# =====================================
# ファイル名安全化
# =====================================

def sanitize_filename(
    filename
):

    filename = str(
        filename
    )


    # -------------------------------------
    # Windows / Unix
    # -------------------------------------

    filename = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        filename
    )


    # -------------------------------------
    # 制御文字
    # -------------------------------------

    filename = re.sub(
        r"[\x00-\x1f]",
        "_",
        filename
    )


    # -------------------------------------
    # 空白
    # -------------------------------------

    filename = re.sub(
        r"\s+",
        " ",
        filename
    ).strip()


    # -------------------------------------
    # 末尾
    # -------------------------------------

    filename = filename.rstrip(
        ". "
    )


    # -------------------------------------
    # 空の場合
    # -------------------------------------

    if not filename:

        filename = "youtube"


    # -------------------------------------
    # 長すぎるファイル名
    # -------------------------------------

    if len(filename) > 180:

        filename = filename[:180].rstrip()


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


# =====================================
# 一時ディレクトリ削除
# =====================================

def cleanup_directory(
    directory
):

    if directory is None:

        return


    try:

        directory = Path(
            directory
        )


        if directory.exists():

            shutil.rmtree(
                directory
            )


            print(
                "[YTDOWN] temp cleanup:",
                directory,
                flush=True
            )


    except Exception as error:

        print(
            "[YTDOWN] temp cleanup warning:",
            error,
            flush=True
        )
