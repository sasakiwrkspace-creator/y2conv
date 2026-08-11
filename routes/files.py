from flask import (
    render_template,
    send_from_directory,
    redirect,
    request
)

import os
import shutil


# ==========================================================
# プロジェクトルート
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==========================================================
# downloads
# ==========================================================

DOWNLOAD_DIR = os.path.join(
    BASE_DIR,
    "downloads"
)


# ==========================================================
# 古いtmpフォルダ
#
# 以前使用していたフォルダ
# /tmp/y2conv_downloads
# ==========================================================

TMP_DOWNLOAD_DIR = "/tmp/y2conv_downloads"


# ==========================================================
# 4桁番号
# ==========================================================

FILE_PASSWORD = "1234"


# ==========================================================
# ファイル管理
# ==========================================================

def register_files(app):


    # ======================================================
    # ファイル一覧
    # ======================================================

    @app.route(
        "/files",
        methods=["GET", "POST"]
    )
    def list_files():


        # ==================================================
        # パスワード確認
        # ==================================================

        if request.method == "POST":


            password = request.form.get(
                "password",
                ""
            )


            if password == FILE_PASSWORD:


                os.makedirs(
                    DOWNLOAD_DIR,
                    exist_ok=True
                )


                items = []


                # ------------------------------------------
                # downloads一覧
                # ------------------------------------------

                for name in sorted(
                    os.listdir(DOWNLOAD_DIR)
                ):


                    path = os.path.join(
                        DOWNLOAD_DIR,
                        name
                    )


                    if os.path.isfile(path):

                        items.append({

                            "name": name,

                            "type": "file",

                            "size":
                                os.path.getsize(path)

                        })


                    elif os.path.isdir(path):

                        items.append({

                            "name": name,

                            "type": "folder",

                            "size": None

                        })


                # ------------------------------------------
                # tmpフォルダの存在確認
                # ------------------------------------------

                tmp_exists = os.path.exists(
                    TMP_DOWNLOAD_DIR
                )


                tmp_items = []


                if tmp_exists:

                    try:

                        for name in sorted(
                            os.listdir(
                                TMP_DOWNLOAD_DIR
                            )
                        ):

                            path = os.path.join(
                                TMP_DOWNLOAD_DIR,
                                name
                            )


                            if os.path.isfile(path):

                                tmp_items.append({

                                    "name": name,

                                    "type": "file",

                                    "size":
                                        os.path.getsize(path)

                                })


                            elif os.path.isdir(path):

                                tmp_items.append({

                                    "name": name,

                                    "type": "folder",

                                    "size": None

                                })


                    except Exception as e:

                        print(
                            "tmpフォルダ一覧取得失敗:",
                            repr(e)
                        )


                return render_template(

                    "files.html",

                    items=items,

                    tmp_exists=tmp_exists,

                    tmp_items=tmp_items

                )


        # ==================================================
        # パスワード入力画面
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
        inputmode="numeric"
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


    # ======================================================
    # downloads
    #
    # 選択したファイル・フォルダを削除
    # ======================================================

    @app.route(
        "/delete-selected",
        methods=["POST"]
    )
    def delete_selected():


        selected_items = request.form.getlist(
            "selected"
        )


        print(
            "downloads削除対象:",
            selected_items
        )


        if not selected_items:

            return redirect(
                "/files"
            )


        for name in selected_items:


            # ------------------------------------------
            # セキュリティ対策
            # ------------------------------------------

            safe_name = os.path.basename(
                name
            )


            path = os.path.join(

                DOWNLOAD_DIR,

                safe_name

            )


            # ------------------------------------------
            # ファイル
            # ------------------------------------------

            if os.path.isfile(path):

                try:

                    os.remove(path)

                    print(
                        "ファイル削除:",
                        path
                    )

                except Exception as e:

                    print(
                        "ファイル削除失敗:",
                        path,
                        repr(e)
                    )


            # ------------------------------------------
            # フォルダ
            # ------------------------------------------

            elif os.path.isdir(path):

                try:

                    shutil.rmtree(path)

                    print(
                        "フォルダ削除:",
                        path
                    )

                except Exception as e:

                    print(
                        "フォルダ削除失敗:",
                        path,
                        repr(e)
                    )


        return redirect(
            "/files"
        )


    # ======================================================
    # 古いtmpフォルダを完全削除
    #
    # /tmp/y2conv_downloads
    # ======================================================

    @app.route(
        "/delete-tmp-downloads",
        methods=["POST"]
    )
    def delete_tmp_downloads():


        print(
            "tmp/y2conv_downloads削除要求"
        )


        # ----------------------------------------------
        # 存在確認
        # ----------------------------------------------

        if not os.path.exists(
            TMP_DOWNLOAD_DIR
        ):

            print(
                "tmpフォルダは存在しません"
            )

            return redirect(
                "/files"
            )


        # ----------------------------------------------
        # 完全削除
        # ----------------------------------------------

        try:

            shutil.rmtree(
                TMP_DOWNLOAD_DIR
            )


            print(
                "tmpフォルダ完全削除:",
                TMP_DOWNLOAD_DIR
            )


        except Exception as e:

            print(
                "tmpフォルダ削除失敗:",
                repr(e)
            )


        return redirect(
            "/files"
        )
