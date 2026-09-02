# =====================================
# YouTube Converter
# subtitle_mp4.py
#
# 字幕MP4連続処理管理
#
# 処理順:
#
# 1. MP4作成
# 2. MP3作成
# 3. SRT作成
# 4. 字幕MP4作成
#
# 注意:
# ・既存のMP4 / MP3 / SRT処理をできるだけ再利用する
# ・このファイルは「処理順序の管理」を担当する
# ・全工程成功後のみ complete にする
# =====================================

import traceback

from datetime import datetime
from pathlib import Path


# ==========================================================
# 共通
# ==========================================================

def _format_seconds(seconds):
    """
    秒数を HH:MM:SS / MM:SS に変換する。
    """

    if seconds is None:
        return ""

    try:
        total = int(float(seconds))
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
# 進捗通知
# ==========================================================

def _notify(
    callback,
    step,
    status,
    message,
    **extra
):
    """
    routes/convert.py 側へ進捗を通知する。

    callback が指定されていなければ
    コンソールへ出力するだけ。
    """

    data = {

        "step":
            step,

        "status":
            status,

        "message":
            message

    }

    data.update(extra)

    print(
        "[SUBTITLE_MP4]",
        data,
        flush=True
    )

    if callback:

        callback(
            data
        )


# ==========================================================
# 字幕MP4連続処理
# ==========================================================

def create_subtitle_mp4_job(
    url,
    output_dir,
    start_time=None,
    end_time=None,
    title=None,
    mp4_creator=None,
    mp3_creator=None,
    srt_creator=None,
    subtitle_mp4_creator=None,
    progress_callback=None
):
    """
    字幕MP4連続処理。

    処理順:

        MP4
         ↓
        MP3
         ↓
        SRT
         ↓
        字幕MP4

    各処理関数は外部から渡す。

    これにより既存コードを
    できるだけ変更せず利用できる。
    """

    started_at = datetime.now()

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    result = {

        "status":
            "processing",

        "step":
            "mp4",

        "title":
            title,

        "mp4":
            None,

        "mp3":
            None,

        "srt":
            None,

        "subtitle_mp4":
            None,

        "started_at":
            started_at.isoformat(),

        "completed_at":
            None,

        "execution_seconds":
            None,

        "message":
            "字幕MP4連続処理を開始しました。"

    }

    try:

        # ==================================================
        # STEP 1
        # MP4作成
        # ==================================================

        result["step"] = "mp4"

        _notify(

            progress_callback,

            "mp4",

            "processing",

            "MP4を作成しています・・・"

        )

        if mp4_creator is None:

            raise RuntimeError(
                "MP4作成関数が指定されていません。"
            )

        mp4_result = mp4_creator(

            url=url,

            output_dir=output_dir,

            start_time=start_time,

            end_time=end_time

        )

        if not mp4_result:

            raise RuntimeError(
                "MP4作成結果が空です。"
            )

        result["mp4"] = mp4_result

        _notify(

            progress_callback,

            "mp4",

            "complete",

            "MP4作成が完了しました。",

            file=mp4_result

        )

        # ==================================================
        # STEP 2
        # MP3作成
        # ==================================================

        result["step"] = "mp3"

        _notify(

            progress_callback,

            "mp3",

            "processing",

            "MP3を作成しています・・・"

        )

        if mp3_creator is None:

            raise RuntimeError(
                "MP3作成関数が指定されていません。"
            )

        mp3_result = mp3_creator(

            url=url,

            output_dir=output_dir,

            start_time=start_time,

            end_time=end_time,

            title=title

        )

        if not mp3_result:

            raise RuntimeError(
                "MP3作成結果が空です。"
            )

        result["mp3"] = mp3_result

        _notify(

            progress_callback,

            "mp3",

            "complete",

            "MP3作成が完了しました。",

            file=mp3_result

        )

        # ==================================================
        # STEP 3
        # SRT作成
        # ==================================================

        result["step"] = "srt"

        _notify(

            progress_callback,

            "srt",

            "processing",

            "SRTを作成しています・・・"

        )

        if srt_creator is None:

            raise RuntimeError(
                "SRT作成関数が指定されていません。"
            )

        srt_result = srt_creator(

            mp3_result=mp3_result,

            title=title,

            output_dir=output_dir

        )

        if not srt_result:

            raise RuntimeError(
                "SRT作成結果が空です。"
            )

        result["srt"] = srt_result

        _notify(

            progress_callback,

            "srt",

            "complete",

            "SRT作成が完了しました。",

            file=srt_result

        )

        # ==================================================
        # STEP 4
        # 字幕MP4作成
        # ==================================================

        result["step"] = "subtitle_mp4"

        _notify(

            progress_callback,

            "subtitle_mp4",

            "processing",

            "字幕付きMP4を作成しています・・・"

        )

        if subtitle_mp4_creator is None:

            raise RuntimeError(
                "字幕MP4作成関数が指定されていません。"
            )

        subtitle_result = subtitle_mp4_creator(

            mp4_result=mp4_result,

            srt_result=srt_result,

            title=title,

            output_dir=output_dir,

            start_time=start_time,

            end_time=end_time

        )

        if not subtitle_result:

            raise RuntimeError(
                "字幕MP4作成結果が空です。"
            )

        result["subtitle_mp4"] = subtitle_result

        _notify(

            progress_callback,

            "subtitle_mp4",

            "complete",

            "字幕付きMP4作成が完了しました。",

            file=subtitle_result

        )

        # ==================================================
        # 全工程完了
        # ==================================================

        completed_at = datetime.now()

        elapsed = (
            completed_at
            -
            started_at
        ).total_seconds()

        result.update({

            "status":
                "complete",

            "step":
                "complete",

            "completed_at":
                completed_at.isoformat(),

            "execution_seconds":
                elapsed,

            "execution_seconds_text":
                "処理時間: "
                +
                _format_seconds(
                    elapsed
                ),

            "message":
                "MP4 → MP3 → SRT → 字幕MP4 の全処理が完了しました。"

        })

        _notify(

            progress_callback,

            "complete",

            "complete",

            "MP4 → MP3 → SRT → 字幕MP4 の全処理が完了しました。",

            result=result

        )

        print(
            "[SUBTITLE_MP4] ALL COMPLETE",
            flush=True
        )

        return result

    except Exception as error:

        completed_at = datetime.now()

        elapsed = (
            completed_at
            -
            started_at
        ).total_seconds()

        result.update({

            "status":
                "error",

            "completed_at":
                completed_at.isoformat(),

            "execution_seconds":
                elapsed,

            "execution_seconds_text":
                "処理時間: "
                +
                _format_seconds(
                    elapsed
                ),

            "message":
                str(error),

            "error":
                str(error)

        })

        _notify(

            progress_callback,

            result.get(
                "step"
            ),

            "error",

            str(error),

            result=result

        )

        print(
            "[SUBTITLE_MP4] ERROR:",
            repr(error),
            flush=True
        )

        traceback.print_exc()

        return result
