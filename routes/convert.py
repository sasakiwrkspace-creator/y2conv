# =====================================
# YouTube Converter
# routes/convert.py
#
# 役割:
# ・/convert の受付
# ・YouTube URLの受け取り
# ・converter_ytdlp.pyへMP3作成を依頼
# ・作成結果をJSONで返す
# =====================================

from flask import request, jsonify

from ytdlp import create_mp3


# =====================================
# Routes登録
# =====================================

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

            # =================================
            # JSON取得
            # =================================

            data = request.get_json(
                silent=True
            ) or {}

            url = data.get(
                "url"
            )

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

            # =================================
            # URL確認
            # =================================

            if not url:

                return jsonify({
                    "success": False,
                    "message":
                        "YouTube URLが指定されていません。"
                }), 400

            # =================================
            # MP3作成
            # =================================

            print(
                "[CONVERT] MP3作成開始"
            )

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
            # 結果確認
            # =================================

            if not result:

                return jsonify({
                    "success": False,
                    "message":
                        "MP3作成結果を取得できませんでした。"
                }), 500

            # =================================
            # JSON返却
            # =================================

            return jsonify({
                "success": True,
                "filename":
                    result["filename"]
            })

        except Exception as error:

            print("==========================================")

            print(
                "[CONVERT] エラー:",
                error
            )

            print("==========================================")

            return jsonify({
                "success": False,
                "message":
                    str(error)
            }), 500
