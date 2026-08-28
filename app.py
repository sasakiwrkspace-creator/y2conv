import os

from flask import Flask

from routes.index import register_index
from routes.check import register_check, register_video_info
from routes.convert import register_convert
from routes.status import register_status
from routes.download import register_download
from routes.gemini import register_gemini
from routes.files import register_files
from routes.sub_embed_routes import register_sub_embed


app = Flask(__name__)

app.secret_key = "y2conv-secret-key"


# =====================================
# downloadsフォルダ
# =====================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DOWNLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "downloads"
)

os.makedirs(
    DOWNLOAD_FOLDER,
    exist_ok=True
)


print("================================")
print("DOWNLOAD FOLDER")
print(DOWNLOAD_FOLDER)
print(
    "exists:",
    os.path.isdir(DOWNLOAD_FOLDER)
)
print("================================")


# =====================================
# Routes
# =====================================

register_index(app)
register_check(app)
register_video_info(app)
register_convert(app)
register_status(app)
register_download(app)
register_gemini(app)
register_files(app)
register_sub_embed(app)

# =====================================
# 起動
# =====================================

if __name__ == "__main__":

    print("Flask起動します")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
    )
