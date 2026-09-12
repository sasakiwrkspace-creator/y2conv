# =====================================
# FFmpeg字幕テスト
#
# /subtitle-test/ffmpeg
#
# 画面
#   ↓
# mp4_file
# srt_file
#   ↓
# app.py
#   ↓
# subtitle_test_ffmpeg.py
#   ↓
# FFmpeg
#
# 入力:
#
#   画面から指定されたMP4
#   画面から指定されたSRT
#
# 出力:
#
#   入力MP4が
#
#       タイトル.mp4
#
#   の場合、
#
#       タイトル_字幕.mp4
#
#   とする。
#
# test.mp4
# test.srt
# test_embed.mp4
#
# は使用しない。
#
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] /subtitle-test/ffmpeg START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    try:

        # =====================================
        # JSON取得
        # =====================================

        data = request.get_json(
            silent=True
        )


        if not data:

            raise ValueError(
                "リクエストJSONがありません。"
            )


        print(
            "[APP] /subtitle-test/ffmpeg request:",
            data,
            flush=True
        )


        # =====================================
        # MP4ファイル名取得
        #
        # ★test.mp4をデフォルトにしない
        #
        # 必ず画面から受け取る。
        # =====================================

        mp4_filename = data.get(
            "mp4_file"
        )


        if not isinstance(
            mp4_filename,
            str
        ):

            raise ValueError(
                "mp4_fileが指定されていません。"
            )


        mp4_filename = mp4_filename.strip()


        if not mp4_filename:

            raise ValueError(
                "mp4_fileが空です。"
            )


        # =====================================
        # SRTファイル名取得
        #
        # ★test.srtをデフォルトにしない
        #
        # 必ず画面から受け取る。
        # =====================================

        srt_filename = data.get(
            "srt_file"
        )


        if not isinstance(
            srt_filename,
            str
        ):

            raise ValueError(
                "srt_fileが指定されていません。"
            )


        srt_filename = srt_filename.strip()


        if not srt_filename:

            raise ValueError(
                "srt_fileが空です。"
            )


        # =====================================
        # ファイル名安全化
        #
        # downloads直下だけを使用する。
        # =====================================

        mp4_name = Path(
            mp4_filename
        ).name


        srt_name = Path(
            srt_filename
        ).name


        if not mp4_name:

            raise ValueError(
                "MP4ファイル名を取得できません。"
            )


        if not srt_name:

            raise ValueError(
                "SRTファイル名を取得できません。"
            )


        # =====================================
        # 拡張子確認
        # =====================================

        if Path(
            mp4_name
        ).suffix.lower() != ".mp4":

            raise ValueError(
                "指定されたMP4ファイルの拡張子が"
                ".mp4ではありません: "
                f"{mp4_name}"
            )


        if Path(
            srt_name
        ).suffix.lower() != ".srt":

            raise ValueError(
                "指定されたSRTファイルの拡張子が"
                ".srtではありません: "
                f"{srt_name}"
            )


        # =====================================
        # downloads内の入力ファイル
        # =====================================

        input_path = (
            Path(DOWNLOAD_DIR)
            / mp4_name
        )


        srt_path = (
            Path(DOWNLOAD_DIR)
            / srt_name
        )


        # =====================================
        # 出力ファイル名
        #
        # タイトル.mp4
        #      ↓
        # タイトル_字幕.mp4
        # =====================================

        output_path = (
            input_path.parent
            /
            f"{input_path.stem}_字幕.mp4"
        )


        print(
            "[APP] 入力MP4:",
            input_path,
            flush=True
        )


        print(
            "[APP] 入力SRT:",
            srt_path,
            flush=True
        )


        print(
            "[APP] 出力字幕MP4:",
            output_path,
            flush=True
        )


        # =====================================
        # MP4存在確認
        # =====================================

        print(
            "[APP] MP4存在確認 START",
            flush=True
        )


        if not input_path.exists():

            raise FileNotFoundError(
                "入力MP4が存在しません: "
                f"{input_path}"
            )


        if not input_path.is_file():

            raise FileNotFoundError(
                "入力MP4が通常ファイルではありません: "
                f"{input_path}"
            )


        input_size = (
            input_path.stat().st_size
        )


        if input_size <= 0:

            raise RuntimeError(
                "入力MP4のサイズが0 bytesです: "
                f"{input_path}"
            )


        print(
            "[APP] MP4存在確認 OK",
            flush=True
        )


        print(
            "[APP] 入力MP4サイズ:",
            input_size,
            "bytes",
            flush=True
        )


        # =====================================
        # SRT存在確認
        # =====================================

        print(
            "[APP] SRT存在確認 START",
            flush=True
        )


        if not srt_path.exists():

            raise FileNotFoundError(
                "入力SRTが存在しません: "
                f"{srt_path}"
            )


        if not srt_path.is_file():

            raise FileNotFoundError(
                "入力SRTが通常ファイルではありません: "
                f"{srt_path}"
            )


        srt_size = (
            srt_path.stat().st_size
        )


        if srt_size <= 0:

            raise RuntimeError(
                "入力SRTのサイズが0 bytesです: "
                f"{srt_path}"
            )


        print(
            "[APP] SRT存在確認 OK",
            flush=True
        )


        print(
            "[APP] 入力SRTサイズ:",
            srt_size,
            "bytes",
            flush=True
        )


        # =====================================
        # 前回の同名字幕MP4を削除
        # =====================================

        if output_path.exists():

            if output_path.is_file():

                print(
                    "[APP] 既存字幕MP4を削除:",
                    output_path,
                    flush=True
                )

                output_path.unlink()

            else:

                raise RuntimeError(
                    "字幕MP4出力先が通常ファイルではありません: "
                    f"{output_path}"
                )


        # =====================================
        # subtitle_test_ffmpeg import
        # =====================================

        print(
            "[APP] subtitle_test_ffmpeg "
            "import START",
            flush=True
        )


        from subtitle_test_ffmpeg import (
            run_ffmpeg_subtitle_test
        )


        print(
            "[APP] subtitle_test_ffmpeg "
            "import OK",
            flush=True
        )


        # =====================================
        # FFmpeg開始
        # =====================================

        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] FFmpeg START",
            flush=True
        )


        print(
            "[APP] FFmpeg input:",
            input_path,
            flush=True
        )


        print(
            "[APP] FFmpeg SRT:",
            srt_path,
            flush=True
        )


        print(
            "[APP] FFmpeg output:",
            output_path,
            flush=True
        )


        print(
            "==========================================",
            flush=True
        )


        result = run_ffmpeg_subtitle_test(
            input_path=str(
                input_path
            ),

            srt_path=str(
                srt_path
            ),

            output_path=str(
                output_path
            )
        )


        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] FFmpeg RETURN",
            flush=True
        )


        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] result:",
            result,
            flush=True
        )


        # =====================================
        # 戻り値をPath化
        # =====================================

        actual_output = Path(
            result
        ).resolve()


        expected_output = (
            output_path
            .resolve()
        )


        print(
            "[APP] actual output:",
            actual_output,
            flush=True
        )


        print(
            "[APP] expected output:",
            expected_output,
            flush=True
        )


        # =====================================
        # 出力先確認
        # =====================================

        if actual_output != expected_output:

            raise RuntimeError(
                "字幕MP4の出力先が想定と異なります。\n"
                f"想定: {expected_output}\n"
                f"実際: {actual_output}"
            )


        # =====================================
        # 出力ファイル確認
        # =====================================

        print(
            "[APP] 出力ファイル確認 START",
            flush=True
        )


        if not output_path.exists():

            raise FileNotFoundError(
                "FFmpeg終了後も字幕MP4が存在しません: "
                f"{output_path}"
            )


        if not output_path.is_file():

            raise FileNotFoundError(
                "字幕MP4出力が通常ファイルではありません: "
                f"{output_path}"
            )


        output_size = (
            output_path.stat().st_size
        )


        if output_size <= 0:

            raise RuntimeError(
                "字幕MP4のサイズが0 bytesです: "
                f"{output_path}"
            )


        print(
            "[APP] 出力ファイル確認 OK",
            flush=True
        )


        print(
            "[APP] 出力サイズ:",
            output_size,
            "bytes",
            flush=True
        )


        # =====================================
        # 成功
        # =====================================

        result_json = {

            "success":
                True,

            "mp4":
                str(input_path),

            "srt":
                str(srt_path),

            "output":
                str(output_path),

            "filename":
                output_path.name,

            "mp4_size":
                input_size,

            "srt_size":
                srt_size,

            "output_size":
                output_size

        }


        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] /subtitle-test/ffmpeg SUCCESS",
            flush=True
        )


        print(
            "[APP] INPUT MP4:",
            input_path,
            flush=True
        )


        print(
            "[APP] INPUT SRT:",
            srt_path,
            flush=True
        )


        print(
            "[APP] OUTPUT:",
            output_path,
            flush=True
        )


        print(
            "==========================================",
            flush=True
        )


        return jsonify(
            result_json
        ), 200


    except Exception as error:

        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] /subtitle-test/ffmpeg FAILED",
            flush=True
        )


        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] ERROR TYPE:",
            type(error).__name__,
            flush=True
        )


        print(
            "[APP] ERROR:",
            str(error),
            flush=True
        )


        print(
            "[APP] TRACEBACK START",
            flush=True
        )


        traceback.print_exc()


        print(
            "[APP] TRACEBACK END",
            flush=True
        )


        return jsonify({

            "success":
                False,

            "message":
                str(error),

            "error_type":
                type(error).__name__

        }), 500


    finally:

        # =====================================
        # 一時ディレクトリ削除
        # =====================================

        if (
            temporary_directory
            and temporary_directory.exists()
        ):

            try:

                shutil.rmtree(
                    temporary_directory
                )

                print(
                    "[APP] temporary directory removed:",
                    temporary_directory,
                    flush=True
                )

            except Exception as cleanup_error:

                print(
                    "[APP] temporary directory cleanup FAILED:",
                    cleanup_error,
                    flush=True
                )


