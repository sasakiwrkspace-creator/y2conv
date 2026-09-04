import sys
import os
import traceback
import shutil
import subprocess
import tempfile
import re

from pathlib import Path


# ==========================================================
# 起動時 DEBUG
# ==========================================================

print(
    "==========================================",
    flush=True
)

print(
    "[DEBUG] ytdlp.py loaded",
    flush=True
)

print(
    "[DEBUG] Python:",
    sys.version,
    flush=True
)

print(
    "[DEBUG] Python executable:",
    sys.executable,
    flush=True
)

print(
    "[DEBUG] Current working directory:",
    os.getcwd(),
    flush=True
)

print(
    "[DEBUG] yt-dlp module loading...",
    flush=True
)


# ==========================================================
# Deno PATH
# ==========================================================

DENO_PATH = os.environ.get(
    "DENO_PATH",
    "/app/.deno/bin/deno"
)

print(
    "[DEBUG] DENO_PATH:",
    DENO_PATH,
    flush=True
)

print(
    "[DEBUG] PATH:",
    os.environ.get("PATH"),
    flush=True
)


# ==========================================================
# Cookie
# ==========================================================

COOKIES_SOURCE = "/etc/secrets/cookies.txt"


# ==========================================================
# yt-dlp import
# ==========================================================

try:

    import yt_dlp

    print(
        "[DEBUG] yt_dlp imported",
        flush=True
    )

    print(
        "[DEBUG] yt_dlp version:",
        yt_dlp.version.__version__,
        flush=True
    )

    print(
        "[DEBUG] yt_dlp location:",
        yt_dlp.__file__,
        flush=True
    )

except Exception as e:

    print(
        "[DEBUG] yt_dlp import ERROR:",
        repr(e),
        flush=True
    )

    traceback.print_exc()

    raise


# ==========================================================
# yt-dlp-ejs確認
# ==========================================================

try:

    import yt_dlp_ejs

    print(
        "[DEBUG] yt_dlp_ejs imported",
        flush=True
    )

    print(
        "[DEBUG] yt_dlp_ejs location:",
        yt_dlp_ejs.__file__,
        flush=True
    )

except Exception as e:

    print(
        "[DEBUG] yt_dlp_ejs import ERROR:",
        repr(e),
        flush=True
    )

    traceback.print_exc()


# ==========================================================
# Deno確認
# ==========================================================

print(
    "[DEBUG] Deno configured path:",
    DENO_PATH,
    flush=True
)

print(
    "[DEBUG] Deno exists:",
    os.path.isfile(DENO_PATH),
    flush=True
)

print(
    "[DEBUG] Deno executable:",
    os.access(
        DENO_PATH,
        os.X_OK
    ),
    flush=True
)

print(
    "[DEBUG] Deno which:",
    shutil.which("deno"),
    flush=True
)


if os.path.isfile(DENO_PATH):

    try:

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
            "[DEBUG] deno returncode:",
            result.returncode,
            flush=True
        )

        print(
            "[DEBUG] deno stdout:",
            result.stdout,
            flush=True
        )

        print(
            "[DEBUG] deno stderr:",
            result.stderr,
            flush=True
        )

    except Exception as e:

        print(
            "[DEBUG] deno execution ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

else:

    print(
        "[DEBUG] Deno NOT FOUND:",
        DENO_PATH,
        flush=True
    )


# ==========================================================
# FFmpeg確認
# ==========================================================

print(
    "[DEBUG] ffmpeg path:",
    shutil.which("ffmpeg"),
    flush=True
)

print(
    "[DEBUG] ffprobe path:",
    shutil.which("ffprobe"),
    flush=True
)


try:

    result = subprocess.run(

        [
            "ffmpeg",
            "-version"
        ],

        capture_output=True,

        text=True,

        timeout=10

    )

    print(
        "[DEBUG] ffmpeg returncode:",
        result.returncode,
        flush=True
    )

    if result.stdout:

        print(
            "[DEBUG] ffmpeg version:",
            result.stdout.splitlines()[0],
            flush=True
        )

except Exception as e:

    print(
        "[DEBUG] ffmpeg execution ERROR:",
        repr(e),
        flush=True
    )


print(
    "==========================================",
    flush=True
)


# ==========================================================
# downloadsフォルダ
# ==========================================================

def _get_download_dir():

    download_dir = (
        Path(os.getcwd())
        /
        "downloads"
    )

    download_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return download_dir


# ==========================================================
# ファイル名安全化
# ==========================================================

def _sanitize_filename(title):

    if not title:

        title = "YouTube Video"

    title = str(
        title
    ).strip()

    title = re.sub(
        r"[\r\n\t]+",
        " ",
        title
    )

    title = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        title
    )

    title = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    title = title.rstrip(
        " ."
    )

    if not title:

        title = "YouTube Video"

    title = title[:180]

    title = title.rstrip(
        " ."
    )

    if not title:

        title = "YouTube Video"

    return title


