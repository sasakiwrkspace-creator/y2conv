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
#   mp3
#   mp4
#
# 時間指定:
#   start_time
#   end_time
#
# config.pyに合わせて
# すべて文字列パスで処理する。
# =====================================

import os
import re
import shutil
import subprocess
import traceback

from flask import request, jsonify

import config


# =====================================
# 設定
# =====================================

DOWNLOAD_DIR = config.DOWNLOAD_DIR

COOKIES_FILE = config.COOKIES_FILE

DENO_PATH = config.DENO_PATH

FFMPEG_PATH = config.FFMPEG_PATH

FFPROBE_PATH = config.FFPROBE_PATH


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
    "[YTDOWN] COOKIES_FILE:",
    COOKIES_FILE,
    flush=True
)

print(
    "[YTDOWN] COOKIES_FILE exists:",
    os.path.isfile(
        COOKIES_FILE
    ),
    flush=True
)

print(
    "[YTDOWN] DENO_PATH:",
    DENO_PATH,
    flush=True
)

print(
    "[YTDOWN] FFMPEG_PATH:",
    FFMPEG_PATH,
    flush=True
)

print(
    "[YTDOWN] FFPROBE_PATH:",
    FFPROBE_PATH,
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

                end_time = "00:00:00"


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

            print(
                "[YTDOWN] duration:",
                clip_duration,
                flush=True
            )


            # =================================
            # downloads
            # =================================

            os.makedirs(
                DOWNLOAD_DIR,
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

            if not FFMPEG_PATH:

                raise RuntimeError(
                    "FFmpegが見つかりません。"
                )


            if not os.path.isfile(
                FFMPEG_PATH
            ):

                raise RuntimeError(
                    "FFmpegが見つかりません:\n"
                    +
                    str(FFMPEG_PATH)
                )


            print(
                "[YTDOWN] ffmpeg:",
                FFMPEG_PATH,
                flush=True
            )


            # =================================
            # FFprobe
            # =================================

            if FFPROBE_PATH:

                print(
                    "[YTDOWN] ffprobe:",
                    FFPROBE_PATH,
                    flush=True
                )


            # =================================
            # Deno
            # =================================

            if DENO_PATH:

                print(
                    "[YTDOWN] deno:",
                    DENO_PATH,
                    flush=True
                )

            else:

                print(
                    "[YTDOWN] WARNING: Deno not found",
                    flush=True
                )


            # =================================
            # Cookies
            # =================================

            cookies_available = (
                os.path.isfile(
                    COOKIES_FILE
                )
            )


            print(
                "[YTDOWN] cookies:",
                COOKIES_FILE,
                flush=True
            )

            print(
                "[YTDOWN] cookies available:",
                cookies_available,
                flush=True
            )


            # =================================
            # 一時ディレクトリ
            # =================================

            temporary_directory = os.path.join(
                DOWNLOAD_DIR,
                ".ytdown_tmp"
            )


            # =================================
            # 前回の一時ディレクトリ削除
            # =================================

            if os.path.exists(
                temporary_directory
            ):

                print(
                    "[YTDOWN] removing old temp:",
                    temporary_directory,
                    flush=True
                )


                if os.path.isdir(
                    temporary_directory
                ):

                    shutil.rmtree(
                        temporary_directory
                    )

                else:

                    os.remove(
                        temporary_directory
                    )


            os.makedirs(
                temporary_directory,
                exist_ok=True
            )


            # =================================
            # UUID風の安全な一時名
            # =================================

            temporary_template = os.path.join(

                temporary_directory,

                "%(title)s_%(id)s.%(ext)s"

            )


            # =================================
            # 基本コマンド
            # =================================

            command = [

                yt_dlp_command,

                "--no-playlist",

                "--newline",

                "--no-update",

                "--restrict-filenames",

                "--ffmpeg-location",
                FFMPEG_PATH,

                "-o",
                temporary_template

            ]


            # =================================
            # EJS / Deno
            # =================================
            #
            # yt-dlp-ejsを利用するため
            # DenoがPATHにある環境では
            # 通常そのまま利用される。
            #
            # 念のためPATHを明示する。
            # =================================

            if DENO_PATH:

                deno_directory = os.path.dirname(
                    DENO_PATH
                )


                current_path = os.environ.get(
                    "PATH",
                    ""
                )


                if deno_directory not in current_path.split(
                    os.pathsep
                ):

                    command_environment_path = (
                        deno_directory
                        +
                        os.pathsep
                        +
                        current_path
                    )

                else:

                    command_environment_path = (
                        current_path
                    )

            else:

                command_environment_path = (
                    os.environ.get(
                        "PATH",
                        ""
                    )
                )


            # =================================
            # Cookies
            # =================================
            #
            # RenderのSecret Fileに
            # cookies.txtが存在する場合のみ使用。
            #
            # 無い場合はcookiesなしで実行する。
            # =================================

            if cookies_available:

                command.extend(
                    [
                        "--cookies",
                        COOKIES_FILE
                    ]
                )


                print(
                    "[YTDOWN] Using cookies.txt",
                    flush=True
                )

            else:

                print(
                    "[YTDOWN] Cookies not found.",
                    flush=True
                )

                print(
                    "[YTDOWN] Running without cookies.",
                    flush=True
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


            command.extend(
                [
                    "--download-sections",
                    section
                ]
            )


            print(
                "[YTDOWN] section:",
                section,
                flush=True
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
            # =================================

            else:

                command.extend(
                    [

                        "-f",
                        "bv*[ext=mp4]+ba[ext=m4a]/"
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
            # コマンドログ
            # =================================

            safe_command = list(
                command
            )


            if cookies_available:

                for index, value in enumerate(
                    safe_command
                ):

                    if value == COOKIES_FILE:

                        safe_command[index] = (
                            "[COOKIES_FILE]"
                        )


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
                safe_command,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            # =================================
            # 環境変数
            # =================================

            process_environment = os.environ.copy()

            process_environment["PATH"] = (
                command_environment_path
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

                errors="replace",

                env=process_environment,

                cwd=DOWNLOAD_DIR

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
            # エラー
            # =================================

            if process.returncode != 0:

                error_message = (
                    "yt-dlpでダウンロードに失敗しました。\n\n"
                    +
                    output[-10000:]
                )


                # -----------------------------
                # Bot判定
                # -----------------------------

                if (
                    "Sign in to confirm"
                    in output
                    or
                    "not a bot"
                    in output
                    or
                    "429" in output
                ):

                    if cookies_available:

                        error_message = (
                            "YouTubeからBot判定または"
                            "アクセス制限を受けました。\n\n"
                            "cookies.txtは読み込まれています。\n\n"
                            +
                            output[-10000:]
                        )

                    else:

                        error_message = (
                            "YouTubeからBot判定または"
                            "アクセス制限を受けました。\n\n"
                            "Renderにcookies.txtが設定されていません。\n"
                            "RenderのSecret Fileとして"
                            "/etc/secrets/cookies.txtを設定してください。\n\n"
                            +
                            output[-10000:]
                        )


                raise RuntimeError(
                    error_message
                )


            # =================================
            # 出力ファイル検索
            # =================================

            files = []


            for filename in os.listdir(
                temporary_directory
            ):

                file_path = os.path.join(

                    temporary_directory,

                    filename

                )


                if not os.path.isfile(
                    file_path
                ):

                    continue


                # yt-dlpの途中ファイルを除外

                if filename.endswith(
                    ".part"
                ):

                    continue


                if filename.endswith(
                    ".ytdl"
                ):

                    continue


                files.append(
                    file_path
                )


            # =================================
            # ファイルなし
            # =================================

            if not files:

                raise FileNotFoundError(
                    "yt-dlp終了後に出力ファイルが見つかりません。"
                )


            # =================================
            # 最新ファイル
            # =================================

            files.sort(

                key=os.path.getmtime,

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

            temporary_size = os.path.getsize(
                temporary_output
            )


            if temporary_size <= 0:

                raise RuntimeError(
                    "ダウンロードされたファイルのサイズが0 bytesです。"
                )


            # =================================
            # 拡張子
            # =================================

            if output_format == "mp3":

                final_extension = ".mp3"

            else:

                final_extension = ".mp4"


            # =================================
            # ファイル名
            # =================================

            temporary_filename = os.path.basename(
                temporary_output
            )


            temporary_stem = os.path.splitext(
                temporary_filename
            )[0]


            safe_stem = sanitize_filename(
                temporary_stem
            )


            # =================================
            # yt-dlpがIDを付けている場合
            #
            # そのままでも問題ないが、
            # ダウンロードファイル名として
            # 安全な形にする。
            # =================================

            final_filename = (
                safe_stem
                +
                final_extension
            )


            final_path = os.path.join(

                DOWNLOAD_DIR,

                final_filename

            )


            # =================================
            # 同名回避
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

                temporary_output,

                final_path

            )


            # =================================
            # 保存確認
            # =================================

            if not os.path.isfile(
                final_path
            ):

                raise FileNotFoundError(
                    "最終出力ファイルが作成されませんでした。"
                )


            final_size = os.path.getsize(
                final_path
            )


            if final_size <= 0:

                raise RuntimeError(
                    "最終出力ファイルのサイズが0 bytesです。"
                )


            # =================================
            # 一時ディレクトリ削除
            # =================================

            cleanup_temp_directory(
                temporary_directory
            )


            temporary_directory = None


            # =================================
            # ダウンロードURL
            # =================================
            #
            # app.py側にファイル配信routeがある場合、
            # /downloads/filename を使用。
            #
            # 既存のytdown.jsが
            # download_url / url のどちらでも
            # 受け取れるようにする。
            # =================================

            download_url = (
                "/downloads/"
                +
                final_filename
            )


            # =================================
            # 成功
            # =================================

            result = {

                "success":
                    True,

                "message":
                    "ダウンロードの準備ができました。",

                "filename":
                    final_filename,

                "file":
                    final_filename,

                "path":
                    final_path,

                "download_url":
                    download_url,

                "url":
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
            # 一時ディレクトリ削除
            # =================================

            if temporary_directory:

                try:

                    cleanup_temp_directory(
                        temporary_directory
                    )

                except Exception as cleanup_error:

                    print(
                        "[YTDOWN] cleanup warning:",
                        cleanup_error,
                        flush=True
                    )


            return jsonify({

                "success":
                    False,

                "message":
                    str(error),

                "error":
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
# =====================================

def parse_time(
    value
):

    value = str(
        value
    ).strip()


    if not value:

        return 0


    # =================================
    # 数字だけ
    # =================================

    if value.isdigit():

        return int(
            value
        )


    # =================================
    # 時間分割
    # =================================

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


    # =================================
    # 値チェック
    # =================================

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

    # =================================
    # config / PATH
    # =================================

    path = shutil.which(
        command
    )


    if path:

        return path


    # =================================
    # よくある場所
    # =================================

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
# ファイル名安全化
# =====================================

def sanitize_filename(
    filename
):

    filename = str(
        filename
    )


    # =================================
    # Windows / Unix禁止文字
    # =================================

    filename = re.sub(

        r'[\\/:*?"<>|]',

        "_",

        filename

    )


    # =================================
    # 制御文字
    # =================================

    filename = re.sub(

        r"[\x00-\x1f]",

        "_",

        filename

    )


    # =================================
    # 空白整理
    # =================================

    filename = re.sub(

        r"\s+",

        " ",

        filename

    ).strip()


    # =================================
    # 末尾
    # =================================

    filename = filename.rstrip(
        ". "
    )


    # =================================
    # 空の場合
    # =================================

    if not filename:

        filename = "youtube"


    return filename


# =====================================
# 同名ファイル回避
# =====================================

def unique_path(
    path
):

    path = str(
        path
    )


    if not os.path.exists(
        path
    ):

        return path


    directory = os.path.dirname(
        path
    )


    filename = os.path.basename(
        path
    )


    stem, suffix = os.path.splitext(
        filename
    )


    counter = 1


    while True:

        candidate = os.path.join(

            directory,

            f"{stem}_{counter}{suffix}"

        )


        if not os.path.exists(
            candidate
        ):

            return candidate


        counter += 1


# =====================================
# 一時ディレクトリ削除
# =====================================

def cleanup_temp_directory(
    temporary_directory
):

    if not temporary_directory:

        return


    if not os.path.exists(
        temporary_directory
    ):

        return


    if os.path.isdir(
        temporary_directory
    ):

        shutil.rmtree(
            temporary_directory
        )

    else:

        os.remove(
            temporary_directory
        )
