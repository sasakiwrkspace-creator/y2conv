from flask import (
    render_template,
    send_from_directory,
    redirect,
    request,
    abort
)

import os


# ==========================================================
# downloads
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# routes/files.py の1つ上がプロジェクトルート
PROJECT_DIR = os.path.dirname(
    BASE_DIR
)

DOWNLOAD_DIR = os.path.join(
    PROJECT_DIR,
    "downloads"
)


# ==========================================================
# 4桁番号
# ==========================================================

FILE_PASSWORD = "1234"


# ==========================================================
# ファイル一覧
# ==========================================================

def register_files(app):

    @app.route(
        "/files",
        methods=["GET", "POST"]
    )
    def list_files():

        # ==================================================
        # 4桁チェック
        # ==================================================

        if request.method == "POST":

            password = request.form.get(
                "password"
            )

            if password == FILE_PASSWORD:

                # ------------------------------------------
                # downloads一覧
                # ------------------------------------------

                files = []

                if os.path.exists(
                    DOWNLOAD_DIR
                ):

                    files = sorted(
                        os.listdir(
                            DOWNLOAD_DIR
                        )
                    )

                # ------------------------------------------
                # /tmp/y2conv_downloads一覧
                # ------------------------------------------

                tmp_dir = "/tmp/y2conv_downloads"

                tmp_files = []

                if os.path.exists(
                    tmp_dir
                ):

                    tmp_files = sorted(
                        os.listdir(
                            tmp_dir
                        )
                    )

                return render_template(
                    "files.html",
                    files=files,
                    tmp_files=tmp_files,
                    tmp_exists=os.path.exists(
                        tmp_dir
                    )
                )

        # ==================================================
        # 毎回表示する入力画面
        # ==================================================

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


    # ======================================================
    # ファイル削除確認
    # ======================================================

    @app.route(
        "/delete-confirm",
        methods=["POST"]
    )
    def delete_confirm():

        filename = request.form.get(
            "filename",
            ""
        ).strip()

        if not filename:

            return redirect(
                "/files"
            )

        # ----------------------------------------------
        # downloads/ を許可
        # ----------------------------------------------

        if filename.startswith(
            "downloads/"
        ):

            filename = filename[
                len("downloads/"):
            ]

        # ----------------------------------------------
        # パスを正規化
        # ----------------------------------------------

        requested_path = os.path.abspath(
            os.path.join(
                DOWNLOAD_DIR,
                filename
            )
        )

        download_root = os.path.abspath(
            DOWNLOAD_DIR
        )

        # ----------------------------------------------
        # downloadsの外を禁止
        # ----------------------------------------------

        try:

            if os.path.commonpath(
                [
                    requested_path,
                    download_root
                ]
            ) != download_root:

                return """
                <h3>削除できません</h3>
                <p>
                downloadsフォルダ内のファイルだけ削除できます。
                </p>
                <a href="/files">
                戻る
                </a>
                """

        except ValueError:

            return """
            <h3>削除できません</h3>
            <a href="/files">
            戻る
            </a>
            """

        # ----------------------------------------------
        # ファイル存在確認
        # ----------------------------------------------

        if not os.path.exists(
            requested_path
        ):

            return """
            <h3>ファイルがありません</h3>
            <a href="/files">
            戻る
            </a>
            """

        # ----------------------------------------------
        # フォルダ削除は禁止
        # ----------------------------------------------

        if not os.path.isfile(
            requested_path
        ):

            return """
            <h3>ファイルではありません</h3>
            <p>
            フォルダはこの画面から削除できません。
            </p>
            <a href="/files">
            戻る
            </a>
            """

        # ----------------------------------------------
        # 確認画面
        # ----------------------------------------------

        display_name = (
            "downloads/"
            + os.path.relpath(
                requested_path,
                download_root
            )
        )

        return render_template(
            "delete_confirm.html",
            filename=display_name
        )


    # ======================================================
    # ファイル削除実行
    # ======================================================

    @app.route(
        "/delete",
        methods=["POST"]
    )
    def delete_file():

        filename = request.form.get(
            "filename",
            ""
        ).strip()

        if not filename:

            return redirect(
                "/files"
            )

        # ----------------------------------------------
        # downloads/ を除去
        # ----------------------------------------------

        if filename.startswith(
            "downloads/"
        ):

            filename = filename[
                len("downloads/"):
            ]

        # ----------------------------------------------
        # パス作成
        # ----------------------------------------------

        filepath = os.path.abspath(
            os.path.join(
                DOWNLOAD_DIR,
                filename
            )
        )

        download_root = os.path.abspath(
            DOWNLOAD_DIR
        )

        # ----------------------------------------------
        # downloads外は禁止
        # ----------------------------------------------

        try:

            if os.path.commonpath(
                [
                    filepath,
                    download_root
                ]
            ) != download_root:

                return """
                <h3>削除できません</h3>
                <p>
                downloadsフォルダ外へのアクセスは禁止されています。
                </p>
                <a href="/files">
                戻る
                </a>
                """

        except ValueError:

            return """
            <h3>削除できません</h3>
            <a href="/files">
            戻る
            </a>
            """

        # ----------------------------------------------
        # ファイルだけ削除
        # ----------------------------------------------

        if os.path.isfile(
            filepath
        ):

            try:

                os.remove(
                    filepath
                )

                print(
                    "ファイル削除:",
                    filepath
                )

            except Exception as e:

                print(
                    "ファイル削除エラー:",
                    repr(e)
                )

        # ----------------------------------------------
        # filesへ戻る
        # ----------------------------------------------

        return redirect(
            "/files"
        )


    # ======================================================
    # ダウンロード
    # ======================================================

    @app.route(
        "/download/<path:filename>"
    )
    def download_file(filename):

        return send_from_directory(
            DOWNLOAD_DIR,
            filename,
            as_attachment=True
        )