# =====================================
# FFmpeg字幕テスト
#
# /subtitle-test/ffmpeg
#
# app.py
#   ↓
# subtitle_test_ffmpeg.py
#   ↓
# FFmpeg
#
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] /subtitle-test/ffmpeg START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    try:

        # =====================================
        # パス
        # =====================================

        input_path = (
            Path(DOWNLOAD_DIR)
            / "test.mp4"
        )

        output_path = (
            Path(DOWNLOAD_DIR)
            / "test_embed.mp4"
        )


        print(
            "[APP] 入力ファイル:",
            input_path,
            flush=True
        )

        print(
            "[APP] 出力ファイル:",
            output_path,
            flush=True
        )


        # =====================================
        # MP4存在確認
        # =====================================

        print(
            "[APP] MP4存在確認 START",
            flush=True
        )


        if not input_path.exists():

            raise FileNotFoundError(
                "入力ファイルが存在しません: "
                f"{input_path}"
            )


        if not input_path.is_file():

            raise FileNotFoundError(
                "入力パスがファイルではありません: "
                f"{input_path}"
            )


        input_size = (
            input_path.stat().st_size
        )


        print(
            "[APP] MP4存在確認 OK",
            flush=True
        )

        print(
            f"[APP] 入力サイズ: "
            f"{input_size} bytes",
            flush=True
        )


        # =====================================
        # 前回出力削除
        # =====================================

        if output_path.exists():

            print(
                "[APP] 前回のtest_embed.mp4を削除",
                flush=True
            )

            output_path.unlink()


        # =====================================
        # subtitle_test_ffmpeg import
        # =====================================

        print(
            "[APP] subtitle_test_ffmpeg "
            "import START",
            flush=True
        )


        from subtitle_test_ffmpeg import (
            run_ffmpeg_subtitle_test
        )


        print(
            "[APP] subtitle_test_ffmpeg "
            "import OK",
            flush=True
        )


        # =====================================
        # FFmpeg開始
        # =====================================

        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] FFmpeg START",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        result = run_ffmpeg_subtitle_test(
            input_path=str(input_path),
            output_path=str(output_path)
        )


        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] FFmpeg RETURN",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] result:",
            result,
            flush=True
        )


        # =====================================
        # 出力確認
        # =====================================

        print(
            "[APP] 出力ファイル確認 START",
            flush=True
        )


        if not output_path.exists():

            raise FileNotFoundError(
                "FFmpegは終了しましたが、"
                "出力ファイルが存在しません: "
                f"{output_path}"
            )


        if not output_path.is_file():

            raise FileNotFoundError(
                "出力パスがファイルではありません: "
                f"{output_path}"
            )


        output_size = (
            output_path.stat().st_size
        )


        print(
            "[APP] 出力ファイル確認 OK",
            flush=True
        )

        print(
            f"[APP] 出力サイズ: "
            f"{output_size} bytes",
            flush=True
        )


        # =====================================
        # 成功
        # =====================================

        message = (
            "【字幕FFmpegテスト完了】\n\n"
            "FFmpeg終了\n\n"
            f"入力ファイル:\n"
            f"{input_path}\n\n"
            f"入力サイズ:\n"
            f"{input_size} bytes\n\n"
            f"出力ファイル:\n"
            f"{output_path}\n\n"
            f"出力サイズ:\n"
            f"{output_size} bytes"
        )


        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] /subtitle-test/ffmpeg SUCCESS",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        return (
            message,
            200,
            {
                "Content-Type":
                    "text/plain; charset=utf-8"
            }
        )


    except Exception as error:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] /subtitle-test/ffmpeg FAILED",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] ERROR TYPE:",
            type(error).__name__,
            flush=True
        )

        print(
            "[APP] ERROR:",
            str(error),
            flush=True
        )


        print(
            "[APP] TRACEBACK START",
            flush=True
        )

        traceback.print_exc()

        print(
            "[APP] TRACEBACK END",
            flush=True
        )


        message = (
            "【字幕FFmpegテスト失敗】\n\n"
            "字幕FFmpegテストに失敗しました。\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}\n\n"
            "サーバーログにもTracebackを出力しました。"
        )


        return (
            message,
            500,
            {
                "Content-Type":
                    "text/plain; charset=utf-8"
            }
        )


