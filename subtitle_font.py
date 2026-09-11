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
# 仕様:
#   ・何も指定しない → 標準設定
#   ・全項目が正常 → 指定値を使用
#   ・1項目でも不正 → 設定全体を標準設定へ戻す
#
# 標準設定:
#   フォント     : Noto Sans CJK JP
#   文字色       : 白
#   縁色         : 青
#   縁太さ       : 3
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
            3,

    },

    "白文字青縁": {

        "font":
            "Noto Sans CJK JP",

        "text_color":
            "白",

        "outline_color":
            "青",

        "outline_width":
            3,

    },

}


# ==========================================================
# 標準設定
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
# デフォルト設定へ戻す
# ==========================================================

def _get_default_settings():

    return dict(
        DEFAULT_SUBTITLE_FONT_SETTINGS
    )


# ==========================================================
# 設定全体の妥当性確認
#
# ★重要
#
# 1項目でも不正ならFalseを返す。
#
# ==========================================================

def _is_valid_subtitle_settings(
    settings
):

    if not isinstance(
        settings,
        dict
    ):

        return False


    # ------------------------------------------------------
    # 必須キー確認
    # ------------------------------------------------------

    required_keys = (

        "preset_name",

        "font",

        "text_color",

        "outline_color",

        "outline_width",

    )

    for key in required_keys:

        if key not in settings:

            _log(
                f"invalid setting: missing key={key}"
            )

            return False


    # ------------------------------------------------------
    # preset_name
    # ------------------------------------------------------

    preset_name = settings.get(
        "preset_name"
    )

    if not isinstance(
        preset_name,
        str
    ):

        _log(
            "invalid preset_name: "
            f"{preset_name!r}"
        )

        return False

    preset_name = preset_name.strip()

    if not preset_name:

        _log(
            "invalid preset_name: empty"
        )

        return False


    if preset_name not in SUBTITLE_PRESETS:

        _log(
            "invalid preset_name: "
            f"{preset_name}"
        )

        return False


    # ------------------------------------------------------
    # font
    # ------------------------------------------------------

    font = settings.get(
        "font"
    )

    if not isinstance(
        font,
        str
    ):

        _log(
            f"invalid font: {font!r}"
        )

        return False

    if not font.strip():

        _log(
            "invalid font: empty"
        )

        return False


    # ------------------------------------------------------
    # text_color
    # ------------------------------------------------------

    text_color = settings.get(
        "text_color"
    )

    if text_color not in SUBTITLE_COLORS:

        _log(
            "invalid text_color: "
            f"{text_color!r}"
        )

        return False


    # ------------------------------------------------------
    # outline_color
    # ------------------------------------------------------

    outline_color = settings.get(
        "outline_color"
    )

    if outline_color not in SUBTITLE_COLORS:

        _log(
            "invalid outline_color: "
            f"{outline_color!r}"
        )

        return False


    # ------------------------------------------------------
    # outline_width
    #
    # 0～10 の整数のみ許可
    # ------------------------------------------------------

    outline_width = settings.get(
        "outline_width"
    )

    try:

        width = int(
            outline_width
        )

    except (
        ValueError,
        TypeError
    ):

        _log(
            "invalid outline_width: "
            f"{outline_width!r}"
        )

        return False


    if width < 0 or width > 10:

        _log(
            "invalid outline_width range: "
            f"{width}"
        )

        return False


    # ------------------------------------------------------
    # すべて正常
    # ------------------------------------------------------

    return True


# ==========================================================
# デフォルト設定取得
# ==========================================================

