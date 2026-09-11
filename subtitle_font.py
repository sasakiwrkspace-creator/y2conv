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
# 動作ルール:
#
#   1. 値を指定しない
#        ↓
#      標準設定を使用
#
#   2. 正常な値を指定
#        ↓
#      指定値を使用
#
#   3. 1項目でも不正な値が入る
#        ↓
#      設定全体を標準設定へ戻す
#
#   4. 標準設定へ戻した場合も、
#      FFmpegには必ず正常な5項目を渡す
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
# 標準プリセット名
# ==========================================================

DEFAULT_PRESET_NAME = "標準"


# ==========================================================
# 標準設定生成
#
# ★SUBTITLE_PRESETS["標準"]から生成する。
# ==========================================================

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
# 標準設定をコピー
#
# 毎回新しいdictを返す。
# 外部から変更されても、
# DEFAULT_SUBTITLE_FONT_SETTINGS自体を壊さない。
# ==========================================================

def _get_default_settings_copy():

    return dict(
        DEFAULT_SUBTITLE_FONT_SETTINGS
    )


# ==========================================================
# 空値判定
#
# None / 空文字 / 空白文字
# → 未指定として扱う。
# ==========================================================

def _is_empty_value(
    value
):

    if value is None:

        return True

    if isinstance(
        value,
        str
    ):

        return not value.strip()

    return False


# ==========================================================
# フォント値検証
#
# 空値:
#   未指定として扱う
#
# 不正:
#   全体を標準設定へ戻す
#
# ※ここではフォントがOSに実際に存在するかまでは確認しない。
#   フォント存在確認はsubtitle.py側で行う。
# ==========================================================

def _validate_font(
    value
):

    if _is_empty_value(
        value
    ):

        return (
            True,
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "font"
            ]
        )

    if not isinstance(
        value,
        str
    ):

        return (
            False,
            None
        )

    value = value.strip()

    if not value:

        return (
            True,
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "font"
            ]
        )

    return (
        True,
        value
    )


# ==========================================================
# カラー値検証
#
# None / 空文字:
#   未指定 → 標準値
#
# 不正カラー:
#   Falseを返す
#
# ★ここでは個別フォールバックしない。
# ==========================================================

def _validate_color(
    value,
    default_color
):

    if _is_empty_value(
        value
    ):

        return (
            True,
            default_color
        )

    if not isinstance(
        value,
        str
    ):

        return (
            False,
            None
        )

    value = value.strip()

    if value in SUBTITLE_COLORS:

        return (
            True,
            value
        )

    return (
        False,
        None
    )


# ==========================================================
# 縁太さ検証
#
# 許可範囲:
#   0 ～ 10
#
# None / 空文字:
#   未指定 → 標準値
#
# 不正値:
#   False
#
# ★int("3.5") のような暗黙変換はしない。
# ==========================================================

def _validate_outline_width(
    value
):

    default_width = (
        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "outline_width"
        ]
    )

    if _is_empty_value(
        value
    ):

        return (
            True,
            default_width
        )

    # boolはintのサブクラスなので明示的に拒否
    if isinstance(
        value,
        bool
    ):

        return (
            False,
            None
        )

    try:

        # 整数として表現できるものだけ許可
        if isinstance(
            value,
            int
        ):

            normalized = value

        elif isinstance(
            value,
            str
        ):

            value = value.strip()

            if not value:

                return (
                    True,
                    default_width
                )

            # "3.5" などを許可しない
            if not value.isdigit():

                return (
                    False,
                    None
                )

            normalized = int(
                value
            )

        else:

            return (
                False,
                None
            )

    except (
        ValueError,
        TypeError
    ):

        return (
            False,
            None
        )

    if normalized < 0 or normalized > 10:

        return (
            False,
            None
        )

    return (
        True,
        normalized
    )


# ==========================================================
# デフォルト設定取得
# ==========================================================

