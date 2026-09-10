# ==========================================================
# gemini.py
#
# Gemini 音声文字起こし
#
# MP3
#   ↓
# Gemini Files API
#   ↓
# Gemini
#   ↓
# SRT
#
# 入口・出口は従来のまま
#
# transcribe_mp3(mp3_path)
#     ↓
#     SRT文字列を返す
#
# save_srt(mp3_path, srt_text)
#     ↓
#     mp3と同名の.srtを保存
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
# 環境変数 GEMINI_MODEL があれば優先。
#
# ※ 現在の環境で設定されているモデルを使用。
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
        "5"
    )
)


# ==========================================================
# Files API 待機
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
# SRT最低文字数
# ==========================================================

MIN_SRT_TEXT_LENGTH = int(
    os.getenv(
        "MIN_SRT_TEXT_LENGTH",
        "5"
    )
)


# ==========================================================
# リトライ可能エラー判定
# ==========================================================

def is_retryable_gemini_error(error):

    error_text = str(
        error
    ).lower()


    retryable_words = [

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
        "internal error",

        "timeout",
        "timed out",

        "deadline exceeded",

        "resource exhausted",

        "connection reset",
        "connection aborted",
        "connection error",

        "unavailable",

    ]


    for word in retryable_words:

        if word in error_text:

            return True


    return False


# ==========================================================
# Geminiレスポンスのデバッグ
# ==========================================================

