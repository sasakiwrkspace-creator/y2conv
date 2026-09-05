# ==========================================================
# gemini.py
#
# Gemini 音声文字起こし
#
# 役割:
#
#   MP3
#     ↓
#   Gemini Files API
#     ↓
#   Gemini
#     ↓
#   SRT形式文字起こし
#
# ==========================================================
#
# 使用箇所:
#
# routes/subtitle_routes.py
#
#     from routes.gemini import (
#         transcribe_mp3,
#         save_srt
#     )
#
# ==========================================================
#
# 重要:
#
# Gemini側では時間範囲をカットしない。
#
# MP4 / MP3の時間指定は、
# subtitle_mp4.py / media_extract.py側で
# すでに処理済みのものを使用する。
#
# Geminiには完成したMP3全体を渡す。
#
# ==========================================================


import os
import re
import uuid
import shutil
import tempfile
import time


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
#
# Renderなどの環境変数で変更可能。
#
# GEMINI_MODEL が設定されていれば、
# それを優先する。
#
# 未設定の場合:
#
#   gemini-3.5-flash
#
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
# Geminiレスポンス待機
#
# Files APIでアップロードしたファイルが
# 処理中の場合に備える。
#
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
#
# 完全に空の場合だけでなく、
# Geminiが説明文だけ返した場合も検知しやすくする。
#
# ==========================================================

MIN_SRT_TEXT_LENGTH = int(

    os.getenv(

        "MIN_SRT_TEXT_LENGTH",

        "5"

    )

)


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
        "connection error"

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

    print(
        "=========================================="
    )

    print(
        "[GEMINI] RESPONSE DEBUG"
    )

    print(
        "response type:",
        type(response).__name__
    )


    # ------------------------------------------------------
    # response.text
    # ------------------------------------------------------

    try:

        response_text = getattr(

            response,

            "text",

            None

        )


        print(
            "response.text type:",
            type(response_text).__name__
        )


        if response_text is None:

            print(
                "response.text: None"
            )

        else:

            print(
                "response.text length:",
                len(
                    str(
                        response_text
                    )
                )
            )

            print(
                "response.text preview:",
                str(
                    response_text
                )[:500]
            )


    except Exception as error:

        print(
            "response.text取得エラー:",
            repr(error)
        )


    # ------------------------------------------------------
    # candidates
    # ------------------------------------------------------

    try:

        candidates = getattr(

            response,

            "candidates",

            None

        )


        if candidates is None:

            print(
                "candidates: None"
            )

        else:

            print(
                "candidates count:",
                len(candidates)
            )


            for index, candidate in enumerate(

                candidates

            ):

                print(
                    f"candidate[{index}] type:",
                    type(candidate).__name__
                )


                finish_reason = getattr(

                    candidate,

                    "finish_reason",

                    None

                )


                print(
                    f"candidate[{index}] finish_reason:",
                    finish_reason
                )


                safety_ratings = getattr(

                    candidate,

                    "safety_ratings",

                    None

                )


                print(
                    f"candidate[{index}] safety_ratings:",
                    safety_ratings
                )


                content = getattr(

                    candidate,

                    "content",

                    None

                )


                if content is None:

                    print(
                        f"candidate[{index}] content: None"
                    )

                    continue


                print(
                    f"candidate[{index}] content type:",
                    type(content).__name__
                )


                parts = getattr(

                    content,

                    "parts",

                    None

                )


                if parts is None:

                    print(
                        f"candidate[{index}] parts: None"
                    )

                    continue


                print(
                    f"candidate[{index}] parts count:",
                    len(parts)
                )


                for part_index, part in enumerate(

                    parts

                ):

                    part_text = getattr(

                        part,

                        "text",

                        None

                    )


                    print(
                        f"candidate[{index}] "
                        f"part[{part_index}] "
                        f"text length:",
                        len(
                            str(
                                part_text or ""
                            )
                        )
                    )


    except Exception as error:

        print(
            "candidates解析ログエラー:",
            repr(error)
        )


    # ------------------------------------------------------
    # prompt feedback
    # ------------------------------------------------------

    try:

        prompt_feedback = getattr(

            response,

            "prompt_feedback",

            None

        )


        print(
            "prompt_feedback:",
            prompt_feedback
        )


    except Exception as error:

        print(
            "prompt_feedback取得エラー:",
            repr(error)
        )


    print(
        "=========================================="
    )