def get_default_subtitle_font_settings():

    settings = _get_default_settings_copy()

    _log(
        "get_default_subtitle_font_settings()"
    )

    _log(
        f"default: {settings}"
    )

    return settings


# ==========================================================
# 設定全体を標準設定へ戻す
# ==========================================================

def _fallback_to_default(
    reason
):

    default_settings = (
        _get_default_settings_copy()
    )

    _log(
        "=========================================="
    )

    _log(
        "字幕設定エラーを検出しました。"
    )

    _log(
        f"理由: {reason}"
    )

    _log(
        "設定全体を標準設定へフォールバックします。"
    )

    _log(
        f"default: {default_settings}"
    )

    _log(
        "=========================================="
    )

    return default_settings


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
# settings:
#   正式キーを使用
#
# 旧キー:
#   preset
#
# は入力互換のためのみ許可する。
#
# ★重要:
#
#   1項目でも不正
#       ↓
#   5項目すべて標準設定
#
#   何も指定しない
#       ↓
#   標準設定
#
#   正常な指定
#       ↓
#   指定設定
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

    elif settings is None:

        source = {}

    else:

        return _fallback_to_default(
            "settingsがdictではありません"
        )


    # ======================================================
    # preset_name取得
    #
    # 正式:
    #   preset_name
    #
    # 旧:
    #   preset
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


    # ======================================================
    # 優先順位
    #
    # settings
    #   ↓
    # 関数引数
    #   ↓
    # 標準
    # ======================================================

    if not _is_empty_value(
        source_preset_name
    ):

        selected_preset_name = (
            source_preset_name
        )

    elif not _is_empty_value(
        preset_name
    ):

        selected_preset_name = (
            preset_name
        )

    else:

        selected_preset_name = (
            DEFAULT_PRESET_NAME
        )


    # ======================================================
    # preset_name検証
    # ======================================================

    if not isinstance(
        selected_preset_name,
        str
    ):

        return _fallback_to_default(
            "preset_nameが文字列ではありません"
        )


    selected_preset_name = (
        selected_preset_name.strip()
    )


    if not selected_preset_name:

        selected_preset_name = (
            DEFAULT_PRESET_NAME
        )


    # ======================================================
    # プリセット存在確認
    # ======================================================

    preset_settings = (
        SUBTITLE_PRESETS.get(
            selected_preset_name
        )
    )


    if not isinstance(
        preset_settings,
        dict
    ):

        return _fallback_to_default(
            "存在しないpreset_name: "
            f"{selected_preset_name}"
        )


    # ======================================================
    # プリセットをベースにする
    # ======================================================

    result_font = (
        preset_settings.get(
            "font"
        )
    )

    result_text_color = (
        preset_settings.get(
            "text_color"
        )
    )

    result_outline_color = (
        preset_settings.get(
            "outline_color"
        )
    )

    result_outline_width = (
        preset_settings.get(
            "outline_width"
        )
    )


    # ======================================================
    # settingsから上書き
    #
    # None / 空文字は「未指定」
    #
    # ただし明示的に不正な値が入っていた場合は、
    # 後段の検証で全体を標準設定へ戻す。
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
    # 関数引数から上書き
    #
    # None:
    #   未指定
    #
    # 空文字:
    #   後段で標準値として扱う
    #
    # 不正値:
    #   後段で全体を標準設定へ戻す
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
    # 各項目を検証
    #
    # ★重要
    #
    # どれか1つでもFalseなら、
    # 全体を標準設定へ戻す。
    # ======================================================

    font_ok, normalized_font = (
        _validate_font(
            result_font
        )
    )


    text_color_ok, normalized_text_color = (
        _validate_color(

            result_text_color,

            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "text_color"
            ]

        )
    )


    outline_color_ok, normalized_outline_color = (
        _validate_color(

            result_outline_color,

            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_color"
            ]

        )
    )


    outline_width_ok, normalized_outline_width = (
        _validate_outline_width(
            result_outline_width
        )
    )


    # ======================================================
    # エラーが1つでもあれば全体を標準設定
    # ======================================================

    if not font_ok:

        return _fallback_to_default(
            f"fontが不正です: {result_font!r}"
        )


    if not text_color_ok:

        return _fallback_to_default(
            f"text_colorが不正です: "
            f"{result_text_color!r}"
        )


    if not outline_color_ok:

        return _fallback_to_default(
            f"outline_colorが不正です: "
            f"{result_outline_color!r}"
        )


    if not outline_width_ok:

        return _fallback_to_default(
            f"outline_widthが不正です: "
            f"{result_outline_width!r}"
        )


    # ======================================================
    # 最終設定
    #
    # ★正式な内部キー5つのみ
    # ======================================================

    normalized = {

        "preset_name":
            selected_preset_name,

        "font":
            normalized_font,

        "text_color":
            normalized_text_color,

        "outline_color":
            normalized_outline_color,

        "outline_width":
            normalized_outline_width,

    }


    # ======================================================
    # 最終確認
    #
    # 念のため完成した設定をもう一度確認する。
    # ======================================================

    required_keys = (

        "preset_name",
        "font",
        "text_color",
        "outline_color",
        "outline_width",

    )


    for key in required_keys:

        if key not in normalized:

            return _fallback_to_default(
                f"最終設定に必須キーがありません: {key}"
            )


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
#
# select_subtitle_font()を通った後の値を
# 使用することを前提とする。
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
    #
    # → 標準設定
    # ======================================================

    print()
    print("TEST 1: no settings")

    settings = select_subtitle_font()

    print(
        settings
    )


    # ======================================================
    # 2. 正常な設定
    #
    # → 指定値
    # ======================================================

    print()
    print("TEST 2: valid settings")

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
    # 3. 1項目だけ不正
    #
    # outline_color = 紫
    #
    # → 全体を標準設定
    # ======================================================

    print()
    print("TEST 3: invalid outline_color")

    settings = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="赤",

        outline_color="紫",

        outline_width=8

    )

    print(
        settings
    )


    # ======================================================
    # 4. 1項目だけ不正
    #
    # outline_width = 999
    #
    # → 全体を標準設定
    # ======================================================

    print()
    print("TEST 4: invalid outline_width")

    settings = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="赤",

        outline_color="黒",

        outline_width=999

    )

    print(
        settings
    )


    # ======================================================
    # 5. 不正フォント型
    #
    # → 全体を標準設定
    # ======================================================

    print()
    print("TEST 5: invalid font type")

    settings = select_subtitle_font(

        font=12345,

        text_color="赤",

        outline_color="黒",

        outline_width=8

    )

    print(
        settings
    )


    # ======================================================
    # 6. 空文字
    #
    # → 未指定として標準設定
    # ======================================================

    print()
    print("TEST 6: empty values")

    settings = select_subtitle_font(

        font="",

        text_color="",

        outline_color="",

        outline_width=""

    )

    print(
        settings
    )


    # ======================================================
    # 7. 旧キー preset
    #
    # → 入力互換
    # ======================================================

    print()
    print("TEST 7: legacy preset key")

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
    # 8. 不正preset
    #
    # → 全体を標準設定
    # ======================================================

    print()
    print("TEST 8: invalid preset")

    settings = select_subtitle_font(

        preset_name="存在しないプリセット",

        font="Noto Sans CJK JP",

        text_color="赤",

        outline_color="黒",

        outline_width=8

    )

    print(
        settings
    )


    # ======================================================
    # 9. 標準設定判定
    # ======================================================

    print()
    print("TEST 9: is_default")

    print(
        is_default_subtitle_setting(
            settings
        )
    )


    # ======================================================
    # 10. 不正カラー直接取得
    # ======================================================

    print()
    print("TEST 10: invalid color lookup")

    try:

        get_subtitle_color(
            "紫"
        )

    except RuntimeError as error:

        print(
            error
        )


    print()
    print("==========================================")
    print("test complete")
    print("==========================================")