def log_response_debug(response):

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


        print(
            "response.text:",
            repr(response_text)[:1000]
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
                    f"candidate[{index}]:",
                    candidate
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


                content = getattr(
                    candidate,
                    "content",
                    None
                )


                print(
                    f"candidate[{index}] content:",
                    content
                )


                if content is not None:

                    parts = getattr(
                        content,
                        "parts",
                        None
                    )


                    print(
                        f"candidate[{index}] parts:",
                        parts
                    )


    except Exception as error:

        print(
            "candidates解析エラー:",
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
# Geminiレスポンスからテキスト取得
#
# response.textだけに依存しない。
# ==========================================================

def extract_response_text(response):

    if response is None:

        return ""


    # ======================================================
    # ① response.text
    # ======================================================

    try:

        value = getattr(
            response,
            "text",
            None
        )


        if value:

            value = str(
                value
            ).strip()


            if value:

                return value


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

            texts = []


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

                    text = getattr(
                        part,
                        "text",
                        None
                    )


                    if text:

                        texts.append(
                            str(text)
                        )


            if texts:

                result = "\n".join(
                    texts
                ).strip()


                if result:

                    return result


    except Exception as error:

        print(
            "[GEMINI] candidates取得失敗:",
            repr(error)
        )


    return ""


# ==========================================================
# SRT整形
# ==========================================================

def clean_srt_text(text):

    if text is None:

        return ""


    text = str(
        text
    ).strip()


    if not text:

        return ""


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
    # Markdownコードブロック除去
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
    # Geminiが前置きを付けた場合
    #
    # 最初のSRT番号から開始
    # ------------------------------------------------------

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
# SRT簡易チェック
# ==========================================================

def validate_srt_text(srt_text):

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
    # タイムコード
    # ------------------------------------------------------

    timestamp_pattern = re.compile(

        r"\d{2}:\d{2}:\d{2},\d{3}"
        r"\s*-->\s*"
        r"\d{2}:\d{2}:\d{2},\d{3}"

    )


    if not timestamp_pattern.search(text):

        raise ValueError(
            "Gemini結果にSRTの時間情報がありません"
        )


    # ------------------------------------------------------
    # 字幕番号
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
# Files API状態取得
# ==========================================================

def get_uploaded_file_state(uploaded_file):

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
# Files API処理待機
# ==========================================================

def wait_for_uploaded_file_ready(uploaded_file):

    if uploaded_file is None:

        raise ValueError(
            "Gemini uploaded_file がありません"
        )


    current_state = get_uploaded_file_state(
        uploaded_file
    )


    # ------------------------------------------------------
    # stateが取得できない場合
    #
    # そのままGeminiへ渡す。
    # ------------------------------------------------------

    if current_state is None:

        print(
            "[GEMINI] uploaded_file.state "
            "を取得できないため、そのまま使用します"
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
            "[GEMINI] file state:",
            state_name
        )


        # --------------------------------------------------
        # ACTIVE
        # --------------------------------------------------

        if "ACTIVE" in state_name:

            return uploaded_file


        # --------------------------------------------------
        # FAILED / ERROR
        # --------------------------------------------------

        if (
            "FAILED" in state_name
            or
            "ERROR" in state_name
        ):

            raise RuntimeError(
                "Gemini Files APIの処理に失敗しました: "
                +
                state_name
            )


        # --------------------------------------------------
        # タイムアウト
        # --------------------------------------------------

        if (
            time.time() - start_time
            >= GEMINI_FILE_MAX_WAIT
        ):

            raise TimeoutError(
                "Gemini Files APIの処理待機が"
                "タイムアウトしました: "
                +
                state_name
            )


        time.sleep(
            GEMINI_FILE_WAIT_SECONDS
        )


        # --------------------------------------------------
        # 最新状態取得
        # --------------------------------------------------

        file_name = getattr(
            uploaded_file,
            "name",
            None
        )


        if not file_name:

            continue


        try:

            uploaded_file = client.files.get(
                name=file_name
            )


            current_state = get_uploaded_file_state(
                uploaded_file
            )


            if current_state is None:

                return uploaded_file


        except Exception as error:

            print(
                "[GEMINI] file state取得エラー:",
                repr(error)
            )


            if is_retryable_gemini_error(
                error
            ):

                continue


            raise


# ==========================================================
# GeminiへMP3を送信してSRTを取得
# ==========================================================

def transcribe_mp3(mp3_path):

    mp3_path = os.path.abspath(
        str(mp3_path)
    )


    # ======================================================
    # MP3確認
    # ======================================================

    if not os.path.exists(mp3_path):

        raise FileNotFoundError(
            f"MP3がありません: {mp3_path}"
        )


    if not os.path.isfile(mp3_path):

        raise ValueError(
            "指定されたパスはファイルではありません"
        )


    if not mp3_path.lower().endswith(".mp3"):

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


    print(
        "=========================================="
    )

    print(
        "Gemini解析開始"
    )

    print(
        "MP3:",
        mp3_path
    )

    print(
        "MP3サイズ:",
        mp3_size,
        "bytes"
    )

    print(
        "Geminiモデル:",
        GEMINI_MODEL
    )

    print(
        "時間カット:",
        "なし"
    )

    print(
        "MP3全体をそのままGeminiへ送信します"
    )

    print(
        "=========================================="
    )


    # ======================================================
    # 一時ファイル
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
        # MP3コピー
        # ==================================================

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


        print(
            "Gemini upload用一時MP3:",
            temp_mp3
        )

        print(
            "Gemini送信用MP3サイズ:",
            temp_size,
            "bytes"
        )


        # ==================================================
        # Files API upload
        # ==================================================

        upload_error = None


        for upload_attempt in range(
            1,
            GEMINI_MAX_RETRIES + 1
        ):

            try:

                print(
                    ">>> Gemini Files API upload:",
                    f"{upload_attempt}/{GEMINI_MAX_RETRIES}"
                )


                uploaded_file = client.files.upload(
                    file=temp_mp3
                )


                print(
                    ">>> Gemini Files API upload成功"
                )


                upload_error = None

                break


            except Exception as error:

                upload_error = error


                print(
                    ">>> Gemini uploadエラー:",
                    repr(error)
                )


                if (
                    upload_attempt
                    >=
                    GEMINI_MAX_RETRIES
                ):

                    raise


                if not is_retryable_gemini_error(
                    error
                ):

                    raise


                wait_seconds = (
                    upload_attempt
                    *
                    GEMINI_RETRY_WAIT_SECONDS
                )


                print(
                    ">>>",
                    wait_seconds,
                    "秒待って再試行"
                )


                time.sleep(
                    wait_seconds
                )


        if upload_error is not None:

            raise upload_error


        if uploaded_file is None:

            raise RuntimeError(
                "Gemini Files APIから"
                "uploaded_fileが返されませんでした"
            )


        # ==================================================
        # Files API ACTIVE待ち
        # ==================================================

        uploaded_file = wait_for_uploaded_file_ready(
            uploaded_file
        )


        # ==================================================
        # プロンプト
        #
        # 重要:
        # GeminiにSRTの「テキスト」と「時間」を生成させる。
        #
        # ==================================================

        prompt = """
この音声ファイル全体を日本語で文字起こししてください。

必ずMP3の最初から最後まで確認してください。

音声を要約しないでください。
文章を省略しないでください。
説明文を付けないでください。

各字幕には、音声内で実際にその発話が始まった時間と
終了した時間を付けてください。

出力はSRT形式だけにしてください。

Markdownコードブロックは禁止です。

出力例:

1
00:00:00,000 --> 00:00:03,500
これは字幕の文章です。

2
00:00:03,500 --> 00:00:07,200
次の字幕の文章です。

重要:

・MP3全体を文字起こしする
・音声を途中で省略しない
・要約しない
・日本語で出力する
・字幕として読みやすい長さに分割する
・各字幕に時間情報を付ける
・SRT以外の文章を出力しない

必ずSRT本文だけを返してください。
"""


        # ==================================================
        # generate_content
        #
        # ここが今回の重要修正部分。
        #
        # MALFORMED_RESPONSEなど、
        # 「API呼び出し自体は成功したが中身が空」
        # のケースも再試行する。
        #
        # ==================================================

        last_error = None


        for attempt in range(
            1,
            GEMINI_MAX_RETRIES + 1
        ):

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


            try:

                # ==================================================
                # Gemini呼び出し
                # ==================================================

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


                # ==================================================
                # レスポンス確認
                # ==================================================

                log_response_debug(
                    response
                )


                # ==================================================
                # finish_reason確認
                # ==================================================

                finish_reason_text = ""


                try:

                    candidates = getattr(
                        response,
                        "candidates",
                        None
                    )


                    if candidates:

                        first_candidate = candidates[0]


                        finish_reason = getattr(
                            first_candidate,
                            "finish_reason",
                            None
                        )


                        finish_reason_text = str(
                            finish_reason
                        ).upper()


                        print(
                            "[GEMINI] finish_reason:",
                            finish_reason_text
                        )


                except Exception as error:

                    print(
                        "[GEMINI] finish_reason取得失敗:",
                        repr(error)
                    )


                # ==================================================
                # テキスト取得
                # ==================================================

                raw_text = extract_response_text(
                    response
                )


                print(
                    "[GEMINI] 抽出テキスト長:",
                    len(raw_text)
                )


                # ==================================================
                # テキストが空
                #
                # MALFORMED_RESPONSEを含めて
                # 一時的な異常として再試行する。
                # ==================================================

                if not raw_text:

                    last_error = RuntimeError(
                        "Geminiレスポンスにテキストがありません"
                    )


                    print(
                        ">>> Geminiレスポンスに"
                        "テキストがありません"
                    )


                    if attempt < GEMINI_MAX_RETRIES:

                        wait_seconds = (
                            attempt
                            *
                            GEMINI_RETRY_WAIT_SECONDS
                        )


                        print(
                            ">>> 空レスポンスのため",
                            wait_seconds,
                            "秒待って再試行します"
                        )


                        time.sleep(
                            wait_seconds
                        )


                        continue


                    raise last_error


                # ==================================================
                # SRT整形
                # ==================================================

                srt_text = clean_srt_text(
                    raw_text
                )


                print(
                    "[GEMINI] 整形後SRT長:",
                    len(srt_text)
                )


                # ==================================================
                # SRTチェック
                # ==================================================

                try:

                    validate_srt_text(
                        srt_text
                    )


                except Exception as validation_error:

                    last_error = validation_error


                    print(
                        ">>> SRT形式チェック失敗:",
                        repr(validation_error)
                    )


                    print(
                        ">>> Gemini結果:"
                    )


                    print(
                        raw_text[:3000]
                    )


                    if attempt < GEMINI_MAX_RETRIES:

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


                    raise RuntimeError(

                        "Geminiから有効なSRTを"
                        "取得できませんでした: "
                        +
                        str(validation_error)

                    ) from validation_error


                # ==================================================
                # 成功
                # ==================================================

                print(
                    "=========================================="
                )

                print(
                    "[GEMINI] 解析完了"
                )

                print(
                    "[GEMINI] SRT文字数:",
                    len(srt_text)
                )

                print(
                    "=========================================="
                )


                return srt_text


            except Exception as error:

                last_error = error


                print(
                    ">>> Gemini generate_contentエラー"
                )

                print(
                    ">>> TYPE:",
                    type(error).__name__
                )

                print(
                    ">>> ERROR:",
                    repr(error)
                )


                # ==================================================
                # 重要:
                #
                # INTERNAL / MALFORMED_RESPONSE / 503などは
                # 一時エラーとして再試行する。
                # ==================================================

                retryable = (

                    is_retryable_gemini_error(
                        error
                    )

                    or

                    "MALFORMED_RESPONSE"
                    in
                    str(error).upper()

                    or

                    "INTERNAL"
                    in
                    str(error).upper()

                    or

                    "EMPTY"
                    in
                    str(error).upper()

                    or

                    "テキストがありません"
                    in
                    str(error)

                )


                print(
                    ">>> リトライ対象:",
                    retryable
                )


                if attempt >= GEMINI_MAX_RETRIES:

                    print(
                        ">>> 最大リトライ回数に到達"
                    )

                    raise


                if not retryable:

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
        # 念のため
        # ======================================================

        if last_error is not None:

            raise last_error


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
                    "[GEMINI] WARNING:"
                    "uploaded file削除失敗:",
                    repr(error)
                )


        # ======================================================
        # 一時MP3削除
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
                    "Gemini一時MP3削除:",
                    temp_mp3
                )


            except Exception as error:

                print(
                    "[GEMINI] WARNING:"
                    "一時MP3削除失敗:",
                    repr(error)
                )


