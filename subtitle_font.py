# ==========================================================
# subtitle_font.py
#
# 字幕フォント設定
# ==========================================================


from copy import deepcopy


# ==========================================================
# 色
# ==========================================================

SUBTITLE_COLORS = {

    "白": "#FFFFFF",

    "黒": "#000000",

    "赤": "#FF0000",

    "青": "#0000FF",

    "黄": "#FFFF00",

}


# ==========================================================
# フォント
# ==========================================================

SUBTITLE_FONTS = [

    "Noto Sans CJK JP",

    "Noto Sans JP",

    "Noto Serif CJK JP",

    "Noto Serif JP",

    "IPAGothic",

    "IPAMincho",

]


# ==========================================================
# 縁取り太さ
# ==========================================================

MIN_OUTLINE_WIDTH = 0

MAX_OUTLINE_WIDTH = 10

DEFAULT_OUTLINE_WIDTH = 5


# ==========================================================
# デフォルトプリセット
# ==========================================================

DEFAULT_SUBTITLE_PRESET = "標準"


# ==========================================================
# プリセット
# ==========================================================

SUBTITLE_FONT_PRESETS = {

    "標準": {

        "font": "Noto Sans CJK JP",

        "text_color": "白",

        "outline_color": "青",

        "outline_width": 5,

    },

    "ゴシック": {

        "font": "Noto Sans CJK JP",

        "text_color": "白",

        "outline_color": "青",

        "outline_width": 5,

    },

    "明朝": {

        "font": "Noto Serif CJK JP",

        "text_color": "白",

        "outline_color": "青",

        "outline_width": 5,

    },

    "太字ゴシック": {

        "font": "Noto Sans CJK JP",

        "text_color": "白",

        "outline_color": "青",

        "outline_width": 5,

    },

    "太字明朝": {

        "font": "Noto Serif CJK JP",

        "text_color": "白",

        "outline_color": "青",

        "outline_width": 5,

    },

}


# ==========================================================
# 色HEX
# ==========================================================

def get_color_hex(
    color_name
):

    return SUBTITLE_COLORS.get(
        color_name,
        "#FFFFFF"
    )


# ==========================================================
# 縁取り太さ
# ==========================================================

