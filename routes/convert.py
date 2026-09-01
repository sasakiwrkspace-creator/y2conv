from flask import request, jsonify

import os
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

def _get_job(job_id):

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
# 時間 → 秒
#
# HH:MM:SS
# MM:SS
# 秒
# に対応
# ==========================================================

def _time_to_seconds(value):

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
# 時間指定判定
#
# 00:00:00 ～ 00:00:00
# または
# None / None
# は全体扱い
# ==========================================================

def _is_full_download(
    start_time=None,
    end_time=None
):

    return (
        _time_to_seconds(start_time) == 0
        and
        _time_to_seconds(end_time) == 0
    )


# ==========================================================
# ファイル名用時間
#
# 5秒
# → 000005
#
# 1分30秒
# → 000130
#
# 1時間2分3秒
# → 010203
#
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
# 時間指定ファイル名サフィックス
#
# 全体：
#   ""
#
# 5秒～10秒：
#   "_000005_000010"
#
# 0秒～10秒：
#   "_000000_000010"
#
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

    start_text = _format_filename_time(
        start_time
    )

    end_text = _format_filename_time(
        end_time
    )

    return (
        "_"
        +
        start_text
        +
        "_"
        +
        end_text
    )


# ==========================================================
# 完成後ファイルをリネーム
#
# ここでは「変換完了後」にだけ名前を変更する。
#
# 例：
#
# video_id.mp3
# ↓
# video_id_000005_000010.mp3
#
# video_id.mp4
# ↓
# video_id_000005_000010.mp4
#
# 全体の場合：
#
# video_id.mp3
# video_id.mp4
#
# のまま。
# ==========================================================

