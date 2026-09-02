import os
import subprocess
import tempfile
import uuid
import shutil
import traceback
from pathlib import Path

import yt_dlp


# ==========================================================
# 起動時 DEBUG
# ==========================================================

print(
    "==========================================",
    flush=True
)

print(
    "[YTDLP_STREAM] ytdlp_stream.py loaded",
    flush=True
)

print(
    "[YTDLP_STREAM] Python:",
    os.sys.version,
    flush=True
)

print(
    "[YTDLP_STREAM] Python executable:",
    os.sys.executable,
    flush=True
)

print(
    "[YTDLP_STREAM] Current working directory:",
    os.getcwd(),
    flush=True
)


# ==========================================================
# Deno
# ==========================================================

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)


print(
    "[YTDLP_STREAM] DENO_PATH:",
    DENO_PATH,
    flush=True
)

print(
    "[YTDLP_STREAM] Deno exists:",
    os.path.isfile(DENO_PATH),
    flush=True
)

print(
    "[YTDLP_STREAM] Deno executable:",
    os.access(
        DENO_PATH,
        os.X_OK
    ),
    flush=True
)

print(
    "[YTDLP_STREAM] Deno which:",
    shutil.which("deno"),
    flush=True
)


# ==========================================================
# FFmpeg
# ==========================================================

FFMPEG_BINARY = "ffmpeg"


print(
    "[YTDLP_STREAM] ffmpeg:",
    shutil.which(FFMPEG_BINARY),
    flush=True
)

print(
    "==========================================",
    flush=True
)


# ==========================================================
# Cookie
# ==========================================================

COOKIES_SOURCE = (
    "/etc/secrets/cookies.txt"
)


# ==========================================================
# Cookie準備
# ==========================================================

