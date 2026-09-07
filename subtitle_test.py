# ==========================================================
# Subtitle Test
# subtitle_test.py
#
# 字幕処理テスト専用画面
#
# ① ローカルMP4をアップロード
#    -> config.py の DOWNLOAD_DIR に保存
#
# ② ローカルSRTをアップロード
#    -> config.py の DOWNLOAD_DIR に保存
#
# ③ subtitle.py を使用して字幕MP4を作成
#    -> config.py の DOWNLOAD_DIR に保存
#
# ==========================================================

import os
import sys
import time
import shutil
import traceback

from pathlib import Path

import streamlit as st

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
    Renderログへテスト処理ログを出力。
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


def log_exception(message, error):
    """
    エラーとtracebackをRenderログへ出力。
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

        traceback_text = traceback.format_exc()

        if traceback_text:

            print(
                "[SUBTITLE_TEST] " + traceback_text,
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
# ページ設定
# ==========================================================

st.set_page_config(

    page_title="Subtitle Test",

    page_icon="🎬",

    layout="wide"

)


# ==========================================================
# モジュール読み込みログ
# ==========================================================

log_separator()

log(
    "subtitle_test.py START"
)

try:

    log(
        f"subtitle_test.py __file__: "
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
    f"DOWNLOAD_DIR config: {DOWNLOAD_DIR}"
)

log(
    f"DOWNLOADS_DIR resolved: {DOWNLOADS_DIR}"
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
            +
            str(error)

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
    ファイル名だけを取得して安全化。
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

    if actual_extension != expected_extension.lower():

        raise ValueError(

            f"{expected_extension}ファイルを選択してください。"
            f"現在の拡張子: {actual_extension}"

        )


# ==========================================================
# アップロードファイル保存
# ==========================================================

def save_uploaded_file(
    uploaded_file,
    expected_extension
):

    """
    Streamlit UploadedFileをdownloadsへ保存。

    同名ファイルがある場合は上書きする。
    """

    if uploaded_file is None:

        raise ValueError(
            "ファイルが選択されていません。"
        )

    ensure_downloads_directory()

    original_name = (
        safe_filename(
            uploaded_file.name
        )
    )

    validate_extension(

        original_name,

        expected_extension

    )

    destination = (
        DOWNLOADS_DIR
        /
        original_name
    )

    log_separator()

    log(
        "アップロードファイル保存開始"
    )

    log(
        f"original filename: {original_name}"
    )

    log(
        f"destination: {destination}"
    )

    try:

        file_bytes = (
            uploaded_file.getvalue()
        )

    except Exception as error:

        log_exception(
            "アップロードデータ取得失敗",
            error
        )

        raise RuntimeError(

            "アップロードされたファイルを"
            "読み込めませんでした: "
            +
            str(error)

        ) from error

    if not file_bytes:

        raise ValueError(
            "アップロードされたファイルが空です。"
        )

    log(
        f"upload size: {len(file_bytes)} bytes"
    )

    try:

        with open(

            destination,

            "wb"

        ) as file:

            file.write(
                file_bytes
            )

    except OSError as error:

        log_exception(
            "ファイル保存失敗",
            error
        )

        raise RuntimeError(

            "downloadsへのファイル保存に失敗しました: "
            +
            str(error)

        ) from error

    if not destination.exists():

        raise RuntimeError(

            "保存処理は完了しましたが、"
            "保存先ファイルが存在しません。"

        )

    try:

        saved_size = (
            destination.stat().st_size
        )

    except OSError as error:

        log_exception(
            "保存ファイルサイズ取得失敗",
            error
        )

        raise RuntimeError(

            "保存されたファイルを確認できませんでした: "
            +
            str(error)

        ) from error

    if saved_size <= 0:

        raise RuntimeError(
            "保存されたファイルのサイズが0 bytesです。"
        )

    log(
        f"saved size: {saved_size} bytes"
    )

    log(
        f"保存成功: {destination}"
    )

    log_separator()

    return destination


# ==========================================================
# downloads内ファイル確認
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
# ファイル情報表示
# ==========================================================

def display_file_info(
    file_path
):

    path = Path(
        file_path
    )

    if not path.exists():

        st.error(
            f"ファイルが存在しません: {path}"
        )

        return

    try:

        size = path.stat().st_size

    except OSError:

        size = 0

    st.write(
        f"**ファイル名:** `{path.name}`"
    )

    st.write(
        f"**保存先:** `{path}`"
    )

    st.write(
        f"**サイズ:** `{size:,} bytes`"
    )


# ==========================================================
# セッション状態初期化
# ==========================================================

if "subtitle_test_mp4" not in st.session_state:

    st.session_state.subtitle_test_mp4 = None


if "subtitle_test_srt" not in st.session_state:

    st.session_state.subtitle_test_srt = None


if "subtitle_test_output" not in st.session_state:

    st.session_state.subtitle_test_output = None


if "subtitle_test_step1_done" not in st.session_state:

    st.session_state.subtitle_test_step1_done = False


if "subtitle_test_step2_done" not in st.session_state:

    st.session_state.subtitle_test_step2_done = False


if "subtitle_test_step3_done" not in st.session_state:

    st.session_state.subtitle_test_step3_done = False


# ==========================================================
# タイトル
# ==========================================================

st.title(
    "🎬 Subtitle Test"
)

st.caption(
    "字幕処理を3段階に分けて、一つずつ確認するためのテスト画面です。"
)


# ==========================================================
# 保存先表示
# ==========================================================

st.info(

    "字幕処理用の保存先\n\n"
    f"`{DOWNLOADS_DIR}`\n\n"
    "※ config.py の DOWNLOAD_DIR を使用しています。"

)


# ==========================================================
# STEP 1
# ==========================================================

st.header(
    "① MP4をアップロード"
)

st.write(
    "ローカルPCからMP4を選択し、"
    "config.py の DOWNLOAD_DIR へ保存します。"
)

uploaded_mp4 = st.file_uploader(

    "MP4ファイルを選択",

    type=["mp4"],

    key="subtitle_test_mp4_uploader"

)


if uploaded_mp4 is not None:

    st.write(
        f"選択ファイル: `{uploaded_mp4.name}`"
    )

    try:

        upload_size = (
            len(
                uploaded_mp4.getvalue()
            )
        )

        st.write(
            f"サイズ: `{upload_size:,} bytes`"
        )

    except Exception:

        pass


if st.button(

    "① MP4をdownloadsへ保存",

    key="subtitle_test_step1_button",

    type="primary"

):

    log_separator()

    log(
        "STEP 1 BUTTON CLICK"
    )

    try:

        if uploaded_mp4 is None:

            st.error(
                "先にMP4ファイルを選択してください。"
            )

        else:

            mp4_path = (
                save_uploaded_file(

                    uploaded_mp4,

                    ".mp4"

                )
            )

            st.session_state.subtitle_test_mp4 = (
                str(
                    mp4_path
                )
            )

            st.session_state.subtitle_test_step1_done = True

            st.success(
                "① MP4の保存に成功しました。"
            )

            display_file_info(
                mp4_path
            )

    except Exception as error:

        log_exception(
            "STEP 1失敗",
            error
        )

        st.session_state.subtitle_test_step1_done = False

        st.error(
            f"① MP4保存失敗: {error}"
        )


if st.session_state.subtitle_test_step1_done:

    st.success(
        "✓ STEP 1 完了"
    )

    if st.session_state.subtitle_test_mp4:

        display_file_info(
            st.session_state.subtitle_test_mp4
        )


# ==========================================================
# 区切り
# ==========================================================

st.divider()


# ==========================================================
# STEP 2
# ==========================================================

st.header(
    "② SRTをアップロード"
)

st.write(
    "ローカルPCからSRTを選択し、"
    "config.py の DOWNLOAD_DIR へ保存します。"
)

uploaded_srt = st.file_uploader(

    "SRTファイルを選択",

    type=["srt"],

    key="subtitle_test_srt_uploader"

)


if uploaded_srt is not None:

    st.write(
        f"選択ファイル: `{uploaded_srt.name}`"
    )

    try:

        upload_size = (
            len(
                uploaded_srt.getvalue()
            )
        )

        st.write(
            f"サイズ: `{upload_size:,} bytes`"
        )

    except Exception:

        pass


if st.button(

    "② SRTをdownloadsへ保存",

    key="subtitle_test_step2_button",

    type="primary"

):

    log_separator()

    log(
        "STEP 2 BUTTON CLICK"
    )

    try:

        if uploaded_srt is None:

            st.error(
                "先にSRTファイルを選択してください。"
            )

        else:

            srt_path = (
                save_uploaded_file(

                    uploaded_srt,

                    ".srt"

                )
            )

            st.session_state.subtitle_test_srt = (
                str(
                    srt_path
                )
            )

            st.session_state.subtitle_test_step2_done = True

            st.success(
                "② SRTの保存に成功しました。"
            )

            display_file_info(
                srt_path
            )

    except Exception as error:

        log_exception(
            "STEP 2失敗",
            error
        )

        st.session_state.subtitle_test_step2_done = False

        st.error(
            f"② SRT保存失敗: {error}"
        )


if st.session_state.subtitle_test_step2_done:

    st.success(
        "✓ STEP 2 完了"
    )

    if st.session_state.subtitle_test_srt:

        display_file_info(
            st.session_state.subtitle_test_srt
        )


# ==========================================================
# 区切り
# ==========================================================

st.divider()


# ==========================================================
# STEP 3
# ==========================================================

st.header(
    "③ FFmpegで字幕MP4を作成"
)

st.write(
    "downloadsに保存されたMP4とSRTを使用して、"
    "`subtitle.py` の処理を実行します。"
)


# ==========================================================
# 現在の入力ファイル表示
# ==========================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "入力MP4"
    )

    if st.session_state.subtitle_test_mp4:

        display_file_info(
            st.session_state.subtitle_test_mp4
        )

    else:

        st.warning(
            "まだMP4が保存されていません。"
        )


with col2:

    st.subheader(
        "入力SRT"
    )

    if st.session_state.subtitle_test_srt:

        display_file_info(
            st.session_state.subtitle_test_srt
        )

    else:

        st.warning(
            "まだSRTが保存されていません。"
        )


# ==========================================================
# STEP 3実行
# ==========================================================

step3_ready = (

    st.session_state.subtitle_test_mp4
    and
    st.session_state.subtitle_test_srt

)


if not step3_ready:

    st.info(
        "STEP 3を実行するには、"
        "STEP 1とSTEP 2を先に完了してください。"
    )


if st.button(

    "③ FFmpegを実行して字幕MP4を作成",

    key="subtitle_test_step3_button",

    type="primary",

    disabled=not step3_ready

):

    log_separator()

    log(
        "STEP 3 BUTTON CLICK"
    )

    start_time = time.monotonic()

    mp4_path = Path(
        st.session_state.subtitle_test_mp4
    )

    srt_path = Path(
        st.session_state.subtitle_test_srt
    )

    log(
        f"STEP 3 MP4: {mp4_path}"
    )

    log(
        f"STEP 3 SRT: {srt_path}"
    )

    log(
        f"DOWNLOADS_DIR: {DOWNLOADS_DIR}"
    )

    try:

        # ==================================================
        # 入力ファイル確認
        # ==================================================

        if not mp4_path.exists():

            raise FileNotFoundError(

                f"MP4が存在しません: "
                f"{mp4_path}"

            )

        if not srt_path.exists():

            raise FileNotFoundError(

                f"SRTが存在しません: "
                f"{srt_path}"

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

        # ==================================================
        # 出力ファイル名
        # ==================================================

        output_stem = (
            mp4_path.stem
        )

        output_path = (

            DOWNLOADS_DIR
            /
            f"{output_stem}_sub_embed.mp4"

        )

        # ==================================================
        # 同名出力がある場合
        # ==================================================

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

        log(
            f"output_path: {output_path}"
        )

        # ==================================================
        # subtitle.py実行
        # ==================================================

        log(
            "subtitle.py create_subtitle_mp4()開始"
        )

        with st.spinner(

            "FFmpegで字幕MP4を作成しています。"
            "しばらくお待ちください..."

        ):

            result = create_subtitle_mp4(

                str(mp4_path),

                str(srt_path),

                str(output_path)

            )

        log(
            f"create_subtitle_mp4 result: {result}"
        )

        # ==================================================
        # 結果確認
        # ==================================================

        if result is None:

            raise RuntimeError(

                "subtitle.pyから出力パスが"
                "返されませんでした。"

            )

        result_path = Path(
            result
        ).resolve()

        log(
            f"result_path: {result_path}"
        )

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
                +
                str(error)

            ) from error

        if result_size <= 0:

            raise RuntimeError(

                "字幕MP4のサイズが0 bytesです。"
                f"\n出力: {result_path}"

            )

        elapsed = (

            time.monotonic()
            -
            start_time

        )

        st.session_state.subtitle_test_output = (
            str(
                result_path
            )
        )

        st.session_state.subtitle_test_step3_done = True

        log(
            f"STEP 3成功: {result_path}"
        )

        log(
            f"出力サイズ: {result_size} bytes"
        )

        log(
            f"処理時間: {elapsed:.1f} sec"
        )

        log_separator()

        st.success(
            "③ 字幕MP4の作成に成功しました。"
        )

        st.write(
            f"**出力ファイル:** `{result_path.name}`"
        )

        st.write(
            f"**保存先:** `{result_path}`"
        )

        st.write(
            f"**サイズ:** `{result_size:,} bytes`"
        )

        st.write(
            f"**処理時間:** `{elapsed:.1f} 秒`"
        )

        st.session_state.subtitle_test_output = (
            str(
                result_path
            )
        )

    except Exception as error:

        elapsed = (

            time.monotonic()
            -
            start_time

        )

        log_exception(
            "STEP 3失敗",
            error
        )

        log(
            f"STEP 3処理時間: {elapsed:.1f} sec"
        )

        st.session_state.subtitle_test_step3_done = False

        st.error(
            "③ 字幕MP4作成に失敗しました。"
        )

        st.exception(
            error
        )


# ==========================================================
# STEP 3完了表示
# ==========================================================

if st.session_state.subtitle_test_step3_done:

    st.success(
        "✓ STEP 3 完了"
    )

    if st.session_state.subtitle_test_output:

        display_file_info(
            st.session_state.subtitle_test_output
        )


# ==========================================================
# 区切り
# ==========================================================

st.divider()


# ==========================================================
# downloads内ファイル一覧
# ==========================================================

st.header(
    "📁 downloads内のファイル"
)

st.caption(
    "config.py の DOWNLOAD_DIR を参照しています。"
)


if st.button(

    "downloadsを再確認",

    key="subtitle_test_refresh_files"

):

    st.rerun()


download_files = (
    list_download_files()
)


if not download_files:

    st.info(
        "downloadsフォルダにファイルがありません。"
    )

else:

    for file_path in download_files:

        try:

            size = (
                file_path.stat().st_size
            )

        except OSError:

            size = 0

        st.write(

            f"- `{file_path.name}` "
            f"({size:,} bytes)"

        )


# ==========================================================
# テスト状態
# ==========================================================

st.divider()

st.header(
    "🧪 テスト状態"
)


status_col1, status_col2, status_col3 = (
    st.columns(3)
)


with status_col1:

    if st.session_state.subtitle_test_step1_done:

        st.success(
            "① MP4\n\n完了"
        )

    else:

        st.warning(
            "① MP4\n\n未実行"
        )


with status_col2:

    if st.session_state.subtitle_test_step2_done:

        st.success(
            "② SRT\n\n完了"
        )

    else:

        st.warning(
            "② SRT\n\n未実行"
        )


with status_col3:

    if st.session_state.subtitle_test_step3_done:

        st.success(
            "③ 字幕MP4\n\n完了"
        )

    else:

        st.warning(
            "③ 字幕MP4\n\n未実行"
        )


# ==========================================================
# 現在のパス情報
# ==========================================================

st.divider()

with st.expander(
    "🔍 現在のテスト情報"
):

    st.write(
        f"**DOWNLOAD_DIR:** `{DOWNLOAD_DIR}`"
    )

    st.write(
        f"**DOWNLOADS_DIR:** `{DOWNLOADS_DIR}`"
    )

    st.write(
        f"**MP4:** "
        f"`{st.session_state.subtitle_test_mp4}`"
    )

    st.write(
        f"**SRT:** "
        f"`{st.session_state.subtitle_test_srt}`"
    )

    st.write(
        f"**出力:** "
        f"`{st.session_state.subtitle_test_output}`"
    )


# ==========================================================
# リセット
# ==========================================================

st.divider()

if st.button(

    "🔄 テスト状態をリセット",

    key="subtitle_test_reset"

):

    log(
        "テスト状態リセット"
    )

    st.session_state.subtitle_test_mp4 = None

    st.session_state.subtitle_test_srt = None

    st.session_state.subtitle_test_output = None

    st.session_state.subtitle_test_step1_done = False

    st.session_state.subtitle_test_step2_done = False

    st.session_state.subtitle_test_step3_done = False

    st.rerun()


# ==========================================================
# 終了ログ
# ==========================================================

log(
    "subtitle_test.py RENDER COMPLETE"
)

log_separator()
