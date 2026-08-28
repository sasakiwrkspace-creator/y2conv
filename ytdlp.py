# =====================================
# YouTube Converter
# ytdlp.py
#
# YouTube → MP3変換
# =====================================

import os
import shutil
import tempfile

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
    # Secret File確認
    # =================================

    if not os.path.isfile(
        COOKIES_FILE
    ):

        raise RuntimeError(
            "Renderのcookies.txtが見つかりません。"
        )


    print("==========================================")
    print("[YTDLP] MP3作成開始")
    print("[YTDLP] URL:", url)
    print("[YTDLP] start_time:", start_time)
    print("[YTDLP] end_time:", end_time)
    print("[YTDLP] DOWNLOAD_DIR:", DOWNLOAD_DIR)
    print("[YTDLP] COOKIES_FILE:", COOKIES_FILE)
    print(
        "[YTDLP] cookies exists:",
        os.path.isfile(COOKIES_FILE)
    )
    print("==========================================")


    # =====================================
    # 一時Cookie
    # =====================================

    temporary_cookie = None


    try:

        # =================================
        # 一時ファイル作成
        # =================================

        temporary_file = tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".txt",
            prefix="y2conv_cookies_",
            delete=False
        )

        temporary_cookie = (
            temporary_file.name
        )

        temporary_file.close()


        print(
            "[YTDLP] temporary cookie:",
            temporary_cookie
        )


        # =================================
        # Secret File → 一時ファイル
        # =================================

        shutil.copyfile(
            COOKIES_FILE,
            temporary_cookie
        )


        print(
            "[YTDLP] cookies.txtを一時コピーしました"
        )


        # =================================
        # yt-dlp設定
        # =================================

        ydl_opts = {

            # =================================
            # 音声
            # =================================

            "format":
                "bestaudio/best",


            # =================================
            # 出力先
            # =================================

            "outtmpl":
                os.path.join(
                    DOWNLOAD_DIR,
                    "%(title)s.%(ext)s"
                ),


            # =================================
            # Cookie
            # =================================

            "cookiefile":
                temporary_cookie,


            # =================================
            # YouTube EJS Challenge対策
            # =================================
            #
            # Render上のDenoを明示的に指定
            #

            "js_runtimes": {

                "deno":
                    "/root/.deno/bin/deno"

            },


            # =================================
            # EJS remote component
            # =================================

            "remote_components": [

                "ejs:npm"

            ],


            # =================================
            # MP3変換
            # =================================

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


            # =================================
            # ログ
            # =================================

            "quiet":
                False,

            "no_warnings":
                False,


            # =================================
            # 上書き
            # =================================

            "overwrites":
                True

        }


        # =====================================
        # 時間範囲
        # =====================================

        # 空文字をNoneとして扱う
        if start_time == "":
            start_time = None

        if end_time == "":
            end_time = None


        # =====================================
        # 00:00:00だけの場合は未指定扱い
        # =====================================
        #
        # フロントエンドから
        # end_time=00:00:00
        # が送られてくるケースを考慮
        #

        if (
            start_time is None
            and
            end_time == "00:00:00"
        ):

            end_time = None


        # =====================================
        # download_sections
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

        else:

            print(
                "[YTDLP] download section: FULL"
            )


        # =====================================
        # yt-dlpバージョン確認
        # =====================================

        print(
            "[YTDLP] yt-dlp version:",
            yt_dlp.version.__version__
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
        # MP3確認
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
        # MP3なし
        # =====================================

        if not mp3_files:

            raise RuntimeError(
                "MP3ファイルが作成されませんでした。"
            )


        # =====================================
        # 最新MP3
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

        print(
            "=========================================="
        )

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

        print(
            "=========================================="
        )


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


    finally:

        # =====================================
        # 一時Cookie削除
        # =====================================

        if (
            temporary_cookie
            and
            os.path.exists(
                temporary_cookie
            )
        ):

            try:

                os.remove(
                    temporary_cookie
                )

                print(
                    "[YTDLP] 一時cookies.txtを削除しました"
                )

            except Exception as error:

                print(
                    "[YTDLP] 一時cookies.txt削除エラー:",
                    error
                )
