import os
import shutil
import subprocess
import tempfile
import uuid
import traceback

from pathlib import Path

import yt_dlp


# ==========================================================
# DEBUG
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


# ==========================================================
# 設定
# ==========================================================

FFMPEG_BINARY = "ffmpeg"

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)

COOKIES_SOURCE = (
    "/etc/secrets/cookies.txt"
)


# ==========================================================
# Cookie準備
# ==========================================================

def _prepare_cookie_file():

    if not os.path.isfile(
        COOKIES_SOURCE
    ):

        raise FileNotFoundError(
            "Cookieファイルが見つかりません: "
            +
            COOKIES_SOURCE
        )

    temporary_cookie = (
        tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            prefix="y2conv_stream_cookies_",
            delete=False
        )
    )

    temporary_path = (
        temporary_cookie.name
    )

    temporary_cookie.close()

    try:

        shutil.copyfile(
            COOKIES_SOURCE,
            temporary_path
        )

        return temporary_path

    except Exception:

        try:

            if os.path.exists(
                temporary_path
            ):

                os.remove(
                    temporary_path
                )

        except Exception:

            pass

        raise


# ==========================================================
# 共通yt-dlpオプション
# ==========================================================

def _base_ydl_opts(
    cookie_path=None
):

    opts = {

        "quiet":
            False,

        "no_warnings":
            False,

        "noprogress":
            True,

        "noplaylist":
            True,

        "verbose":
            True,

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        "remote_components": {

            "ejs:github"

        }

    }

    if cookie_path:

        opts[
            "cookiefile"
        ] = cookie_path

    return opts


# ==========================================================
# FFmpeg確認
# ==========================================================

def _check_ffmpeg():

    path = shutil.which(
        FFMPEG_BINARY
    )

    if not path:

        raise RuntimeError(
            "FFmpegが見つかりません。"
        )

    return path


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

    try:

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

        return float(text)

    except Exception as error:

        raise ValueError(
            f"時間形式が不正です: {value}"
        ) from error


# ==========================================================
# 情報取得
# ==========================================================

def _extract_info(
    url
):

    cookie_path = None

    try:

        cookie_path = (
            _prepare_cookie_file()
        )

        opts = _base_ydl_opts(
            cookie_path
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

        return info

    finally:

        if cookie_path:

            try:

                if os.path.exists(
                    cookie_path
                ):

                    os.remove(
                        cookie_path
                    )

            except Exception:

                pass


# ==========================================================
# FFmpeg用HTTPヘッダー
# ==========================================================

def _get_http_headers(
    fmt
):

    if not fmt:

        return {}

    headers = (
        fmt.get("http_headers")
        or {}
    )

    return dict(
        headers
    )


# ==========================================================
# FFmpeg HTTPヘッダー文字列
# ==========================================================

def _headers_to_ffmpeg(
    headers
):

    if not headers:

        return []

    values = []

    for key, value in headers.items():

        if value is None:

            continue

        key_text = str(
            key
        ).strip()

        value_text = str(
            value
        ).strip()

        if not key_text:

            continue

        values.append(
            f"{key_text}: {value_text}"
        )

    if not values:

        return []

    return [

        "-headers",

        "\r\n".join(
            values
        )
        +
        "\r\n"

    ]


# ==========================================================
# MP4フォーマット選択
# ==========================================================

def _select_mp4_format(
    info
):

    formats = info.get(
        "formats"
    ) or []

    # ======================================================
    # combined MP4
    # ======================================================

    combined = []

    for fmt in formats:

        ext = str(
            fmt.get("ext") or ""
        ).lower()

        vcodec = fmt.get(
            "vcodec"
        )

        acodec = fmt.get(
            "acodec"
        )

        if ext != "mp4":

            continue

        if vcodec in (
            None,
            "none"
        ):

            continue

        if acodec in (
            None,
            "none"
        ):

            continue

        combined.append(
            fmt
        )

    if combined:

        combined.sort(

            key=lambda fmt: (

                fmt.get("height") or 0,

                fmt.get("tbr") or 0,

                fmt.get("filesize")
                or
                fmt.get("filesize_approx")
                or
                0

            ),

            reverse=True

        )

        return {

            "_separate":
                False,

            "format":
                combined[0]

        }

    # ======================================================
    # separate video
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

            fmt.get("tbr") or 0,

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

                fmt.get("tbr") or 0,

                fmt.get("filesize")
                or
                fmt.get("filesize_approx")
                or
                0

            ),

            reverse=True

        )

        audio_fmt = audio_candidates[0]

    return {

        "_separate":
            True,

        "video":
            video_fmt,

        "audio":
            audio_fmt

    }


# ==========================================================
# FFmpeg 単一URL
# ==========================================================

def _run_ffmpeg_single(
    input_url,
    output_path,
    start_seconds,
    end_seconds,
    headers=None
):

    ffmpeg_path = _check_ffmpeg()

    duration = (
        end_seconds
        -
        start_seconds
    )

    if duration <= 0:

        raise ValueError(
            "指定時間が不正です。"
        )

    command = [

        ffmpeg_path,

        "-hide_banner",

        "-loglevel",
        "warning",

        "-ss",
        str(start_seconds)

    ]

    command.extend(
        _headers_to_ffmpeg(
            headers
        )
    )

    command.extend([

        "-i",
        input_url,

        "-t",
        str(duration),

        "-map",
        "0:v:0",

        "-map",
        "0:a?",

        "-c",
        "copy",

        "-movflags",
        "+faststart",

        "-y",

        str(output_path)

    ])

    print(
        "[YTDLP_STREAM] FFmpeg command:",
        " ".join(command),
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
            process.stderr[-5000:]

        )

    if not os.path.isfile(
        output_path
    ):

        raise RuntimeError(
            "FFmpeg後のMP4ファイルがありません。"
        )

    if os.path.getsize(
        output_path
    ) <= 0:

        raise RuntimeError(
            "FFmpeg後のMP4ファイルサイズが0です。"
        )

    return str(
        output_path
    )


