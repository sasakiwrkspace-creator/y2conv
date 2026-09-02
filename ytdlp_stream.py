import os
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
# yt-dlp 共通オプション
# ==========================================================

def _base_ydl_opts():

    return {

        "quiet":
            True,

        "no_warnings":
            True,

        "noprogress":
            True,

        "noplaylist":
            True,

        "extractor_args": {

            "youtube": {

                "player_client": [
                    "web"
                ]

            }

        }

    }


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
# ==========================================================

def _extract_info(url):

    opts = _base_ydl_opts()

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


# ==========================================================
# MP4用フォーマット選択
#
# 可能なら映像+音声のMP4を選択。
#
# 時間指定時はFFmpegへURLを渡すため、
# yt-dlpによる実ファイルのダウンロードは行わない。
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

        # ----------------------------------------------
        # 映像+音声
        # ----------------------------------------------

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

    # ==================================================
    # combined MP4を優先
    # ==================================================

    if candidates:

        candidates.sort(

            key=lambda item: (

                item["height"],

                item["filesize"]

            ),

            reverse=True

        )

        return candidates[0]["format"]

    # ==================================================
    # combinedがない場合
    #
    # 映像+音声の分離ストリームを返す。
    # この場合は後段でFFmpegがmuxする。
    # 再エンコードはしない。
    # ==================================================

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

    return {

        "_separate":
            True,

        "video":
            video_fmt,

        "audio":
            audio_fmt

    }


# ==========================================================
# FFmpeg実行
# ==========================================================

def _run_ffmpeg(
    input_url,
    output_path,
    start_seconds,
    end_seconds
):

    output_path = str(
        output_path
    )

    # ======================================================
    # -ss を入力側に置く
    #
    # できるだけ早く指定位置へシークする。
    #
    # -c copy
    #
    # 再エンコードしない。
    # ======================================================

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
                end_seconds - start_seconds
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
# MP4全体ダウンロード
#
# 時間指定なしの場合はこちら。
# yt-dlpが通常通りファイルを保存する。
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

    output_template = str(
        output_dir
        /
        (
            "%(id)s.%(ext)s"
        )
    )

    opts = _base_ydl_opts()

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

    # ------------------------------------------------------
    # merge後に .mp4 になっている場合
    # ------------------------------------------------------

    mp4_path = prepared_path.with_suffix(
        ".mp4"
    )

    if mp4_path.is_file():

        final_path = mp4_path

    elif prepared_path.is_file():

        final_path = prepared_path

    else:

        # --------------------------------------------------
        # 念のためidベースで検索
        # --------------------------------------------------

        matches = list(
            output_dir.glob(
                f"{video_id}.*"
            )
        )

        if not matches:

            raise FileNotFoundError(
                "MP4ダウンロード後のファイルが見つかりません。"
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

    # ======================================================
    # YouTube情報
    # ======================================================

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

    # ======================================================
    # フォーマット
    # ======================================================

    selected = _select_mp4_format(
        info
    )

    # ======================================================
    # 出力ファイル
    # ======================================================

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

    try:

        # ==================================================
        # combined MP4
        #
        # URLを直接FFmpegへ渡す。
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
                "[YTDLP_STREAM] Direct MP4 stream:",
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
                    end_seconds

            )

        # ==================================================
        # video + audio separate
        #
        # それぞれのURLをFFmpegへ直接入力。
        #
        # muxのみ。
        # 映像・音声の再エンコードはしない。
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
            # audioなし
            # ------------------------------------------------

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
                        end_seconds

                )

            # ------------------------------------------------
            # video + audio
            #
            # FFmpegへ2つのURLを直接入力。
            # ------------------------------------------------

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
                    str(start_seconds),

                    "-i",
                    video_url,

                    "-ss",
                    str(start_seconds),

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

                ]

                print(
                    "[YTDLP_STREAM] Direct video/audio stream",
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

    except Exception:

        # --------------------------------------------------
        # エラー時の一時ファイル削除
        # --------------------------------------------------

        try:

            if output_path.exists():

                output_path.unlink()

        except Exception:

            pass

        raise
