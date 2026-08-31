import os
import sys
import shutil
import subprocess
import tempfile
import traceback
from pathlib import Path

import yt_dlp


# ==========================================================
# DEBUG
# ==========================================================

print("==========================================", flush=True)
print("[STREAM] ytdlp_stream.py loaded", flush=True)
print("[STREAM] Python:", sys.version, flush=True)
print("[STREAM] Python executable:", sys.executable, flush=True)
print("[STREAM] Current working directory:", os.getcwd(), flush=True)


# ==========================================================
# Deno
# ==========================================================

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)

print(
    "[STREAM] DENO_PATH:",
    DENO_PATH,
    flush=True
)

print(
    "[STREAM] Deno exists:",
    os.path.isfile(DENO_PATH),
    flush=True
)


# ==========================================================
# 共通
# ==========================================================

def _prepare_cookie_file():

    cookies_source = "/etc/secrets/cookies.txt"

    print(
        "[STREAM] Cookie source:",
        cookies_source,
        flush=True
    )

    if not os.path.isfile(cookies_source):

        raise FileNotFoundError(
            f"Cookieファイルが見つかりません: {cookies_source}"
        )

    temporary_cookie = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        prefix="y2conv_stream_",
        delete=False
    )

    temporary_cookie_path = temporary_cookie.name

    temporary_cookie.close()

    shutil.copyfile(
        cookies_source,
        temporary_cookie_path
    )

    print(
        "[STREAM] Temporary cookie:",
        temporary_cookie_path,
        flush=True
    )

    return temporary_cookie_path


# ==========================================================
# 時間 → 秒
# ==========================================================

def _time_to_seconds(value):

    if value is None:
        return 0.0

    text = str(value).strip()

    if not text:
        return 0.0

    parts = text.split(":")

    if len(parts) == 3:

        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])

        return (
            hours * 3600
            + minutes * 60
            + seconds
        )

    if len(parts) == 2:

        minutes = float(parts[0])
        seconds = float(parts[1])

        return (
            minutes * 60
            + seconds
        )

    return float(text)


# ==========================================================
# 時間指定が実質的にあるか
#
# 00:00:00 ～ 00:00:00
# は「指定なし」として扱う
# ==========================================================

def _has_time_range(
    start_time,
    end_time
):

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    if (
        start_seconds == 0
        and
        end_seconds == 0
    ):

        return False

    return (
        start_time is not None
        or
        end_time is not None
    )


# ==========================================================
# yt-dlp共通設定
# ==========================================================

def _build_ydl_options(
    output_dir,
    temporary_cookie_path
):

    output_template = str(
        Path(output_dir) / "%(id)s.%(ext)s"
    )

    return {

        "outtmpl":
            output_template,

        # 映像＋音声
        "format":
            "bv*+ba/b",

        "noplaylist":
            True,

        "quiet":
            False,

        "no_warnings":
            False,

        "verbose":
            True,

        # ==================================================
        # YouTube JS challenge
        # ==================================================

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        "remote_components": {

            "ejs:github"

        },

        # ==================================================
        # Cookie
        # ==================================================

        "cookiefile":
            temporary_cookie_path,

        # ==================================================
        # MP4
        # ==================================================

        "merge_output_format":
            "mp4",

        # ==================================================
        # プレイリスト禁止
        # ==================================================

        "noplaylist":
            True

    }


# ==========================================================
# YouTube情報取得
# ==========================================================

def _extract_info(
    url,
    output_dir,
    cookie_path
):

    options = _build_ydl_options(
        output_dir,
        cookie_path
    )

    # 情報取得時はダウンロードしない
    options["skip_download"] = True

    with yt_dlp.YoutubeDL(
        options
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=False
        )

    if not info:

        raise RuntimeError(
            "YouTube情報を取得できませんでした"
        )

    return info


# ==========================================================
# MP4全体ダウンロード
#
# 時間指定なしの場合はこちら
# ==========================================================

