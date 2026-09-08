# ==========================================================
# Subtitle Test
# subtitle_test.py
#
# app.py と同じ階層に配置
#
# 字幕処理テスト専用処理
#
# ① MP4保存
# ② SRT保存
# ③ subtitle.py で字幕MP4作成
#
# ==========================================================

import os
import sys
import time
import traceback
import shuti
from pathlib import Path

from config import DOWNLOAD_DIR
from subtitle import create_subtitle_mp4


# ==========================================================
# 設定
# ==========================================================

DOWNLOADS_DIR = Path(
    DOWNLOAD_DIR
).resolve()


# ==========================================================
# ログ
# ==========================================================

def log(message):
    """
    Renderログへ出力。
    """

    try:

        print(
            "[SUBTITLE_TEST]",
            message,
            flush=True
        )

    except Exception:
        pass


def log_separator():

    log(
        "=================================================="
    )


def log_exception(
    message,
    error
):
    """
    エラー内容とtracebackをRenderログへ出力。
    """

    log(
        message
    )

    try:

        log(
            f"TYPE: {type(error).__name__}"
        )

        log(
            f"ERROR: {error}"
        )

        log(
            "TRACEBACK START"
        )

        traceback_text = (
            traceback.format_exc()
        )

        if traceback_text:

            print(
                "[SUBTITLE_TEST] "
                + traceback_text,
                flush=True
            )

        log(
            "TRACEBACK END"
        )

    except Exception as traceback_error:

        log(
            f"traceback取得失敗: {traceback_error}"
        )


# ==========================================================
# 初期ログ
# ==========================================================

log_separator()

log(
    "subtitle_test.py LOAD"
)

try:

    log(
        f"__file__: "
        f"{Path(__file__).resolve()}"
    )

except Exception as error:

    log(
        f"__file__取得失敗: {error}"
    )

log(
    f"Python executable: {sys.executable}"
)

log(
    f"Python version: {sys.version}"
)

try:

    log(
        f"Current working directory: "
        f"{os.getcwd()}"
    )

except Exception as error:

    log(
        f"cwd取得失敗: {error}"
    )

log(
    f"DOWNLOAD_DIR: {DOWNLOAD_DIR}"
)

log(
    f"DOWNLOADS_DIR: {DOWNLOADS_DIR}"
)

log_separator()


# ==========================================================
# downloadsフォルダ確認
# ==========================================================

def ensure_downloads_directory():

    log(
        "downloadsフォルダ確認開始"
    )

    try:

        DOWNLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    except OSError as error:

        log_exception(
            "downloadsフォルダ作成失敗",
            error
        )

        raise RuntimeError(
            "downloadsフォルダを作成できませんでした: "
            + str(error)
        ) from error

    log(
        f"downloadsフォルダ確認OK: "
        f"{DOWNLOADS_DIR}"
    )

    return DOWNLOADS_DIR


# ==========================================================
# ファイル名安全化
# ==========================================================

def safe_filename(
    filename
):
    """
    パス情報を除去してファイル名だけにする。
    """

    if not filename:

        raise ValueError(
            "ファイル名が空です。"
        )

    filename = Path(
        filename
    ).name

    if not filename:

        raise ValueError(
            "ファイル名を取得できませんでした。"
        )

    return filename


# ==========================================================
# 拡張子確認
# ==========================================================

def validate_extension(
    filename,
    expected_extension
):

    actual_extension = (
        Path(
            filename
        ).suffix.lower()
    )

    if actual_extension != (
        expected_extension.lower()
    ):

        raise ValueError(
            f"{expected_extension}ファイルを指定してください。"
            f"現在の拡張子: {actual_extension}"
        )


# ==========================================================
# ローカルファイル保存
# ==========================================================

def save_file(
    file_path,
    expected_extension
):
    """
    ローカルファイルをdownloadsへ保存。

    同名ファイルがある場合は上書き。
    """

    source = Path(
        file_path
    ).resolve()

    if not source.exists():

        raise FileNotFoundError(
            f"入力ファイルが存在しません: {source}"
        )

    if not source.is_file():

        raise ValueError(
            f"入力ファイルが通常ファイルではありません: "
            f"{source}"
        )

    filename = safe_filename(
        source.name
    )

    validate_extension(
        filename,
        expected_extension
    )

    ensure_downloads_directory()

    destination = (
        DOWNLOADS_DIR
        /
        filename
    )

    log_separator()

    log(
        "ファイル保存開始"
    )

    log(
        f"source: {source}"
    )

    log(
        f"destination: {destination}"
    )

    try:

        shutil.copy2(
            source,
            destination
        )

    except Exception as error:

        log_exception(
            "ファイルコピー失敗",
            error
        )

        raise RuntimeError(
            "downloadsへのファイル保存に失敗しました: "
            + str(error)
        ) from error

    if not destination.exists():

        raise RuntimeError(
            "保存処理後にファイルが確認できません。"
        )

    try:

        size = (
            destination.stat().st_size
        )

    except OSError as error:

        raise RuntimeError(
            "保存ファイルのサイズ取得に失敗しました: "
            + str(error)
        ) from error

    if size <= 0:

        raise RuntimeError(
            "保存されたファイルのサイズが0 bytesです。"
        )

    log(
        f"保存成功: {destination}"
    )

    log(
        f"size: {size} bytes"
    )

    log_separator()

    return destination


# ==========================================================
# 字幕MP4作成
# ==========================================================

