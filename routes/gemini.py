# ==========================================================
# gemini.py
#
# Gemini 音声文字起こし
#
# MP3
#   ↓
# Gemini Files API
#   ↓
# Gemini generate_content
#   ↓
# SRT
#
# ==========================================================

import os
import re
import uuid
import shutil
import tempfile
import time
import traceback


from dotenv import load_dotenv


from flask import (
    request,
    jsonify
)


from google import genai


from config import DOWNLOAD_DIR


# ==========================================================
# 環境変数
# ==========================================================

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY が設定されていません"
    )


# ==========================================================
# Gemini Client
# ==========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==========================================================
# Geminiモデル
# ==========================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)


# ==========================================================
# リトライ設定
# ==========================================================

GEMINI_MAX_RETRIES = int(
    os.getenv(
        "GEMINI_MAX_RETRIES",
        "3"
    )
)


GEMINI_RETRY_WAIT_SECONDS = int(
    os.getenv(
        "GEMINI_RETRY_WAIT_SECONDS",
        "3"
    )
)


# ==========================================================
# Files API 状態確認
# ==========================================================

GEMINI_FILE_WAIT_SECONDS = int(
    os.getenv(
        "GEMINI_FILE_WAIT_SECONDS",
        "2"
    )
)


GEMINI_FILE_MAX_WAIT = int(
    os.getenv(
        "GEMINI_FILE_MAX_WAIT",
        "60"
    )
)


# ==========================================================
# SRT最小文字数
# ==========================================================

MIN_SRT_TEXT_LENGTH = int(
    os.getenv(
        "MIN_SRT_TEXT_LENGTH",
        "5"
    )
)


# ==========================================================
# ログヘルパー
# ==========================================================

def gemini_log(message):

    print(
        f"[GEMINI] {message}",
        flush=True
    )


def gemini_separator():

    print(
        "==========================================",
        flush=True
    )


# ==========================================================
# エラー全文取得
# ==========================================================

def format_exception(error):

    try:

        return (
            f"TYPE={type(error).__name__}\n"
            f"STR={str(error)}\n"
            f"REPR={repr(error)}"
        )

    except Exception:

        return repr(error)


# ==========================================================
# リトライ対象エラー判定
# ==========================================================

def is_retryable_gemini_error(
    error
):

    error_text = str(
        error
    ).lower()


    retryable_codes = [

        "408",
        "409",
        "429",

        "500",
        "502",
        "503",
        "504",

        "too many requests",
        "rate limit",

        "temporarily unavailable",
        "service unavailable",

        "bad gateway",
        "gateway timeout",

        "internal server error",

        "timeout",
        "timed out",

        "deadline exceeded",
        "resource exhausted",

        "connection reset",
        "connection aborted",
        "connection error",

    ]


    for code in retryable_codes:

        if code in error_text:

            return True


    return False


# ==========================================================
# Geminiレスポンス情報ログ
# ==========================================================

