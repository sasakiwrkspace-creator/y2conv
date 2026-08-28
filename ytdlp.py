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
        temporary_cookie,

    # =================================
    # YouTube EJS Challenge対策
    # =================================

    "js_runtimes": {
        "deno":
            "/root/.deno/bin/deno"
    },

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

    "quiet":
        False,

    "no_warnings":
        False,

    "overwrites":
        True
}
