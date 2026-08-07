import os
import time


DOWNLOAD_DIR = "downloads"

MAX_AGE = 86400  # 24時間


def cleanup():

    now = time.time()


    if not os.path.exists(DOWNLOAD_DIR):
        return


    for filename in os.listdir(DOWNLOAD_DIR):

        filepath = os.path.join(
            DOWNLOAD_DIR,
            filename
        )


        if os.path.isfile(filepath):

            age = now - os.path.getmtime(filepath)


            if age > MAX_AGE:

                os.remove(filepath)

                print(
                    "削除:",
                    filename
                )


if __name__ == "__main__":
    cleanup()