def normalize_outline_width(
    value
):

    if value is None:

        return DEFAULT_OUTLINE_WIDTH

    try:

        width = int(
            round(
                float(value)
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return DEFAULT_OUTLINE_WIDTH

    width = max(
        MIN_OUTLINE_WIDTH,
        min(
            MAX_OUTLINE_WIDTH,
            width
        )
    )

    return width


# ==========================================================
# 色
# ==========================================================

def normalize_color(
    value,
    default_color
):

    if value in SUBTITLE_COLORS:

        return value

    return default_color


# ==========================================================
# フォント
# ==========================================================

def normalize_font(
    value,
    default_font
):

    if value in SUBTITLE_FONTS:

        return value

    return default_font


# ==========================================================
# プリセット取得
# ==========================================================

def get_subtitle_font_presets():

    return list(
        SUBTITLE_FONT_PRESETS.keys()
    )


# ==========================================================
# フォント一覧
# ==========================================================

def get_subtitle_fonts():

    return list(
        SUBTITLE_FONTS
    )


# ==========================================================
# 色一覧
# ==========================================================

def get_subtitle_colors():

    return dict(
        SUBTITLE_COLORS
    )


# ==========================================================
# 字幕フォント設定
# ==========================================================

def select_subtitle_font(
    font=None,
    text_color=None,
    outline_color=None,
    outline_width=None,
    preset=None,
    settings=None
):

    print(
        "[SUBTITLE_FONT] select_subtitle_font() START",
        flush=True
    )


    # ======================================================
    # settings
    # ======================================================

    if isinstance(
        settings,
        dict
    ):

        input_settings = deepcopy(
            settings
        )

    else:

        input_settings = {}


    # ======================================================
    # preset
    # ======================================================

    requested_preset = (

        input_settings.get(
            "preset_name"
        )

        or

        input_settings.get(
            "preset"
        )

        or

        preset

        or

        DEFAULT_SUBTITLE_PRESET

    )


    if requested_preset not in SUBTITLE_FONT_PRESETS:

        requested_preset = (
            DEFAULT_SUBTITLE_PRESET
        )


    preset_settings = deepcopy(

        SUBTITLE_FONT_PRESETS[
            requested_preset
        ]

    )


    # ======================================================
    # font
    # ======================================================

    requested_font = (

        input_settings.get(
            "font"
        )

        if "font" in input_settings

        else font

    )


    if requested_font is None:

        requested_font = (
            preset_settings[
                "font"
            ]
        )


    final_font = normalize_font(

        requested_font,

        preset_settings[
            "font"
        ]

    )


    # ======================================================
    # text color
    # ======================================================

    requested_text_color = (

        input_settings.get(
            "text_color"
        )

        if "text_color" in input_settings

        else text_color

    )


    if requested_text_color is None:

        requested_text_color = (
            preset_settings[
                "text_color"
            ]
        )


    final_text_color = normalize_color(

        requested_text_color,

        preset_settings[
            "text_color"
        ]

    )


    # ======================================================
    # outline color
    # ======================================================

    requested_outline_color = (

        input_settings.get(
            "outline_color"
        )

        if "outline_color" in input_settings

        else outline_color

    )


    if requested_outline_color is None:

        requested_outline_color = (
            preset_settings[
                "outline_color"
            ]
        )


    final_outline_color = normalize_color(

        requested_outline_color,

        preset_settings[
            "outline_color"
        ]

    )


    # ======================================================
    # outline width
    # ======================================================

    requested_outline_width = (

        input_settings.get(
            "outline_width"
        )

        if "outline_width" in input_settings

        else outline_width

    )


    if requested_outline_width is None:

        requested_outline_width = (
            preset_settings.get(
                "outline_width",
                DEFAULT_OUTLINE_WIDTH
            )
        )


    final_outline_width = (
        normalize_outline_width(
            requested_outline_width
        )
    )


    # ======================================================
    # プリセット一致判定
    # ======================================================

    same_as_preset = (

        final_font
        ==
        preset_settings["font"]

        and

        final_text_color
        ==
        preset_settings["text_color"]

        and

        final_outline_color
        ==
        preset_settings["outline_color"]

        and

        final_outline_width
        ==
        preset_settings["outline_width"]

    )


    if same_as_preset:

        final_preset = requested_preset

    else:

        final_preset = "カスタム"


    # ======================================================
    # 結果
    # ======================================================

    result = {

        "preset_name":
            final_preset,

        "font":
            final_font,

        "text_color":
            final_text_color,

        "text_color_hex":
            get_color_hex(
                final_text_color
            ),

        "outline_color":
            final_outline_color,

        "outline_color_hex":
            get_color_hex(
                final_outline_color
            ),

        "outline_width":
            final_outline_width,

    }


    print(
        "[SUBTITLE_FONT] normalized:",
        result,
        flush=True
    )


    print(
        "[SUBTITLE_FONT] select_subtitle_font() COMPLETE",
        flush=True
    )


    return result


# ==========================================================
# デフォルト設定
# ==========================================================

def get_default_subtitle_font_settings():

    return select_subtitle_font(

        preset=DEFAULT_SUBTITLE_PRESET

    )


# ==========================================================
# 起動ログ
# ==========================================================

print(
    "[SUBTITLE_FONT] subtitle_font.py loaded",
    flush=True
)

print(
    "[SUBTITLE_FONT] default preset:",
    DEFAULT_SUBTITLE_PRESET,
    flush=True
)

print(
    "[SUBTITLE_FONT] default outline width:",
    DEFAULT_OUTLINE_WIDTH,
    flush=True
)

print(
    "[SUBTITLE_FONT] colors:",
    list(
        SUBTITLE_COLORS.keys()
    ),
    flush=True
)
