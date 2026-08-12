from dotenv import load_dotenv
import os
import shutil
import tempfile
import subprocess

from flask import request, jsonify
from google import genai


# =====================================
# Gemini API設定
# =====================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY が設定されていません"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =====================================
# プロジェクト
# =====================================

DOWNLOAD_DIR = "downloads"


# =====================================
# 時間文字列を秒へ変換
#
# 0:15
# 00:15
# 1:02:30
# などに対応
# =====================================

def time_to_seconds(time_string):

    if time_string is None:
        return None

    time_string = str(
        time_string
    ).strip()

    if not time_string:
        return None

    try:

        parts = time_string.split(":")

        if len(parts) == 2:

            minutes = int(parts[0])
            seconds = int(parts[1])

            return (
                minutes * 60
                + seconds
            )

        if len(parts) == 3:

            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])

            return (
                hours * 3600
                + minutes * 60
                + seconds
            )

        raise ValueError(
            "時間形式が正しくありません"
        )

    except Exception as e:

        raise ValueError(
            f"時間指定が不正です: "
            f"{time_string}"
        ) from e


# =====================================
# 時間指定が変更されたか確認
# =====================================

def is_time_changed(
    original_start_time,
    original_end_time,
    current_start_time,
    current_end_time
):

    original_start = time_to_seconds(
        original_start_time
    )

    original_end = time_to_seconds(
        original_end_time
    )

    current_start = time_to_seconds(
        current_start_time
    )

    current_end = time_to_seconds(
        current_end_time
    )

    return (
        original_start != current_start
        or
        original_end != current_end
    )


# =====================================
# MP3をffmpegでカット
# =====================================

def cut_mp3_for_gemini(
    mp3_path,
    start_time,
    end_time
):

    print(
        "=========================================="
    )
    print(
        "Gemini用MP3カット開始"
    )
    print(
        "元MP3:",
        mp3_path
    )
    print(
        "開始:",
        start_time
    )
    print(
        "終了:",
        end_time
    )
    print(
        "=========================================="
    )

    if not os.path.exists(
        mp3_path
    ):

        raise FileNotFoundError(
            f"MP3がありません: {mp3_path}"
        )


    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )


    if start_seconds is None:
        raise ValueError(
            "開始時間がありません"
        )

    if end_seconds is None:
        raise ValueError(
            "終了時間がありません"
        )

    if start_seconds < 0:
        raise ValueError(
            "開始時間は0以上にしてください"
        )

    if end_seconds <= start_seconds:
        raise ValueError(
            "終了時間は開始時間より後にしてください"
        )


    # =================================
    # 出力ファイル
    # =================================

    base_name = os.path.splitext(
        mp3_path
    )[0]

    cut_file = (
        base_name
        + "_gemini_cut.mp3"
    )


    # =================================
    # ffmpeg
    #
    # -ss
    # -to
    #
    # MP3なので再エンコードせず
    # 可能な限り軽量に処理
    # =================================

    command = [

        "ffmpeg",

        "-y",

        "-ss",
        str(start_time),

        "-to",
        str(end_time),

        "-i",
        mp3_path,

        "-vn",

        "-c:a",
        "copy",

        cut_file

    ]


    print(
        "ffmpeg command:",
        command
    )


    result = subprocess.run(

        command,

        stdout=subprocess.DEVNULL,

        stderr=subprocess.PIPE,

        text=True

    )


    if result.returncode != 0:

        print(
            result.stderr
        )

        raise Exception(
            "Gemini用MP3カット失敗"
        )


    if not os.path.exists(
        cut_file
    ):

        raise Exception(
            "カット後MP3が作成されませんでした"
        )


    file_size = os.path.getsize(
        cut_file
    )


    if file_size == 0:

        raise Exception(
            "カット後MP3が0 bytesです"
        )


    print(
        "=========================================="
    )
    print(
        "Gemini用MP3カット完了"
    )
    print(
        "ファイル:",
        cut_file
    )
    print(
        "サイズ:",
        file_size,
        "bytes"
    )
    print(
        "=========================================="
    )


    return cut_file


# =====================================
# GeminiへMP3送信
# =====================================

def transcribe_mp3(
    mp3_path
):

    mp3_path = os.path.abspath(
        mp3_path
    )


    if not os.path.exists(
        mp3_path
    ):

        raise FileNotFoundError(
            f"MP3がありません: {mp3_path}"
        )


    print(
        "=========================================="
    )
    print(
        "Gemini解析開始"
    )
    print(
        "MP3:",
        mp3_path
    )
    print(
        "=========================================="
    )


    # =================================
    # 日本語ファイル名対策
    # =================================

    temp_dir = tempfile.gettempdir()

    temp_mp3 = os.path.join(

        temp_dir,

        f"gemini_audio_{os.getpid()}.mp3"

    )


    try:

        shutil.copy2(

            mp3_path,

            temp_mp3

        )


        print(
            "Gemini upload:",
            temp_mp3
        )


        # =================================
        # Gemini Files API
        # =================================

        uploaded_file = client.files.upload(

            file=temp_mp3

        )


        print(
            "Gemini upload完了"
        )


        # =================================
        # プロンプト
        # =================================

        prompt = """

この音声ファイルを日本語で文字起こししてください。

SRT字幕ファイルとして使用します。

以下の形式で出力してください。

1
00:00:00,000 --> 00:00:05,000
字幕文章

2
00:00:05,000 --> 00:00:10,000
字幕文章

条件:

・日本語
・時間情報を付ける
・文章を省略しない
・要約しない
・説明文を書かない
・SRT形式のみ出力する
・Markdownのコードブロックは使用しない
・「```srt」などを付けない
"""


        # =================================
        # Gemini
        # =================================

        response = client.models.generate_content(

            model="gemini-3.5-flash",

            contents=[

                uploaded_file,

                prompt

            ]

        )


        if not response.text:

            raise Exception(
                "Gemini結果が空です"
            )


        print(
            "Gemini解析完了"
        )


        return response.text


    finally:

        # =================================
        # 一時MP3削除
        # =================================

        if os.path.exists(
            temp_mp3
        ):

            try:

                os.remove(
                    temp_mp3
                )

                print(
                    "Gemini一時MP3削除:",
                    temp_mp3
                )

            except Exception as e:

                print(
                    "WARNING: "
                    "Gemini一時MP3削除失敗:",
                    repr(e)
                )


