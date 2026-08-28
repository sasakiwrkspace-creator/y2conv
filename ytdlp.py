# =====================================
# YouTube Converter
# ytdlp.py
#
# YouTube → MP3変換
# =====================================

import os

import yt_dlp

from config import (
    DOWNLOAD_DIR,
    COOKIES_FILE
)


# =====================================
# MP3作成
# =====================================

def create_mp3(
    url,
    start_time=None,
    end_time=None
):
    """
    YouTube URLからMP3を作成する。
    """

    # =================================
    # URL確認
    # =================================

    if not url:

        raise ValueError(
            "YouTube URLが指定されていません。"
        )


    # =================================
    # downloads確認
    # =================================

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True
    )


    # =================================
    # 開始ログ
    # =================================

    print("==========================================")

    print(
        "[YTDLP] MP3作成開始"
    )

    print(
        "[YTDLP] URL:",
        url
    )

    print(
        "[YTDLP] start_time:",
        start_time
    )

    print(
        "[YTDLP] end_time:",
        end_time
    )

    print(
        "[YTDLP] DOWNLOAD_DIR:",
        DOWNLOAD_DIR
    )

    print(
        "[YTDLP] COOKIES_FILE:",
        COOKIES_FILE
    )

    print(
        "[YTDLP] cookies exists:",
        os.path.isfile(
            COOKIES_FILE
        )
    )

    print("==========================================")


    # =====================================
    # yt-dlp設定
    # =====================================

    ydl_opts = {

        "format":
            "bestaudio/best",

        "outtmpl":
            os.path.join(
                DOWNLOAD_DIR,
                "%(title)s.%(ext)s"
            ),

        "cookiefile":
            COOKIES_FILE,

        "postprocessors": [

            {
                "key":
                    "FFmpegExtractAudio",

                "preferredcodec":
                    "mp3",

                "preferredquality":
                    "192"
            }

        ],

        "quiet":
            False,

        "no_warnings":
            False,

        "overwrites":
            True
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


        ydl_opts[
            "download_sections"
        ] = [

            f"*{start}-{end}"

        ]


        ydl_opts[
            "force_keyframes_at_cuts"
        ] = True


        print(
            "[YTDLP] download section:",
            f"{start}-{end}"
        )


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
            "=========================================="
        )

        print(
            "[YTDLP] MP3作成エラー"
        )

        print(
            "[YTDLP] error:",
            error
        )

        print(
            "=========================================="
        )

        raise


    # =====================================
    # MP3ファイル確認
    # =====================================

    mp3_files = []


    for filename in os.listdir(
        DOWNLOAD_DIR
    ):

        if filename.lower().endswith(
            ".mp3"
        ):

            filepath = os.path.join(
                DOWNLOAD_DIR,
                filename
            )

            if os.path.isfile(
                filepath
            ):

                mp3_files.append(
                    filename
                )


    # =====================================
    # MP3がない場合
    # =====================================

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


    # =====================================
    # ファイル確認
    # =====================================

    if not os.path.isfile(
        filepath
    ):

        raise RuntimeError(
            "MP3ファイルの確認に失敗しました。"
        )


    # =====================================
    # 完了ログ
    # =====================================

    print("==========================================")

    print(
        "[YTDLP] MP3作成完了"
    )

    print(
        "[YTDLP] filename:",
        filename
    )

    print(
        "[YTDLP] path:",
        filepath
    )

    print(
        "[YTDLP] size:",
        os.path.getsize(
            filepath
        ),
        "bytes"
    )

    print("==========================================")


    # =====================================
    # 結果
    # =====================================

    return {

        "success":
            True,

        "filename":
            filename,

        "path":
            filepath

    }
