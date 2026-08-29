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
    # 出力ディレクトリ確認
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
            "Cookieファイルが見つかりません: "
            + COOKIES_FILE
        )


    if os.path.getsize(
        COOKIES_FILE
    ) == 0:
        raise RuntimeError(
            "Cookieファイルが空です: "
            + COOKIES_FILE
        )


    # =================================
    # ログ
    # =================================

    print(
        "==========================================",
        flush=True
    )

    print(
        "[YTDLP] MP3作成開始",
        flush=True
    )

    print(
        "[YTDLP] URL:",
        url,
        flush=True
    )

    print(
        "[YTDLP] start_time:",
        start_time,
        flush=True
    )

    print(
        "[YTDLP] end_time:",
        end_time,
        flush=True
    )

    print(
        "[YTDLP] DOWNLOAD_DIR:",
        DOWNLOAD_DIR,
        flush=True
    )

    print(
        "[YTDLP] COOKIES_FILE:",
        COOKIES_FILE,
        flush=True
    )

    print(
        "[YTDLP] cookies exists:",
        os.path.isfile(COOKIES_FILE),
        flush=True
    )

    print(
        "[YTDLP] yt-dlp version:",
        yt_dlp.version.__version__,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    temporary_cookie = None


    try:

        # =================================
        # 一時Cookie作成
        # =================================

        fd, temporary_cookie = tempfile.mkstemp(
            prefix="y2conv_cookies_",
            suffix=".txt"
        )

        os.close(fd)


        shutil.copyfile(
            COOKIES_FILE,
            temporary_cookie
        )


        print(
            "[YTDLP] 一時Cookie作成:",
            temporary_cookie,
            flush=True
        )


        # =================================
        # yt-dlp設定
        # =================================

        ydl_opts = {

            "format":
                "bestaudio/best",

            "outtmpl":
                os.path.join(
                    DOWNLOAD_DIR,
                    "%(title)s.%(ext)s"
                ),

            "cookiefile":
                temporary_cookie,

            "noplaylist":
                True,

            "quiet":
                False,

            "no_warnings":
                False,

            "overwrites":
                True

        }


        # =================================
        # Deno
        # =================================

        deno_path = (
            "/opt/render/project/src/.deno/bin/deno"
        )


        if (
            os.path.isfile(deno_path)
            and
            os.access(deno_path, os.X_OK)
        ):

            print(
                "[YTDLP] Deno:",
                deno_path,
                flush=True
            )


            ydl_opts["js_runtimes"] = {

                "deno": {

                    "path":
                        deno_path

                }

            }


            ydl_opts["remote_components"] = {

                "ejs":
                    "github"

            }


        else:

            print(
                "[YTDLP] Denoが利用できません:",
                deno_path,
                flush=True
            )


        # =================================
        # 時間指定の整理
        # =================================

        if start_time == "":
            start_time = None


        if end_time == "":
            end_time = None


        # =================================
        # 終了時間だけ指定された場合
        # =================================

        if (
            start_time is None
            and
            end_time is not None
        ):

            start_time = "00:00:00"


        # =================================
        # 時間範囲確認
        # =================================

        if (
            start_time is not None
            and
            end_time is not None
        ):

            ydl_opts["download_sections"] = [

                f"*{start_time}-{end_time}"

            ]


            ydl_opts[
                "force_keyframes_at_cuts"
            ] = False


            print(
                "[YTDLP] download section:",
                f"{start_time}-{end_time}",
                flush=True
            )


        else:

            print(
                "[YTDLP] download section: FULL",
                flush=True
            )


        # =================================
        # YouTubeダウンロード
        # =================================

        print(
            "[YTDLP] YouTube取得開始",
            flush=True
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
                "==========================================",
                flush=True
            )

            print(
                "[YTDLP] yt-dlp ERROR:",
                repr(error),
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            raise


        if not info:

            raise RuntimeError(
                "YouTube情報を取得できませんでした。"
            )


        # =================================
        # MP3検索
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


            if os.path.isfile(
                filepath
            ):

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
        # 最新MP3取得
        # =================================

        output_file = max(
            mp3_files,
            key=os.path.getmtime
        )


        filename = os.path.basename(
            output_file
        )


        # =================================
        # ファイル確認
        # =================================

        if not os.path.isfile(
            output_file
        ):

            raise RuntimeError(
                "MP3ファイルの確認に失敗しました。"
            )


        file_size = os.path.getsize(
            output_file
        )


        if file_size <= 0:

            raise RuntimeError(
                "MP3ファイルが0 bytesです。"
            )


        # =================================
        # 完了ログ
        # =================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[YTDLP] MP3作成完了",
            flush=True
        )

        print(
            "[YTDLP] filename:",
            filename,
            flush=True
        )

        print(
            "[YTDLP] path:",
            output_file,
            flush=True
        )

        print(
            "[YTDLP] size:",
            file_size,
            "bytes",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        # =================================
        # 結果
        # =================================

        return {

            "success":
                True,

            "filename":
                filename,

            "path":
                output_file

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
                    temporary_cookie,
                    flush=True
                )

            except Exception as error:

                print(
                    "[YTDLP] 一時Cookie削除エラー:",
                    repr(error),
                    flush=True
                )