# ==========================================================
# MP4全体
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

    cookie_path = None

    try:

        cookie_path = (
            _prepare_cookie_file()
        )

        opts = _base_ydl_opts(
            cookie_path
        )

        opts.update({

            "format":
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",

            "outtmpl":
                str(
                    output_dir
                    /
                    "%(id)s.%(ext)s"
                ),

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

            info = ydl.extract_info(

                url,

                download=True

            )

            if not info:

                raise RuntimeError(
                    "MP4情報を取得できませんでした。"
                )

            prepared = Path(
                ydl.prepare_filename(
                    info
                )
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

        mp4_path = prepared.with_suffix(
            ".mp4"
        )

        if not mp4_path.is_file():

            if prepared.is_file():

                mp4_path = prepared

            else:

                matches = list(
                    output_dir.glob(
                        f"{video_id}.*"
                    )
                )

                matches = [

                    p for p in matches

                    if p.is_file()

                    and
                    p.suffix.lower()
                    not in (
                        ".part",
                        ".ytdl",
                        ".temp"
                    )

                ]

                if not matches:

                    raise FileNotFoundError(
                        "MP4ダウンロード後のファイルが見つかりません。"
                    )

                matches.sort(

                    key=lambda p:
                        p.stat().st_mtime,

                    reverse=True

                )

                mp4_path = matches[0]

        if mp4_path.stat().st_size <= 0:

            raise RuntimeError(
                "MP4ファイルサイズが0です。"
            )

        print(
            "[YTDLP_STREAM] Full MP4 COMPLETE:",
            mp4_path,
            flush=True
        )

        return {

            "path":
                str(mp4_path),

            "filename":
                mp4_path.name,

            "video_id":
                video_id,

            "title":
                title,

            "duration":
                duration

        }

    except Exception as e:

        print(
            "[YTDLP_STREAM] create_mp4_full ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if cookie_path:

            try:

                if os.path.exists(
                    cookie_path
                ):

                    os.remove(
                        cookie_path
                    )

            except Exception:

                pass


# ==========================================================
# MP4時間指定
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

    print(
        "[YTDLP_STREAM] Extracting stream information...",
        flush=True
    )

    info = _extract_info(
        url
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

    selected = _select_mp4_format(
        info
    )

    temporary_name = (

        "."
        +
        video_id
        +
        "_"
        +
        uuid.uuid4().hex
        +
        ".mp4"

    )

    output_path = (
        output_dir
        /
        temporary_name
    )

    try:

        # ==================================================
        # combined
        # ==================================================

        if not selected.get(
            "_separate"
        ):

            fmt = selected.get(
                "format"
            )

            stream_url = fmt.get(
                "url"
            )

            if not stream_url:

                raise RuntimeError(
                    "MP4ストリームURLを取得できませんでした。"
                )

            headers = _get_http_headers(
                fmt
            )

            print(
                "[YTDLP_STREAM] Direct combined MP4:",
                fmt.get("format_id"),
                flush=True
            )

            _run_ffmpeg_single(

                input_url=
                    stream_url,

                output_path=
                    output_path,

                start_seconds=
                    start_seconds,

                end_seconds=
                    end_seconds,

                headers=
                    headers

            )

        # ==================================================
        # separate video/audio
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
                else None
            )

            audio_url = (
                audio_fmt.get("url")
                if audio_fmt
                else None
            )

            if not video_url:

                raise RuntimeError(
                    "MP4映像ストリームURLを取得できませんでした。"
                )

            video_headers = (
                _get_http_headers(
                    video_fmt
                )
            )

            audio_headers = (
                _get_http_headers(
                    audio_fmt
                )
                if audio_fmt
                else {}
            )

            # ----------------------------------------------
            # video only
            # ----------------------------------------------

            if not audio_url:

                _run_ffmpeg_single(

                    input_url=
                        video_url,

                    output_path=
                        output_path,

                    start_seconds=
                        start_seconds,

                    end_seconds=
                        end_seconds,

                    headers=
                        video_headers

                )

            # ----------------------------------------------
            # video + audio
            # ----------------------------------------------

            else:

                ffmpeg_path = _check_ffmpeg()

                duration_seconds = (
                    end_seconds
                    -
                    start_seconds
                )

                command = [

                    ffmpeg_path,

                    "-hide_banner",

                    "-loglevel",
                    "warning",

                    "-ss",
                    str(start_seconds)

                ]

                command.extend(
                    _headers_to_ffmpeg(
                        video_headers
                    )
                )

                command.extend([

                    "-i",
                    video_url,

                    "-ss",
                    str(start_seconds)

                ])

                command.extend(
                    _headers_to_ffmpeg(
                        audio_headers
                    )
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
                    "[YTDLP_STREAM] Direct video/audio FFmpeg",
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
                        process.stderr[-5000:]

                    )

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

    except Exception:

        try:

            if output_path.exists():

                output_path.unlink()

        except Exception:

            pass

        raise
