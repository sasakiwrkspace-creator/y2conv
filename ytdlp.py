import os
import yt_dlp

from config import DOWNLOAD_DIR


def create_mp3(
    url,
    start_time=None,
    end_time=None
):
    """
    YouTube URLからMP3を作成する。
    """

    if not url:
        raise ValueError(
            "YouTube URLが指定されていません。"
        )

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True
    )

    print("==========================================")
    print("[YTDLP] MP3作成開始")
    print("[YTDLP] URL:", url)
    print("[YTDLP] start_time:", start_time)
    print("[YTDLP] end_time:", end_time)
    print("[YTDLP] DOWNLOAD_DIR:", DOWNLOAD_DIR)
    print("==========================================")

    ydl_opts = {
        "format": "bestaudio/best",

        "outtmpl": os.path.join(
            DOWNLOAD_DIR,
            "%(title)s.%(ext)s"
        ),

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }
        ],

        "quiet": False,
        "no_warnings": False,
        "overwrites": True
    }

    # =====================================
    # 時間範囲
    # =====================================

    if start_time or end_time:

        start = (
            start_time
            if start_time
            else "00:00:00"
        )

        end = (
            end_time
            if end_time
            else "inf"
        )

        ydl_opts["download_sections"] = [
            f"*{start}-{end}"
        ]

        ydl_opts[
            "force_keyframes_at_cuts"
        ] = True

    # =====================================
    # yt-dlp実行
    # =====================================

    try:

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            title = info.get(
                "title",
                "output"
            )

            print(
                "[YTDLP] title:",
                title
            )

    except Exception as error:

        print(
            "[YTDLP] MP3作成エラー:",
            error
        )

        raise

    # =====================================
    # MP3確認
    # =====================================

    mp3_files = []

    for filename in os.listdir(
        DOWNLOAD_DIR
    ):

        if filename.lower().endswith(
            ".mp3"
        ):

            mp3_files.append(
                filename
            )

    if not mp3_files:

        raise RuntimeError(
            "MP3ファイルが作成されませんでした。"
        )

    # =====================================
    # 最新MP3を取得
    # =====================================

    mp3_files.sort(
        key=lambda filename:
            os.path.getmtime(
                os.path.join(
                    DOWNLOAD_DIR,
                    filename
                )
            ),
        reverse=True
    )

    filename = mp3_files[0]

    filepath = os.path.join(
        DOWNLOAD_DIR,
        filename
    )

    if not os.path.isfile(
        filepath
    ):

        raise RuntimeError(
            "MP3ファイルの確認に失敗しました。"
        )

    print("==========================================")
    print("[YTDLP] MP3作成完了")
    print("[YTDLP] filename:", filename)
    print("[YTDLP] path:", filepath)
    print(
        "[YTDLP] size:",
        os.path.getsize(filepath),
        "bytes"
    )
    print("==========================================")

    return {
        "success": True,
        "filename": filename,
        "path": filepath
    }
