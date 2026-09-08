from pathlib import Path
import subprocess

DOWNLOAD_DIR = Path("/app/downloads")

INPUT_MP4 = DOWNLOAD_DIR / "test.mp4"
OUTPUT_MP4 = DOWNLOAD_DIR / "test_embed.mp4"

def run_ffmpeg_subtitle_test():

print("==========================================", flush=True)
print("[SUBTITLE TEST] START", flush=True)
print("==========================================", flush=True)

# -------------------------------------
# 入力確認
# -------------------------------------

print(
    "[SUBTITLE TEST] MP4存在確認 START",
    flush=True
)

if not INPUT_MP4.exists():
    raise FileNotFoundError(
        f"入力ファイルが存在しません: {INPUT_MP4}"
    )

input_size = INPUT_MP4.stat().st_size

print(
    "[SUBTITLE TEST] MP4存在確認 OK",
    flush=True
)

print(
    f"[SUBTITLE TEST] 入力サイズ: {input_size} bytes",
    flush=True
)

# -------------------------------------
# 既存出力削除
# -------------------------------------

if OUTPUT_MP4.exists():

    print(
        "[SUBTITLE TEST] 既存出力削除",
        flush=True
    )

    OUTPUT_MP4.unlink()

# -------------------------------------
# FFmpeg
#
# 字幕なし
# 再エンコードなし
# 単純コピー
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

    "-map",
    "0",

    "-c",
    "copy",

    str(OUTPUT_MP4)
]

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

# -------------------------------------
# FFmpeg起動
# -------------------------------------

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

# -------------------------------------
# FFmpeg実行
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
print(
    "[SUBTITLE TEST] FFmpeg終了",
    flush=True
)
print(
    f"[SUBTITLE TEST] returncode: {result.returncode}",
    flush=True
)
print("==========================================", flush=True)

# -------------------------------------
# stderr
# -------------------------------------

if result.stderr:

    print(
        "[SUBTITLE TEST] FFmpeg stderr:",
        flush=True
    )

    print(
        result.stderr,
        flush=True
    )

# -------------------------------------
# FFmpeg失敗
# -------------------------------------

if result.returncode != 0:

    raise RuntimeError(
        f"FFmpeg処理失敗 "
        f"(returncode={result.returncode})"
    )

# -------------------------------------
# 出力確認
# -------------------------------------

print(
    "[SUBTITLE TEST] 出力ファイル確認 START",
    flush=True
)

if not OUTPUT_MP4.exists():

    raise FileNotFoundError(
        "FFmpeg終了後も出力ファイルがありません: "
        f"{OUTPUT_MP4}"
    )

output_size = OUTPUT_MP4.stat().st_size

print(
    "[SUBTITLE TEST] 出力ファイル確認 OK",
    flush=True
)

print(
    f"[SUBTITLE TEST] 出力サイズ: "
    f"{output_size} bytes",
    flush=True
)

# -------------------------------------
# 完了
# -------------------------------------

print("==========================================", flush=True)
print(
    "[SUBTITLE TEST] COMPLETE",
    flush=True
)
print("==========================================", flush=True)

return OUTPUT_MP4
