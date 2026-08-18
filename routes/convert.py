def create_mp3(
    source_file,
    output_file
):

    print("==========================================")
    print("MP3作成")
    print("入力:", source_file)
    print("出力:", output_file)
    print("==========================================", flush=True)


    if not check_ffmpeg():

        raise Exception(
            "ffmpegが利用できません"
        )


    # ======================================================
    # MP3化のみ
    #
    # source_file はすでに yt-dlp によって
    # 指定時間範囲に切り出されている。
    #
    # ここでは時間指定を再度行わない。
    # ======================================================

    command = [

        "ffmpeg",

        "-y",

        "-i",
        source_file,

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-b:a",
        "128k",

        "-map_metadata",
        "-1",

        output_file

    ]


    print(
        "FFmpeg:",
        command,
        flush=True
    )


    print(
        "DEBUG: FFmpeg MP3 START",
        flush=True
    )


    try:

        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=600

        )

    except subprocess.TimeoutExpired as e:

        print(
            "ERROR: FFmpeg MP3 TIMEOUT",
            flush=True
        )

        if os.path.exists(output_file):

            try:

                os.remove(output_file)

            except Exception:

                pass

        raise Exception(
            "MP3作成が600秒でタイムアウトしました"
        ) from e


    print(
        "DEBUG: FFmpeg MP3 END",
        flush=True
    )


    if result.returncode != 0:

        print(
            result.stderr,
            flush=True
        )


        if os.path.exists(output_file):

            try:

                os.remove(output_file)

            except Exception:

                pass


        raise Exception(
            "MP3作成に失敗しました"
        )


    if not os.path.exists(output_file):

        raise Exception(
            "MP3ファイルが作成されませんでした"
        )


    file_size = os.path.getsize(
        output_file
    )


    if file_size <= 0:

        raise Exception(
            "MP3ファイルが0 bytesです"
        )


    print("==========================================")
    print("DEBUG: MP3保存先確認")
    print(
        "output_file:",
        output_file
    )
    print(
        "絶対パス:",
        os.path.abspath(output_file)
    )
    print(
        "exists:",
        os.path.exists(output_file)
    )

    if os.path.exists(output_file):

        print(
            "size:",
            os.path.getsize(output_file)
        )

    print(
        "DOWNLOAD_DIR:",
        DOWNLOAD_DIR
    )

    try:

        print(
            "downloads内容:",
            os.listdir(DOWNLOAD_DIR)
        )

    except Exception as e:

        print(
            "downloads読み込み失敗:",
            repr(e)
        )

    print("==========================================")


    actual_duration = get_media_duration(
        output_file
    )


    print("==========================================")
    print("MP3作成完了")
    print("ファイル:", output_file)
    print("サイズ:", file_size)
    print(
        "実際の再生時間:",
        actual_duration
    )
    print(
        "ファイル存在確認:",
        os.path.isfile(output_file)
    )
    print("==========================================", flush=True)


    return actual_duration
