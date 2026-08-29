import sys
import traceback
import shutil
import subprocess
import tempfile
from pathlib import Path

print("==========================================", flush=True)
print("[DEBUG] ytdlp.py loaded", flush=True)
print("[DEBUG] Python:", sys.version, flush=True)
print("[DEBUG] yt-dlp module loading...", flush=True)

try:
    import yt_dlp
    print("[DEBUG] yt_dlp imported", flush=True)
    print("[DEBUG] yt_dlp version:", yt_dlp.version.__version__, flush=True)
    print("[DEBUG] yt_dlp location:", yt_dlp.__file__, flush=True)
except Exception as e:
    print("[DEBUG] yt_dlp import ERROR:", repr(e), flush=True)
    traceback.print_exc()
    raise

print("[DEBUG] deno path:", shutil.which("deno"), flush=True)

try:
    result = subprocess.run(
        ["deno", "--version"],
        capture_output=True,
        text=True,
        timeout=10
    )
    print("[DEBUG] deno returncode:", result.returncode, flush=True)
    print("[DEBUG] deno stdout:", result.stdout, flush=True)
    print("[DEBUG] deno stderr:", result.stderr, flush=True)
except Exception as e:
    print("[DEBUG] deno execution ERROR:", repr(e), flush=True)

try:
    import yt_dlp_ejs
    print("[DEBUG] yt_dlp_ejs imported", flush=True)
    print("[DEBUG] yt_dlp_ejs location:", yt_dlp_ejs.__file__, flush=True)
except Exception as e:
    print("[DEBUG] yt_dlp_ejs import ERROR:", repr(e), flush=True)

print("==========================================", flush=True)
