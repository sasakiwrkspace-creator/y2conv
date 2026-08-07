from flask import Flask

from routes.index import register_index
from routes.check import register_check
from routes.convert import register_convert
from routes.status import register_status
from routes.download import register_download
from routes.gemini import register_gemini
from routes.files import register_files

app = Flask(__name__)

app.secret_key = "y2conv-secret-key"

register_index(app)
register_check(app)
register_convert(app)
register_status(app)
register_download(app)
register_gemini(app)


if __name__ == "__main__":

    print("Flask起動します")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
    )


