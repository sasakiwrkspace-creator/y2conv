# ==========================================================
# routes/subtitle_routes.py
#
# 字幕関連Route
#
# ==========================================================
#
# タブ2:
#
# MP3アップロード
#     ↓
# downloadsへ保存
#     ↓
# Gemini
#     ↓
# SRT作成
#
#
# タブ2:
#
# MP4アップロード
# SRTアップロード
#     ↓
# downloadsから取得
#     ↓
# subtitle.py
#     ↓
# 字幕付きMP4作成
#
#
# タブ1:
#
# converter.js / routes/convert.py
#     ↓
# MP4作成
#     ↓
# MP3作成
#     ↓
# create_srt_from_mp3()
#     ↓
# Gemini
#     ↓
# create_subtitle_mp4()
#     ↓
# subtitle.py
#
# ==========================================================
#
# このファイルではタブ1のRouteを登録しない。
#
# 登録するRoute:
#
# /subtitle-upload-mp3
# /subtitle-upload-mp4
# /subtitle-upload-srt
# /subtitle-create-srt
# /subtitle-create-mp4
# /subtitle-download-mp3
#
# 登録しない:
#
# /convert
# /status/<job_id>
# /video-info
#
# ==========================================================


import os


from flask import (
    request,
    jsonify,
    send_from_directory
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
    str(
        DOWNLOAD_DIR
    )
)


# ==========================================================
# 許可する拡張子
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
# ファイル拡張子取得
# ==========================================================

def get_file_extension(
    filename
):

    return os.path.splitext(
        str(
            filename or ""
        )
    )[1].lower()


# ==========================================================
# 安全なファイル名作成
#
# 日本語ファイル名対応。
#
# secure_filename()だけに任せると、
# 日本語部分が消えて拡張子まで失われる場合があるため、
# 拡張子を最後に必ず付け直す。
# ==========================================================

