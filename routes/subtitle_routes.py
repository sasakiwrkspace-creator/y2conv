# ==========================================================
# Subtitle Routes
# routes/subtitle_routes.py
#
# 字幕関連HTTP API
#
# ==========================================================
#
# エンドポイント
#
# POST /subtitle-upload-mp3
#   MP3をDOWNLOAD_DIRへ保存
#   保存直後にcreate_srt_from_mp3()を実行
#
# POST /subtitle-upload-mp4
#   MP4アップロード専用
#
# POST /subtitle-upload-srt
#   SRTアップロード専用
#
# POST /subtitle-create-srt
#   DOWNLOAD_DIRに保存済みMP3からSRTを作成
#
# GET /subtitle-create-srt
#   POST専用であることを返す
#
# POST /subtitle-create-mp4
#   MP4 + SRT + 字幕設定から字幕MP4を作成
#
# GET /subtitle-download-mp3
#   MP3ダウンロード
#
# ==========================================================
#
# 字幕設定の正式名称
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# 別名はHTTP入力受付時だけ吸収する。
#
# subtitle.pyへ渡す段階では必ず正式名称へ統一する。
#
# ==========================================================

import os
import importlib
from pathlib import Path

from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
)

from werkzeug.utils import secure_filename

from config import DOWNLOAD_DIR

from subtitle_font import (
    get_default_subtitle_font_settings,
    select_subtitle_font,
)

from subtitle import (
    create_subtitle_mp4,
)


# ==========================================================
# Blueprint
#
# app.py:
#
#   from routes.subtitle_routes import subtitle_bp
#
# が成立するため、必ずsubtitle_bpを公開する。
# ==========================================================

subtitle_bp = Blueprint(
    "subtitle",
    __name__
)


# ==========================================================
# DOWNLOAD_DIR
# ==========================================================

DOWNLOADS_DIR = Path(
    DOWNLOAD_DIR
).resolve()


# ==========================================================
# 正式な字幕設定キー
# ==========================================================

SUBTITLE_SETTING_KEYS = (
    "preset_name",
    "font",
    "text_color",
    "outline_color",
    "outline_width",
)


# ==========================================================
# ログ
# ==========================================================

def log(message):

    print(
        "[SUBTITLE_ROUTE]",
        message,
        flush=True
    )


# ==========================================================
# DOWNLOAD_DIR作成
# ==========================================================

def ensure_download_dir():

    DOWNLOADS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return DOWNLOADS_DIR


# ==========================================================
# ファイル名安全化
# ==========================================================

def safe_filename(
    filename
):

    filename = (
        secure_filename(
            str(filename or "")
        )
    )

    if not filename:

        raise ValueError(
            "ファイル名が指定されていません。"
        )

    return filename


# ==========================================================
# DOWNLOAD_DIR内のパス
#
# パス traversal 防止
# ==========================================================

def get_download_path(
    filename
):

    filename = safe_filename(
        filename
    )

    path = (
        DOWNLOADS_DIR
        /
        filename
    ).resolve()

    try:

        path.relative_to(
            DOWNLOADS_DIR
        )

    except ValueError:

        raise ValueError(
            "不正なファイルパスです。"
        )

    return path


# ==========================================================
# 拡張子確認
# ==========================================================

def validate_extension(
    filename,
    extension
):

    filename = str(
        filename or ""
    )

    if not filename.lower().endswith(
        extension.lower()
    ):

        raise ValueError(
            f"{extension}ファイルを指定してください。"
        )


# ==========================================================
# アップロード保存
# ==========================================================

