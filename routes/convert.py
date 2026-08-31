from flask import request, jsonify

import threading
import traceback
import uuid
from datetime import datetime

from ytdlp import create_mp3, create_mp4


# ==========================================================
# Job管理
# ==========================================================

_jobs = {}

_jobs_lock = threading.Lock()


# ==========================================================
# Job作成
# ==========================================================

def _create_job(
    url,
    outputs,
    start_time=None,
    end_time=None
):

    job_id = str(uuid.uuid4())

    job = {

        "job_id":
            job_id,

        "status":
            "queued",

        # ==================================================
        # YouTube動画タイトル
        # ==================================================

        "title":
            "",

        "url":
            url,

        "duration":
            None,

        "duration_text":
            "",

        "start_time":
            start_time,

        "end_time":
            end_time,

        # ==================================================
        # 出力ファイル
        # ==================================================

        "files": {

            "mp3": {

                "status":
                    "pending",

                "filename":
                    None,

                "path":
                    None,

                "message":
                    ""

            },

            "mp4": {

                "status":
                    "pending",

                "filename":
                    None,

                "path":
                    None,

                "message":
                    ""

            }

        },

        # ==================================================
        # 全体メッセージ
        # ==================================================

        "message":
            "変換処理を開始する準備をしています。",

        # ==================================================
        # 処理時間
        # ==================================================

        "execution_seconds":
            None,

        "execution_seconds_text":
            "",

        # ==================================================
        # 時刻
        # ==================================================

        "created_at":
            datetime.now().isoformat(),

        "started_at":
            None,

        "completed_at":
            None

    }

    with _jobs_lock:

        _jobs[job_id] = job

    return job_id


# ==========================================================
# Job取得
# ==========================================================

def _get_job(job_id):

    with _jobs_lock:

        job = _jobs.get(
            job_id
        )

        if job is None:

            return None

        # --------------------------------------------------
        # JSON返却用に最低限コピー
        # --------------------------------------------------

        result = {

            "job_id":
                job.get("job_id"),

            "status":
                job.get("status"),

            "title":
                job.get("title"),

            "url":
                job.get("url"),

            "duration":
                job.get("duration"),

            "duration_text":
                job.get("duration_text"),

            "start_time":
                job.get("start_time"),

            "end_time":
                job.get("end_time"),

            "files": {

                "mp3":
                    dict(
                        job["files"]["mp3"]
                    ),

                "mp4":
                    dict(
                        job["files"]["mp4"]
                    )

            },

            "message":
                job.get("message"),

            "execution_seconds":
                job.get("execution_seconds"),

            "execution_seconds_text":
                job.get(
                    "execution_seconds_text"
                ),

            "created_at":
                job.get("created_at"),

            "started_at":
                job.get("started_at"),

            "completed_at":
                job.get("completed_at")

        }

        return result


# ==========================================================
# Job更新
# ==========================================================

def _update_job(
    job_id,
    **kwargs
):

    with _jobs_lock:

        job = _jobs.get(
            job_id
        )

        if job is None:

            return

        job.update(
            kwargs
        )


# ==========================================================
# ファイルJob更新
# ==========================================================

def _update_file(
    job_id,
    output_type,
    **kwargs
):

    with _jobs_lock:

        job = _jobs.get(
            job_id
        )

        if job is None:

            return

        file_info = job["files"].get(
            output_type
        )

        if file_info is None:

            return

        file_info.update(
            kwargs
        )


# ==========================================================
# 時間表示
# ==========================================================

