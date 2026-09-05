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
# =====================================


# =====================================
# 字幕カラー
#
# ASS形式:
#
# &HAABBGGRR
#
# AA = Alpha
# BB = Blue
# GG = Green
# RR = Red
#
# 完全不透明:
# 00
# =====================================

SUBTITLE_COLORS = {

    "白": {
        "ass": "&H00FFFFFF",
    },

    "黒": {
        "ass": "&H00000000",
    },

    "赤": {
        "ass": "&H000000FF",
    },

    "青": {
        "ass": "&H00FF0000",
    },

    "緑": {
        "ass": "&H0000FF00",
    },

    "黄": {
        "ass": "&H0000FFFF",
    },

    "オレンジ": {
        "ass": "&H0000A5FF",
    },

    "水色": {
        "ass": "&H00FFFF00",
    },

    "紫": {
        "ass": "&H00800080",
    },

}


# =====================================
# フォントプリセット
#
# font:
#   FFmpeg / ASS の FontName として使用
#
# name:
#   UI表示用
#
# =====================================

SUBTITLE_FONT_PRESETS = {

    "標準": {

        "font": "Noto Sans CJK JP",

        "text_color": "白",

        "outline_color": "黒",

        "outline_width": 2,

    },

    "ゴシック": {

        "font": "Noto Sans CJK JP",

        "text_color": "白",

        "outline_color": "黒",

        "outline_width": 2,

    },

    "明朝": {

        "font": "Noto Serif CJK JP",

        "text_color": "白",

        "outline_color": "黒",

        "outline_width": 2,

    },

    "太字ゴシック": {

        "font": "Noto Sans CJK JP",

        "text_color": "白",

        "outline_color": "黒",

        "outline_width": 3,

    },

}


# =====================================
# デフォルト設定
# =====================================

DEFAULT_SUBTITLE_PRESET = "標準"


# =====================================
# 設定値の正規化
# =====================================

def normalize_outline_width(
    value,
    default=2
):

    try:

        value = int(value)

    except (
        ValueError,
        TypeError
    ):

        value = default

    # 安全範囲
    value = max(
        0,
        min(
            value,
            10
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
    # subtitle.py と共通の辞書
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
#
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
# =====================================

def get_available_text_colors():

    return list(
        SUBTITLE_COLORS.keys()
    )


# =====================================
# 利用可能な縁色
# =====================================

def get_available_outline_colors():

    return list(
        SUBTITLE_COLORS.keys()
    )


# =====================================
# 字幕設定を更新
#
# 既存設定を維持しながら
# 指定された項目だけ変更する。
#
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
#
# 例:
#
# settings = select_subtitle_font(
#     font="Noto Sans JP",
#     text_color="黄色",
#     outline_color="黒",
#     outline_width=3
# )
#
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
    # 引数で指定された値を反映
    # ---------------------------------

    if font is not None:

        current_settings["font"] = (
            normalize_font_name(
                font
            )
        )

    if text_color is not None:

        current_settings["text_color"] = (
            normalize_color_name(

                text_color,

                "白"

            )
        )

    if outline_color is not None:

        current_settings["outline_color"] = (
            normalize_color_name(

                outline_color,

                "黒"

            )
        )

    if outline_width is not None:

        current_settings["outline_width"] = (
            normalize_outline_width(

                outline_width

            )
        )

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
# テスト
#
# python subtitle_font.py
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
        "利用可能な色:"
    )

    for color in get_available_text_colors():

        print(
            f" - {color}"
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

    return 0


# =====================================
# 実行
# =====================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )
