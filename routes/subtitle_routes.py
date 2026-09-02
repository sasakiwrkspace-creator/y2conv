# ==========================================================
# routes/subtitle_routes.py
#
# 字幕関連Route
#
# タブ1のYouTube変換処理とは完全分離。
#
# タブ2:
#
# MP3
#   ↓
# Gemini
#   ↓
# SRT
#
# MP4 + SRT
#   ↓
# 字幕焼き込み
#   ↓
# 字幕MP4
#
# 重要:
# ・converter.js のイベントには触れない
# ・#convertBtn には触れない
# ・タブ1の処理を登録しない
# ・同名ファイルは上書きする
# ==========================================================


import os

from flask import (
    request,
    jsonify
)

from werkzeug.utils import secure_filename

from config import DOWNLOAD_DIR

from routes.gemini import (
    transcribe_mp3,
    save_srt
)


# ==========================================================
# 保存先
# ==========================================================

DOWNLOAD_ROOT = os.path.abspath(
    DOWNLOAD_DIR
)


# ==========================================================
# 許可拡張子
# ==========================================================

ALLOWED_MP3_EXTENSIONS = {
    ".mp3"
}


ALLOWED_MP4_EXTENSIONS = {
    ".mp4"
}


ALLOWED_SRT_EXTENSIONS = {
    ".srt"
}


# ==========================================================
# DOWNLOAD_DIR確認
# ==========================================================

def ensure_download_dir():

    os.makedirs(
        DOWNLOAD_ROOT,
        exist_ok=True
    )


# ==========================================================
# 拡張子取得
# ==========================================================

def get_file_extension(
    filename
):

    return os.path.splitext(
        filename
    )[1].lower()


# ==========================================================
# 安全なファイル名
#
# 同名の場合はUUIDを付けない。
# 必ず同じ名前で上書きする。
# ==========================================================

def make_safe_filename(
    filename
):

    filename = str(
        filename or ""
    ).strip()


    if not filename:

        raise ValueError(
            "ファイル名がありません"
        )


    extension = get_file_extension(
        filename
    )


    safe_name = secure_filename(
        filename
    )


    # ------------------------------------------------------
    # secure_filename()で空になった場合
    # ------------------------------------------------------

    if not safe_name:

        base_name = os.path.splitext(
            os.path.basename(
                filename
            )
        )[0]


        if not base_name:

            raise ValueError(
                "安全なファイル名を作成できませんでした"
            )


        safe_name = (
            base_name
            + extension
        )


    # ------------------------------------------------------
    # basename化
    # ------------------------------------------------------

    safe_name = os.path.basename(
        safe_name
    )


    if not safe_name:

        raise ValueError(
            "不正なファイル名です"
        )


    return safe_name


# ==========================================================
# downloadsパス
# ==========================================================

def make_download_path(
    filename
):

    ensure_download_dir()


    filename = os.path.basename(
        filename
    )


    path = os.path.abspath(
        os.path.join(
            DOWNLOAD_ROOT,
            filename
        )
    )


    # ------------------------------------------------------
    # パストラバーサル対策
    # ------------------------------------------------------

    try:

        common_path = os.path.commonpath(
            [
                DOWNLOAD_ROOT,
                path
            ]
        )

    except ValueError:

        common_path = None


    if common_path != DOWNLOAD_ROOT:

        raise ValueError(
            "不正なファイルパスです"
        )


    return path


# ==========================================================
# アップロード保存
#
# 重要:
#
# 同名ファイルが存在してもUUIDを付けない。
#
# タブ2で a.mp3 を選択
# ↓
# downloads/a.mp3
# ↓
# 既存a.mp3があれば上書き
#
# ==========================================================

