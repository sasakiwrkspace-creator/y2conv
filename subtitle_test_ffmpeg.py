# =====================================
# subtitle_test_ffmpeg.py
#
# FFmpeg字幕テスト
#
# 処理:
#
# test.mp4
#     ↓
# FFmpeg 1回
#     ↓
# test_embed.mp4
#
# =====================================

from pathlib import Path
import subprocess


# =====================================
# パス
# =====================================

DOWNLOAD_DIR = Path("/app/downloads")

INPUT_MP4 = DOWNLOAD_DIR / "test.mp4"
INPUT_SRT = DOWNLOAD_DIR / "test.srt"
OUTPUT_MP4 = DOWNLOAD_DIR / "test_embed.mp4"


# =====================================
# FFmpeg実行
# =====================================

def run_ffmpeg_subtitle_test(
    input_path=None,
    output_path=None
):

    print("==========================================", flush=True)
    print("[SUBTITLE TEST] run_ffmpeg_subtitle_test()", flush=True)
    print("==========================================", flush=True)


    # =====================================
    # パス決定
    # =====================================

    if input_path is None:
        input_file = INPUT_MP4
    else:
        input_file = Path(input_path)


    if output_path is None:
        output_file = OUTPUT_MP4
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
            f"入力パスがファイルではありません: {input_file}"
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


    if not INPUT_SRT.exists():

        raise FileNotFoundError(
            f"SRTファイルが存在しません: {INPUT_SRT}"
        )


    if not INPUT_SRT.is_file():

        raise FileNotFoundError(
            f"SRTパスがファイルではありません: {INPUT_SRT}"
        )


    print(
        "[SUBTITLE TEST] SRT存在確認 OK",
        flush=True
    )


    # =====================================
    # 出力ファイル削除
    # =====================================

    if output_file.exists():

        print(
            "[SUBTITLE TEST] 既存出力を削除",
            flush=True
        )

        output_file.unlink()


    # =====================================
    # 字幕フィルター
    # =====================================

    subtitle_filter = (
        "subtitles="
        f"'{INPUT_SRT}':"
        "fontsdir='/usr/share/fonts/opentype/noto':"
        "force_style="
        "'FontName=Noto Sans CJK JP,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00FF0000,"
        "Outline=5'"
    )


    # =====================================
    # FFmpeg command
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
        f"scale=640:360,{subtitle_filter}",

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
    # Command表示
    # =====================================

    print("==========================================", flush=True)
    print("[SUBTITLE TEST] FFmpeg command", flush=True)
    print("==========================================", flush=True)

    print(
        " ".join(command),
        flush=True
    )


    # =====================================
    # FFmpeg起動
    #
    # ここだけ。
    #
    # FFmpegは1回だけ起動する。
    # =====================================

    print("==========================================", flush=True)
    print("[SUBTITLE TEST] FFmpeg起動【1回だけ】", flush=True)
    print("==========================================", flush=True)


    try:

        result = subprocess.run(

            command,

            # ---------------------------------
            # FFmpegの標準出力・エラーを
            # Python側に大量に溜めない
            # ---------------------------------

            stdout=subprocess.DEVNULL,

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
            "FFmpegが120秒以内に終了しませんでした。"
        )


    except Exception as error:

        print(
            "[SUBTITLE TEST] FFmpeg起動例外",
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
        f"[SUBTITLE TEST] returncode: {result.returncode}",
        flush=True
    )

    print("==========================================", flush=True)


    # =====================================
    # stderr表示
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
    # returncode確認
    # =====================================

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg処理失敗\n\n"
            f"returncode: {result.returncode}\n\n"
            f"stderr:\n{result.stderr}"
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
            "出力パスがファイルではありません: "
            f"{output_file}"
        )


    output_size = output_file.stat().st_size


    if output_size <= 0:

        raise RuntimeError(
            "FFmpegは終了しましたが、"
            "出力ファイルのサイズが0 bytesです。"
        )


    print(
        "[SUBTITLE TEST] 出力ファイル確認 OK",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] 出力ファイル: {output_file}",
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
        "[SUBTITLE TEST] FFmpegテスト完了",
        flush=True
    )

    print("==========================================", flush=True)


    return output_file
