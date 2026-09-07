# =====================================
# YouTube Converter
# app.py
#
# アプリケーションの入口
#
# 役割:
# ・Flaskアプリ起動
# ・各routes登録
# ・設定読み込み
#
# タブ1:
# ・YouTube URL
# ・動画情報取得
# ・MP3 / MP4変換
# ・Job監視
# ・MP3完成後のSRT / Gemini処理
#
# タブ2:
# ・ファイル変換
# ・MP3アップロード → SRT
# ・MP4アップロード
# ・SRTアップロード
# ・MP4 + SRT → 字幕MP4
#
# 完成ファイル確認:
# ・/find-completed-files
#
# 単体テスト:
# ・/test
# ・/subtitle-test
#
# 注意:
# ・converter.js / subtitle.js の処理は
#   このファイルでは直接行わない。
# ・subtitle_test.py は Flask から呼び出す
#   単体テスト用モジュールとして使用する。
# =====================================


import os
import sys
import traceback
from pathlib import Path


from flask import (
    Flask,
    render_template,
    request,
    jsonify
)


import config


from routes.index import register_index
from routes.files import register_files
from routes.convert import register_convert
from routes.check import register_video_info, register_check
from routes.gemini import register_gemini
from routes.completed_files import register_completed_files

# subtitle_routes.py は Blueprint方式
from routes.subtitle_routes import subtitle_bp


# =====================================
# subtitle_test.py
#
# 単体テスト専用処理
# =====================================

try:

    import subtitle_test

    print(
        "[APP] subtitle_test.py loaded",
        flush=True
    )

except Exception as error:

    subtitle_test = None

    print(
        "[APP] subtitle_test.py load failed:",
        error,
        flush=True
    )

    traceback.print_exc()


# =====================================
# Flask
# =====================================

app = Flask(__name__)


# =====================================
# プロジェクト設定
# =====================================

BASE_DIR = config.BASE_DIR

DOWNLOAD_DIR = config.DOWNLOAD_DIR


# =====================================
# Routes登録開始
# =====================================

print("==========================================")
print("[APP] Registering routes")
print("==========================================")


# -------------------------------------
# index
# -------------------------------------

register_index(app)


# -------------------------------------
# files
# -------------------------------------

register_files(app)


# -------------------------------------
# convert
# -------------------------------------

register_convert(app)


# -------------------------------------
# video-info / check
# -------------------------------------

register_video_info(app)

register_check(app)


# -------------------------------------
# Gemini / SRT
# -------------------------------------

register_gemini(app)


# -------------------------------------
# subtitle
#
# subtitle_routes.py は Blueprint方式。
#
# タブ2:
#
# MP3アップロード
#     ↓
# Gemini
#     ↓
# SRT
#
# MP4アップロード
# SRTアップロード
#     ↓
# MP4 + SRT
#     ↓
# 字幕付きMP4
#
# -------------------------------------

app.register_blueprint(
    subtitle_bp
)


# -------------------------------------
# completed files
#
# POST /find-completed-files
#
# completed_files.py に処理を分離
# -------------------------------------

register_completed_files(
    app
)


# =====================================
# test route
#
# Flaskのルートが正常に動作しているか
# 確認するためのテスト用ルート。
#
# ブラウザ:
#
# https://y2conv-main.onrender.com/test
#
# 正常:
#
# TEST OK
#
# -------------------------------------

@app.route("/test")
def test_page():

    print(
        "★ /test が呼ばれました ★",
        flush=True
    )

    return "TEST OK"


# =====================================
# subtitle test
#
# 単体テスト画面
#
# templates/test.html を表示する。
#
# ブラウザ:
#
# https://y2conv-main.onrender.com/subtitle-test
#
# -------------------------------------

@app.route("/subtitle-test")
def subtitle_test_page():

    print(
        "★ /subtitle-test が呼ばれました ★",
        flush=True
    )

    return render_template(
        "test.html"
    )


# =====================================
# subtitle test
#
# 共通エラー処理
# =====================================

