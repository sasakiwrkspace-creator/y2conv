# =====================================
# YouTube Converter
# app.py
#
# YouTube時間指定ダウンロード対応版
#
# YouTube変換:
#
# /ytdown
#   ↓
# routes/ytdown.py
#   ↓
# yt-dlp / FFmpeg
#
# ファイル変換:
#
# routes/subtitle_routes.py
#   ↓
# 字幕関連処理
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

# =====================================
# 既存 convert.py
#
# 今回は変更しない。
# =====================================

from routes.convert import register_convert

from routes.check import register_video_info, register_check
from routes.gemini import register_gemini
from routes.completed_files import register_completed_files

# =====================================
# 新しいYouTube時間指定ダウンロード
# =====================================

from routes.ytdown import register_ytdown

# =====================================
# 字幕関連
# =====================================

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


print(
    "==========================================",
    flush=True
)

print(
    "[APP] app.py START",
    flush=True
)

print(
    "==========================================",
    flush=True
)


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

print(
    "==========================================",
    flush=True
)

print(
    "[APP] Registering routes",
    flush=True
)

print(
    "==========================================",
    flush=True
)


# =====================================
# index
# =====================================

print(
    "[APP] register_index START",
    flush=True
)

register_index(app)

print(
    "[APP] register_index OK",
    flush=True
)


# =====================================
# files
# =====================================

print(
    "[APP] register_files START",
    flush=True
)

register_files(app)

print(
    "[APP] register_files OK",
    flush=True
)


# =====================================
# convert
#
# 既存処理
#
# 今回は削除・変更しない。
# =====================================

print(
    "[APP] register_convert START",
    flush=True
)

register_convert(app)

print(
    "[APP] register_convert OK",
    flush=True
)


# =====================================
# YouTube時間指定ダウンロード
#
# 新規:
#
# routes/ytdown.py
#
# URL:
#
# /ytdown
#
# =====================================

print(
    "[APP] register_ytdown START",
    flush=True
)

register_ytdown(app)

print(
    "[APP] register_ytdown OK",
    flush=True
)


# =====================================
# video-info
# =====================================

print(
    "[APP] register_video_info START",
    flush=True
)

register_video_info(app)

print(
    "[APP] register_video_info OK",
    flush=True
)


# =====================================
# check
# =====================================

print(
    "[APP] register_check START",
    flush=True
)

register_check(app)

print(
    "[APP] register_check OK",
    flush=True
)


# =====================================
# Gemini
# =====================================

print(
    "[APP] register_gemini START",
    flush=True
)

register_gemini(app)

print(
    "[APP] register_gemini OK",
    flush=True
)


# =====================================
# subtitle blueprint
# =====================================

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


