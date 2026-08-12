import os


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


# =====================================
# なければ作成
# =====================================

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


print("==========================================")
print("PATH設定")
print("BASE_DIR:", BASE_DIR)
print("DOWNLOAD_DIR:", DOWNLOAD_DIR)
print(
    "DOWNLOAD_DIR exists:",
    os.path.isdir(DOWNLOAD_DIR)
)
print("==========================================")
