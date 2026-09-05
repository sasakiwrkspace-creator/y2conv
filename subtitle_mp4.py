# ==========================================================
# subtitle_mp4.py
#
# タブ1「字幕mp4」専用
#
# 処理順:
#
#   ① MP4作成
#       ↓
#   ② MP3作成
#       ↓
#   ③ SRT作成
#       ↓
#   ④ 字幕MP4作成
#
# ==========================================================
#
# 重要:
#
#   ・MP4は create_mp4_full() / create_mp4_range() を使用。
#
#   ・MP3はMP4から作成する。
#     MP4がすでに指定区間の場合、
#     MP3側では時間指定を再適用しない。
#
#   ・SRTは create_srt_from_mp3() が生成したファイルを
#     そのまま使用する。
#
#   ・SRTのリネームは行わない。
#
#   ・時間指定が
#
#       00:00:00 / 00:00:00
#
#     の場合はファイル名に時間サフィックスを付けない。
#
#   ・時間指定がある場合だけ
#
#       _000600_000630
#
#     のようなサフィックスを付ける。
#
#   ・字幕MP4作成は
#
#       routes.subtitle_routes.create_subtitle_mp4()
#
#     に完全に任せる。
#
# ==========================================================
#
# Gemini SRT生成:
#
#   ・503 UNAVAILABLE等の一時的なGeminiエラーのみ
#     自動リトライする。
#
#   ・リトライ待機時間:
#
#       1回目失敗 → 10秒
#       2回目失敗 → 30秒
#       3回目失敗 → 60秒
#       4回目失敗 → 120秒
#
#   ・最大4回リトライ。
#   ・503以外のエラーは即座に失敗。
#
# ==========================================================


import os
import re
import time
import traceback

from pathlib import Path


# ==========================================================
# MP4作成
# ==========================================================

from ytdlp_stream import (
    create_mp4_full,
    create_mp4_range
)


# ==========================================================
# MP3作成
# ==========================================================

from media_extract import (
    create_mp3_from_file
)


# ==========================================================
# 字幕関連
#
# routes/subtitle_routes.py の共通関数を使用する。
# ==========================================================

from routes.subtitle_routes import (
    create_srt_from_mp3,
    create_subtitle_mp4 as create_subtitle_mp4_from_route
)


# ==========================================================
# Gemini SRT リトライ設定
# ==========================================================

# 初回実行
#   +
# 4回リトライ
#
# 合計最大5回Geminiへアクセスする。
#
SRT_MAX_RETRIES = 4


# ==========================================================
# リトライ待機時間
#
# 1回目失敗 → 10秒
# 2回目失敗 → 30秒
# 3回目失敗 → 60秒
# 4回目失敗 → 120秒
# ==========================================================

SRT_RETRY_DELAYS = [
    10,
    30,
    60,
    120
]


# ==========================================================
# 共通ログ
# ==========================================================

def log(message):

    print(
        "[SUBTITLE_MP4]",
        message,
        flush=True
    )


# ==========================================================
# Gemini一時エラー判定
#
# 503 UNAVAILABLE等だけをリトライ対象にする。
# ==========================================================

def is_gemini_temporary_error(error):

    if error is None:

        return False

    error_text = str(error)

    error_text_lower = (
        error_text
        .lower()
    )

    # ------------------------------------------------------
    # HTTP / API 503
    # ------------------------------------------------------

    if "503" in error_text:

        return True

    if "unavailable" in error_text_lower:

        return True

    # ------------------------------------------------------
    # Geminiの高負荷メッセージ
    # ------------------------------------------------------

    if "high demand" in error_text_lower:

        return True

    if "spikes in demand" in error_text_lower:

        return True

    # ------------------------------------------------------
    # 一時的なサービス利用不可
    # ------------------------------------------------------

    if "service unavailable" in error_text_lower:

        return True

    if "temporarily unavailable" in error_text_lower:

        return True

    return False


