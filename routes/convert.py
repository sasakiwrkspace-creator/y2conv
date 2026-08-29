from flask import request, jsonify

from ytdlp import create_mp3, create_mp4


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

            print(
                "[CONVERT] request data:",
                data,
                flush=True
            )

            url = data.get("url")

            start_time = data.get("start_time")
            end_time = data.get("end_time")

            # ★ ラジオボタンから送られる値
            # 例:
            # "mp3"
            # "mp4"
            output_type = data.get(
                "output_type",
                "mp3"
            )

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

            print(
                "[CONVERT] output_type:",
                output_type,
                flush=True
            )

            if not url:

                return jsonify({
                    "success": False,
                    "message": "YouTube URLが指定されていません。"
                }), 400

            # ==========================================
            # MP3
            # ==========================================

            if output_type == "mp3":

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

            # ==========================================
            # MP4
            # ==========================================

            elif output_type == "mp4":

                print(
                    "[CONVERT] MP4作成開始",
                    flush=True
                )

                result = create_mp4(
                    url
                )

                print(
                    "[CONVERT] MP4作成完了:",
                    result,
                    flush=True
                )

            else:

                print(
                    "[CONVERT] 未対応のoutput_type:",
                    output_type,
                    flush=True
                )

                return jsonify({
                    "success": False,
                    "message": (
                        "未対応の出力形式です: "
                        + str(output_type)
                    )
                }), 400

            # ==========================================
            # 結果確認
            # ==========================================

            if not result:

                print(
                    "[CONVERT] 結果が空です",
                    flush=True
                )

                return jsonify({
                    "success": False,
                    "message": "ファイル作成結果を取得できませんでした。"
                }), 500

            print(
                "[CONVERT] result:",
                repr(result),
                flush=True
            )

            print(
                "[CONVERT] result type:",
                type(result).__name__,
                flush=True
            )

            # ==========================================
            # ファイルパスをそのまま返す
            # ==========================================

            return jsonify({
                "success": True,
                "filename": result
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
                "[CONVERT] exception type:",
                type(error).__name__,
                flush=True
            )

            import traceback

            traceback.print_exc()

            print(
                "==========================================",
                flush=True
            )

            return jsonify({
                "success": False,
                "message": str(error)
            }), 500