# ==========================================================
# Cookie準備
# ==========================================================

def _prepare_cookie_file():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[DEBUG] Cookieファイル準備開始",
        flush=True
    )

    print(
        "[DEBUG] 元Cookieファイル:",
        COOKIES_SOURCE,
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
            "[DEBUG] 元Cookieサイズ:",
            source_size,
            "bytes",
            flush=True
        )

        temporary_cookie_file = (
            tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                prefix="y2conv_cookies_",
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
            "[DEBUG] 一時Cookie:",
            temporary_cookie_path,
            flush=True
        )

        return temporary_cookie_path

    except Exception as e:

        print(
            "[DEBUG] Cookie preparation ERROR:",
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

    finally:

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# yt-dlpオプション
# ==========================================================

def _build_ydl_options(
    output_dir,
    format_string,
    temporary_cookie_path=None
):

    download_template = str(
        Path(output_dir)
        /
        "%(id)s.%(ext)s"
    )

    ydl_opts = {

        # ----------------------------------------------
        # 出力先
        # ----------------------------------------------

        "outtmpl":
            download_template,

        # ----------------------------------------------
        # フォーマット
        # ----------------------------------------------

        "format":
            format_string,

        # ----------------------------------------------
        # プレイリスト禁止
        # ----------------------------------------------

        "noplaylist":
            True,

        # ----------------------------------------------
        # ログ
        # ----------------------------------------------

        "quiet":
            False,

        "no_warnings":
            False,

        "verbose":
            True,

        # ----------------------------------------------
        # Deno
        # ----------------------------------------------

        "js_runtimes": {

            "deno": {

                "path":
                    DENO_PATH

            }

        },

        # ----------------------------------------------
        # EJS
        # ----------------------------------------------

        "remote_components": {

            "ejs:github"

        }

    }

    # ======================================================
    # Cookie
    # ======================================================

    if temporary_cookie_path:

        ydl_opts[
            "cookiefile"
        ] = temporary_cookie_path


    # ======================================================
    # DEBUG
    # ======================================================

    print(
        "[DEBUG] yt-dlp format:",
        format_string,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp output:",
        download_template,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp Deno:",
        DENO_PATH,
        flush=True
    )

    print(
        "[DEBUG] yt-dlp cookie:",
        temporary_cookie_path,
        flush=True
    )

    return ydl_opts


# ==========================================================
# YouTube情報取得
# ==========================================================

def get_youtube_info(
    url
):

    temporary_cookie_path = None

    try:

        if not url:

            raise ValueError(
                "YouTube URLが空です"
            )

        temporary_cookie_path = (
            _prepare_cookie_file()
        )

        ydl_opts = _build_ydl_options(

            output_dir=
                _get_download_dir(),

            format_string=
                "bestaudio/best",

            temporary_cookie_path=
                temporary_cookie_path

        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        if not info:

            raise RuntimeError(
                "YouTube情報を取得できませんでした"
            )

        print(
            "[INFO] Video ID:",
            info.get("id"),
            flush=True
        )

        print(
            "[INFO] Title:",
            info.get("title"),
            flush=True
        )

        print(
            "[INFO] Duration:",
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

            except Exception:

                pass


# ==========================================================
# ダウンロード済み完成ファイル検索
#
# yt-dlpのprepare_filename()だけに依存しない。
#
# 最終的に実際に存在するファイルを探す。
# ==========================================================

def _find_downloaded_file(
    output_dir,
    video_id,
    preferred_path=None,
    preferred_extension=None
):

    output_dir = Path(
        output_dir
    )

    print(
        "[DEBUG] Searching downloaded file",
        flush=True
    )

    print(
        "[DEBUG] output_dir:",
        output_dir,
        flush=True
    )

    print(
        "[DEBUG] video_id:",
        video_id,
        flush=True
    )

    print(
        "[DEBUG] preferred_path:",
        preferred_path,
        flush=True
    )

    print(
        "[DEBUG] preferred_extension:",
        preferred_extension,
        flush=True
    )


    # ======================================================
    # 1. preferred_path
    # ======================================================

    if preferred_path:

        preferred = Path(
            preferred_path
        )

        if (
            preferred.is_file()
            and
            preferred.stat().st_size > 0
        ):

            print(
                "[DEBUG] Found preferred file:",
                preferred,
                flush=True
            )

            return preferred


    # ======================================================
    # 2. video_id.mp4
    #
    # MP4結合後はこちらを最優先。
    # ======================================================

    if video_id:

        mp4_path = (

            output_dir
            /
            f"{video_id}.mp4"

        )

        if (
            mp4_path.is_file()
            and
            mp4_path.stat().st_size > 0
        ):

            print(
                "[DEBUG] Found merged MP4:",
                mp4_path,
                flush=True
            )

            return mp4_path


    # ======================================================
    # 3. 指定拡張子
    # ======================================================

    if video_id and preferred_extension:

        extension = (
            str(
                preferred_extension
            )
            .lower()
            .lstrip(".")
        )

        preferred = (

            output_dir
            /
            f"{video_id}.{extension}"

        )

        if (
            preferred.is_file()
            and
            preferred.stat().st_size > 0
        ):

            print(
                "[DEBUG] Found extension file:",
                preferred,
                flush=True
            )

            return preferred


    # ======================================================
    # 4. video_id.* 全検索
    # ======================================================

    if video_id:

        matches = []

        for path in output_dir.glob(
            f"{video_id}.*"
        ):

            if not path.is_file():

                continue

            if path.suffix.lower() in (

                ".part",
                ".ytdl",
                ".temp",
                ".tmp"

            ):

                continue

            try:

                size = path.stat().st_size

            except Exception:

                continue

            if size <= 0:

                continue

            matches.append(
                path
            )


        if matches:

            # MP4を優先
            matches.sort(

                key=lambda p: (

                    0
                    if p.suffix.lower() == ".mp4"
                    else 1,

                    -p.stat().st_mtime

                )

            )

            selected = matches[0]

            print(
                "[DEBUG] Found downloaded file:",
                selected,
                flush=True
            )

            return selected


    # ======================================================
    # 5. 見つからない
    # ======================================================

    print(
        "[DEBUG] No downloaded file found",
        flush=True
    )

    return None


# ==========================================================
# sourceファイルをFFprobeで検証
#
# ここで「ダウンロードは成功したが再生できない」
# ファイルを検出する。
# ==========================================================

def _probe_source_file(
    path
):

    path = Path(
        path
    )

    ffprobe_path = shutil.which(
        "ffprobe"
    )

    if not ffprobe_path:

        print(
            "[DEBUG] ffprobe not found. "
            "source検証をスキップします。",
            flush=True
        )

        return True


    command = [

        ffprobe_path,

        "-v",
        "error",

        "-show_entries",
        "format=format_name,duration,size",

        "-show_entries",
        "stream=index,codec_type,codec_name,width,height,duration",

        "-of",
        "json",

        str(path)

    ]


    print(
        "[DEBUG] Source FFprobe:",
        " ".join(command),
        flush=True
    )


    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=60

        )

    except Exception as e:

        print(
            "[DEBUG] Source FFprobe ERROR:",
            repr(e),
            flush=True
        )

        raise RuntimeError(
            "sourceファイルのFFprobe検証に失敗しました。"
        ) from e


    print(
        "[DEBUG] Source FFprobe returncode:",
        result.returncode,
        flush=True
    )


    if result.stdout:

        print(
            "[DEBUG] Source FFprobe stdout:",
            result.stdout,
            flush=True
        )


    if result.stderr:

        print(
            "[DEBUG] Source FFprobe stderr:",
            result.stderr,
            flush=True
        )


    if result.returncode != 0:

        raise RuntimeError(

            "ダウンロードされたsourceファイルを"
            "FFprobeで読み込めません。\n"
            +
            result.stderr[-5000:]

        )


    return True


# ==========================================================
# YouTube → source
#
# 重要:
#
# 動画 + 音声を取得してMP4へ結合する。
#
# 以前:
#
#     best
#
# 今回:
#
#     bv*+ba/b
#
# さらに:
#
#     merge_output_format = mp4
#
# ==========================================================

def download_source(
    url
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[DEBUG] download_source START",
        flush=True
    )

    print(
        "[DEBUG] URL:",
        url,
        flush=True
    )


    if not url:

        raise ValueError(
            "YouTube URLが空です"
        )


    output_dir = _get_download_dir()

    temporary_cookie_path = None


    try:

        # ==================================================
        # Cookie
        # ==================================================

        temporary_cookie_path = (
            _prepare_cookie_file()
        )


        # ==================================================
        # yt-dlp
        #
        # 動画＋音声
        # ==================================================

        ydl_opts = _build_ydl_options(

            output_dir=
                output_dir,

            format_string=
                "bv*+ba/b",

            temporary_cookie_path=
                temporary_cookie_path

        )


        # ==================================================
        # MP4へマージ
        # ==================================================

        ydl_opts[
            "merge_output_format"
        ] = "mp4"


        print(
            "[DEBUG] merge_output_format: mp4",
            flush=True
        )


        info = None

        expected_filename = None


        # ==================================================
        # yt-dlp実行
        # ==================================================

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            # ----------------------------------------------
            # 情報取得
            # ----------------------------------------------

            info = ydl.extract_info(

                url,

                download=False

            )


            if info is None:

                raise RuntimeError(
                    "YouTube情報を取得できませんでした"
                )


            print(
                "[DEBUG] source video id:",
                info.get("id"),
                flush=True
            )


            print(
                "[DEBUG] source title:",
                info.get("title"),
                flush=True
            )


            print(
                "[DEBUG] source duration:",
                info.get("duration"),
                flush=True
            )


            print(
                "[DEBUG] source selected format:",
                info.get("format"),
                flush=True
            )


            print(
                "[DEBUG] source format_id:",
                info.get("format_id"),
                flush=True
            )


            # ----------------------------------------------
            # prepare filename
            # ----------------------------------------------

            expected_filename = (
                ydl.prepare_filename(
                    info
                )
            )


            print(
                "[DEBUG] expected filename:",
                expected_filename,
                flush=True
            )


            # ----------------------------------------------
            # ダウンロード
            # ----------------------------------------------

            print(
                "[DEBUG] download_source download START",
                flush=True
            )


            download_result = ydl.download([

                url

            ])


            print(
                "[DEBUG] yt-dlp download return:",
                download_result,
                flush=True
            )


            print(
                "[DEBUG] download_source download SUCCESS",
                flush=True
            )


        # ==================================================
        # Video ID
        # ==================================================

        video_id = info.get(
            "id"
        )


        if not video_id:

            raise RuntimeError(
                "YouTube video IDを取得できませんでした"
            )


        # ==================================================
        # 完成ファイル検索
        # ==================================================

        downloaded_file = _find_downloaded_file(

            output_dir=
                output_dir,

            video_id=
                video_id,

            preferred_path=
                expected_filename,

            preferred_extension=
                "mp4"

        )


        # ==================================================
        # ファイルがない
        # ==================================================

        if downloaded_file is None:

            print(
                "[DEBUG] downloads directory contents:",
                flush=True
            )

            try:

                for path in sorted(
                    output_dir.iterdir()
                ):

                    print(
                        "[DEBUG]   ",
                        path,
                        flush=True
                    )

            except Exception:

                pass


            raise FileNotFoundError(

                "ダウンロードしたsourceファイルを"
                "確認できませんでした"

            )


        # ==================================================
        # ファイルサイズ
        # ==================================================

        file_size = (

            downloaded_file.stat().st_size

        )


        print(
            "[DEBUG] Downloaded source:",
            downloaded_file,
            flush=True
        )


        print(
            "[DEBUG] Downloaded source size:",
            file_size,
            "bytes",
            flush=True
        )


        if file_size <= 0:

            raise RuntimeError(
                "sourceファイルのサイズが0です"
            )


        # ==================================================
        # sourceファイルをFFprobe検証
        # ==================================================

        _probe_source_file(
            downloaded_file
        )


        # ==================================================
        # MP4でない場合の注意
        # ==================================================

        if downloaded_file.suffix.lower() != ".mp4":

            print(
                "[DEBUG] WARNING: "
                "sourceファイルはMP4ではありません:",
                downloaded_file,
                flush=True
            )


        # ==================================================
        # 戻り値
        # ==================================================

        result = {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "title":
                info.get("title")
                or "YouTube Video",

            "duration":
                info.get("duration"),

            "video_id":
                video_id,

            "info":
                info

        }


        print(
            "[DEBUG] download_source RESULT:",
            result,
            flush=True
        )


        return result


    except Exception as e:

        print(
            "[DEBUG] download_source ERROR:",
            repr(e),
            flush=True
        )

        traceback.print_exc()

        raise


    finally:

        # ==================================================
        # Cookie削除
        # ==================================================

        if temporary_cookie_path:

            try:

                if os.path.exists(
                    temporary_cookie_path
                ):

                    os.remove(
                        temporary_cookie_path
                    )

                    print(
                        "[DEBUG] temporary cookie removed:",
                        temporary_cookie_path,
                        flush=True
                    )

            except Exception as e:

                print(
                    "[DEBUG] temporary cookie remove ERROR:",
                    repr(e),
                    flush=True
                )


        print(
            "[DEBUG] download_source END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# source削除
# ==========================================================

def cleanup_download(
    download_result
):

    if not download_result:

        return


    source_path = (

        download_result.get("path")

        if isinstance(
            download_result,
            dict
        )

        else None

    )


    if not source_path:

        return


    try:

        path = Path(
            source_path
        )


        if (
            path.exists()
            and
            path.is_file()
        ):

            path.unlink()


            print(
                "[DEBUG] source removed:",
                path,
                flush=True
            )


    except Exception as e:

        print(
            "[DEBUG] cleanup_download ERROR:",
            repr(e),
            flush=True
        )


# ==========================================================
# 後方互換
#
# 他のコードから呼ばれている可能性があるため残す。
# ==========================================================

def _download_with_ytdlp(
    url,
    output_dir,
    format_string,
    merge_output_format=None,
    mode_name="UNKNOWN"
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


        ydl_opts = _build_ydl_options(

            output_dir=
                output_dir,

            format_string=
                format_string,

            temporary_cookie_path=
                temporary_cookie_path

        )


        if merge_output_format:

            ydl_opts[
                "merge_output_format"
            ] = merge_output_format


        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(

                url,

                download=True

            )


            if not info:

                raise RuntimeError(

                    f"{mode_name} "
                    "extract_info() returned None"

                )


            prepared_filename = (
                ydl.prepare_filename(
                    info
                )
            )


        # ==================================================
        # 完成ファイル検索
        # ==================================================

        downloaded_file = _find_downloaded_file(

            output_dir=
                output_dir,

            video_id=
                info.get("id"),

            preferred_path=
                prepared_filename,

            preferred_extension=
                merge_output_format

        )


        if downloaded_file is None:

            raise FileNotFoundError(

                f"{mode_name} "
                "ダウンロードファイルが見つかりません"

            )


        # ==================================================
        # サイズ
        # ==================================================

        if downloaded_file.stat().st_size <= 0:

            raise RuntimeError(

                f"{mode_name} "
                "ファイルサイズが0です"

            )


        # ==================================================
        # FFprobe
        # ==================================================

        _probe_source_file(
            downloaded_file
        )


        # ==================================================
        # 戻り値
        # ==================================================

        return {

            "path":
                str(downloaded_file),

            "filename":
                downloaded_file.name,

            "video_id":
                info.get("id"),

            "title":
                info.get("title")
                or "YouTube Video",

            "duration":
                info.get("duration"),

            "info":
                info

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
