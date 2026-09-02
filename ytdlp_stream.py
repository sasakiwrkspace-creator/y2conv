import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

import yt_dlp


# ==========================================================
# FFmpeg
# ==========================================================

FFMPEG_BINARY = "ffmpeg"


# ==========================================================
# Deno
# ==========================================================

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)


# ==========================================================
# Cookie
# ==========================================================

COOKIES_SOURCE = "/etc/secrets/cookies.txt"


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
    "[YTDLP_STREAM] yt_dlp version:",
    yt_dlp.version.__version__,
    flush=True
)

print(
    "[YTDLP_STREAM] yt_dlp location:",
    yt_dlp.__file__,
    flush=True
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
    "[YTDLP_STREAM] Cookie exists:",
    os.path.isfile(COOKIES_SOURCE),
    flush=True
)

print(
    "[YTDLP_STREAM] ffmpeg:",
    shutil.which("ffmpeg"),
    flush=True
)

print(
    "==========================================",
    flush=True
)


# ==========================================================
# Cookie準備
#
# ytdlp.py と同じ方式。
#
# 元ファイル:
#   /etc/secrets/cookies.txt
#
# yt-dlpには一時コピーを渡す。
# ==========================================================

def _prepare_cookie_file():

    print(
        "[YTDLP_STREAM] Cookie preparation START",
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

        source_size = os.path.getsize(
            COOKIES_SOURCE
        )

        print(
            "[YTDLP_STREAM] Cookie source size:",
            source_size,
            "bytes",
            flush=True
        )

        temporary_cookie = (
            tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                prefix="y2conv_stream_cookies_",
                delete=False
            )
        )

        temporary_cookie_path = (
            temporary_cookie.name
        )

        temporary_cookie.close()

        shutil.copyfile(
            COOKIES_SOURCE,
            temporary_cookie_path
        )

        temporary_size = os.path.getsize(
            temporary_cookie_path
        )

        print(
            "[YTDLP_STREAM] Temporary cookie:",
            temporary_cookie_path,
            flush=True
        )

        print(
            "[YTDLP_STREAM] Temporary cookie size:",
            temporary_size,
            "bytes",
            flush=True
        )

        return temporary_cookie_path

    except Exception:

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

    finally:

        print(
            "[YTDLP_STREAM] Cookie preparation END",
            flush=True
        )


# ==========================================================
# yt-dlp 共通オプション
#
# ytdlp.py と同じYouTube対策を使用。
# ==========================================================

def _base_ydl_opts(
    temporary_cookie_path=None
):

    opts = {

        "quiet":
            True,

        "no_warnings":
            False,

        "noprogress":
            True,

        "noplaylist":
            True,

        "verbose":
            True,

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

        }

    }

    if temporary_cookie_path:

        opts[
            "cookiefile"
        ] = temporary_cookie_path

    return opts


# ==========================================================
# Deno確認
# ==========================================================

def _validate_deno():

    print(
        "[YTDLP_STREAM] Checking Deno...",
        flush=True
    )

    if not os.path.isfile(
        DENO_PATH
    ):

        raise RuntimeError(
            "Denoが利用できません: "
            +
            DENO_PATH
        )

    if not os.access(
        DENO_PATH,
        os.X_OK
    ):

        raise RuntimeError(
            "Denoに実行権限がありません: "
            +
            DENO_PATH
        )

    result = subprocess.run(

        [
            DENO_PATH,
            "--version"
        ],

        capture_output=True,

        text=True,

        timeout=10

    )

    print(
        "[YTDLP_STREAM] Deno returncode:",
        result.returncode,
        flush=True
    )

    print(
        "[YTDLP_STREAM] Deno stdout:",
        result.stdout,
        flush=True
    )

    if result.stderr:

        print(
            "[YTDLP_STREAM] Deno stderr:",
            result.stderr,
            flush=True
        )

    if result.returncode != 0:

        raise RuntimeError(
            "Denoの実行に失敗しました。"
        )


# ==========================================================
# 時間 → 秒
# ==========================================================

def _time_to_seconds(value):

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
# 安全なファイル名
# ==========================================================

def _safe_filename(value):

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
# YouTube情報取得
#
# ytdlp.py と同じ
# Cookie + Deno + EJS
# を使用。
# ==========================================================

