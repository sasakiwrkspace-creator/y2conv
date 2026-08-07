from flask import (
    render_template,
    send_from_directory,
    redirect,
    request
)

import os


DOWNLOAD_DIR = "downloads"

# 4桁番号
FILE_PASSWORD = "1234"


def register_files(app):


    # ==========================
    # ファイル一覧
    # ==========================

    @app.route(
        "/files",
        methods=["GET", "POST"]
    )
    def list_files():


        # 4桁チェック
        if request.method == "POST":


            password = request.form.get(
                "password"
            )


            if password == FILE_PASSWORD:


                if not os.path.exists(
                    DOWNLOAD_DIR
                ):

                    files = []

                else:

                    files = os.listdir(
                        DOWNLOAD_DIR
                    )


                return render_template(
                    "files.html",
                    files=files
                )


        # 毎回表示する入力画面

        return """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <title>File Check</title>
        </head>

        <body>

        <h3>
        ファイル管理
        </h3>


        <form method="post">


        <p>
        4桁番号を入力してください
        </p>


        <input
        type="password"
        name="password"
        maxlength="4"
        autofocus
        >


        <button type="submit">
        確認
        </button>


        </form>


        </body>
        </html>
        """



    # ==========================
    # ダウンロード
    # ==========================

    @app.route(
        "/download/<filename>"
    )
    def download_file(filename):


        return send_from_directory(
            DOWNLOAD_DIR,
            filename,
            as_attachment=True
        )



    # ==========================
    # 削除
    # ==========================

    @app.route(
        "/delete/<filename>",
        methods=["POST"]
    )
    def delete_file(filename):


        filepath = os.path.join(
            DOWNLOAD_DIR,
            filename
        )


        if os.path.exists(filepath):

            os.remove(
                filepath
            )


        return redirect(
            "/files"
        )
