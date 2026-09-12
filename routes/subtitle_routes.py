# ==========================================================
# routes/subtitle_routes.py
#
# 字幕関連Route
#
# ==========================================================

import os
import traceback

from flask import (
    Blueprint,
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

from subtitle_font import (
    select_subtitle_font,
    get_default_subtitle_font_settings
)


# ==========================================================
# Blueprint
# ==========================================================

subtitle_bp = Blueprint(
    "subtitle",
    __name__
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
# 字幕設定キー
# ==========================================================

SUBTITLE_SETTING_KEYS = (
    "preset_name",
    "font",
    "text_color",
    "text_color_hex",
    "outline_color",
    "outline_color_hex",
    "outline_width",
)


# ==========================================================
# DOWNLOAD_DIR確認
# ==========================================================

def ensure_download_dir():

    os.makedirs(
        DOWNLOAD_ROOT,
        exist_ok=True
    )


# ==========================================================
# 拡張子
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
# 安全なファイル名
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

    # パス部分を完全に除去
    filename = os.path.basename(
        filename
    )

    if not filename:

        raise ValueError(
            "ファイル名がありません"
        )

    # 元の拡張子
    original_extension = get_file_extension(
        filename
    )

    # 指定された拡張子を優先
    if extension:

        extension = str(
            extension
        ).strip().lower()

        if not extension.startswith("."):

            extension = "." + extension

    else:

        extension = original_extension

    if not extension:

        raise ValueError(
            "ファイル拡張子がありません"
        )

    # 元のファイル名
    original_stem = os.path.splitext(
        filename
    )[0]

    # Werkzeugで安全化
    safe_name = secure_filename(
        filename
    )

    # secure_filename()で空になる場合
    # 日本語ファイル名などが該当する
    if not safe_name:

        safe_stem = secure_filename(
            original_stem
        )

        if not safe_stem:

            # 日本語だけなど、secure_filename()で
            # 完全に空になる場合は固定名を使用
            safe_stem = "file"

        safe_name = (
            safe_stem
            +
            extension
        )

    # secure_filename()後の拡張子を確認
    safe_extension = get_file_extension(
        safe_name
    )

    # 拡張子を必ず指定値へ統一
    if safe_extension != extension:

        safe_stem = os.path.splitext(
            safe_name
        )[0]

        if not safe_stem:

            safe_stem = "file"

        safe_name = (
            safe_stem
            +
            extension
        )

    # 最終的にbasenameだけを許可
    safe_name = os.path.basename(
        safe_name
    )

    if not safe_name:

        raise ValueError(
            "安全なファイル名を作成できませんでした"
        )

    # 最終拡張子チェック
    if get_file_extension(
        safe_name
    ) != extension:

        safe_stem = os.path.splitext(
            safe_name
        )[0]

        if not safe_stem:

            safe_stem = "file"

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

    filename = str(
        filename or ""
    ).strip()

    if not filename:

        raise ValueError(
            "ファイル名がありません"
        )

    # パスを許可しない
    filename = os.path.basename(
        filename
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

    download_root = os.path.abspath(
        DOWNLOAD_ROOT
    )

    try:

        common_path = os.path.commonpath(
            [
                download_root,
                path
            ]
        )

    except ValueError:

        common_path = None

    if common_path != download_root:

        raise ValueError(
            "不正なファイルパスです"
        )

    return path


# ==========================================================
# アップロード保存
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

    # ------------------------------------------------------
    # 拡張子取得
    # ------------------------------------------------------

    extension = get_file_extension(
        original_filename
    )

    # ------------------------------------------------------
    # 許可拡張子チェック
    # ------------------------------------------------------

    if extension not in allowed_extensions:

        raise ValueError(
            "対応していないファイル形式です: "
            +
            extension
        )

    # ------------------------------------------------------
    # 安全なファイル名へ変換
    # ------------------------------------------------------

    safe_filename = make_safe_filename(
        original_filename,
        extension
    )

    if not safe_filename:

        raise ValueError(
            "安全なファイル名を作成できませんでした"
        )

    # ------------------------------------------------------
    # downloads配下の絶対パス
    # ------------------------------------------------------

    save_path = make_download_path(
        safe_filename
    )

    # ------------------------------------------------------
    # 既存ファイル確認
    # ------------------------------------------------------

    existed = os.path.exists(
        save_path
    )

    if existed:

        print(
            "[SUBTITLE] 同名ファイルを上書き:",
            save_path,
            flush=True
        )

    # ------------------------------------------------------
    # 保存
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # サイズ確認
    # ------------------------------------------------------

    file_size = os.path.getsize(
        save_path
    )

    if file_size <= 0:

        raise ValueError(
            "保存されたファイルが0 bytesです"
        )

    # ------------------------------------------------------
    # 最終ファイル名確認
    # ------------------------------------------------------

    actual_filename = os.path.basename(
        save_path
    )

    actual_extension = get_file_extension(
        actual_filename
    )

    if actual_extension not in allowed_extensions:

        raise ValueError(
            "保存されたファイルの拡張子が不正です: "
            +
            actual_extension
        )

    # ------------------------------------------------------
    # ログ
    # ------------------------------------------------------

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE] ファイル保存完了",
        flush=True
    )

    print(
        "[SUBTITLE] original filename:",
        original_filename,
        flush=True
    )

    print(
        "[SUBTITLE] safe filename:",
        actual_filename,
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
            actual_filename,

        "path":
            save_path,

        "size":
            file_size,

        "overwritten":
            existed

    }

# ==========================================================
# downloads内の保存先
# ==========================================================

def make_download_path(
    filename
):

    ensure_download_dir()

    filename = str(
        filename or ""
    ).strip()

    if not filename:

        raise ValueError(
            "ファイル名がありません"
        )

    # パスを許可しない
    filename = os.path.basename(
        filename
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

    download_root = os.path.abspath(
        DOWNLOAD_ROOT
    )

    try:

        common_path = os.path.commonpath(
            [
                download_root,
                path
            ]
        )

    except ValueError:

        common_path = None

    if common_path != download_root:

        raise ValueError(
            "不正なファイルパスです"
        )

    return path


# ==========================================================
# アップロード保存
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

    # 拡張子取得
    extension = get_file_extension(
        original_filename
    )

    # 許可拡張子チェック
    if extension not in allowed_extensions:

        raise ValueError(
            "対応していないファイル形式です: "
            +
            extension
        )

    # 安全なファイル名へ変換
    safe_filename = make_safe_filename(
        original_filename,
        extension
    )

    # downloads配下の絶対パス
    save_path = make_download_path(
        safe_filename
    )

    # 既存ファイル確認
    existed = os.path.exists(
        save_path
    )

    if existed:

        print(
            "[SUBTITLE] 同名ファイルを上書き:",
            save_path,
            flush=True
        )

    # 保存
    uploaded_file.save(
        save_path
    )

    # 保存確認
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

    # サイズ確認
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
        "[SUBTITLE] original filename:",
        original_filename,
        flush=True
    )

    print(
        "[SUBTITLE] safe filename:",
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
# downloadsから取得
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

    # パス指定を禁止
    filename = os.path.basename(
        filename
    )

    if not filename:

        raise ValueError(
            "ファイル名がありません"
        )

    # 拡張子確認
    extension = get_file_extension(
        filename
    )

    if extension not in allowed_extensions:

        raise ValueError(
            "対応していないファイル形式です: "
            +
            extension
        )

    # downloads配下
    file_path = make_download_path(
        filename
    )

    # 存在確認
    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            "ファイルがありません: "
            +
            filename
        )

    # ファイル確認
    if not os.path.isfile(
        file_path
    ):

        raise ValueError(
            "指定されたパスはファイルではありません"
        )

    # サイズ確認
    file_size = os.path.getsize(
        file_path
    )

    if file_size <= 0:

        raise ValueError(
            "ファイルが0 bytesです"
        )

    return file_path

# ==========================================================
# 字幕設定正規化
# ==========================================================

def normalize_subtitle_settings(
    subtitle_settings=None
):

    if subtitle_settings is None:

        return (
            get_default_subtitle_font_settings()
        )

    if not isinstance(
        subtitle_settings,
        dict
    ):

        raise TypeError(
            "subtitle_settingsはdictで指定してください。"
        )

    normalized = {}

    for key in SUBTITLE_SETTING_KEYS:

        if key in subtitle_settings:

            normalized[key] = (
                subtitle_settings.get(
                    key
                )
            )

    try:

        result = select_subtitle_font(
            settings=normalized
        )

    except TypeError as error:

        raise TypeError(
            "subtitle_font.pyの"
            "select_subtitle_font()は"
            "settings=形式に対応してください。"
        ) from error

    if not isinstance(
        result,
        dict
    ):

        raise TypeError(
            "select_subtitle_font()から"
            "dictが返されませんでした。"
        )

    return {

        "preset_name":
            result.get(
                "preset_name"
            ),

        "font":
            result.get(
                "font"
            ),

        "text_color":
            result.get(
                "text_color"
            ),

        "text_color_hex":
            result.get(
                "text_color_hex"
            ),

        "outline_color":
            result.get(
                "outline_color"
            ),

        "outline_color_hex":
            result.get(
                "outline_color_hex"
            ),

        "outline_width":
            result.get(
                "outline_width"
            )

    }


# ==========================================================
# MP3 → SRT
# ==========================================================

def create_srt_from_mp3(
    mp3_path
):

    mp3_path = os.path.abspath(
        str(
            mp3_path
        )
    )

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
        "==========================================",
        flush=True
    )

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
    srt_path,
    subtitle_settings=None
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

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
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
        "[SUBTITLE] SRT:",
        srt_path,
        flush=True
    )

    print(
        "[SUBTITLE] 字幕設定:",
        subtitle_settings,
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    import subtitle

    subtitle_function = getattr(
        subtitle,
        "create_subtitle_mp4",
        None
    )

    if subtitle_function is None:

        subtitle_function = getattr(
            subtitle,
            "create_burned_subtitle",
            None
        )

    if subtitle_function is None:

        subtitle_function = getattr(
            subtitle,
            "burn_subtitles",
            None
        )

    if subtitle_function is None:

        raise AttributeError(
            "subtitle.pyに字幕MP4作成関数がありません。"
        )

    print(
        "[SUBTITLE] subtitle.py function:",
        getattr(
            subtitle_function,
            "__name__",
            str(
                subtitle_function
            )
        ),
        flush=True
    )

    print(
        "[SUBTITLE] subtitle.py START",
        flush=True
    )

    result = subtitle_function(

        mp4_path,

        srt_path,

        subtitle_settings=subtitle_settings

    )

    print(
        "[SUBTITLE] subtitle.py COMPLETE",
        flush=True
    )

    if not result:

        raise ValueError(
            "字幕MP4作成処理から結果が返されませんでした"
        )

    if isinstance(
        result,
        dict
    ):

        result_path = (

            result.get(
                "subtitle_mp4_path"
            )

            or

            result.get(
                "path"
            )

            or

            result.get(
                "output"
            )

            or

            result.get(
                "output_path"
            )

        )

    else:

        result_path = result

    if not result_path:

        raise ValueError(
            "subtitle.pyから字幕MP4のパスを取得できませんでした"
        )

    result_path = os.path.abspath(
        str(
            result_path
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

    if not result_path.lower().endswith(
        ".mp4"
    ):

        raise ValueError(
            "字幕MP4の出力拡張子が.mp4ではありません"
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
            result_path,

        "path":
            result_path,

        "subtitle_settings":
            subtitle_settings

    }


# ==========================================================
# MP3アップロード
# ==========================================================

@subtitle_bp.route(
    "/subtitle-upload-mp3",
    methods=["POST"]
)
def subtitle_upload_mp3():

    try:

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
                "MP3を保存し、GeminiからSRTを作成しました。",

            "mp3_file":
                saved["filename"],

            "srt_file":
                result["srt_file"],

            "srt_path":
                result["srt_path"],

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
            "[SUBTITLE] MP3処理エラー:",
            traceback.format_exc(),
            flush=True
        )

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==========================================================
# MP4アップロード
# ==========================================================

@subtitle_bp.route(
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
            traceback.format_exc(),
            flush=True
        )

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==========================================================
# SRTアップロード
# ==========================================================

@subtitle_bp.route(
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
            traceback.format_exc(),
            flush=True
        )

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==========================================================
# MP3 → SRT
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-srt",
    methods=["POST"]
)
def subtitle_create_srt():

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

        mp3_path = get_download_file(

            mp3_filename,

            ALLOWED_MP3_EXTENSIONS

        )

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

            "srt_path":
                result["srt_path"],

            "files": {

                "mp3":
                    result["mp3_file"],

                "srt":
                    result["srt_file"]

            }

        })

    except FileNotFoundError as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 404

    except Exception as e:

        print(
            "[SUBTITLE] create-srt error:",
            traceback.format_exc(),
            flush=True
        )

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==========================================================
# MP4 + SRT → 字幕MP4
#
# POST /subtitle-create-mp4
#
# 1. 既にdownloadsへ保存されたMP4を取得
# 2. 既にdownloadsへ保存されたSRTを取得
# 3. subtitle.pyへ渡す
# 4. FFmpegで字幕MP4作成
# 5. 作成されたファイル名をJSONで返す
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-mp4",
    methods=["POST"]
)
def subtitle_create_mp4_route():

    print(
        "==========================================",
        flush=True
    )

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


        # ==================================================
        # ファイル名
        # ==================================================

        mp4_filename = str(
            data.get(
                "mp4_file",
                ""
            )
        ).strip()

        srt_filename = str(
            data.get(
                "srt_file",
                ""
            )
        ).strip()


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


        print(
            "[SUBTITLE] requested MP4:",
            mp4_filename,
            flush=True
        )

        print(
            "[SUBTITLE] requested SRT:",
            srt_filename,
            flush=True
        )


        # ==================================================
        # 字幕設定
        # ==================================================

        requested_settings = {}

        for key in SUBTITLE_SETTING_KEYS:

            if key in data:

                requested_settings[key] = (
                    data.get(
                        key
                    )
                )


        print(
            "[SUBTITLE] requested settings:",
            requested_settings,
            flush=True
        )


        # ==================================================
        # downloadsからMP4取得
        # ==================================================

        mp4_path = get_download_file(

            mp4_filename,

            ALLOWED_MP4_EXTENSIONS

        )


        print(
            "[SUBTITLE] MP4 found:",
            mp4_path,
            flush=True
        )


        # ==================================================
        # downloadsからSRT取得
        # ==================================================

        srt_path = get_download_file(

            srt_filename,

            ALLOWED_SRT_EXTENSIONS

        )


        print(
            "[SUBTITLE] SRT found:",
            srt_path,
            flush=True
        )


        # ==================================================
        # 字幕MP4作成
        # ==================================================

        result = create_subtitle_mp4(

            mp4_path,

            srt_path,

            subtitle_settings=requested_settings

        )


        output_filename = (
            result[
                "subtitle_mp4_file"
            ]
        )


        output_path = (
            result[
                "subtitle_mp4_path"
            ]
        )


        print(
            "[SUBTITLE] subtitle MP4 created:",
            output_path,
            flush=True
        )


        # ==================================================
        # JSON
        # ==================================================

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
                output_filename,

            "subtitle_mp4_path":
                output_path,

            "filename":
                output_filename,

            "download_url":
                "/downloads/" +
                output_filename,

            "subtitle_settings":
                result["subtitle_settings"],

            "files": {

                "mp4":
                    result["mp4_file"],

                "srt":
                    result["srt_file"],

                "subtitle_mp4":
                    output_filename

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
            "[SUBTITLE] TYPE:",
            type(e).__name__,
            flush=True
        )

        print(
            "[SUBTITLE] ERROR:",
            str(e),
            flush=True
        )

        print(
            traceback.format_exc(),
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


# ==========================================================
# MP4 / SRT / 字幕MP4 ダウンロード
# ==========================================================

@subtitle_bp.route(
    "/downloads/<path:filename>",
    methods=["GET"]
)
def subtitle_download_file(
    filename
):

    try:

        filename = os.path.basename(
            str(
                filename
            )
        )

        extension = get_file_extension(
            filename
        )

        allowed_extensions = (
            ALLOWED_MP3_EXTENSIONS
            |
            ALLOWED_MP4_EXTENSIONS
            |
            ALLOWED_SRT_EXTENSIONS
        )

        if extension not in allowed_extensions:

            return jsonify({

                "success":
                    False,

                "message":
                    "対応していないファイル形式です"

            }), 400


        file_path = get_download_file(

            filename,

            allowed_extensions

        )


        safe_filename = os.path.basename(
            file_path
        )


        return send_from_directory(

            DOWNLOAD_ROOT,

            safe_filename,

            as_attachment=True,

            download_name=safe_filename

        )


    except FileNotFoundError as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 404


    except Exception as e:

        print(
            "[SUBTITLE] ダウンロードエラー:",
            traceback.format_exc(),
            flush=True
        )

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==========================================================
# MP3ダウンロード
# ==========================================================

@subtitle_bp.route(
    "/subtitle-download-mp3",
    methods=["GET"]
)
def subtitle_download_mp3():

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

        mp3_path = get_download_file(

            filename,

            ALLOWED_MP3_EXTENSIONS

        )

        safe_filename = os.path.basename(
            mp3_path
        )

        return send_from_directory(

            DOWNLOAD_ROOT,

            safe_filename,

            as_attachment=True,

            download_name=safe_filename

        )

    except FileNotFoundError as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 404

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 500


# ==========================================================
# GET /subtitle-create-srt
# ==========================================================

@subtitle_bp.route(
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


# ==========================================================
# GET /subtitle-create-mp4
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-mp4",
    methods=["GET"]
)
def subtitle_create_mp4_get():

    return jsonify({

        "success":
            False,

        "message":
            "このURLはPOSTで使用してください。",

        "endpoint":
            "/subtitle-create-mp4",

        "method":
            "POST"

    }), 405


# ==========================================================
# 互換用Route登録関数
# ==========================================================

def register_subtitle_routes(
    app
):

    ensure_download_dir()

    blueprint_registered = False

    for registered_blueprint in (
        app.blueprints.values()
    ):

        if registered_blueprint is subtitle_bp:

            blueprint_registered = True

            break


    if not blueprint_registered:

        app.register_blueprint(
            subtitle_bp
        )


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
        "[SUBTITLE] GET  /downloads/<filename>",
        flush=True
    )

    print(
        "[SUBTITLE] subtitle settings enabled",
        flush=True
    )

    print(
        "[SUBTITLE] preset_name is supported",
        flush=True
    )

    print(
        "[SUBTITLE] /subtitle-test/create-subtitle-mp4 は使用しません",
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


# ==========================================================
# モジュール読み込み時
# ==========================================================

ensure_download_dir()


print(
    "[SUBTITLE] routes/subtitle_routes.py loaded",
    flush=True
)


print(
    "[SUBTITLE] Blueprint: subtitle_bp",
    flush=True
)


print(
    "[SUBTITLE] endpoint: /subtitle-create-mp4",
    flush=True
)