def log_response_debug(
    response
):

    gemini_separator()

    gemini_log("RESPONSE DEBUG")

    try:

        gemini_log(
            "response type: "
            +
            type(response).__name__
        )

    except Exception:
        pass


    # ======================================================
    # response.text
    # ======================================================

    try:

        response_text = getattr(
            response,
            "text",
            None
        )


        gemini_log(
            "response.text type: "
            +
            type(response_text).__name__
        )


        if response_text is None:

            gemini_log(
                "response.text: None"
            )

        else:

            response_text_string = str(
                response_text
            )


            gemini_log(
                "response.text length: "
                +
                str(
                    len(
                        response_text_string
                    )
                )
            )


            gemini_log(
                "response.text preview: "
                +
                response_text_string[:500]
            )


    except Exception as error:

        gemini_log(
            "response.text取得エラー: "
            +
            repr(error)
        )


    # ======================================================
    # candidates
    # ======================================================

    try:

        candidates = getattr(
            response,
            "candidates",
            None
        )


        if candidates is None:

            gemini_log(
                "candidates: None"
            )

        else:

            gemini_log(
                "candidates count: "
                +
                str(
                    len(candidates)
                )
            )


            for index, candidate in enumerate(
                candidates
            ):

                finish_reason = getattr(
                    candidate,
                    "finish_reason",
                    None
                )


                gemini_log(
                    f"candidate[{index}] "
                    f"finish_reason: "
                    f"{finish_reason}"
                )


                safety_ratings = getattr(
                    candidate,
                    "safety_ratings",
                    None
                )


                gemini_log(
                    f"candidate[{index}] "
                    f"safety_ratings: "
                    f"{safety_ratings}"
                )


                content = getattr(
                    candidate,
                    "content",
                    None
                )


                if content is None:

                    gemini_log(
                        f"candidate[{index}] "
                        "content: None"
                    )

                    continue


                parts = getattr(
                    content,
                    "parts",
                    None
                )


                if not parts:

                    gemini_log(
                        f"candidate[{index}] "
                        "parts: None"
                    )

                    continue


                gemini_log(
                    f"candidate[{index}] "
                    f"parts count: {len(parts)}"
                )


                for part_index, part in enumerate(
                    parts
                ):

                    part_text = getattr(
                        part,
                        "text",
                        None
                    )


                    gemini_log(
                        f"candidate[{index}] "
                        f"part[{part_index}] "
                        f"text length: "
                        f"{len(str(part_text or ''))}"
                    )


    except Exception as error:

        gemini_log(
            "candidates解析ログエラー: "
            +
            repr(error)
        )


    # ======================================================
    # prompt feedback
    # ======================================================

    try:

        prompt_feedback = getattr(
            response,
            "prompt_feedback",
            None
        )


        gemini_log(
            "prompt_feedback: "
            +
            str(
                prompt_feedback
            )
        )


    except Exception as error:

        gemini_log(
            "prompt_feedback取得エラー: "
            +
            repr(error)
        )


    gemini_separator()


# ==========================================================
# Geminiレスポンスからテキスト抽出
# ==========================================================

def extract_response_text(
    response
):

    if response is None:

        return ""


    # ======================================================
    # response.text
    # ======================================================

    try:

        response_text = getattr(
            response,
            "text",
            None
        )


        if response_text:

            response_text = str(
                response_text
            ).strip()


            if response_text:

                return response_text


    except Exception as error:

        gemini_log(
            "response.text取得失敗: "
            +
            repr(error)
        )


    # ======================================================
    # candidates
    # ======================================================

    try:

        candidates = getattr(
            response,
            "candidates",
            None
        )


        if candidates:

            collected_parts = []


            for candidate in candidates:

                content = getattr(
                    candidate,
                    "content",
                    None
                )


                if content is None:

                    continue


                parts = getattr(
                    content,
                    "parts",
                    None
                )


                if not parts:

                    continue


                for part in parts:

                    part_text = getattr(
                        part,
                        "text",
                        None
                    )


                    if part_text:

                        collected_parts.append(
                            str(
                                part_text
                            )
                        )


            if collected_parts:

                combined_text = "\n".join(
                    collected_parts
                ).strip()


                if combined_text:

                    return combined_text


    except Exception as error:

        gemini_log(
            "candidatesからのテキスト取得失敗: "
            +
            repr(error)
        )


    return ""


# ==========================================================
# SRT整形
# ==========================================================

