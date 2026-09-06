# =====================================
# YouTube Converter - Subtitle Font
# subtitle_font.py
#
# 字幕フォント設定
#
# JavaScript の subtitle_font.js と
# データ形式を共有する。
#
# subtitle_routes.py:
#
#   select_subtitle_font(...)
#
# subtitle.py:
#
#   normalize_subtitle_font_settings(...)
#   get_ass_font_settings(...)
#
# から利用する。
# =====================================

from __future__ import annotations

from copy import deepcopy
from typing import Any


# =====================================
# カラー定義
#
# JavaScript側と同じ色名を使用する。
#
# 値はHEX文字列。
#
# 例:
#
#   "白" → "#FFFFFF"
#   "青" → "#0000FF"
#
# ASSカラーへの変換は subtitle.py 側で行う。
# =====================================

SUBTITLE_COLORS = {

    "白":
        "#FFFFFF",

    "黒":
        "#000000",

    "赤":
        "#FF0000",

    "青":
        "#0000FF",

    "黄":
        "#FFFF00",

}


# =====================================
# デフォルト設定
# =====================================

DEFAULT_SUBTITLE_PRESET = "標準"


DEFAULT_SUBTITLE_SETTINGS = {

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
            "青",

        "outline_width":
            5,

    },


    "明朝": {

        "font":
            "Noto Serif CJK JP",

        "text_color":
            "白",

        "outline_color":
            "青",

        "outline_width":
            5,

    },


    "太字ゴシック": {

        "font":
            "Noto Sans CJK JP",

        "text_color":
            "白",

        "outline_color":
            "青",

        "outline_width":
            5,

    },


    "太字明朝": {

        "font":
            "Noto Serif CJK JP",

        "text_color":
            "白",

        "outline_color":
            "青",

        "outline_width":
            5,

    },

}


# =====================================
# カスタムプリセット
#
# JavaScript側から
# preset_name="カスタム"
# が送られる場合に使用する。
#
# 実際の値は入力された
# font / color / outline_width
# から生成する。
# =====================================

CUSTOM_SUBTITLE_PRESET = "カスタム"


# =====================================
# Python側で使用可能なフォント
# =====================================

SUBTITLE_FONTS = [

    "Noto Sans CJK JP",

    "Noto Sans JP",

    "Noto Serif CJK JP",

    "Noto Serif JP",

    "IPAGothic",

    "IPAMincho",

]


# =====================================
# 縁取り太さ
# =====================================

MIN_OUTLINE_WIDTH = 0

MAX_OUTLINE_WIDTH = 10

DEFAULT_OUTLINE_WIDTH = 5


# =====================================
# 色名 → HEX
# =====================================

def get_color_hex(
    color_name: str,
) -> str:

    return (
        SUBTITLE_COLORS.get(
            color_name,
            "#FFFFFF",
        )
    )


# =====================================
# 縁取り太さを正規化
# =====================================