def save_uploaded_file(
    uploaded_file,
    extension
):

    if uploaded_file is None:

        raise ValueError(
            "ファイルがアップロードされていません。"
        )

    original_filename = (
        uploaded_file.filename
    )

    if not original_filename:

        raise ValueError(
            "ファイル名がありません。"
        )

    validate_extension(
        original_filename,
        extension
    )

    filename = safe_filename(
        original_filename
    )

    path = get_download_path(
        filename
    )

    ensure_download_dir()

    uploaded_file.save(
        str(path)
    )

    if not path.exists():

        raise RuntimeError(
            "アップロードファイルを保存できませんでした。"
        )

    if not path.is_file():

        raise RuntimeError(
            "保存されたファイルが通常のファイルではありません。"
        )

    try:

        size = path.stat().st_size

    except OSError as error:

        raise RuntimeError(
            f"保存ファイルのサイズを確認できません: {error}"
        ) from error

    if size <= 0:

        try:
            path.unlink()
        except Exception:
            pass

        raise RuntimeError(
            "アップロードされたファイルが0 bytesです。"
        )

    log(
        f"保存完了: {path}"
    )

    log(
        f"サイズ: {size} bytes"
    )

    return path


# ==========================================================
# JSON / formから値取得
# ==========================================================

def get_request_value(
    name,
    default=None
):

    # ------------------------------------------------------
    # JSON
    # ------------------------------------------------------

    if request.is_json:

        data = request.get_json(
            silent=True
        )

        if isinstance(data, dict):

            value = data.get(
                name
            )

            if value is not None:

                return value

    # ------------------------------------------------------
    # form
    # ------------------------------------------------------

    value = request.form.get(
        name
    )

    if value is not None:

        return value

    # ------------------------------------------------------
    # args
    # ------------------------------------------------------

    value = request.args.get(
        name
    )

    if value is not None:

        return value

    return default


# ==========================================================
# 字幕設定取得
#
# ここだけでHTTP入力の表記ゆれを吸収する。
#
# subtitle.pyへ渡す際には正式名称だけにする。
# ==========================================================

def get_subtitle_settings_from_request():

    settings = {}

    # ======================================================
    # preset_name
    #
    # 正式名称:
    #   preset_name
    #
    # 旧名が存在する場合だけここで吸収。
    # ======================================================

    preset_name = get_request_value(
        "preset_name"
    )

    if preset_name is None:

        preset_name = get_request_value(
            "preset"
        )

    if preset_name is not None:

        settings[
            "preset_name"
        ] = preset_name

    # ======================================================
    # font
    # ======================================================

    font = get_request_value(
        "font"
    )

    if font is not None:

        settings[
            "font"
        ] = font

    # ======================================================
    # text_color
    #
    # HTTP側の旧表記だけ吸収。
    # ======================================================

    text_color = get_request_value(
        "text_color"
    )

    if text_color is None:

        text_color = get_request_value(
            "textColor"
        )

    if text_color is None:

        text_color = get_request_value(
            "color"
        )

    if text_color is not None:

        settings[
            "text_color"
        ] = text_color

    # ======================================================
    # outline_color
    # ======================================================

    outline_color = get_request_value(
        "outline_color"
    )

    if outline_color is None:

        outline_color = get_request_value(
            "outlineColor"
        )

    if outline_color is None:

        outline_color = get_request_value(
            "stroke_color"
        )

    if outline_color is None:

        outline_color = get_request_value(
            "strokeColor"
        )

    if outline_color is not None:

        settings[
            "outline_color"
        ] = outline_color

    # ======================================================
    # outline_width
    # ======================================================

    outline_width = get_request_value(
        "outline_width"
    )

    if outline_width is None:

        outline_width = get_request_value(
            "outlineWidth"
        )

    if outline_width is None:

        outline_width = get_request_value(
            "stroke_width"
        )

    if outline_width is None:

        outline_width = get_request_value(
            "strokeWidth"
        )

    if outline_width is not None:

        settings[
            "outline_width"
        ] = outline_width

    # ======================================================
    # subtitle_font.pyで正規化
    # ======================================================

    try:

        normalized = select_subtitle_font(
            settings=settings
        )

    except Exception as error:

        raise RuntimeError(
            f"字幕設定の正規化に失敗しました: {error}"
        ) from error

    # ======================================================
    # 正式名称5つだけを返す
    # ======================================================

    result = {

        "preset_name":
            normalized.get(
                "preset_name"
            ),

        "font":
            normalized.get(
                "font"
            ),

        "text_color":
            normalized.get(
                "text_color"
            ),

        "outline_color":
            normalized.get(
                "outline_color"
            ),

        "outline_width":
            normalized.get(
                "outline_width"
            ),

    }

    log(
        "字幕設定:"
    )

    log(
        str(result)
    )

    return result


