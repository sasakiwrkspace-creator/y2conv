# =====================================
# Subtitle Font Settings
# subtitle_font.py
#
# 字幕フォント・文字色・縁色・縁太さ管理
#
# subtitle.py と連動して使用
#
# =====================================


# =====================================
# 字幕カラー設定
# =====================================

SUBTITLE_COLORS = {

    "白": {
        "hex": "#FFFFFF",
        "ass": "&H00FFFFFF",
    },

    "黒": {
        "hex": "#000000",
        "ass": "&H00000000",
    },

    "赤": {
        "hex": "#FF0000",
        "ass": "&H000000FF",
    },

    "青": {
        "hex": "#0000FF",
        "ass": "&H00FF0000",
    },

    "黄": {
        "hex": "#FFFF00",
        "ass": "&H0000FFFF",
    },

    "緑": {
        "hex": "#00FF00",
        "ass": "&H0000FF00",
    },

    "オレンジ": {
        "hex": "#FFA500",
        "ass": "&H0000A5FF",
    },

    "水色": {
        "hex": "#00FFFF",
        "ass": "&H00FFFF00",
    },

    "紫": {
        "hex": "#800080",
        "ass": "&H00800080",
    },

}


# =====================================
# UI基本カラー
# =====================================

SUBTITLE_BASIC_COLORS = [

    "白",
    "黒",
    "赤",
    "青",
    "黄",

]


# =====================================
# フォントプリセット
# =====================================

SUBTITLE_FONT_PRESETS = {

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

    "ゴシック": {

        "font":
            "Noto Sans CJK JP",

        "text_color":
            "白",

        "outline_color":
            "黒",

        "outline_width":
            2,

    },

    "明朝": {

        "font":
            "Noto Serif CJK JP",

        "text_color":
            "白",

        "outline_color":
            "黒",

        "outline_width":
            2,

    },

    "太字ゴシック": {

        "font":
            "Noto Sans CJK JP",

        "text_color":
            "白",

        "outline_color":
            "黒",

        "outline_width":
            3,

    },

}


# =====================================
# デフォルト
# =====================================

DEFAULT_SUBTITLE_PRESET = "標準"


# =====================================
# 縁取り太さ
# =====================================

MIN_OUTLINE_WIDTH = 0

MAX_OUTLINE_WIDTH = 10


# =====================================
# 設定値の正規化
# =====================================

def normalize_outline_width(
    value,
    default=2
):

    try:

        value = int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        value = default

    value = max(

        MIN_OUTLINE_WIDTH,

        min(
            value,
            MAX_OUTLINE_WIDTH
        )

    )

    return value


# =====================================
# フォント名
# =====================================

def normalize_font_name(
    font
):

    if font is None:

        return None

    font = str(
        font
    ).strip()

    if not font:

        return None

    return font


# =====================================
# 色
# =====================================

def normalize_color_name(
    color,
    default
):

    if color in SUBTITLE_COLORS:

        return color

    return default


# =====================================
# HEXカラー
# =====================================

def get_subtitle_color_hex(
    color,
    default="白"
):

    color = normalize_color_name(
        color,
        default
    )

    return (
        SUBTITLE_COLORS[
            color
        ]["hex"]
    )


# =====================================
# ASSカラー
# =====================================

def get_subtitle_color_ass(
    color,
    default="白"
):

    color = normalize_color_name(
        color,
        default
    )

    return (
        SUBTITLE_COLORS[
            color
        ]["ass"]
    )


# =====================================
# カラー情報
# =====================================

def get_subtitle_color_info(
    color
):

    color = normalize_color_name(
        color,
        "白"
    )

    data = (
        SUBTITLE_COLORS[
            color
        ]
    )

    return {

        "name":
            color,

        "hex":
            data["hex"],

        "ass":
            data["ass"],

    }


# =====================================
# 字幕設定作成
# =====================================