def make_safe_filename(
    filename,
    extension=None
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

    original_extension = (
        get_file_extension(
            filename
        )
    )

    if extension:

        extension = str(
            extension
        ).lower()

    else:

        extension = original_extension

    if not extension:

        raise ValueError(
            "ファイル拡張子がありません"
        )

    # ---------------------------------
    # 元のbasename
    # ---------------------------------

    original_stem = os.path.splitext(
        filename
    )[0]

    # ---------------------------------
    # secure_filename
    # ---------------------------------

    safe_name = secure_filename(
        filename
    )

    # ---------------------------------
    # secure_filenameで拡張子が消えた
    # または違う拡張子になった場合
    # ---------------------------------

    safe_extension = get_file_extension(
        safe_name
    )

    if safe_extension != extension:

        safe_stem = os.path.splitext(
            safe_name
        )[0]

        if not safe_stem:

            safe_stem = secure_filename(
                original_stem
            )

        if not safe_stem:

            # 日本語などでsecure_filenameが
            # 完全に空になる場合
            safe_stem = original_stem

        safe_name = (
            safe_stem
            +
            extension
        )

    # ---------------------------------
    # 最終的なbasename
    # ---------------------------------

    safe_name = os.path.basename(
        safe_name
    )

    if not safe_name:

        raise ValueError(
            "安全なファイル名を作成できませんでした"
        )

    # ---------------------------------
    # 最終的に正しい拡張子を保証
    # ---------------------------------

    if get_file_extension(
        safe_name
    ) != extension:

        safe_stem = os.path.splitext(
            safe_name
        )[0]

        if not safe_stem:

            safe_stem = original_stem

        safe_name = (
            safe_stem
            +
            extension
        )

    return safe_name


# ==========================================================
# downloads内の保存先
# ==========================================================

def make_download_path(
    filename
):

    ensure_download_dir()

    filename = os.path.basename(
        str(
            filename
        )
    )

    if not filename:

        raise ValueError(
            "ファイル名がありません"
        )

    path = os.path.abspath(
        os.path.join(
            DOWNLOAD_ROOT,
            filename
        )
    )

    # ---------------------------------
    # パストラバーサル対策
    # ---------------------------------

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
# アップロードファイル保存
#
# 同名ファイルは上書きする。
# UUIDは付けない。
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
            +
            extension
        )

    safe_filename = make_safe_filename(

        original_filename,

        extension

    )

    save_path = make_download_path(
        safe_filename
    )

    existed = os.path.exists(
        save_path
    )

    if existed:

        print(
            "[SUBTITLE] 同名ファイルを上書き:",
            save_path,
            flush=True
        )

    uploaded_file.save(
        save_path
    )

    # ---------------------------------
    # 保存確認
    # ---------------------------------

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
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE] ファイル保存完了",
        flush=True
    )

    print(
        "[SUBTITLE] filename:",
        safe_filename,
        flush=True
    )

    print(
        "[SUBTITLE] path:",
        save_path,
        flush=True
    )

    print(
        "[SUBTITLE] size:",
        file_size,
        "bytes",
        flush=True
    )

    print(
        "[SUBTITLE] overwritten:",
        existed,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    return {

        "filename":
            safe_filename,

        "path":
            save_path,

        "size":
            file_size,

        "overwritten":
            existed

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
            +
            filename
        )

    if not os.path.isfile(
        file_path
    ):

        raise ValueError(
            "指定されたパスはファイルではありません"
        )

    file_size = os.path.getsize(
        file_path
    )

    if file_size <= 0:

        raise ValueError(
            "ファイルが0 bytesです"
        )

    return file_path


# ==========================================================
# MP3 → SRT
#
# タブ1・タブ2共通
# ==========================================================

def create_srt_from_mp3(
    mp3_path
):

    mp3_path = os.path.abspath(
        str(
            mp3_path
        )
    )

    # ---------------------------------
    # MP3確認
    # ---------------------------------

    if not os.path.exists(
        mp3_path
    ):

        raise FileNotFoundError(
            "MP3がありません: "
            +
            mp3_path
        )

    if not os.path.isfile(
        mp3_path
    ):

        raise ValueError(
            "MP3のパスがファイルではありません"
        )

    if not mp3_path.lower().endswith(
        ".mp3"
    ):

        raise ValueError(
            "MP3ファイルを指定してください"
        )

    if os.path.getsize(
        mp3_path
    ) <= 0:

        raise ValueError(
            "MP3ファイルが0 bytesです"
        )

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE] MP3 → SRT 開始",
        flush=True
    )

    print(
        "[SUBTITLE] MP3:",
        mp3_path,
        flush=True
    )

    print(
        "[SUBTITLE] MP3 size:",
        os.path.getsize(mp3_path),
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    # =====================================
    # Gemini
    # =====================================

    print(
        "[SUBTITLE] Gemini transcribe START",
        flush=True
    )

    srt_text = transcribe_mp3(
        mp3_path
    )

    if not srt_text:

        raise ValueError(
            "GeminiからSRT結果を取得できませんでした"
        )

    print(
        "[SUBTITLE] Gemini transcribe COMPLETE",
        flush=True
    )

    # =====================================
    # SRT保存
    # =====================================

    print(
        "[SUBTITLE] SRT save START",
        flush=True
    )

    srt_path = save_srt(

        mp3_path,

        srt_text

    )

    if not srt_path:

        raise IOError(
            "SRT保存先が返されませんでした"
        )

    srt_path = os.path.abspath(
        str(
            srt_path
        )
    )

    if not os.path.exists(
        srt_path
    ):

        raise IOError(
            "SRTファイルの保存に失敗しました: "
            +
            srt_path
        )

    if not os.path.isfile(
        srt_path
    ):

        raise IOError(
            "SRT保存先がファイルではありません"
        )

    if os.path.getsize(
        srt_path
    ) <= 0:

        raise ValueError(
            "SRTファイルが0 bytesです"
        )

    print(
        "[SUBTITLE] SRT save COMPLETE",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE] MP3 → SRT 完了",
        flush=True
    )

    print(
        "[SUBTITLE] SRT:",
        srt_path,
        flush=True
    )

    print(
        "[SUBTITLE] SRT size:",
        os.path.getsize(srt_path),
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
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
#
# subtitle.pyを呼び出す共通関数。
# ==========================================================

def create_subtitle_mp4(
    mp4_path,
    srt_path
):

    mp4_path = os.path.abspath(
        str(
            mp4_path
        )
    )

    srt_path = os.path.abspath(
        str(
            srt_path
        )
    )

    # =====================================
    # MP4確認
    # =====================================

    if not os.path.exists(
        mp4_path
    ):

        raise FileNotFoundError(
            "MP4がありません: "
            +
            mp4_path
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

    if os.path.getsize(
        mp4_path
    ) <= 0:

        raise ValueError(
            "MP4ファイルが0 bytesです"
        )

    # =====================================
    # SRT確認
    # =====================================

    if not os.path.exists(
        srt_path
    ):

        raise FileNotFoundError(
            "SRTがありません: "
            +
            srt_path
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

    if os.path.getsize(
        srt_path
    ) <= 0:

        raise ValueError(
            "SRTファイルが0 bytesです"
        )

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE] MP4 + SRT 合成開始",
        flush=True
    )

    print(
        "[SUBTITLE] MP4:",
        mp4_path,
        flush=True
    )

    print(
        "[SUBTITLE] MP4 size:",
        os.path.getsize(mp4_path),
        "bytes",
        flush=True
    )

    print(
        "[SUBTITLE] SRT:",
        srt_path,
        flush=True
    )

    print(
        "[SUBTITLE] SRT size:",
        os.path.getsize(srt_path),
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    # =====================================
    # subtitle.py
    # =====================================

    import subtitle

    # -------------------------------------
    # 正式関数を優先
    # -------------------------------------

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

    else:

        raise AttributeError(

            "subtitle.pyに字幕MP4作成関数がありません。"
            "create_subtitle_mp4() / "
            "create_burned_subtitle() / "
            "burn_subtitles() "
            "のいずれかを実装してください。"

        )

    print(
        "[SUBTITLE] subtitle.py function:",
        getattr(
            subtitle_function,
            "__name__",
            str(subtitle_function)
        ),
        flush=True
    )

    # =====================================
    # 字幕MP4作成
    # =====================================

    print(
        "[SUBTITLE] subtitle.py START",
        flush=True
    )

    result = subtitle_function(

        mp4_path,

        srt_path

    )

    print(
        "[SUBTITLE] subtitle.py COMPLETE",
        flush=True
    )

    if not result:

        raise ValueError(
            "字幕MP4作成処理から結果が返されませんでした"
        )

    result_path = os.path.abspath(
        str(
            result
        )
    )

    if not os.path.exists(
        result_path
    ):

        raise IOError(
            "字幕MP4が作成されませんでした: "
            +
            result_path
        )

    if not os.path.isfile(
        result_path
    ):

        raise IOError(
            "字幕MP4の出力先がファイルではありません"
        )

    result_size = os.path.getsize(
        result_path
    )

    if result_size <= 0:

        raise ValueError(
            "字幕MP4が0 bytesです"
        )

    result_filename = os.path.basename(
        result_path
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE] MP4 + SRT 合成完了",
        flush=True
    )

    print(
        "[SUBTITLE] output:",
        result_path,
        flush=True
    )

    print(
        "[SUBTITLE] output size:",
        result_size,
        "bytes",
        flush=True
    )

    print(
        "==========================================",
        flush=True
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
# Flask Route登録
# ==========================================================

def register_subtitle_routes(
    app
):

    ensure_download_dir()

    # ======================================================
    # タブ2
    # MP3アップロード → Gemini → SRT
    # ======================================================

    @app.route(
        "/subtitle-upload-mp3",
        methods=["POST"]
    )
    def subtitle_upload_mp3():

        try:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[SUBTITLE] MP3アップロード開始",
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            uploaded_file = request.files.get(
                "file"
            )

            saved = save_uploaded_file(

                uploaded_file,

                ALLOWED_MP3_EXTENSIONS

            )

            print(
                "[SUBTITLE] MP3 upload COMPLETE",
                flush=True
            )

            print(
                "[SUBTITLE] Starting Gemini processing...",
                flush=True
            )

            result = create_srt_from_mp3(

                saved["path"]

            )

            return jsonify({

                "success":
                    True,

                "message":
                    "MP3からSRTを作成しました。",

                "mp3_file":
                    saved["filename"],

                "srt_file":
                    result["srt_file"],

                "overwritten":
                    saved["overwritten"],

                "files": {

                    "mp3":
                        saved["filename"],

                    "srt":
                        result["srt_file"]

                }

            })

        except Exception as e:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[SUBTITLE] MP3処理エラー",
                flush=True
            )

            print(
                "TYPE:",
                type(e).__name__,
                flush=True
            )

            print(
                "ERROR:",
                str(e),
                flush=True
            )

            traceback_text = (
                __import__("traceback")
                .format_exc()
            )

            print(
                traceback_text,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500

    # ======================================================
    # タブ2
    # MP4アップロード
    # ======================================================

    @app.route(
        "/subtitle-upload-mp4",
        methods=["POST"]
    )
    def subtitle_upload_mp4():

        try:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[SUBTITLE] MP4アップロード開始",
                flush=True
            )

            uploaded_file = request.files.get(
                "file"
            )

            saved = save_uploaded_file(

                uploaded_file,

                ALLOWED_MP4_EXTENSIONS

            )

            print(
                "[SUBTITLE] MP4アップロード完了",
                flush=True
            )

            return jsonify({

                "success":
                    True,

                "message":
                    "MP4を保存しました。",

                "mp4_file":
                    saved["filename"],

                "filename":
                    saved["filename"],

                "overwritten":
                    saved["overwritten"]

            })

        except Exception as e:

            print(
                "[SUBTITLE] MP4アップロードエラー:",
                repr(e),
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500

    # ======================================================
    # タブ2
    # SRTアップロード
    # ======================================================

    @app.route(
        "/subtitle-upload-srt",
        methods=["POST"]
    )
    def subtitle_upload_srt():

        try:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[SUBTITLE] SRTアップロード開始",
                flush=True
            )

            uploaded_file = request.files.get(
                "file"
            )

            saved = save_uploaded_file(

                uploaded_file,

                ALLOWED_SRT_EXTENSIONS

            )

            print(
                "[SUBTITLE] SRTアップロード完了",
                flush=True
            )

            return jsonify({

                "success":
                    True,

                "message":
                    "SRTを保存しました。",

                "srt_file":
                    saved["filename"],

                "filename":
                    saved["filename"],

                "overwritten":
                    saved["overwritten"]

            })

        except Exception as e:

            print(
                "[SUBTITLE] SRTアップロードエラー:",
                repr(e),
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500

    # ======================================================
    # MP3 → SRT
    #
    # POST /subtitle-create-srt
    # ======================================================

    @app.route(
        "/subtitle-create-srt",
        methods=["POST"]
    )
    def subtitle_create_srt():

        print(
            "[SUBTITLE] POST /subtitle-create-srt",
            flush=True
        )

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

            mp3_filename = data.get(
                "mp3_file"
            )

            if not mp3_filename:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3ファイル名がありません"

                }), 400

            # --------------------------------------------
            # downloadsからMP3取得
            # --------------------------------------------

            mp3_path = get_download_file(

                mp3_filename,

                ALLOWED_MP3_EXTENSIONS

            )

            print(
                "[SUBTITLE] MP3 for SRT:",
                mp3_path,
                flush=True
            )

            # --------------------------------------------
            # Gemini → SRT
            # --------------------------------------------

            result = create_srt_from_mp3(

                mp3_path

            )

            return jsonify({

                "success":
                    True,

                "message":
                    "MP3からSRTを作成しました。",

                "mp3_file":
                    result["mp3_file"],

                "srt_file":
                    result["srt_file"],

                "files": {

                    "mp3":
                        result["mp3_file"],

                    "srt":
                        result["srt_file"]

                }

            })

        except FileNotFoundError as e:

            print(
                "[SUBTITLE] MP3がありません:",
                str(e),
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 404

        except Exception as e:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[SUBTITLE] MP3 → SRTエラー",
                flush=True
            )

            print(
                "TYPE:",
                type(e).__name__,
                flush=True
            )

            print(
                "ERROR:",
                str(e),
                flush=True
            )

            print(
                __import__("traceback").format_exc(),
                flush=True
            )

            print(
                "==========================================",
                flush=True
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

        print(
            "[SUBTITLE] POST /subtitle-create-mp4",
            flush=True
        )

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

            # --------------------------------------------
            # downloadsから取得
            # --------------------------------------------

            mp4_path = get_download_file(

                mp4_filename,

                ALLOWED_MP4_EXTENSIONS

            )

            srt_path = get_download_file(

                srt_filename,

                ALLOWED_SRT_EXTENSIONS

            )

            print(
                "[SUBTITLE] MP4:",
                mp4_path,
                flush=True
            )

            print(
                "[SUBTITLE] SRT:",
                srt_path,
                flush=True
            )

            # --------------------------------------------
            # 字幕MP4作成
            # --------------------------------------------

            result = create_subtitle_mp4(

                mp4_path,

                srt_path

            )

            return jsonify({

                "success":
                    True,

                "message":
                    "字幕付きMP4を作成しました。",

                "mp4_file":
                    result["mp4_file"],

                "srt_file":
                    result["srt_file"],

                "subtitle_mp4_file":
                    result["subtitle_mp4_file"],

                "filename":
                    result["subtitle_mp4_file"],

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
                str(e),
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 404

        except Exception as e:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[SUBTITLE] 字幕MP4作成エラー",
                flush=True
            )

            print(
                "TYPE:",
                type(e).__name__,
                flush=True
            )

            print(
                "ERROR:",
                str(e),
                flush=True
            )

            print(
                __import__("traceback").format_exc(),
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500

    # ======================================================
    # MP3ダウンロード
    #
    # GET /subtitle-download-mp3?filename=VIDEO_ID.mp3
    #
    # [MP3]▲ ボタンからここを呼び出す。
    # ======================================================

    @app.route(
        "/subtitle-download-mp3",
        methods=["GET"]
    )
    def subtitle_download_mp3():

        print(
            "[SUBTITLE] GET /subtitle-download-mp3",
            flush=True
        )

        try:

            filename = request.args.get(
                "filename",
                ""
            ).strip()

            if not filename:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3ファイル名がありません"

                }), 400

            # --------------------------------------------
            # downloads内のMP3だけ取得
            # --------------------------------------------

            mp3_path = get_download_file(

                filename,

                ALLOWED_MP3_EXTENSIONS

            )

            safe_filename = os.path.basename(
                mp3_path
            )

            print(
                "[SUBTITLE] MP3 download:",
                mp3_path,
                flush=True
            )

            # --------------------------------------------
            # MP3ダウンロード
            # --------------------------------------------

            return send_from_directory(

                DOWNLOAD_ROOT,

                safe_filename,

                as_attachment=True,

                download_name=safe_filename

            )

        except FileNotFoundError as e:

            print(
                "[SUBTITLE] MP3 download 404:",
                str(e),
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 404

        except Exception as e:

            print(
                "[SUBTITLE] MP3 download error:",
                repr(e),
                flush=True
            )

            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500

    # ======================================================
    # Route確認用
    #
    # GET /subtitle-create-srt
    #
    # 本来SRT作成はPOST。
    #
    # ただしブラウザ等からGETされた場合に
    # Flask標準404/HTMLを返さずJSONを返す。
    #
    # これによりフロント側のエラー確認が容易になる。
    # ======================================================

    @app.route(
        "/subtitle-create-srt",
        methods=["GET"]
    )
    def subtitle_create_srt_get():

        return jsonify({

            "success":
                False,

            "message":
                "このURLはPOSTで使用してください。",

            "endpoint":
                "/subtitle-create-srt",

            "method":
                "POST"

        }), 405

    # ======================================================
    # 登録完了
    # ======================================================

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE] subtitle routes registered",
        flush=True
    )

    print(
        "[SUBTITLE] POST /subtitle-upload-mp3",
        flush=True
    )

    print(
        "[SUBTITLE] POST /subtitle-upload-mp4",
        flush=True
    )

    print(
        "[SUBTITLE] POST /subtitle-upload-srt",
        flush=True
    )

    print(
        "[SUBTITLE] POST /subtitle-create-srt",
        flush=True
    )

    print(
        "[SUBTITLE] POST /subtitle-create-mp4",
        flush=True
    )

    print(
        "[SUBTITLE] GET  /subtitle-download-mp3",
        flush=True
    )

    print(
        "[SUBTITLE] converter.js /convert には干渉しません",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )
