# =====================================
# Subtitle Font Settings
# subtitle_font.py
#
# 字幕フォント・文字色・縁色・縁太さ管理
#
# subtitle.py と連動して使用
#
# 戻り値:
#
# {
#     "preset": "標準",
#     "font": "Noto Sans CJK JP",
#     "text_color": "白",
#     "outline_color": "黒",
#     "outline_width": 2
# }
#
# subtitle.py側では、この設定を受け取り
# FFmpeg subtitles filter の force_style
# に変換する。
#
# UI側では、
#
# get_subtitle_font_ui_config()
#
# を使用することで、
#
# ・プリセット
# ・フォント
# ・文字色
# ・縁取り色
# ・縁取り太さ
# ・カラーコード
#
# を取得できる。
# =====================================


# =====================================
# 字幕カラー設定
#
# UI表示用:
#
# hex
#   HTML/CSSで使用するカラーコード
#
# ass
#   ASS字幕で使用するカラーコード
#
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

    # ---------------------------------
    # 追加色
    # ---------------------------------

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
#
# 現在は5色を基本表示する。
#
# 必要になったらここへ色名を追加する。
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
#
# ここを変更することで、
# プリセットの内容を自由に変更できる。
#
# font:
#   FFmpeg / ASS の FontName
#
# text_color:
#   文字色
#
# outline_color:
#   縁取り色
#
# outline_width:
#   縁取りの太さ
#
# =====================================