def get_default_subtitle_font_settings():

    settings = _get_default_settings()

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
#   1つでも不正
#       ↓
#   全体を標準設定へ戻す
#
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
    # 入力値を1つのsourceへまとめる
    # ======================================================

    source = {}

    if isinstance(
        settings,
        dict
    ):

        source.update(
            settings
        )


    # ======================================================
    # preset_name
    #
    # 旧キー preset も入力互換として許可。
    # ======================================================

    if (
        "preset_name" not in source
        and
        "preset" in source
    ):

        source[
            "preset_name"
        ] = source.get(
            "preset"
        )


    # ======================================================
    # 関数引数を反映
    #
    # 明示的に指定された場合のみ上書き。
    # ======================================================

    if preset_name is not None:

        source[
            "preset_name"
        ] = preset_name


    if font is not None:

        source[
            "font"
        ] = font


    if text_color is not None:

        source[
            "text_color"
        ] = text_color


    if outline_color is not None:

        source[
            "outline_color"
        ] = outline_color


    if outline_width is not None:

        source[
            "outline_width"
        ] = outline_width


    # ======================================================
    # 何も指定されていない
    #
    # → 標準設定
    # ======================================================

    if not source:

        result = _get_default_settings()

        _log(
            "no subtitle settings specified."
        )

        _log(
            f"fallback to default: {result}"
        )

        _log(
            "select_subtitle_font() COMPLETE"
        )

        return result


    # ======================================================
    # 値を整形
    #
    # ※ここでは勝手に標準値へ置き換えない。
    #   不正なら「全体を標準」にするため。
    # ======================================================

    candidate = {

        "preset_name":
            source.get(
                "preset_name"
            ),

        "font":
            source.get(
                "font"
            ),

        "text_color":
            source.get(
                "text_color"
            ),

        "outline_color":
            source.get(
                "outline_color"
            ),

        "outline_width":
            source.get(
                "outline_width"
            ),

    }


    # ------------------------------------------------------
    # 文字列項目だけstrip
    # ------------------------------------------------------

    if isinstance(
        candidate["preset_name"],
        str
    ):

        candidate[
            "preset_name"
        ] = candidate[
            "preset_name"
        ].strip()


    if isinstance(
        candidate["font"],
        str
    ):

        candidate[
            "font"
        ] = candidate[
            "font"
        ].strip()


    # ======================================================
    # 1項目でも不正なら全体を標準へ
    # ======================================================

    if not _is_valid_subtitle_settings(
        candidate
    ):

        _log(
            "subtitle settings contain invalid value."
        )

        _log(
            "IMPORTANT: "
            "one or more values are invalid."
        )

        _log(
            "ALL subtitle settings "
            "will fallback to default."
        )

        result = _get_default_settings()

        _log(
            f"fallback settings: {result}"
        )

        _log(
            "select_subtitle_font() COMPLETE"
        )

        return result


    # ======================================================
    # outline_widthを整数化
    # ======================================================

    candidate[
        "outline_width"
    ] = int(
        candidate[
            "outline_width"
        ]
    )


    # ======================================================
    # 最終設定
    # ======================================================

    normalized = {

        "preset_name":
            candidate[
                "preset_name"
            ],

        "font":
            candidate[
                "font"
            ],

        "text_color":
            candidate[
                "text_color"
            ],

        "outline_color":
            candidate[
                "outline_color"
            ],

        "outline_width":
            candidate[
                "outline_width"
            ],

    }


    _log(
        f"normalized: {normalized}"
    )

    _log(
        "select_subtitle_font() COMPLETE"
    )

    return normalized


# ==========================================================
# カラー情報取得
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
# 標準設定判定
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
    print("==========================================")
    print("subtitle_font.py test")
    print("==========================================")


    # ======================================================
    # 1. 何も指定しない
    # ======================================================

    print()
    print("[TEST 1] no settings")

    result = select_subtitle_font()

    print(result)


    # ======================================================
    # 2. 正常な設定
    # ======================================================

    print()
    print("[TEST 2] valid settings")

    result = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width=3

    )

    print(result)


    # ======================================================
    # 3. text_colorだけ不正
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("[TEST 3] invalid text_color")

    result = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="紫",

        outline_color="青",

        outline_width=3

    )

    print(result)


    # ======================================================
    # 4. outline_widthだけ不正
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("[TEST 4] invalid outline_width")

    result = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width=999

    )

    print(result)


    # ======================================================
    # 5. fontだけ不正
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("[TEST 5] invalid font")

    result = select_subtitle_font(

        preset_name="標準",

        font="",

        text_color="白",

        outline_color="青",

        outline_width=3

    )

    print(result)


    # ======================================================
    # 6. preset_nameだけ不正
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("[TEST 6] invalid preset_name")

    result = select_subtitle_font(

        preset_name="存在しないプリセット",

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width=3

    )

    print(result)


    # ======================================================
    # 7. settingsに1つでも不正値
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("[TEST 7] invalid settings")

    result = select_subtitle_font(

        settings={

            "preset_name":
                "標準",

            "font":
                "Noto Sans CJK JP",

            "text_color":
                "白",

            "outline_color":
                "紫",

            "outline_width":
                3,

        }

    )

    print(result)


    # ======================================================
    # 8. 旧キー preset
    # ======================================================

    print()
    print("[TEST 8] legacy preset")

    result = select_subtitle_font(

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
                3,

        }

    )

    print(result)


    # ======================================================
    # 9. 標準設定判定
    # ======================================================

    print()
    print("[TEST 9] is_default")

    print(
        is_default_subtitle_setting(
            result
        )
    )


    print()
    print("==========================================")
    print("TEST COMPLETE")
    print("==========================================")
