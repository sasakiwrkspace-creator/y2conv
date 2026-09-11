# ==========================================================
# subtitle_font.py
#
# 字幕フォント・字幕スタイル設定
#
# 正式な内部キー:
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# subtitle_routes.py / subtitle.py から使用
#
# 標準設定:
#   フォント     : Noto Sans CJK JP
#   文字色       : 白
#   縁色         : 青
#   縁太さ       : 5
#
# ==========================================================


# ==========================================================
# 字幕カラー
# ==========================================================

SUBTITLE_COLORS = {

    "白": {
        "hex": "#FFFFFF",
        "ass": "&H00FFFFFF",
    },

    "黒": {
        "hex": "#000000",
        "ass": "&H00000000",
    },

    "青": {
        "hex": "#0000FF",
        "ass": "&H00FF0000",
    },

    "赤": {
        "hex": "#FF0000",
        "ass": "&H000000FF",
    },

    "緑": {
        "hex": "#00FF00",
        "ass": "&H0000FF00",
    },

    "黄": {
        "hex": "#FFFF00",
        "ass": "&H0000FFFF",
    },

}


# ==========================================================
# プリセット
#
# preset_nameをキーとして使用する。
#
# ★字幕設定値の唯一の情報源
# ==========================================================

SUBTITLE_PRESETS = {

    "標準": {

        "font":
            "Noto Sans CJK JP",

        "text_color":
            "白",

        "outline_color":
            "青",

        "outline_width":
            5,

    },

    "白文字青縁": {

        "font":
            "Noto Sans CJK JP",

        "text_color":
            "白",

        "outline_color":
            "青",

        "outline_width":
            5,

    },

}


# ==========================================================
# 標準設定
#
# ★SUBTITLE_PRESETS["標準"] から生成する。
#
# 二重管理を防止するため、
# font / text_color / outline_color / outline_width は
# ここでは個別に定義しない。
#
# 正式な内部キー:
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
# ==========================================================

DEFAULT_PRESET_NAME = "標準"


def _build_default_subtitle_font_settings():

    default_preset = SUBTITLE_PRESETS.get(
        DEFAULT_PRESET_NAME
    )

    if not isinstance(
        default_preset,
        dict
    ):

        raise RuntimeError(
            "標準プリセットが定義されていません: "
            f"{DEFAULT_PRESET_NAME}"
        )

    settings = dict(
        default_preset
    )

    settings[
        "preset_name"
    ] = DEFAULT_PRESET_NAME

    return settings


# ==========================================================
# 標準設定
#
# 外部から従来通り
# DEFAULT_SUBTITLE_FONT_SETTINGS
# を参照できるようにする。
#
# 実際の設定値はSUBTITLE_PRESETS["標準"]を使用する。
# ==========================================================

DEFAULT_SUBTITLE_FONT_SETTINGS = (
    _build_default_subtitle_font_settings()
)


# ==========================================================
# ログ
# ==========================================================

def _log(
    message
):

    print(
        "[SUBTITLE_FONT]",
        message,
        flush=True
    )


# ==========================================================
# 整数変換
# ==========================================================

def _normalize_outline_width(
    value
):

    try:

        value = int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        value = DEFAULT_SUBTITLE_FONT_SETTINGS[
            "outline_width"
        ]

    return max(
        0,
        min(
            value,
            10
        )
    )


# ==========================================================
# カラー名正規化
#
# ※不正カラーはフォールバックせず、
#   get_subtitle_color() でエラーにする。
#
# select_subtitle_font() 内では、
#   不正値 → 標準カラー
# の既存動作を維持する。
# ==========================================================

def _normalize_color(
    value,
    default
):

    if value is None:

        return default

    value = str(
        value
    ).strip()

    if value in SUBTITLE_COLORS:

        return value

    return default


# ==========================================================
# フォント名正規化
# ==========================================================

def _normalize_font(
    value
):

    if value is None:

        return DEFAULT_SUBTITLE_FONT_SETTINGS[
            "font"
        ]

    value = str(
        value
    ).strip()

    if not value:

        return DEFAULT_SUBTITLE_FONT_SETTINGS[
            "font"
        ]

    return value


# ==========================================================
# デフォルト設定取得
#
# 戻り値の正式キー:
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# ※HEXはここでは返さない。
# ==========================================================