# =====================================
# completed files
# =====================================

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
# 現在の字幕テスト機能は
# そのまま残す。
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

        mp4_filename = data.get(
            "mp4_file"
        )

        srt_filename = data.get(
            "srt_file"
        )


        if mp4_filename is None:

            raise ValueError(
                "mp4_fileが指定されていません。"
            )


        if srt_filename is None:

            raise ValueError(
                "srt_fileが指定されていません。"
            )


        mp4_filename = str(
            mp4_filename
        ).strip()

        srt_filename = str(
            srt_filename
        ).strip()


        if not mp4_filename:

            raise ValueError(
                "mp4_fileが空です。"
            )


        if not srt_filename:

            raise ValueError(
                "srt_fileが空です。"
            )


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
        # downloads内
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
        # MP4確認
        # =====================================

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


        # =====================================
        # SRT確認
        # =====================================

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


        # =====================================
        # 既存出力確認
        # =====================================

        expected_output = (
            Path(DOWNLOAD_DIR)
            / "test_sub_embed.mp4"
        ).resolve()


        if expected_output.exists():

            if expected_output.is_file():

                expected_output.unlink()

            else:

                raise RuntimeError(
                    "test_sub_embed.mp4が通常ファイルではありません: "
                    f"{expected_output}"
                )


        # =====================================
        # 一時ディレクトリ
        # =====================================

        temporary_directory = Path(
            tempfile.mkdtemp(
                prefix="subtitle_test_"
            )
        ).resolve()


        temporary_mp4 = (
            temporary_directory
            / mp4_name
        )

        temporary_srt = (
            temporary_directory
            / srt_name
        )


        # =====================================
        # コピー
        # =====================================

        shutil.copy2(
            mp4_path,
            temporary_mp4
        )

        shutil.copy2(
            srt_path,
            temporary_srt
        )


        # =====================================
        # subtitle_test
        # =====================================

        from subtitle_test import run_test


        test_result = run_test(
            str(temporary_mp4),
            str(temporary_srt)
        )


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


        if actual_output != expected_output:

            raise RuntimeError(
                "字幕MP4の出力先が想定と異なります。\n"
                f"想定: {expected_output}\n"
                f"実際: {actual_output}"
            )


        # =====================================
        # 出力確認
        # =====================================

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
            "[APP] /subtitle-test SUCCESS",
            flush=True
        )


        return jsonify(
            result
        ), 200


    except Exception as error:

        print(
            "[APP] /subtitle-test FAILED",
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

        traceback.print_exc()


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
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg_route():

    print(
        "[APP] /subtitle-test/ffmpeg START",
        flush=True
    )

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            raise ValueError(
                "リクエストJSONがありません。"
            )


        mp4_filename = data.get(
            "mp4_file"
        )

        srt_filename = data.get(
            "srt_file"
        )


        if mp4_filename is None:

            raise ValueError(
                "mp4_fileが指定されていません。"
            )


        if srt_filename is None:

            raise ValueError(
                "srt_fileが指定されていません。"
            )


        mp4_name = Path(
            str(mp4_filename).strip()
        ).name

        srt_name = Path(
            str(srt_filename).strip()
        ).name


        if not mp4_name:

            raise ValueError(
                "MP4ファイル名を取得できません。"
            )


        if not srt_name:

            raise ValueError(
                "SRTファイル名を取得できません。"
            )


        input_path = (
            Path(DOWNLOAD_DIR)
            / mp4_name
        )

        srt_path = (
            Path(DOWNLOAD_DIR)
            / srt_name
        )


        output_path = (
            Path(DOWNLOAD_DIR)
            /
            f"{Path(mp4_name).stem}_字幕.mp4"
        )


        if not input_path.exists():

            raise FileNotFoundError(
                "入力MP4ファイルが存在しません: "
                f"{input_path}"
            )


        if not srt_path.exists():

            raise FileNotFoundError(
                "SRTファイルが存在しません: "
                f"{srt_path}"
            )


        if output_path.exists():

            if output_path.is_file():

                output_path.unlink()

            else:

                raise RuntimeError(
                    "出力パスが通常ファイルではありません: "
                    f"{output_path}"
                )


        from subtitle_test_ffmpeg import (
            run_ffmpeg_subtitle_test
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


        if not output_path.exists():

            raise FileNotFoundError(
                "FFmpeg終了後も出力ファイルが存在しません: "
                f"{output_path}"
            )


        output_size = (
            output_path.stat().st_size
        )


        if output_size <= 0:

            raise RuntimeError(
                "出力ファイルのサイズが0 bytesです: "
                f"{output_path}"
            )


        return (
            "【字幕FFmpegテスト完了】\n\n"
            f"入力ファイル:\n{input_path}\n\n"
            f"SRTファイル:\n{srt_path}\n\n"
            f"出力ファイル:\n{output_path}\n\n"
            f"出力サイズ:\n{output_size} bytes",
            200,
            {
                "Content-Type":
                    "text/plain; charset=utf-8"
            }
        )


    except Exception as error:

        print(
            "[APP] /subtitle-test/ffmpeg FAILED:",
            error,
            flush=True
        )

        traceback.print_exc()


        return (
            "【字幕FFmpegテスト失敗】\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
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
# =====================================

@app.route(
    "/subtitle-test/fonts",
    methods=["POST"]
)
def subtitle_test_fonts_route():

    print(
        "[APP] /subtitle-test/fonts START",
        flush=True
    )


    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            raise ValueError(
                "リクエストJSONがありません。"
            )


        mp4_filename = data.get(
            "mp4_file"
        )


        if mp4_filename is None:

            raise ValueError(
                "mp4_fileが指定されていません。"
            )


        mp4_name = Path(
            str(mp4_filename).strip()
        ).name


        if not mp4_name:

            raise ValueError(
                "MP4ファイル名を取得できません。"
            )


        input_path = (
            Path(DOWNLOAD_DIR)
            / mp4_name
        )


        output_path = (
            Path(DOWNLOAD_DIR)
            /
            f"{Path(mp4_name).stem}_embed_fonts.mp4"
        )


        if not input_path.exists():

            raise FileNotFoundError(
                "入力ファイルが存在しません: "
                f"{input_path}"
            )


        if output_path.exists():

            if output_path.is_file():

                output_path.unlink()

            else:

                raise RuntimeError(
                    "出力パスが通常ファイルではありません: "
                    f"{output_path}"
                )


        from subtitle_test_fonts import (
            run_font_test
        )


        result = run_font_test(
            input_path=str(
                input_path
            ),
            output_path=str(
                output_path
            )
        )


        if not output_path.exists():

            raise FileNotFoundError(
                "フォントテスト終了後も"
                "出力ファイルがありません: "
                f"{output_path}"
            )


        output_size = (
            output_path.stat().st_size
        )


        if output_size <= 0:

            raise RuntimeError(
                "フォントテスト出力のサイズが0 bytesです: "
                f"{output_path}"
            )


        return (
            "【字幕フォントFFmpegテスト完了】\n\n"
            f"入力ファイル:\n{input_path}\n\n"
            f"出力ファイル:\n{output_path}\n\n"
            f"出力サイズ:\n{output_size} bytes",
            200,
            {
                "Content-Type":
                    "text/plain; charset=utf-8"
            }
        )


    except Exception as error:

        print(
            "[APP] /subtitle-test/fonts FAILED:",
            error,
            flush=True
        )

        traceback.print_exc()


        return (
            "【字幕フォントFFmpegテスト失敗】\n\n"
            f"ERROR TYPE:\n"
            f"{type(error).__name__}\n\n"
            f"ERROR:\n"
            f"{error}",
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
    "[APP] YouTube時間指定ダウンロード: /ytdown",
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
