# ==========================================================
# routes/subtitle_routes.py
#
# 字幕関連 API Route
#
# 役割:
#   - HTTPリクエストを受け取る
#   - 字幕設定を subtitle_font.py で正規化
#   - subtitle.py に処理を渡す
#
# ==========================================================
#
# 【字幕設定の正式な内部キー】
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# この5つを
#
#   subtitle_font.py
#   subtitle_routes.py
#   subtitle.py
#
# の3ファイルで共通語彙として使用する。
#
# ==========================================================
#
# 【重要】
#
# 字幕の標準値は subtitle_font.py のみを正とする。
#
# subtitle_routes.py では
#
#   白
#   青
#   5
#
# などの標準値を定義しない。
#
# 指定されていない値は None のまま
# subtitle_font.py に渡す。
#
# ==========================================================
#
# 【外部入力の旧キー】
#
# HTTP APIの互換性維持のため、入口では以下を受け付ける。
#
#   preset
#   font_name
#   textColor
#   color
#   outlineColor
#   stroke_color
#   strokeColor
#   outlineWidth
#   stroke_width
#   strokeWidth
#
# ただし、これらはRoute内部では正式キーへ変換する。
#
# ==========================================================


import traceback

from pathlib import Path

from flask import (
    Blueprint,
    request,
    jsonify,
)

from subtitle_font import (
    select_subtitle_font,
    get_default_subtitle_font_settings,
)

from subtitle import (
    create_subtitle_mp4,
)


# ==========================================================
# Blueprint
# ==========================================================

subtitle_bp = Blueprint(
    "subtitle",
    __name__
)


# ==========================================================
# ログ
# ==========================================================

def log(message):

    print(
        "[SUBTITLE]",
        message,
        flush=True
    )


# ==========================================================
# JSON取得
# ==========================================================

def get_request_json():

    try:

        data = request.get_json(
            silent=True
        )

    except Exception as error:

        log(
            f"JSON取得エラー: {error}"
        )

        return {}

    if not isinstance(
        data,
        dict
    ):

        return {}

    return data


# ==========================================================
# 値取得
#
# 注意:
#
# この関数はHTTP入口での旧キー互換処理にのみ使用する。
#
# Route内部で使用する正式キーは必ず
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# とする。
# ==========================================================

def get_value(
    data,
    *keys
):

    for key in keys:

        if key not in data:

            continue

        value = data.get(
            key
        )

        if value is not None:

            return value

    return None


# ==========================================================
# 字幕設定正規化
# ==========================================================
#
# 【正式内部キー】
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# Routeでは標準値を決めない。
#
# 指定されていない値は None のまま
# subtitle_font.py に渡す。
#
# 標準値の決定は subtitle_font.py の責任。
#
# ==========================================================

def normalize_subtitle_settings(
    data
):

    if not isinstance(
        data,
        dict
    ):

        data = {}

    # ======================================================
    # preset_name
    #
    # 正式キー:
    #   preset_name
    #
    # 旧キー:
    #   preset
    # ======================================================

    preset_name = get_value(

        data,

        "preset_name",
        "preset"

    )

    # ======================================================
    # font
    #
    # 正式キー:
    #   font
    #
    # 旧キー:
    #   font_name
    # ======================================================

    font = get_value(

        data,

        "font",
        "font_name"

    )

    # ======================================================
    # text_color
    #
    # 正式キー:
    #   text_color
    #
    # 旧キー:
    #   textColor
    #   color
    # ======================================================

    text_color = get_value(

        data,

        "text_color",
        "textColor",
        "color"

    )

    # ======================================================
    # outline_color
    #
    # 正式キー:
    #   outline_color
    #
    # 旧キー:
    #   outlineColor
    #   stroke_color
    #   strokeColor
    # ======================================================

    outline_color = get_value(

        data,

        "outline_color",
        "outlineColor",
        "stroke_color",
        "strokeColor"

    )

    # ======================================================
    # outline_width
    #
    # 正式キー:
    #   outline_width
    #
    # 旧キー:
    #   outlineWidth
    #   stroke_width
    #   strokeWidth
    # ======================================================

    outline_width = get_value(

        data,

        "outline_width",
        "outlineWidth",
        "stroke_width",
        "strokeWidth"

    )

    # ======================================================
    # subtitle_font.pyへ渡す
    #
    # 【重要】
    #
    # ここから先は正式内部キーのみ。
    #
    # 標準値は subtitle_font.py が決定する。
    # ======================================================

    settings = select_subtitle_font(

        preset_name=preset_name,

        font=font,

        text_color=text_color,

        outline_color=outline_color,

        outline_width=outline_width

    )

    return settings


# ==========================================================
# ファイル名安全化
# ==========================================================

def safe_filename(
    value
):

    if value is None:

        return None

    value = str(
        value
    ).strip()

    if not value:

        return None

    # ファイル名のみ許可
    return Path(
        value
    ).name


