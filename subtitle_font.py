# =====================================
# YouTube Converter - Subtitle Font
# subtitle_font.py
#
# 字幕フォント設定
#
# JavaScript の subtitle_font.js と
# データ形式を共有する。
#
# 重要:
#   subtitle_routes.py が使用する
#   select_subtitle_font() を提供する。
#
#   subtitle.py が使用する
#   SUBTITLE_COLORS は
#   {
#       "白": {
#           "hex": "#FFFFFF",
#           "ass": "&H00FFFFFF"
#       }
#   }
#   の形式にする。
# =====================================

from __future__ import annotations

from copy import deepcopy
from typing import Any


# =====================================
# カラー定義
#
# JS側と同じ日本語色名を使用する。
#
# hex:
#   Web / API用
#
# ass:
#   FFmpeg / ASS用
#
# ASSカラー:
#   &HAABBGGRR
#
# AA = Alpha
# BB = Blue
# GG = Green
# RR = Red
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

}


# =====================================
# デフォルト
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

    color_info = SUBTITLE_COLORS.get(
        color_name
    )

    if not isinstance(
        color_info,
        dict,
    ):
        return "#FFFFFF"

    return color_info.get(
        "hex",
        "#FFFFFF",
    )


# =====================================
# 色名 → ASS
# =====================================

def get_color_ass(
    color_name: str,
) -> str:

    color_info = SUBTITLE_COLORS.get(
        color_name
    )

    if not isinstance(
        color_info,
        dict,
    ):
        return "&H00FFFFFF"

    return color_info.get(
        "ass",
        "&H00FFFFFF",
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
# プリセット名を正規化
# =====================================

def normalize_preset_name(
    preset_name: Any,
) -> str:

    if not isinstance(
        preset_name,
        str,
    ):

        return DEFAULT_SUBTITLE_PRESET

    preset_name = preset_name.strip()

    if preset_name == "カスタム":

        return "カスタム"

    if preset_name in SUBTITLE_FONT_PRESETS:

        return preset_name

    return DEFAULT_SUBTITLE_PRESET


# =====================================
# 設定を正規化
#
# JS → Python
#
# 外部データ形式:
#
# {
#   preset_name,
#   font,
#   text_color,
#   text_color_hex,
#   outline_color,
#   outline_color_hex,
#   outline_width
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

    # ---------------------------------
    # preset_name
    # ---------------------------------

    preset_name = normalize_preset_name(
        settings.get(
            "preset_name",
            settings.get(
                "preset",
                DEFAULT_SUBTITLE_PRESET,
            ),
        )
    )

    # ---------------------------------
    # プリセット
    # ---------------------------------

    preset = SUBTITLE_FONT_PRESETS.get(
        preset_name
    )

    if (
        preset is not None
        and preset_name != "カスタム"
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

        outline_width = (
            normalize_outline_width(
                preset.get(
                    "outline_width",
                    DEFAULT_OUTLINE_WIDTH,
                )
            )
        )

    else:

        # ---------------------------------
        # カスタム
        # ---------------------------------

        preset_name = "カスタム"

        font = normalize_font(
            settings.get(
                "font"
            )
        )

        # JSからcamelCaseで来る場合にも対応
        text_color = normalize_color(
            settings.get(
                "text_color",
                settings.get(
                    "textColor",
                    "白",
                ),
            )
        )

        outline_color = normalize_color(
            settings.get(
                "outline_color",
                settings.get(
                    "outlineColor",
                    "黒",
                ),
            )
        )

        outline_width = (
            normalize_outline_width(
                settings.get(
                    "outline_width",
                    settings.get(
                        "outlineWidth",
                        DEFAULT_OUTLINE_WIDTH,
                    ),
                )
            )
        )

    # ---------------------------------
    # HEX再生成
    # ---------------------------------

    text_color_hex = get_color_hex(
        text_color
    )

    outline_color_hex = get_color_hex(
        outline_color
    )

    # ---------------------------------
    # 正式形式
    # ---------------------------------

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
# 重要:
# select_subtitle_font
#
# subtitle_routes.py が import している
# 関数。
#
# これが以前のファイルに存在しなかった
# ためGunicorn起動時に
#
# ImportError:
# cannot import name
# 'select_subtitle_font'
#
# が発生していた。
# =====================================

def select_subtitle_font(
    preset_name: Any = None,
    font: Any = None,
    text_color: Any = None,
    outline_color: Any = None,
    outline_width: Any = None,
    settings: Any = None,
) -> dict[str, Any]:

    print(
        "[SUBTITLE_FONT] "
        "select_subtitle_font() START",
        flush=True,
    )

    # ---------------------------------
    # settingsが直接渡された場合
    # ---------------------------------

    if isinstance(
        settings,
        dict,
    ):

        source = deepcopy(
            settings
        )

    else:

        source = {}

    # ---------------------------------
    # 明示的な引数を優先
    # ---------------------------------

    if preset_name is not None:

        source["preset_name"] = (
            preset_name
        )

    if font is not None:

        source["font"] = font

    if text_color is not None:

        source["text_color"] = (
            text_color
        )

    if outline_color is not None:

        source["outline_color"] = (
            outline_color
        )

    if outline_width is not None:

        source["outline_width"] = (
            outline_width
        )

    # ---------------------------------
    # 設定なし
    # ---------------------------------

    if not source:

        source = (
            get_default_subtitle_font_settings()
        )

    # ---------------------------------
    # 正規化
    # ---------------------------------

    normalized = (
        normalize_subtitle_font_settings(
            source
        )
    )

    print(
        "[SUBTITLE_FONT] normalized:",
        normalized,
        flush=True,
    )

    print(
        "[SUBTITLE_FONT] "
        "select_subtitle_font() COMPLETE",
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

    preset = SUBTITLE_FONT_PRESETS.get(
        preset_name
    )

    if preset is None:

        raise ValueError(
            "存在しない字幕フォントプリセットです: "
            + preset_name
        )

    return normalize_subtitle_font_settings(
        {
            "preset_name":
                preset_name,

            "font":
                preset.get(
                    "font"
                ),

            "text_color":
                preset.get(
                    "text_color"
                ),

            "outline_color":
                preset.get(
                    "outline_color"
                ),

            "outline_width":
                preset.get(
                    "outline_width"
                ),
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
            get_color_ass(
                normalized[
                    "text_color"
                ]
            ),

        "outline_color":
            get_color_ass(
                normalized[
                    "outline_color"
                ]
            ),

        "outline_width":
            normalized[
                "outline_width"
            ],

    }


# =====================================
# JavaScript互換用
#
# camelCase形式も取得できるようにする。
# =====================================

def get_subtitle_font_settings_for_js(
    settings: Any = None,
) -> dict[str, Any]:

    normalized = (
        normalize_subtitle_font_settings(
            settings
        )
    )

    return {

        "preset":
            normalized["preset_name"],

        "preset_name":
            normalized["preset_name"],

        "font":
            normalized["font"],

        "textColor":
            normalized["text_color"],

        "textColorHex":
            normalized["text_color_hex"],

        "outlineColor":
            normalized["outline_color"],

        "outlineColorHex":
            normalized["outline_color_hex"],

        "outlineWidth":
            normalized["outline_width"],

        "text_color":
            normalized["text_color"],

        "text_color_hex":
            normalized["text_color_hex"],

        "outline_color":
            normalized["outline_color"],

        "outline_color_hex":
            normalized["outline_color_hex"],

        "outline_width":
            normalized["outline_width"],

    }


# =====================================
# デバッグ
# =====================================

if __name__ == "__main__":

    print(
        "====================================="
    )

    print(
        "Subtitle Font Module Test"
    )

    print(
        "====================================="
    )

    print(
        "Default:"
    )

    print(
        get_default_subtitle_font_settings()
    )

    print()

    print(
        "Presets:"
    )

    print(
        get_subtitle_font_presets()
    )

    print()

    print(
        "Colors:"
    )

    print(
        get_subtitle_colors()
    )

    print()

    print(
        "Fonts:"
    )

    print(
        get_subtitle_fonts()
    )

    print()

    print(
        "select_subtitle_font:"
    )

    print(
        select_subtitle_font(
            preset_name="標準"
        )
    )

    print()

    print(
        "ASS settings:"
    )

    print(
        get_ass_font_settings(
            {
                "preset_name": "標準"
            }
        )
    )

    print()

    print(
        "====================================="
    )