# ==========================================================
# SRT保存
#
# MP3:
#   sample.mp3
#
# SRT:
#   sample.srt
#
# ==========================================================

def save_srt(
    mp3_path,
    srt_text
):

    mp3_path = os.path.abspath(
        str(mp3_path)
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
# 入口は変更しない
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

                    "success": False,

                    "message":
                        "JSONデータがありません"

                }), 400


            # ==================================================
            # ファイル名
            # ==================================================

            filename = data.get(
                "file"
            )


            if not filename:

                return jsonify({

                    "success": False,

                    "message":
                        "MP3ファイル名がありません"

                }), 400


            filename = str(
                filename
            ).strip()


            if not filename:

                return jsonify({

                    "success": False,

                    "message":
                        "MP3ファイル名がありません"

                }), 400


            # ==================================================
            # basename
            # ==================================================

            filename = os.path.basename(
                filename
            )


            # ==================================================
            # MP3限定
            # ==================================================

            if not filename.lower().endswith(
                ".mp3"
            ):

                return jsonify({

                    "success": False,

                    "message":
                        "MP3ファイルを指定してください"

                }), 400


            # ==================================================
            # DOWNLOAD_DIR
            # ==================================================

            download_root = os.path.abspath(
                str(DOWNLOAD_DIR)
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

                common_path = os.path.commonpath([

                    download_root,
                    mp3_path

                ])

            except ValueError:

                common_path = None


            if common_path != download_root:

                return jsonify({

                    "success": False,

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

                    "success": False,

                    "message":
                        f"MP3がありません: {filename}"

                }), 404


            if not os.path.isfile(
                mp3_path
            ):

                return jsonify({

                    "success": False,

                    "message":
                        "指定されたパスはファイルではありません"

                }), 400


            mp3_size = os.path.getsize(
                mp3_path
            )


            if mp3_size <= 0:

                return jsonify({

                    "success": False,

                    "message":
                        "MP3ファイルが0 bytesです"

                }), 400


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

                "success": True,

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
                "[GEMINI ROUTE] FILE NOT FOUND:",
                str(error)
            )


            return jsonify({

                "success": False,

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

                "success": False,

                "message":
                    str(error)

            }), 500
