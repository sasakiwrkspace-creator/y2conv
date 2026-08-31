import os

from flask import send_from_directory


# ==========================================================
# ダウンロードRoute
# ==========================================================

def register_download(app):

    @app.route(
        "/download/<path:filename>",
        methods=["GET"]
    )
    def download(filename):

        print(
            "==========================================",
            flush=True
        )

        print(
            "[DOWNLOAD] /download 呼び出し",
            flush=True
        )

        print(
            "[DOWNLOAD] filename:",
            filename,
            flush=True
        )

        print(
            "[DOWNLOAD] os.getcwd():",
            os.getcwd(),
            flush=True
        )

        print(
            "[DOWNLOAD] app.root_path:",
            app.root_path,
            flush=True
        )

        # ==================================================
        # downloadsフォルダ
        #
        # ytdlp.py と同じ
        # os.getcwd()/downloads
        # ==================================================

        download_folder = os.path.join(
            os.getcwd(),
            "downloads"
        )

        print(
            "[DOWNLOAD] download_folder:",
            download_folder,
            flush=True
        )

        # ==================================================
        # フォルダ作成
        # ==================================================

        os.makedirs(
            download_folder,
            exist_ok=True
        )

        # ==================================================
        # ファイル名確認
        # ==================================================

        if not filename:

            print(
                "[DOWNLOAD] filenameが空です",
                flush=True
            )

            return {

                "success":
                    False,

                "message":
                    "ファイル名が指定されていません。"

            }, 400

        # ==================================================
        # ファイルパス
        # ==================================================

        file_path = os.path.join(
            download_folder,
            filename
        )

        print(
            "[DOWNLOAD] file_path:",
            file_path,
            flush=True
        )

        # ==================================================
        # ファイル存在確認
        # ==================================================

        file_exists = os.path.isfile(
            file_path
        )

        print(
            "[DOWNLOAD] file exists:",
            file_exists,
            flush=True
        )

        # ==================================================
        # ファイルサイズ
        # ==================================================

        if file_exists:

            try:

                file_size = os.path.getsize(
                    file_path
                )

                print(
                    "[DOWNLOAD] file size:",
                    file_size,
                    "bytes",
                    flush=True
                )

                if file_size <= 0:

                    print(
                        "[DOWNLOAD] ファイルサイズが0です",
                        flush=True
                    )

                    return {

                        "success":
                            False,

                        "message":
                            "ファイルサイズが0です。",

                        "filename":
                            filename

                    }, 404

            except Exception as error:

                print(
                    "[DOWNLOAD] サイズ取得ERROR:",
                    repr(error),
                    flush=True
                )

        # ==================================================
        # ファイルなし
        # ==================================================

        if not file_exists:

            print(
                "[DOWNLOAD] ファイルが見つかりません",
                flush=True
            )

            print(
                "[DOWNLOAD] 探した場所:",
                file_path,
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            return {

                "success":
                    False,

                "message":
                    "ファイルが見つかりません",

                "filename":
                    filename

            }, 404

        # ==================================================
        # ダウンロード開始
        # ==================================================

        print(
            "[DOWNLOAD] ダウンロード開始:",
            filename,
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        return send_from_directory(

            directory=
                download_folder,

            path=
                filename,

            as_attachment=
                True

        )
