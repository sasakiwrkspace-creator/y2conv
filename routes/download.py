import os

from flask import send_from_directory


def register_download(app):

    @app.route("/download/<path:filename>")
    def download(filename):

        download_folder = os.path.join(
            os.getcwd(),
            "downloads"
        )


        return send_from_directory(
            download_folder,
            filename,
            as_attachment=True
        )