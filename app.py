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
import shutil
import tempfile
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
# subtitle.py
#   ↓
# FFmpeg
#
# 出力:
# /app/downloads/test_sub_embed.mp4
#
# 重要:
#
# このrouteではsubtitle.pyを直接呼ばない。
#
# subtitle_test.pyのrun_test()を使用する。
#
# ただしrun_test()内部では、
#
# save_file()
#   ↓
# downloadsへコピー
#
# を行うため、
#
# /app/downloads/test.mp4
# ↓
# /app/downloads/test.mp4
#
# とするとSameFileErrorになる。
#
# そのため入力ファイルだけを一時ディレクトリへ
# コピーしてからrun_test()へ渡す。
#
# これによりsubtitle_test.pyの
#
# STEP 1
# STEP 2
# STEP 3
#
# をそのまま実行する。
#
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

    temporary_directory = None

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
        # ファイル名取得
        # =====================================

        mp4_filename = (
            data.get("mp4_file")
            or "test.mp4"
        ).strip()

        srt_filename = (
            data.get("srt_file")
            or "test.srt"
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
        # ファイル名安全化
        #
        # パスは受け付けず、
        # downloads直下のファイルだけを使用する。
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
        # downloads内の入力ファイル
        # =====================================

        mp4_path = (
            Path(DOWNLOAD_DIR)
            / mp4_name
        )

        srt_path = (
            Path(DOWNLOAD_DIR)
            / srt_name
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
        # MP4存在確認
        # =====================================

        print(
            "[APP] MP4入力確認 START",
            flush=True
        )


        if not mp4_path.exists():

            raise FileNotFoundError(
                "MP4ファイルが存在しません: "
                f"{mp4_path}"
            )

        if not mp4_path.is_file():

            raise ValueError(
                "MP4パスが通常ファイルではありません: "
                f"{mp4_path}"
            )


        mp4_size = (
            mp4_path.stat().st_size
        )


        if mp4_size <= 0:

            raise ValueError(
                "MP4ファイルのサイズが0 bytesです: "
                f"{mp4_path}"
            )


        print(
            "[APP] MP4入力確認 OK",
            flush=True
        )

        print(
            "[APP] MP4 size:",
            mp4_size,
            "bytes",
            flush=True
        )


        # =====================================
        # SRT存在確認
        # =====================================

        print(
            "[APP] SRT入力確認 START",
            flush=True
        )


        if not srt_path.exists():

            raise FileNotFoundError(
                "SRTファイルが存在しません: "
                f"{srt_path}"
            )

        if not srt_path.is_file():

            raise ValueError(
                "SRTパスが通常ファイルではありません: "
                f"{srt_path}"
            )


        srt_size = (
            srt_path.stat().st_size
        )


        if srt_size <= 0:

            raise ValueError(
                "SRTファイルのサイズが0 bytesです: "
                f"{srt_path}"
            )


        print(
            "[APP] SRT入力確認 OK",
            flush=True
        )

        print(
            "[APP] SRT size:",
            srt_size,
            "bytes",
            flush=True
        )


        # =====================================
        # 字幕設定
        #
        # subtitle_test.py / subtitle.py側の
        # 標準設定を使用する。
        #
        # requestで渡されたfont等は、
        # このテストでは使用しない。
        # =====================================

        print(
            "[APP] subtitle settings are ignored "
            "for this test",
            flush=True
        )


        # =====================================
        # 既存出力確認
        #
        # subtitle_test.pyの
        # create_subtitle_test_mp4()は、
        # 同名出力があると _2, _3 ... を作る。
        #
        # 今回は必ず
        #
        # /app/downloads/test_sub_embed.mp4
        #
        # にするため、開始前に既存ファイルを削除する。
        # =====================================

        expected_output = (
            Path(DOWNLOAD_DIR)
            / "test_sub_embed.mp4"
        ).resolve()


        print(
            "[APP] expected output:",
            expected_output,
            flush=True
        )


        if expected_output.exists():

            if expected_output.is_file():

                print(
                    "[APP] 既存test_sub_embed.mp4を削除",
                    flush=True
                )

                expected_output.unlink()

            else:

                raise RuntimeError(
                    "test_sub_embed.mp4が通常ファイルではありません: "
                    f"{expected_output}"
                )


        # =====================================
        # 一時ディレクトリ作成
        #
        # subtitle_test.pyのrun_test()へ
        # 入力を渡すために使用する。
        #
        # downloads内の同一ファイルを渡すと
        # SameFileErrorになるため。
        # =====================================

        temporary_directory = Path(
            tempfile.mkdtemp(
                prefix="subtitle_test_"
            )
        ).resolve()


        temporary_mp4 = (
            temporary_directory
            /
            mp4_name
        )

        temporary_srt = (
            temporary_directory
            /
            srt_name
        )


        print(
            "[APP] temporary directory:",
            temporary_directory,
            flush=True
        )

        print(
            "[APP] temporary MP4:",
            temporary_mp4,
            flush=True
        )

        print(
            "[APP] temporary SRT:",
            temporary_srt,
            flush=True
        )


        # =====================================
        # テスト入力を一時ディレクトリへコピー
        #
        # ここはsubtitle_test.pyの処理を変更する
        # ためではなく、run_test()のsave_file()
        # が同一ファイルをコピーすることを防ぐため。
        # =====================================

        print(
            "[APP] subtitle_test input preparation START",
            flush=True
        )


        shutil.copy2(
            mp4_path,
            temporary_mp4
        )

        shutil.copy2(
            srt_path,
            temporary_srt
        )


        print(
            "[APP] subtitle_test input preparation OK",
            flush=True
        )


        # =====================================
        # subtitle_test.py import
        # =====================================

        print(
            "[APP] subtitle_test import START",
            flush=True
        )


        from subtitle_test import run_test


        print(
            "[APP] subtitle_test import OK",
            flush=True
        )


        # =====================================
        # subtitle_test.py 実行
        #
        # ここから先はsubtitle_test.pyの
        # run_test()を使用する。
        #
        # app.py側ではFFmpegを実行しない。
        # =====================================

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
            "[APP] MP4 argument:",
            temporary_mp4,
            flush=True
        )

        print(
            "[APP] SRT argument:",
            temporary_srt,
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


        test_result = run_test(
            str(temporary_mp4),
            str(temporary_srt)
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
            test_result,
            flush=True
        )


        # =====================================
        # subtitle_test.pyの結果確認
        # =====================================

        if not isinstance(
            test_result,
            dict
        ):

            raise RuntimeError(
                "subtitle_test.pyから不正な結果が返されました。"
            )


        if not test_result.get(
            "success"
        ):

            raise RuntimeError(
                "subtitle_test.pyで字幕テストに失敗しました: "
                + str(
                    test_result.get(
                        "error",
                        "不明なエラー"
                    )
                )
            )


        # =====================================
        # subtitle_test.py出力取得
        # =====================================

        result_output = test_result.get(
            "output"
        )


        if not result_output:

            raise RuntimeError(
                "subtitle_test.pyから出力ファイルパスが返されませんでした。"
            )


        actual_output = Path(
            result_output
        ).resolve()


        print(
            "[APP] subtitle_test output:",
            actual_output,
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
            "[APP] output file check START",
            flush=True
        )


        if not expected_output.exists():

            raise FileNotFoundError(
                "字幕MP4作成後も出力ファイルが存在しません: "
                f"{expected_output}"
            )


        if not expected_output.is_file():

            raise ValueError(
                "字幕MP4出力先が通常ファイルではありません: "
                f"{expected_output}"
            )


        output_size = (
            expected_output.stat().st_size
        )


        if output_size <= 0:

            raise RuntimeError(
                "字幕MP4のサイズが0 bytesです: "
                f"{expected_output}"
            )


        print(
            "[APP] output file check OK",
            flush=True
        )

        print(
            "[APP] output size:",
            output_size,
            "bytes",
            flush=True
        )


        # =====================================
        # 成功結果
        # =====================================

        result = {

            "success":
                True,

            "mp4":
                str(mp4_path),

            "srt":
                str(srt_path),

            "output":
                str(expected_output),

            "filename":
                expected_output.name,

            "mp4_size":
                mp4_size,

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
            "[APP] /subtitle-test SUCCESS",
            flush=True
        )

        print(
            "[APP] output:",
            expected_output,
            flush=True
        )

        print(
            "==========================================",
            flush=True
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
