# =====================================
# YouTube Converter
# app.py
#
# FFmpeg字幕テスト切り分け版
#
# テスト:
#
# /subtitle-test
#   ↓
# subtitle_test.py
#
# /subtitle-test/ffmpeg
#   ↓
# subtitle_test_ffmpeg.py
#
# /subtitle-test/fonts
#   ↓
# subtitle_test_fonts.py
#
# =====================================

import os
import traceback
from pathlib import Path

from flask import Flask, render_template, request, jsonify

import config

from routes.index import register_index
from routes.files import register_files
from routes.convert import register_convert
from routes.check import register_video_info, register_check
from routes.gemini import register_gemini
from routes.completed_files import register_completed_files

from routes.subtitle_routes import subtitle_bp


# =====================================
# Flask
# =====================================

app = Flask(__name__)


# =====================================
# 設定
# =====================================

BASE_DIR = config.BASE_DIR
DOWNLOAD_DIR = config.DOWNLOAD_DIR


print("==========================================", flush=True)
print("[APP] app.py START", flush=True)
print("==========================================", flush=True)

print(
    "[APP] BASE_DIR:",
    BASE_DIR,
    flush=True
)

print(
    "[APP] DOWNLOAD_DIR:",
    DOWNLOAD_DIR,
    flush=True
)


# =====================================
# Routes登録
# =====================================

print("==========================================", flush=True)
print("[APP] Registering routes", flush=True)
print("==========================================", flush=True)


# -------------------------------------
# index
# -------------------------------------

print(
    "[APP] register_index START",
    flush=True
)

register_index(app)

print(
    "[APP] register_index OK",
    flush=True
)


# -------------------------------------
# files
# -------------------------------------

print(
    "[APP] register_files START",
    flush=True
)

register_files(app)

print(
    "[APP] register_files OK",
    flush=True
)


# -------------------------------------
# convert
# -------------------------------------

print(
    "[APP] register_convert START",
    flush=True
)

register_convert(app)

print(
    "[APP] register_convert OK",
    flush=True
)


# -------------------------------------
# video-info
# -------------------------------------

print(
    "[APP] register_video_info START",
    flush=True
)

register_video_info(app)

print(
    "[APP] register_video_info OK",
    flush=True
)


# -------------------------------------
# check
# -------------------------------------

print(
    "[APP] register_check START",
    flush=True
)

register_check(app)

print(
    "[APP] register_check OK",
    flush=True
)


# -------------------------------------
# Gemini
# -------------------------------------

print(
    "[APP] register_gemini START",
    flush=True
)

register_gemini(app)

print(
    "[APP] register_gemini OK",
    flush=True
)


# -------------------------------------
# subtitle blueprint
# -------------------------------------

print(
    "[APP] subtitle_bp register START",
    flush=True
)

app.register_blueprint(
    subtitle_bp
)

print(
    "[APP] subtitle_bp register OK",
    flush=True
)


# -------------------------------------
# completed files
# -------------------------------------

print(
    "[APP] register_completed_files START",
    flush=True
)

register_completed_files(app)

print(
    "[APP] register_completed_files OK",
    flush=True
)


# =====================================
# /test
# =====================================

@app.route("/test")
def test_page():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] /test START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return render_template(
        "test.html"
    )


# =====================================
# 字幕MP4テスト本体
#
# /subtitle-test
#
# app.py
#   ↓
# subtitle_test.py
#   ↓
# run_test()
#   ↓
# ① MP4保存
# ② SRT保存
# ③ 字幕MP4作成
#
# subtitle_test.py の仕様を優先する
# =====================================

