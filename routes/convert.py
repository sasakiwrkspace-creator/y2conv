from flask import request, jsonify

from ytdlp import create_mp3


def register_convert(app):

    @app.route(
        "/convert",
        methods=["POST"]
    )
    def convert():

        print("==========================================", flush=True)
        print("[CONVERT] /convert 呼び出し", flush=True)
        print("==========================================", flush=True)

        try:

            data = request.get_json(
                silent=True
            ) or {}

            url = data.get("url")

            start_time = data.get("start_time")
            end_time = data.get("end_time")

            print(
                "[CONVERT] URL:",
                url,
                flush=True
            )

            print(
                "[CONVERT] start_time:",
                start_time,
                flush=True
            )

            print(
                "[CONVERT] end_time:",
                end_time,
                flush=True
            )

            if not url:

                return jsonify({
                    "success": False,
                    "message": "YouTube URLが指定されていません。"
                }), 400

            print(
                "[CONVERT] MP3作成開始",
                flush=True
            )

            result = create_mp3(
                url,
                start_time=start_time,
                end_time=end_time
            )

            print(
                "[CONVERT] MP3作成完了:",
                result,
                flush=True
            )

            if not result:

                return jsonify({
                    "success": False,
                    "message": "MP3作成結果を取得できませんでした。"
                }), 500

            return jsonify({
                "success": True,
                "filename": result["filename"]
            })

        except Exception as error:

            print(
                "==========================================",
                flush=True
            )

            print(
                "[CONVERT] エラー:",
                repr(error),
                flush=True
            )

            print(
                "==========================================",
                flush=True
            )

            return jsonify({
                "success": False,
                "message": str(error)
            }), 500
