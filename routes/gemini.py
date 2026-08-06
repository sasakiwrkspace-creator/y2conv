from dotenv import load_dotenv
import os
import shutil
import tempfile

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


print(
    "GEMINI KEY:",
    GEMINI_API_KEY[:10]
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)



# =====================================
# MP3 → Gemini → SRT
# =====================================

def transcribe_mp3(mp3_path):

    mp3_path = os.path.abspath(
        mp3_path
    )


    if not os.path.exists(mp3_path):

        raise FileNotFoundError(
            f"MP3がありません: {mp3_path}"
        )


    print(
        "Gemini解析開始:",
        mp3_path
    )


    # =================================
    # 日本語ファイル名対策
    # 一時ファイル作成
    # =================================

    temp_dir = tempfile.gettempdir()

    temp_mp3 = os.path.join(
        temp_dir,
        f"gemini_audio_{os.getpid()}.mp3"
    )


    shutil.copy2(
        mp3_path,
        temp_mp3
    )


    print(
        "Gemini upload:",
        temp_mp3
    )


    uploaded_file = client.files.upload(
        file=temp_mp3
    )


    prompt = """
この音声ファイルを日本語で文字起こししてください。

SRT字幕ファイルとして使用します。

以下の形式で出力してください。

1
00:00:00,000 --> 00:00:05,000
字幕文章


条件:

・日本語
・時間情報を付ける
・文章を省略しない
・要約しない
・説明文を書かない
・SRT形式のみ出力する
"""

    #   model="gemini-2.5-flash", #2026.08.06以前

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


    return response.text




# =====================================
# Flask Route
# =====================================

def register_gemini(app):


    @app.route(
        "/gemini-transcribe",
        methods=["POST"]
    )
    def gemini_transcribe():

        try:

            data = request.get_json()


            if not data:

                return jsonify({

                    "success": False,

                    "message":
                    "JSONデータがありません"

                }), 400



            filename = data.get(
                "file"
            )


            if not filename:

                return jsonify({

                    "success": False,

                    "message":
                    "MP3ファイル名がありません"

                }), 400



            mp3_path = os.path.join(

                "downloads",

                filename

            )


            srt_text = transcribe_mp3(
                mp3_path
            )


            srt_path = os.path.splitext(
                mp3_path
            )[0] + ".srt"



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



            return jsonify({

                "success": True,

                "srt_file":
                os.path.basename(srt_path),

                "text":
                "SRT作成完了"

            })


        except Exception as e:


            print(
                "Gemini ERROR:",
                type(e).__name__,
                str(e)
            )


            return jsonify({

                "success": False,

                "message":
                str(e)

            }), 500