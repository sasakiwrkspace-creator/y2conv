def create_mp4(
    url,
    output_dir=None
):
    print("==========================================", flush=True)
    print("[DEBUG] create_mp4 START", flush=True)

    try:

        print(
            "[DEBUG] MP4 URL:",
            url,
            flush=True
        )

        print(
            "[DEBUG] MP4 output_dir:",
            output_dir,
            flush=True
        )

        if not url:
            raise ValueError(
                "YouTube URLが空です"
            )

        if output_dir is None:
            output_dir = os.path.join(
                os.getcwd(),
                "downloads"
            )

        output_dir = Path(output_dir)

        print(
            "[DEBUG] MP4 output directory:",
            output_dir,
            flush=True
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "[DEBUG] MP4 output directory exists:",
            output_dir.exists(),
            flush=True
        )

        print(
            "[DEBUG] MP4 output directory writable:",
            os.access(
                output_dir,
                os.W_OK
            ),
            flush=True
        )

        # ==========================================
        # Cookie
        # ==========================================

        cookies_source = "/etc/secrets/cookies.txt"

        print(
            "[DEBUG] MP4 cookies source:",
            cookies_source,
            flush=True
        )

        print(
            "[DEBUG] MP4 cookies exists:",
            os.path.isfile(cookies_source),
            flush=True
        )

        temporary_cookie_path = None

        if os.path.isfile(cookies_source):

            print(
                "[DEBUG] MP4: cookies file detected",
                flush=True
            )

            temporary_cookie_file = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                prefix="y2conv_cookies_",
                delete=False
            )

            temporary_cookie_path = (
                temporary_cookie_file.name
            )

            temporary_cookie_file.close()

            shutil.copyfile(
                cookies_source,
                temporary_cookie_path
            )

            print(
                "[DEBUG] MP4 temporary cookies:",
                temporary_cookie_path,
                flush=True
            )

        else:

            print(
                "[DEBUG] MP4: cookies file does not exist",
                flush=True
            )

        # ==========================================
        # yt-dlp設定
        # ==========================================

        download_template = str(
            output_dir / "%(id)s.%(ext)s"
        )

        print(
            "[DEBUG] MP4 download template:",
            download_template,
            flush=True
        )

        ydl_opts = {
            "outtmpl": download_template,

            # 動画 + 音声
            "format": "bv*+ba/b",

            "noplaylist": True,

            "quiet": False,

            "no_warnings": False,

            "verbose": True,

            "merge_output_format": "mp4",

            "js_runtimes": {
                "deno": {}
            },

            "remote_components": {
                "ejs:github"
            },
        }

        if temporary_cookie_path:

            ydl_opts["cookiefile"] = (
                temporary_cookie_path
            )

            print(
                "[DEBUG] MP4 cookiefile enabled",
                flush=True
            )

        else:

            print(
                "[DEBUG] MP4 cookiefile NOT enabled",
                flush=True
            )

        print(
            "[DEBUG] MP4 yt-dlp options:",
            flush=True
        )

        print(
            "[DEBUG] MP4 format:",
            ydl_opts.get("format"),
            flush=True
        )

        print(
            "[DEBUG] MP4 merge_output_format:",
            ydl_opts.get("merge_output_format"),
            flush=True
        )

        print(
            "[DEBUG] MP4 js_runtimes:",
            ydl_opts.get("js_runtimes"),
            flush=True
        )

        print(
            "[DEBUG] MP4 remote_components:",
            ydl_opts.get("remote_components"),
            flush=True
        )

        # ==========================================
        # yt-dlp実行
        # ==========================================

        info = None

        try:

            print(
                "[DEBUG] MP4 Creating YoutubeDL instance...",
                flush=True
            )

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                print(
                    "[DEBUG] MP4 YoutubeDL instance created",
                    flush=True
                )

                print(
                    "[DEBUG] MP4 Starting extract_info()",
                    flush=True
                )

                print(
                    "[DEBUG] MP4 Connecting to YouTube...",
                    flush=True
                )

                info = ydl.extract_info(
                    url,
                    download=True
                )

                print(
                    "[DEBUG] MP4 extract_info/download SUCCESS",
                    flush=True
                )

                if info is None:

                    raise RuntimeError(
                        "MP4 extract_info() returned None"
                    )

                print(
                    "[DEBUG] MP4 video id:",
                    info.get("id"),
                    flush=True
                )

                print(
                    "[DEBUG] MP4 video title:",
                    info.get("title"),
                    flush=True
                )

                print(
                    "[DEBUG] MP4 duration:",
                    info.get("duration"),
                    flush=True
                )

                print(
                    "[DEBUG] MP4 webpage_url:",
                    info.get("webpage_url"),
                    flush=True
                )

                print(
                    "[DEBUG] MP4 extractor:",
                    info.get("extractor"),
                    flush=True
                )

        except Exception as e:

            print(
                "[DEBUG] MP4 yt-dlp PROCESS ERROR:",
                repr(e),
                flush=True
            )

            print(
                "[DEBUG] MP4 exception type:",
                type(e).__name__,
                flush=True
            )

            traceback.print_exc()

            raise

        # ==========================================
        # ダウンロードファイル検索
        # ==========================================

        print(
            "[DEBUG] MP4 Searching downloaded files...",
            flush=True
        )

        video_id = None

        if info:
            video_id = info.get("id")

        print(
            "[DEBUG] MP4 video_id:",
            video_id,
            flush=True
        )

        downloaded_file = None

        if video_id:

            candidates = list(
                output_dir.glob(
                    video_id + ".*"
                )
            )

            print(
                "[DEBUG] MP4 candidate files:",
                len(candidates),
                flush=True
            )

            for candidate in candidates:

                print(
                    "[DEBUG] MP4 candidate:",
                    candidate,
                    "size=",
                    candidate.stat().st_size,
                    flush=True
                )

                if candidate.is_file():

                    # 一時ファイルを除外
                    if candidate.suffix.lower() in [
                        ".part",
                        ".ytdl",
                        ".temp"
                    ]:
                        continue

                    downloaded_file = candidate

                    break

        # ==========================================
        # ファイルが見つからない場合
        # ==========================================

        if downloaded_file is None:

            print(
                "[DEBUG] MP4 No file found by video ID",
                flush=True
            )

            all_files = [
                p
                for p in output_dir.iterdir()
                if p.is_file()
            ]

            print(
                "[DEBUG] MP4 files in output directory:",
                len(all_files),
                flush=True
            )

            for p in all_files:

                print(
                    "[DEBUG] MP4 existing file:",
                    p,
                    "size=",
                    p.stat().st_size,
                    flush=True
                )

        if downloaded_file is None:

            raise FileNotFoundError(
                "yt-dlpでダウンロードしたMP4ファイルを確認できませんでした"
            )

        print(
            "[DEBUG] MP4 downloaded file:",
            downloaded_file,
            flush=True
        )

        print(
            "[DEBUG] MP4 downloaded file size:",
            downloaded_file.stat().st_size,
            flush=True
        )

        # ==========================================
        # MP4確認
        # ==========================================

        if downloaded_file.suffix.lower() != ".mp4":

            print(
                "[DEBUG] WARNING: downloaded file is not .mp4:",
                downloaded_file.suffix,
                flush=True
            )

        print(
            "[DEBUG] MP4 create SUCCESS",
            flush=True
        )

        return str(downloaded_file)

    except Exception as e:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[DEBUG] create_mp4 ERROR:",
            repr(e),
            flush=True
        )

        print(
            "[DEBUG] exception type:",
            type(e).__name__,
            flush=True
        )

        traceback.print_exc()

        raise

    finally:

        if "temporary_cookie_path" in locals():

            if temporary_cookie_path:

                print(
                    "[DEBUG] Removing MP4 temporary cookies...",
                    flush=True
                )

                try:

                    if os.path.exists(
                        temporary_cookie_path
                    ):

                        os.remove(
                            temporary_cookie_path
                        )

                        print(
                            "[DEBUG] MP4 temporary cookies removed",
                            flush=True
                        )

                except Exception as e:

                    print(
                        "[DEBUG] MP4 temporary cookies removal ERROR:",
                        repr(e),
                        flush=True
                    )

        print(
            "[DEBUG] create_mp4 END",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )
