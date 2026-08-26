from flask import jsonify


# ==========================================================
# Job Status Storage
# ==========================================================

jobs = {}


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

    if job_id not in jobs:

        return False

    job = jobs[job_id]

    # ------------------------------------------------------
    # files が存在しなければ作成
    # ------------------------------------------------------

    if "files" not in job:

        job["files"] = {}

    # ------------------------------------------------------
    # ファイル情報
    # ------------------------------------------------------

    file_info = {

        "status":
            status

    }

    if filename is not None:

        file_info["filename"] = filename

    if message is not None:

        file_info["message"] = message

    if duration is not None:

        file_info["duration"] = duration

    if duration_text is not None:

        file_info["duration_text"] = duration_text

    # ------------------------------------------------------
    # 更新
    # ------------------------------------------------------

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

    if job_id not in jobs:

        return False

    jobs[job_id]["status"] = status

    for key, value in kwargs.items():

        jobs[job_id][key] = value

    return True


# ==========================================================
# Job取得
# ==========================================================

def get_job_status(job_id):

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

        # --------------------------------------------------
        # Jobなし
        # --------------------------------------------------

        if job_id not in jobs:

            return jsonify({

                "status":
                    "error",

                "message":
                    "jobなし"

            }), 404

        # --------------------------------------------------
        # Job情報
        # --------------------------------------------------

        return jsonify(
            jobs[job_id]
        )