def create_subtitle_font_settings(
    font=None,
    text_color=None,
    outline_color=None,
    outline_width=None,
    preset=None
):

    # ---------------------------------
    # プリセット
    # ---------------------------------

    if preset is None:

        preset_name = (
            DEFAULT_SUBTITLE_PRESET
        )

    else:

        preset_name = str(
            preset
        ).strip()

        if not preset_name:

            preset_name = (
                DEFAULT_SUBTITLE_PRESET
            )

    if preset_name in SUBTITLE_FONT_PRESETS:

        preset_settings = (
            SUBTITLE_FONT_PRESETS[
                preset_name
            ]
        )

    else:

        preset_name = (
            DEFAULT_SUBTITLE_PRESET
        )

        preset_settings = (
            SUBTITLE_FONT_PRESETS[
                DEFAULT_SUBTITLE_PRESET
            ]
        )

    # ---------------------------------
    # フォント
    # ---------------------------------

    if font is None:

        font = preset_settings.get(
            "font"
        )

    font = normalize_font_name(
        font
    )

    if not font:

        font = (
            SUBTITLE_FONT_PRESETS[
                DEFAULT_SUBTITLE_PRESET
            ]["font"]
        )

    # ---------------------------------
    # 文字色
    # ---------------------------------

    if text_color is None:

        text_color = preset_settings.get(
            "text_color",
            "白"
        )

    text_color = normalize_color_name(

        text_color,

        "白"

    )

    # ---------------------------------
    # 縁色
    # ---------------------------------

    if outline_color is None:

        outline_color = preset_settings.get(
            "outline_color",
            "黒"
        )

    outline_color = normalize_color_name(

        outline_color,

        "黒"

    )

    # ---------------------------------
    # 縁太さ
    # ---------------------------------

    if outline_width is None:

        outline_width = preset_settings.get(
            "outline_width",
            2
        )

    outline_width = normalize_outline_width(
        outline_width
    )

    # ---------------------------------
    # 完成
    # ---------------------------------

    return {

        "preset":
            preset_name,

        "font":
            font,

        "text_color":
            text_color,

        "outline_color":
            outline_color,

        "outline_width":
            outline_width,

    }


# =====================================
# デフォルト設定
# =====================================

def get_default_subtitle_font_settings():

    return create_subtitle_font_settings(
        preset=DEFAULT_SUBTITLE_PRESET
    )


# =====================================
# プリセット取得
# =====================================

def get_subtitle_font_preset(
    preset_name
):

    if preset_name not in SUBTITLE_FONT_PRESETS:

        return get_default_subtitle_font_settings()

    return create_subtitle_font_settings(

        preset=preset_name

    )


# =====================================
# プリセット一覧
# =====================================

def get_subtitle_font_presets():

    return list(
        SUBTITLE_FONT_PRESETS.keys()
    )


# =====================================
# 利用可能フォント
# =====================================

def get_available_subtitle_fonts():

    return [

        "Noto Sans CJK JP",

        "Noto Sans JP",

        "Noto Serif CJK JP",

        "Noto Serif JP",

        "IPAexGothic",

        "IPAGothic",

        "IPAexMincho",

        "IPAMincho",

        "VL Gothic",

        "TakaoGothic",

    ]


# =====================================
# 文字色
# =====================================

def get_available_text_colors():

    return list(
        SUBTITLE_BASIC_COLORS
    )


# =====================================
# 縁色
# =====================================

def get_available_outline_colors():

    return list(
        SUBTITLE_BASIC_COLORS
    )


# =====================================
# 全色
# =====================================

def get_all_subtitle_colors():

    return list(
        SUBTITLE_COLORS.keys()
    )


# =====================================
# UIカラー
# =====================================

def get_subtitle_ui_colors():

    result = []

    for color in SUBTITLE_BASIC_COLORS:

        result.append(
            get_subtitle_color_info(
                color
            )
        )

    return result


# =====================================
# 設定更新
# =====================================