def subtitle_test_error_response(
    message,
    error=None,
    status_code=500
):
    """
    subtitle_test API用のエラー処理。
    """

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE_TEST_API] ERROR",
        flush=True
    )

    print(
        message,
        flush=True
    )

    if error is not None:

        print(
            "[SUBTITLE_TEST_API] TYPE:",
            type(error).__name__,
            flush=True
        )

        print(
            "[SUBTITLE_TEST_API] ERROR:",
            str(error),
            flush=True
        )

        traceback.print_exc()

    print(
        "==========================================",
        flush=True
    )

    return jsonify(
        {
            "success": False,
            "error": message,
            "detail": (
                str(error)
                if error is not None
                else None
            )
        }
    ), status_code


# =====================================
# subtitle test
#
# subtitle_test.py確認
# =====================================

def get_subtitle_test_module():

    if subtitle_test is None:

        raise RuntimeError(
            "subtitle_test.pyを読み込めませんでした。"
        )

    return subtitle_test


# =====================================
# STEP 1
# MP4アップロード
#
# POST:
# /subtitle-test/upload-mp4
#
# form-data:
# file=<MP4>
# =====================================

@app.route(
    "/subtitle-test/upload-mp4",
    methods=["POST"]
)
def subtitle_test_upload_mp4():

    print(
        "★ /subtitle-test/upload-mp4 ★",
        flush=True
    )

    try:

        module = (
            get_subtitle_test_module()
        )

        uploaded_file = (
            request.files.get("file")
        )

        if uploaded_file is None:

            return subtitle_test_error_response(
                "MP4ファイルが送信されていません。",
                status_code=400
            )

        filename = (
            uploaded_file.filename
        )

        print(
            "[SUBTITLE_TEST_API] MP4:",
            filename,
            flush=True
        )

        if not filename:

            return subtitle_test_error_response(
                "MP4ファイル名が空です。",
                status_code=400
            )

        # ---------------------------------
        # 一時保存
        # ---------------------------------

        temp_dir = (
            Path(
                DOWNLOAD_DIR
            ).resolve()
            /
            ".subtitle_test_tmp"
        )

        temp_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        safe_name = (
            module.safe_filename(
                filename
            )
        )

        temp_path = (
            temp_dir
            /
            safe_name
        )

        uploaded_file.save(
            str(temp_path)
        )

        print(
            "[SUBTITLE_TEST_API] temporary:",
            temp_path,
            flush=True
        )

        # ---------------------------------
        # downloadsへ保存
        # ---------------------------------

        saved_path = (
            module.save_file(
                temp_path,
                ".mp4"
            )
        )

        # ---------------------------------
        # 一時ファイル削除
        # ---------------------------------

        try:

            temp_path.unlink(
                missing_ok=True
            )

        except Exception as cleanup_error:

            print(
                "[SUBTITLE_TEST_API] "
                "temporary file cleanup failed:",
                cleanup_error,
                flush=True
            )

        # ---------------------------------
        # 完了
        # ---------------------------------

        print(
            "[SUBTITLE_TEST_API] MP4 saved:",
            saved_path,
            flush=True
        )

        return jsonify(
            {
                "success": True,
                "message": "MP4の保存に成功しました。",
                "filename": saved_path.name,
                "path": str(saved_path),
                "size": saved_path.stat().st_size
            }
        )


    except Exception as error:

        return subtitle_test_error_response(
            "MP4保存に失敗しました。",
            error
        )


# =====================================
# STEP 2
# SRTアップロード
#
# POST:
# /subtitle-test/upload-srt
#
# form-data:
# file=<SRT>
# =====================================

