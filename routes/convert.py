from flask import request, jsonify

from ytdlp import create_mp3, create_mp4


# ==========================================================
# /convert
#
# YouTube Converter タブ1専用
#
# 受信:
# {
#     "url": "...",
#     "output_type": "mp3" または "mp4",
#     "start_time": 0,
#     "end_time": 120
# }
#
# start_time / end_time はMP3・MP4の両方に反映する
# ==========================================================

def register_convert(app):

    @app.route(
        "/convert",
        methods=["POST"]
    )
    def convert():

        print(
            "==========================================",
            flush=True
        )

        print(
            "[CONVERT] /convert 呼び出し",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        try:

            # ==================================================
            # JSON
            # ==================================================

            data = request.get_json(
                silent=True
            ) or {}

            print(
                "[CONVERT] request data:",
                data,
                flush=True
            )


            # ==================================================
            # URL
            # ==================================================

            url = data.get(
                "url"
            )


            # ==================================================
            # 開始時間
            # ==================================================

            start_time = data.get(
                "start_time"
            )


            # ==================================================
            # 終了時間
            # ==================================================

            end_time = data.get(
                "end_time"
            )


            # ==================================================
            # 出力形式
            #
            # converter.js から
            # output_type を受け取る
            # ==================================================

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


            # ==================================================
            # URL確認
            # ==================================================

            if not url:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "YouTube URLが指定されていません。"

                }), 400


            # ==================================================
            # 時間値確認
            # ==================================================

            if start_time is not None:

                try:

                    start_time = int(
                        start_time
                    )

                except Exception:

                    return jsonify({

                        "success":
                        False,

                        "message":
                        "開始時間が正しくありません。"

                    }), 400


                if start_time < 0:

                    return jsonify({

                        "success":
                        False,

                        "message":
                        "開始時間は0秒以上で指定してください。"

                    }), 400


            if end_time is not None:

                try:

                    end_time = int(
                        end_time
                    )

                except Exception:

                    return jsonify({

                        "success":
                        False,

                        "message":
                        "終了時間が正しくありません。"

                    }), 400


                if end_time <= 0:

                    return jsonify({

                        "success":
                        False,

                        "message":
                        "終了時間は0秒より大きくしてください。"

                    }), 400


            # ==================================================
            # 開始・終了チェック
            # ==================================================

            if (
                start_time is not None
                and end_time is not None
            ):

                if end_time <= start_time:

                    return jsonify({

                        "success":
                        False,

                        "message":
                        "終了時間は開始時間より後にしてください。"

                    }), 400


            # ==================================================
            # MP3
            # ==================================================

            if output_type == "mp3":

                print(
                    "==========================================",
                    flush=True
                )

                print(
                    "[CONVERT] MP3作成開始",
                    flush=True
                )

                print(
                    "[CONVERT] 開始:",
                    start_time,
                    flush=True
                )

                print(
                    "[CONVERT] 終了:",
                    end_time,
                    flush=True
                )

                print(
                    "==========================================",
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


            # ==================================================
            # MP4
            # ==================================================

            elif output_type == "mp4":

                print(
                    "==========================================",
                    flush=True
                )

                print(
                    "[CONVERT] MP4作成開始",
                    flush=True
                )

                print(
                    "[CONVERT] 開始:",
                    start_time,
                    flush=True
                )

                print(
                    "[CONVERT] 終了:",
                    end_time,
                    flush=True
                )

                print(
                    "==========================================",
                    flush=True
                )


                # ★重要
                #
                # MP4にも開始・終了時間を渡す
                #

                result = create_mp4(

                    url,

                    start_time=start_time,

                    end_time=end_time

                )


                print(
                    "[CONVERT] MP4作成完了:",
                    result,
                    flush=True
                )


            # ==================================================
            # 未対応
            # ==================================================

            else:

                print(
                    "[CONVERT] 未対応のoutput_type:",
                    output_type,
                    flush=True
                )


                return jsonify({

                    "success":
                    False,

                    "message":
                    (
                        "未対応の出力形式です: "
                        + str(output_type)
                    )

                }), 400


            # ==================================================
            # 結果確認
            # ==================================================

            if not result:

                print(
                    "[CONVERT] 結果が空です",
                    flush=True
                )


                return jsonify({

                    "success":
                    False,

                    "message":
                    "ファイル作成結果を取得できませんでした。"

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


            # ==================================================
            # 成功
            # ==================================================

            return jsonify({

                "success":
                True,

                "filename":
                result,

                "output_type":
                output_type,

                "start_time":
                start_time,

                "end_time":
                end_time

            })


        # ======================================================
        # エラー
        # ======================================================

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

                "success":
                False,

                "message":
                str(error)

            }), 500