SUBTITLE_FONT_PRESETS = {

    "標準": {

        "font":
            "Noto Sans CJK JP",

        "text_color":
            "白",

        "outline_color":
            "黒",

        "outline_width":
            2,

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
# デフォルト設定
# =====================================

DEFAULT_SUBTITLE_PRESET = "標準"


# =====================================
# 縁取り太さ
#
# UI側で使用する最小・最大値
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
# フォント名の正規化
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
# 色の正規化
# =====================================

def normalize_color_name(
    color,
    default
):

    if color in SUBTITLE_COLORS:

        return color

    return default


# =====================================
# カラーコード取得
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
# ASSカラー取得
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
# 字幕カラー情報取得
#
# UI側で使用。
#
# 例:
#
# {
#     "name": "白",
#     "hex": "#FFFFFF",
#     "ass": "&H00FFFFFF"
# }
#
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
# 字幕設定を作成
# =====================================

def create_subtitle_font_settings(
    font=None,
    text_color="白",
    outline_color="黒",
    outline_width=2,
    preset=None
):

    # ---------------------------------
    # フォント
    # ---------------------------------

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

    text_color = normalize_color_name(

        text_color,

        "白"

    )

    # ---------------------------------
    # 縁色
    # ---------------------------------

    outline_color = normalize_color_name(

        outline_color,

        "黒"

    )

    # ---------------------------------
    # 縁太さ
    # ---------------------------------

    outline_width = normalize_outline_width(

        outline_width

    )

    # ---------------------------------
    # プリセット
    # ---------------------------------

    if preset is None:

        preset = DEFAULT_SUBTITLE_PRESET

    preset = str(
        preset
    ).strip()

    if not preset:

        preset = DEFAULT_SUBTITLE_PRESET

    # ---------------------------------
    # 共通設定
    # ---------------------------------

    return {

        "preset":
            preset,

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
# デフォルト字幕設定
#
# subtitle.pyから使用
# =====================================

def get_default_subtitle_font_settings():

    preset = (
        SUBTITLE_FONT_PRESETS[
            DEFAULT_SUBTITLE_PRESET
        ]
    )

    return create_subtitle_font_settings(

        font=preset.get(
            "font"
        ),

        text_color=preset.get(
            "text_color",
            "白"
        ),

        outline_color=preset.get(
            "outline_color",
            "黒"
        ),

        outline_width=preset.get(
            "outline_width",
            2
        ),

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

    preset = (
        SUBTITLE_FONT_PRESETS[
            preset_name
        ]
    )

    return create_subtitle_font_settings(

        font=preset.get(
            "font"
        ),

        text_color=preset.get(
            "text_color",
            "白"
        ),

        outline_color=preset.get(
            "outline_color",
            "黒"
        ),

        outline_width=preset.get(
            "outline_width",
            2
        ),

        preset=preset_name

    )


# =====================================
# 利用可能なプリセット一覧
# =====================================

def get_subtitle_font_presets():

    return list(
        SUBTITLE_FONT_PRESETS.keys()
    )


# =====================================
# 利用可能なフォント一覧
#
# UI側で選択肢として使用可能
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
# 利用可能な文字色
#
# UIでは基本5色を使用
# =====================================

def get_available_text_colors():

    return list(
        SUBTITLE_BASIC_COLORS
    )


# =====================================
# 利用可能な縁色
#
# UIでは基本5色を使用
# =====================================

def get_available_outline_colors():

    return list(
        SUBTITLE_BASIC_COLORS
    )


# =====================================
# 全カラー一覧
#
# 必要になった場合に使用
# =====================================

def get_all_subtitle_colors():

    return list(
        SUBTITLE_COLORS.keys()
    )


# =====================================
# UI用カラー一覧
#
# 例:
#
# [
#     {
#         "name": "白",
#         "hex": "#FFFFFF",
#         "ass": "&H00FFFFFF"
#     },
#     ...
# ]
#
# =====================================

def get_subtitle_ui_colors():

    result = []

    for color in SUBTITLE_BASIC_COLORS:

        info = get_subtitle_color_info(
            color
        )

        result.append(
            info
        )

    return result


# =====================================
# 字幕設定を更新
#
# 既存設定を維持しながら
# 指定された項目だけ変更する。
# =====================================

def update_subtitle_font_settings(
    settings=None,
    font=None,
    text_color=None,
    outline_color=None,
    outline_width=None,
    preset=None
):

    # ---------------------------------
    # 元設定
    # ---------------------------------

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
    # フォント
    # ---------------------------------

    if font is not None:

        normalized_font = normalize_font_name(
            font
        )

        if normalized_font:

            settings["font"] = normalized_font

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
    # 縁太さ
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
    # プリセット
    # ---------------------------------

    if preset is not None:

        preset = str(
            preset
        ).strip()

        if preset:

            settings["preset"] = preset

    # ---------------------------------
    # 必須キーを保証
    # ---------------------------------

    if not settings.get(
        "font"
    ):

        settings["font"] = (
            get_default_subtitle_font_settings()[
                "font"
            ]
        )

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

    if not settings.get(
        "preset"
    ):

        settings["preset"] = (
            DEFAULT_SUBTITLE_PRESET
        )

    return settings


# =====================================
# フォント選択
#
# UI / route側から使用
# =====================================

def select_subtitle_font(
    font=None,
    text_color="白",
    outline_color="黒",
    outline_width=2,
    preset=None,
    settings=None
):

    # ---------------------------------
    # プリセットが指定された場合
    # ---------------------------------

    if preset:

        preset_settings = (
            get_subtitle_font_preset(
                preset
            )
        )

    else:

        preset_settings = (
            get_default_subtitle_font_settings()
        )

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
            preset_settings
        )

    # ---------------------------------
    # フォント
    # ---------------------------------

    if font is not None:

        normalized_font = normalize_font_name(
            font
        )

        if normalized_font:

            current_settings["font"] = (
                normalized_font
            )

    # ---------------------------------
    # 文字色
    # ---------------------------------

    if text_color is not None:

        current_settings["text_color"] = (
            normalize_color_name(

                text_color,

                "白"

            )
        )

    # ---------------------------------
    # 縁色
    # ---------------------------------

    if outline_color is not None:

        current_settings["outline_color"] = (
            normalize_color_name(

                outline_color,

                "黒"

            )
        )

    # ---------------------------------
    # 縁太さ
    # ---------------------------------

    if outline_width is not None:

        current_settings["outline_width"] = (
            normalize_outline_width(

                outline_width

            )
        )

    # ---------------------------------
    # プリセット
    # ---------------------------------

    if preset is not None:

        current_settings["preset"] = (
            str(preset)
        )

    # ---------------------------------
    # 最終正規化
    # ---------------------------------

    return update_subtitle_font_settings(

        settings=current_settings,

        font=current_settings.get(
            "font"
        ),

        text_color=current_settings.get(
            "text_color",
            "白"
        ),

        outline_color=current_settings.get(
            "outline_color",
            "黒"
        ),

        outline_width=current_settings.get(
            "outline_width",
            2
        ),

        preset=current_settings.get(
            "preset"
        )

    )


# =====================================
# 現在設定の表示用データ
#
# UI側で、
#
# 現在の設定
# プリセット 標準
# フォント Noto Sans CJK JP
# 文字色 白
# 縁色 黒
# 縁の太さ 2
#
# のように表示するために使用。
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
#
# subtitle.js / route側から使用可能。
#
# ダイアログに必要な情報をまとめて返す。
# =====================================

def get_subtitle_font_ui_config():

    default_settings = (
        get_default_subtitle_font_settings()
    )

    return {

        # ---------------------------------
        # 現在のデフォルト設定
        # ---------------------------------

        "default":
            get_subtitle_font_display_settings(
                default_settings
            ),

        # ---------------------------------
        # プリセット
        # ---------------------------------

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

        # ---------------------------------
        # フォント
        # ---------------------------------

        "fonts":
            get_available_subtitle_fonts(),

        # ---------------------------------
        # 文字色
        # ---------------------------------

        "text_colors":
            get_subtitle_ui_colors(),

        # ---------------------------------
        # 縁色
        # ---------------------------------

        "outline_colors":
            get_subtitle_ui_colors(),

        # ---------------------------------
        # 太さ
        # ---------------------------------

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
        "=====================================")


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
        "=====================================")


# =====================================
# テスト
#
# python subtitle_font.py
# =====================================

def main():

    # ---------------------------------
    # デフォルト設定
    # ---------------------------------

    settings = (
        get_default_subtitle_font_settings()
    )

    describe_subtitle_font_settings(
        settings
    )

    print()

    # ---------------------------------
    # プリセット
    # ---------------------------------

    print(
        "利用可能なプリセット:"
    )

    for preset in get_subtitle_font_presets():

        print(
            f" - {preset}"
        )

    print()

    # ---------------------------------
    # フォント
    # ---------------------------------

    print(
        "利用可能なフォント:"
    )

    for font in get_available_subtitle_fonts():

        print(
            f" - {font}"
        )

    print()

    # ---------------------------------
    # 基本カラー
    # ---------------------------------

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

    # ---------------------------------
    # 選択テスト
    # ---------------------------------

    test_settings = select_subtitle_font(

        font="Noto Sans CJK JP",

        text_color="黄",

        outline_color="黒",

        outline_width=3,

        preset="カスタム"

    )

    print(
        "選択テスト:"
    )

    print(
        test_settings
    )

    print()

    # ---------------------------------
    # UI設定
    # ---------------------------------

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
