# ==========================================================
# subtitle_font.py
#
# 字幕フォント・字幕スタイル設定
#
# 標準設定:
#   フォント     : Noto Sans CJK JP
#   文字色       : 白
#   縁色         : 青
#   縁太さ       : 5
#
# subtitle_routes.py / subtitle.py から使用
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

    "黄色": {
        "hex": "#FFFF00",
        "ass": "&H0000FFFF",
    },

}


# ==========================================================
# 標準設定
#
# ★ここが標準プリセット
#
# 白文字
# 青縁
# 縁5
# ==========================================================

DEFAULT_SUBTITLE_FONT_SETTINGS = {

    "preset_name":
        "標準",

    "font":
        "Noto Sans CJK JP",

    "text_color":
        "白",

    "text_color_hex":
        "#FFFFFF",

    "outline_color":
        "青",

    "outline_color_hex":
        "#0000FF",

    "outline_width":
        5,

}


# ==========================================================
# プリセット
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

        value = 5

    return max(
        0,
        min(
            value,
            10
        )
    )


# ==========================================================
# カラー名正規化
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

        return "Noto Sans CJK JP"

    value = str(
        value
    ).strip()

    if not value:

        return "Noto Sans CJK JP"

    return value


# ==========================================================
# デフォルト設定取得
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
# 重要:
#
# 引数が明示されている場合は、
# その値を優先する。
#
# Noneの場合だけ標準設定を使用。
#
# これにより、
#
# Route:
#   白 / 青 / 5
#
# が勝手に別設定へ変更されない。
# ==========================================================

def select_subtitle_font(
    font=None,
    text_color=None,
    outline_color=None,
    outline_width=None,
    preset=None,
    settings=None
):

    _log(
        "select_subtitle_font() START"
    )

    # ======================================================
    # settingsが渡された場合
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
    # preset
    # ======================================================

    preset_name = (
        source.get(
            "preset_name"
        )
        or
        source.get(
            "preset"
        )
        or
        preset
        or
        "標準"
    )

    preset_name = str(
        preset_name
    ).strip()

    preset_settings = (
        SUBTITLE_PRESETS.get(
            preset_name
        )
    )

    # ======================================================
    # 存在しないpresetの場合
    # ======================================================

    if preset_settings is None:

        preset_name = "標準"

        preset_settings = (
            SUBTITLE_PRESETS[
                "標準"
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
    # settingsから値を上書き
    #
    # ★明示された値を優先
    # ======================================================

    if "font" in source:

        result_font = source.get(
            "font"
        )

    if "text_color" in source:

        result_text_color = source.get(
            "text_color"
        )

    if "outline_color" in source:

        result_outline_color = source.get(
            "outline_color"
        )

    if "outline_width" in source:

        result_outline_width = source.get(
            "outline_width"
        )


    # ======================================================
    # 関数引数から値を上書き
    #
    # Noneの場合は上書きしない
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
        "白"
    )

    result_outline_color = _normalize_color(
        result_outline_color,
        "青"
    )

    result_outline_width = _normalize_outline_width(
        result_outline_width
    )


    # ======================================================
    # HEX
    # ======================================================

    text_color_info = (
        SUBTITLE_COLORS.get(
            result_text_color,
            SUBTITLE_COLORS[
                "白"
            ]
        )
    )

    outline_color_info = (
        SUBTITLE_COLORS.get(
            result_outline_color,
            SUBTITLE_COLORS[
                "青"
            ]
        )
    )


    # ======================================================
    # 最終設定
    # ======================================================

    normalized = {

        "preset_name":
            preset_name,

        "font":
            result_font,

        "text_color":
            result_text_color,

        "text_color_hex":
            text_color_info[
                "hex"
            ],

        "outline_color":
            result_outline_color,

        "outline_color_hex":
            outline_color_info[
                "hex"
            ],

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
# ==========================================================

def is_default_subtitle_setting(
    settings
):

    if not isinstance(
        settings,
        dict
    ):

        return False

    return (

        settings.get(
            "font"
        )
        ==
        "Noto Sans CJK JP"

        and

        settings.get(
            "text_color"
        )
        ==
        "白"

        and

        settings.get(
            "outline_color"
        )
        ==
        "青"

        and

        int(
            settings.get(
                "outline_width",
                -1
            )
        )
        ==
        5

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

    settings = (
        get_default_subtitle_font_settings()
    )

    print(
        settings
    )

    print(
        "=========================================="
    )

    settings = select_subtitle_font(
        font="Noto Sans CJK JP",
        text_color="白",
        outline_color="青",
        outline_width=5
    )

    print(
        settings
    )

    print(
        "=========================================="
    )
