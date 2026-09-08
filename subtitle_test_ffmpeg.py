from pathlib import Path
import subprocess


DOWNLOAD_DIR = Path("/app/downloads")

DEFAULT_INPUT_MP4 = DOWNLOAD_DIR / "test.mp4"
DEFAULT_OUTPUT_MP4 = DOWNLOAD_DIR / "test_embed.mp4"


def run_ffmpeg_subtitle_test(
    input_path=None,
    output_path=None
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

    if output_path is None:
        output_file = DEFAULT_OUTPUT_MP4
    else:
        output_file = Path(output_path)

    print(
        f"[SUBTITLE TEST] input: {input_file}",
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
            f"入力ファイルが存在しません: {input_file}"
        )

    if not input_file.is_file():
        raise FileNotFoundError(
            f"入力ファイルではありません: {input_file}"
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
    # FFmpegコマンド
    #
    # 字幕なし
    # scaleなし
    #
    # 動画だけ再エンコード
    #
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
            "FFmpeg処理失敗 "
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