# ==========================================================
# 標準字幕設定
# ==========================================================

def get_default_settings():

    try:

        settings = (
            get_default_subtitle_font_settings()
        )

    except Exception as error:

        raise RuntimeError(
            f"字幕標準設定を取得できません: {error}"
        ) from error

    result = {

        "preset_name":
            settings.get(
                "preset_name"
            ),

        "font":
            settings.get(
                "font"
            ),

        "text_color":
            settings.get(
                "text_color"
            ),

        "outline_color":
            settings.get(
                "outline_color"
            ),

        "outline_width":
            settings.get(
                "outline_width"
            ),

    }

    return result


# ==========================================================
# create_srt_from_mp3() 検出
#
# プロジェクトによってGemini処理モジュール名が
# 異なる可能性があるため、候補を順番に探す。
#
# 環境変数:
#
#   SUBTITLE_SRT_MODULE
#
# を設定すれば、そのモジュールを最優先する。
# ==========================================================

def get_create_srt_from_mp3():

    module_candidates = []

    environment_module = os.environ.get(
        "SUBTITLE_SRT_MODULE"
    )

    if environment_module:

        module_candidates.append(
            environment_module.strip()
        )

    module_candidates.extend([

        "subtitle_srt",

        "subtitle_gemini",

        "gemini_srt",

        "gemini",

        "srt",

        "transcribe",

        "transcription",

        "subtitle",

    ])

    checked = set()

    for module_name in module_candidates:

        if not module_name:

            continue

        if module_name in checked:

            continue

        checked.add(
            module_name
        )

        try:

            module = importlib.import_module(
                module_name
            )

        except ImportError:

            continue

        function = getattr(
            module,
            "create_srt_from_mp3",
            None
        )

        if callable(function):

            log(
                "create_srt_from_mp3検出:"
            )

            log(
                f"module: {module_name}"
            )

            return function

    raise RuntimeError(

        "create_srt_from_mp3() が見つかりません。"
        "GeminiによるSRT作成関数を定義したモジュールを"
        "確認してください。"
        "必要であればSUBTITLE_SRT_MODULE環境変数に"
        "モジュール名を指定してください。"

    )


# ==========================================================
# create_srt_from_mp3() 実行
#
# プロジェクト側の関数シグネチャ差をある程度吸収する。
# ==========================================================

