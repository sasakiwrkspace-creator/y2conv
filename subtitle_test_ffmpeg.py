from pathlib import Path
import subprocess


DOWNLOAD_DIR = Path("/app/downloads")

DEFAULT_INPUT_MP4 = DOWNLOAD_DIR / "test.mp4"
DEFAULT_INPUT_SRT = DOWNLOAD_DIR / "test.srt"

# ==========================================================
# デフォルト字幕MP4
#
# 入力:
#   test.mp4
#
# 出力:
#   test_字幕.mp4
# ==========================================================

DEFAULT_OUTPUT_MP4 = DOWNLOAD_DIR / "test_字幕.mp4"


# フォントディレクトリ
DEFAULT_FONT_DIR = DOWNLOAD_DIR / "fonts"


# =====================================
# subtitle_font.js と同じデフォルト設定
# =====================================

DEFAULT_SUBTITLE_FONT_SETTINGS = {
    "preset_name": "",
    "font": "Noto Sans CJK JP",
    "text_color": "白",
    "outline_color": "青",
    "outline_width": 3,
}


# =====================================
# subtitle_font.js と同じ色
# =====================================

COLOR_MAP = {
    "白": "#FFFFFF",
    "黒": "#000000",
    "赤": "#FF0000",
    "青": "#0000FF",
    "黄": "#FFFF00",
    "シアン": "#00FFFF",
}


TEXT_COLORS = {
    "白",
    "黒",
    "赤",
    "青",
    "黄",
}


OUTLINE_COLORS = {
    "白",
    "黒",
    "赤",
    "青",
    "黄",
    "シアン",
}


# =====================================
# subtitle_font.js と同じフォント一覧
# =====================================

FONT_LIST = {
    "Noto Sans CJK JP",
    "Noto Serif CJK JP",
    "Noto Sans JP",
    "Noto Serif JP",
    "IPAGothic",
    "IPAMincho",
}


# =====================================
# HEX → FFmpeg/libass ASSカラー
#
# #RRGGBB
#       ↓
# &H00BBGGRR
# =====================================

def hex_to_ass_color(color_hex):

    if not isinstance(color_hex, str):

        return "&H00FFFFFF"

    value = color_hex.strip().upper()

    if value.startswith("#"):

        value = value[1:]

    if len(value) != 6:

        return "&H00FFFFFF"

    try:

        int(value, 16)

    except ValueError:

        return "&H00FFFFFF"

    rr = value[0:2]
    gg = value[2:4]
    bb = value[4:6]

    return f"&H00{bb}{gg}{rr}"


# =====================================
# 色名 → FFmpeg/libassカラー
# =====================================

def color_name_to_ass(color_name):

    color_hex = COLOR_MAP.get(
        color_name,
        "#FFFFFF"
    )

    return hex_to_ass_color(
        color_hex
    )


# =====================================
# 字幕フォント設定を正規化
# =====================================

def normalize_subtitle_settings(
    settings=None
):

    if not isinstance(settings, dict):

        settings = {}


    # =================================
    # プリセット名
    # =================================

    preset_name = settings.get(
        "preset_name",
        settings.get(
            "presetName",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "preset_name"
            ]
        )
    )

    if not isinstance(
        preset_name,
        str
    ):

        preset_name = ""


    # =================================
    # フォント
    # =================================

    font = settings.get(
        "font",
        DEFAULT_SUBTITLE_FONT_SETTINGS[
            "font"
        ]
    )

    if not isinstance(
        font,
        str
    ):

        font = DEFAULT_SUBTITLE_FONT_SETTINGS[
            "font"
        ]

    font = font.strip()

    if font not in FONT_LIST:

        font = DEFAULT_SUBTITLE_FONT_SETTINGS[
            "font"
        ]


    # =================================
    # 文字色
    # =================================

    text_color = settings.get(
        "text_color",
        settings.get(
            "textColor",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "text_color"
            ]
        )
    )

    if text_color not in TEXT_COLORS:

        text_color = DEFAULT_SUBTITLE_FONT_SETTINGS[
            "text_color"
        ]


    # =================================
    # 縁取り色
    # =================================

    outline_color = settings.get(
        "outline_color",
        settings.get(
            "outlineColor",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_color"
            ]
        )
    )

    if outline_color not in OUTLINE_COLORS:

        outline_color = DEFAULT_SUBTITLE_FONT_SETTINGS[
            "outline_color"
        ]


    # =================================
    # 縁の太さ
    # =================================

    outline_width = settings.get(
        "outline_width",
        settings.get(
            "outlineWidth",
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_width"
            ]
        )
    )

    try:

        outline_width = int(
            round(
                float(outline_width)
            )
        )

    except (
        TypeError,
        ValueError
    ):

        outline_width = (
            DEFAULT_SUBTITLE_FONT_SETTINGS[
                "outline_width"
            ]
        )


    outline_width = max(
        0,
        min(
            10,
            outline_width
        )
    )


    # =================================
    # HEX
    # =================================

    text_color_hex = COLOR_MAP.get(
        text_color,
        "#FFFFFF"
    )

    outline_color_hex = COLOR_MAP.get(
        outline_color,
        "#0000FF"
    )


    # =================================
    # ASSカラー
    # =================================

    primary_colour = hex_to_ass_color(
        text_color_hex
    )

    outline_colour = hex_to_ass_color(
        outline_color_hex
    )


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

        "primary_colour":
            primary_colour,

        "outline_colour":
            outline_colour,

    }