def get_default_subtitle_font_settings():

    settings = dict(
        DEFAULT_SUBTITLE_FONT_SETTINGS
    )

    _log(
        "get_default_subtitle_font_settings()"
    )

    _log(
        f"default: {settings}"
    )

    return settings


# ==========================================================
# 字幕設定選択
#
# 正式な引数:
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
#
# settingsを渡した場合も、
# 内部では正式キー5つを使用する。
#
# 旧キー:
#   preset
#
# は入力互換のためのみ許可する。
# ==========================================================

def select_subtitle_font(
    preset_name=None,
    font=None,
    text_color=None,
    outline_color=None,
    outline_width=None,
    settings=None
):

    _log(
        "select_subtitle_font() START"
    )


    # ======================================================
    # settings
    # ======================================================

    if isinstance(
        settings,
        dict
    ):

        source = dict(
            settings
        )

    else:

        source = {}


    # ======================================================
    # preset_name
    #
    # 正式キー:
    #   preset_name
    #
    # 旧キー:
    #   preset
    #
    # 旧キーは外部入力互換のみ。
    # 内部変数はpreset_nameへ統一する。
    #
    # settings側を優先する既存仕様を維持。
    # ======================================================

    source_preset_name = (
        source.get(
            "preset_name"
        )
    )

    if source_preset_name is None:

        source_preset_name = (
            source.get(
                "preset"
            )
        )

    preset_name = (

        source_preset_name

        or

        preset_name

        or

        DEFAULT_PRESET_NAME

    )

    preset_name = str(
        preset_name
    ).strip()


    # ======================================================
    # preset_name="" の確認
    #
    # 通常はセレクトボックスから必ず値が入る。
    #
    # 初期値などで空文字が入った場合は、
    # 標準プリセットへフォールバックする。
    # ======================================================

    if not preset_name:

        _log(
            "preset_name is empty. "
            f"fallback to default: {DEFAULT_PRESET_NAME}"
        )

        preset_name = (
            DEFAULT_PRESET_NAME
        )


    # ======================================================
    # プリセット取得
    # ======================================================

    preset_settings = (
        SUBTITLE_PRESETS.get(
            preset_name
        )
    )


    # ======================================================
    # 存在しないpreset_nameの場合
    #
    # 標準プリセットへ戻す。
    # ======================================================

    if preset_settings is None:

        _log(
            "unknown preset_name: "
            f"{preset_name}"
        )

        preset_name = (
            DEFAULT_PRESET_NAME
        )

        preset_settings = (
            SUBTITLE_PRESETS[
                preset_name
            ]
        )


    # ======================================================
    # ベース設定
    # ======================================================

    result_font = (
        preset_settings.get(
            "font",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "font"
            ]
        )
    )

    result_text_color = (
        preset_settings.get(
            "text_color",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "text_color"
            ]
        )

    )

    result_outline_color = (
        preset_settings.get(
            "outline_color",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_color"
            ]
        )
    )

    result_outline_width = (
        preset_settings.get(
            "outline_width",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_width"
            ]
        )
    )


    # ======================================================
    # settingsから正式キーを上書き
    #
    # Noneの場合は上書きしない。
    #
    # ★この優先順位は既存仕様を維持。
    # ======================================================

    if (
        "font" in source
        and
        source.get("font") is not None
    ):

        result_font = source.get(
            "font"
        )


    if (
        "text_color" in source
        and
        source.get("text_color") is not None
    ):

        result_text_color = source.get(
            "text_color"
        )


    if (
        "outline_color" in source
        and
        source.get("outline_color") is not None
    ):

        result_outline_color = source.get(
            "outline_color"
        )


    if (
        "outline_width" in source
        and
        source.get("outline_width") is not None
    ):

        result_outline_width = source.get(
            "outline_width"
        )


    # ======================================================
    # 関数引数から正式キーを上書き
    #
    # Noneの場合は上書きしない。
    #
    # ★settingsより関数引数を優先。
    # ======================================================

    if font is not None:

        result_font = font


    if text_color is not None:

        result_text_color = text_color


    if outline_color is not None:

        result_outline_color = outline_color


    if outline_width is not None:

        result_outline_width = outline_width


    # ======================================================
    # 正規化
    # ======================================================

    result_font = _normalize_font(
        result_font
    )

    result_text_color = _normalize_color(

        result_text_color,

        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "text_color"
        ]

    )

    result_outline_color = _normalize_color(

        result_outline_color,

        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "outline_color"
        ]

    )

    result_outline_width = _normalize_outline_width(
        result_outline_width
    )


    # ======================================================
    # 最終設定
    #
    # ★内部の正式な設定キーはこの5つ
    #
    #   preset_name
    #   font
    #   text_color
    #   outline_color
    #   outline_width
    # ======================================================

    normalized = {

        "preset_name":
            preset_name,

        "font":
            result_font,

        "text_color":
            result_text_color,

        "outline_color":
            result_outline_color,

        "outline_width":
            result_outline_width,

    }


    # ======================================================
    # ログ
    # ======================================================

    _log(
        f"normalized: {normalized}"
    )

    _log(
        "select_subtitle_font() COMPLETE"
    )

    return normalized


