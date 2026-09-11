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
# 動作仕様:
#
#   1. 値が未指定(None)の場合
#      → 標準設定を使用
#
#   2. 1項目でも不正な値がある場合
#      → 設定全体を標準設定へ戻す
#
#   3. 正常な値だけの場合
#      → 指定された設定を使用
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
# 標準プリセット名
# ==========================================================

DEFAULT_PRESET_NAME = "標準"


# ==========================================================
# 標準設定生成
#
# SUBTITLE_PRESETS["標準"] から生成する。
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
# 標準設定を新しいdictとして取得
#
# 元のDEFAULT_SUBTITLE_FONT_SETTINGSを
# 外部から変更されないようにする。
# ==========================================================

def _get_default_settings():

    return dict(
        DEFAULT_SUBTITLE_FONT_SETTINGS
    )


# ==========================================================
# preset_name 正規化・検証
#
# 戻り値:
#   (正常, 正規化後の値)
#
# None:
#   未指定として標準値を使用
#
# 空文字:
#   不正
#
# 存在しないプリセット:
#   不正
# ==========================================================

def _validate_preset_name(
    value
):

    if value is None:

        return (
            True,
            DEFAULT_PRESET_NAME
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
            False,
            None
        )

    if value not in SUBTITLE_PRESETS:

        return (
            False,
            None
        )

    return (
        True,
        value
    )


# ==========================================================
# フォント検証
#
# None:
#   未指定として標準フォント
#
# 空文字:
#   不正
# ==========================================================

def _validate_font(
    value
):

    if value is None:

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
            False,
            None
        )

    return (
        True,
        value
    )


# ==========================================================
# カラー検証
#
# None:
#   未指定として標準カラー
#
# 存在しないカラー:
#   不正
# ==========================================================

def _validate_color(
    value,
    default
):

    if value is None:

        return (
            True,
            default
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
            False,
            None
        )

    if value not in SUBTITLE_COLORS:

        return (
            False,
            None
        )

    return (
        True,
        value
    )


# ==========================================================
# 縁太さ検証
#
# None:
#   未指定として標準値
#
# 整数以外:
#   不正
#
# 0～10:
#   正常
#
# 0未満 / 10超:
#   不正
# ==========================================================

