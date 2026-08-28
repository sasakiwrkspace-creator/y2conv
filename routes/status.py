from flask import jsonify
import threading
import time


# ==========================================================
# Job Status Storage
# ==========================================================

jobs = {}

jobs_lock = threading.RLock()


# ==========================================================
# ファイル単位のステータス更新
# ==========================================================

def update_file_status(
    job_id,
    file_type,
    status,
    filename=None,
    message=None,
    duration=None,
    duration_text=None
):

    with jobs_lock:

        if job_id not in jobs:

            return False

        job = jobs[job_id]

        if "files" not in job:

            job["files"] = {}

        file_info = {

            "status":
                status,

            "updated_at":
                time.time()

        }

        if filename is not None:

            file_info["filename"] = filename

        if message is not None:

            file_info["message"] = message

        if duration is not None:

            file_info["duration"] = duration

        if duration_text is not None:

            file_info["duration_text"] = duration_text

        job["files"][file_type] = file_info

        return True


# ==========================================================
# Job全体ステータス更新
# ==========================================================

def update_job_status(
    job_id,
    status,
    **kwargs
):

    with jobs_lock:

        if job_id not in jobs:

            return False

        jobs[job_id]["status"] = status

        jobs[job_id]["updated_at"] = time.time()

        for key, value in kwargs.items():

            jobs[job_id][key] = value

        return True


# ==========================================================
# Job取得
# ==========================================================

def get_job_status(job_id):

    with jobs_lock:

        if job_id not in jobs:

            return None

        return jobs[job_id]


# ==========================================================
# /status/<job_id>
# ==========================================================

def register_status(app):

    @app.route(
        "/status/<job_id>",
        methods=["GET"]
    )
    def status(job_id):

        with jobs_lock:

            if job_id not in jobs:

                return jsonify({

                    "status":
                        "error",

                    "message":
                        "jobなし"

                }), 404

            # コピーして返す
            result = dict(
                jobs[job_id]
            )

            if "files" in jobs[job_id]:

                result["files"] = {}

                for file_type, file_info in jobs[job_id]["files"].items():

                    result["files"][file_type] = dict(
                        file_info
                    )

            return jsonify(
                result
            )