def run_create_srt_from_mp3(
    mp3_path
):

    function = (
        get_create_srt_from_mp3()
    )

    log(
        "create_srt_from_mp3() 開始"
    )

    log(
        f"MP3: {mp3_path}"
    )

    # ------------------------------------------------------
    # まずPathを渡す
    # ------------------------------------------------------

    try:

        result = function(
            mp3_path
        )

    except TypeError as first_error:

        log(
            "Path引数での実行に失敗。"
        )

        log(
            f"原因: {first_error}"
        )

        # --------------------------------------------------
        # 文字列パスで再試行
        # --------------------------------------------------

        try:

            result = function(
                str(mp3_path)
            )

        except TypeError as second_error:

            raise RuntimeError(

                "create_srt_from_mp3() の"
                "引数形式が一致しません。"
                f" Path形式: {first_error}"
                f" / str形式: {second_error}"

            ) from second_error

        except Exception as error:

            raise RuntimeError(
                f"SRT作成に失敗しました: {error}"
            ) from error

    except Exception as error:

        raise RuntimeError(
            f"SRT作成に失敗しました: {error}"
        ) from error

    # ------------------------------------------------------
    # 戻り値がPath / strの場合
    # ------------------------------------------------------

    if result is None:

        # 関数がDOWNLOAD_DIRへ出力するタイプを想定。
        #
        # 同名MP3の.srtを第一候補として確認。
        candidate = (
            mp3_path.with_suffix(".srt")
        )

        if candidate.exists():

            result = candidate

        else:

            # 最新SRTを探す
            srt_files = sorted(

                DOWNLOADS_DIR.glob(
                    "*.srt"
                ),

                key=lambda p: p.stat().st_mtime,

                reverse=True

            )

            if srt_files:

                result = srt_files[0]

    if result is None:

        raise RuntimeError(

            "create_srt_from_mp3() は終了しましたが、"
            "SRTファイルが確認できませんでした。"

        )

    result_path = Path(
        str(result)
    ).resolve()

    # ------------------------------------------------------
    # 相対パスの場合
    # ------------------------------------------------------

    if not result_path.exists():

        relative_candidate = (
            DOWNLOADS_DIR
            /
            str(result)
        ).resolve()

        if relative_candidate.exists():

            result_path = (
                relative_candidate
            )

    if not result_path.exists():

        raise RuntimeError(

            "SRT作成処理は終了しましたが、"
            f"出力ファイルが見つかりません: {result}"

        )

    if not result_path.is_file():

        raise RuntimeError(
            f"SRT出力先がファイルではありません: {result_path}"
        )

    if result_path.suffix.lower() != ".srt":

        raise RuntimeError(
            f"SRTではないファイルが返されました: {result_path}"
        )

    log(
        "create_srt_from_mp3() 完了"
    )

    log(
        f"SRT: {result_path}"
    )

    return result_path


# ==========================================================
# JSON成功レスポンス
# ==========================================================

def success_response(
    message,
    **kwargs
):

    data = {

        "success":
            True,

        "message":
            message,

    }

    data.update(
        kwargs
    )

    return jsonify(
        data
    ), 200


# ==========================================================
# JSONエラーレスポンス
# ==========================================================

def error_response(
    message,
    status=400
):

    return jsonify({

        "success":
            False,

        "error":
            str(message),

    }), status


# ==========================================================
# POST /subtitle-upload-mp3
#
# MP3アップロード
# ↓
# DOWNLOAD_DIR保存
# ↓
# Gemini
# ↓
# SRT作成
#
# 一括処理
# ==========================================================

@subtitle_bp.route(
    "/subtitle-upload-mp3",
    methods=["POST"]
)
def subtitle_upload_mp3():

    try:

        uploaded_file = (
            request.files.get(
                "file"
            )
        )

        if uploaded_file is None:

            uploaded_file = (
                request.files.get(
                    "mp3"
                )
            )

        mp3_path = save_uploaded_file(
            uploaded_file,
            ".mp3"
        )

        # --------------------------------------------------
        # 保存直後にSRT作成
        # --------------------------------------------------

        srt_path = (
            run_create_srt_from_mp3(
                mp3_path
            )
        )

        return success_response(

            "MP3アップロードとSRT作成が完了しました。",

            mp3_filename=
                mp3_path.name,

            mp3_path=
                str(mp3_path),

            srt_filename=
                srt_path.name,

            srt_path=
                str(srt_path),

        )

    except Exception as error:

        log(
            f"subtitle-upload-mp3 エラー: {error}"
        )

        return error_response(
            error,
            500
        )


# ==========================================================
# POST /subtitle-upload-mp4
#
# MP4アップロード専用
#
# SRT作成や字幕焼き込みは行わない。
# ==========================================================