# ==========================================================
# SRT作成
#
# Gemini 503リトライ対応
# ==========================================================

def create_srt_with_retry(
    mp3_path
):

    log(
        "=========================================="
    )

    log(
        "Gemini SRT作成開始"
    )

    log(
        f"MP3: {mp3_path}"
    )

    log(
        f"最大リトライ回数: {SRT_MAX_RETRIES}"
    )

    log(
        f"リトライ待機: {SRT_RETRY_DELAYS}秒"
    )

    log(
        "=========================================="
    )

    attempt = 0

    while True:

        attempt += 1

        log(
            f"SRT作成試行 {attempt}/{SRT_MAX_RETRIES + 1}"
        )

        try:

            result = create_srt_from_mp3(
                str(mp3_path)
            )

            log(
                f"SRT作成成功: 試行 {attempt}"
            )

            return result

        except Exception as error:

            log(
                f"SRT作成エラー: 試行 {attempt}"
            )

            log(
                repr(error)
            )

            # --------------------------------------------------
            # 503等の一時エラーか確認
            # --------------------------------------------------

            temporary_error = (
                is_gemini_temporary_error(
                    error
                )
            )

            if not temporary_error:

                log(
                    "一時的なGeminiエラーではないため、"
                    "リトライせず終了します。"
                )

                raise

            # --------------------------------------------------
            # 最大リトライ回数確認
            # --------------------------------------------------

            if attempt > SRT_MAX_RETRIES:

                log(
                    "Gemini SRT作成の最大リトライ回数に到達しました。"
                )

                raise

            # --------------------------------------------------
            # 待機時間取得
            # --------------------------------------------------

            retry_index = attempt - 1

            if retry_index < len(
                SRT_RETRY_DELAYS
            ):

                delay = (
                    SRT_RETRY_DELAYS[
                        retry_index
                    ]
                )

            else:

                delay = (
                    SRT_RETRY_DELAYS[-1]
                )

            log(
                "Geminiが一時的に利用できません。"
            )

            log(
                f"リトライします: {delay}秒後"
            )

            log(
                f"次回試行: "
                f"{attempt + 1}/{SRT_MAX_RETRIES + 1}"
            )

            # --------------------------------------------------
            # 待機
            # --------------------------------------------------

            time.sleep(
                delay
            )

            log(
                "リトライ待機終了"
            )


# ==========================================================
# 時間 → 秒
# ==========================================================

def time_to_seconds(value):

    if value is None:

        return 0.0

    text = str(value).strip()

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
# 全体ダウンロード判定
#
# 00:00:00 ～ 00:00:00
#       ↓
# 全体
#
# None / None も全体として扱う。
# ==========================================================

def is_full_download(
    start_time=None,
    end_time=None
):

    return (
        time_to_seconds(start_time) == 0
        and
        time_to_seconds(end_time) == 0
    )


# ==========================================================
# ファイル名用時間
#
# 例:
#
#   0      → 000000
#   5      → 000005
#   65     → 000105
#   3665   → 010105
#
# ==========================================================

def format_filename_time(value):

    seconds = time_to_seconds(value)

    total_seconds = int(seconds)

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
# 時間サフィックス
#
# 全体:
#
#   ""
#
# 指定区間:
#
#   _000600_000630
#
# ==========================================================

def build_range_suffix(
    start_time=None,
    end_time=None
):

    if is_full_download(
        start_time=start_time,
        end_time=end_time
    ):

        return ""

    return (
        "_"
        +
        format_filename_time(start_time)
        +
        "_"
        +
        format_filename_time(end_time)
    )


# ==========================================================
# ファイル確認
# ==========================================================

