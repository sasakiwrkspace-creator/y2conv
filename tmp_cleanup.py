from flask import redirect
import os
import shutil


# ==========================================================
# 削除対象
# ==========================================================

TMP_DOWNLOAD_DIR = "/tmp/y2conv_downloads"


# ==========================================================
# /tmp/y2conv_downloads 一括削除
# ==========================================================

def register_tmp_cleanup(app):

    @app.route(
        "/tmp-cleanup",
        methods=["POST"]
    )
    def tmp_cleanup():

        print("==========================================")
        print("TMP一括削除")
        print("対象:", TMP_DOWNLOAD_DIR)
        print("==========================================")

        if not os.path.exists(
            TMP_DOWNLOAD_DIR
        ):

            print(
                "削除対象フォルダは存在しません"
            )

            return redirect("/files")


        try:

            shutil.rmtree(
                TMP_DOWNLOAD_DIR
            )

            print(
                "TMPフォルダ削除完了:",
                TMP_DOWNLOAD_DIR
            )

        except Exception as e:

            print(
                "TMPフォルダ削除失敗:",
                repr(e)
            )

        return redirect("/files")