def save_uploaded_file(
    uploaded_file,
    allowed_extensions
):

    if uploaded_file is None:

        raise ValueError(
            "ファイルが選択されていません"
        )


    original_filename = (
        uploaded_file.filename
        or ""
    ).strip()


    if not original_filename:

        raise ValueError(
            "ファイル名がありません"
        )


    extension = get_file_extension(
        original_filename
    )


    if extension not in allowed_extensions:

        raise ValueError(
            "対応していないファイル形式です: "
            + extension
        )


    safe_filename = make_safe_filename(
        original_filename
    )


    save_path = make_download_path(
        safe_filename
    )


    # ======================================================
    # 重要:
    #
    # ここでは同名ファイルを別名にしない。
    # save() により既存ファイルを上書きする。
    # ======================================================

    print(
        "=========================================="
    )

    print(
        "[SUBTITLE] ファイル保存開始"
    )

    print(
        "[SUBTITLE] filename:",
        safe_filename
    )

    print(
        "[SUBTITLE] path:",
        save_path
    )

    if os.path.exists(save_path):

        print(
            "[SUBTITLE] 同名ファイルを上書きします"
        )

    print(
        "=========================================="
    )


    uploaded_file.save(
        save_path
    )


    # ------------------------------------------------------
    # 保存確認
    # ------------------------------------------------------

    if not os.path.exists(
        save_path
    ):

        raise IOError(
            "ファイルの保存に失敗しました"
        )


    if not os.path.isfile(
        save_path
    ):

        raise IOError(
            "保存先がファイルではありません"
        )


    file_size = os.path.getsize(
        save_path
    )


    if file_size <= 0:

        raise ValueError(
            "保存されたファイルが0 bytesです"
        )


    print(
        "=========================================="
    )

    print(
        "[SUBTITLE] ファイル保存完了"
    )

    print(
        "[SUBTITLE] filename:",
        safe_filename
    )

    print(
        "[SUBTITLE] size:",
        file_size,
        "bytes"
    )

    print(
        "=========================================="
    )


    return {

        "filename":
            safe_filename,

        "path":
            save_path,

        "size":
            file_size

    }


# ==========================================================
# downloadsから既存ファイル取得
# ==========================================================

def get_download_file(
    filename,
    allowed_extensions
):

    filename = str(
        filename or ""
    ).strip()


    if not filename:

        raise ValueError(
            "ファイル名がありません"
        )


    filename = os.path.basename(
        filename
    )


    extension = get_file_extension(
        filename
    )


    if extension not in allowed_extensions:

        raise ValueError(
            "対応していないファイル形式です"
        )


    file_path = make_download_path(
        filename
    )


    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            "ファイルがありません: "
            + filename
        )


    if not os.path.isfile(
        file_path
    ):

        raise ValueError(
            "指定されたパスはファイルではありません"
        )


    if os.path.getsize(
        file_path
    ) <= 0:

        raise ValueError(
            "ファイルが0 bytesです"
        )


    return file_path


# ==========================================================
# MP3 → SRT
#
# タブ2から使用。
# 将来タブ1から呼び出すことも可能。
# ==========================================================

def create_srt_from_mp3(
    mp3_path
):

    mp3_path = os.path.abspath(
        mp3_path
    )


    if not os.path.exists(
        mp3_path
    ):

        raise FileNotFoundError(
            "MP3がありません: "
            + mp3_path
        )


    if not os.path.isfile(
        mp3_path
    ):

        raise ValueError(
            "指定されたパスはファイルではありません"
        )


    if not mp3_path.lower().endswith(
        ".mp3"
    ):

        raise ValueError(
            "MP3ファイルを指定してください"
        )


    print(
        "=========================================="
    )

    print(
        "[SUBTITLE] MP3 → SRT 開始"
    )

    print(
        "[SUBTITLE] MP3:",
        mp3_path
    )

    print(
        "=========================================="
    )


    # ------------------------------------------------------
    # Gemini
    # ------------------------------------------------------

    srt_text = transcribe_mp3(
        mp3_path
    )


    if not srt_text:

        raise ValueError(
            "GeminiからSRT結果を取得できませんでした"
        )


    # ------------------------------------------------------
    # SRT保存
    # ------------------------------------------------------

    srt_path = save_srt(
        mp3_path,
        srt_text
    )


    if not srt_path:

        raise IOError(
            "SRT保存処理からパスが返されませんでした"
        )


    srt_path = os.path.abspath(
        str(srt_path)
    )


    if not os.path.exists(
        srt_path
    ):

        raise IOError(
            "SRTファイルの保存に失敗しました"
        )


    print(
        "=========================================="
    )

    print(
        "[SUBTITLE] MP3 → SRT 完了"
    )

    print(
        "[SUBTITLE] SRT:",
        srt_path
    )

    print(
        "=========================================="
    )


    return {

        "mp3_file":
            os.path.basename(
                mp3_path
            ),

        "srt_file":
            os.path.basename(
                srt_path
            ),

        "srt_path":
            srt_path

    }