def validate_file(
    file_path,
    extension,
    label
):

    if not file_path:

        raise RuntimeError(
            f"{label}のパスがありません。"
        )

    path = Path(file_path)

    if not path.exists():

        raise FileNotFoundError(
            f"{label}がありません: {path}"
        )

    if not path.is_file():

        raise RuntimeError(
            f"{label}のパスがファイルではありません: "
            +
            str(path)
        )

    if path.suffix.lower() != extension.lower():

        raise RuntimeError(
            f"{label}の拡張子が不正です: "
            +
            str(path)
        )

    try:

        size = path.stat().st_size

    except OSError as error:

        raise RuntimeError(
            f"{label}のサイズを確認できません: "
            +
            str(error)
        )

    if size <= 0:

        raise RuntimeError(
            f"{label}のファイルサイズが0 bytesです: "
            +
            str(path)
        )

    return path


# ==========================================================
# MP4結果確認
# ==========================================================

def validate_mp4_result(result):

    if not result:

        raise RuntimeError(
            "MP4作成結果が空です。"
        )

    result_path = result.get("path")

    if not result_path:

        raise RuntimeError(
            "MP4作成結果にpathがありません。"
        )

    return validate_file(
        result_path,
        ".mp4",
        "MP4"
    )


# ==========================================================
# MP4タイトル取得
# ==========================================================

def get_title_from_result(result):

    if not result:

        return "YouTube Video"

    title = (
        result.get("title")
        or
        "YouTube Video"
    )

    return str(title).strip() or "YouTube Video"


# ==========================================================
# MP4 duration取得
# ==========================================================

def get_duration_from_result(result):

    if not result:

        return None

    return result.get("duration")


# ==========================================================
# MP3結果確認
# ==========================================================

def validate_mp3_result(result):

    if not result:

        raise RuntimeError(
            "MP3作成結果が空です。"
        )

    result_path = result.get("path")

    if not result_path:

        raise RuntimeError(
            "MP3作成結果にpathがありません。"
        )

    return validate_file(
        result_path,
        ".mp3",
        "MP3"
    )


# ==========================================================
# タイトル安全化
# ==========================================================

def sanitize_filename(value):

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

    text = text.rstrip(" .")

    if not text:

        text = "YouTube Video"

    text = text[:180]

    text = text.rstrip(" .")

    if not text:

        text = "YouTube Video"

    return text


# ==========================================================
# MP4 / MP3 リネーム
#
# 全体:
#
#   タイトル.mp4
#   タイトル.mp3
#
# 指定区間:
#
#   タイトル_000600_000630.mp4
#   タイトル_000600_000630.mp3
#
# ==========================================================

