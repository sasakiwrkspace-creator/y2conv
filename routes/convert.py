from flask import request, jsonify

import os
import re
import threading
import traceback
import uuid

from datetime import datetime

from pathlib import Path

from ytdlp import (
    download_source,
    cleanup_download
)

from ytdlp_stream import (
    create_mp4_full,
    create_mp4_range
)

from media_extract import (
    create_mp3_from_file
)

from subtitle_mp4 import (
    create_subtitle_mp4 as create_subtitle_mp4_pipeline
)


# ==========================================================
# Job管理
# ==========================================================

_jobs = {}

_jobs_lock = threading.Lock()


# ==========================================================
# ファイル名安全化
# ==========================================================

def _sanitize_filename(
    value
):

    text = str(
        value or "YouTube Video"
    ).strip()

    if not text:

        text = "YouTube Video"

    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    text = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        text
    )

    text = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.rstrip(
        " ."
    )

    if not text:

        text = "YouTube Video"

    text = text[:180]

    return text.rstrip(
        " ."
    ) or "YouTube Video"


# ==========================================================
# Job作成
# ==========================================================

def _create_job(
    url,
    outputs,
    start_time=None,
    end_time=None
):

    job_id = str(
        uuid.uuid4()
    )

    job = {

        "job_id":
            job_id,

        "status":
            "queued",

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

            },

            "subtitle_mp4": {

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

        "message":
            "変換処理を開始する準備をしています。",

        "execution_seconds":
            None,

        "execution_seconds_text":
            "",

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

def _get_job(
    job_id
):

    with _jobs_lock:

        job = _jobs.get(
            job_id
        )

        if job is None:

            return None

        return {

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
                    ),

                "subtitle_mp4":
                    dict(
                        job["files"]["subtitle_mp4"]
                    )

            },

            "message":
                job.get("message"),

            "execution_seconds":
                job.get("execution_seconds"),

            "execution_seconds_text":
                job.get("execution_seconds_text"),

            "created_at":
                job.get("created_at"),

            "started_at":
                job.get("started_at"),

            "completed_at":
                job.get("completed_at")

        }


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

        if job:

            job.update(
                kwargs
            )


# ==========================================================
# File更新
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

        if not job:

            return

        file_info = job["files"].get(
            output_type
        )

        if file_info:

            file_info.update(
                kwargs
            )


# ==========================================================
# 秒表示
# ==========================================================

def _format_seconds(
    seconds
):

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
# 時間 → 秒
# ==========================================================

def _time_to_seconds(
    value
):

    if value is None:

        return 0.0

    text = str(
        value
    ).strip()

    if not text:

        return 0.0

    parts = text.split(":")

    try:

        if len(parts) == 3:

            return (
                float(parts[0]) * 3600
                +
                float(parts[1]) * 60
                +
                float(parts[2])
            )

        if len(parts) == 2:

            return (
                float(parts[0]) * 60
                +
                float(parts[1])
            )

        return float(text)

    except Exception as error:

        raise ValueError(
            f"時間形式が不正です: {value}"
        ) from error


# ==========================================================
# 全体判定
# ==========================================================

def _is_full_download(
    start_time=None,
    end_time=None
):

    return (

        _time_to_seconds(
            start_time
        ) == 0

        and

        _time_to_seconds(
            end_time
        ) == 0

    )


# ==========================================================
# ファイル名時間
# ==========================================================

def _format_filename_time(
    value
):

    seconds = _time_to_seconds(
        value
    )

    total_seconds = int(
        seconds
    )

    hours = total_seconds // 3600

    minutes = (
        total_seconds % 3600
    ) // 60

    secs = (
        total_seconds % 60
    )

    return (
        f"{hours:02d}"
        f"{minutes:02d}"
        f"{secs:02d}"
    )


# ==========================================================
# 時間suffix
# ==========================================================

def _build_range_suffix(
    start_time=None,
    end_time=None
):

    if _is_full_download(
        start_time,
        end_time
    ):

        return ""

    return (

        "_"
        +
        _format_filename_time(
            start_time
        )
        +
        "_"
        +
        _format_filename_time(
            end_time
        )

    )