def _prepare_cookie_file():

    print(
        "[YTDLP_STREAM] Cookie preparation START",
        flush=True
    )

    print(
        "[YTDLP_STREAM] Cookie source:",
        COOKIES_SOURCE,
        flush=True
    )

    print(
        "[YTDLP_STREAM] Cookie exists:",
        os.path.isfile(COOKIES_SOURCE),
        flush=True
    )

    if not os.path.isfile(
        COOKIES_SOURCE
    ):

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            +
            COOKIES_SOURCE
        )

    temporary_cookie_path = None

    try:

        temporary_cookie_file = (
            tempfile.NamedTemporaryFile(

                mode="w",

                suffix=".txt",

                prefix="y2conv_stream_cookies_",

                delete=False

            )
        )

        temporary_cookie_path = (
            temporary_cookie_file.name
        )

        temporary_cookie_file.close()

        shutil.copyfile(

            COOKIES_SOURCE,

            temporary_cookie_path

        )

        print(
            "[YTDLP_STREAM] Temporary cookie:",
            temporary_cookie_path,
            flush=True
        )

        print(
            "[YTDLP_STREAM] Cookie size:",
            os.path.getsize(
                temporary_cookie_path
            ),
            "bytes",
            flush=True
        )

        return temporary_cookie_path

    except Exception as e:

        print(
            "[YTDLP_STREAM] Cookie preparation ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

            except Exception:

                pass

        raise


# ==========================================================
# yt-dlp 共通オプション
#
# ytdlp.py と同じ方向に統一
# ==========================================================

def _base_ydl_opts(
    temporary_cookie_path=None
):

    opts = {

        "quiet":
            True,

        "no_warnings":
            True,

        "noprogress":
            True,

        "noplaylist":
            True,

        "verbose":
            False,

        # ==================================================
        # YouTube JavaScript challenge
        # ==================================================

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        # ==================================================
        # EJS challenge scripts
        # ==================================================

        "remote_components": {

            "ejs:github"

        },

        # ==================================================
        # YouTube client
        # ==================================================

        "extractor_args": {

            "youtube": {

                "player_client": [
                    "web"
                ]

            }

        }

    }


    if temporary_cookie_path:

        opts[
            "cookiefile"
        ] = temporary_cookie_path


    print(
        "[YTDLP_STREAM] yt-dlp options:",
        flush=True
    )

    print(
        "[YTDLP_STREAM] js_runtimes:",
        opts.get("js_runtimes"),
        flush=True
    )

    print(
        "[YTDLP_STREAM] remote_components:",
        opts.get("remote_components"),
        flush=True
    )

    print(
        "[YTDLP_STREAM] extractor_args:",
        opts.get("extractor_args"),
        flush=True
    )

    print(
        "[YTDLP_STREAM] cookiefile:",
        temporary_cookie_path,
        flush=True
    )


    return opts


# ==========================================================
# 時間 → 秒
# ==========================================================

def _time_to_seconds(
    value
):

    if value is None:

        return 0.0


    text = str(
        value
    ).strip()


    if not text:

        return 0.0


    parts = text.split(":")


    if len(parts) == 3:

        return (

            float(parts[0]) * 3600

            +

            float(parts[1]) * 60

            +

            float(parts[2])

        )


    if len(parts) == 2:

        return (

            float(parts[0]) * 60

            +

            float(parts[1])

        )


    return float(
        text
    )


# ==========================================================
# 安全なファイル名
# ==========================================================

def _safe_filename(
    value
):

    text = str(
        value or "video"
    ).strip()


    if not text:

        text = "video"


    invalid_chars = (

        "/",
        "\\",
        ":",
        "*",
        "?",
        '"',
        "<",
        ">",
        "|"

    )


    for char in invalid_chars:

        text = text.replace(

            char,

            "_"

        )


    return text[:180]


# ==========================================================
# CookieファイルからCookieヘッダー生成
#
# FFmpegへ直接URLを渡す場合に使用。
#
# Netscape形式Cookie:
#
# domain
# flag
# path
# secure
# expiration
# name
# value
# ==========================================================

def _cookie_header_from_file(
    cookie_path
):

    if not cookie_path:

        return ""


    if not os.path.isfile(
        cookie_path
    ):

        return ""


    cookies = []


    try:

        with open(
            cookie_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            for line in file:

                line = line.strip()


                if not line:

                    continue


                if line.startswith(
                    "#"
                ):

                    continue


                parts = line.split(
                    "\t"
                )


                if len(parts) < 7:

                    continue


                name = parts[5].strip()

                value = parts[6].strip()


                if not name:

                    continue


                cookies.append(

                    name
                    +
                    "="
                    +
                    value

                )


    except Exception as e:

        print(
            "[YTDLP_STREAM] Cookie header ERROR:",
            repr(e),
            flush=True
        )

        return ""


    if not cookies:

        return ""


    return "; ".join(
        cookies
    )


# ==========================================================
# YouTube情報取得
#
# Cookie + Deno + EJSを使用
# ==========================================================

def _extract_info(
    url,
    temporary_cookie_path=None
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP_STREAM] extract_info START",
        flush=True
    )

    print(
        "[YTDLP_STREAM] URL:",
        url,
        flush=True
    )


    if not url:

        raise ValueError(
            "YouTube URLが空です。"
        )


    opts = _base_ydl_opts(
        temporary_cookie_path
    )


    with yt_dlp.YoutubeDL(
        opts
    ) as ydl:

        info = ydl.extract_info(

            url,

            download=False

        )


    if not info:

        raise RuntimeError(
            "YouTube動画情報を取得できませんでした。"
        )


    print(
        "[YTDLP_STREAM] Video ID:",
        info.get("id"),
        flush=True
    )

    print(
        "[YTDLP_STREAM] Title:",
        info.get("title"),
        flush=True
    )

    print(
        "[YTDLP_STREAM] Duration:",
        info.get("duration"),
        flush=True
    )

    print(
        "[YTDLP_STREAM] Format count:",
        len(
            info.get("formats") or []
        ),
        flush=True
    )

    print(
        "[YTDLP_STREAM] extract_info COMPLETE",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    return info


# ==========================================================
# MP4用フォーマット選択
# ==========================================================

def _select_mp4_format(
    info
):

    formats = info.get(
        "formats"
    ) or []


    candidates = []


    # ======================================================
    # combined MP4
    # ======================================================

    for fmt in formats:

        if fmt.get("vcodec") in (
            None,
            "none"
        ):

            continue


        ext = str(
            fmt.get("ext") or ""
        ).lower()


        if ext != "mp4":

            continue


        acodec = fmt.get(
            "acodec"
        )


        filesize = (

            fmt.get("filesize")

            or

            fmt.get("filesize_approx")

            or

            0

        )


        height = (

            fmt.get("height")

            or

            0

        )


        if acodec not in (
            None,
            "none"
        ):

            candidates.append({

                "format":
                    fmt,

                "kind":
                    "combined",

                "height":
                    height,

                "filesize":
                    filesize

            })


    # ======================================================
    # combined優先
    # ======================================================

    if candidates:

        candidates.sort(

            key=lambda item: (

                item["height"],

                item["filesize"]

            ),

            reverse=True

        )


        selected = candidates[0][
            "format"
        ]


        print(
            "[YTDLP_STREAM] Selected combined MP4:",
            selected.get("format_id"),
            flush=True
        )


        return selected


    # ======================================================
    # separate
    # ======================================================

    video_candidates = []

    audio_candidates = []


    for fmt in formats:

        ext = str(
            fmt.get("ext") or ""
        ).lower()


        if ext != "mp4":

            continue


        vcodec = fmt.get(
            "vcodec"
        )

        acodec = fmt.get(
            "acodec"
        )

        height = (

            fmt.get("height")

            or

            0

        )


        if (

            vcodec not in (
                None,
                "none"
            )

            and

            acodec in (
                None,
                "none"
            )

        ):

            video_candidates.append(
                fmt
            )


        elif (

            vcodec in (
                None,
                "none"
            )

            and

            acodec not in (
                None,
                "none"
            )

        ):

            audio_candidates.append(
                fmt
            )


    if not video_candidates:

        raise RuntimeError(
            "利用可能なMP4映像ストリームが見つかりません。"
        )


    video_candidates.sort(

        key=lambda fmt: (

            fmt.get("height") or 0,

            fmt.get("filesize")

            or

            fmt.get("filesize_approx")

            or

            0

        ),

        reverse=True

    )


    video_fmt = video_candidates[0]


    audio_fmt = None


    if audio_candidates:

        audio_candidates.sort(

            key=lambda fmt: (

                fmt.get("abr") or 0,

                fmt.get("filesize")

                or

                fmt.get("filesize_approx")

                or

                0

            ),

            reverse=True

        )


        audio_fmt = audio_candidates[0]


    print(
        "[YTDLP_STREAM] Selected video:",
        video_fmt.get("format_id"),
        flush=True
    )


    print(
        "[YTDLP_STREAM] Selected audio:",
        audio_fmt.get("format_id")
        if audio_fmt
        else None,
        flush=True
    )


    return {

        "_separate":
            True,

        "video":
            video_fmt,

        "audio":
            audio_fmt

    }


# ==========================================================
# FFmpeg URL用HTTPヘッダー
# ==========================================================

def _build_ffmpeg_headers(
    stream_info,
    cookie_header=""
):

    headers = []


    http_headers = (
        stream_info.get(
            "http_headers"
        )
        or {}
        if isinstance(
            stream_info,
            dict
        )
        else {}
    )


    for key, value in http_headers.items():

        if not key:

            continue


        if str(key).lower() == "cookie":

            continue


        headers.append(

            str(key)
            +
            ": "
            +
            str(value)

        )


    if cookie_header:

        headers.append(

            "Cookie: "
            +
            cookie_header

        )


    return headers


# ==========================================================
# FFmpegコマンドへheaders追加
# ==========================================================

def _append_headers(
    command,
    headers
):

    for header in headers:

        command.extend([

            "-headers",

            header

        ])


    return command


# ==========================================================
# FFmpeg実行
#
# combined stream用
# ==========================================================

def _run_ffmpeg(
    input_url,
    output_path,
    start_seconds,
    end_seconds,
    stream_info=None,
    cookie_header=""
):

    output_path = str(
        output_path
    )


    command = [

        FFMPEG_BINARY,

        "-hide_banner",

        "-loglevel",
        "warning",

        "-ss",
        str(start_seconds)

    ]


    headers = _build_ffmpeg_headers(

        stream_info
        if stream_info
        else {},

        cookie_header

    )


    _append_headers(
        command,
        headers
    )


    command.extend([

        "-i",

        input_url,

        "-t",

        str(

            max(

                0,

                end_seconds -
                start_seconds

            )

        ),

        "-map",
        "0:v:0",

        "-map",
        "0:a?",

        "-c",
        "copy",

        "-movflags",
        "+faststart",

        "-y",

        output_path

    ])


    print(
        "[YTDLP_STREAM] FFmpeg command START",
        flush=True
    )

    print(
        "[YTDLP_STREAM] Input URL length:",
        len(
            input_url
        ),
        flush=True
    )

    print(
        "[YTDLP_STREAM] Header count:",
        len(
            headers
        ),
        flush=True
    )


    process = subprocess.run(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )


    if process.returncode != 0:

        print(
            "[YTDLP_STREAM] FFmpeg stderr:",
            process.stderr,
            flush=True
        )


        raise RuntimeError(

            "指定区間のMP4作成に失敗しました。\n"

            +

            process.stderr[-3000:]

        )


    if not os.path.isfile(
        output_path
    ):

        raise RuntimeError(
            "FFmpeg実行後のMP4ファイルがありません。"
        )


    if os.path.getsize(
        output_path
    ) <= 0:

        raise RuntimeError(
            "FFmpeg実行後のMP4ファイルサイズが0です。"
        )


    return output_path


# ==========================================================
# MP4全体ダウンロード
#
# 時間指定なしの場合
#
# yt-dlpが実際にダウンロードする。
# ==========================================================

def create_mp4_full(
    url,
    output_dir
):

    output_dir = Path(
        output_dir
    )


    output_dir.mkdir(

        parents=True,

        exist_ok=True

    )


    temporary_cookie_path = None


    try:

        temporary_cookie_path = (
            _prepare_cookie_file()
        )


        info = _extract_info(

            url,

            temporary_cookie_path

        )


        video_id = (

            info.get("id")

            or

            str(uuid.uuid4())

        )


        title = (

            info.get("title")

            or

            "YouTube Video"

        )


        duration = info.get(
            "duration"
        )


        output_template = str(

            output_dir
            /
            "%(id)s.%(ext)s"

        )


        opts = _base_ydl_opts(

            temporary_cookie_path

        )


        opts.update({

            "format":
                "best[ext=mp4]/best",

            "outtmpl":
                output_template,

            "merge_output_format":
                "mp4"

        })


        print(
            "[YTDLP_STREAM] Full MP4 download START",
            flush=True
        )


        with yt_dlp.YoutubeDL(
            opts
        ) as ydl:

            result_info = ydl.extract_info(

                url,

                download=True

            )


            prepared_path = Path(

                ydl.prepare_filename(
                    result_info
                )

            )


        mp4_path = prepared_path.with_suffix(
            ".mp4"
        )


        if mp4_path.is_file():

            final_path = mp4_path


        elif prepared_path.is_file():

            final_path = prepared_path


        else:

            matches = list(

                output_dir.glob(

                    f"{video_id}.*"

                )

            )


            if not matches:

                raise FileNotFoundError(

                    "MP4ダウンロード後のファイルが"
                    "見つかりません。"

                )


            matches.sort(

                key=lambda p:
                    p.stat().st_mtime,

                reverse=True

            )


            final_path = matches[0]


        if final_path.stat().st_size <= 0:

            raise RuntimeError(
                "MP4ファイルサイズが0です。"
            )


        print(
            "[YTDLP_STREAM] Full MP4 COMPLETE:",
            final_path,
            flush=True
        )


        return {

            "path":
                str(final_path),

            "filename":
                final_path.name,

            "video_id":
                video_id,

            "title":
                title,

            "duration":
                duration

        }


    finally:

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

            except Exception:

                pass


# ==========================================================
# MP4時間指定
#
# YouTube全体をローカルへ保存せず、
# yt-dlpでストリーム情報を取得し、
# FFmpegへ直接URLを渡す。
#
# 再エンコードなし。
# ==========================================================

def create_mp4_range(
    url,
    output_dir,
    start_time=None,
    end_time=None
):

    output_dir = Path(
        output_dir
    )


    output_dir.mkdir(

        parents=True,

        exist_ok=True

    )


    start_seconds = _time_to_seconds(
        start_time
    )


    end_seconds = _time_to_seconds(
        end_time
    )


    if start_seconds < 0:

        raise ValueError(
            "開始時間は0秒以上である必要があります。"
        )


    if end_seconds <= start_seconds:

        raise ValueError(
            "終了時間は開始時間より後である必要があります。"
        )


    temporary_cookie_path = None


    # ======================================================
    # 一時出力
    # ======================================================

    output_path = (

        output_dir
        /
        (
            "."
            +
            uuid.uuid4().hex
            +
            ".mp4"
        )

    )


    try:

        # ==================================================
        # Cookie
        # ==================================================

        temporary_cookie_path = (
            _prepare_cookie_file()
        )


        cookie_header = (
            _cookie_header_from_file(
                temporary_cookie_path
            )
        )


        print(
            "[YTDLP_STREAM] Cookie header available:",
            bool(cookie_header),
            flush=True
        )


        # ==================================================
        # YouTube情報
        # ==================================================

        print(
            "[YTDLP_STREAM] Extracting stream information...",
            flush=True
        )


        info = _extract_info(

            url,

            temporary_cookie_path

        )


        video_id = (

            info.get("id")

            or

            str(uuid.uuid4())

        )


        title = (

            info.get("title")

            or

            "YouTube Video"

        )


        duration = info.get(
            "duration"
        )


        # ==================================================
        # フォーマット選択
        # ==================================================

        selected = _select_mp4_format(
            info
        )


        # ==================================================
        # combined MP4
        # ==================================================

        if not selected.get(
            "_separate"
        ):

            stream_url = selected.get(
                "url"
            )


            if not stream_url:

                raise RuntimeError(
                    "MP4ストリームURLを取得できませんでした。"
                )


            print(
                "[YTDLP_STREAM] Direct combined MP4:",
                selected.get("format_id"),
                flush=True
            )


            _run_ffmpeg(

                input_url=
                    stream_url,

                output_path=
                    output_path,

                start_seconds=
                    start_seconds,

                end_seconds=
                    end_seconds,

                stream_info=
                    selected,

                cookie_header=
                    cookie_header

            )


        # ==================================================
        # separate video + audio
        # ==================================================

        else:

            video_fmt = selected.get(
                "video"
            )


            audio_fmt = selected.get(
                "audio"
            )


            video_url = (

                video_fmt.get("url")

                if video_fmt

                else

                None

            )


            audio_url = (

                audio_fmt.get("url")

                if audio_fmt

                else

                None

            )


            if not video_url:

                raise RuntimeError(
                    "MP4映像ストリームURLを取得できませんでした。"
                )


            # ==================================================
            # video only
            # ==================================================

            if not audio_url:

                print(
                    "[YTDLP_STREAM] Direct video-only stream",
                    flush=True
                )


                _run_ffmpeg(

                    input_url=
                        video_url,

                    output_path=
                        output_path,

                    start_seconds=
                        start_seconds,

                    end_seconds=
                        end_seconds,

                    stream_info=
                        video_fmt,

                    cookie_header=
                        cookie_header

                )


            # ==================================================
            # video + audio
            # ==================================================

            else:

                duration_seconds = (

                    end_seconds -
                    start_seconds

                )


                command = [

                    FFMPEG_BINARY,

                    "-hide_banner",

                    "-loglevel",
                    "warning",

                    "-ss",
                    str(start_seconds)

                ]


                video_headers = (
                    _build_ffmpeg_headers(

                        video_fmt,

                        cookie_header

                    )
                )


                _append_headers(

                    command,

                    video_headers

                )


                command.extend([

                    "-i",

                    video_url,

                    "-ss",

                    str(start_seconds)

                ])


                audio_headers = (
                    _build_ffmpeg_headers(

                        audio_fmt,

                        cookie_header

                    )
                )


                _append_headers(

                    command,

                    audio_headers

                )


                command.extend([

                    "-i",

                    audio_url,

                    "-t",

                    str(duration_seconds),

                    "-map",
                    "0:v:0",

                    "-map",
                    "1:a:0",

                    "-c:v",
                    "copy",

                    "-c:a",
                    "copy",

                    "-movflags",
                    "+faststart",

                    "-y",

                    str(output_path)

                ])


                print(
                    "[YTDLP_STREAM] Direct video/audio stream",
                    flush=True
                )


                print(
                    "[YTDLP_STREAM] Video format:",
                    video_fmt.get("format_id"),
                    flush=True
                )


                print(
                    "[YTDLP_STREAM] Audio format:",
                    audio_fmt.get("format_id"),
                    flush=True
                )


                process = subprocess.run(

                    command,

                    stdout=subprocess.PIPE,

                    stderr=subprocess.PIPE,

                    text=True

                )


                if process.returncode != 0:

                    print(
                        "[YTDLP_STREAM] FFmpeg stderr:",
                        process.stderr,
                        flush=True
                    )


                    raise RuntimeError(

                        "指定区間のMP4作成に失敗しました。\n"

                        +

                        process.stderr[-3000:]

                    )


        # ==================================================
        # 完成確認
        # ==================================================

        if not output_path.is_file():

            raise RuntimeError(
                "指定区間MP4の出力ファイルがありません。"
            )


        if output_path.stat().st_size <= 0:

            raise RuntimeError(
                "指定区間MP4のサイズが0です。"
            )


        print(
            "[YTDLP_STREAM] Range MP4 COMPLETE:",
            output_path,
            flush=True
        )


        return {

            "path":
                str(output_path),

            "filename":
                output_path.name,

            "video_id":
                video_id,

            "title":
                title,

            "duration":
                duration

        }


    except Exception as e:

        print(
            "[YTDLP_STREAM] create_mp4_range ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()


        try:

            if output_path.exists():

                output_path.unlink()

        except Exception:

            pass


        raise


    finally:

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

                    print(
                        "[YTDLP_STREAM] Temporary cookie removed",
                        flush=True
                    )

            except Exception as e:

                print(
                    "[YTDLP_STREAM] Cookie cleanup ERROR:",
                    repr(e),
                    flush=True
                )


# ==========================================================
# 終了
# ==========================================================

print(
    "[YTDLP_STREAM] Module initialization complete",
    flush=True
)

print(
    "==========================================",
    flush=True
)