def _rename_completed_file(
    result,
    output_type,
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
            f"{output_type} 完成ファイルのサイズが0です: "
            +
            str(original_path)
        )

    # ------------------------------------------------------
    # video_id
    # ------------------------------------------------------

    video_id = (
        result.get("video_id")
        or
        original_path.stem
    )

    # ------------------------------------------------------
    # 拡張子
    # ------------------------------------------------------

    extension = (
        original_path.suffix.lower()
    )

    if extension not in (
        ".mp3",
        ".mp4"
    ):

        raise RuntimeError(
            f"{output_type} の拡張子が不正です: "
            +
            extension
        )

    # ------------------------------------------------------
    # 時間指定サフィックス
    # ------------------------------------------------------

    range_suffix = _build_range_suffix(

        start_time=
            start_time,

        end_time=
            end_time

    )

    # ------------------------------------------------------
    # 新しいファイル名
    #
    # 全体：
    #   video_id.mp3
    #
    # 時間指定：
    #   video_id_000005_000010.mp3
    # ------------------------------------------------------

    new_filename = (

        str(video_id)
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

    print(
        "[CONVERT] Rename:",
        original_path,
        "->",
        new_path,
        flush=True
    )

    # ------------------------------------------------------
    # 同じパスなら何もしない
    # ------------------------------------------------------

    if original_path == new_path:

        return {

            "path":
                str(new_path),

            "filename":
                new_path.name

        }

    # ------------------------------------------------------
    # 既存ファイルがある場合
    # ------------------------------------------------------

    if new_path.exists():

        print(
            "[CONVERT] Removing existing file:",
            new_path,
            flush=True
        )

        new_path.unlink()

    # ------------------------------------------------------
    # 完成済みファイルをリネーム
    # ------------------------------------------------------

    original_path.rename(
        new_path
    )

    # ------------------------------------------------------
    # リネーム後確認
    # ------------------------------------------------------

    if not new_path.is_file():

        raise FileNotFoundError(
            f"リネーム後のファイルがありません: "
            +
            str(new_path)
        )

    if new_path.stat().st_size <= 0:

        raise RuntimeError(
            f"リネーム後のファイルサイズが0です: "
            +
            str(new_path)
        )

    print(
        "[CONVERT] Rename COMPLETE:",
        new_path,
        flush=True
    )

    return {

        "path":
            str(new_path),

        "filename":
            new_path.name

    }


# ==========================================================
# sourceファイル確認
# ==========================================================

def _validate_source(
    download_result
):

    if not download_result:

        raise RuntimeError(
            "動画ダウンロード結果が空です。"
        )

    source_path = Path(
        download_result.get("path", "")
    )

    if not source_path.is_file():

        raise FileNotFoundError(
            f"一時動画ファイルがありません: {source_path}"
        )

    size = source_path.stat().st_size

    if size <= 0:

        raise RuntimeError(
            f"一時動画ファイルのサイズが0です: {source_path}"
        )

    return source_path


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

    download_result = None

    try:

        # ==================================================
        # processing
        # ==================================================

        _update_job(

            job_id,

            status="processing",

            started_at=
                started_at.isoformat(),

            message=
                "変換処理を開始しています・・・"

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

        # ==================================================
        # 出力先
        # ==================================================

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
        # 時間指定判定
        # ==================================================

        full_download = _is_full_download(
            start_time,
            end_time
        )

        print(
            "[CONVERT] full_download:",
            full_download,
            flush=True
        )

        # ==================================================
        # ファイル名用サフィックス確認
        # ==================================================

        range_suffix = _build_range_suffix(

            start_time=
                start_time,

            end_time=
                end_time

        )

        print(
            "[CONVERT] filename range suffix:",
            range_suffix or "(none)",
            flush=True
        )

        # ==================================================
        # title / duration
        # ==================================================

        title = "YouTube Video"

        duration = None

        # ==================================================
        # MP3処理
        # ==================================================

        if "mp3" in outputs:

            _update_file(

                job_id,

                "mp3",

                status="processing",

                message="mp3 用動画をダウンロード中・・・"

            )

            _update_job(

                job_id,

                message="mp3 用動画をダウンロード中・・・"

            )

            print(
                "[CONVERT] MP3 source download START",
                flush=True
            )

            download_result = download_source(
                url
            )

            source_path = _validate_source(
                download_result
            )

            title = (
                download_result.get("title")
                or "YouTube Video"
            )

            duration = (
                download_result.get("duration")
            )

            _update_job(

                job_id,

                title=title,

                duration=duration,

                duration_text=
                    _format_seconds(
                        duration
                    ),

                message=
                    "動画のダウンロードが完了しました。"

            )

            print(
                "[CONVERT] MP3 source:",
                source_path,
                flush=True
            )

            print(
                "[CONVERT] MP3 source size:",
                source_path.stat().st_size,
                "bytes",
                flush=True
            )

            # ==================================================
            # MP3作成
            # ==================================================

            _update_file(

                job_id,

                "mp3",

                status="processing",

                message="mp3 変換中・・・"

            )

            _update_job(

                job_id,

                message="mp3 変換中・・・"

            )

            print(
                "[CONVERT] MP3 extraction START",
                flush=True
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

            if not mp3_result:

                raise RuntimeError(
                    "MP3作成結果が空です。"
                )

            # ==================================================
            # MP3完成後にリネーム
            #
            # ここで初めて時間範囲をファイル名に追加する。
            # ==================================================

            print(
                "[CONVERT] MP3 completed. Rename START",
                flush=True
            )

            renamed_mp3 = _rename_completed_file(

                result=
                    mp3_result,

                output_type=
                    "mp3",

                start_time=
                    start_time,

                end_time=
                    end_time

            )

            # ==================================================
            # MP3 Job更新
            # ==================================================

            _update_file(

                job_id,

                "mp3",

                status="complete",

                filename=
                    renamed_mp3.get(
                        "filename"
                    ),

                path=
                    renamed_mp3.get(
                        "path"
                    ),

                message=
                    "mp3 変換終了"

            )

            print(
                "[CONVERT] MP3 COMPLETE:",
                renamed_mp3,
                flush=True
            )

        # ==================================================
        # MP4処理
        # ==================================================

        if "mp4" in outputs:

            _update_file(

                job_id,

                "mp4",

                status="processing",

                message="mp4 ダウンロード中・・・"

            )

            _update_job(

                job_id,

                message="mp4 ダウンロード中・・・"

            )

            print(
                "[CONVERT] MP4 processing START",
                flush=True
            )

            # ==================================================
            # MP4全体
            #
            # FFmpegを使用せず、
            # yt-dlpが取得したMP4をそのまま完成ファイルとして使用。
            # ==================================================

            if full_download:

                print(
                    "[CONVERT] MP4 full download",
                    flush=True
                )

                mp4_result = create_mp4_full(

                    url=
                        url,

                    output_dir=
                        output_dir

                )

            # ==================================================
            # MP4時間指定
            #
            # 一時ファイルへダウンロード後、
            # FFmpegで指定区間を抽出。
            # ==================================================

            else:

                print(
                    "[CONVERT] MP4 range extraction",
                    flush=True
                )

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

            if not mp4_result:

                raise RuntimeError(
                    "MP4作成結果が空です。"
                )

            # ==================================================
            # MP4情報
            # ==================================================

            mp4_title = (
                mp4_result.get("title")
                or "YouTube Video"
            )

            if not title or title == "YouTube Video":

                title = mp4_title

            _update_job(

                job_id,

                title=title,

                message=
                    "mp4 ダウンロードが完了しました。"

            )

            # ==================================================
            # MP4完成後にリネーム
            #
            # ここで初めて時間範囲をファイル名に追加する。
            # ==================================================

            print(
                "[CONVERT] MP4 completed. Rename START",
                flush=True
            )

            renamed_mp4 = _rename_completed_file(

                result=
                    mp4_result,

                output_type=
                    "mp4",

                start_time=
                    start_time,

                end_time=
                    end_time

            )

            # ==================================================
            # MP4 Job更新
            # ==================================================

            _update_file(

                job_id,

                "mp4",

                status="complete",

                filename=
                    renamed_mp4.get(
                        "filename"
                    ),

                path=
                    renamed_mp4.get(
                        "path"
                    ),

                message=
                    "mp4 変換終了"

            )

            print(
                "[CONVERT] MP4 COMPLETE:",
                renamed_mp4,
                flush=True
            )

        # ==================================================
        # durationがまだない場合
        # ==================================================

        if duration is not None:

            _update_job(

                job_id,

                duration=
                    duration,

                duration_text=
                    _format_seconds(
                        duration
                    )

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

        print(
            "[CONVERT] Job ERROR:",
            job_id,
            repr(error),
            flush=True
        )

        traceback.print_exc()

        # ==================================================
        # processing中の出力をerrorへ
        # ==================================================

        for output_type in outputs:

            job = _get_job(
                job_id
            )

            if not job:

                continue

            file_status = (
                job["files"][output_type]["status"]
            )

            if file_status == "processing":

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

        # ==================================================
        # MP3用source削除
        #
        # MP4全体はsourceを作っていないので何もしない。
        # ==================================================

        if download_result:

            cleanup_download(
                download_result
            )

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
# Route
# ==========================================================

def register_convert(app):

    # ======================================================
    # /convert
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
            # 旧形式
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
            # 時間
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

                    # ------------------------------------------
                    # 両方0なら全体扱い
                    # ------------------------------------------

                    if (
                        start_value == 0
                        and
                        end_value == 0
                    ):

                        pass

                    # ------------------------------------------
                    # それ以外は終了時間 > 開始時間
                    # ------------------------------------------

                    elif end_value <= start_value:

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

            # ==================================================
            # Thread
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
    # /status
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