# ==========================================================
# 完成ファイルリネーム
# ==========================================================

def _rename_completed_file(
    result,
    output_type,
    title=None,
    start_time=None,
    end_time=None
):

    if not result:

        raise RuntimeError(
            f"{output_type} 作成結果が空です。"
        )

    original_path_text = result.get(
        "path"
    )

    if not original_path_text:

        raise RuntimeError(
            f"{output_type} の出力パスがありません。"
        )

    original_path = Path(
        original_path_text
    )

    if not original_path.is_file():

        raise FileNotFoundError(
            f"{output_type} 完成ファイルがありません: "
            +
            str(original_path)
        )

    if original_path.stat().st_size <= 0:

        raise RuntimeError(
            f"{output_type} 完成ファイルサイズが0です。"
        )

    actual_title = (

        title
        or
        result.get("title")
        or
        "YouTube Video"

    )

    safe_title = _sanitize_filename(
        actual_title
    )

    extension = (
        original_path.suffix.lower()
    )

    if extension not in (
        ".mp3",
        ".mp4"
    ):

        raise RuntimeError(
            f"{output_type} の拡張子が不正です: {extension}"
        )

    range_suffix = _build_range_suffix(
        start_time,
        end_time
    )

    new_filename = (
        safe_title
        +
        range_suffix
        +
        extension
    )

    new_path = (
        original_path.parent
        /
        new_filename
    )

    if original_path != new_path:

        if new_path.exists():

            new_path.unlink()

        original_path.rename(
            new_path
        )

    if not new_path.is_file():

        raise FileNotFoundError(
            f"リネーム後のファイルがありません: {new_path}"
        )

    if new_path.stat().st_size <= 0:

        raise RuntimeError(
            f"リネーム後のファイルサイズが0です: {new_path}"
        )

    return {

        "path":
            str(new_path),

        "filename":
            new_path.name

    }


# ==========================================================
# source確認
# ==========================================================

def _validate_source(
    download_result
):

    if not download_result:

        raise RuntimeError(
            "動画ダウンロード結果が空です。"
        )

    source_path = Path(
        download_result.get(
            "path",
            ""
        )
    )

    if not source_path.is_file():

        raise FileNotFoundError(
            f"一時動画ファイルがありません: {source_path}"
        )

    if source_path.stat().st_size <= 0:

        raise RuntimeError(
            f"一時動画ファイルサイズが0です: {source_path}"
        )

    return source_path


# ==========================================================
# Background Job
# ==========================================================