def update_subtitle_font_settings(
    settings=None,
    font=None,
    text_color=None,
    outline_color=None,
    outline_width=None,
    preset=None
):

    if not isinstance(
        settings,
        dict
    ):

        settings = (
            get_default_subtitle_font_settings()
        )

    else:

        settings = dict(
            settings
        )

    # ---------------------------------
    # プリセット
    # ---------------------------------

    if preset is not None:

        preset_name = str(
            preset
        ).strip()

        if preset_name in SUBTITLE_FONT_PRESETS:

            settings["preset"] = (
                preset_name
            )

            preset_settings = (
                SUBTITLE_FONT_PRESETS[
                    preset_name
                ]
            )

            # 明示的な値が指定されなければ
            # プリセット値を使用
            if font is None:

                font = preset_settings.get(
                    "font"
                )

            if text_color is None:

                text_color = preset_settings.get(
                    "text_color"
                )

            if outline_color is None:

                outline_color = preset_settings.get(
                    "outline_color"
                )

            if outline_width is None:

                outline_width = preset_settings.get(
                    "outline_width"
                )

    # ---------------------------------
    # フォント
    # ---------------------------------

    if font is not None:

        normalized_font = (
            normalize_font_name(
                font
            )
        )

        if normalized_font:

            settings["font"] = (
                normalized_font
            )

    # ---------------------------------
    # 文字色
    # ---------------------------------

    if text_color is not None:

        settings["text_color"] = (
            normalize_color_name(

                text_color,

                settings.get(
                    "text_color",
                    "白"
                )

            )
        )

    # ---------------------------------
    # 縁色
    # ---------------------------------

    if outline_color is not None:

        settings["outline_color"] = (
            normalize_color_name(

                outline_color,

                settings.get(
                    "outline_color",
                    "黒"
                )

            )
        )

    # ---------------------------------
    # 太さ
    # ---------------------------------

    if outline_width is not None:

        settings["outline_width"] = (
            normalize_outline_width(

                outline_width,

                settings.get(
                    "outline_width",
                    2
                )

            )
        )

    # ---------------------------------
    # 必須値
    # ---------------------------------

    default = (
        get_default_subtitle_font_settings()
    )

    if not settings.get("font"):

        settings["font"] = default["font"]

    settings["text_color"] = (
        normalize_color_name(

            settings.get(
                "text_color"
            ),

            "白"

        )
    )

    settings["outline_color"] = (
        normalize_color_name(

            settings.get(
                "outline_color"
            ),

            "黒"

        )
    )

    settings["outline_width"] = (
        normalize_outline_width(

            settings.get(
                "outline_width"
            ),

            2

        )
    )

    if not settings.get("preset"):

        settings["preset"] = (
            DEFAULT_SUBTITLE_PRESET
        )

    return settings


# =====================================
# 字幕フォント選択
# =====================================

def select_subtitle_font(
    font=None,
    text_color=None,
    outline_color=None,
    outline_width=None,
    preset=None,
    settings=None
):

    # ---------------------------------
    # 既存設定
    # ---------------------------------

    if isinstance(
        settings,
        dict
    ):

        current_settings = dict(
            settings
        )

    else:

        current_settings = (
            get_default_subtitle_font_settings()
        )

    # ---------------------------------
    # プリセット
    #
    # プリセットを選択した場合、
    # まずプリセット値を適用。
    # その後、明示された個別設定で上書き。
    # ---------------------------------

    if preset is not None:

        preset_name = str(
            preset
        ).strip()

        if preset_name in SUBTITLE_FONT_PRESETS:

            preset_settings = (
                get_subtitle_font_preset(
                    preset_name
                )
            )

            current_settings.update(
                preset_settings
            )

    # ---------------------------------
    # 個別設定
    # ---------------------------------

    if font is not None:

        normalized_font = (
            normalize_font_name(
                font
            )
        )

        if normalized_font:

            current_settings["font"] = (
                normalized_font
            )

    if text_color is not None:

        current_settings["text_color"] = (
            normalize_color_name(

                text_color,

                current_settings.get(
                    "text_color",
                    "白"
                )

            )
        )

    if outline_color is not None:

        current_settings["outline_color"] = (
            normalize_color_name(

                outline_color,

                current_settings.get(
                    "outline_color",
                    "黒"
                )

            )
        )

    if outline_width is not None:

        current_settings["outline_width"] = (
            normalize_outline_width(

                outline_width,

                current_settings.get(
                    "outline_width",
                    2
                )

            )
        )

    if preset is not None:

        preset_name = str(
            preset
        ).strip()

        if preset_name:

            current_settings["preset"] = (
                preset_name
            )

    return update_subtitle_font_settings(

        settings=current_settings,

        font=current_settings.get(
            "font"
        ),

        text_color=current_settings.get(
            "text_color"
        ),

        outline_color=current_settings.get(
            "outline_color"
        ),

        outline_width=current_settings.get(
            "outline_width"
        ),

        preset=current_settings.get(
            "preset"
        )

    )


# =====================================
# 表示用設定
# =====================================