def create_subtitle_test_mp4(
    mp4_path,
    srt_path
):
    """
    subtitle.py の create_subtitle_mp4() を実行。
    """

    mp4_path = Path(
        mp4_path
    ).resolve()

    srt_path = Path(
        srt_path
    ).resolve()

    if not mp4_path.exists():

        raise FileNotFoundError(
            f"MP4が存在しません: {mp4_path}"
        )

    if not srt_path.exists():

        raise FileNotFoundError(
            f"SRTが存在しません: {srt_path}"
        )

    if not mp4_path.is_file():

        raise ValueError(
            f"MP4が通常ファイルではありません: "
            f"{mp4_path}"
        )

    if not srt_path.is_file():

        raise ValueError(
            f"SRTが通常ファイルではありません: "
            f"{srt_path}"
        )

    ensure_downloads_directory()

    output_stem = (
        mp4_path.stem
    )

    output_path = (
        DOWNLOADS_DIR
        /
        f"{output_stem}_sub_embed.mp4"
    )

    # ------------------------------------------------------
    # 同名ファイルが存在する場合は連番
    # ------------------------------------------------------

    if output_path.exists():

        counter = 2

        while True:

            candidate = (
                DOWNLOADS_DIR
                /
                f"{output_stem}_sub_embed_"
                f"{counter}.mp4"
            )

            if not candidate.exists():

                output_path = candidate

                break

            counter += 1

    log_separator()

    log(
        "字幕MP4作成開始"
    )

    log(
        f"MP4: {mp4_path}"
    )

    log(
        f"SRT: {srt_path}"
    )

    log(
        f"OUTPUT: {output_path}"
    )

    start_time = time.monotonic()

    try:

        result = create_subtitle_mp4(

            str(mp4_path),

            str(srt_path),

            str(output_path)

        )

    except Exception as error:

        log_exception(
            "create_subtitle_mp4()実行失敗",
            error
        )

        raise

    elapsed = (
        time.monotonic()
        -
        start_time
    )

    log(
        f"create_subtitle_mp4 result: {result}"
    )

    if result is None:

        raise RuntimeError(
            "subtitle.pyから出力パスが返されませんでした。"
        )

    result_path = Path(
        result
    ).resolve()

    if not result_path.exists():

        raise RuntimeError(
            "subtitle.pyは終了しましたが、"
            "字幕MP4が存在しません。"
            f"\n出力予定: {result_path}"
        )

    if not result_path.is_file():

        raise RuntimeError(
            "字幕MP4の出力先が通常ファイルではありません。"
            f"\n出力: {result_path}"
        )

    try:

        result_size = (
            result_path.stat().st_size
        )

    except OSError as error:

        raise RuntimeError(
            "字幕MP4のサイズを確認できませんでした: "
            + str(error)
        ) from error

    if result_size <= 0:

        raise RuntimeError(
            "字幕MP4のサイズが0 bytesです。"
            f"\n出力: {result_path}"
        )

    log(
        f"字幕MP4作成成功: {result_path}"
    )

    log(
        f"output size: {result_size} bytes"
    )

    log(
        f"elapsed: {elapsed:.1f} sec"
    )

    log_separator()

    return result_path


# ==========================================================
# downloads内ファイル一覧
# ==========================================================

def list_download_files():

    ensure_downloads_directory()

    files = []

    try:

        for path in sorted(
            DOWNLOADS_DIR.iterdir()
        ):

            if path.is_file():

                files.append(
                    path
                )

    except OSError as error:

        log_exception(
            "downloadsファイル一覧取得失敗",
            error
        )

        return []

    return files


# ==========================================================
# テスト実行
# ==========================================================

def run_test(
    mp4_path,
    srt_path
):
    """
    STEP 1～3を一括で実行する場合に使用。
    """

    log_separator()

    log(
        "Subtitle Test START"
    )

    try:

        # --------------------------------------------------
        # STEP 1
        # --------------------------------------------------

        saved_mp4 = save_file(
            mp4_path,
            ".mp4"
        )

        # --------------------------------------------------
        # STEP 2
        # --------------------------------------------------

        saved_srt = save_file(
            srt_path,
            ".srt"
        )

        # --------------------------------------------------
        # STEP 3
        # --------------------------------------------------

        output = create_subtitle_test_mp4(
            saved_mp4,
            saved_srt
        )

        log(
            "Subtitle Test SUCCESS"
        )

        return {
            "success": True,
            "mp4": str(saved_mp4),
            "srt": str(saved_srt),
            "output": str(output),
        }

    except Exception as error:

        log_exception(
            "Subtitle Test FAILED",
            error
        )

        return {
            "success": False,
            "error": str(error),
        }


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":

    log_separator()

    log(
        "subtitle_test.py CLI START"
    )

    if len(sys.argv) < 3:

        print(
            "使い方:"
        )

        print(
            "python subtitle_test.py "
            "<input.mp4> <input.srt>"
        )

        sys.exit(1)

    mp4_input = sys.argv[1]

    srt_input = sys.argv[2]

    result = run_test(
        mp4_input,
        srt_input
    )

    if result.get("success"):

        print(
            "\n[成功]"
        )

        print(
            f"MP4: {result['mp4']}"
        )

        print(
            f"SRT: {result['srt']}"
        )

        print(
            f"字幕MP4: {result['output']}"
        )

        sys.exit(0)

    else:

        print(
            "\n[失敗]"
        )

        print(
            result.get(
                "error",
                "不明なエラー"
            )
        )

        sys.exit(1)
