# =====================================
# YouTube Converter
# config.py
#
# プロジェクト全体の設定
# =====================================

import os

from dotenv import load_dotenv


# =====================================
# .env
# =====================================

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

# Render Secret File
RENDER_COOKIES_FILE = "/etc/secrets/cookies.txt"


# =====================================
# Cookieファイル決定
#
# 優先順位:
#
# 1. Render Secret File
# 2. 環境変数 COOKIES_FILE
# 3. BASE_DIR/cookies.txt
#
# =====================================

if os.path.isfile(
    RENDER_COOKIES_FILE
):

    COOKIES_FILE = (
        RENDER_COOKIES_FILE
    )

else:

    env_cookies_file = os.environ.get(
        "COOKIES_FILE"
    )

    if (
        env_cookies_file
        and
        os.path.isfile(
            env_cookies_file
        )
    ):

        COOKIES_FILE = (
            env_cookies_file
        )

    else:

        local_cookies_file = os.path.join(
            BASE_DIR,
            "cookies.txt"
        )

        COOKIES_FILE = (
            local_cookies_file
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
print("==========================================")

print(
    "BASE_DIR:",
    BASE_DIR
)

print(
    "DOWNLOAD_DIR:",
    DOWNLOAD_DIR
)

print(
    "DOWNLOAD_DIR exists:",
    os.path.isdir(
        DOWNLOAD_DIR
    )
)

print("------------------------------------------")

print(
    "RENDER_COOKIES_FILE:",
    RENDER_COOKIES_FILE
)

print(
    "RENDER_COOKIES_FILE exists:",
    os.path.isfile(
        RENDER_COOKIES_FILE
    )
)

print("------------------------------------------")

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

print("------------------------------------------")

print(
    "GEMINI_API_KEY exists:",
    bool(
        GEMINI_API_KEY
    )
)

print("==========================================")