@subtitle_bp.route(
    "/subtitle-upload-mp4",
    methods=["POST"]
)
def subtitle_upload_mp4():

    try:

        uploaded_file = (
            request.files.get(
                "file"
            )
        )

        if uploaded_file is None:

            uploaded_file = (
                request.files.get(
                    "mp4"
                )
            )

        mp4_path = save_uploaded_file(
            uploaded_file,
            ".mp4"
        )

        return success_response(

            "MP4アップロードが完了しました。",

            mp4_filename=
                mp4_path.name,

            mp4_path=
                str(mp4_path),

        )

    except Exception as error:

        log(
            f"subtitle-upload-mp4 エラー: {error}"
        )

        return error_response(
            error,
            500
        )


# ==========================================================
# POST /subtitle-upload-srt
#
# SRTアップロード専用
# ==========================================================

@subtitle_bp.route(
    "/subtitle-upload-srt",
    methods=["POST"]
)
def subtitle_upload_srt():

    try:

        uploaded_file = (
            request.files.get(
                "file"
            )
        )

        if uploaded_file is None:

            uploaded_file = (
                request.files.get(
                    "srt"
                )
            )

        srt_path = save_uploaded_file(
            uploaded_file,
            ".srt"
        )

        return success_response(

            "SRTアップロードが完了しました。",

            srt_filename=
                srt_path.name,

            srt_path=
                str(srt_path),

        )

    except Exception as error:

        log(
            f"subtitle-upload-srt エラー: {error}"
        )

        return error_response(
            error,
            500
        )


# ==========================================================
# POST /subtitle-create-srt
#
# 保存済みMP3からSRTを作成
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-srt",
    methods=["POST"]
)
def subtitle_create_srt():

    try:

        mp3_filename = get_request_value(
            "mp3_filename"
        )

        if mp3_filename is None:

            mp3_filename = get_request_value(
                "filename"
            )

        if mp3_filename is None:

            mp3_filename = get_request_value(
                "mp3"
            )

        if not mp3_filename:

            raise ValueError(
                "mp3_filenameを指定してください。"
            )

        validate_extension(
            mp3_filename,
            ".mp3"
        )

        mp3_path = get_download_path(
            mp3_filename
        )

        if not mp3_path.exists():

            raise FileNotFoundError(
                f"MP3がありません: {mp3_path}"
            )

        if not mp3_path.is_file():

            raise ValueError(
                f"MP3ではありません: {mp3_path}"
            )

        srt_path = (
            run_create_srt_from_mp3(
                mp3_path
            )
        )

        return success_response(

            "SRT作成が完了しました。",

            mp3_filename=
                mp3_path.name,

            srt_filename=
                srt_path.name,

            srt_path=
                str(srt_path),

        )

    except Exception as error:

        log(
            f"subtitle-create-srt エラー: {error}"
        )

        return error_response(
            error,
            500
        )


# ==========================================================
# GET /subtitle-create-srt
#
# POST専用であることを明示
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-srt",
    methods=["GET"]
)
def subtitle_create_srt_get():

    return jsonify({

        "success":
            False,

        "error":
            "Method Not Allowed",

        "message":
            "このエンドポイントはPOST専用です。",

        "allowed_methods":
            ["POST"],

    }), 405