# ==========================================================
# カラー情報取得
#
# ※ここでは不正カラーをフォールバックしない。
#   明示的にRuntimeErrorを発生させる。
# ==========================================================

def get_subtitle_color(
    color_name
):

    if color_name not in SUBTITLE_COLORS:

        raise RuntimeError(
            f"字幕カラーが定義されていません: "
            f"{color_name}"
        )

    return dict(
        SUBTITLE_COLORS[
            color_name
        ]
    )


# ==========================================================
# 互換用
# ==========================================================

def get_subtitle_font_settings(
    *args,
    **kwargs
):

    return select_subtitle_font(
        *args,
        **kwargs
    )


# ==========================================================
# 標準設定確認
#
# ★preset_nameを含めて5項目すべて確認する。
# ==========================================================

def is_default_subtitle_setting(
    settings
):

    if not isinstance(
        settings,
        dict
    ):

        return False

    try:

        outline_width = int(
            settings.get(
                "outline_width",
                -1
            )
        )

    except (
        ValueError,
        TypeError
    ):

        return False

    return (

        settings.get(
            "preset_name"
        )
        ==
        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "preset_name"
        ]

        and

        settings.get(
            "font"
        )
        ==
        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "font"
        ]

        and

        settings.get(
            "text_color"
        )
        ==
        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "text_color"
        ]

        and

        settings.get(
            "outline_color"
        )
        ==
        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "outline_color"
        ]

        and

        outline_width
        ==
        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "outline_width"
        ]

    )


# ==========================================================
# テスト
# ==========================================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        "subtitle_font.py test"
    )

    print(
        "=========================================="
    )


    # ======================================================
    # 標準設定
    # ======================================================

    settings = (
        get_default_subtitle_font_settings()
    )

    print(
        settings
    )


    # ======================================================
    # 明示指定
    # ======================================================

    print(
        "=========================================="
    )

    settings = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width=5

    )

    print(
        settings
    )


    # ======================================================
    # 旧キー互換確認
    #
    # presetは外部入力互換としてのみ許可。
    # 戻り値はpreset_nameに統一される。
    # ======================================================

    print(
        "=========================================="
    )

    settings = select_subtitle_font(

        settings={

            "preset":
                "標準",

            "font":
                "Noto Sans CJK JP",

            "text_color":
                "白",

            "outline_color":
                "青",

            "outline_width":
                5,

        }

    )

    print(
        settings
    )


    # ======================================================
    # 標準設定判定
    # ======================================================

    print(
        "=========================================="
    )

    print(
        "is_default:"
    )

    print(
        is_default_subtitle_setting(
            settings
        )
    )

    print(
        "=========================================="
    )


    # ======================================================
    # 不正カラー確認
    # ======================================================

    print(
        "=========================================="
    )

    print(
        "invalid color test:"
    )

    try:

        get_subtitle_color(
            "紫"
        )

    except RuntimeError as error:

        print(
            error
        )

    print(
        "=========================================="
    )


    # ======================================================
    # 空preset_name確認
    # ======================================================

    print(
        "=========================================="
    )

    print(
        "empty preset_name test:"
    )

    settings = select_subtitle_font(
        preset_name=""
    )

    print(
        settings
    )

    print(
        "=========================================="
    )
