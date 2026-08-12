import os
import time

from paths import DOWNLOAD_DIR


# ==========================================================
# ファイル保持期間
#
# max_age=3600
# 1時間（3600秒）
#
# max_age=43200
# 12時間（43200秒）
#
# max_age=86400
# 24時間（86400秒）
# ==========================================================


def cleanup_downloads(
    max_age=86400
):

    # ======================================================
    # downloads確認
    # ======================================================

    if not os.path.exists(
        DOWNLOAD_DIR
    ):

        return


    # ======================================================
    # 現在時刻
    # ======================================================

    now = time.time()


    # ======================================================
    # downloads内を確認
    # ======================================================

    try:

        filenames = os.listdir(
            DOWNLOAD_DIR
        )

    except Exception as e:

        print(
            "downloads読み込み失敗:",
            repr(e)
        )

        return


    # ======================================================
    # 古いファイル削除
    # ======================================================

    for filename in filenames:

        filepath = os.path.join(
            DOWNLOAD_DIR,
            filename
        )


        # --------------------------------------------------
        # ファイルのみ対象
        # --------------------------------------------------

        if not os.path.isfile(
            filepath
        ):

            continue


        try:

            age = (
                now
                - os.path.getmtime(
                    filepath
                )
            )


        except Exception as e:

            print(
                "ファイル時刻取得失敗:",
                filepath,
                repr(e)
            )

            continue


        # ==================================================
        # 保持期間超過
        # ==================================================

        if age > max_age:

            try:

                os.remove(
                    filepath
                )

                print(
                    "古いファイル削除:",
                    filename
                )

            except Exception as e:

                print(
                    "削除失敗:",
                    filepath,
                    repr(e)
                )