# ==========================================================
# Geminiレスポンスからテキスト抽出
#
# response.textだけに依存しない。
#
# ==========================================================

def extract_response_text(
    response
):

    if response is None:

        return ""


    # ======================================================
    # ① response.text
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

        print(
            "[GEMINI] response.text取得失敗:",
            repr(error)
        )


    # ======================================================
    # ② candidates
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

        print(
            "[GEMINI] candidatesからのテキスト取得失敗:",
            repr(error)
        )


    # ======================================================
    # ③ それでも取れない
    # ======================================================

    return ""


# ==========================================================
# Geminiが返したSRTを整形
#
# Markdownコードブロックなどを除去。
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


    # ------------------------------------------------------
    # ```srt
    # ```
    # ------------------------------------------------------

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


    # ------------------------------------------------------
    # BOM
    # ------------------------------------------------------

    text = text.lstrip(
        "\ufeff"
    )


    # ------------------------------------------------------
    # 改行統一
    # ------------------------------------------------------

    text = text.replace(

        "\r\n",

        "\n"

    )


    text = text.replace(

        "\r",

        "\n"

    )


    # ------------------------------------------------------
    # 先頭の説明文を除去
    #
    # Geminiが
    #
    # "以下がSRTです:"
    #
    # のような文を付けた場合、
    # 最初のSRT番号から開始する。
    # ------------------------------------------------------

    match = re.search(

        r"(?m)^\s*1\s*$",

        text

    )


    if match:

        text = text[
            match.start():
        ]


    # ------------------------------------------------------
    # 末尾空白除去
    # ------------------------------------------------------

    text = text.strip()


    return text


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
            str(len(text))
            +
            "文字"

        )


    # ------------------------------------------------------
    # SRTの時間形式
    #
    # 00:00:00,000 --> 00:00:05,000
    # ------------------------------------------------------

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


    # ------------------------------------------------------
    # SRT番号
    # ------------------------------------------------------

    if not re.search(

        r"(?m)^\s*\d+\s*$",

        text

    ):

        raise ValueError(

            "Gemini結果にSRT字幕番号がありません"

        )


    return True


# ==========================================================
# Gemini Files APIの状態取得
# ==========================================================

def get_uploaded_file_state(
    uploaded_file
):

    if uploaded_file is None:

        return None


    # ------------------------------------------------------
    # state
    # ------------------------------------------------------

    try:

        state = getattr(

            uploaded_file,

            "state",

            None

        )


        if state is not None:

            return state


    except Exception:

        pass


    return None


# ==========================================================
# Gemini Files APIアップロード後の状態確認
#
# 音声ファイルが処理中の場合、
# ACTIVEになるまで少し待つ。
#
# ==========================================================