def _validate_outline_width(
    value
):

    if value is None:

        return (
            True,
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_width"
            ]
        )

    # boolはintのサブクラスなので明示的に除外
    if isinstance(
        value,
        bool
    ):

        return (
            False,
            None
        )

    try:

        normalized = int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        return (
            False,
            None
        )

    # "3.5" のような値をint()で
    # 通してしまわないための確認
    if isinstance(
        value,
        float
    ):

        if value != normalized:

            return (
                False,
                None
            )

    if isinstance(
        value,
        str
    ):

        if value.strip() != str(
            normalized
        ):

            return (
                False,
                None
            )

    if normalized < 0:

        return (
            False,
            None
        )

    if normalized > 10:

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
#
# 戻り値の正式キー:
#   preset_name
#   font
#   text_color
#   outline_color
#   outline_width
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
# ★重要
#
# 1項目でも不正な値が入った場合、
# 個別フォールバックではなく、
# 設定全体を標準設定へ戻す。
#
# None / 未指定は不正ではない。
# その項目だけ標準値を使用する。
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

        _log(
            "settings is invalid. "
            "fallback to default."
        )

        return _get_default_settings()


    # ======================================================
    # settings側の値
    #
    # 正式キー:
    #   preset_name
    #
    # 旧キー:
    #   preset
    #
    # settings側を優先。
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


    source_font = source.get(
        "font"
    )

    source_text_color = source.get(
        "text_color"
    )

    source_outline_color = source.get(
        "outline_color"
    )

    source_outline_width = source.get(
        "outline_width"
    )


    # ======================================================
    # 最終入力値
    #
    # settings側を優先し、
    # settingsに値がなければ関数引数を使用。
    # ======================================================

    final_preset_name = (

        source_preset_name
        if source_preset_name is not None
        else preset_name

    )

    final_font = (

        source_font
        if source_font is not None
        else font

    )

    final_text_color = (

        source_text_color
        if source_text_color is not None
        else text_color

    )

    final_outline_color = (

        source_outline_color
        if source_outline_color is not None
        else outline_color

    )

    final_outline_width = (

        source_outline_width
        if source_outline_width is not None
        else outline_width

    )


    # ======================================================
    # preset_name 検証
    # ======================================================

    preset_valid, normalized_preset_name = (
        _validate_preset_name(
            final_preset_name
        )
    )

    if not preset_valid:

        _log(
            "INVALID preset_name: "
            f"{final_preset_name!r}"
        )

        _log(
            "設定全体を標準設定へ戻します。"
        )

        return _get_default_settings()


    # ======================================================
    # プリセット取得
    # ======================================================

    preset_settings = (
        SUBTITLE_PRESETS[
            normalized_preset_name
        ]
    )


    # ======================================================
    # プリセットをベースにする
    #
    # preset_nameが指定されている場合、
    # まずプリセット値を使用。
    #
    # 個別指定がある場合のみ上書き。
    # ======================================================

    base_font = preset_settings.get(
        "font"
    )

    base_text_color = preset_settings.get(
        "text_color"
    )

    base_outline_color = preset_settings.get(
        "outline_color"
    )

    base_outline_width = preset_settings.get(
        "outline_width"
    )


    if final_font is None:

        final_font = base_font


    if final_text_color is None:

        final_text_color = base_text_color


    if final_outline_color is None:

        final_outline_color = base_outline_color


    if final_outline_width is None:

        final_outline_width = base_outline_width


    # ======================================================
    # 各項目を検証
    # ======================================================

    font_valid, normalized_font = (
        _validate_font(
            final_font
        )
    )

    if not font_valid:

        _log(
            "INVALID font: "
            f"{final_font!r}"
        )

        _log(
            "設定全体を標準設定へ戻します。"
        )

        return _get_default_settings()


    text_color_valid, normalized_text_color = (
        _validate_color(
            final_text_color,
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "text_color"
            ]
        )
    )

    if not text_color_valid:

        _log(
            "INVALID text_color: "
            f"{final_text_color!r}"
        )

        _log(
            "設定全体を標準設定へ戻します。"
        )

        return _get_default_settings()


    outline_color_valid, normalized_outline_color = (
        _validate_color(
            final_outline_color,
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_color"
            ]
        )
    )

    if not outline_color_valid:

        _log(
            "INVALID outline_color: "
            f"{final_outline_color!r}"
        )

        _log(
            "設定全体を標準設定へ戻します。"
        )

        return _get_default_settings()


    outline_width_valid, normalized_outline_width = (
        _validate_outline_width(
            final_outline_width
        )
    )

    if not outline_width_valid:

        _log(
            "INVALID outline_width: "
            f"{final_outline_width!r}"
        )

        _log(
            "設定全体を標準設定へ戻します。"
        )

        return _get_default_settings()


    # ======================================================
    # 最終設定
    #
    # ★正式な5キーだけを返す
    # ======================================================

    normalized = {

        "preset_name":
            normalized_preset_name,

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
# 不正カラーはフォールバックしない。
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
    # 1. 標準設定
    # ======================================================

    print()
    print("=== 1. default ===")

    settings = (
        get_default_subtitle_font_settings()
    )

    print(
        settings
    )


    # ======================================================
    # 2. 正常な明示指定
    # ======================================================

    print()
    print("=== 2. valid ===")

    settings = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width=3

    )

    print(
        settings
    )


    # ======================================================
    # 3. 1項目だけ不正
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("=== 3. invalid color ===")

    settings = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="紫",

        outline_width=3

    )

    print(
        settings
    )


    # ======================================================
    # 4. フォントが不正
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("=== 4. invalid font ===")

    settings = select_subtitle_font(

        preset_name="標準",

        font="存在しないフォント",

        text_color="赤",

        outline_color="緑",

        outline_width=7

    )

    print(
        settings
    )


    # ======================================================
    # 5. 縁太さが不正
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("=== 5. invalid outline width ===")

    settings = select_subtitle_font(

        preset_name="標準",

        font="Noto Sans CJK JP",

        text_color="赤",

        outline_color="緑",

        outline_width="abc"

    )

    print(
        settings
    )


    # ======================================================
    # 6. 縁太さが範囲外
    #
    # → 全体が標準へ戻る
    # ======================================================

    print()
    print("=== 6. outline width over 10 ===")

    settings = select_subtitle_font(

        outline_width=11

    )

    print(
        settings
    )


    # ======================================================
    # 7. 未指定
    #
    # → 標準設定
    # ======================================================

    print()
    print("=== 7. none ===")

    settings = select_subtitle_font()

    print(
        settings
    )


    # ======================================================
    # 8. 空文字
    #
    # → 不正なので全体を標準へ戻す
    # ======================================================

    print()
    print("=== 8. empty string ===")

    settings = select_subtitle_font(

        font=""

    )

    print(
        settings
    )


    # ======================================================
    # 9. 旧キー preset
    #
    # → 入力互換
    # → 内部ではpreset_nameへ統一
    # ======================================================

    print()
    print("=== 9. legacy preset ===")

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
                3,

        }

    )

    print(
        settings
    )


    # ======================================================
    # 10. 標準設定判定
    # ======================================================

    print()
    print("=== 10. is_default ===")

    print(
        is_default_subtitle_setting(
            settings
        )
    )


    print()
    print("==========================================")
    print("TEST COMPLETE")
    print("==========================================")