# =====================================
# 字幕FFmpeg filter生成
# =====================================

def build_subtitle_filter(
    srt_file,
    font_directory,
    subtitle_settings=None
):

    settings = normalize_subtitle_settings(
        subtitle_settings
    )


    # =================================
    # パス
    # =================================

    subtitle_filename = (
        str(srt_file)
        .replace("\\", "/")
        .replace("'", "\\'")
    )


    font_dir_name = (
        str(font_directory)
        .replace("\\", "/")
        .replace("'", "\\'")
    )


    # =================================
    # force_style
    # =================================

    force_style = (
        f"FontName={settings['font']},"
        f"PrimaryColour={settings['primary_colour']},"
        f"OutlineColour={settings['outline_colour']},"
        f"Outline={settings['outline_width']}"
    )


    subtitle_filter = (
        "subtitles="
        f"filename='{subtitle_filename}':"
        f"fontsdir='{font_dir_name}':"
        f"force_style='{force_style}'"
    )


    return (
        subtitle_filter,
        settings
    )


# =====================================
# 字幕MP4出力ファイル名生成
#
# 入力:
#
#   /app/downloads/タイトル.mp4
#
# 出力:
#
#   /app/downloads/タイトル_字幕.mp4
#
# =====================================

def build_subtitle_output_path(
    input_file
):

    input_file = Path(
        input_file
    )

    return (
        input_file.parent
        /
        f"{input_file.stem}_字幕.mp4"
    )


# =====================================
# FFmpeg字幕テスト
# =====================================

