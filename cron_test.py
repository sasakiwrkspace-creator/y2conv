import os
from datetime import datetime, timezone


# Cron Jobの実行環境にあるdownloadsフォルダ
DOWNLOAD_DIR = "downloads"

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


# 現在時刻（UTC）
now = datetime.now(timezone.utc)


# 日本時間にしたい場合は9時間足す
from datetime import timedelta

jst = now + timedelta(hours=9)


# time.txtに書き込む
time_file = os.path.join(
    DOWNLOAD_DIR,
    "time.txt"
)


with open(
    time_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        jst.strftime("%Y-%m-%d %H:%M:%S")
    )


print(
    "Cron実行:",
    jst.strftime("%Y-%m-%d %H:%M:%S")
)

print(
    "ファイル:",
    time_file
)