def _extract_info(url):

    temporary_cookie_path = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です。"
            )

        _validate_deno()

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        opts = _base_ydl_opts(
            temporary_cookie_path
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

        print(
            "[YTDLP_STREAM] Deno:",
            DENO_PATH,
            flush=True
        )

        print(
            "[YTDLP_STREAM] Cookie:",
            temporary_cookie_path,
            flush=True
        )

        print(
            "[YTDLP_STREAM] remote_components:",
            opts.get("remote_components"),
            flush=True
        )

        print(
            "[YTDLP_STREAM] js_runtimes:",
            opts.get("js_runtimes"),
            flush=True
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
            "[YTDLP_STREAM] extract_info SUCCESS",
            flush=True
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

        return info

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

            except Exception as error:

                print(
                    "[YTDLP_STREAM] Cookie remove ERROR:",
                    repr(error),
                    flush=True
                )


# ==========================================================
# MP4用フォーマット選択
#
# 可能なら映像+音声のMP4を選択。
#
# combinedが無い場合は
# video + audio の分離ストリームを選択。
# ==========================================================

def _select_mp4_format(info):

    formats = info.get(
        "formats"
    ) or []

    candidates = []

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

        # ==================================================
        # 映像 + 音声
        # ==================================================

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
    # combined MP4優先
    # ======================================================

    if candidates:

        candidates.sort(

            key=lambda item: (
                item["height"],
                item["filesize"]
            ),

            reverse=True

        )

        selected = candidates[0]["format"]

        print(
            "[YTDLP_STREAM] Selected combined MP4:",
            selected.get("format_id"),
            flush=True
        )

        print(
            "[YTDLP_STREAM] Resolution:",
            selected.get("width"),
            "x",
            selected.get("height"),
            flush=True
        )

        return selected

    # ======================================================
    # separate streams
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

        filesize = (
            fmt.get("filesize")
            or
            fmt.get("filesize_approx")
            or
            0
        )

        # --------------------------------------------------
        # 映像のみ
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 音声のみ
        # --------------------------------------------------

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
            fmt.get("fps") or 0,
            fmt.get("filesize") or
            fmt.get("filesize_approx") or
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
                fmt.get("filesize") or
                fmt.get("filesize_approx") or
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
        "[YTDLP_STREAM] Video resolution:",
        video_fmt.get("width"),
        "x",
        video_fmt.get("height"),
        flush=True
    )

    if audio_fmt:

        print(
            "[YTDLP_STREAM] Selected audio:",
            audio_fmt.get("format_id"),
            flush=True
        )

    else:

        print(
            "[YTDLP_STREAM] No separate audio stream",
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
# FFmpeg 単一URL
# ==========================================================

def _run_ffmpeg_single(
    input_url,
    output_path,
    start_seconds,
    end_seconds
):

    output_path = str(
        output_path
    )

    duration_seconds = (
        end_seconds
        -
        start_seconds
    )

    command = [

        FFMPEG_BINARY,

        "-hide_banner",

        "-loglevel",
        "warning",

        "-ss",
        str(start_seconds),

        "-i",
        input_url,

        "-t",
        str(
            max(
                0,
                duration_seconds
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

    ]

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
# FFmpeg video + audio
#
# URLを2本直接入力。
# 再エンコードなし。
# ==========================================================

def _run_ffmpeg_video_audio(
    video_url,
    audio_url,
    output_path,
    start_seconds,
    end_seconds
):

    output_path = str(
        output_path
    )

    duration_seconds = (
        end_seconds
        -
        start_seconds
    )

    command = [

        FFMPEG_BINARY,

        "-hide_banner",

        "-loglevel",
        "warning",

        # ==================================================
        # video
        # ==================================================

        "-ss",
        str(start_seconds),

        "-i",
        video_url,

        # ==================================================
        # audio
        # ==================================================

        "-ss",
        str(start_seconds),

        "-i",
        audio_url,

        # ==================================================
        # duration
        # ==================================================

        "-t",
        str(
            max(
                0,
                duration_seconds
            )
        ),

        # ==================================================
        # map
        # ==================================================

        "-map",
        "0:v:0",

        "-map",
        "1:a:0",

        # ==================================================
        # no re-encode
        # ==================================================

        "-c:v",
        "copy",

        "-c:a",
        "copy",

        "-movflags",
        "+faststart",

        "-y",

        output_path

    ]

    print(
        "[YTDLP_STREAM] FFmpeg video/audio command START",
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
# 時間指定なしの場合。
#
# Cookie + Deno + EJSを使用して
# yt-dlpが通常通りダウンロードする。
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

        _validate_deno()

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        info = None

        # --------------------------------------------------
        # まず情報取得
        # --------------------------------------------------

        opts = _base_ydl_opts(
            temporary_cookie_path
        )

        output_template = str(
            output_dir
            /
            "%(id)s.%(ext)s"
        )

        opts.update({

            "format":
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
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

        print(
            "[YTDLP_STREAM] URL:",
            url,
            flush=True
        )

        print(
            "[YTDLP_STREAM] Output:",
            output_template,
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
                    "YouTube動画情報を取得できませんでした。"
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

            prepared_path = Path(
                ydl.prepare_filename(
                    info
                )
            )

        # --------------------------------------------------
        # MP4
        # --------------------------------------------------

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

            matches = [

                path

                for path in matches

                if path.is_file()

                and
                path.suffix.lower()
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

                key=lambda path:
                    path.stat().st_mtime,

                reverse=True

            )

            final_path = matches[0]

        # --------------------------------------------------
        # 最終確認
        # --------------------------------------------------

        if not final_path.is_file():

            raise FileNotFoundError(
                "MP4完成ファイルが存在しません: "
                +
                str(final_path)
            )

        if final_path.stat().st_size <= 0:

            raise RuntimeError(
                "MP4ファイルサイズが0です。"
            )

        print(
            "[YTDLP_STREAM] Full MP4 COMPLETE:",
            final_path,
            flush=True
        )

        print(
            "[YTDLP_STREAM] File size:",
            final_path.stat().st_size,
            "bytes",
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

    except Exception as error:

        print(
            "[YTDLP_STREAM] create_mp4_full ERROR:",
            repr(error),
            flush=True
        )

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

            except Exception:

                pass


# ==========================================================
# MP4時間指定
#
# 重要：
#
# YouTube動画全体をローカルへ保存しない。
#
# yt-dlp:
#   情報取得
#   ↓
#   ストリームURL取得
#
# FFmpeg:
#   URLを直接入力
#   ↓
#   指定時間だけ取得
#   ↓
#   -c copy
#   ↓
#   再エンコードなし
#
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

    temporary_output = None

    try:

        # ==================================================
        # YouTube情報
        #
        # Cookie + Deno + EJS
        # ==================================================

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

        # ==================================================
        # 時間範囲チェック
        # ==================================================

        if duration is not None:

            try:

                duration_seconds = float(
                    duration
                )

                if start_seconds >= duration_seconds:

                    raise ValueError(
                        "開始時間が動画の長さを超えています。"
                    )

                if end_seconds > duration_seconds:

                    print(
                        "[YTDLP_STREAM] end_time adjusted:",
                        end_seconds,
                        "->",
                        duration_seconds,
                        flush=True
                    )

                    end_seconds = (
                        duration_seconds
                    )

                if end_seconds <= start_seconds:

                    raise ValueError(
                        "指定された時間範囲が動画の長さを超えています。"
                    )

            except ValueError:

                raise

            except Exception:

                pass

        # ==================================================
        # フォーマット
        # ==================================================

        selected = _select_mp4_format(
            info
        )

        # ==================================================
        # 出力ファイル
        # ==================================================

        temporary_name = (

            f".{video_id}_"
            f"{uuid.uuid4().hex}"
            ".mp4"

        )

        output_path = (
            output_dir
            /
            temporary_name
        )

        temporary_output = output_path

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
                "[YTDLP_STREAM] Direct combined MP4 stream:",
                selected.get("format_id"),
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
                    end_seconds

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

            # ------------------------------------------------
            # videoのみ
            # ------------------------------------------------

            if not audio_url:

                print(
                    "[YTDLP_STREAM] Direct video-only stream",
                    flush=True
                )

                _run_ffmpeg_single(

                    input_url=
                        video_url,

                    output_path=
                        output_path,

                    start_seconds=
                        start_seconds,

                    end_seconds=
                        end_seconds

                )

            # ------------------------------------------------
            # video + audio
            # ------------------------------------------------

            else:

                print(
                    "[YTDLP_STREAM] Direct video/audio streams",
                    flush=True
                )

                _run_ffmpeg_video_audio(

                    video_url=
                        video_url,

                    audio_url=
                        audio_url,

                    output_path=
                        output_path,

                    start_seconds=
                        start_seconds,

                    end_seconds=
                        end_seconds

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

        print(
            "[YTDLP_STREAM] File size:",
            output_path.stat().st_size,
            "bytes",
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

    except Exception as error:

        print(
            "[YTDLP_STREAM] create_mp4_range ERROR:",
            repr(error),
            flush=True
        )

        try:

            if (
                temporary_output
                and
                temporary_output.exists()
            ):

                temporary_output.unlink()

                print(
                    "[YTDLP_STREAM] Temporary output removed",
                    flush=True
                )

        except Exception:

            pass

        raise
