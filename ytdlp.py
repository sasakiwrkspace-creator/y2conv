import os
import shutil
import tempfile
from pathlib import Path

import yt_dlp

from config import (
DOWNLOAD_DIR,
COOKIES_FILE,
)

============================================================
環境設定
============================================================

DENO_PATH = "/root/.deno/bin/deno"

DOWNLOAD_PATH = Path(DOWNLOAD_DIR)
COOKIES_PATH = Path(COOKIES_FILE)

print("==========================================")
print("[YTDLP] 設定")
print("[YTDLP] DOWNLOAD_DIR:", DOWNLOAD_DIR)
print("[YTDLP] COOKIES_FILE:", COOKIES_FILE)
print("[YTDLP] cookies exists:", COOKIES_PATH.is_file())
print("[YTDLP] Deno:", DENO_PATH)
print("[YTDLP] Deno exists:", os.path.isfile(DENO_PATH))
print("==========================================")

============================================================
Denoの確認
============================================================

def check_deno():
"""
Denoが存在するか確認する。
DenoそのもののインストールはDockerfileで行う。
"""

if not os.path.isfile(DENO_PATH):
    print("[YTDLP] WARNING: Denoが見つかりません")
    return False

if not os.access(DENO_PATH, os.X_OK):
    print("[YTDLP] WARNING: Denoに実行権限がありません")
    return False

print("[YTDLP] Deno OK:", DENO_PATH)
return True

============================================================
Cookie一時ファイル作成
============================================================

def create_temp_cookie_file():
"""
Render Secret File:
/etc/secrets/cookies.txt

を一時ファイルへコピーする。

yt-dlp終了後に必ず削除する。
"""

if not COOKIES_PATH.is_file():
    print("[YTDLP] Cookieファイルがありません:", COOKIES_FILE)
    return None

temp_path = None

try:
    fd, temp_path = tempfile.mkstemp(
        prefix="y2conv_cookies_",
        suffix=".txt",
    )

    os.close(fd)

    shutil.copyfile(
        str(COOKIES_PATH),
        temp_path,
    )

    os.chmod(
        temp_path,
        0o600,
    )

    print("[YTDLP] 一時Cookie作成:", temp_path)
    print(
        "[YTDLP] 一時Cookieサイズ:",
        os.path.getsize(temp_path),
    )

    return temp_path

except Exception as e:
    print("[YTDLP] Cookie一時ファイル作成失敗:", repr(e))

    if temp_path and os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass

    return None

============================================================
時間指定
============================================================

def time_to_seconds(value):
"""
00:00:10
00:01:30
01:02:03

などを秒へ変換する。
"""

if value is None:
    return None

if isinstance(value, (int, float)):
    return float(value)

value = str(value).strip()

if not value:
    return None

try:
    parts = value.split(":")

    if len(parts) == 1:
        return float(parts[0])

    if len(parts) == 2:
        minutes = float(parts[0])
        seconds = float(parts[1])

        return minutes * 60 + seconds

    if len(parts) == 3:
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])

        return hours * 3600 + minutes * 60 + seconds

except Exception:
    pass

return None

============================================================
yt-dlpオプション作成
============================================================

def build_ydl_options(
cookie_file=None,
start_time=None,
end_time=None,
):
"""
yt-dlpの設定を作成する。
"""

options = {
    # 音声取得
    "format": "bestaudio/best",

    # 出力先
    "outtmpl": str(
        DOWNLOAD_PATH / "%(id)s.%(ext)s"
    ),

    # FFmpegでMP3化
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],

    # HTTPS / YouTube対策
    "nocheckcertificate": True,

    # ログ
    "quiet": False,
    "no_warnings": False,

    # プレイリストではなく指定動画のみ
    "noplaylist": True,

    # リトライ
    "retries": 5,
    "fragment_retries": 5,

    # タイムアウト
    "socket_timeout": 30,

    # EJS
    "js_runtimes": {
        "deno": {
            "path": DENO_PATH,
        }
    },

    # YouTubeクライアント
    "extractor_args": {
        "youtube": {
            "player_client": [
                "web",
                "web_safari",
                "android",
            ],
        }
    },
}

# --------------------------------------------------------
# Cookie
# --------------------------------------------------------

if cookie_file:
    options["cookiefile"] = cookie_file
    print("[YTDLP] cookiefile:", cookie_file)
else:
    print("[YTDLP] cookiefile: 使用なし")

# --------------------------------------------------------
# 時間範囲
# --------------------------------------------------------

start_seconds = time_to_seconds(start_time)
end_seconds = time_to_seconds(end_time)

print("[YTDLP] start_seconds:", start_seconds)
print("[YTDLP] end_seconds:", end_seconds)

if start_seconds is not None:
    options["download_ranges"] = yt_dlp.utils.download_range_func(
        None,
        start_time=start_seconds,
        end_time=end_seconds,
    )

    options["force_keyframes_at_cuts"] = True

