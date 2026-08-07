import os
import time


# ファイル保持期間
# max_age=3600   # 1時間（3600秒）
# max_age=43200  # 12時間（43200秒）
# max_age=86400  # 24時間（86400秒）
def cleanup_downloads(
    folder="downloads",
    max_age=86400  # 24時間（86400秒） 
):

    if not os.path.exists(folder):
        return


    now = time.time()


    for filename in os.listdir(folder):

        filepath = os.path.join(
            folder,
            filename
        )


        if os.path.isfile(filepath):

            age = now - os.path.getmtime(filepath)


            if age > max_age:

                try:

                    os.remove(filepath)

                    print(
                        "古いファイル削除:",
                        filename
                    )

                except Exception as e:

                    print(
                        "削除失敗:",
                        e
                    )
