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
    # Cookie確認
    # =================================

    if not os.path.isfile(
        COOKIES_FILE
    ):

        raise RuntimeError(
            "Renderのcookies.txtが見つかりません。"
        )


    print(
        "=========================================="
    )

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
        os.path.isfile(COOKIES_FILE)
    )

    print(
        "=========================================="
    )


    temporary_cookie = None


    try:

        # =================================
        # 一時Cookie作成
        # =================================

        fd, temporary_cookie = tempfile.mkstemp(
            prefix="y2conv_cookies_",
            suffix=".txt",
            dir="/tmp"
        )

        os.close(
            fd
        )


        shutil.copyfile(
            COOKIES_FILE,
            temporary_cookie
        )


        print(
            "[YTDLP] 一時Cookie作成:",
            temporary_cookie
        )


        # =================================
        # 時間指定整理
        # =================================

        if start_time == "":
            start_time = None


        if end_time == "":
            end_time = None


        # =================================
        # 終了時間だけ指定された場合
        #
        # 00:00:00 ～ end_time
        # =================================

        if (
            start_time is None
            and
            end_time is not None
        ):

            start_time = "00:00:00"


        # =================================
        # yt-dlp設定
        # =================================

        ydl_opts = {

            # ---------------------------------
            # 音声
            # ---------------------------------

            "format":
                "bestaudio/best",


            # ---------------------------------
            # 出力先
            # ---------------------------------

            "outtmpl":
                os.path.join(
                    DOWNLOAD_DIR,
                    "%(title)s.%(ext)s"
                ),


            # ---------------------------------
            # Cookie
            # ---------------------------------

            "cookiefile":
                temporary_cookie,


            # ---------------------------------
            # プレイリスト無効
            # ---------------------------------

            "noplaylist":
                True,


            # ---------------------------------
            # Deno
            # ---------------------------------

            "js_runtimes": {

                "deno": {}

            },


            # ---------------------------------
            # EJS
            #
            # 重要:
            # ejs:github を使用する。
            # ---------------------------------

            "remote_components": {

                "ejs":
                    "github"

            },


            # ---------------------------------
            # ログ
            # ---------------------------------

            "quiet":
                False,

            "no_warnings":
                False,


            # ---------------------------------
            # 上書き
            # ---------------------------------

            "overwrites":
                True

        }


        # =================================
        # 時間範囲
        # =================================

        if (
            start_time is not None
            or
            end_time is not None
        ):

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


            print(
                "[YTDLP] download section:",
                f"{start}-{end}"
            )

        else:

            print(
                "[YTDLP] download section: FULL"
            )


        # =================================
        # yt-dlpバージョン
        # =================================

        print(
            "[YTDLP] yt-dlp version:",
            yt_dlp.version.__version__
        )


        # =================================
        # Deno確認
        # =================================

        deno_path = None


        try:

            import shutil as _shutil

            deno_path = _shutil.which(
                "deno"
            )

        except Exception:

            deno_path = None


        print(
            "[YTDLP] Deno:",
            deno_path
        )


        # =================================
        # YouTube取得
        # =================================

        print(
            "[YTDLP] YouTube取得開始"
        )


        try:

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(
                    url,
                    download=True
                )


        except Exception as error:

            print(
                "=========================================="
            )

            print(
                "[YTDLP] yt-dlp ERROR:",
                repr(error)
            )

            print(
                "=========================================="
            )

            raise


        # =================================
        # 情報確認
        # =================================

        if not info:

            raise RuntimeError(
                "YouTube情報を取得できませんでした。"
            )


        # =================================
        # タイトル
        # =================================

        title = info.get(
            "title",
            "output"
        )


        print(
            "[YTDLP] title:",
            title
        )


        # =================================
        # MP3確認
        # =================================

        mp3_files = []


        for filename in os.listdir(
            DOWNLOAD_DIR
        ):

            if not filename.lower().endswith(
                ".mp3"
            ):

                continue


            filepath = os.path.join(
                DOWNLOAD_DIR,
                filename
            )


            if not os.path.isfile(
                filepath
            ):

                continue


            if os.path.getsize(
                filepath
            ) <= 0:

                continue


            mp3_files.append(
                filepath
            )


        # =================================
        # MP3なし
        # =================================

        if not mp3_files:

            raise RuntimeError(
                "MP3ファイルが作成されませんでした。"
            )


        # =================================
        # 最新MP3
        # =================================

        filepath = max(
            mp3_files,
            key=os.path.getmtime
        )


        filename = os.path.basename(
            filepath
        )


        # =================================
        # 完了
        # =================================

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
            os.path.getsize(filepath),
            "bytes"
        )

        print(
            "=========================================="
        )


        return {

            "success":
                True,

            "filename":
                filename,

            "path":
                filepath

        }


    finally:

        # =================================
        # 一時Cookie削除
        # =================================

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
                    "[YTDLP] 一時Cookie削除:",
                    temporary_cookie
                )

            except Exception as error:

                print(
                    "[YTDLP] "
                    "一時Cookie削除エラー:",
                    repr(error)
                )
