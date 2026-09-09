from pathlib import Path
import subprocess


DOWNLOAD_DIR = Path("/app/downloads")

DEFAULT_INPUT_MP4 = DOWNLOAD_DIR / "test.mp4"
DEFAULT_INPUT_SRT = DOWNLOAD_DIR / "test.srt"
DEFAULT_OUTPUT_MP4 = DOWNLOAD_DIR / "test_embed.mp4"

# フォントディレクトリ
DEFAULT_FONT_DIR = DOWNLOAD_DIR / "fonts"


def run_ffmpeg_subtitle_test(
    input_path=None,
    srt_path=None,
    output_path=None,
    font_dir=None
):
    print("==========================================", flush=True)
    print("[SUBTITLE TEST] START", flush=True)
    print("==========================================", flush=True)

    # =====================================
    # パス
    # =====================================

    if input_path is None:
        input_file = DEFAULT_INPUT_MP4
    else:
        input_file = Path(input_path)

    if srt_path is None:
        srt_file = DEFAULT_INPUT_SRT
    else:
        srt_file = Path(srt_path)

    if output_path is None:
        output_file = DEFAULT_OUTPUT_MP4
    else:
        output_file = Path(output_path)

    if font_dir is None:
        font_directory = DEFAULT_FONT_DIR
    else:
        font_directory = Path(font_dir)

    print(
        f"[SUBTITLE TEST] input: {input_file}",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] subtitle: {srt_file}",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] font directory: {font_directory}",
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
            f"入力MP4が存在しません: {input_file}"
        )

    if not input_file.is_file():
        raise FileNotFoundError(
            f"入力MP4ではありません: {input_file}"
        )

    input_size = input_file.stat().st_size

    print(
        "[SUBTITLE TEST] MP4存在確認 OK",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] 入力サイズ: {input_size} bytes",
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
            f"字幕SRTが存在しません: {srt_file}"
        )

    if not srt_file.is_file():
        raise FileNotFoundError(
            f"字幕SRTではありません: {srt_file}"
        )

    srt_size = srt_file.stat().st_size

    print(
        "[SUBTITLE TEST] SRT存在確認 OK",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] SRTサイズ: {srt_size} bytes",
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
            font_directory.glob(extension)
        )

    print(
        f"[SUBTITLE TEST] "
        f"フォントファイル数: {len(font_files)}",
        flush=True
    )

    for font_file in font_files:
        print(
            f"[SUBTITLE TEST] font: {font_file}",
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
    #
    # 今回追加するのは fontsdir のみ
    #
    # force_styleなどはまだ使用しない
    # =====================================

    subtitle_filter = (
        f"subtitles="
        f"filename={srt_file}:"
        f"fontsdir={font_directory}"
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

    print("==========================================", flush=True)

    print(
        "[SUBTITLE TEST] FFmpeg command",
        flush=True
    )

    print("==========================================", flush=True)

    print(
        " ".join(command),
        flush=True
    )

    # =====================================
    # FFmpeg開始
    # =====================================

    print("==========================================", flush=True)

    print(
        "[SUBTITLE TEST] FFmpeg起動【1回だけ】",
        flush=True
    )

    print("==========================================", flush=True)

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
            "[SUBTITLE TEST] subprocess.run ERROR",
            flush=True
        )

        print(
            f"[SUBTITLE TEST] "
            f"{type(error).__name__}: {error}",
            flush=True
        )

        raise

    # =====================================
    # FFmpeg終了
    # =====================================

    print("==========================================", flush=True)

    print(
        "[SUBTITLE TEST] FFmpeg終了",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] returncode: "
        f"{result.returncode}",
        flush=True
    )

    print("==========================================", flush=True)

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

    output_size = output_file.stat().st_size

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

    print("==========================================", flush=True)

    print(
        "[SUBTITLE TEST] COMPLETE",
        flush=True
    )

    print("==========================================", flush=True)

    return output_file