# =====================================
# SRT保存
# =====================================

def save_srt(
    mp3_path,
    srt_text
):

    srt_path = (

        os.path.splitext(
            mp3_path
        )[0]

        + ".srt"

    )


    with open(

        srt_path,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(
            srt_text
        )


    print(
        "SRT保存:",
        srt_path
    )


    return srt_path


# =====================================
# Flask Route
#
# /gemini-transcribe
#
# ここで
#
# 1. 元MP3
# 2. 保存していた開始/終了
# 3. 現在の開始/終了
#
# を比較
#
# 変更あり
#   ↓
# ffmpegカット
#   ↓
# Gemini
#
# 変更なし
#   ↓
# 元MP3
#   ↓
# Gemini
# =====================================

def register_gemini(app):


    @app.route(
        "/gemini-transcribe",
        methods=["POST"]
    )

    def gemini_transcribe():

        try:

            # =================================
            # JSON
            # =================================

            data = request.get_json(
                silent=True
            )


            if not data:

                return jsonify({

                    "success": False,

                    "message":
                    "JSONデータがありません"

                }), 400


            # =================================
            # MP3ファイル名
            # =================================

            filename = data.get(
                "file"
            )


            if not filename:

                return jsonify({

                    "success": False,

                    "message":
                    "MP3ファイル名がありません"

                }), 400


            # =================================
            # パス
            # =================================

            mp3_path = os.path.join(

                DOWNLOAD_DIR,

                filename

            )


            mp3_path = os.path.abspath(
                mp3_path
            )


            # =================================
            # パストラバーサル対策
            # =================================

            download_root = os.path.abspath(
                DOWNLOAD_DIR
            )


            if not mp3_path.startswith(
                download_root + os.sep
            ):

                return jsonify({

                    "success": False,

                    "message":
                    "不正なファイルパスです"

                }), 400


            if not os.path.exists(
                mp3_path
            ):

                return jsonify({

                    "success": False,

                    "message":
                    f"MP3がありません: {filename}"

                }), 404


            # =================================
            # 元の時間
            #
            # convert.pyで保存した値
            # =================================

            original_start_time = data.get(
                "original_start_time"
            )

            original_end_time = data.get(
                "original_end_time"
            )


            # =================================
            # 現在の時間
            #
            # ユーザーが画面で変更した値
            # =================================

            current_start_time = data.get(
                "start_time"
            )

            current_end_time = data.get(
                "end_time"
            )


            print(
                "=========================================="
            )
            print(
                "Gemini送信準備"
            )
            print(
                "MP3:",
                mp3_path
            )
            print(
                "元開始:",
                original_start_time
            )
            print(
                "元終了:",
                original_end_time
            )
            print(
                "現在開始:",
                current_start_time
            )
            print(
                "現在終了:",
                current_end_time
            )
            print(
                "=========================================="
            )


            # =================================
            # 時間変更判定
            # =================================

            time_changed = is_time_changed(

                original_start_time,

                original_end_time,

                current_start_time,

                current_end_time

            )


            print(
                "時間指定変更:",
                time_changed
            )


            # =================================
            # Geminiへ送るMP3
            # =================================

            gemini_mp3_path = mp3_path


            # =================================
            # 変更あり
            # =================================

            if time_changed:

                print(
                    "時間変更あり"
                )

                print(
                    "→ ffmpegでMP3をカット"
                )


                gemini_mp3_path = cut_mp3_for_gemini(

                    mp3_path,

                    current_start_time,

                    current_end_time

                )


            # =================================
            # 変更なし
            # =================================

            else:

                print(
                    "時間変更なし"
                )

                print(
                    "→ 元MP3をそのままGeminiへ送信"
                )


            # =================================
            # Gemini
            # =================================

            srt_text = transcribe_mp3(

                gemini_mp3_path

            )


            # =================================
            # SRT
            #
            # カット版の場合は
            # カットMP3と同じ場所に保存
            # =================================

            srt_path = save_srt(

                gemini_mp3_path,

                srt_text

            )


            # =================================
            # 完了
            # =================================

            return jsonify({

                "success": True,

                "srt_file":
                os.path.basename(
                    srt_path
                ),

                "mp3_file":
                os.path.basename(
                    gemini_mp3_path
                ),

                "time_changed":
                time_changed,

                "text":
                "Gemini文字起こし完了"

            })


        except Exception as e:


            print(
                "=========================================="
            )

            print(
                "Gemini ERROR"
            )

            print(
                "TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                str(e)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success": False,

                "message":
                str(e)

            }), 500