def _format_seconds(seconds):

    if seconds is None:

        return ""

    try:

        total = int(
            float(seconds)
        )

    except Exception:

        return ""

    hours = total // 3600

    minutes = (
        total % 3600
    ) // 60

    secs = (
        total % 60
    )

    if hours > 0:

        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{secs:02d}"
        )

    return (
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ==========================================================
# Job実行
# ==========================================================

def _run_conversion_job(
    job_id,
    url,
    outputs,
    start_time=None,
    end_time=None
):

    started_at = datetime.now()

    # ======================================================
    # 処理開始
    # ======================================================

    _update_job(

        job_id,

        status="processing",

        started_at=
            started_at.isoformat(),

        message=
            "動画情報を取得しています・・・"

    )

    print(
        "==========================================",
        flush=True
    )

    print(
        "[CONVERT] Background job START:",
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

    try:

        # ==================================================
        # MP3
        # ==================================================

        if "mp3" in outputs:

            # ------------------------------------------------
            # MP3変換開始
            # ------------------------------------------------

            _update_file(

                job_id,

                "mp3",

                status="processing",

                message=
                    "mp3 変換中・・・"

            )

            _update_job(

                job_id,

                message=
                    "mp3 変換中・・・"

            )

            print(
                "[CONVERT] MP3作成開始",
                flush=True
            )

            try:

                result = create_mp3(

                    url,

                    start_time=
                        start_time,

                    end_time=
                        end_time

                )

                print(
                    "[CONVERT] MP3作成完了:",
                    result,
                    flush=True
                )

                if not result:

                    raise RuntimeError(
                        "MP3作成結果が空です。"
                    )

                # ------------------------------------------------
                # 動画タイトル
                # ------------------------------------------------

                title = (
                    result.get("title")
                    or ""
                )

                if title:

                    _update_job(

                        job_id,

                        title=title

                    )

                # ------------------------------------------------
                # 動画時間
                # ------------------------------------------------

                duration = (
                    result.get("duration")
                )

                if duration is not None:

                    _update_job(

                        job_id,

                        duration=duration,

                        duration_text=
                            _format_seconds(
                                duration
                            )

                    )

                # ------------------------------------------------
                # MP3完了
                # ------------------------------------------------

                _update_file(

                    job_id,

                    "mp3",

                    status="complete",

                    filename=
                        result.get(
                            "filename"
                        ),

                    path=
                        result.get(
                            "path"
                        ),

                    message=
                        "mp3 変換終了"

                )

                _update_job(

                    job_id,

                    message=
                        "mp3 変換終了"

                )

            except Exception as error:

                print(
                    "[CONVERT] MP3 ERROR:",
                    repr(error),
                    flush=True
                )

                _update_file(

                    job_id,

                    "mp3",

                    status="error",

                    filename=None,

                    path=None,

                    message=
                        "mp3 変換エラー: "
                        + str(error)

                )

                raise

        # ==================================================
        # MP4
        # ==================================================

        if "mp4" in outputs:

            # ------------------------------------------------
            # MP4変換開始
            # ------------------------------------------------

            _update_file(

                job_id,

                "mp4",

                status="processing",

                message=
                    "mp4 変換中・・・"

            )

            _update_job(

                job_id,

                message=
                    "mp4 変換中・・・"

            )

            print(
                "[CONVERT] MP4作成開始",
                flush=True
            )

            try:

                result = create_mp4(

                    url,

                    start_time=
                        start_time,

                    end_time=
                        end_time

                )

                print(
                    "[CONVERT] MP4作成完了:",
                    result,
                    flush=True
                )

                if not result:

                    raise RuntimeError(
                        "MP4作成結果が空です。"
                    )

                # ------------------------------------------------
                # 動画タイトル
                # ------------------------------------------------

                title = (
                    result.get("title")
                    or ""
                )

                if title:

                    _update_job(

                        job_id,

                        title=title

                    )

                # ------------------------------------------------
                # 動画時間
                # ------------------------------------------------

                duration = (
                    result.get("duration")
                )

                if duration is not None:

                    _update_job(

                        job_id,

                        duration=duration,

                        duration_text=
                            _format_seconds(
                                duration
                            )

                    )

                # ------------------------------------------------
                # MP4完了
                # ------------------------------------------------

                _update_file(

                    job_id,

                    "mp4",

                    status="complete",

                    filename=
                        result.get(
                            "filename"
                        ),

                    path=
                        result.get(
                            "path"
                        ),

                    message=
                        "mp4 変換終了"

                )

                _update_job(

                    job_id,

                    message=
                        "mp4 変換終了"

                )

            except Exception as error:

                print(
                    "[CONVERT] MP4 ERROR:",
                    repr(error),
                    flush=True
                )

                _update_file(

                    job_id,

                    "mp4",

                    status="error",

                    filename=None,

                    path=None,

                    message=
                        "mp4 変換エラー: "
                        + str(error)

                )

                raise

        # ==================================================
        # 全体完了
        # ==================================================

        completed_at = datetime.now()

        elapsed = (
            completed_at
            -
            started_at
        ).total_seconds()

        _update_job(

            job_id,

            status="complete",

            completed_at=
                completed_at.isoformat(),

            execution_seconds=
                elapsed,

            execution_seconds_text=
                "処理時間: "
                +
                _format_seconds(
                    elapsed
                ),

            message=
                "変換が完了しました。"

        )

        print(
            "[CONVERT] Job COMPLETE:",
            job_id,
            flush=True
        )

    except Exception as error:

        # ======================================================
        # エラー
        # ======================================================

        completed_at = datetime.now()

        elapsed = (
            completed_at
            -
            started_at
        ).total_seconds()

        _update_job(

            job_id,

            status="error",

            completed_at=
                completed_at.isoformat(),

            execution_seconds=
                elapsed,

            execution_seconds_text=
                "処理時間: "
                +
                _format_seconds(
                    elapsed
                ),

            message=
                str(error)

        )

        print(
            "[CONVERT] Job ERROR:",
            job_id,
            repr(error),
            flush=True
        )

        traceback.print_exc()

    finally:

        print(
            "[CONVERT] Background job END:",
            job_id,
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )


# ==========================================================
# Route登録
# ==========================================================

def register_convert(app):

    # ======================================================
    # 変換開始
    # ======================================================

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

        try:

            # ==================================================
            # Request
            # ==================================================

            data = request.get_json(
                silent=True
            ) or {}

            print(
                "[CONVERT] request data:",
                data,
                flush=True
            )

            url = data.get(
                "url"
            )

            outputs = data.get(
                "outputs"
            )

            start_time = data.get(
                "start_time"
            )

            end_time = data.get(
                "end_time"
            )

            # ==================================================
            # 旧形式 output_type 対応
            # ==================================================

            if not outputs:

                output_type = data.get(
                    "output_type"
                )

                if output_type in (
                    "mp3",
                    "mp4"
                ):

                    outputs = [
                        output_type
                    ]

            # ==================================================
            # outputs正規化
            # ==================================================

            if isinstance(
                outputs,
                str
            ):

                outputs = [
                    outputs
                ]

            if not isinstance(
                outputs,
                list
            ):

                outputs = []

            outputs = [

                output

                for output in outputs

                if output in (
                    "mp3",
                    "mp4"
                )

            ]

            outputs = list(
                dict.fromkeys(
                    outputs
                )
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
            # 出力形式確認
            # ==================================================

            if not outputs:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "出力形式を選択してください。"

                }), 400

            # ==================================================
            # 時間確認
            # ==================================================

            if (
                start_time is not None
                and
                end_time is not None
            ):

                try:

                    start_value = float(
                        start_time
                    )

                    end_value = float(
                        end_time
                    )

                    if end_value <= start_value:

                        return jsonify({

                            "success":
                                False,

                            "message":
                                "終了時間は開始時間より後にしてください。"

                        }), 400

                except (
                    TypeError,
                    ValueError
                ):

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "開始時間または終了時間が不正です。"

                    }), 400

            # ==================================================
            # Job作成
            # ==================================================

            job_id = _create_job(

                url=
                    url,

                outputs=
                    outputs,

                start_time=
                    start_time,

                end_time=
                    end_time

            )

            print(
                "[CONVERT] job_id:",
                job_id,
                flush=True
            )

            # ==================================================
            # バックグラウンド実行
            # ==================================================

            thread = threading.Thread(

                target=
                    _run_conversion_job,

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

            # ==================================================
            # 即時レスポンス
            # ==================================================

            return jsonify({

                "success":
                    True,

                "job_id":
                    job_id,

                "message":
                    "変換ジョブを開始しました。"

            })

        except Exception as error:

            print(
                "[CONVERT] /convert ERROR:",
                repr(error),
                flush=True
            )

            traceback.print_exc()

            return jsonify({

                "success":
                    False,

                "message":
                    str(error)

            }), 500

    # ======================================================
    # Jobステータス
    # ======================================================

    @app.route(
        "/status/<job_id>",
        methods=["GET"]
    )
    def status(job_id):

        print(
            "[CONVERT] /status:",
            job_id,
            flush=True
        )

        job = _get_job(
            job_id
        )

        if job is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "指定されたjob_idが見つかりません。"

            }), 404

        return jsonify(
            job
        )