# =====================================
# フォントテスト
#
# /subtitle-test/fonts
#
# app.py
#   ↓
# subtitle_test_fonts.py
#   ↓
# subtitle_font.py
#   ↓
# FFmpeg
#
# =====================================

@app.route(
    "/subtitle-test/fonts",
    methods=["POST"]
)
def subtitle_test_fonts_route():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] /subtitle-test/fonts START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    try:

        input_path = (
            Path(DOWNLOAD_DIR)
            / "test.mp4"
        )

        output_path = (
            Path(DOWNLOAD_DIR)
            / "test_embed_fonts.mp4"
        )


        print(
            "[APP] FONT TEST input:",
            input_path,
            flush=True
        )

        print(
            "[APP] FONT TEST output:",
            output_path,
            flush=True
        )


        if not input_path.exists():

            raise FileNotFoundError(
                "入力ファイルが存在しません: "
                f"{input_path}"
            )


        if not input_path.is_file():

            raise FileNotFoundError(
                "入力パスがファイルではありません: "
                f"{input_path}"
            )


        input_size = (
            input_path.stat().st_size
        )


        if output_path.exists():

            print(
                "[APP] FONT TEST "
                "前回出力削除",
                flush=True
            )

            output_path.unlink()


        print(
            "[APP] subtitle_test_fonts "
            "import START",
            flush=True
        )


        from subtitle_test_fonts import (
            run_font_test
        )


        print(
            "[APP] subtitle_test_fonts "
            "import OK",
            flush=True
        )


        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] FONT TEST START",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        result = run_font_test(
            input_path=str(input_path),
            output_path=str(output_path)
        )


        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] FONT TEST RETURN",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        print(
            "[APP] FONT TEST result:",
            result,
            flush=True
        )


        if not output_path.exists():

            raise FileNotFoundError(
                "フォントテスト終了後も"
                "出力ファイルがありません: "
                f"{output_path}"
            )


        if not output_path.is_file():

            raise FileNotFoundError(
                "フォントテスト出力が"
                "ファイルではありません: "
                f"{output_path}"
            )


        output_size = (
            output_path.stat().st_size
        )


        message = (
            "【字幕フォントFFmpegテスト完了】\n\n"
            "フォントを指定した字幕FFmpeg処理が"
            "正常終了しました。\n\n"
            f"入力ファイル:\n"
            f"{input_path}\n\n"
            f"入力サイズ:\n"
            f"{input_size} bytes\n\n"
            f"出力ファイル:\n"
            f"{output_path}\n\n"
            f"出力サイズ:\n"
            f"{output_size} bytes"
        )


        print(
            "[APP] /subtitle-test/fonts SUCCESS",
            flush=True
        )


        return (
            message,
            200,
            {
                "Content-Type":
                    "text/plain; charset=utf-8"
            }
        )


    except Exception as error:

        print(
            "[APP] /subtitle-test/fonts FAILED",
            flush=True
        )

        print(
            "[APP] FONT TEST ERROR TYPE:",
            type(error).__name__,
            flush=True
        )

        print(
            "[APP] FONT TEST ERROR:",
            str(error),
            flush=True
        )

        traceback.print_exc()


        message = (
            "【字幕フォントFFmpegテスト失敗】\n\n"
            "字幕フォントFFmpegテストに"
            "失敗しました。\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}\n\n"
            "サーバーログにもTracebackを"
            "出力しました。"
        )


        return (
            message,
            500,
            {
                "Content-Type":
                    "text/plain; charset=utf-8"
            }
        )


# =====================================
# Routes確認
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] Registered routes",
    flush=True
)

print(
    "==========================================",
    flush=True
)


for rule in app.url_map.iter_rules():

    print(
        rule,
        "->",
        rule.endpoint,
        flush=True
    )


print(
    "==========================================",
    flush=True
)


# =====================================
# READY
# =====================================

print(
    "==========================================",
    flush=True
)

print(
    "[APP] app.py READY",
    flush=True
)

print(
    "[APP] FFmpegはまだ実行していません",
    flush=True
)

print(
    "==========================================",
    flush=True
)


# =====================================
# 起動
# =====================================

if __name__ == "__main__":

    print(
        "[APP] Starting Flask server",
        flush=True
    )


    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