@app.route(
    "/subtitle-test",
    methods=["POST"]
)
def subtitle_test_route():

    print(
        "==========================================",
        flush=True
    )

    print(
        "[APP] /subtitle-test START",
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
            "[APP] /subtitle-test request:",
            data,
            flush=True
        )


        # =====================================
        # ファイル名
        # =====================================

        mp4_filename = (
            data.get("mp4_file")
            or ""
        ).strip()

        srt_filename = (
            data.get("srt_file")
            or ""
        ).strip()


        if not mp4_filename:

            raise ValueError(
                "mp4_fileが指定されていません。"
            )


        if not srt_filename:

            raise ValueError(
                "srt_fileが指定されていません。"
            )


        # =====================================
        # ファイル名だけにする
        # =====================================

        mp4_filename = Path(
            mp4_filename
        ).name

        srt_filename = Path(
            srt_filename
        ).name


        # =====================================
        # downloads確認
        # =====================================

        mp4_path = (
            Path(DOWNLOAD_DIR)
            / mp4_filename
        )

        srt_path = (
            Path(DOWNLOAD_DIR)
            / srt_filename
        )


        print(
            "[APP] subtitle test MP4:",
            mp4_path,
            flush=True
        )

        print(
            "[APP] subtitle test SRT:",
            srt_path,
            flush=True
        )


        # =====================================
        # 入力ファイル確認
        # =====================================

        if not mp4_path.exists():

            raise FileNotFoundError(
                "MP4ファイルが存在しません: "
                f"{mp4_path}"
            )


        if not mp4_path.is_file():

            raise ValueError(
                "MP4ファイルが通常ファイルではありません: "
                f"{mp4_path}"
            )


        if not srt_path.exists():

            raise FileNotFoundError(
                "SRTファイルが存在しません: "
                f"{srt_path}"
            )


        if not srt_path.is_file():

            raise ValueError(
                "SRTファイルが通常ファイルではありません: "
                f"{srt_path}"
            )


        # =====================================
        # ファイルサイズ
        # =====================================

        mp4_size = mp4_path.stat().st_size
        srt_size = srt_path.stat().st_size


        print(
            "[APP] MP4 size:",
            mp4_size,
            "bytes",
            flush=True
        )

        print(
            "[APP] SRT size:",
            srt_size,
            "bytes",
            flush=True
        )


        # =====================================
        # subtitle_test.py import
        # =====================================

        print(
            "[APP] subtitle_test import START",
            flush=True
        )


        from subtitle_test import (
            run_test
        )


        print(
            "[APP] subtitle_test import OK",
            flush=True
        )


        # =====================================
        # run_test() に渡す入力
        #
        # 重要:
        # run_test() は入力ファイルを
        # downloadsへコピーする仕様。
        #
        # そのため downloads内の同じファイルを
        # 直接渡すと SameFileError になる。
        #
        # 一時入力ファイルを作成する。
        # =====================================

        import tempfile
        import shutil


        temp_dir = Path(
            tempfile.mkdtemp(
                prefix="subtitle_test_"
            )
        )


        temp_mp4_path = (
            temp_dir
            / mp4_filename
        )

        temp_srt_path = (
            temp_dir
            / srt_filename
        )


        print(
            "[APP] temporary directory:",
            temp_dir,
            flush=True
        )

        print(
            "[APP] temporary MP4:",
            temp_mp4_path,
            flush=True
        )

        print(
            "[APP] temporary SRT:",
            temp_srt_path,
            flush=True
        )


        try:

            # =================================
            # downloads → 一時ファイル
            # =================================

            shutil.copy2(
                mp4_path,
                temp_mp4_path
            )

            shutil.copy2(
                srt_path,
                temp_srt_path
            )


            print(
                "[APP] temporary input files created",
                flush=True
            )


            # =================================
            # subtitle_test.py 実行
            # =================================

            print(
                "==========================================",
                flush=True
            )

            print(
                "[APP] subtitle_test.py START",
                flush=True
            )

            print(
                "[APP] function: run_test()",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            result = run_test(

                str(temp_mp4_path),

                str(temp_srt_path)

            )


            print(
                "==========================================",
                flush=True
            )

            print(
                "[APP] subtitle_test.py RETURN",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )


            print(
                "[APP] subtitle_test result:",
                result,
                flush=True
            )


        finally:

            # =================================
            # 一時ファイル削除
            # =================================

            try:

                shutil.rmtree(
                    temp_dir
                )

                print(
                    "[APP] temporary directory removed:",
                    temp_dir,
                    flush=True
                )

            except Exception as cleanup_error:

                print(
                    "[APP] temporary directory cleanup failed:",
                    cleanup_error,
                    flush=True
                )


        # =====================================
        # 結果確認
        # =====================================

        if result is None:

            raise RuntimeError(
                "subtitle_test.pyから結果が返されませんでした。"
            )


        if not isinstance(
            result,
            dict
        ):

            return jsonify({

                "success":
                    True,

                "filename":
                    str(result)

            }), 200


        if result.get(
            "success"
        ) is False:

            return jsonify(
                result
            ), 500


        # =====================================
        # subtitle_test.py の戻り値を優先
        # =====================================

        output_path = (
            result.get("output")
            or ""
        )


        if output_path:

            output_file = Path(
                output_path
            ).resolve()

            if output_file.exists():

                result.setdefault(
                    "filename",
                    output_file.name
                )


        result.setdefault(
            "success",
            True
        )


        return jsonify(
            result
        ), 200


    except Exception as error:

        print(
            "==========================================",
            flush=True
        )

        print(
            "[APP] /subtitle-test FAILED",
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
