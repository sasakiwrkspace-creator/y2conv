# ==========================================================
# routes/subtitle_routes.py
#
# 字幕関連 API Route
#
# 役割:
#   - HTTPリクエストを受け取る
#   - 字幕設定を subtitle_font.py で正規化
#   - subtitle.py に処理を渡す
#   - MP3からSRTを作成する
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
# ただし、これらはHTTP入口でのみ使用する。
#
# Route内部では必ず正式キーへ変換する。
#
# ==========================================================


import traceback

from pathlib import Path

from flask import (
    Blueprint,
    request,
    jsonify,
)

from routes.gemini import (
    transcribe_mp3,
    save_srt,
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
# HTTP入力値取得
# ==========================================================
#
# ここだけ旧キーを許可する。
#
# Route内部では正式キーのみを使用する。
#
# 正式キー:
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
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
# HTTP入力:
#
#   正式キー
#   または旧キー
#
#        ↓
#
# 正式内部キーへ変換
#
#        ↓
#
# subtitle_font.py
#
#        ↓
#
# 正規化済み設定
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
    # 正式キー: preset_name
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
    # 正式キー: font
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
    # 正式キー: text_color
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
    # 正式キー: outline_color
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
    # 正式キー: outline_width
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
    # subtitle_font.py
    #
    # ここから先は正式キーのみ使用する。
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
# MP3 → SRT 共通処理
#
# タブ1:
#
#   YouTube
#      ↓
#   MP4作成
#      ↓
#   MP3作成
#      ↓
#   create_srt_from_mp3()
#      ↓
#   Gemini
#      ↓
#   SRT
#
# タブ2:
#
#   ローカルMP3アップロード
#      ↓
#   downloads保存
#      ↓
#   create_srt_from_mp3()
#      ↓
#   Gemini
#      ↓
#   SRT
#
# GeminiへMP3を渡してSRTを作る処理は
# この関数に一本化する。
# ==========================================================

def create_srt_from_mp3(
    mp3_path
):

    mp3_path = Path(
        mp3_path
    ).resolve()

    # ======================================================
    # MP3確認
    # ======================================================

    if not mp3_path.exists():

        raise FileNotFoundError(
            f"MP3がありません: {mp3_path}"
        )

    if not mp3_path.is_file():

        raise ValueError(
            "MP3のパスがファイルではありません"
        )

    if not mp3_path.name.lower().endswith(
        ".mp3"
    ):

        raise ValueError(
            "MP3ファイルを指定してください"
        )

    try:

        mp3_size = (
            mp3_path.stat().st_size
        )

    except OSError as error:

        raise RuntimeError(
            f"MP3ファイルサイズを取得できません: {error}"
        )

    if mp3_size <= 0:

        raise ValueError(
            "MP3ファイルが0 bytesです"
        )

    # ======================================================
    # DOWNLOAD_DIR内確認
    #
    # タブ1・タブ2ともdownloadsにあるMP3を
    # Geminiへ渡す。
    # ======================================================

    if not is_inside_download_dir(
        mp3_path
    ):

        raise ValueError(
            "MP3がDOWNLOAD_DIR外にあります"
        )

    # ======================================================
    # 開始ログ
    # ======================================================

    log(
        "=========================================="
    )

    log(
        "MP3 → SRT 開始"
    )

    log(
        f"MP3: {mp3_path}"
    )

    log(
        f"MP3 size: {mp3_size} bytes"
    )

    # ======================================================
    # Gemini文字起こし
    # ======================================================

    log(
        "Gemini transcribe START"
    )

    srt_text = transcribe_mp3(
        str(mp3_path)
    )

    if not srt_text:

        raise RuntimeError(
            "GeminiからSRT結果を取得できませんでした"
        )

    log(
        "Gemini transcribe COMPLETE"
    )

    # ======================================================
    # SRT保存
    # ======================================================

    log(
        "SRT save START"
    )

    srt_path = save_srt(
        str(mp3_path),
        srt_text
    )

    if not srt_path:

        raise RuntimeError(
            "SRT保存先が返されませんでした"
        )

    srt_path = Path(
        srt_path
    ).resolve()

    # ======================================================
    # SRT確認
    # ======================================================

    if not srt_path.exists():

        raise RuntimeError(
            f"SRTファイルの保存に失敗しました: {srt_path}"
        )

    if not srt_path.is_file():

        raise RuntimeError(
            "SRT保存先がファイルではありません"
        )

    if not srt_path.name.lower().endswith(
        ".srt"
    ):

        raise ValueError(
            "SRTファイルの拡張子が.srtではありません"
        )

    try:

        srt_size = (
            srt_path.stat().st_size
        )

    except OSError as error:

        raise RuntimeError(
            f"SRTファイルサイズを取得できません: {error}"
        )

    if srt_size <= 0:

        raise RuntimeError(
            "SRTファイルが0 bytesです"
        )

    log(
        "SRT save COMPLETE"
    )

    log(
        f"SRT: {srt_path}"
    )

    log(
        f"SRT size: {srt_size} bytes"
    )

    log(
        "MP3 → SRT 完了"
    )

    log(
        "=========================================="
    )

    # ======================================================
    # 戻り値
    # ======================================================

    return {

        "mp3_file":
            mp3_path.name,

        "srt_file":
            srt_path.name,

        "srt_path":
            str(srt_path),

    }


# ==========================================================
# 字幕設定ログ
#
# ログ上も正式5キーへ統一する。
# ==========================================================

def log_subtitle_request_settings(
    settings
):

    log(
        "request subtitle settings:"
    )

    log(
        f"  preset_name: "
        f"{settings.get('preset_name')}"
    )

    log(
        f"  font: "
        f"{settings.get('font')}"
    )

    log(
        f"  text_color: "
        f"{settings.get('text_color')}"
    )

    log(
        f"  outline_color: "
        f"{settings.get('outline_color')}"
    )

    log(
        f"  outline_width: "
        f"{settings.get('outline_width')}"
    )


# ==========================================================
# 正規化後の正式キー確認
# ==========================================================

def validate_subtitle_settings(
    settings
):

    if not isinstance(
        settings,
        dict
    ):

        raise RuntimeError(
            "字幕設定が辞書形式ではありません。"
        )

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

    return True


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

        validate_subtitle_settings(
            settings
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

        traceback.print_exc()

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# ==========================================================
# POST /subtitle-upload-mp3
#
# タブ2:
#
# ローカルMP3をdownloadsへ保存する。
#
# その後、フロント側から
#
#   /subtitle-create-srt
#
# を呼び出してSRTを作成する。
#
# ==========================================================

@subtitle_bp.route(
    "/subtitle-upload-mp3",
    methods=["POST"]
)
def subtitle_upload_mp3():

    log(
        "=========================================="
    )

    log(
        "POST /subtitle-upload-mp3"
    )

    try:

        uploaded_file = request.files.get(
            "file"
        )

        if uploaded_file is None:

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3ファイルが選択されていません。"

            }), 400

        original_filename = (
            uploaded_file.filename
            or ""
        ).strip()

        if not original_filename:

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3ファイル名がありません。"

            }), 400

        safe_name = safe_filename(
            original_filename
        )

        if not safe_name:

            return jsonify({

                "success":
                    False,

                "error":
                    "安全なファイル名を取得できません。"

            }), 400

        if not safe_name.lower().endswith(
            ".mp3"
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3ファイルを指定してください。"

            }), 400

        mp3_path = make_download_path(
            safe_name
        )

        if mp3_path is None:

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3保存先を作成できません。"

            }), 400

        if not is_inside_download_dir(
            mp3_path
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "不正なMP3保存先です。"

            }), 400

        # ==================================================
        # downloads保存
        # ==================================================

        mp3_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        existed = mp3_path.exists()

        if existed:

            log(
                f"同名MP3を上書き: {mp3_path}"
            )

        uploaded_file.save(
            str(mp3_path)
        )

        # ==================================================
        # 保存確認
        # ==================================================

        if not mp3_path.exists():

            raise RuntimeError(
                "MP3ファイルの保存に失敗しました。"
            )

        if not mp3_path.is_file():

            raise RuntimeError(
                "MP3保存先がファイルではありません。"
            )

        mp3_size = (
            mp3_path.stat().st_size
        )

        if mp3_size <= 0:

            raise RuntimeError(
                "保存されたMP3が0 bytesです。"
            )

        log(
            f"MP3保存完了: {mp3_path}"
        )

        log(
            f"size: {mp3_size} bytes"
        )

        log(
            f"overwritten: {existed}"
        )

        return jsonify({

            "success":
                True,

            "message":
                "MP3を保存しました。",

            "mp3_file":
                mp3_path.name,

            "filename":
                mp3_path.name,

            "path":
                str(mp3_path),

            "size":
                mp3_size,

            "overwritten":
                existed

        })

    except Exception as error:

        log(
            "MP3アップロード失敗"
        )

        log(
            f"error: {error}"
        )

        traceback.print_exc()

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 500


