```python
# ==========================================================
# YouTube情報・format診断
# ==========================================================

def diagnose_formats(
    url
):

    temp_cookie = None

    try:

        print("==========================================")
        print("YouTube情報取得開始")
        print("URL:", url)
        print(
            "yt-dlp version:",
            yt_dlp.version.__version__
        )
        print(
            "Python version:",
            __import__("sys").version
        )
        print(
            "Deno path:",
            shutil.which("deno")
        )
        print("==========================================")


        # --------------------------------------------------
        # yt-dlp設定
        # --------------------------------------------------

        ydl_opts = get_ydl_base_options()


        # --------------------------------------------------
        # Cookieファイルを取得
        # --------------------------------------------------

        temp_cookie = ydl_opts.get(
            "cookiefile"
        )


        ydl_opts.update({

            "quiet":
            False,

            "no_warnings":
            False,

            "verbose":
            True,

            "skip_download":
            True

        })


        # --------------------------------------------------
        # YouTube情報取得
        # --------------------------------------------------

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            print(
                "extract_info開始"
            )


            info = ydl.extract_info(
                url,
                download=False
            )


        if not info:

            raise Exception(
                "YouTube情報を取得できませんでした"
            )


        # ==================================================
        # 基本情報
        # ==================================================

        title = info.get(
            "title"
        )


        duration = info.get(
            "duration"
        )


        print("==========================================")
        print(
            "動画タイトル:",
            title
        )
        print(
            "再生時間:",
            duration,
            "秒"
        )
        print("==========================================")


        # ==================================================
        # Format一覧
        # ==================================================

        formats = info.get(
            "formats",
            []
        )


        print(
            "利用可能format数:",
            len(formats)
        )


        print("==========================================")
        print("利用可能format一覧")
        print("==========================================")


        for f in formats:

            print(
                "ID=",
                f.get("format_id"),
                "EXT=",
                f.get("ext"),
                "VCODEC=",
                f.get("vcodec"),
                "ACODEC=",
                f.get("acodec"),
                "RES=",
                f.get("resolution"),
                "ABR=",
                f.get("abr")
            )


        print("==========================================")
        print("音声format一覧")
        print("==========================================")


        audio_formats = []


        for f in formats:

            acodec = f.get(
                "acodec"
            )


            vcodec = f.get(
                "vcodec"
            )


            if (
                acodec
                and acodec != "none"
                and (
                    not vcodec
                    or vcodec == "none"
                )
            ):

                audio_formats.append(
                    f
                )


                print(
                    "AUDIO",
                    "ID=",
                    f.get("format_id"),
                    "EXT=",
                    f.get("ext"),
                    "ACODEC=",
                    f.get("acodec"),
                    "ABR=",
                    f.get("abr"),
                    "ASR=",
                    f.get("asr")
                )


        print("==========================================")
        print(
            "音声format数:",
            len(audio_formats)
        )
        print("==========================================")


        return info


    finally:

        # --------------------------------------------------
        # 診断終了後に一時Cookie削除
        # --------------------------------------------------

        remove_cookie_file(
            temp_cookie
        )
```
