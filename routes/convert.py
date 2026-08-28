from flask import request, jsonify
import importlib.util
import os


# =====================================
# converter-ytdlp.py 読み込み
# =====================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CONVERTER_PATH = os.path.join(
    BASE_DIR,
    "converter-ytdlp.py"
)


spec = importlib.util.spec_from_file_location(
    "converter_ytdlp",
    CONVERTER_PATH
)

converter_ytdlp = importlib.util.module_from_spec(
    spec
)

spec.loader.exec_module(
    converter_ytdlp
)


# =====================================
# Route登録
# =====================================

def register_convert(app):

    @app.route(
        "/convert",
        methods=["POST"]
    )
    def convert():

        print("==========================================")
        print("[CONVERT] MP3変換受付")
        print("==========================================")

        # =================================
        # JSON取得
        # =================================

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "success": False,
                "message": "リクエストデータがありません。"
            }), 400

        # =================================
        # URL
        # =================================

        url = data.get(
            "url",
            ""
        )

        if not url:

            return jsonify({
                "success": False,
                "message": "YouTube URLを入力してください。"
            }), 400

        # =================================
        # 出力形式
        #
        # 今回はMP3のみ
        # =================================

        outputs = data.get(
            "outputs",
            ["mp3"]
        )

        if not isinstance(
            outputs,
            list
        ):

            return jsonify({
                "success": False,
                "message": "出力形式が不正です。"
            }), 400

        if "mp3" not in outputs:

            return jsonify({
                "success": False,
                "message": "現在はMP3変換のみ対応しています。"
            }), 400

        # =================================
        # 時間指定
        # =================================

        start_time = data.get(
            "start_time"
        )

        end_time = data.get(
            "end_time"
        )

        if not start_time:
            start_time = None

        if not end_time:
            end_time = None

        print(
            "[CONVERT] URL:",
            url
        )

        print(
            "[CONVERT] outputs:",
            outputs
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
        # MP3作成
        # =================================

        try:

            result = converter_ytdlp.create_mp3(
                url=url,
                start_time=start_time,
                end_time=end_time
            )

        except Exception as error:

            print(
                "[CONVERT] MP3変換エラー:",
                error
            )

            return jsonify({
                "success": False,
                "message": str(error)
            }), 500

        # =================================
        # 結果確認
        # =================================

        if not result:

            return jsonify({
                "success": False,
                "message": "MP3変換結果を取得できませんでした。"
            }), 500

        filename = result.get(
            "filename"
        )

        if not filename:

            return jsonify({
                "success": False,
                "message": "MP3ファイル名を取得できませんでした。"
            }), 500

        # =================================
        # 完了
        # =================================

        print("==========================================")
        print("[CONVERT] MP3変換完了")
        print("[CONVERT] filename:", filename)
        print("==========================================")

        return jsonify({

            "success": True,

            "message":
                "MP3の作成が完了しました。",

            "filename":
                filename,

            "file":
                filename

        })