elif end_seconds is not None:
    options["download_ranges"] = yt_dlp.utils.download_range_func(
        None,
        start_time=0,
        end_time=end_seconds,
    )

    options["force_keyframes_at_cuts"] = True

return options

============================================================
MP3作成
============================================================

def create_mp3(
url,
start_time=None,
end_time=None,
):
"""
YouTube URLからMP3を作成する。

戻り値:
    作成されたMP3ファイルのパス
"""

print("==========================================")
print("[YTDLP] MP3作成開始")
print("[YTDLP] URL:", url)
print("[YTDLP] start_time:", start_time)
print("[YTDLP] end_time:", end_time)
print("[YTDLP] DOWNLOAD_DIR:", DOWNLOAD_DIR)
print("[YTDLP] COOKIES_FILE:", COOKIES_FILE)
print("==========================================")

DOWNLOAD_PATH.mkdir(
    parents=True,
    exist_ok=True,
)

check_deno()

# --------------------------------------------------------
# Cookie一時ファイル
# --------------------------------------------------------

temp_cookie_file = create_temp_cookie_file()

try:
    # ----------------------------------------------------
    # yt-dlp設定
    # ----------------------------------------------------

    ydl_opts = build_ydl_options(
        cookie_file=temp_cookie_file,
        start_time=start_time,
        end_time=end_time,
    )

    print("==========================================")
    print("[YTDLP] yt-dlp実行")
    print("[YTDLP] version:", yt_dlp.version.__version__)
    print("[YTDLP] EJS: yt-dlp-ejsを使用")
    print("[YTDLP] Deno:", DENO_PATH)
    print("[YTDLP] Cookie:", bool(temp_cookie_file))
    print("==========================================")

    # ----------------------------------------------------
    # 情報取得
    # ----------------------------------------------------

    print("[YTDLP] YouTube情報取得開始")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            url,
            download=False,
        )

        print("[YTDLP] 情報取得成功")
        print("[YTDLP] title:", info.get("title"))
        print("[YTDLP] id:", info.get("id"))
        print("[YTDLP] extractor:", info.get("extractor"))

        # ------------------------------------------------
        # ダウンロード
        # ------------------------------------------------

        print("[YTDLP] ダウンロード開始")

        ydl.download([url])

    # ----------------------------------------------------
    # MP3検索
    # ----------------------------------------------------

    video_id = info.get("id")

    if video_id:
        candidates = [
            DOWNLOAD_PATH / f"{video_id}.mp3",
        ]
    else:
        candidates = []

    # 念のためディレクトリ内も検索
    if not candidates:
        candidates = list(
            DOWNLOAD_PATH.glob("*.mp3")
        )

    mp3_file = None

    for candidate in candidates:
        if candidate.is_file():
            mp3_file = candidate
            break

    if mp3_file is None:
        # 最終確認
        mp3_files = sorted(
            DOWNLOAD_PATH.glob("*.mp3"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if mp3_files:
            mp3_file = mp3_files[0]

    if mp3_file is None:
        raise RuntimeError(
            "MP3ファイルが作成されませんでした"
        )

    print("==========================================")
    print("[YTDLP] MP3作成成功")
    print("[YTDLP] file:", str(mp3_file))
    print("[YTDLP] size:", mp3_file.stat().st_size)
    print("==========================================")

    return str(mp3_file)

finally:
    # ----------------------------------------------------
    # 一時Cookie削除
    # ----------------------------------------------------

    if temp_cookie_file:
        try:
            if os.path.exists(temp_cookie_file):
                os.remove(temp_cookie_file)
                print(
                    "[YTDLP] 一時Cookie削除:",
                    temp_cookie_file,
                )
        except Exception as e:
            print(
                "[YTDLP] 一時Cookie削除失敗:",
                repr(e),
            )

============================================================
互換用関数
============================================================

def download_mp3(
url,
start_time=None,
end_time=None,
):
"""
既存コードがdownload_mp3()を呼んでいる場合の互換用。
"""

return create_mp3(
    url=url,
    start_time=start_time,
    end_time=end_time,
)


def convert_to_mp3(
url,
start_time=None,
end_time=None,
):
"""
既存コードがconvert_to_mp3()を呼んでいる場合の互換用。
"""

return create_mp3(
    url=url,
    start_time=start_time,
    end_time=end_time,
)

============================================================
直接実行時のテスト
============================================================

if name == "main":

print("==========================================")
print("[YTDLP] TEST MODE")
print("==========================================")

print("Python:", os.sys.version)
print("yt-dlp:", yt_dlp.version.__version__)
print("Deno:", DENO_PATH)
print("Deno exists:", os.path.isfile(DENO_PATH))
print("Cookie:", COOKIES_FILE)
print("Cookie exists:", COOKIES_PATH.is_file())

print("==========================================")
print("[YTDLP] TEST END")
print("==========================================")
