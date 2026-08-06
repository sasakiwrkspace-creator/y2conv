from flask import request, jsonify
import yt_dlp
import uuid
import threading
import os

from routes.status import jobs



def convert_task(job_id, url, outputs):

    try:

        print("変換開始:", job_id)


        jobs[job_id] = {

            "status": "running"

        }


        output_dir = "downloads"


        os.makedirs(
            output_dir,
            exist_ok=True
        )


        files = []



        # ==========================
        # mp3作成
        # ==========================

        if "mp3" in outputs:


            print("mp3変換開始")


            ydl_opts = {

                "format":
                "bestaudio/best",


                "outtmpl":
                f"{output_dir}/%(title)s.%(ext)s",


                "postprocessors": [

                    {

                        "key":
                        "FFmpegExtractAudio",


                        "preferredcodec":
                        "mp3",


                        "preferredquality":
                        "192"

                    }

                ]

            }



            with yt_dlp.YoutubeDL(ydl_opts) as ydl:


                info = ydl.extract_info(

                    url,

                    download=True

                )



            files.append(

                info["title"] + ".mp3"

            )



            print("mp3完成")




        # ==========================
        # mp4作成
        # ==========================

        if "mp4" in outputs:


            print("mp4変換開始")


            ydl_opts = {


                "format":
                "bestvideo+bestaudio/best",


                "outtmpl":
                f"{output_dir}/%(title)s.%(ext)s"

            }



            with yt_dlp.YoutubeDL(ydl_opts) as ydl:


                info = ydl.extract_info(

                    url,

                    download=True

                )



            files.append(

                info["title"] + ".mp4"

            )



            print("mp4完成")





        # ==========================
        # 完了
        # ==========================

        jobs[job_id] = {


            "status":
            "complete",


            "files":
            files

        }


        print(
            "変換完了:",
            files
        )



    except Exception as e:


        print(
            "変換エラー:",
            e
        )


        jobs[job_id] = {


            "status":
            "error",


            "message":
            str(e)

        }





def register_convert(app):


    @app.route(
        "/convert",
        methods=["POST"]
    )

    def convert():


        try:


            data = request.get_json()



            url = data.get(
                "url"
            )


            outputs = data.get(
                "outputs",
                []
            )



            if not url:


                return jsonify({

                    "success":
                    False,


                    "message":
                    "URLがありません"

                })



            job_id = str(
                uuid.uuid4()
            )



            thread = threading.Thread(

                target=convert_task,

                args=(

                    job_id,

                    url,

                    outputs

                )

            )



            thread.start()



            return jsonify({

                "success":
                True,


                "job_id":
                job_id

            })



        except Exception as e:


            return jsonify({

                "success":
                False,


                "message":
                str(e)

            })