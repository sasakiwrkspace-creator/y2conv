# =====================================
# routes/download.py
# =====================================

import os

from flask import send_from_directory


def register_download(app):

    @app.route("/download/<path:filename>")
    def download(filename):

        # =================================
        # プロジェクトルート
        #
        # routes/download.py
        #        ↓
        # routes/
        #        ↓
        # プロジェクト/
        # =================================

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )


        # =================================
        # downloadsフォルダ
        # =================================

        download_folder = os.path.join(
            project_root,
            "downloads"
        )


        print("================================")
        print("DOWNLOAD")
        print("filename:", filename)
        print("download_folder:", download_folder)
        print(
            "folder exists:",
            os.path.isdir(download_folder)
        )


        # =================================
        # 実ファイル確認
        # =================================

        file_path = os.path.join(
            download_folder,
            filename
        )


        print(
            "file_path:",
            file_path
        )

        print(
            "file exists:",
            os.path.isfile(file_path)
        )

        print("================================")


        # =================================
        # ファイルが存在しない
        # =================================

        if not os.path.isfile(file_path):

            print(
                "DOWNLOAD ERROR: "
                "ファイルがありません"
            )

            return {
                "success": False,
                "message": "ファイルが見つかりません",
                "filename": filename
            }, 404


        # =================================
        # ダウンロード
        # =================================

        return send_from_directory(
            download_folder,
            filename,
            as_attachment=True
        )
