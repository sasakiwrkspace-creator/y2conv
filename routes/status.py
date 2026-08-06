from flask import jsonify


jobs = {}


def register_status(app):

    @app.route("/status/<job_id>")
    def status(job_id):

        if job_id not in jobs:

            return jsonify({

                "status": "error",

                "message": "jobなし"

            })


        return jsonify(
            jobs[job_id]
        )