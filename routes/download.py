import os

from flask import send_from_directory


def register_download(app):

    @app.route("/download/<path:filename>")
    def download(filename):

        # =================================
        # Flaskアプリのルート
        # =================================

        download_folder = os.path.join(
            app.root_path,
            "downloads"
        )

        print("================================", flush=True)
        print("[DOWNLOAD] filename:", filename, flush=True)
        print(
            "[DOWNLOAD] app.root_path:",
            app.root_path,
            flush=True
        )
        print(
            "[DOWNLOAD] download_folder:",
            download_folder,
            flush=True
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
            "[DOWNLOAD] file_path:",
            file_path,
            flush=True
        )

        print(
            "[DOWNLOAD] file exists:",
            os.path.isfile(file_path),
            flush=True
        )

        if os.path.isfile(file_path):

            try:

                print(
                    "[DOWNLOAD] file size:",
                    os.path.getsize(file_path),
                    "bytes",
                    flush=True
                )

            except Exception:
                pass

        print("================================", flush=True)

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