# ==========================================================
# DOWNLOAD_DIR取得
# ==========================================================

def get_download_dir():

    try:

        from config import DOWNLOAD_DIR

        return Path(
            DOWNLOAD_DIR
        ).resolve()

    except Exception as error:

        log(
            f"DOWNLOAD_DIR取得エラー: {error}"
        )

        # config.pyが通常存在するため、
        # ここはフォールバックとしてのみ使用。
        return Path(
            "/app/downloads"
        ).resolve()


# ==========================================================
# ファイルパス作成
# ==========================================================

def make_download_path(
    filename
):

    filename = safe_filename(
        filename
    )

    if not filename:

        return None

    download_dir = (
        get_download_dir()
    )

    return (
        download_dir
        /
        filename
    ).resolve()


# ==========================================================
# DOWNLOAD_DIR内確認
# ==========================================================

def is_inside_download_dir(
    file_path
):

    if not file_path:

        return False

    download_dir = (
        get_download_dir()
    )

    try:

        Path(
            file_path
        ).resolve().relative_to(
            download_dir
        )

        return True

    except ValueError:

        return False


# ==========================================================
# GET /subtitle-settings
#
# 現在の標準字幕設定を返す。
#
# 標準値は subtitle_font.py から取得する。
# ==========================================================

@subtitle_bp.route(
    "/subtitle-settings",
    methods=["GET"]
)
def subtitle_settings():

    log(
        "=========================================="
    )

    log(
        "GET /subtitle-settings"
    )

    try:

        settings = (
            get_default_subtitle_font_settings()
        )

        log(
            f"default settings: {settings}"
        )

        return jsonify({

            "success":
                True,

            "settings":
                settings

        })

    except Exception as error:

        log(
            f"字幕設定取得エラー: {error}"
        )

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# ==========================================================
# POST /subtitle-create-mp4
#
# MP4 + SRT 合成
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-mp4",
    methods=["POST"]
)
def subtitle_create_mp4():

    log(
        "=========================================="
    )

    log(
        "POST /subtitle-create-mp4"
    )

    try:

        # ==================================================
        # JSON
        # ==================================================

        data = get_request_json()

        log(
            f"request data: {data}"
        )

        # ==================================================
        # MP4
        #
        # ファイル名については字幕設定5キーとは
        # 別の入力項目なので従来の互換キーを維持。
        # ==================================================

        mp4_filename = get_value(

            data,

            "mp4",
            "mp4_filename",
            "video",
            "video_filename",
            "input_mp4"

        )

        # ==================================================
        # SRT
        # ==================================================

        srt_filename = get_value(

            data,

            "srt",
            "srt_filename",
            "subtitle",
            "subtitle_filename",
            "input_srt"

        )

        mp4_filename = safe_filename(
            mp4_filename
        )

        srt_filename = safe_filename(
            srt_filename
        )

        # ==================================================
        # 入力確認
        # ==================================================

        if not mp4_filename:

            return jsonify({

                "success":
                    False,

                "error":
                    "MP4ファイル名が指定されていません。"

            }), 400

        if not srt_filename:

            return jsonify({

                "success":
                    False,

                "error":
                    "SRTファイル名が指定されていません。"

            }), 400

        # ==================================================
        # 拡張子
        # ==================================================

        if not mp4_filename.lower().endswith(
            ".mp4"
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "MP4ファイルを指定してください。"

            }), 400

        if not srt_filename.lower().endswith(
            ".srt"
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "SRTファイルを指定してください。"

            }), 400

        # ==================================================
        # パス
        # ==================================================

        mp4_path = make_download_path(
            mp4_filename
        )

        srt_path = make_download_path(
            srt_filename
        )

        # ==================================================
        # セキュリティ確認
        # ==================================================

        if not is_inside_download_dir(
            mp4_path
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "不正なMP4パスです。"

            }), 400

        if not is_inside_download_dir(
            srt_path
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "不正なSRTパスです。"

            }), 400

        # ==================================================
        # ファイル存在確認
        # ==================================================

        if not mp4_path.exists():

            return jsonify({

                "success":
                    False,

                "error":
                    f"MP4ファイルがありません: {mp4_filename}"

            }), 404

        if not srt_path.exists():

            return jsonify({

                "success":
                    False,

                "error":
                    f"SRTファイルがありません: {srt_filename}"

            }), 404

        # ==================================================
        # リクエスト字幕設定
        #
        # ログ上も正式名称へ統一する。
        #
        # 旧キーの存在はHTTP入口の互換処理としてのみ扱う。
        # ======================================================

        log(
            "request subtitle settings:"
        )

        log(
            f"  preset_name: "
            f"{get_value(data, 'preset_name', 'preset')}"
        )

        log(
            f"  font: "
            f"{get_value(data, 'font', 'font_name')}"
        )

        log(
            f"  text_color: "
            f"{get_value(data, 'text_color', 'textColor', 'color')}"
        )

        log(
            f"  outline_color: "
            f"{get_value(data, 'outline_color', 'outlineColor', 'stroke_color', 'strokeColor')}"
        )

        log(
            f"  outline_width: "
            f"{get_value(data, 'outline_width', 'outlineWidth', 'stroke_width', 'strokeWidth')}"
        )

        # ==================================================
        # 字幕設定正規化
        #
        # subtitle_font.pyだけが標準値を決定する。
        # ==================================================

        subtitle_settings = (
            normalize_subtitle_settings(
                data
            )
        )

        log(
            "normalized subtitle settings:"
        )

        log(
            str(
                subtitle_settings
            )
        )

        # ==================================================
        # 正規化後のキー確認
        #
        # subtitle_font.pyから返る設定も
        # 5つの正式キーを基本とする。
        # ==================================================

        required_setting_keys = [

            "preset_name",

            "font",

            "text_color",

            "outline_color",

            "outline_width",

        ]

        for key in required_setting_keys:

            if key not in subtitle_settings:

                raise RuntimeError(

                    "字幕設定に正式キーがありません: "
                    +
                    key

                )

        # ==================================================
        # MP4 + SRT
        # ==================================================

        log(
            "=========================================="
        )

        log(
            "MP4 + SRT 合成開始"
        )

        log(
            f"MP4: {mp4_path}"
        )

        log(
            f"SRT: {srt_path}"
        )

        log(
            f"字幕設定: {subtitle_settings}"
        )

        # ==================================================
        # subtitle.py
        #
        # subtitle_settingsは正式5キーの辞書をそのまま渡す。
        # ==================================================

        log(
            "subtitle.py function: create_subtitle_mp4"
        )

        output_path = create_subtitle_mp4(

            mp4_path,

            srt_path,

            subtitle_settings=subtitle_settings

        )

        # ==================================================
        # 出力確認
        # ==================================================

        if not output_path:

            raise RuntimeError(
                "字幕MP4の出力パスが取得できませんでした。"
            )

        output_path = Path(
            output_path
        ).resolve()

        if not output_path.exists():

            raise RuntimeError(
                "字幕MP4が作成されていません。"
            )

        if not output_path.is_file():

            raise RuntimeError(
                "字幕MP4出力先がファイルではありません。"
            )

        # ==================================================
        # サイズ
        # ==================================================

        try:

            output_size = (
                output_path.stat().st_size
            )

        except OSError:

            output_size = 0

        if output_size <= 0:

            raise RuntimeError(
                "字幕MP4のサイズが0 bytesです。"
            )

        # ==================================================
        # 成功
        # ==================================================

        log(
            "=========================================="
        )

        log(
            "字幕MP4作成成功"
        )

        log(
            f"output: {output_path}"
        )

        log(
            f"size: {output_size} bytes"
        )

        log(
            f"settings: {subtitle_settings}"
        )

        log(
            "=========================================="
        )

        return jsonify({

            "success":
                True,

            "message":
                "字幕MP4を作成しました。",

            "output":
                output_path.name,

            "output_path":
                str(output_path),

            "size":
                output_size,

            "subtitle_settings":
                subtitle_settings

        })

    except Exception as error:

        log(
            "=========================================="
        )

        log(
            "字幕MP4作成失敗"
        )

        log(
            f"error: {error}"
        )

        traceback.print_exc()

        log(
            "=========================================="
        )

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# ==========================================================
# POST /subtitle-font-settings
#
# 字幕設定だけを正規化して確認するAPI
#
# デバッグ用。
#
# 入力:
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# 旧キーもHTTP入口では互換対応。
# ==========================================================

@subtitle_bp.route(
    "/subtitle-font-settings",
    methods=["POST"]
)
def subtitle_font_settings():

    log(
        "=========================================="
    )

    log(
        "POST /subtitle-font-settings"
    )

    try:

        data = get_request_json()

        log(
            f"request data: {data}"
        )

        settings = (
            normalize_subtitle_settings(
                data
            )
        )

        log(
            f"normalized: {settings}"
        )

        # ==================================================
        # 正規化後のキー確認
        # ==================================================

        required_setting_keys = [

            "preset_name",

            "font",

            "text_color",

            "outline_color",

            "outline_width",

        ]

        for key in required_setting_keys:

            if key not in settings:

                raise RuntimeError(

                    "字幕設定に正式キーがありません: "
                    +
                    key

                )

        return jsonify({

            "success":
                True,

            "settings":
                settings

        })

    except Exception as error:

        log(
            f"字幕設定正規化エラー: {error}"
        )

        traceback.print_exc()

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# ==========================================================
# Blueprint登録用
#
# app.py / main.py:
#
# from routes.subtitle_routes import subtitle_bp
#
# app.register_blueprint(subtitle_bp)
# ==========================================================

__all__ = [
    "subtitle_bp",
]