# ==========================================================
# MP4 + SRT → 字幕MP4
# ==========================================================

def create_subtitle_mp4(
    mp4_path,
    srt_path
):

    mp4_path = os.path.abspath(
        mp4_path
    )

    srt_path = os.path.abspath(
        srt_path
    )


    # ------------------------------------------------------
    # MP4確認
    # ------------------------------------------------------

    if not os.path.exists(
        mp4_path
    ):

        raise FileNotFoundError(
            "MP4がありません: "
            + mp4_path
        )


    if not os.path.isfile(
        mp4_path
    ):

        raise ValueError(
            "MP4のパスがファイルではありません"
        )


    if not mp4_path.lower().endswith(
        ".mp4"
    ):

        raise ValueError(
            "MP4ファイルを指定してください"
        )


    # ------------------------------------------------------
    # SRT確認
    # ------------------------------------------------------

    if not os.path.exists(
        srt_path
    ):

        raise FileNotFoundError(
            "SRTがありません: "
            + srt_path
        )


    if not os.path.isfile(
        srt_path
    ):

        raise ValueError(
            "SRTのパスがファイルではありません"
        )


    if not srt_path.lower().endswith(
        ".srt"
    ):

        raise ValueError(
            "SRTファイルを指定してください"
        )


    print(
        "=========================================="
    )

    print(
        "[SUBTITLE] MP4 + SRT 合成開始"
    )

    print(
        "[SUBTITLE] MP4:",
        mp4_path
    )

    print(
        "[SUBTITLE] SRT:",
        srt_path
    )

    print(
        "=========================================="
    )


    import subtitle


    subtitle_function = None


    if hasattr(
        subtitle,
        "create_subtitle_mp4"
    ):

        subtitle_function = (
            subtitle.create_subtitle_mp4
        )

    elif hasattr(
        subtitle,
        "create_burned_subtitle"
    ):

        subtitle_function = (
            subtitle.create_burned_subtitle
        )

    elif hasattr(
        subtitle,
        "burn_subtitles"
    ):

        subtitle_function = (
            subtitle.burn_subtitles
        )


    if subtitle_function is None:

        raise AttributeError(

            "subtitle.pyに字幕MP4作成関数がありません。"

        )


    result = subtitle_function(
        mp4_path,
        srt_path
    )


    if not result:

        raise ValueError(
            "字幕MP4作成処理から結果が返されませんでした"
        )


    result_path = os.path.abspath(
        str(result)
    )


    if not os.path.exists(
        result_path
    ):

        raise IOError(
            "字幕MP4が作成されませんでした: "
            + result_path
        )


    result_filename = os.path.basename(
        result_path
    )


    print(
        "=========================================="
    )

    print(
        "[SUBTITLE] MP4 + SRT 合成完了"
    )

    print(
        "[SUBTITLE] output:",
        result_path
    )

    print(
        "=========================================="
    )


    return {

        "mp4_file":
            os.path.basename(
                mp4_path
            ),

        "srt_file":
            os.path.basename(
                srt_path
            ),

        "subtitle_mp4_file":
            result_filename,

        "subtitle_mp4_path":
            result_path

    }


# ==========================================================
# Route登録
# ==========================================================