# ==========================================================
# POST /subtitle-create-mp4
#
# MP4 + SRT + 字幕設定
# ↓
# 字幕MP4作成
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-mp4",
    methods=["POST"]
)
def subtitle_create_mp4():

    try:

        # ==================================================
        # MP4
        # ==================================================

        mp4_filename = get_request_value(
            "mp4_filename"
        )

        if mp4_filename is None:

            mp4_filename = get_request_value(
                "mp4"
            )

        if not mp4_filename:

            raise ValueError(
                "mp4_filenameを指定してください。"
            )

        validate_extension(
            mp4_filename,
            ".mp4"
        )

        mp4_path = get_download_path(
            mp4_filename
        )

        if not mp4_path.exists():

            raise FileNotFoundError(
                f"MP4がありません: {mp4_path}"
            )

        # ==================================================
        # SRT
        # ==================================================

        srt_filename = get_request_value(
            "srt_filename"
        )

        if srt_filename is None:

            srt_filename = get_request_value(
                "srt"
            )

        if not srt_filename:

            raise ValueError(
                "srt_filenameを指定してください。"
            )

        validate_extension(
            srt_filename,
            ".srt"
        )

        srt_path = get_download_path(
            srt_filename
        )

        if not srt_path.exists():

            raise FileNotFoundError(
                f"SRTがありません: {srt_path}"
            )

        # ==================================================
        # 字幕設定
        #
        # preset_nameを含む正式5項目へ統一。
        # ==================================================

        subtitle_settings = (
            get_subtitle_settings_from_request()
        )

        # ==================================================
        # 字幕MP4作成
        # ==================================================

        output_path = (
            create_subtitle_mp4(

                mp4_path,

                srt_path,

                subtitle_settings=
                    subtitle_settings

            )
        )

        output_path = Path(
            output_path
        ).resolve()

        return success_response(

            "字幕MP4の作成が完了しました。",

            mp4_filename=
                mp4_path.name,

            srt_filename=
                srt_path.name,

            output_filename=
                output_path.name,

            output_path=
                str(output_path),

            subtitle_settings=
                subtitle_settings,

        )

    except Exception as error:

        log(
            f"subtitle-create-mp4 エラー: {error}"
        )

        return error_response(
            error,
            500
        )


# ==========================================================
# POST /subtitle-download-mp3
#
# 仕様上の名前はsubtitle-download-mp3。
#
# ダウンロードはGETの方が自然だが、
# 既存フロントとの互換性を考慮してPOSTも許可する。
# ==========================================================

@subtitle_bp.route(
    "/subtitle-download-mp3",
    methods=["GET", "POST"]
)
def subtitle_download_mp3():

    try:

        filename = get_request_value(
            "filename"
        )

        if filename is None:

            filename = get_request_value(
                "mp3_filename"
            )

        if filename is None:

            filename = get_request_value(
                "mp3"
            )

        if not filename:

            raise ValueError(
                "MP3ファイル名を指定してください。"
            )

        validate_extension(
            filename,
            ".mp3"
        )

        mp3_path = get_download_path(
            filename
        )

        if not mp3_path.exists():

            raise FileNotFoundError(
                f"MP3がありません: {mp3_path}"
            )

        if not mp3_path.is_file():

            raise ValueError(
                f"MP3ではありません: {mp3_path}"
            )

        return send_file(

            str(mp3_path),

            as_attachment=True,

            download_name=
                mp3_path.name,

            mimetype=
                "audio/mpeg"

        )

    except Exception as error:

        log(
            f"subtitle-download-mp3 エラー: {error}"
        )

        return error_response(
            error,
            404
        )


# ==========================================================
# OPTIONS / 簡易確認
# ==========================================================

@subtitle_bp.route(
    "/subtitle-routes",
    methods=["GET"]
)
def subtitle_routes_info():

    return jsonify({

        "success":
            True,

        "service":
            "subtitle",

        "routes": [

            {
                "path":
                    "/subtitle-upload-mp3",

                "method":
                    "POST",

                "description":
                    "MP3保存後、SRTを自動作成"

            },

            {
                "path":
                    "/subtitle-upload-mp4",

                "method":
                    "POST",

                "description":
                    "MP4アップロード"

            },

            {
                "path":
                    "/subtitle-upload-srt",

                "method":
                    "POST",

                "description":
                    "SRTアップロード"

            },

            {
                "path":
                    "/subtitle-create-srt",

                "method":
                    "POST",

                "description":
                    "保存済みMP3からSRTを作成"

            },

            {
                "path":
                    "/subtitle-create-mp4",

                "method":
                    "POST",

                "description":
                    "MP4 + SRTから字幕MP4を作成"

            },

            {
                "path":
                    "/subtitle-download-mp3",

                "method":
                    "GET/POST",

                "description":
                    "MP3ダウンロード"

            },

        ],

        "subtitle_setting_keys": [

            "preset_name",

            "font",

            "text_color",

            "outline_color",

            "outline_width",

        ],

    })