def run_ffmpeg_subtitle_test(
    input_path=None,
    srt_path=None,
    output_path=None,
    font_dir=None,
    subtitle_settings=None
):

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] START",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    # =====================================
    # 入力MP4
    # =====================================

    if input_path is None:

        input_file = DEFAULT_INPUT_MP4

    else:

        input_file = Path(
            input_path
        )


    # =====================================
    # SRT
    # =====================================

    if srt_path is None:

        srt_file = DEFAULT_INPUT_SRT

    else:

        srt_file = Path(
            srt_path
        )


    # =====================================
    # 出力MP4
    #
    # output_pathが指定されていない場合、
    # 入力MP4の名前を基準に
    #
    #   タイトル.mp4
    #       ↓
    #   タイトル_字幕.mp4
    #
    # とする。
    # =====================================

    if output_path is None:

        output_file = build_subtitle_output_path(
            input_file
        )

    else:

        output_file = Path(
            output_path
        )


    # =====================================
    # フォントディレクトリ
    # =====================================

    if font_dir is None:

        font_directory = DEFAULT_FONT_DIR

    else:

        font_directory = Path(
            font_dir
        )


    # =====================================
    # 字幕設定
    # =====================================

    settings = normalize_subtitle_settings(
        subtitle_settings
    )


    print(
        "[SUBTITLE TEST] subtitle settings:",
        flush=True
    )

    print(
        f"  preset_name: "
        f"{settings['preset_name']}",
        flush=True
    )

    print(
        f"  font: "
        f"{settings['font']}",
        flush=True
    )

    print(
        f"  text_color: "
        f"{settings['text_color']} "
        f"({settings['text_color_hex']})",
        flush=True
    )

    print(
        f"  outline_color: "
        f"{settings['outline_color']} "
        f"({settings['outline_color_hex']})",
        flush=True
    )

    print(
        f"  outline_width: "
        f"{settings['outline_width']}",
        flush=True
    )


    # =====================================
    # パス表示
    # =====================================

    print(
        f"[SUBTITLE TEST] input: {input_file}",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] subtitle: {srt_file}",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] font directory: "
        f"{font_directory}",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] output: {output_file}",
        flush=True
    )


    # =====================================
    # MP4確認
    # =====================================

    print(
        "[SUBTITLE TEST] MP4存在確認 START",
        flush=True
    )

    if not input_file.exists():

        raise FileNotFoundError(
            f"入力MP4が存在しません: "
            f"{input_file}"
        )

    if not input_file.is_file():

        raise FileNotFoundError(
            f"入力MP4ではありません: "
            f"{input_file}"
        )


    input_size = (
        input_file.stat().st_size
    )


    print(
        "[SUBTITLE TEST] MP4存在確認 OK",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] 入力サイズ: "
        f"{input_size} bytes",
        flush=True
    )


    # =====================================
    # SRT確認
    # =====================================

    print(
        "[SUBTITLE TEST] SRT存在確認 START",
        flush=True
    )

    if not srt_file.exists():

        raise FileNotFoundError(
            f"字幕SRTが存在しません: "
            f"{srt_file}"
        )

    if not srt_file.is_file():

        raise FileNotFoundError(
            f"字幕SRTではありません: "
            f"{srt_file}"
        )


    srt_size = (
        srt_file.stat().st_size
    )


    print(
        "[SUBTITLE TEST] SRT存在確認 OK",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] SRTサイズ: "
        f"{srt_size} bytes",
        flush=True
    )


    # =====================================
    # フォントディレクトリ確認
    # =====================================

    print(
        "[SUBTITLE TEST] FONT DIRECTORY確認 START",
        flush=True
    )

    if not font_directory.exists():

        raise FileNotFoundError(
            f"フォントディレクトリが存在しません: "
            f"{font_directory}"
        )

    if not font_directory.is_dir():

        raise FileNotFoundError(
            f"フォントディレクトリではありません: "
            f"{font_directory}"
        )


    print(
        "[SUBTITLE TEST] FONT DIRECTORY確認 OK",
        flush=True
    )


    # =====================================
    # フォントファイル確認
    # =====================================

    font_files = []


    for extension in (
        "*.ttf",
        "*.ttc",
        "*.otf"
    ):

        font_files.extend(
            font_directory.glob(
                extension
            )
        )


    print(
        f"[SUBTITLE TEST] "
        f"フォントファイル数: "
        f"{len(font_files)}",
        flush=True
    )


    for font_file in font_files:

        print(
            f"[SUBTITLE TEST] font: "
            f"{font_file}",
            flush=True
        )


    # =====================================
    # 出力ディレクトリ
    # =====================================

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # =====================================
    # 既存出力削除
    # =====================================

    if output_file.exists():

        print(
            "[SUBTITLE TEST] 既存出力削除",
            flush=True
        )

        output_file.unlink()


    # =====================================
    # 字幕フィルター
    # =====================================

    subtitle_filter, settings = (
        build_subtitle_filter(
            srt_file,
            font_directory,
            settings
        )
    )


    # =====================================
    # FFmpegコマンド
    # =====================================

    command = [

        "/usr/bin/ffmpeg",

        "-y",

        "-nostdin",

        "-hide_banner",

        "-loglevel",
        "error",

        "-i",
        str(input_file),

        "-vf",
        subtitle_filter,

        "-map",
        "0:v:0",

        "-map",
        "0:a:0?",

        "-c:v",
        "libx264",

        "-threads",
        "1",

        "-preset",
        "ultrafast",

        "-crf",
        "28",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-movflags",
        "+faststart",

        str(output_file)
    ]


    # =====================================
    # コマンド表示
    # =====================================

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg command",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        " ".join(command),
        flush=True
    )


    # =====================================
    # FFmpeg開始
    # =====================================

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg起動【1回だけ】",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] subprocess.run BEFORE",
        flush=True
    )


    # =====================================
    # FFmpeg実行
    # =====================================

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120
        )

    except subprocess.TimeoutExpired:

        print(
            "[SUBTITLE TEST] FFmpeg TIMEOUT",
            flush=True
        )

        raise RuntimeError(
            "FFmpegが120秒以内に終了しませんでした"
        )

    except Exception as error:

        print(
            "[SUBTITLE TEST] "
            "subprocess.run ERROR",
            flush=True
        )

        print(
            f"[SUBTITLE TEST] "
            f"{type(error).__name__}: "
            f"{error}",
            flush=True
        )

        raise


    # =====================================
    # FFmpeg終了
    # =====================================

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg終了",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] returncode: "
        f"{result.returncode}",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )


    # =====================================
    # stderr
    # =====================================

    if result.stderr:

        print(
            "[SUBTITLE TEST] FFmpeg stderr:",
            flush=True
        )

        print(
            result.stderr,
            flush=True
        )


    # =====================================
    # FFmpeg失敗
    # =====================================

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg字幕処理失敗 "
            f"(returncode={result.returncode})"
        )


    # =====================================
    # 出力確認
    # =====================================

    print(
        "[SUBTITLE TEST] 出力ファイル確認 START",
        flush=True
    )


    if not output_file.exists():

        raise FileNotFoundError(
            "FFmpeg終了後も出力ファイルがありません: "
            f"{output_file}"
        )


    if not output_file.is_file():

        raise FileNotFoundError(
            "FFmpeg出力がファイルではありません: "
            f"{output_file}"
        )


    output_size = (
        output_file.stat().st_size
    )


    if output_size <= 0:

        raise RuntimeError(
            "FFmpeg出力ファイルのサイズが0 bytesです: "
            f"{output_file}"
        )


    print(
        "[SUBTITLE TEST] 出力ファイル確認 OK",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] 出力サイズ: "
        f"{output_size} bytes",
        flush=True
    )


    # =====================================
    # 完了
    # =====================================

    print(
        "==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] COMPLETE",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] output: "
        f"{output_file}",
        flush=True
    )


    return output_file
