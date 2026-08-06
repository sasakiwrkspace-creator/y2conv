from flask import request, jsonify
import yt_dlp


def register_check(app):


    @app.route("/check", methods=["POST"])
    def check():

        try:

            data = request.get_json()

            url = data.get("url")


            if not url:

                return jsonify({
                    "success": False,
                    "message": "YouTube URLを入力してください"
                })



            ydl_opts = {

                "quiet": True,

                "no_warnings": True,

                "skip_download": True

            }



            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False
                )



            title = info.get(
                "title",
                "タイトル取得失敗"
            )


            duration_sec = info.get(
                "duration",
                0
            )


            hours = duration_sec // 3600

            minutes = (
                duration_sec % 3600
            ) // 60

            seconds = (
                duration_sec % 60
            )



            if hours > 0:

                duration = (
                    f"{hours}:"
                    f"{minutes:02}:"
                    f"{seconds:02}"
                )

            else:

                duration = (
                    f"{minutes}:"
                    f"{seconds:02}"
                )



            return jsonify({

                "success": True,

                "filename": title,

                "duration": duration

            })


        except Exception as e:


            print(
                "check error:",
                e
            )


            return jsonify({

                "success": False,

                "message": str(e)

            })