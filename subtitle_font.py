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
# 動作:
#
#   初期値
#      ↓
#   subtitle_font.py で任意値をセット
#      ↓
#   値が未指定なら初期値
#      ↓
#   どれか1つでも不正値なら設定全体を初期値へ戻す
#      ↓
#   正常な設定だけFFmpegへ渡す
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
# 設定全体を初期値へ戻す
# ==========================================================

def _get_default_settings():

    return dict(
        DEFAULT_SUBTITLE_FONT_SETTINGS
    )


# ==========================================================
# フォント値の検証
#
# 未指定:
#   初期値として扱う
#
# 空文字:
#   初期値として扱う
#
# その他:
#   文字列として有効なら使用
# ==========================================================

def _normalize_font(
    value
):

    if value is None:

        return (
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "font"
            ]
        )

    value = str(
        value
    ).strip()

    if not value:

        return (
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "font"
            ]
        )

    return value


# ==========================================================
# カラー値の検証
#
# None / 空文字:
#   初期値
#
# 定義済みカラー:
#   OK
#
# 未定義カラー:
#   エラー
# ==========================================================

def _validate_color(
    value,
    field_name
):

    if value is None:

        return (
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                field_name
            ]
        )

    value = str(
        value
    ).strip()

    if not value:

        return (
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                field_name
            ]
        )

    if value not in SUBTITLE_COLORS:

        raise ValueError(
            f"{field_name} が不正です: {value}"
        )

    return value


# ==========================================================
# 縁太さの検証
#
# None / 空文字:
#   初期値
#
# 0～10:
#   OK
#
# それ以外:
#   エラー
# ==========================================================

def _validate_outline_width(
    value
):

    if value is None:

        return int(
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_width"
            ]
        )

    if isinstance(
        value,
        str
    ):

        value = value.strip()

        if not value:

            return int(
                DEFAULT_SUBTITLE_FONT_SETTINGS[
                    "outline_width"
                ]
            )

    try:

        # boolはintとして扱わない
        if isinstance(
            value,
            bool
        ):

            raise ValueError

        normalized = int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        raise ValueError(
            f"outline_width が不正です: {value}"
        )

    if normalized < 0 or normalized > 10:

        raise ValueError(
            f"outline_width が範囲外です: {normalized}"
        )

    return normalized


