from flask import request, jsonify
from converter_ytdlp import create_mp3

def register_convert(app):

@app.route(
    "/convert",
    methods=["POST"]
)
def convert():

    print("==========================================")
    print("[CONVERT] /convert 呼び出し")
    print("==========================================")

    try:

        data = request.get_json(
            silent=True
        ) or {}

        url = data.get("url")

        start_time = data.get(
            "start_time"
        )

        end_time = data.get(
            "end_time"
        )

        print(
            "[CONVERT] URL:",
            url
        )

        print(
            "[CONVERT] start_time:",
            start_time
        )

        print(
            "[CONVERT] end_time:",
            end_time
        )

        if not url:

            return jsonify({
                "success": False,
                "message":
                    "YouTube URLが指定されていません。"
            }), 400

        # =================================
        # MP3作成
        # =================================

        result = create_mp3(

            url,

            start_time=start_time,

            end_time=end_time

        )

        print(
            "[CONVERT] MP3作成完了:",
            result
        )

        # =================================
        # 結果
        # =================================

        return jsonify({

            "success": True,

            "filename":
                result["filename"]

        })

    except Exception as error:

        print(
            "[CONVERT] エラー:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500