# ==========================================================
# POST /subtitle-create-srt
#
# MP3 → SRT
#
# downloadsに存在するMP3を指定し、
# 共通関数 create_srt_from_mp3() を呼ぶ。
#
# ==========================================================

@subtitle_bp.route(
    "/subtitle-create-srt",
    methods=["POST"]
)
def subtitle_create_srt():

    log(
        "=========================================="
    )

    log(
        "POST /subtitle-create-srt"
    )

    try:

        data = get_request_json()

        log(
            f"request data: {data}"
        )

        # ==================================================
        # MP3ファイル名
        #
        # 互換キーも許可する。
        # ==================================================

        mp3_filename = get_value(

            data,

            "mp3_file",
            "mp3",
            "filename",
            "input_mp3"

        )

        mp3_filename = safe_filename(
            mp3_filename
        )

        # ==================================================
        # 入力確認
        # ==================================================

        if not mp3_filename:

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3ファイル名が指定されていません。"

            }), 400

        # ==================================================
        # 拡張子
        # ==================================================

        if not mp3_filename.lower().endswith(
            ".mp3"
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3ファイルを指定してください。"

            }), 400

        # ==================================================
        # パス
        # ==================================================

        mp3_path = make_download_path(
            mp3_filename
        )

        if mp3_path is None:

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3ファイルのパスを作成できません。"

            }), 400

        # ==================================================
        # セキュリティ確認
        # ==================================================

        if not is_inside_download_dir(
            mp3_path
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "不正なMP3パスです。"

            }), 400

        # ==================================================
        # ファイル存在確認
        # ==================================================

        if not mp3_path.exists():

            return jsonify({

                "success":
                    False,

                "error":
                    f"MP3ファイルがありません: {mp3_filename}"

            }), 404

        if not mp3_path.is_file():

            return jsonify({

                "success":
                    False,

                "error":
                    "指定されたMP3パスがファイルではありません。"

            }), 400

        if mp3_path.stat().st_size <= 0:

            return jsonify({

                "success":
                    False,

                "error":
                    "MP3ファイルが0 bytesです。"

            }), 400

        # ==================================================
        # 共通MP3 → SRT処理
        #
        # タブ1・タブ2ともここへ集約する。
        # ==================================================

        result = create_srt_from_mp3(
            mp3_path
        )

        # ==================================================
        # 成功
        # ==================================================

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

    except FileNotFoundError as error:

        log(
            f"MP3/SRTファイルがありません: {error}"
        )

        return jsonify({

            "success":
                False,

            "error":
                str(error)

        }), 404

    except Exception as error:

        log(
            "MP3 → SRT 作成失敗"
        )

        log(
            f"error: {error}"
        )

        traceback.print_exc()

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
        # 字幕設定5キーとは別の入力項目。
        # 既存の互換キーを維持する。
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
        # 字幕設定
        #
        # HTTP入口では旧キーも受け付ける。
        #
        # normalize_subtitle_settings()
        # が正式5キーへ変換する。
        # ==================================================

        request_subtitle_settings = {

            "preset_name":
                get_value(
                    data,
                    "preset_name",
                    "preset"
                ),

            "font":
                get_value(
                    data,
                    "font",
                    "font_name"
                ),

            "text_color":
                get_value(
                    data,
                    "text_color",
                    "textColor",
                    "color"
                ),

            "outline_color":
                get_value(
                    data,
                    "outline_color",
                    "outlineColor",
                    "stroke_color",
                    "strokeColor"
                ),

            "outline_width":
                get_value(
                    data,
                    "outline_width",
                    "outlineWidth",
                    "stroke_width",
                    "strokeWidth"
                ),

        }

        # ==================================================
        # ログ
        # ==================================================

        log_subtitle_request_settings(
            request_subtitle_settings
        )

        # ==================================================
        # 字幕設定正規化
        #
        # 標準値の決定は
        # subtitle_font.pyだけが担当する。
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
        # ==================================================

        validate_subtitle_settings(
            subtitle_settings
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
        # 正規化済みの設定をそのまま渡す。
        #
        # subtitle.py側でも
        #
        #   preset_name
        #   font
        #   text_color
        #   outline_color
        #   outline_width
        #
        # の5キーを使用する。
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
# 正式内部キー:
#
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# 旧キーはHTTP入口でのみ互換対応する。
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

        validate_subtitle_settings(
            settings
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