def wait_for_uploaded_file_ready(
    uploaded_file
):

    if uploaded_file is None:

        raise ValueError(
            "Gemini uploaded_file がありません"
        )


    print(
        ">>> Gemini uploaded file 状態確認開始"
    )


    # ======================================================
    # stateが取れない場合
    #
    # SDKのバージョンによってはstateが直接取得できる。
    # 取れない場合はそのまま進む。
    # ======================================================

    current_state = get_uploaded_file_state(

        uploaded_file

    )


    if current_state is None:

        print(
            ">>> uploaded_file.state を取得できません。"
            "そのまま generate_content を実行します。"
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


        print(
            ">>> Gemini file state:",
            state_name
        )


        # --------------------------------------------------
        # ACTIVE
        # --------------------------------------------------

        if "ACTIVE" in state_name:

            print(
                ">>> Gemini file ACTIVE"
            )

            return uploaded_file


        # --------------------------------------------------
        # FAILED
        # --------------------------------------------------

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


        # --------------------------------------------------
        # タイムアウト
        # --------------------------------------------------

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


        print(

            ">>> Gemini file 処理中。"
            f" {GEMINI_FILE_WAIT_SECONDS}秒待機します"

        )


        time.sleep(

            GEMINI_FILE_WAIT_SECONDS

        )


        # --------------------------------------------------
        # files.get
        #
        # nameが取れる場合は最新状態を取得する。
        # --------------------------------------------------

        file_name = getattr(

            uploaded_file,

            "name",

            None

        )


        if not file_name:

            print(
                ">>> uploaded_file.name が取得できないため、"
                "現在の状態のまま再確認します。"
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

                print(
                    ">>> 最新stateが取得できません。"
                )

                return uploaded_file


        except Exception as error:

            print(
                ">>> Gemini file state取得エラー:",
                repr(error)
            )


            # ファイル状態取得だけの一時エラーなら
            # 少し待って再確認する。

            if is_retryable_gemini_error(
                error
            ):

                time.sleep(

                    GEMINI_FILE_WAIT_SECONDS

                )

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
    # MP3存在確認
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


    # ======================================================
    # MP3サイズ確認
    # ======================================================

    mp3_size = os.path.getsize(

        mp3_path

    )


    if mp3_size <= 0:

        raise ValueError(

            "MP3ファイルが0 bytesです"

        )


    # ======================================================
    # ログ
    # ======================================================

    print(
        "=========================================="
    )

    print(
        "[GEMINI] 解析開始"
    )

    print(
        "[GEMINI] MP3:",
        mp3_path
    )

    print(
        "[GEMINI] MP3サイズ:",
        mp3_size,
        "bytes"
    )

    print(
        "[GEMINI] モデル:",
        GEMINI_MODEL
    )

    print(
        "[GEMINI] 時間カット:",
        "なし"
    )

    print(
        "[GEMINI] MP3全体をGeminiへ送信"
    )

    print(
        "=========================================="
    )


    # ======================================================
    # 日本語ファイル名対策
    #
    # Gemini upload用の一時ファイルを作る。
    # 元MP3は変更しない。
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
        # 一時MP3作成
        # ==================================================

        shutil.copy2(

            mp3_path,

            temp_mp3

        )


        print(
            "[GEMINI] upload用一時MP3:",
            temp_mp3
        )


        # ==================================================
        # 一時MP3確認
        # ==================================================

        temp_size = os.path.getsize(

            temp_mp3

        )


        if temp_size <= 0:

            raise RuntimeError(

                "Gemini送信用MP3が0 bytesです"

            )


        print(
            "[GEMINI] upload用MP3サイズ:",
            temp_size,
            "bytes"
        )


        # ==================================================
        # Gemini Files API
        # ==================================================

        print(
            ">>> Gemini Files API upload開始"
        )


        upload_exception = None


        for upload_attempt in range(

            1,

            GEMINI_MAX_RETRIES + 1

        ):

            try:

                print(

                    ">>> upload試行:",
                    f"{upload_attempt}/{GEMINI_MAX_RETRIES}"

                )


                uploaded_file = client.files.upload(

                    file=temp_mp3

                )


                print(
                    ">>> Gemini Files API upload成功"
                )


                print(
                    ">>> uploaded_file:",
                    uploaded_file
                )


                upload_exception = None


                break


            except Exception as error:

                upload_exception = error


                print(
                    ">>> Gemini Files API upload失敗"
                )

                print(
                    ">>> TYPE:",
                    type(error).__name__
                )

                print(
                    ">>> ERROR:",
                    repr(error)
                )


                retryable = is_retryable_gemini_error(

                    error

                )


                print(
                    ">>> リトライ対象:",
                    retryable
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


                print(
                    ">>>",
                    wait_seconds,
                    "秒待ってuploadを再試行します"
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
        # Files API状態確認
        # ==================================================

        uploaded_file = wait_for_uploaded_file_ready(

            uploaded_file

        )


        # ==================================================
        # Geminiプロンプト
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
・各字幕に正確な時間情報を付ける
・SRT形式で出力する
・説明文を書かない
・前置きを書かない
・後書きを書かない
・Markdownのコードブロックを使用しない
・```srt を付けない
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
        # Gemini generate_content
        # ==================================================

        print(
            ">>> Gemini generate_content開始"
        )


        response = None


        for attempt in range(

            1,

            GEMINI_MAX_RETRIES + 1

        ):

            try:

                print(
                    "------------------------------------------"
                )

                print(
                    "[GEMINI] generate_content"
                )

                print(
                    "[GEMINI] 試行:",
                    f"{attempt}/{GEMINI_MAX_RETRIES}"
                )

                print(
                    "------------------------------------------"
                )


                response = client.models.generate_content(

                    model=GEMINI_MODEL,

                    contents=[

                        uploaded_file,

                        prompt

                    ]

                )


                print(
                    ">>> Gemini generate_content API成功"
                )


                # --------------------------------------------------
                # レスポンス詳細
                # --------------------------------------------------

                log_response_debug(

                    response

                )


                # --------------------------------------------------
                # テキスト抽出
                # --------------------------------------------------

                raw_text = extract_response_text(

                    response

                )


                print(
                    ">>> 抽出テキスト長:",
                    len(
                        raw_text
                    )
                )


                # --------------------------------------------------
                # 空レスポンス
                #
                # API自体は成功しているが、
                # テキストが取れなかった場合。
                # --------------------------------------------------

                if not raw_text:

                    print(
                        ">>> Geminiレスポンスに"
                        "テキストがありません"
                    )


                    # ----------------------------------------------
                    # 最終試行なら詳細エラー
                    # ----------------------------------------------

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


                    print(

                        ">>> 空レスポンスのため"
                        "リトライします"

                    )


                    wait_seconds = (

                        attempt
                        *
                        GEMINI_RETRY_WAIT_SECONDS

                    )


                    time.sleep(

                        wait_seconds

                    )


                    continue


                # --------------------------------------------------
                # SRT整形
                # --------------------------------------------------

                srt_text = clean_srt_text(

                    raw_text

                )


                print(
                    ">>> 整形後SRT長:",
                    len(
                        srt_text
                    )
                )


                # --------------------------------------------------
                # SRT形式確認
                # --------------------------------------------------

                try:

                    validate_srt_text(

                        srt_text

                    )


                except Exception as validation_error:

                    print(
                        ">>> SRT形式チェック失敗"
                    )

                    print(
                        ">>> ERROR:",
                        repr(
                            validation_error
                        )
                    )

                    print(
                        ">>> Gemini raw result:"
                    )

                    print(
                        raw_text[:3000]
                    )


                    # SRT形式がおかしい場合も、
                    # 一時的な生成異常を考慮して
                    # 再試行する。

                    if (

                        attempt
                        >=
                        GEMINI_MAX_RETRIES

                    ):

                        raise RuntimeError(

                            "Geminiから有効なSRTを取得できませんでした: "
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


                    print(

                        ">>>",
                        wait_seconds,
                        "秒待って再生成します"

                    )


                    time.sleep(

                        wait_seconds

                    )


                    continue


                # --------------------------------------------------
                # 成功
                # --------------------------------------------------

                print(
                    "=========================================="
                )

                print(
                    "[GEMINI] 解析完了"
                )

                print(
                    "[GEMINI] SRT文字数:",
                    len(
                        srt_text
                    )
                )

                print(
                    "=========================================="
                )


                return srt_text


            except Exception as error:

                print(
                    ">>> Gemini generate_content失敗"
                )

                print(
                    ">>> TYPE:",
                    type(error).__name__
                )

                print(
                    ">>> ERROR:",
                    repr(error)
                )


                # ----------------------------------------------
                # リトライ判定
                # ----------------------------------------------

                retryable = is_retryable_gemini_error(

                    error

                )


                print(
                    ">>> リトライ対象:",
                    retryable
                )


                # ----------------------------------------------
                # 最大回数
                # ----------------------------------------------

                if (

                    attempt
                    >=
                    GEMINI_MAX_RETRIES

                ):

                    print(
                        ">>> 最大リトライ回数に到達"
                    )

                    raise


                # ----------------------------------------------
                # リトライ対象外
                # ----------------------------------------------

                if not retryable:

                    print(
                        ">>> 一時的エラーではないため"
                        "リトライしません"
                    )

                    raise


                wait_seconds = (

                    attempt
                    *
                    GEMINI_RETRY_WAIT_SECONDS

                )


                print(
                    ">>>",
                    wait_seconds,
                    "秒待って再試行します"
                )


                time.sleep(

                    wait_seconds

                )


        # ======================================================
        # ここまで来た場合
        # ======================================================

        raise RuntimeError(

            "Gemini文字起こし処理が完了しませんでした"

        )


    finally:

        # ======================================================
        # Gemini Files APIのファイル削除
        #
        # アップロードしたファイルを削除できる場合は
        # 削除する。
        #
        # SDK / APIの状態によって削除失敗しても、
        # ローカルMP3処理自体は壊さない。
        # ======================================================

        if uploaded_file is not None:

            try:

                uploaded_name = getattr(

                    uploaded_file,

                    "name",

                    None

                )


                if uploaded_name:

                    print(
                        "[GEMINI] uploaded file削除:",
                        uploaded_name
                    )


                    client.files.delete(

                        name=uploaded_name

                    )


                    print(
                        "[GEMINI] uploaded file削除完了"
                    )


            except Exception as error:

                print(

                    "[GEMINI] WARNING: "
                    "uploaded file削除失敗:",
                    repr(error)

                )


        # ======================================================
        # ローカル一時MP3削除
        #
        # 元MP3は削除しない。
        # ======================================================

        if os.path.exists(
            temp_mp3
        ):

            try:

                os.remove(

                    temp_mp3

                )


                print(
                    "[GEMINI] 一時MP3削除:",
                    temp_mp3
                )


            except Exception as error:

                print(

                    "[GEMINI] WARNING: "
                    "一時MP3削除失敗:",
                    repr(error)

                )


# ==========================================================
# SRT保存
#
# MP3と同じ名前にする。
#
# sample.mp3
# ↓
# sample.srt
#
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


    # ======================================================
    # SRT本文確認
    # ======================================================

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


    # ======================================================
    # SRTパス
    # ======================================================

    srt_path = (

        os.path.splitext(

            mp3_path

        )[0]

        +
        ".srt"

    )


    # ======================================================
    # 保存
    # ======================================================

    print(
        "[GEMINI] SRT保存開始:"
    )

    print(
        "[GEMINI] SRT:",
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


    print(
        "=========================================="
    )

    print(
        "[GEMINI] SRT保存完了"
    )

    print(
        "[GEMINI] SRT:",
        srt_path
    )

    print(
        "[GEMINI] SRTサイズ:",
        srt_size,
        "bytes"
    )

    print(
        "=========================================="
    )


    return srt_path


# ==========================================================
# Flask Route
#
# /gemini-transcribe
#
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


            # ==================================================
            # パス区切り文字対策
            #
            # basenameだけを使用。
            # ==================================================

            filename = os.path.basename(

                filename

            )


            # ==================================================
            # MP3以外禁止
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


            # ==================================================
            # MP3サイズ
            # ==================================================

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
            # ログ
            # ==================================================

            print(
                "=========================================="
            )

            print(
                "[GEMINI ROUTE] 文字起こし開始"
            )

            print(
                "[GEMINI ROUTE] MP3:",
                mp3_path
            )

            print(
                "[GEMINI ROUTE] MP3サイズ:",
                mp3_size,
                "bytes"
            )

            print(
                "[GEMINI ROUTE] モデル:",
                GEMINI_MODEL
            )

            print(
                "=========================================="
            )


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

            print(
                "=========================================="
            )

            print(
                "[GEMINI ROUTE] 完了"
            )

            print(
                "[GEMINI ROUTE] MP3:",
                mp3_path
            )

            print(
                "[GEMINI ROUTE] SRT:",
                srt_path
            )

            print(
                "=========================================="
            )


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

            print(
                "=========================================="
            )

            print(
                "[GEMINI ROUTE] FILE NOT FOUND"
            )

            print(
                "ERROR:",
                str(error)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(error)

            }), 404


        except Exception as error:

            print(
                "=========================================="
            )

            print(
                "[GEMINI ROUTE] Gemini ERROR"
            )

            print(
                "TYPE:",
                type(error).__name__
            )

            print(
                "ERROR:",
                str(error)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(error)

            }), 500