def register_subtitle_routes(
    app
):

    ensure_download_dir()


    # ======================================================
    # MP3アップロード + Gemini + SRT
    #
    # POST /subtitle-upload-mp3
    # ======================================================

    @app.route(
        "/subtitle-upload-mp3",
        methods=["POST"]
    )

    def subtitle_upload_mp3():

        try:

            print(
                "[SUBTITLE] MP3処理開始"
            )


            uploaded_file = request.files.get(
                "file"
            )


            saved = save_uploaded_file(

                uploaded_file,

                ALLOWED_MP3_EXTENSIONS

            )


            result = create_srt_from_mp3(
                saved["path"]
            )


            return jsonify({

                "success":
                    True,

                "message":
                    "MP3からSRTを作成しました。",

                "filename":
                    saved["filename"],

                "mp3_file":
                    saved["filename"],

                "srt_file":
                    result["srt_file"],

                "files": {

                    "mp3":
                        saved["filename"],

                    "srt":
                        result["srt_file"]

                },

                "download_url":
                    "/download/"
                    + result["srt_file"]

            })


        except Exception as e:

            print(
                "=========================================="
            )

            print(
                "[SUBTITLE] MP3処理エラー"
            )

            print(
                "TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                str(e)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500


    # ======================================================
    # MP4アップロード
    # ======================================================

    @app.route(
        "/subtitle-upload-mp4",
        methods=["POST"]
    )

    def subtitle_upload_mp4():

        try:

            uploaded_file = request.files.get(
                "file"
            )


            saved = save_uploaded_file(

                uploaded_file,

                ALLOWED_MP4_EXTENSIONS

            )


            return jsonify({

                "success":
                    True,

                "message":
                    "MP4を保存しました。",

                "filename":
                    saved["filename"],

                "mp4_file":
                    saved["filename"]

            })


        except Exception as e:

            print(
                "[SUBTITLE] MP4アップロードエラー:",
                repr(e)
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500


    # ======================================================
    # SRTアップロード
    # ======================================================

    @app.route(
        "/subtitle-upload-srt",
        methods=["POST"]
    )

    def subtitle_upload_srt():

        try:

            uploaded_file = request.files.get(
                "file"
            )


            saved = save_uploaded_file(

                uploaded_file,

                ALLOWED_SRT_EXTENSIONS

            )


            return jsonify({

                "success":
                    True,

                "message":
                    "SRTを保存しました。",

                "filename":
                    saved["filename"],

                "srt_file":
                    saved["filename"]

            })


        except Exception as e:

            print(
                "[SUBTITLE] SRTアップロードエラー:",
                repr(e)
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500


    # ======================================================
    # MP4 + SRT → 字幕MP4
    # ======================================================

    @app.route(
        "/subtitle-create-mp4",
        methods=["POST"]
    )

    def subtitle_create_mp4():

        try:

            data = request.get_json(
                silent=True
            )


            if not data:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "JSONデータがありません"

                }), 400


            mp4_filename = data.get(
                "mp4_file"
            )


            srt_filename = data.get(
                "srt_file"
            )


            if not mp4_filename:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP4ファイル名がありません"

                }), 400


            if not srt_filename:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "SRTファイル名がありません"

                }), 400


            mp4_path = get_download_file(

                mp4_filename,

                ALLOWED_MP4_EXTENSIONS

            )


            srt_path = get_download_file(

                srt_filename,

                ALLOWED_SRT_EXTENSIONS

            )


            result = create_subtitle_mp4(

                mp4_path,

                srt_path

            )


            return jsonify({

                "success":
                    True,

                "message":
                    "字幕付きMP4を作成しました。",

                "filename":
                    result["subtitle_mp4_file"],

                "mp4_file":
                    result["mp4_file"],

                "srt_file":
                    result["srt_file"],

                "subtitle_mp4_file":
                    result["subtitle_mp4_file"],

                "download_url":
                    "/download/"
                    + result["subtitle_mp4_file"],

                "files": {

                    "mp4":
                        result["mp4_file"],

                    "srt":
                        result["srt_file"],

                    "subtitle_mp4":
                        result["subtitle_mp4_file"]

                }

            })


        except FileNotFoundError as e:

            print(
                "[SUBTITLE] ファイルがありません:",
                str(e)
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 404


        except Exception as e:

            print(
                "=========================================="
            )

            print(
                "[SUBTITLE] 字幕MP4作成エラー"
            )

            print(
                "TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                str(e)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500


    print(
        "=========================================="
    )

    print(
        "[SUBTITLE] subtitle routes registered"
    )

    print(
        "[SUBTITLE] POST /subtitle-upload-mp3"
    )

    print(
        "[SUBTITLE] POST /subtitle-upload-mp4"
    )

    print(
        "[SUBTITLE] POST /subtitle-upload-srt"
    )

    print(
        "[SUBTITLE] POST /subtitle-create-mp4"
    )

    print(
        "=========================================="
    )
