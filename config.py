import os
from dotenv import load_dotenv


load_dotenv()


DOWNLOAD_DIR = "downloads"


# Gemini API

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)


# 音声分割設定

CHUNK_MINUTES = 15

CHUNK_SECONDS = CHUNK_MINUTES * 60