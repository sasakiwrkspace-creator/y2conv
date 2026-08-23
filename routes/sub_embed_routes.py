# =====================================
# Subtitle Embed Routes
# routes/sub_embed_routes.py
#
# 役割：
#   1. MP4 / SRTをdownloadsへ保存
#   2. downloads内のMP4 + SRTをsub_embed.pyへ渡す
#   3. xxx_sub_embed.mp4を生成
#
# API：
#   POST /subtitle-upload
#   POST /subtitle-embed
# =====================================

import os
from pathlib import Path

from flask import (
    request,
    jsonify,
    send_from_directory
)

from sub_embed import embed_from_downloads


# =====================================
# パス設定
# =====================================

BASE_DIR = Path(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


DOWNLOAD_DIR = (
    BASE_DIR /
    "downloads"
)


# =====================================
# downloadsフォルダ作成
# =====================================

DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =====================================
# ログ
# =====================================

def log(message):

    print(
        "[SUB EMBED ROUTES]",
        message,
        flush=True
    )


# =====================================
# ファイル名安全化
# =====================================

def safe_filename(filename):

    if not filename:

        return None


    # パス部分を除去
    filename = Path(
        filename
    ).name


    if filename in (
        "",
        ".",
        ".."
    ):

        return None


    return filename


# =====================================
# 拡張子確認
# =====================================

def check_extension(
    filename,
    extension
):

    return (
        filename.lower()
        .endswith(extension)
    )


# =====================================
# アップロード
#
# POST /subtitle-upload
#
# form-data:
#
# file = MP4またはSRT
# =====================================

def subtitle_upload():

    log(
        "アップロードAPI開始"
    )


    # ---------------------------------
    # ファイル確認
    # ---------------------------------

    if "file" not in request.files:

        log(
            "fileがありません"
        )

        return jsonify({
            "success": False,
            "message": "ファイルが選択されていません。"
        }), 400


    uploaded_file = request.files[
        "file"
    ]


    # ---------------------------------
    # ファイル名確認
    # ---------------------------------

    filename = safe_filename(
        uploaded_file.filename
    )


    if not filename:

        return jsonify({
            "success": False,
            "message": "ファイル名がありません。"
        }), 400


    # ---------------------------------
    # 拡張子確認
    # ---------------------------------

    lower_filename = (
        filename.lower()
    )


    if not (
        lower_filename.endswith(".mp4")
        or
        lower_filename.endswith(".srt")
    ):

        log(
            f"許可されていないファイル: {filename}"
        )

        return jsonify({
            "success": False,
            "message":
                "MP4またはSRTファイルのみアップロードできます。"
        }), 400


    # ---------------------------------
    # 保存先
    # ---------------------------------

    save_path = (
        DOWNLOAD_DIR /
        filename
    )


    log(
        f"保存先: {save_path}"
    )


    # ---------------------------------
    # 保存
    # ---------------------------------

    try:

        uploaded_file.save(
            save_path
        )

    except Exception as error:

        log(
            f"保存エラー: {error}"
        )

        return jsonify({
            "success": False,
            "message":
                "ファイル保存中にエラーが発生しました。",
            "error": str(error)
        }), 500


    # ---------------------------------
    # 保存確認
    # ---------------------------------

    if not save_path.exists():

        log(
            "保存後ファイルが存在しません"
        )

        return jsonify({
            "success": False,
            "message":
                "ファイル保存を確認できませんでした。"
        }), 500


    file_size = (
        save_path.stat().st_size
    )


    log(
        f"アップロード完了: {filename}"
    )

    log(
        f"サイズ: {file_size} bytes"
    )


    # ---------------------------------
    # レスポンス
    # ---------------------------------

    return jsonify({

        "success": True,

        "message":
            "アップロードしました。",

        "filename":
            filename,

        "size":
            file_size,

        "path":
            str(save_path)

    })


# =====================================
# 字幕焼き込み
#
# POST /subtitle-embed
#
# JSON:
#
# {
#     "mp4_filename": "test.mp4",
#     "srt_filename": "test.srt"
# }
#
# または form-data
# =====================================

def subtitle_embed():

    log(
        "字幕焼き込みAPI開始"
    )


    # ---------------------------------
    # JSON / form-data取得
    # ---------------------------------

    data = request.get_json(
        silent=True
    )


    if data is None:

        data = request.form


    mp4_filename = data.get(
        "mp4_filename"
    )


    srt_filename = data.get(
        "srt_filename"
    )


    # ---------------------------------
    # ファイル名確認
    # ---------------------------------

    mp4_filename = safe_filename(
        mp4_filename
    )


    srt_filename = safe_filename(
        srt_filename
    )


    if not mp4_filename:

        return jsonify({
            "success": False,
            "message":
                "MP4ファイル名が指定されていません。"
        }), 400


    if not srt_filename:

        return jsonify({
            "success": False,
            "message":
                "SRTファイル名が指定されていません。"
        }), 400


    # ---------------------------------
    # 拡張子確認
    # ---------------------------------

    if not check_extension(
        mp4_filename,
        ".mp4"
    ):

        return jsonify({
            "success": False,
            "message":
                "MP4ファイルを指定してください。"
        }), 400


    if not check_extension(
        srt_filename,
        ".srt"
    ):

        return jsonify({
            "success": False,
            "message":
                "SRTファイルを指定してください。"
        }), 400


    # ---------------------------------
    # 入力ファイル確認
    # ---------------------------------

    mp4_path = (
        DOWNLOAD_DIR /
        mp4_filename
    )


    srt_path = (
        DOWNLOAD_DIR /
        srt_filename
    )


    if not mp4_path.exists():

        log(
            f"MP4がありません: {mp4_path}"
        )

        return jsonify({
            "success": False,
            "message":
                f"MP4ファイルがありません: {mp4_filename}"
        }), 404


    if not srt_path.exists():

        log(
            f"SRTがありません: {srt_path}"
        )

        return jsonify({
            "success": False,
            "message":
                f"SRTファイルがありません: {srt_filename}"
        }), 404


    # ---------------------------------
    # 字幕焼き込み実行
    # ---------------------------------

    try:

        output_path = embed_from_downloads(
            mp4_filename,
            srt_filename
        )

    except Exception as error:

        log(
            f"字幕焼き込みエラー: {error}"
        )

        return jsonify({

            "success": False,

            "message":
                "字幕焼き込みに失敗しました。",

            "error":
                str(error)

        }), 500


    # ---------------------------------
    # 出力確認
    # ---------------------------------

    output_path = Path(
        output_path
    )


    if not output_path.exists():

        return jsonify({

            "success": False,

            "message":
                "出力ファイルが作成されませんでした。"

        }), 500


    output_filename = (
        output_path.name
    )


    output_size = (
        output_path.stat().st_size
    )


    log(
        "字幕焼き込み完了"
    )

    log(
        f"出力: {output_filename}"
    )

    log(
        f"サイズ: {output_size} bytes"
    )


    # ---------------------------------
    # レスポンス
    # ---------------------------------

    return jsonify({

        "success": True,

        "message":
            "字幕焼き込みが完了しました。",

        "filename":
            output_filename,

        "size":
            output_size,

        "download_url":
            "/subtitle-download/"
            + output_filename

    })


# =====================================
# 字幕焼き込み後MP4ダウンロード
#
# GET /subtitle-download/<filename>
# =====================================

def subtitle_download(
    filename
):

    filename = safe_filename(
        filename
    )


    if not filename:

        return jsonify({
            "success": False,
            "message":
                "ファイル名が指定されていません。"
        }), 400


    file_path = (
        DOWNLOAD_DIR /
        filename
    )


    if not file_path.exists():

        return jsonify({
            "success": False,
            "message":
                "ファイルがありません。"
        }), 404


    return send_from_directory(

        DOWNLOAD_DIR,

        filename,

        as_attachment=True

    )


# =====================================
# Route登録
# =====================================

def register_sub_embed(app):

    # ---------------------------------
    # アップロード
    # ---------------------------------

    app.add_url_rule(

        "/subtitle-upload",

        view_func=subtitle_upload,

        methods=["POST"]

    )


    # ---------------------------------
    # 字幕焼き込み
    # ---------------------------------

    app.add_url_rule(

        "/subtitle-embed",

        view_func=subtitle_embed,

        methods=["POST"]

    )


    # ---------------------------------
    # ダウンロード
    # ---------------------------------

    app.add_url_rule(

        "/subtitle-download/<path:filename>",

        view_func=subtitle_download,

        methods=["GET"]

    )


    log(
        "Subtitle Embed routes registered"
    )
