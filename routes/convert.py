from flask import request, jsonify
import yt_dlp
import uuid
import threading
import os
import subprocess

from routes.status import jobs
from cleanup import cleanup_downloads


def convert_task(
    job_id,
    url,
    outputs,
    start_time=None,
    end_time=None
):

    try:

        # 24時間以上経過したファイルを削除
        cleanup_downloads()


        print("変換開始:", job_id)


        jobs[job_id] = {

            "status":
            "running"

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

                "noplaylist":
                True,

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


                filename = ydl.prepare_filename(

                    info

                )



            mp3_file = os.path.splitext(

                filename

            )[0] + ".mp3"



            # 時間指定カット

            if start_time and end_time and start_time < end_time:


                cut_file = os.path.splitext(

                    mp3_file

                )[0] + "_cut.mp3"



                result = subprocess.run([

                    "ffmpeg",

                    "-y",

                    "-i",

                    mp3_file,

                    "-ss",

                    start_time,

                    "-to",

                    end_time,

                    "-c",

                    "copy",

                    cut_file

                ])



                if result.returncode != 0:

                    raise Exception(
                        "ffmpeg処理失敗(mp3)"
                    )



                os.remove(

                    mp3_file

                )


                os.rename(

                    cut_file,

                    mp3_file

                )



            files.append(

                os.path.basename(

                    mp3_file

                )

            )


            print("mp3完成")




        # ==========================
        # mp4作成
        # ==========================

        if "mp4" in outputs:


            print("mp4変換開始")


            ydl_opts = {

                "format":

                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",


                "merge_output_format":

                "mp4",


                "outtmpl":

                f"{output_dir}/%(title)s.%(ext)s",


                "noplaylist":

                True

            }



            with yt_dlp.YoutubeDL(ydl_opts) as ydl:


                info = ydl.extract_info(

                    url,

                    download=True

                )


                filename = ydl.prepare_filename(

                    info

                )



            mp4_file = os.path.splitext(

                filename

            )[0] + ".mp4"



            # 時間指定カット

            if start_time and end_time and start_time < end_time:


                cut_file = os.path.splitext(

                    mp4_file

                )[0] + "_cut.mp4"



                result = subprocess.run([

                    "ffmpeg",

                    "-y",

                    "-i",

                    mp4_file,

                    "-ss",

                    start_time,

                    "-to",

                    end_time,

                    "-c",

                    "copy",

                    cut_file

                ])



                if result.returncode != 0:

                    raise Exception(
                        "ffmpeg処理失敗(mp4)"
                    )



                os.remove(

                    mp4_file

                )


                os.rename(

                    cut_file,

                    mp4_file

                )



            files.append(

                os.path.basename(

                    mp4_file

                )

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


            start_time = data.get(

                "start_time"

            )


            end_time = data.get(

                "end_time"

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

                    outputs,

                    start_time,

                    end_time

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