def _run_conversion_job(
    job_id,
    url,
    outputs,
    start_time=None,
    end_time=None
):

    started_at = datetime.now()

    download_result = None

    try:

        _update_job(

            job_id,

            status="processing",

            started_at=
                started_at.isoformat(),

            message=
                "変換処理を開始しています・・・"

        )

        output_dir = (
            Path(os.getcwd())
            /
            "downloads"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        # ==================================================
        # ★ 字幕MP4専用モード
        # ==================================================

        if "subtitle_mp4" in outputs:

            _update_file(

                job_id,

                "subtitle_mp4",

                status="processing",

                message=
                    "字幕MP4連続処理を開始しています・・・"

            )

            _update_job(

                job_id,

                message=
                    "① MP4を作成しています・・・"

            )

            print(
                "[CONVERT] SUBTITLE MP4 MODE START",
                flush=True
            )

            pipeline_result = (
                create_subtitle_mp4_pipeline(

                    url=
                        url,

                    start_time=
                        start_time,

                    end_time=
                        end_time,

                    output_dir=
                        output_dir

                )
            )

            if not pipeline_result:

                raise RuntimeError(
                    "字幕MP4連続処理結果が空です。"
                )

            subtitle_mp4_path = Path(
                pipeline_result[
                    "subtitle_mp4_path"
                ]
            )

            if not subtitle_mp4_path.is_file():

                raise FileNotFoundError(
                    f"字幕MP4がありません: "
                    +
                    str(subtitle_mp4_path)
                )

            if subtitle_mp4_path.stat().st_size <= 0:

                raise RuntimeError(
                    "字幕MP4のファイルサイズが0です。"
                )

            title = (
                pipeline_result.get(
                    "title"
                )
                or
                "YouTube Video"
            )

            duration = pipeline_result.get(
                "duration"
            )

            _update_job(

                job_id,

                title=
                    title,

                duration=
                    duration,

                duration_text=
                    _format_seconds(
                        duration
                    ),

                message=
                    "字幕MP4連続処理が完了しました。"

            )

            _update_file(

                job_id,

                "subtitle_mp4",

                status="complete",

                filename=
                    subtitle_mp4_path.name,

                path=
                    str(subtitle_mp4_path),

                message=
                    "字幕MP4変換終了"

            )

            # ------------------------------------------------
            # 補助ファイル情報
            # ------------------------------------------------

            if pipeline_result.get(
                "mp4_path"
            ):

                _update_job(

                    job_id,

                    subtitle_mp4_source_mp4=
                        pipeline_result[
                            "mp4_path"
                        ]

                )

            if pipeline_result.get(
                "mp3_path"
            ):

                _update_job(

                    job_id,

                    subtitle_mp4_source_mp3=
                        pipeline_result[
                            "mp3_path"
                        ]

                )

            if pipeline_result.get(
                "srt_path"
            ):

                _update_job(

                    job_id,

                    subtitle_mp4_srt=
                        pipeline_result[
                            "srt_path"
                        ]

                )

            print(
                "[CONVERT] SUBTITLE MP4 MODE COMPLETE:",
                subtitle_mp4_path,
                flush=True
            )


        # ==================================================
        # 通常モード
        # ==================================================

        else:

            full_download = _is_full_download(
                start_time,
                end_time
            )

            title = "YouTube Video"

            duration = None


            # ==================================================
            # MP3
            # ==================================================

            if "mp3" in outputs:

                _update_file(

                    job_id,
                    "mp3",

                    status="processing",

                    message=
                        "mp3 用動画をダウンロード中・・・"

                )

                _update_job(

                    job_id,

                    message=
                        "mp3 用動画をダウンロード中・・・"

                )

                download_result = download_source(
                    url
                )

                source_path = _validate_source(
                    download_result
                )

                title = (
                    download_result.get(
                        "title"
                    )
                    or
                    "YouTube Video"
                )

                duration = (
                    download_result.get(
                        "duration"
                    )
                )

                _update_job(

                    job_id,

                    title=
                        title,

                    duration=
                        duration,

                    duration_text=
                        _format_seconds(
                            duration
                        )

                )

                mp3_result = create_mp3_from_file(

                    input_file=
                        str(source_path),

                    output_dir=
                        output_dir,

                    title=
                        title,

                    start_time=
                        start_time,

                    end_time=
                        end_time

                )

                renamed_mp3 = _rename_completed_file(

                    result=
                        mp3_result,

                    output_type=
                        "mp3",

                    title=
                        title,

                    start_time=
                        start_time,

                    end_time=
                        end_time

                )

                _update_file(

                    job_id,

                    "mp3",

                    status="complete",

                    filename=
                        renamed_mp3["filename"],

                    path=
                        renamed_mp3["path"],

                    message=
                        "mp3 変換終了"

                )


            # ==================================================
            # MP4
            # ==================================================

            if "mp4" in outputs:

                _update_file(

                    job_id,

                    "mp4",

                    status="processing",

                    message=
                        "mp4 ダウンロード中・・・"

                )

                if full_download:

                    mp4_result = create_mp4_full(

                        url=
                            url,

                        output_dir=
                            output_dir

                    )

                else:

                    mp4_result = create_mp4_range(

                        url=
                            url,

                        output_dir=
                            output_dir,

                        start_time=
                            start_time,

                        end_time=
                            end_time

                    )

                mp4_title = (
                    mp4_result.get(
                        "title"
                    )
                    or
                    "YouTube Video"
                )

                if (
                    not title
                    or
                    title == "YouTube Video"
                ):

                    title = mp4_title

                mp4_duration = (
                    mp4_result.get(
                        "duration"
                    )
                )

                if (
                    duration is None
                    and
                    mp4_duration is not None
                ):

                    duration = mp4_duration

                renamed_mp4 = _rename_completed_file(

                    result=
                        mp4_result,

                    output_type=
                        "mp4",

                    title=
                        title,

                    start_time=
                        start_time,

                    end_time=
                        end_time

                )

                _update_job(

                    job_id,

                    title=
                        title,

                    duration=
                        duration,

                    duration_text=
                        _format_seconds(
                            duration
                        )

                )

                _update_file(

                    job_id,

                    "mp4",

                    status="complete",

                    filename=
                        renamed_mp4["filename"],

                    path=
                        renamed_mp4["path"],

                    message=
                        "mp4 変換終了"

                )


        # ==================================================
        # 完了
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

        traceback.print_exc()

        for output_type in outputs:

            job = _get_job(
                job_id
            )

            if not job:

                continue

            if output_type not in job["files"]:

                continue

            current_status = (
                job["files"]
                [output_type]
                ["status"]
            )

            if current_status == "processing":

                _update_file(

                    job_id,

                    output_type,

                    status="error",

                    message=
                        f"{output_type} 変換エラー: "
                        +
                        str(error)

                )


    finally:

        if download_result:

            cleanup_download(
                download_result
            )

        print(
            "[CONVERT] Background job END:",
            job_id,
            flush=True
        )


# ==========================================================
# Route
# ==========================================================

def register_convert(
    app
):

    @app.route(
        "/convert",
        methods=["POST"]
    )
    def convert():

        try:

            data = (
                request.get_json(
                    silent=True
                )
                or
                {}
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
            # output_type
            # ==================================================

            if not outputs:

                output_type = data.get(
                    "output_type"
                )

                if output_type in (
                    "mp3",
                    "mp4",
                    "subtitle_mp4"
                ):

                    outputs = [
                        output_type
                    ]


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
                    "mp4",
                    "subtitle_mp4"
                )

            ]


            outputs = list(
                dict.fromkeys(
                    outputs
                )
            )


            # ==================================================
            # URL
            # ==================================================

            if not url:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "YouTube URLが指定されていません。"

                }), 400


            # ==================================================
            # 出力形式
            # ==================================================

            if not outputs:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "出力形式を選択してください。"

                }), 400


            # ==================================================
            # ★字幕MP4は完全独立
            # ==================================================

            if "subtitle_mp4" in outputs:

                outputs = [
                    "subtitle_mp4"
                ]


            # ==================================================
            # 時間検証
            # ==================================================

            if (
                start_time is not None
                or
                end_time is not None
            ):

                try:

                    start_value = _time_to_seconds(
                        start_time
                    )

                    end_value = _time_to_seconds(
                        end_time
                    )

                    if start_value < 0:

                        return jsonify({

                            "success":
                                False,

                            "message":
                                "開始時間は0秒以上にしてください。"

                        }), 400

                    if end_value < 0:

                        return jsonify({

                            "success":
                                False,

                            "message":
                                "終了時間は0秒以上にしてください。"

                        }), 400

                    if not (
                        start_value == 0
                        and
                        end_value == 0
                    ):

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
                ) as error:

                    print(
                        "[CONVERT] Time validation ERROR:",
                        repr(error),
                        flush=True
                    )

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "開始時間または終了時間が不正です。"

                    }), 400


            # ==================================================
            # Job
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

            print(
                "[CONVERT] outputs:",
                outputs,
                flush=True
            )


            # ==================================================
            # Background
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
    # Status
    # ======================================================

    @app.route(
        "/status/<job_id>",
        methods=["GET"]
    )
    def status(
        job_id
    ):

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