def rename_output_file(
    result,
    output_type,
    title,
    start_time=None,
    end_time=None
):

    if not result:

        raise RuntimeError(
            f"{output_type}作成結果がありません。"
        )

    original_path_text = result.get("path")

    if not original_path_text:

        raise RuntimeError(
            f"{output_type}作成結果にpathがありません。"
        )

    extension = "." + output_type.lower()

    original_path = validate_file(
        original_path_text,
        extension,
        output_type.upper()
    )

    safe_title = sanitize_filename(title)

    range_suffix = build_range_suffix(
        start_time=start_time,
        end_time=end_time
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

    log(
        f"{output_type.upper()} rename:"
    )

    log(
        f"  {original_path}"
    )

    log(
        f"  -> {new_path}"
    )

    if original_path != new_path:

        if new_path.exists():

            log(
                f"既存ファイル削除: {new_path}"
            )

            new_path.unlink()

        original_path.rename(
            new_path
        )

    return validate_file(
        new_path,
        extension,
        output_type.upper()
    )


# ==========================================================
# SRT結果確認
#
# ★重要
#
# SRTはリネームしない。
#
# create_srt_from_mp3() の戻り値:
#
#   srt_path
#
# を最優先で使用する。
#
# srt_pathがない場合だけ
#
#   srt_file
#
# をoutput_dir基準で取得する。
#
# ==========================================================

def validate_srt_result(
    result,
    output_dir
):

    if not result:

        raise RuntimeError(
            "SRT作成結果が空です。"
        )

    log(
        f"SRT result: {result}"
    )

    # ------------------------------------------------------
    # srt_pathを最優先
    # ------------------------------------------------------

    srt_path_text = result.get(
        "srt_path"
    )

    if srt_path_text:

        srt_path = Path(
            srt_path_text
        )

    else:

        # --------------------------------------------------
        # srt_fileを使用
        #
        # create_srt_from_mp3() が返したファイル名を
        # そのまま使用する。
        # --------------------------------------------------

        srt_filename = result.get(
            "srt_file"
        )

        if not srt_filename:

            raise RuntimeError(
                "SRT作成結果に"
                "srt_path / srt_fileがありません。"
            )

        srt_filename = os.path.basename(
            str(srt_filename)
        )

        srt_path = (
            Path(output_dir)
            /
            srt_filename
        )

    # ------------------------------------------------------
    # SRTはここではリネームしない。
    # ------------------------------------------------------

    return validate_file(
        srt_path,
        ".srt",
        "SRT"
    )


# ==========================================================
# 字幕MP4結果確認
#
# create_subtitle_mp4_from_route() の戻り値:
#
#   subtitle_mp4_path
#
# を優先。
#
# 念のためpathも確認する。
#
# ==========================================================

def validate_subtitle_mp4_result(result):

    if not result:

        raise RuntimeError(
            "字幕MP4作成結果が空です。"
        )

    log(
        f"字幕MP4 result: {result}"
    )

    result_path = (
        result.get(
            "subtitle_mp4_path"
        )
        or
        result.get(
            "path"
        )
    )

    if not result_path:

        raise RuntimeError(
            "字幕MP4作成結果に"
            "subtitle_mp4_path / pathがありません。"
        )

    return validate_file(
        result_path,
        ".mp4",
        "字幕MP4"
    )


# ==========================================================
# 字幕MP4ファイル名統一
#
# 字幕MP4の作成処理そのものは
# routes.subtitle_routes.py に任せる。
#
# 作成後、最終ファイル名だけ統一する。
#
# 全体:
#
#   タイトル_字幕.mp4
#
# 指定区間:
#
#   タイトル_000600_000630_字幕.mp4
#
# ==========================================================

def rename_subtitle_mp4(
    subtitle_mp4_path,
    title,
    start_time=None,
    end_time=None
):

    subtitle_mp4_path = validate_file(
        subtitle_mp4_path,
        ".mp4",
        "字幕MP4"
    )

    safe_title = sanitize_filename(
        title
    )

    range_suffix = build_range_suffix(
        start_time=start_time,
        end_time=end_time
    )

    new_filename = (
        safe_title
        +
        range_suffix
        +
        "_字幕.mp4"
    )

    new_path = (
        subtitle_mp4_path.parent
        /
        new_filename
    )

    log(
        "字幕MP4 rename:"
    )

    log(
        f"  {subtitle_mp4_path}"
    )

    log(
        f"  -> {new_path}"
    )

    if subtitle_mp4_path != new_path:

        if new_path.exists():

            log(
                f"既存字幕MP4削除: {new_path}"
            )

            new_path.unlink()

        subtitle_mp4_path.rename(
            new_path
        )

    return validate_file(
        new_path,
        ".mp4",
        "字幕MP4"
    )


# ==========================================================
# 連続処理本体
#
# ==========================================================

def create_subtitle_mp4_pipeline(
    url,
    start_time=None,
    end_time=None,
    output_dir=None
):

    log(
        "=========================================="
    )

    log(
        "字幕MP4連続処理 START"
    )

    log(
        "=========================================="
    )

    # ======================================================
    # 出力先
    # ======================================================

    if output_dir:

        output_dir = Path(
            output_dir
        )

    else:

        output_dir = (
            Path(os.getcwd())
            /
            "downloads"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    log(
        f"OUTPUT_DIR: {output_dir}"
    )

    # ======================================================
    # URL確認
    # ======================================================

    if not url:

        raise ValueError(
            "YouTube URLが指定されていません。"
        )

    # ======================================================
    # 時間確認
    # ======================================================

    try:

        start_seconds = time_to_seconds(
            start_time
        )

        end_seconds = time_to_seconds(
            end_time
        )

    except Exception as error:

        raise ValueError(
            "開始時間または終了時間が不正です: "
            +
            str(error)
        ) from error

    if start_seconds < 0:

        raise ValueError(
            "開始時間は0秒以上である必要があります。"
        )

    if end_seconds < 0:

        raise ValueError(
            "終了時間は0秒以上である必要があります。"
        )

    if not (
        start_seconds == 0
        and
        end_seconds == 0
    ):

        if end_seconds <= start_seconds:

            raise ValueError(
                "終了時間は開始時間より後である必要があります。"
            )

    # ======================================================
    # 全体判定
    # ======================================================

    full_download = is_full_download(
        start_time=start_time,
        end_time=end_time
    )

    log(
        f"FULL_DOWNLOAD: {full_download}"
    )

    log(
        f"START_TIME: {start_time}"
    )

    log(
        f"END_TIME: {end_time}"
    )

    title = "YouTube Video"

    duration = None

    mp4_path = None
    mp3_path = None
    srt_path = None
    subtitle_mp4_path = None

    # ======================================================
    # ① MP4
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 1 / 4"
    )

    log(
        "MP4作成開始"
    )

    log(
        "------------------------------------------"
    )

    try:

        if full_download:

            log(
                "MP4 full download"
            )

            mp4_result = create_mp4_full(
                url=url,
                output_dir=output_dir
            )

        else:

            log(
                "MP4 range download"
            )

            log(
                f"range: {start_time} -> {end_time}"
            )

            mp4_result = create_mp4_range(
                url=url,
                output_dir=output_dir,
                start_time=start_time,
                end_time=end_time
            )

        # --------------------------------------------------
        # MP4確認
        # --------------------------------------------------

        mp4_path = validate_mp4_result(
            mp4_result
        )

        # --------------------------------------------------
        # タイトル
        # --------------------------------------------------

        title = get_title_from_result(
            mp4_result
        )

        # --------------------------------------------------
        # duration
        # --------------------------------------------------

        duration = get_duration_from_result(
            mp4_result
        )

        # --------------------------------------------------
        # MP4リネーム
        # --------------------------------------------------

        mp4_path = rename_output_file(
            result={
                "path": str(mp4_path)
            },
            output_type="mp4",
            title=title,
            start_time=start_time,
            end_time=end_time
        )

        log(
            f"STEP 1 COMPLETE: {mp4_path}"
        )

    except Exception as error:

        log(
            "STEP 1 ERROR"
        )

        log(
            repr(error)
        )

        traceback.print_exc()

        raise RuntimeError(
            "MP4作成に失敗しました: "
            +
            str(error)
        ) from error

    # ======================================================
    # ② MP3
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 2 / 4"
    )

    log(
        "MP3作成開始"
    )

    log(
        "------------------------------------------"
    )

    try:

        # --------------------------------------------------
        # MP4はすでに指定区間に切り出されているため、
        # MP3側では時間指定を再適用しない。
        # --------------------------------------------------

        log(
            "MP3 source:"
        )

        log(
            str(mp4_path)
        )

        log(
            "MP3時間再指定なし"
        )

        mp3_result = create_mp3_from_file(
            input_file=str(mp4_path),
            output_dir=output_dir,
            title=title,
            start_time=None,
            end_time=None
        )

        # --------------------------------------------------
        # MP3確認
        # --------------------------------------------------

        mp3_path = validate_mp3_result(
            mp3_result
        )

        # --------------------------------------------------
        # MP3リネーム
        # --------------------------------------------------

        mp3_path = rename_output_file(
            result={
                "path": str(mp3_path)
            },
            output_type="mp3",
            title=title,
            start_time=start_time,
            end_time=end_time
        )

        log(
            f"STEP 2 COMPLETE: {mp3_path}"
        )

    except Exception as error:

        log(
            "STEP 2 ERROR"
        )

        log(
            repr(error)
        )

        traceback.print_exc()

        raise RuntimeError(
            "MP3作成に失敗しました: "
            +
            str(error)
        ) from error

    # ======================================================
    # ③ SRT
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 3 / 4"
    )

    log(
        "SRT作成開始"
    )

    log(
        "------------------------------------------"
    )

    try:

        # --------------------------------------------------
        # ★SRTは作成された名前をそのまま使用
        # --------------------------------------------------

        log(
            "SRT source MP3:"
        )

        log(
            str(mp3_path)
        )

        log(
            "create_srt_from_mp3() を実行します"
        )

        # --------------------------------------------------
        # ★Gemini 503リトライ対応
        # --------------------------------------------------

        srt_result = create_srt_with_retry(
            mp3_path
        )

        log(
            f"SRT作成結果: {srt_result}"
        )

        # --------------------------------------------------
        # SRT確認
        # --------------------------------------------------

        srt_path = validate_srt_result(
            result=srt_result,
            output_dir=output_dir
        )

        # --------------------------------------------------
        # ★SRTはリネームしない
        # --------------------------------------------------

        log(
            "SRTは作成されたファイル名をそのまま使用: "
            f"{srt_path}"
        )

        log(
            f"STEP 3 COMPLETE: {srt_path}"
        )

    except Exception as error:

        log(
            "STEP 3 ERROR"
        )

        log(
            repr(error)
        )

        traceback.print_exc()

        raise RuntimeError(
            "SRT作成に失敗しました: "
            +
            str(error)
        ) from error

    # ======================================================
    # ④ 字幕MP4
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "STEP 4 / 4"
    )

    log(
        "字幕MP4作成開始"
    )

    log(
        "------------------------------------------"
    )

    try:

        # --------------------------------------------------
        # ★字幕MP4作成は
        #
        # routes.subtitle_routes.py
        #
        # の create_subtitle_mp4() に完全に任せる。
        #
        # 入力:
        #
        #   ① MP4
        #   ② SRT
        #
        # 時間指定はここでは渡さない。
        # --------------------------------------------------

        log(
            "Subtitle MP4 source:"
        )

        log(
            f"MP4: {mp4_path}"
        )

        log(
            f"SRT: {srt_path}"
        )

        log(
            "routes.subtitle_routes.create_subtitle_mp4() "
            "を呼び出します"
        )

        subtitle_result = (
            create_subtitle_mp4_from_route(
                str(mp4_path),
                str(srt_path)
            )
        )

        log(
            f"字幕MP4作成結果: {subtitle_result}"
        )

        # --------------------------------------------------
        # 字幕MP4確認
        # --------------------------------------------------

        subtitle_mp4_path = (
            validate_subtitle_mp4_result(
                subtitle_result
            )
        )

        log(
            f"STEP 4 RAW COMPLETE: {subtitle_mp4_path}"
        )

        # --------------------------------------------------
        # 字幕MP4ファイル名統一
        #
        # 全体:
        #
        #   タイトル_字幕.mp4
        #
        # 指定区間:
        #
        #   タイトル_000600_000630_字幕.mp4
        #
        # --------------------------------------------------

        subtitle_mp4_path = rename_subtitle_mp4(
            subtitle_mp4_path=subtitle_mp4_path,
            title=title,
            start_time=start_time,
            end_time=end_time
        )

        log(
            f"STEP 4 COMPLETE: {subtitle_mp4_path}"
        )

    except Exception as error:

        log(
            "STEP 4 ERROR"
        )

        log(
            repr(error)
        )

        traceback.print_exc()

        raise RuntimeError(
            "字幕MP4作成に失敗しました: "
            +
            str(error)
        ) from error

    # ======================================================
    # 最終確認
    # ======================================================

    log(
        "=========================================="
    )

    log(
        "最終ファイル確認"
    )

    log(
        "=========================================="
    )

    mp4_path = validate_file(
        mp4_path,
        ".mp4",
        "MP4"
    )

    mp3_path = validate_file(
        mp3_path,
        ".mp3",
        "MP3"
    )

    srt_path = validate_file(
        srt_path,
        ".srt",
        "SRT"
    )

    subtitle_mp4_path = validate_file(
        subtitle_mp4_path,
        ".mp4",
        "字幕MP4"
    )

    # ======================================================
    # 完了ログ
    # ======================================================

    log(
        "=========================================="
    )

    log(
        "字幕MP4連続処理 COMPLETE"
    )

    log(
        "=========================================="
    )

    log(
        f"MP4: {mp4_path}"
    )

    log(
        f"MP3: {mp3_path}"
    )

    log(
        f"SRT: {srt_path}"
    )

    log(
        f"字幕MP4: {subtitle_mp4_path}"
    )

    log(
        "=========================================="
    )

    # ======================================================
    # 戻り値
    # ======================================================

    return {

        "success":
            True,

        "title":
            title,

        "duration":
            duration,

        "mp4_path":
            str(mp4_path),

        "mp4_file":
            mp4_path.name,

        "mp3_path":
            str(mp3_path),

        "mp3_file":
            mp3_path.name,

        "srt_path":
            str(srt_path),

        "srt_file":
            srt_path.name,

        "subtitle_mp4_path":
            str(subtitle_mp4_path),

        "subtitle_mp4_file":
            subtitle_mp4_path.name

    }