@app.route(
    "/subtitle-test/upload-srt",
    methods=["POST"]
)
def subtitle_test_upload_srt():

    print(
        "★ /subtitle-test/upload-srt ★",
        flush=True
    )

    try:

        module = (
            get_subtitle_test_module()
        )

        uploaded_file = (
            request.files.get("file")
        )

        if uploaded_file is None:

            return subtitle_test_error_response(
                "SRTファイルが送信されていません。",
                status_code=400
            )

        filename = (
            uploaded_file.filename
        )

        print(
            "[SUBTITLE_TEST_API] SRT:",
            filename,
            flush=True
        )

        if not filename:

            return subtitle_test_error_response(
                "SRTファイル名が空です。",
                status_code=400
            )

        # ---------------------------------
        # 一時保存
        # ---------------------------------

        temp_dir = (
            Path(
                DOWNLOAD_DIR
            ).resolve()
            /
            ".subtitle_test_tmp"
        )

        temp_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        safe_name = (
            module.safe_filename(
                filename
            )
        )

        temp_path = (
            temp_dir
            /
            safe_name
        )

        uploaded_file.save(
            str(temp_path)
        )

        print(
            "[SUBTITLE_TEST_API] temporary:",
            temp_path,
            flush=True
        )

        # ---------------------------------
        # downloadsへ保存
        # ---------------------------------

        saved_path = (
            module.save_file(
                temp_path,
                ".srt"
            )
        )

        # ---------------------------------
        # 一時ファイル削除
        # ---------------------------------

        try:

            temp_path.unlink(
                missing_ok=True
            )

        except Exception as cleanup_error:

            print(
                "[SUBTITLE_TEST_API] "
                "temporary file cleanup failed:",
                cleanup_error,
                flush=True
            )

        # ---------------------------------
        # 完了
        # ---------------------------------

        print(
            "[SUBTITLE_TEST_API] SRT saved:",
            saved_path,
            flush=True
        )

        return jsonify(
            {
                "success": True,
                "message": "SRTの保存に成功しました。",
                "filename": saved_path.name,
                "path": str(saved_path),
                "size": saved_path.stat().st_size
            }
        )


    except Exception as error:

        return subtitle_test_error_response(
            "SRT保存に失敗しました。",
            error
        )


# =====================================
# STEP 3
# FFmpeg
#
# POST:
# /subtitle-test/ffmpeg
#
# downloads内にあるMP4とSRTを使用。
#
# 現在のtest.htmlからは
# このAPIを呼び出す。
#
# -------------------------------------
#
# MP4:
# downloads/*.mp4
#
# SRT:
# downloads/*.srt
#
# -------------------------------------
#
# 注意:
# test.htmlのSTEP 1 / STEP 2で
# 保存されたファイルを使用する。
# =====================================