def clean_srt_text(
    text
):

    if text is None:

        return ""


    text = str(
        text
    ).strip()


    if not text:

        return ""


    # ======================================================
    # Markdownコードブロック除去
    # ======================================================

    text = re.sub(
        r"^\s*```(?:srt|text)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )


    text = re.sub(
        r"\s*```\s*$",
        "",
        text,
        flags=re.IGNORECASE
    )


    text = text.strip()


    # ======================================================
    # BOM除去
    # ======================================================

    text = text.lstrip(
        "\ufeff"
    )


    # ======================================================
    # 改行統一
    # ======================================================

    text = text.replace(
        "\r\n",
        "\n"
    )


    text = text.replace(
        "\r",
        "\n"
    )


    # ======================================================
    # 先頭説明文除去
    # ======================================================

    match = re.search(
        r"(?m)^\s*1\s*$",
        text
    )


    if match:

        text = text[
            match.start():
        ]


    return text.strip()


# ==========================================================
# SRT形式簡易チェック
# ==========================================================

def validate_srt_text(
    srt_text
):

    if not srt_text:

        raise ValueError(
            "Gemini結果が空です"
        )


    text = str(
        srt_text
    ).strip()


    if len(text) < MIN_SRT_TEXT_LENGTH:

        raise ValueError(
            "Gemini結果が短すぎます: "
            +
            str(
                len(text)
            )
            +
            "文字"
        )


    # ======================================================
    # 時間情報
    # ======================================================

    timestamp_pattern = re.compile(

        r"\d{2}:\d{2}:\d{2},\d{3}"
        r"\s*-->\s*"
        r"\d{2}:\d{2}:\d{2},\d{3}"

    )


    if not timestamp_pattern.search(
        text
    ):

        raise ValueError(
            "Gemini結果にSRTの時間情報がありません"
        )


    # ======================================================
    # 字幕番号
    # ======================================================

    if not re.search(
        r"(?m)^\s*\d+\s*$",
        text
    ):

        raise ValueError(
            "Gemini結果にSRT字幕番号がありません"
        )


    return True


# ==========================================================
# Files API state
# ==========================================================

def get_uploaded_file_state(
    uploaded_file
):

    if uploaded_file is None:

        return None


    try:

        return getattr(
            uploaded_file,
            "state",
            None
        )

    except Exception:

        return None


# ==========================================================
# Files API状態待機
# ==========================================================

def wait_for_uploaded_file_ready(
    uploaded_file
):

    if uploaded_file is None:

        raise ValueError(
            "Gemini uploaded_file がありません"
        )


    gemini_separator()

    gemini_log(
        "STEP: Gemini Files API ファイル状態確認"
    )


    current_state = get_uploaded_file_state(
        uploaded_file
    )


    # ======================================================
    # stateが取れない場合
    # ======================================================

    if current_state is None:

        gemini_log(
            "uploaded_file.state を取得できません"
        )

        gemini_log(
            "そのまま generate_content を実行します"
        )

        return uploaded_file


    start_time = time.time()


    while True:

        state_name = str(

            getattr(
                current_state,
                "name",
                current_state
            )

        ).upper()


        gemini_log(
            "Gemini file state: "
            +
            state_name
        )


        # ==================================================
        # ACTIVE
        # ==================================================

        if "ACTIVE" in state_name:

            gemini_log(
                "Gemini file ACTIVE"
            )

            return uploaded_file


        # ==================================================
        # FAILED
        # ==================================================

        if (
            "FAILED" in state_name
            or
            "ERROR" in state_name
        ):

            raise RuntimeError(

                "Gemini Files APIのファイル処理に失敗しました: "
                +
                state_name

            )


        # ==================================================
        # タイムアウト
        # ==================================================

        elapsed = (
            time.time()
            -
            start_time
        )


        if elapsed >= GEMINI_FILE_MAX_WAIT:

            raise TimeoutError(

                "Gemini Files APIのファイル処理待機が"
                "タイムアウトしました。"
                f" state={state_name}"

            )


        gemini_log(
            "Gemini file 処理中。"
            +
            str(
                GEMINI_FILE_WAIT_SECONDS
            )
            +
            "秒待機します"
        )


        time.sleep(
            GEMINI_FILE_WAIT_SECONDS
        )


        # ==================================================
        # 最新状態取得
        # ==================================================

        file_name = getattr(
            uploaded_file,
            "name",
            None
        )


        if not file_name:

            gemini_log(
                "uploaded_file.name が取得できません"
            )

            continue


        try:

            uploaded_file = client.files.get(
                name=file_name
            )


            current_state = get_uploaded_file_state(
                uploaded_file
            )


            if current_state is None:

                gemini_log(
                    "最新stateが取得できません"
                )

                return uploaded_file


        except Exception as error:

            gemini_log(
                "Gemini file state取得エラー"
            )

            gemini_log(
                format_exception(error)
            )


            if is_retryable_gemini_error(
                error
            ):

                continue


            raise


# ==========================================================
# GeminiへMP3送信
# ==========================================================

def transcribe_mp3(
    mp3_path
):

    mp3_path = os.path.abspath(
        str(
            mp3_path
        )
    )


    # ======================================================
    # MP3確認
    # ======================================================

    if not os.path.exists(
        mp3_path
    ):

        raise FileNotFoundError(
            f"MP3がありません: {mp3_path}"
        )


    if not os.path.isfile(
        mp3_path
    ):

        raise ValueError(
            "指定されたパスはファイルではありません"
        )


    if not mp3_path.lower().endswith(
        ".mp3"
    ):

        raise ValueError(
            "MP3ファイルを指定してください"
        )


    mp3_size = os.path.getsize(
        mp3_path
    )


    if mp3_size <= 0:

        raise ValueError(
            "MP3ファイルが0 bytesです"
        )


    # ======================================================
    # 開始ログ
    # ======================================================

    gemini_separator()

    gemini_log("解析開始")

    gemini_log(
        "MP3: "
        +
        mp3_path
    )

    gemini_log(
        "MP3サイズ: "
        +
        str(mp3_size)
        +
        " bytes"
    )

    gemini_log(
        "モデル: "
        +
        GEMINI_MODEL
    )

    gemini_log(
        "時間カット: なし"
    )

    gemini_log(
        "MP3全体をGeminiへ送信"
    )

    gemini_separator()


    # ======================================================
    # 一時MP3
    # ======================================================

    temp_mp3 = os.path.join(

        tempfile.gettempdir(),

        "gemini_audio_"
        +
        uuid.uuid4().hex
        +
        ".mp3"

    )


    uploaded_file = None


    try:

        # ==================================================
        # STEP 1
        # ==================================================

        gemini_separator()

        gemini_log(
            "STEP 1 / 4"
        )

        gemini_log(
            "Gemini Files API upload開始"
        )

        gemini_separator()


        shutil.copy2(
            mp3_path,
            temp_mp3
        )


        temp_size = os.path.getsize(
            temp_mp3
        )


        if temp_size <= 0:

            raise RuntimeError(
                "Gemini送信用MP3が0 bytesです"
            )


        gemini_log(
            "upload用一時MP3: "
            +
            temp_mp3
        )

        gemini_log(
            "upload用MP3サイズ: "
            +
            str(temp_size)
            +
            " bytes"
        )


        # ==================================================
        # Files API upload
        # ==================================================

        upload_exception = None


        for upload_attempt in range(

            1,

            GEMINI_MAX_RETRIES + 1

        ):

            try:

                gemini_log(
                    "upload試行: "
                    +
                    f"{upload_attempt}/"
                    +
                    f"{GEMINI_MAX_RETRIES}"
                )


                upload_start = time.time()


                uploaded_file = client.files.upload(
                    file=temp_mp3
                )


                upload_elapsed = (
                    time.time()
                    -
                    upload_start
                )


                gemini_log(
                    "Gemini Files API upload成功"
                )


                gemini_log(
                    f"upload時間: "
                    f"{upload_elapsed:.2f}秒"
                )


                gemini_log(
                    "uploaded_file: "
                    +
                    str(
                        uploaded_file
                    )
                )


                upload_exception = None


                break


            except Exception as error:

                upload_exception = error


                gemini_log(
                    "Gemini Files API upload失敗"
                )


                gemini_log(
                    format_exception(error)
                )


                retryable = is_retryable_gemini_error(
                    error
                )


                gemini_log(
                    "リトライ対象: "
                    +
                    str(retryable)
                )


                if (
                    upload_attempt
                    >=
                    GEMINI_MAX_RETRIES
                ):

                    raise


                if not retryable:

                    raise


                wait_seconds = (
                    upload_attempt
                    *
                    GEMINI_RETRY_WAIT_SECONDS
                )


                gemini_log(
                    f"{wait_seconds}秒待って"
                    "uploadを再試行します"
                )


                time.sleep(
                    wait_seconds
                )


        if upload_exception is not None:

            raise upload_exception


        if uploaded_file is None:

            raise RuntimeError(
                "Gemini Files APIから"
                "uploaded_fileが返されませんでした"
            )


        # ==================================================
        # STEP 2
        # ==================================================

        gemini_separator()

        gemini_log(
            "STEP 2 / 4"
        )

        gemini_log(
            "Gemini Files API ファイル状態確認"
        )

        gemini_separator()


        uploaded_file = wait_for_uploaded_file_ready(
            uploaded_file
        )


        # ==================================================
        # プロンプト
        # ==================================================

        prompt = """
この音声ファイル全体を日本語で正確に文字起こししてください。

重要:

・渡されたMP3に含まれている音声を最初から最後まで対象にする
・音声の一部だけを選択しない
・音声をカットしない
・開始時間を判断してカットしない
・終了時間を判断してカットしない
・音声の開始位置や終了位置を変更しない
・音声全体を文字起こしする
・文章を省略しない
・要約しない
・可能な限り正確に聞き取る
・日本語で文字起こしする
・字幕として読みやすい単位に分割する
・各字幕に時間情報を付ける
・SRT形式で出力する
・説明文を書かない
・前置きを書かない
・後書きを書かない
・Markdownのコードブロックを使用しない
・SRT以外の文章を出力しない

このMP3は、必要な時間範囲がすでに切り出されています。

そのため、元動画の時間範囲を推測したり、
音声の一部を選択したりせず、
渡されたMP3そのものを最初から最後まで
文字起こししてください。

SRT形式:

1
00:00:00,000 --> 00:00:05,000
字幕文章

2
00:00:05,000 --> 00:00:10,000
字幕文章

必ずSRT形式だけを返してください。
"""


        # ==================================================
        # STEP 3
        # ==================================================

        gemini_separator()

        gemini_log(
            "STEP 3 / 4"
        )

        gemini_log(
            "Gemini 音声解析開始"
        )

        gemini_log(
            "ここから Gemini generate_content を"
            "実行しています"
        )

        gemini_log(
            "※ この処理は音声時間によって"
            "しばらく時間がかかる場合があります"
        )

        gemini_separator()


        response = None


        # ==================================================
        # generate_content
        # ==================================================

        for attempt in range(

            1,

            GEMINI_MAX_RETRIES + 1

        ):

            try:

                gemini_log(
                    "------------------------------------------"
                )

                gemini_log(
                    "generate_content 試行 "
                    +
                    f"{attempt}/"
                    +
                    f"{GEMINI_MAX_RETRIES}"
                )

                gemini_log(
                    "Geminiへ音声解析リクエスト送信"
                )

                gemini_log(
                    "モデル: "
                    +
                    GEMINI_MODEL
                )

                gemini_log(
                    "------------------------------------------"
                )


                generate_start = time.time()


                response = client.models.generate_content(

                    model=GEMINI_MODEL,

                    contents=[

                        uploaded_file,

                        prompt

                    ]

                )


                generate_elapsed = (
                    time.time()
                    -
                    generate_start
                )


                gemini_log(
                    "Gemini generate_content API成功"
                )


                gemini_log(
                    f"Gemini応答時間: "
                    f"{generate_elapsed:.2f}秒"
                )


                # ==================================================
                # response debug
                # ==================================================

                log_response_debug(
                    response
                )


                # ==================================================
                # テキスト抽出
                # ==================================================

                raw_text = extract_response_text(
                    response
                )


                gemini_log(
                    "抽出テキスト長: "
                    +
                    str(
                        len(raw_text)
                    )
                )


                # ==================================================
                # 空レスポンス
                # ==================================================

                if not raw_text:

                    gemini_log(
                        "Geminiレスポンスに"
                        "テキストがありません"
                    )


                    if (
                        attempt
                        >=
                        GEMINI_MAX_RETRIES
                    ):

                        raise RuntimeError(

                            "Gemini APIはレスポンスを返しましたが、"
                            "テキスト結果が空でした。"
                            "レスポンス詳細はログを確認してください。"

                        )


                    wait_seconds = (
                        attempt
                        *
                        GEMINI_RETRY_WAIT_SECONDS
                    )


                    gemini_log(
                        f"{wait_seconds}秒待って再試行します"
                    )


                    time.sleep(
                        wait_seconds
                    )


                    continue


                # ==================================================
                # SRT整形
                # ==================================================

                gemini_log(
                    "Gemini結果をSRT形式に整形しています"
                )


                srt_text = clean_srt_text(
                    raw_text
                )


                gemini_log(
                    "整形後SRT長: "
                    +
                    str(
                        len(srt_text)
                    )
                )


                # ==================================================
                # SRT検証
                # ==================================================

                try:

                    validate_srt_text(
                        srt_text
                    )


                except Exception as validation_error:

                    gemini_log(
                        "SRT形式チェック失敗"
                    )


                    gemini_log(
                        format_exception(
                            validation_error
                        )
                    )


                    gemini_log(
                        "Gemini raw result:"
                    )


                    print(
                        raw_text[:3000],
                        flush=True
                    )


                    if (
                        attempt
                        >=
                        GEMINI_MAX_RETRIES
                    ):

                        raise RuntimeError(

                            "Geminiから有効なSRTを"
                            "取得できませんでした: "
                            +
                            str(
                                validation_error
                            )

                        ) from validation_error


                    wait_seconds = (
                        attempt
                        *
                        GEMINI_RETRY_WAIT_SECONDS
                    )


                    gemini_log(
                        f"{wait_seconds}秒待って"
                        "再生成します"
                    )


                    time.sleep(
                        wait_seconds
                    )


                    continue


                # ==================================================
                # 成功
                # ==================================================

                gemini_separator()

                gemini_log(
                    "Gemini 音声解析完了"
                )

                gemini_log(
                    "SRT文字数: "
                    +
                    str(
                        len(srt_text)
                    )
                )

                gemini_separator()


                return srt_text


            except Exception as error:

                gemini_separator()

                gemini_log(
                    "Gemini generate_content失敗"
                )

                gemini_log(
                    "TYPE: "
                    +
                    type(error).__name__
                )

                gemini_log(
                    "ERROR: "
                    +
                    str(error)
                )

                gemini_log(
                    "REPR: "
                    +
                    repr(error)
                )


                # ==================================================
                # traceback
                # ==================================================

                traceback.print_exc()


                retryable = is_retryable_gemini_error(
                    error
                )


                gemini_log(
                    "リトライ対象: "
                    +
                    str(retryable)
                )


                if (
                    attempt
                    >=
                    GEMINI_MAX_RETRIES
                ):

                    gemini_log(
                        "最大リトライ回数に到達"
                    )

                    raise


                if not retryable:

                    gemini_log(
                        "一時的エラーではないため"
                        "リトライしません"
                    )

                    raise


                wait_seconds = (
                    attempt
                    *
                    GEMINI_RETRY_WAIT_SECONDS
                )


                gemini_log(
                    f"{wait_seconds}秒待って"
                    "再試行します"
                )


                time.sleep(
                    wait_seconds
                )


        # ======================================================
        # 到達しない想定
        # ======================================================

        raise RuntimeError(
            "Gemini文字起こし処理が完了しませんでした"
        )


    finally:

        # ======================================================
        # Gemini Files API削除
        # ======================================================

        if uploaded_file is not None:

            try:

                uploaded_name = getattr(
                    uploaded_file,
                    "name",
                    None
                )


                if uploaded_name:

                    gemini_log(
                        "uploaded file削除: "
                        +
                        uploaded_name
                    )


                    client.files.delete(
                        name=uploaded_name
                    )


                    gemini_log(
                        "uploaded file削除完了"
                    )


            except Exception as error:

                gemini_log(
                    "WARNING: uploaded file削除失敗: "
                    +
                    repr(error)
                )


        # ======================================================
        # 一時MP3削除
        # ======================================================

        if os.path.exists(
            temp_mp3
        ):

            try:

                os.remove(
                    temp_mp3
                )


                gemini_log(
                    "一時MP3削除: "
                    +
                    temp_mp3
                )


            except Exception as error:

                gemini_log(
                    "WARNING: 一時MP3削除失敗: "
                    +
                    repr(error)
                )


# ==========================================================
# SRT保存
# ==========================================================

def save_srt(
    mp3_path,
    srt_text
):

    mp3_path = os.path.abspath(
        str(
            mp3_path
        )
    )


    if not srt_text:

        raise ValueError(
            "保存するSRT本文が空です"
        )


    srt_text = clean_srt_text(
        srt_text
    )


    if not srt_text:

        raise ValueError(
            "整形後のSRT本文が空です"
        )


    srt_path = (

        os.path.splitext(
            mp3_path
        )[0]

        +
        ".srt"

    )


    gemini_separator()

    gemini_log(
        "SRT保存開始"
    )

    gemini_log(
        "SRT: "
        +
        srt_path
    )


    with open(

        srt_path,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(
            srt_text
        )


    # ======================================================
    # 保存確認
    # ======================================================

    if not os.path.exists(
        srt_path
    ):

        raise IOError(
            "SRTファイルの保存に失敗しました: "
            +
            srt_path
        )


    if not os.path.isfile(
        srt_path
    ):

        raise IOError(
            "SRT保存先がファイルではありません: "
            +
            srt_path
        )


    srt_size = os.path.getsize(
        srt_path
    )


    if srt_size <= 0:

        raise ValueError(
            "SRTファイルが0 bytesです: "
            +
            srt_path
        )


    gemini_separator()

    gemini_log(
        "SRT保存完了"
    )

    gemini_log(
        "SRT: "
        +
        srt_path
    )

    gemini_log(
        "SRTサイズ: "
        +
        str(
            srt_size
        )
        +
        " bytes"
    )

    gemini_separator()


    return srt_path


# ==========================================================
# Flask Route
#
# POST /gemini-transcribe
# ==========================================================

def register_gemini(
    app
):

    @app.route(
        "/gemini-transcribe",
        methods=["POST"]
    )

    def gemini_transcribe():

        try:

            # ==================================================
            # JSON
            # ==================================================

            data = request.get_json(
                silent=True
            )


            if not data:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "JSONデータがありません"

                }), 400


            # ==================================================
            # MP3ファイル名
            # ==================================================

            filename = data.get(
                "file"
            )


            if not filename:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3ファイル名がありません"

                }), 400


            filename = str(
                filename
            ).strip()


            if not filename:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3ファイル名がありません"

                }), 400


            filename = os.path.basename(
                filename
            )


            # ==================================================
            # MP3確認
            # ==================================================

            if not filename.lower().endswith(
                ".mp3"
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3ファイルを指定してください"

                }), 400


            # ==================================================
            # downloads
            # ==================================================

            download_root = os.path.abspath(
                str(
                    DOWNLOAD_DIR
                )
            )


            mp3_path = os.path.abspath(

                os.path.join(
                    download_root,
                    filename
                )

            )


            # ==================================================
            # パストラバーサル対策
            # ==================================================

            try:

                common_path = os.path.commonpath(

                    [
                        download_root,
                        mp3_path
                    ]

                )

            except ValueError:

                common_path = None


            if common_path != download_root:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "不正なファイルパスです"

                }), 400


            # ==================================================
            # MP3存在確認
            # ==================================================

            if not os.path.exists(
                mp3_path
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        f"MP3がありません: {filename}"

                }), 404


            if not os.path.isfile(
                mp3_path
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "指定されたパスはファイルではありません"

                }), 400


            mp3_size = os.path.getsize(
                mp3_path
            )


            if mp3_size <= 0:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "MP3ファイルが0 bytesです"

                }), 400


            # ==================================================
            # Route開始
            # ==================================================

            gemini_separator()

            gemini_log(
                "GEMINI ROUTE 文字起こし開始"
            )

            gemini_log(
                "MP3: "
                +
                mp3_path
            )

            gemini_log(
                "MP3サイズ: "
                +
                str(mp3_size)
                +
                " bytes"
            )

            gemini_log(
                "モデル: "
                +
                GEMINI_MODEL
            )

            gemini_separator()


            # ==================================================
            # Gemini
            # ==================================================

            srt_text = transcribe_mp3(
                mp3_path
            )


            # ==================================================
            # SRT保存
            # ==================================================

            srt_path = save_srt(
                mp3_path,
                srt_text
            )


            # ==================================================
            # 完了
            # ==================================================

            gemini_separator()

            gemini_log(
                "GEMINI ROUTE 完了"
            )

            gemini_log(
                "MP3: "
                +
                mp3_path
            )

            gemini_log(
                "SRT: "
                +
                srt_path
            )

            gemini_separator()


            return jsonify({

                "success":
                    True,

                "srt_file":
                    os.path.basename(
                        srt_path
                    ),

                "mp3_file":
                    os.path.basename(
                        mp3_path
                    ),

                "text":
                    "Gemini文字起こし完了"

            })


        except FileNotFoundError as error:

            gemini_separator()

            gemini_log(
                "GEMINI ROUTE FILE NOT FOUND"
            )

            gemini_log(
                str(error)
            )

            gemini_separator()


            return jsonify({

                "success":
                    False,

                "message":
                    str(error)

            }), 404


        except Exception as error:

            gemini_separator()

            gemini_log(
                "GEMINI ROUTE ERROR"
            )

            gemini_log(
                "TYPE: "
                +
                type(error).__name__
            )

            gemini_log(
                "ERROR: "
                +
                str(error)
            )

            gemini_log(
                "REPR: "
                +
                repr(error)
            )


            traceback.print_exc()


            gemini_separator()


            return jsonify({

                "success":
                    False,

                "message":
                    str(error)

            }), 500
