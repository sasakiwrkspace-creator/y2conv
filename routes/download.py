import os

from flask import send_from_directory


def register_download(app):

    @app.route("/download/<path:filename>")
    def download(filename):

        # =================================
        # プロジェクトルート
        # =================================

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )


        # =================================
        # downloads
        # =================================

        download_folder = os.path.join(
            base_dir,
            "downloads"
        )


        print("================================")
        print("DOWNLOAD")
        print("filename:", filename)
        print(
            "download_folder:",
            download_folder
        )


        # =================================
        # フォルダ作成
        # =================================

        os.makedirs(
            download_folder,
            exist_ok=True
        )


        # =================================
        # ファイル確認
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
        # ファイルなし
        # =================================

        if not os.path.isfile(file_path):

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
