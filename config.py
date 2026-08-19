import os
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
# 音声分割設定
# =====================================

CHUNK_MINUTES = 15

CHUNK_SECONDS = CHUNK_MINUTES * 60


# =====================================
# 確認ログ
# =====================================

print("==========================================")
print("CONFIG")
print("BASE_DIR:", BASE_DIR)
print("DOWNLOAD_DIR:", DOWNLOAD_DIR)
print(
    "DOWNLOAD_DIR exists:",
    os.path.isdir(DOWNLOAD_DIR)
)
print("==========================================")