# ==========================================================
# デフォルト設定取得
#
# 戻り値:
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
# どれか1つでも明示指定値が不正だった場合、
# 設定全体を初期値へ戻す。
#
# 例:
#
# font       = 正常
# text_color = 紫 ← 不正
# outline    = 正常
#
# ↓
#
# 全体を標準設定へ戻す。
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

    else:

        source = {}


    # ======================================================
    # 入力値を取得
    #
    # settingsを優先。
    # 関数引数はsettingsに存在しない場合に使用。
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


    if source_preset_name is not None:

        selected_preset_name = (
            source_preset_name
        )

    else:

        selected_preset_name = (
            preset_name
        )


    # ======================================================
    # preset_name
    #
    # 未指定 / 空文字:
    #   標準
    #
    # 不正:
    #   設定全体を標準へ
    # ======================================================

    if selected_preset_name is None:

        selected_preset_name = (
            DEFAULT_PRESET_NAME
        )

    else:

        selected_preset_name = str(
            selected_preset_name
        ).strip()

        if not selected_preset_name:

            selected_preset_name = (
                DEFAULT_PRESET_NAME
            )


    preset_settings = (
        SUBTITLE_PRESETS.get(
            selected_preset_name
        )
    )


    # ======================================================
    # 不正プリセット
    #
    # ★設定全体を初期値へ戻す
    # ======================================================

    if preset_settings is None:

        _log(
            "invalid preset_name detected: "
            f"{selected_preset_name}"
        )

        _log(
            "fallback to DEFAULT_SUBTITLE_FONT_SETTINGS"
        )

        return _get_default_settings()


    # ======================================================
    # プリセットをベースにする
    # ======================================================

    result_font = preset_settings.get(
        "font"
    )

    result_text_color = preset_settings.get(
        "text_color"
    )

    result_outline_color = preset_settings.get(
        "outline_color"
    )

    result_outline_width = preset_settings.get(
        "outline_width"
    )


    # ======================================================
    # settingsから上書き
    #
    # Noneの場合は上書きしない。
    #
    # 空文字は「未指定」として初期値側を使用。
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
    # settingsより関数引数を優先。
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
    # 正規化・検証
    #
    # ★1つでもエラーになったら全体を初期値へ戻す
    # ======================================================

    try:

        result_font = _normalize_font(
            result_font
        )

        result_text_color = _validate_color(
            result_text_color,
            "text_color"
        )

        result_outline_color = _validate_color(
            result_outline_color,
            "outline_color"
        )

        result_outline_width = _validate_outline_width(
            result_outline_width
        )

    except (
        ValueError,
        TypeError
    ) as error:

        _log(
            "INVALID subtitle setting detected"
        )

        _log(
            f"error: {error}"
        )

        _log(
            "ALL subtitle settings will fallback "
            "to default"
        )

        normalized = _get_default_settings()

        _log(
            f"normalized: {normalized}"
        )

        _log(
            "select_subtitle_font() COMPLETE"
        )

        return normalized


    # ======================================================
    # 最終設定
    # ======================================================

    normalized = {

        "preset_name":
            selected_preset_name,

        "font":
            result_font,

        "text_color":
            result_text_color,

        "outline_color":
            result_outline_color,

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
# カラー情報取得
#
# ここでは不正カラーをフォールバックしない。
# 明示的にRuntimeErrorを発生させる。
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
    # 1. 初期値
    # ======================================================

    print()
    print("[TEST 1] default")

    settings = (
        get_default_subtitle_font_settings()
    )

    print(
        settings
    )


    # ======================================================
    # 2. 明示指定
    # ======================================================

    print()
    print("[TEST 2] explicit")

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
    # 3. 値を何も指定しない
    # ======================================================

    print()
    print("[TEST 3] empty")

    settings = select_subtitle_font()

    print(
        settings
    )


    # ======================================================
    # 4. 不正な文字色
    #
    # ★全体が初期値になる
    # ======================================================

    print()
    print("[TEST 4] invalid text_color")

    settings = select_subtitle_font(

        font="Noto Sans CJK JP",

        text_color="紫",

        outline_color="青",

        outline_width=3

    )

    print(
        settings
    )


    # ======================================================
    # 5. 不正な縁色
    #
    # ★全体が初期値になる
    # ======================================================

    print()
    print("[TEST 5] invalid outline_color")

    settings = select_subtitle_font(

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="紫",

        outline_width=3

    )

    print(
        settings
    )


    # ======================================================
    # 6. 不正な縁太さ
    #
    # ★全体が初期値になる
    # ======================================================

    print()
    print("[TEST 6] invalid outline_width")

    settings = select_subtitle_font(

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width="abc"

    )

    print(
        settings
    )


    # ======================================================
    # 7. 範囲外の縁太さ
    #
    # ★全体が初期値になる
    # ======================================================

    print()
    print("[TEST 7] outline_width out of range")

    settings = select_subtitle_font(

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width=99

    )

    print(
        settings
    )


    # ======================================================
    # 8. 不正プリセット
    #
    # ★全体が初期値になる
    # ======================================================

    print()
    print("[TEST 8] invalid preset")

    settings = select_subtitle_font(

        preset_name="存在しないプリセット",

        font="Noto Sans CJK JP",

        text_color="白",

        outline_color="青",

        outline_width=3

    )

    print(
        settings
    )


    # ======================================================
    # 9. 旧キー互換
    # ======================================================

    print()
    print("[TEST 9] old key compatibility")

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
    print("[TEST 10] is_default")

    print(
        is_default_subtitle_setting(
            settings
        )
    )


    # ======================================================
    # 11. 不正カラー直接取得
    # ======================================================

    print()
    print("[TEST 11] invalid color test")

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