# ==========================================================
# 外部向けエントリーポイント
# ==========================================================

def create_subtitle_mp4(
    url,
    start_time=None,
    end_time=None,
    output_dir=None
):

    return create_subtitle_mp4_pipeline(
        url=url,
        start_time=start_time,
        end_time=end_time,
        output_dir=output_dir
    )


# ==========================================================
# テスト用
#
# python subtitle_mp4.py URL
#
# または
#
# python subtitle_mp4.py URL 00:00:05 00:00:10
#
# ==========================================================

if __name__ == "__main__":

    import sys

    # ======================================================
    # 引数確認
    # ======================================================

    if len(sys.argv) < 2:

        print()
        print(
            "使用方法:"
        )
        print()
        print(
            "python subtitle_mp4.py YouTube_URL"
        )
        print()
        print(
            "時間指定:"
        )
        print()
        print(
            "python subtitle_mp4.py "
            "YouTube_URL "
            "00:00:05 "
            "00:00:10"
        )
        print()

        sys.exit(1)

    # ======================================================
    # URL
    # ======================================================

    url = sys.argv[1]

    # ======================================================
    # 開始時間
    # ======================================================

    start_time = (
        sys.argv[2]
        if len(sys.argv) >= 3
        else None
    )

    # ======================================================
    # 終了時間
    # ======================================================

    end_time = (
        sys.argv[3]
        if len(sys.argv) >= 4
        else None
    )

    # ======================================================
    # 実行
    # ======================================================

    try:

        result = create_subtitle_mp4_pipeline(
            url=url,
            start_time=start_time,
            end_time=end_time
        )

        print()

        print(
            "=========================================="
        )

        print(
            "字幕MP4連続処理成功"
        )

        print(
            "=========================================="
        )

        print(
            "MP4:",
            result["mp4_file"]
        )

        print(
            "MP3:",
            result["mp3_file"]
        )

        print(
            "SRT:",
            result["srt_file"]
        )

        print(
            "字幕MP4:",
            result["subtitle_mp4_file"]
        )

        print(
            "=========================================="
        )

        print()

        sys.exit(0)

    except Exception as error:

        print()

        print(
            "=========================================="
        )

        print(
            "字幕MP4連続処理失敗"
        )

        print(
            "=========================================="
        )

        print(
            str(error)
        )

        print(
            "=========================================="
        )

        traceback.print_exc()

        print()

        sys.exit(1)