@app.route(
    "/subtitle-test/ffmpeg",
    methods=["POST"]
)
def subtitle_test_ffmpeg():

    print(
        "★ /subtitle-test/ffmpeg ★",
        flush=True
    )

    try:

        module = (
            get_subtitle_test_module()
        )

        downloads_dir = (
            Path(
                DOWNLOAD_DIR
            ).resolve()
        )

        if not downloads_dir.exists():

            return subtitle_test_error_response(
                "downloadsフォルダが存在しません。",
                status_code=400
            )

        # ---------------------------------
        # MP4検索
        # ---------------------------------

        mp4_files = sorted(
            [
                path
                for path in downloads_dir.glob("*.mp4")
                if path.is_file()
                and "_sub_embed" not in path.stem
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        # ---------------------------------
        # SRT検索
        # ---------------------------------

        srt_files = sorted(
            [
                path
                for path in downloads_dir.glob("*.srt")
                if path.is_file()
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        if not mp4_files:

            return subtitle_test_error_response(
                "downloadsフォルダに入力MP4がありません。",
                status_code=400
            )

        if not srt_files:

            return subtitle_test_error_response(
                "downloadsフォルダにSRTがありません。",
                status_code=400
            )

        mp4_path = (
            mp4_files[0]
        )

        srt_path = (
            srt_files[0]
        )

        print(
            "[SUBTITLE_TEST_API] MP4:",
            mp4_path,
            flush=True
        )

        print(
            "[SUBTITLE_TEST_API] SRT:",
            srt_path,
            flush=True
        )

        # ---------------------------------
        # subtitle.py実行
        # ---------------------------------

        start_time = (
            time.monotonic()
        )

        output_path = (
            module.create_subtitle_test_mp4(
                mp4_path,
                srt_path
            )
        )

        elapsed = (
            time.monotonic()
            -
            start_time
        )

        output_path = (
            Path(
                output_path
            ).resolve()
        )

        output_size = (
            output_path.stat().st_size
        )

        print(
            "[SUBTITLE_TEST_API] "
            "FFmpeg SUCCESS:",
            output_path,
            flush=True
        )

        print(
            "[SUBTITLE_TEST_API] "
            "elapsed:",
            f"{elapsed:.1f}",
            "sec",
            flush=True
        )

        return jsonify(
            {
                "success": True,
                "message": "FFmpeg処理に成功しました。",
                "mp4": str(mp4_path),
                "srt": str(srt_path),
                "output": str(output_path),
                "filename": output_path.name,
                "size": output_size,
                "elapsed": round(
                    elapsed,
                    1
                )
            }
        )


    except Exception as error:

        return subtitle_test_error_response(
            "FFmpeg処理に失敗しました。",
            error
        )


# =====================================
# STEP 4
# 字幕MP4
#
# POST:
# /subtitle-test/create-subtitle-mp4
#
# /subtitle-test/ffmpeg と同じ処理。
#
# test.htmlではSTEP 3とSTEP 4を
# 分けて表示しているため、
# 別エンドポイントとして用意する。
# =====================================

@app.route(
    "/subtitle-test/create-subtitle-mp4",
    methods=["POST"]
)
def subtitle_test_create_subtitle_mp4():

    print(
        "★ /subtitle-test/create-subtitle-mp4 ★",
        flush=True
    )

    try:

        module = (
            get_subtitle_test_module()
        )

        downloads_dir = (
            Path(
                DOWNLOAD_DIR
            ).resolve()
        )

        if not downloads_dir.exists():

            return subtitle_test_error_response(
                "downloadsフォルダが存在しません。",
                status_code=400
            )

        # ---------------------------------
        # 入力MP4検索
        # ---------------------------------

        mp4_files = sorted(
            [
                path
                for path in downloads_dir.glob("*.mp4")
                if path.is_file()
                and "_sub_embed" not in path.stem
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        # ---------------------------------
        # SRT検索
        # ---------------------------------

        srt_files = sorted(
            [
                path
                for path in downloads_dir.glob("*.srt")
                if path.is_file()
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        if not mp4_files:

            return subtitle_test_error_response(
                "downloadsフォルダに入力MP4がありません。",
                status_code=400
            )

        if not srt_files:

            return subtitle_test_error_response(
                "downloadsフォルダにSRTがありません。",
                status_code=400
            )

        mp4_path = (
            mp4_files[0]
        )

        srt_path = (
            srt_files[0]
        )

        print(
            "[SUBTITLE_TEST_API] MP4:",
            mp4_path,
            flush=True
        )

        print(
            "[SUBTITLE_TEST_API] SRT:",
            srt_path,
            flush=True
        )

        # ---------------------------------
        # 字幕MP4作成
        # ---------------------------------

        start_time = (
            time.monotonic()
        )

        output_path = (
            module.create_subtitle_test_mp4(
                mp4_path,
                srt_path
            )
        )

        elapsed = (
            time.monotonic()
            -
            start_time
        )

        output_path = (
            Path(
                output_path
            ).resolve()
        )

        output_size = (
            output_path.stat().st_size
        )

        print(
            "[SUBTITLE_TEST_API] "
            "Subtitle MP4 SUCCESS:",
            output_path,
            flush=True
        )

        print(
            "[SUBTITLE_TEST_API] "
            "elapsed:",
            f"{elapsed:.1f}",
            "sec",
            flush=True
        )

        return jsonify(
            {
                "success": True,
                "message": "字幕MP4の作成に成功しました。",
                "mp4": str(mp4_path),
                "srt": str(srt_path),
                "output": str(output_path),
                "filename": output_path.name,
                "size": output_size,
                "elapsed": round(
                    elapsed,
                    1
                )
            }
        )


    except Exception as error:

        return subtitle_test_error_response(
            "字幕MP4処理に失敗しました。",
            error
        )


# =====================================
# 登録ルート確認
# =====================================

print("==========================================")
print("[APP] Registered routes")
print("==========================================")


for rule in app.url_map.iter_rules():

    print(
        rule,
        "->",
        rule.endpoint
    )


print("==========================================")


# =====================================
# 起動確認
# =====================================

if __name__ == "__main__":

    print("==========================================")
    print("[APP] YouTube Converter")
    print("==========================================")

    print(
        "[APP] BASE_DIR:",
        BASE_DIR
    )

    print(
        "[APP] DOWNLOAD_DIR:",
        DOWNLOAD_DIR
    )

    print("==========================================")

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=False
    )
