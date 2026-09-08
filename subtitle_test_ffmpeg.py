from pathlib import Path
import subprocess


DOWNLOAD_DIR = Path("/app/downloads")

INPUT_MP4 = DOWNLOAD_DIR / "test.mp4"
INPUT_SRT = DOWNLOAD_DIR / "test.srt"
OUTPUT_MP4 = DOWNLOAD_DIR / "test_embed.mp4"


def run_ffmpeg_subtitle_test():

    print("==========================================", flush=True)
    print("[SUBTITLE TEST] FFmpegテスト開始", flush=True)
    print("==========================================", flush=True)

    # -------------------------------------
    # MP4確認
    # -------------------------------------

    if not INPUT_MP4.exists():
        raise FileNotFoundError(
            f"入力ファイルが存在しません: {INPUT_MP4}"
        )

    # -------------------------------------
    # SRT確認
    # -------------------------------------

    if not INPUT_SRT.exists():
        raise FileNotFoundError(
            f"SRTファイルが存在しません: {INPUT_SRT}"
        )

    print(
        f"[SUBTITLE TEST] 入力MP4: {INPUT_MP4}",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] 入力SRT: {INPUT_SRT}",
        flush=True
    )

    # -------------------------------------
    # 既存出力削除
    # -------------------------------------

    if OUTPUT_MP4.exists():
        OUTPUT_MP4.unlink()

    # -------------------------------------
    # 字幕フィルター
    # -------------------------------------

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

    # -------------------------------------
    # FFmpeg
    # -------------------------------------

    command = [
        "/usr/bin/ffmpeg",
        "-y",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",

        "-i",
        str(INPUT_MP4),

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

        str(OUTPUT_MP4)
    ]

    print("==========================================", flush=True)
    print("[SUBTITLE TEST] FFmpeg起動【1回だけ】", flush=True)
    print("==========================================", flush=True)

    print(
        "[SUBTITLE TEST] command:",
        " ".join(command),
        flush=True
    )

    # -------------------------------------
    # FFmpegを1回だけ起動
    # -------------------------------------

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120
    )

    # -------------------------------------
    # FFmpeg終了
    # -------------------------------------

    print("==========================================", flush=True)
    print("[SUBTITLE TEST] FFmpeg終了", flush=True)
    print(
        f"[SUBTITLE TEST] returncode: {result.returncode}",
        flush=True
    )
    print("==========================================", flush=True)

    if result.stderr:
        print(
            "[SUBTITLE TEST] FFmpeg stderr:",
            result.stderr,
            flush=True
        )

    # -------------------------------------
    # FFmpeg失敗
    # -------------------------------------

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg処理失敗"
        )

    # -------------------------------------
    # 出力確認
    # -------------------------------------

    if not OUTPUT_MP4.exists():

        raise FileNotFoundError(
            f"FFmpeg終了後も出力ファイルがありません: "
            f"{OUTPUT_MP4}"
        )

    output_size = OUTPUT_MP4.stat().st_size

    print(
        f"[SUBTITLE TEST] 出力ファイル: {OUTPUT_MP4}",
        flush=True
    )

    print(
        f"[SUBTITLE TEST] 出力サイズ: {output_size} bytes",
        flush=True
    )

    print("==========================================", flush=True)
    print("[SUBTITLE TEST] 完了", flush=True)
    print("==========================================", flush=True)

    return OUTPUT_MP4