def get_subtitle_font_display_settings(
    settings=None
):

    if not isinstance(
        settings,
        dict
    ):

        settings = (
            get_default_subtitle_font_settings()
        )

    settings = update_subtitle_font_settings(
        settings=settings
    )

    return {

        "preset":
            settings["preset"],

        "font":
            settings["font"],

        "text_color":
            settings["text_color"],

        "text_color_hex":
            get_subtitle_color_hex(
                settings["text_color"]
            ),

        "outline_color":
            settings["outline_color"],

        "outline_color_hex":
            get_subtitle_color_hex(
                settings["outline_color"]
            ),

        "outline_width":
            settings["outline_width"],

    }


# =====================================
# UI用設定一式
# =====================================

def get_subtitle_font_ui_config():

    default_settings = (
        get_default_subtitle_font_settings()
    )

    return {

        "default":
            get_subtitle_font_display_settings(
                default_settings
            ),

        "presets": {

            preset_name:
                get_subtitle_font_display_settings(
                    get_subtitle_font_preset(
                        preset_name
                    )
                )

            for preset_name
            in get_subtitle_font_presets()

        },

        "fonts":
            get_available_subtitle_fonts(),

        "text_colors":
            get_subtitle_ui_colors(),

        "outline_colors":
            get_subtitle_ui_colors(),

        "outline_width": {

            "min":
                MIN_OUTLINE_WIDTH,

            "max":
                MAX_OUTLINE_WIDTH,

            "default":
                default_settings[
                    "outline_width"
                ],

        },

    }


# =====================================
# 設定表示
# =====================================

def describe_subtitle_font_settings(
    settings
):

    if not isinstance(
        settings,
        dict
    ):

        settings = (
            get_default_subtitle_font_settings()
        )

    print(
        "====================================="
    )

    print(
        "字幕設定"
    )

    print(
        "====================================="
    )

    print(
        f"プリセット: "
        f"{settings.get('preset')}"
    )

    print(
        f"フォント: "
        f"{settings.get('font')}"
    )

    print(
        f"文字色: "
        f"{settings.get('text_color')}"
    )

    print(
        f"縁色: "
        f"{settings.get('outline_color')}"
    )

    print(
        f"縁太さ: "
        f"{settings.get('outline_width')}"
    )

    print(
        "====================================="
    )


# =====================================
# UI設定表示
# =====================================

def describe_subtitle_font_ui_config():

    config = (
        get_subtitle_font_ui_config()
    )

    print(
        "====================================="
    )

    print(
        "字幕フォント UI設定"
    )

    print(
        "====================================="
    )

    print(
        "デフォルト:"
    )

    print(
        config["default"]
    )

    print()

    print(
        "プリセット:"
    )

    for name, settings in (
        config["presets"].items()
    ):

        print(
            f" - {name}: "
            f"{settings}"
        )

    print()

    print(
        "フォント:"
    )

    for font in config["fonts"]:

        print(
            f" - {font}"
        )

    print()

    print(
        "カラー:"
    )

    for color in config["text_colors"]:

        print(
            f" - {color['name']}: "
            f"{color['hex']}"
        )

    print()

    print(
        "縁取り太さ:"
    )

    print(
        config["outline_width"]
    )

    print(
        "====================================="
    )


# =====================================
# テスト
# =====================================

def main():

    settings = (
        get_default_subtitle_font_settings()
    )

    describe_subtitle_font_settings(
        settings
    )

    print()

    print(
        "利用可能なプリセット:"
    )

    for preset in get_subtitle_font_presets():

        print(
            f" - {preset}"
        )

    print()

    print(
        "利用可能なフォント:"
    )

    for font in get_available_subtitle_fonts():

        print(
            f" - {font}"
        )

    print()

    print(
        "利用可能な基本色:"
    )

    for color in get_available_text_colors():

        info = get_subtitle_color_info(
            color
        )

        print(
            f" - {info['name']}: "
            f"{info['hex']} "
            f"{info['ass']}"
        )

    print()

    test_settings = select_subtitle_font(

        font="Noto Sans CJK JP",

        text_color="黄",

        outline_color="黒",

        outline_width=3,

        preset="標準"

    )

    print(
        "選択テスト:"
    )

    print(
        test_settings
    )

    print()

    print(
        "UI設定テスト:"
    )

    describe_subtitle_font_ui_config()

    print()

    return 0


# =====================================
# 実行
# =====================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )
