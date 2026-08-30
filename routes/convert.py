# =====================================
# YouTube Converter
# routes/convert.py
#
# 役割:
# ・/convert
# ・変換ジョブ作成
# ・バックグラウンド変換
# ・/status/<job_id>
#
# converter.js と連携
# =====================================

from flask import request, jsonify

from ytdlp import create_mp3, create_mp4

import threading
import uuid
import traceback
import time


# =====================================
# ジョブ保存
# =====================================

JOBS = {}

JOBS_LOCK = threading.Lock()


# =====================================
# ジョブ取得
# =====================================

def get_job(job_id):

    with JOBS_LOCK:

        return JOBS.get(
            job_id
        )


# =====================================
# ジョブ更新
# =====================================

def update_job(
    job_id,
    **kwargs
):

    with JOBS_LOCK:

        job = JOBS.get(
            job_id
        )

        if not job:
            return

        job.update(
            kwargs
        )


# =====================================
# 変換処理本体
# =====================================

def run_conversion(
    job_id,
    url,
    outputs,
    start_time,
    end_time
):

    started_at = time.time()

    print(
        "==========================================",
        flush=True
    )

    print(
        "[CONVERT] バックグラウンド変換開始",
        flush=True
    )

    print(
        "[CONVERT] job_id:",
        job_id,
        flush=True
    )

    print(
        "[CONVERT] URL:",
        url,
        flush=True
    )

    print(
        "[CONVERT] outputs:",
        outputs,
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
        "==========================================",
        flush=True
    )


    try:

        # =====================================
        # MP3
        # =====================================

        if "mp3" in outputs:

            update_job(

                job_id,

                status="processing",

                current="mp3",

                message="MP3を作成しています..."

            )

            print(
                "[CONVERT] MP3作成開始",
                flush=True
            )


            result_mp3 = create_mp3(

                url,

                start_time=start_time,

                end_time=end_time

            )


            print(
                "[CONVERT] MP3作成完了:",
                repr(result_mp3),
                flush=True
            )


            if not result_mp3:

                raise Exception(
                    "MP3ファイルの作成結果を取得できませんでした。"
                )


            update_job(

                job_id,

                files={

                    **get_job(job_id).get(
                        "files",
                        {}
                    ),

                    "mp3": {

                        "status":
                        "complete",

                        "filename":
                        result_mp3

                    }

                }

            )


        # =====================================
        # MP4
        # =====================================

        if "mp4" in outputs:

            update_job(

                job_id,

                status="processing",

                current="mp4",

                message="MP4を作成しています..."

            )

            print(
                "[CONVERT] MP4作成開始",
                flush=True
            )


            result_mp4 = create_mp4(

                url

            )


            print(
                "[CONVERT] MP4作成完了:",
                repr(result_mp4),
                flush=True
            )


            if not result_mp4:

                raise Exception(
                    "MP4ファイルの作成結果を取得できませんでした。"
                )


            update_job(

                job_id,

                files={

                    **get_job(job_id).get(
                        "files",
                        {}
                    ),

                    "mp4": {

                        "status":
                        "complete",

                        "filename":
                        result_mp4

                    }

                }

            )


        # =====================================
        # 完了
        # =====================================

        elapsed = (
            time.time() -
            started_at
        )

        elapsed_seconds = int(
            elapsed
        )


        if elapsed_seconds >= 3600:

            h = elapsed_seconds // 3600

            m = (
                elapsed_seconds % 3600
            ) // 60

            s = (
                elapsed_seconds % 60
            )

            elapsed_text = (
                f"{h}時間 "
                f"{m}分 "
                f"{s}秒"
            )

        elif elapsed_seconds >= 60:

            m = elapsed_seconds // 60

            s = elapsed_seconds % 60

            elapsed_text = (
                f"{m}分 "
                f"{s}秒"
            )

        else:

            elapsed_text = (
                f"{elapsed_seconds}秒"
            )


        update_job(

            job_id,

            status="complete",

            current="",

            message="変換が完了しました。",

            execution_seconds=
                elapsed_seconds,

            execution_seconds_text=
                "処理時間: " +
                elapsed_text,

            finished_at=
                time.time()

        )


        print(
            "==========================================",
            flush=True
        )

        print(
            "[CONVERT] 変換完了",
            flush=True
        )

        print(
            "[CONVERT] job_id:",
            job_id,
            flush=True
        )

        print(
            "[CONVERT] 処理時間:",
            elapsed_text,
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


    except Exception as error:

        elapsed = (
            time.time() -
            started_at
        )

        print(
            "==========================================",
            flush=True
        )

        print(
            "[CONVERT] バックグラウンド変換エラー",
            flush=True
        )

        print(
            "[CONVERT] job_id:",
            job_id,
            flush=True
        )

        print(
            "[CONVERT] error:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        print(
            "==========================================",
            flush=True
        )


        update_job(

            job_id,

            status="error",

            current="",

            message=str(error),

            finished_at=
                time.time(),

            execution_seconds=
                int(elapsed),

            execution_seconds_text=
                "処理時間: " +
                str(
                    int(elapsed)
                ) +
                "秒"

        )


# =====================================
# Route登録
# =====================================

def register_convert(app):


    # =====================================
    # /convert
    # =====================================

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

            # =================================
            # JSON
            # =================================

            data = request.get_json(
                silent=True
            ) or {}


            print(
                "[CONVERT] request data:",
                data,
                flush=True
            )


            # =================================
            # URL
            # =================================

            url = data.get(
                "url"
            )


            if not url:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "YouTube URLが指定されていません。"

                }), 400


            # =================================
            # 出力形式
            #
            # 新形式:
            #
            # outputs:
            # [
            #   "mp3",
            #   "mp4"
            # ]
            #
            # 旧形式:
            #
            # output_type:
            # "mp3"
            # =================================

            outputs = data.get(
                "outputs"
            )


            if not outputs:

                output_type = data.get(
                    "output_type"
                )


                if output_type:

                    outputs = [
                        output_type
                    ]

                else:

                    outputs = [
                        "mp3"
                    ]


            # =================================
            # 文字列対策
            # =================================

            if isinstance(
                outputs,
                str
            ):

                outputs = [
                    outputs
                ]


            # =================================
            # 対応形式確認
            # =================================

            normalized_outputs = []


            for output in outputs:

                output = str(
                    output
                ).lower().strip()


                if output in (
                    "mp3",
                    "mp4"
                ):

                    normalized_outputs.append(
                        output
                    )


            # 重複削除

            outputs = list(
                dict.fromkeys(
                    normalized_outputs
                )
            )


            if not outputs:

                return jsonify({

                    "success":
                    False,

                    "message":
                    "出力形式を選択してください。"

                }), 400


            # =================================
            # 時間
            # =================================

            start_time = data.get(
                "start_time"
            )


            end_time = data.get(
                "end_time"
            )


            print(
                "[CONVERT] URL:",
                url,
                flush=True
            )

            print(
                "[CONVERT] outputs:",
                outputs,
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


            # =================================
            # job_id
            # =================================

            job_id = str(
                uuid.uuid4()
            )


            # =================================
            # 初期ジョブ
            # =================================

            job = {

                "job_id":
                job_id,

                "status":
                "queued",

                "current":
                "",

                "message":
                "変換待機中...",

                "title":
                "",

                "duration_text":
                "",

                "files":
                {},

                "execution_seconds":
                0,

                "execution_seconds_text":
                "",

                "created_at":
                time.time(),

                "finished_at":
                None

            }


            with JOBS_LOCK:

                JOBS[job_id] =
                    job


            # =================================
            # バックグラウンド開始
            # =================================

            thread = threading.Thread(

                target=
                    run_conversion,

                args=(

                    job_id,

                    url,

                    outputs,

                    start_time,

                    end_time

                ),

                daemon=True

            )


            thread.start()


            print(
                "[CONVERT] Job開始:",
                job_id,
                flush=True
            )


            # =================================
            # JSへ返す
            # =================================

            return jsonify({

                "success":
                True,

                "job_id":
                job_id

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


    # =====================================
    # /status/<job_id>
    # =====================================

    @app.route(
        "/status/<job_id>",
        methods=["GET"]
    )
    def status(
        job_id
    ):

        print(
            "[STATUS] job_id:",
            job_id,
            flush=True
        )


        job = get_job(
            job_id
        )


        if not job:

            return jsonify({

                "success":
                False,

                "message":
                "指定されたジョブが見つかりません。",

                "status":
                "error"

            }), 404


        return jsonify({

            "success":
            True,

            **job

        })
