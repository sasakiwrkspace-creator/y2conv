import os
import shutil

from dotenv import load_dotenv


load_dotenv()


# =====================================
# プロジェクトルート
# =====================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =====================================
# downloads
# =====================================

DOWNLOAD_DIR = os.path.join(
    BASE_DIR,
    "downloads"
)

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


# =====================================
# Gemini API
# =====================================

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)


# =====================================
# YouTube cookies
# =====================================

COOKIES_FILE = "/etc/secrets/cookies.txt"


# =====================================
# Deno
# =====================================
#
# DockerではPATHから検索する。
#
# /app/.deno/bin/deno
# /root/.deno/bin/deno
# などを直接固定しない。
#

DENO_PATH = shutil.which(
    "deno"
)


# =====================================
# FFmpeg
# =====================================

FFMPEG_PATH = shutil.which(
    "ffmpeg"
)


FFPROBE_PATH = shutil.which(
    "ffprobe"
)


# =====================================
# 音声分割設定
# =====================================

CHUNK_MINUTES = 15

CHUNK_SECONDS = (
    CHUNK_MINUTES * 60
)


# =====================================
# 確認ログ
# =====================================

print("==========================================")
print("CONFIG")
print("BASE_DIR:", BASE_DIR)
print("DOWNLOAD_DIR:", DOWNLOAD_DIR)

print(
    "DOWNLOAD_DIR exists:",
    os.path.isdir(
        DOWNLOAD_DIR
    )
)

print(
    "COOKIES_FILE:",
    COOKIES_FILE
)

print(
    "COOKIES_FILE exists:",
    os.path.isfile(
        COOKIES_FILE
    )
)

print(
    "DENO_PATH:",
    DENO_PATH
)

print(
    "DENO_PATH exists:",
    bool(
        DENO_PATH
        and os.path.isfile(DENO_PATH)
    )
)

print(
    "FFMPEG_PATH:",
    FFMPEG_PATH
)

print(
    "FFPROBE_PATH:",
    FFPROBE_PATH
)

print("==========================================")