def create_mp4_full(
    url,
    output_dir
):

    print(
        "[STREAM] create_mp4_full START",
        flush=True
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    cookie_path = None

    try:

        cookie_path = _prepare_cookie_file()

        options = _build_ydl_options(
            output_dir,
            cookie_path
        )

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            if not info:

                raise RuntimeError(
                    "MP4ダウンロード情報を取得できませんでした"
                )

            video_id = info.get("id")

            title = (
                info.get("title")
                or "YouTube Video"
            )

            # ------------------------------------------------
            # yt-dlpが作成したファイルを探す
            # ------------------------------------------------

            expected = None

            try:

                prepared = ydl.prepare_filename(
                    info
                )

                prepared_path = Path(
                    prepared
                )

                if prepared_path.exists():

                    expected = prepared_path

            except Exception:

                pass

            # ------------------------------------------------
            # video IDで探す
            # ------------------------------------------------

            if expected is None and video_id:

                mp4_candidate = (
                    output_dir
                    /
                    f"{video_id}.mp4"
                )

                if mp4_candidate.exists():

                    expected = mp4_candidate

            # ------------------------------------------------
            # 最終検索
            # ------------------------------------------------

            if expected is None and video_id:

                candidates = list(
                    output_dir.glob(
                        f"{video_id}.*"
                    )
                )

                candidates = [

                    p

                    for p in candidates

                    if p.is_file()
                    and p.suffix.lower()
                    not in (
                        ".part",
                        ".ytdl",
                        ".temp"
                    )

                ]

                if candidates:

                    candidates.sort(
                        key=lambda p: p.stat().st_mtime,
                        reverse=True
                    )

                    expected = candidates[0]

            if expected is None:

                raise FileNotFoundError(
                    "MP4ファイルを確認できませんでした"
                )

            if expected.stat().st_size <= 0:

                raise RuntimeError(
                    "MP4ファイルのサイズが0です"
                )

            return {

                "path":
                    str(expected),

                "filename":
                    expected.name,

                "video_id":
                    video_id,

                "title":
                    title

            }

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
# MP4指定時間抽出
#
# 重要：
# YouTube動画全体をPythonのメモリには載せない。
#
# yt-dlpで一旦ディスクへ保存し、
# ffmpegで指定区間だけ処理する。
#
# ==========================================================

def create_mp4_range(
    url,
    output_dir,
    start_time,
    end_time
):

    print(
        "[STREAM] create_mp4_range START",
        flush=True
    )

    print(
        "[STREAM] start_time:",
        start_time,
        flush=True
    )

    print(
        "[STREAM] end_time:",
        end_time,
        flush=True
    )

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

    if end_seconds <= start_seconds:

        raise ValueError(
            "終了時間は開始時間より後にしてください。"
        )

    duration = (
        end_seconds
        - start_seconds
    )

    cookie_path = None

    try:

        cookie_path = _prepare_cookie_file()

        # ==================================================
        # 一時ディレクトリ
        #
        # メモリではなくディスクを使用
        # ==================================================

        with tempfile.TemporaryDirectory(
            prefix="y2conv_mp4_"
        ) as temp_dir:

            temp_dir = Path(
                temp_dir
            )

            print(
                "[STREAM] temporary directory:",
                temp_dir,
                flush=True
            )

            # ==================================================
            # YouTube → 一時ファイル
            # ==================================================

            options = _build_ydl_options(
                temp_dir,
                cookie_path
            )

            with yt_dlp.YoutubeDL(
                options
            ) as ydl:

                info = ydl.extract_info(
                    url,
                    download=True
                )

                if not info:

                    raise RuntimeError(
                        "YouTube動画を取得できませんでした"
                    )

                video_id = info.get(
                    "id"
                )

                title = (
                    info.get("title")
                    or "YouTube Video"
                )

                # ------------------------------------------------
                # ダウンロードファイル確認
                # ------------------------------------------------

                source_file = None

                try:

                    prepared = ydl.prepare_filename(
                        info
                    )

                    prepared_path = Path(
                        prepared
                    )

                    if prepared_path.exists():

                        source_file = (
                            prepared_path
                        )

                except Exception:

                    pass

                if source_file is None and video_id:

                    candidates = list(
                        temp_dir.glob(
                            f"{video_id}.*"
                        )
                    )

                    candidates = [

                        p

                        for p in candidates

                        if p.is_file()
                        and p.suffix.lower()
                        not in (
                            ".part",
                            ".ytdl",
                            ".temp"
                        )

                    ]

                    if candidates:

                        candidates.sort(
                            key=lambda p: p.stat().st_mtime,
                            reverse=True
                        )

                        source_file = candidates[0]

                if source_file is None:

                    raise FileNotFoundError(
                        "一時MP4ファイルを確認できませんでした"
                    )

                print(
                    "[STREAM] source:",
                    source_file,
                    flush=True
                )

            # ==================================================
            # 出力ファイル
            # ==================================================

            if video_id:

                output_file = (
                    output_dir
                    /
                    f"{video_id}.mp4"
                )

            else:

                output_file = (
                    output_dir
                    /
                    "video.mp4"
                )

            temp_output = (
                temp_dir
                /
                "converted.mp4"
            )

            # ==================================================
            # FFmpeg
            #
            # -ss を入力前に置いて不要な区間を極力読まない
            # ==================================================

            ffmpeg_command = [

                "ffmpeg",

                "-y",

                "-ss",
                str(start_seconds),

                "-i",
                str(source_file),

                "-t",
                str(duration),

                # ------------------------------------------------
                # メモリ使用を抑えやすい設定
                # ------------------------------------------------

                "-c:v",
                "libx264",

                "-preset",
                "veryfast",

                "-crf",
                "23",

                "-c:a",
                "aac",

                "-b:a",
                "128k",

                "-movflags",
                "+faststart",

                "-metadata",
                "title=" + str(title),

                "-metadata",
                "comment=YouTube Converter",

                str(temp_output)

            ]

            print(
                "[STREAM] FFmpeg:",
                " ".join(
                    ffmpeg_command
                ),
                flush=True
            )

            result = subprocess.run(
                ffmpeg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            print(
                "[STREAM] FFmpeg returncode:",
                result.returncode,
                flush=True
            )

            if result.returncode != 0:

                print(
                    "[STREAM] FFmpeg stderr:",
                    result.stderr,
                    flush=True
                )

                raise RuntimeError(
                    "FFmpeg指定時間変換に失敗しました\n"
                    + result.stderr
                )

            if not temp_output.exists():

                raise FileNotFoundError(
                    "FFmpeg出力ファイルがありません"
                )

            if temp_output.stat().st_size <= 0:

                raise RuntimeError(
                    "FFmpeg出力ファイルのサイズが0です"
                )

            # ==================================================
            # 完成ファイルへ移動
            # ==================================================

            if output_file.exists():

                output_file.unlink()

            shutil.move(
                str(temp_output),
                str(output_file)
            )

            print(
                "[STREAM] MP4完成:",
                output_file,
                flush=True
            )

            return {

                "path":
                    str(output_file),

                "filename":
                    output_file.name,

                "video_id":
                    video_id,

                "title":
                    title

            }

    except Exception as error:

        print(
            "[STREAM] create_mp4_range ERROR:",
            repr(error),
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
# メイン関数
#
# 00:00:00 ～ 00:00:00
# → 全体ダウンロード
#
# 時間指定あり
# → 指定区間抽出
# ==========================================================

def create_mp4_memory_safe(
    url,
    output_dir,
    start_time=None,
    end_time=None
):

    start_seconds = _time_to_seconds(
        start_time
    )

    end_seconds = _time_to_seconds(
        end_time
    )

    # ======================================================
    # 00:00:00 ～ 00:00:00
    # ======================================================

    if (
        start_seconds == 0
        and
        end_seconds == 0
    ):

        print(
            "[STREAM] 時間指定なし → 全体ダウンロード",
            flush=True
        )

        return create_mp4_full(
            url,
            output_dir
        )

    # ======================================================
    # 片方だけ0の場合
    # ======================================================

    if end_seconds <= start_seconds:

        raise ValueError(
            "終了時間は開始時間より後にしてください。"
        )

    return create_mp4_range(

        url,

        output_dir,

        start_time,

        end_time

    )