def normalize_outline_width(
    value: Any,
) -> int:

    try:

        width = int(
            round(
                float(value)
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        width = DEFAULT_OUTLINE_WIDTH


    width = max(
        MIN_OUTLINE_WIDTH,
        min(
            MAX_OUTLINE_WIDTH,
            width,
        ),
    )


    return width


# =====================================
# フォント名を正規化
# =====================================

def normalize_font(
    font: Any,
) -> str:

    if not isinstance(
        font,
        str,
    ):

        return DEFAULT_SUBTITLE_SETTINGS[
            "font"
        ]


    font = font.strip()


    if font not in SUBTITLE_FONTS:

        return DEFAULT_SUBTITLE_SETTINGS[
            "font"
        ]


    return font


# =====================================
# 色名を正規化
# =====================================

def normalize_color(
    color: Any,
) -> str:

    if not isinstance(
        color,
        str,
    ):

        return "白"


    color = color.strip()


    if color not in SUBTITLE_COLORS:

        return "白"


    return color


# =====================================
# 設定を正規化
#
# JSから受け取ったデータを
# Python側の正式な形式に統一する。
#
# 正式な形式:
#
# {
#     "preset_name": "標準",
#     "font": "Noto Sans CJK JP",
#     "text_color": "白",
#     "text_color_hex": "#FFFFFF",
#     "outline_color": "青",
#     "outline_color_hex": "#0000FF",
#     "outline_width": 5
# }
# =====================================

def normalize_subtitle_font_settings(
    settings: Any = None,
) -> dict[str, Any]:

    if not isinstance(
        settings,
        dict,
    ):

        settings = {}


    # =================================
    # preset_name
    # =================================

    preset_name = settings.get(
        "preset_name",
        DEFAULT_SUBTITLE_PRESET,
    )


    if not isinstance(
        preset_name,
        str,
    ):

        preset_name = DEFAULT_SUBTITLE_PRESET


    preset_name = preset_name.strip()


    # =================================
    # プリセット取得
    # =================================

    preset = SUBTITLE_FONT_PRESETS.get(
        preset_name
    )


    # =================================
    # 通常プリセット
    # =================================

    if (
        preset is not None
        and preset_name != CUSTOM_SUBTITLE_PRESET
    ):

        font = normalize_font(
            preset.get(
                "font"
            )
        )

        text_color = normalize_color(
            preset.get(
                "text_color"
            )
        )

        outline_color = normalize_color(
            preset.get(
                "outline_color"
            )
        )

        outline_width = normalize_outline_width(
            preset.get(
                "outline_width",
                DEFAULT_OUTLINE_WIDTH,
            )
        )


    else:

        # =============================
        # カスタム設定
        # =============================

        preset_name = CUSTOM_SUBTITLE_PRESET

        font = normalize_font(
            settings.get(
                "font"
            )
        )

        text_color = normalize_color(
            settings.get(
                "text_color"
            )
        )

        outline_color = normalize_color(
            settings.get(
                "outline_color"
            )
        )

        outline_width = normalize_outline_width(
            settings.get(
                "outline_width",
                DEFAULT_OUTLINE_WIDTH,
            )
        )


    # =================================
    # HEXをPython側で再生成
    #
    # JSから渡されたHEXをそのまま
    # 信用しない。
    # =================================

    text_color_hex = get_color_hex(
        text_color
    )


    outline_color_hex = get_color_hex(
        outline_color
    )


    # =================================
    # 正式な外部データ形式
    #
    # このキー名は変更しない。
    # =================================

    return {

        "preset_name":
            preset_name,

        "font":
            font,

        "text_color":
            text_color,

        "text_color_hex":
            text_color_hex,

        "outline_color":
            outline_color,

        "outline_color_hex":
            outline_color_hex,

        "outline_width":
            outline_width,

    }


# =====================================
# 字幕フォント選択
#
# subtitle_routes.pyから使用する
# 正式関数。
#
# 例:
#
# select_subtitle_font(
#     preset_name="標準",
#     font="Noto Sans CJK JP",
#     text_color="白",
#     outline_color="青",
#     outline_width=5,
# )
#
# ↓
#
# 正規化された設定dictを返す。
# =====================================

def select_subtitle_font(
    preset_name: Any = None,
    font: Any = None,
    text_color: Any = None,
    outline_color: Any = None,
    outline_width: Any = None,
) -> dict[str, Any]:

    print(
        "[SUBTITLE_FONT] select_subtitle_font() START",
        flush=True,
    )


    # =================================
    # preset_nameを正規化
    # =================================

    if isinstance(
        preset_name,
        str,
    ):

        preset_name = preset_name.strip()

    else:

        preset_name = None


    # =================================
    # プリセット指定
    # =================================

    if (
        preset_name
        and preset_name in SUBTITLE_FONT_PRESETS
    ):

        settings = {

            "preset_name":
                preset_name,

        }


    else:

        # =================================
        # カスタム
        # =================================

        settings = {

            "preset_name":
                CUSTOM_SUBTITLE_PRESET,

        }


        if font is not None:

            settings["font"] = font


        if text_color is not None:

            settings["text_color"] = text_color


        if outline_color is not None:

            settings["outline_color"] = outline_color


        if outline_width is not None:

            settings["outline_width"] = outline_width


        # =================================
        # 何も指定されていない場合
        #
        # 標準プリセットを使用
        # =================================

        if not any(

            key in settings

            for key in (

                "font",

                "text_color",

                "outline_color",

                "outline_width",

            )

        ):

            settings = {

                "preset_name":
                    DEFAULT_SUBTITLE_PRESET,

            }


    # =================================
    # 正規化
    # =================================

    normalized = (
        normalize_subtitle_font_settings(
            settings
        )
    )


    # =================================
    # ログ
    # =================================

    print(
        "[SUBTITLE_FONT] normalized:",
        normalized,
        flush=True,
    )


    print(
        "[SUBTITLE_FONT] select_subtitle_font() COMPLETE",
        flush=True,
    )


    return normalized


# =====================================
# デフォルト設定取得
# =====================================

def get_default_subtitle_font_settings(
) -> dict[str, Any]:

    return deepcopy(
        DEFAULT_SUBTITLE_SETTINGS
    )


# =====================================
# プリセット取得
# =====================================

def get_subtitle_font_preset(
    preset_name: str,
) -> dict[str, Any]:

    if not isinstance(
        preset_name,
        str,
    ):

        raise ValueError(
            "プリセット名が不正です"
        )


    preset_name = preset_name.strip()


    preset = SUBTITLE_FONT_PRESETS.get(
        preset_name
    )


    if preset is None:

        raise ValueError(

            "存在しない字幕フォント"
            "プリセットです: "
            +
            preset_name

        )


    return normalize_subtitle_font_settings(

        {
            "preset_name":
                preset_name,

            "font":
                preset["font"],

            "text_color":
                preset["text_color"],

            "outline_color":
                preset["outline_color"],

            "outline_width":
                preset["outline_width"],

        }

    )


# =====================================
# プリセット一覧
# =====================================

def get_subtitle_font_presets(
) -> list[str]:

    return list(
        SUBTITLE_FONT_PRESETS.keys()
    )


# =====================================
# 色一覧
# =====================================

def get_subtitle_colors(
) -> list[str]:

    return list(
        SUBTITLE_COLORS.keys()
    )


# =====================================
# フォント一覧
# =====================================

def get_subtitle_fonts(
) -> list[str]:

    return list(
        SUBTITLE_FONTS
    )


# =====================================
# FFmpeg / ASS用設定取得
#
# subtitle.pyなどから利用する。
#
# 注意:
#
# subtitle.py側でHEX → ASSカラー変換を
# 行うため、ここではHEXを返す。
# =====================================

def get_ass_font_settings(
    settings: Any = None,
) -> dict[str, Any]:

    normalized = (
        normalize_subtitle_font_settings(
            settings
        )
    )


    return {

        "font":
            normalized["font"],

        "text_color":
            normalized["text_color_hex"],

        "outline_color":
            normalized["outline_color_hex"],

        "outline_width":
            normalized["outline_width"],

    }


# =====================================
# 設定取得用エイリアス
#
# 外部コードとの互換性用。
# =====================================

def get_subtitle_font_settings(
    settings: Any = None,
) -> dict[str, Any]:

    return normalize_subtitle_font_settings(
        settings
    )


# =====================================
# デバッグ用
# =====================================

if __name__ == "__main__":

    print(
        "====================================="
    )

    print(
        "Subtitle Font Debug"
    )

    print(
        "====================================="
    )


    print()


    print(
        "Default subtitle font settings:"
    )

    print(
        get_default_subtitle_font_settings()
    )


    print()


    print(
        "Subtitle font presets:"
    )

    print(
        get_subtitle_font_presets()
    )


    print()


    print(
        "Subtitle fonts:"
    )

    print(
        get_subtitle_fonts()
    )


    print()


    print(
        "Subtitle colors:"
    )

    print(
        get_subtitle_colors()
    )


    print()


    print(
        "Standard preset:"
    )

    print(
        select_subtitle_font(
            preset_name="標準"
        )
    )


    print()


    print(
        "Custom settings:"
    )

    print(
        select_subtitle_font(
            preset_name="カスタム",
            font="Noto Sans CJK JP",
            text_color="白",
            outline_color="青",
            outline_width=5,
        )
    )


    print()


    print(
        "ASS settings:"
    )

    print(
        get_ass_font_settings(
            {
                "preset_name":
                    "標準",
            }
        )
    )


    print()


    print(
        "====================================="
    )
