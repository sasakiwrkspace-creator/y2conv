# ==========================================================
# gemini.py
#
# Gemini 3.5 Transcribe 音声文字起こし
#
# MP3
#   ↓
# Gemini Files API
#   ↓
# gemini-3.5-transcribe
#   ↓
# word timestamp
#   ↓
# PythonでSRT生成
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
import google.genai

from dotenv import load_dotenv


from flask import (
    request,
    jsonify
)


from google import genai
from google.genai import types


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
# Renderの環境変数 GEMINI_MODEL があれば優先。
#
# 重要:
# デフォルトを Gemini 3.5 Transcribe に変更。
# ==========================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-transcribe"
)

print("==========================================")
print("[GEMINI] ENVIRONMENT")
print("[GEMINI] GEMINI_MODEL:", GEMINI_MODEL)
print("[GEMINI] google-genai version:", google.genai.__version__)
print("[GEMINI] Python:", os.sys.version)
print("==========================================")

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
# SRT設定
# ==========================================================

MIN_SRT_TEXT_LENGTH = int(
    os.getenv(
        "MIN_SRT_TEXT_LENGTH",
        "5"
    )
)


# 1字幕あたりの最大文字数
#
# 日本語では、おおむね30～45文字程度を目安にする。
# ==========================================================

SRT_MAX_CHARS = int(
    os.getenv(
        "SRT_MAX_CHARS",
        "42"
    )
)


# 1字幕の最大表示秒数
SRT_MAX_DURATION = float(
    os.getenv(
        "SRT_MAX_DURATION",
        "6.0"
    )
)


# 1字幕の最小表示秒数
SRT_MIN_DURATION = float(
    os.getenv(
        "SRT_MIN_DURATION",
        "0.5"
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
# Geminiレスポンス デバッグ
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
                        f"candidate[{index}] parts count:",
                        len(parts)
                        if parts
                        else 0
                    )


                    if parts:

                        for part_index, part in enumerate(
                            parts
                        ):

                            print(
                                f"candidate[{index}] part[{part_index}] type:",
                                type(part).__name__
                            )


                            audio_transcription = getattr(
                                part,
                                "audio_transcription",
                                None
                            )


                            if audio_transcription:

                                print(
                                    f"candidate[{index}] part[{part_index}] "
                                    "audio_transcription:",
                                    audio_transcription
                                )


    except Exception as error:

        print(
            "candidates解析エラー:",
            repr(error)
        )


    print(
        "=========================================="
    )


# ==========================================================
# 秒へ変換
#
# Gemini:
#   "0.100s"
#   "1.250s"
#
# をfloat秒へ変換。
# ==========================================================

def parse_timestamp_seconds(value):

    if value is None:

        return None


    text = str(
        value
    ).strip()


    if not text:

        return None


    # ------------------------------------------------------
    # 例:
    #
    # 0.100s
    # 1.250s
    # ------------------------------------------------------

    match = re.match(
        r"^\s*([0-9]+(?:\.[0-9]+)?)\s*s\s*$",
        text,
        flags=re.IGNORECASE
    )


    if match:

        return float(
            match.group(1)
        )


    # ------------------------------------------------------
    # 念のため数値だけにも対応
    # ------------------------------------------------------

    try:

        return float(
            text
        )

    except Exception:

        return None


# ==========================================================
# SRT timestamp
#
# seconds:
#   0.0
#
# →
#   00:00:00,000
# ==========================================================

def seconds_to_srt_timestamp(seconds):

    if seconds is None:

        seconds = 0.0


    seconds = max(
        0.0,
        float(seconds)
    )


    milliseconds = int(
        round(
            seconds * 1000
        )
    )


    hours = milliseconds // (
        60 * 60 * 1000
    )


    milliseconds %= (
        60 * 60 * 1000
    )


    minutes = milliseconds // (
        60 * 1000
    )


    milliseconds %= (
        60 * 1000
    )


    secs = milliseconds // 1000


    milliseconds %= 1000


    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )


# ==========================================================
# Geminiレスポンスから単語タイムスタンプを取得
#
# 期待する構造:
#
# candidates
#   ↓
# content.parts
#   ↓
# audio_transcription
#   ↓
# words
#
# word:
#   word
#   start_offset
#   end_offset
#
# ==========================================================

def extract_timestamped_words(response):

    words = []


    candidates = getattr(
        response,
        "candidates",
        None
    )


    if not candidates:

        return words


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

            audio_transcription = getattr(
                part,
                "audio_transcription",
                None
            )


            if audio_transcription is None:

                continue


            transcription_words = getattr(
                audio_transcription,
                "words",
                None
            )


            if not transcription_words:

                continue


            for word_info in transcription_words:

                word_text = getattr(
                    word_info,
                    "word",
                    None
                )


                start_offset = getattr(
                    word_info,
                    "start_offset",
                    None
                )


                end_offset = getattr(
                    word_info,
                    "end_offset",
                    None
                )


                # --------------------------------------------------
                # SDKによってcamelCaseになる場合にも対応
                # --------------------------------------------------

                if start_offset is None:

                    start_offset = getattr(
                        word_info,
                        "startOffset",
                        None
                    )


                if end_offset is None:

                    end_offset = getattr(
                        word_info,
                        "endOffset",
                        None
                    )


                if word_text is None:

                    continue


                word_text = str(
                    word_text
                )


                start_seconds = parse_timestamp_seconds(
                    start_offset
                )


                end_seconds = parse_timestamp_seconds(
                    end_offset
                )


                if start_seconds is None:

                    continue


                if end_seconds is None:

                    end_seconds = start_seconds


                words.append({

                    "word":
                        word_text,

                    "start":
                        start_seconds,

                    "end":
                        end_seconds,

                })


    return words


# ==========================================================
# 単語一覧からSRT生成
#
# 日本語を中心に、
#
# - 最大文字数
# - 最大表示時間
# - 句読点
# - 無音
#
# を利用して字幕をまとめる。
#
# ==========================================================

def words_to_srt(words):

    if not words:

        raise ValueError(
            "Geminiから単語タイムスタンプを取得できませんでした"
        )


    subtitles = []


    current_words = []


    current_start = None
    current_end = None


    def flush():

        nonlocal current_words
        nonlocal current_start
        nonlocal current_end


        if not current_words:

            return


        text = "".join(
            current_words
        ).strip()


        if not text:

            current_words = []

            current_start = None
            current_end = None

            return


        start = (
            current_start
            if current_start is not None
            else 0.0
        )


        end = (
            current_end
            if current_end is not None
            else start + SRT_MIN_DURATION
        )


        if end <= start:

            end = (
                start
                +
                SRT_MIN_DURATION
            )


        subtitles.append({

            "start": start,

            "end": end,

            "text": text,

        })


        current_words = []

        current_start = None

        current_end = None


    for index, item in enumerate(
        words
    ):

        word = str(
            item.get(
                "word",
                ""
            )
        )


        start = item.get(
            "start"
        )


        end = item.get(
            "end"
        )


        if not word:

            continue


        if start is None:

            continue


        if end is None:

            end = start


        # --------------------------------------------------
        # 新しい字幕を開始
        # --------------------------------------------------

        if current_start is None:

            current_start = start


        # --------------------------------------------------
        # 現在字幕に追加した場合の長さ
        # --------------------------------------------------

        candidate_text = (
            "".join(
                current_words
            )
            +
            word
        )


        candidate_duration = (
            end
            -
            current_start
        )


        # --------------------------------------------------
        # 句読点で字幕を切る
        # --------------------------------------------------

        punctuation_break = bool(

            re.search(
                r"[。！？!?]",
                word
            )

        )


        # --------------------------------------------------
        # 無音区間
        #
        # 前の単語終了から次の単語開始まで
        # 1秒以上空いていたら区切る。
        # --------------------------------------------------

        silence_break = False


        if current_end is not None:

            silence = (
                start
                -
                current_end
            )


            if silence >= 1.0:

                silence_break = True


        # --------------------------------------------------
        # 最大文字数
        # --------------------------------------------------

        length_break = (
            len(candidate_text)
            >
            SRT_MAX_CHARS
        )


        # --------------------------------------------------
        # 最大時間
        # --------------------------------------------------

        duration_break = (
            candidate_duration
            >
            SRT_MAX_DURATION
        )


        # --------------------------------------------------
        # 追加前に区切る
        #
        # ただし現在字幕が空なら追加する。
        # --------------------------------------------------

        if current_words and (

            length_break
            or
            duration_break
            or
            silence_break

        ):

            flush()

            current_start = start


        current_words.append(
            word
        )


        current_end = end


        # --------------------------------------------------
        # 句読点後は字幕を確定
        # --------------------------------------------------

        if punctuation_break:

            flush()


    # ------------------------------------------------------
    # 最後の字幕
    # ------------------------------------------------------

    flush()


    if not subtitles:

        raise ValueError(
            "字幕を生成できませんでした"
        )


    # ======================================================
    # SRT本文
    # ======================================================

    output = []


    for index, subtitle in enumerate(
        subtitles,
        start=1
    ):

        start = subtitle[
            "start"
        ]


        end = subtitle[
            "end"
        ]


        text = subtitle[
            "text"
        ]


        # --------------------------------------------------
        # 最低表示時間
        # --------------------------------------------------

        if (
            end - start
            <
            SRT_MIN_DURATION
        ):

            end = (
                start
                +
                SRT_MIN_DURATION
            )


        output.append(
            str(index)
        )


        output.append(

            seconds_to_srt_timestamp(
                start
            )
            +
            " --> "
            +
            seconds_to_srt_timestamp(
                end
            )

        )


        output.append(
            text
        )


        output.append("")


    return "\n".join(
        output
    ).strip()


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


    text = text.lstrip(
        "\ufeff"
    )


    text = text.replace(
        "\r\n",
        "\n"
    )


    text = text.replace(
        "\r",
        "\n"
    )


    return text.strip()


# ==========================================================
# SRT簡易チェック
# ==========================================================

def validate_srt_text(srt_text):

    if not srt_text:

        raise ValueError(
            "SRT結果が空です"
        )


    text = str(
        srt_text
    ).strip()


    if len(text) < MIN_SRT_TEXT_LENGTH:

        raise ValueError(
            "SRT結果が短すぎます: "
            +
            str(len(text))
            +
            "文字"
        )


    timestamp_pattern = re.compile(

        r"\d{2}:\d{2}:\d{2},\d{3}"
        r"\s*-->\s*"
        r"\d{2}:\d{2}:\d{2},\d{3}"

    )


    if not timestamp_pattern.search(
        text
    ):

        raise ValueError(
            "SRT結果に時間情報がありません"
        )


    if not re.search(
        r"(?m)^\s*\d+\s*$",
        text
    ):

        raise ValueError(
            "SRT結果に字幕番号がありません"
        )


    return True


# ==========================================================
# Files API状態取得
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
# Files API処理待機
# ==========================================================

def wait_for_uploaded_file_ready(
    uploaded_file
):

    if uploaded_file is None:

        raise ValueError(
            "Gemini uploaded_file がありません"
        )


    current_state = get_uploaded_file_state(
        uploaded_file
    )


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


        if "ACTIVE" in state_name:

            return uploaded_file


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


        if (
            time.time()
            -
            start_time
            >=
            GEMINI_FILE_MAX_WAIT
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


    print(
        "=========================================="
    )

    print(
        "Gemini 3.5 Transcribe 解析開始"
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
        "タイムスタンプ:",
        "word_timestamp=True"
    )

    print(
        "日本語:",
        "language_codes=['ja-JP']"
    )

    print(
        "SRT生成:",
        "Python"
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
                    f"{upload_attempt}/"
                    f"{GEMINI_MAX_RETRIES}"
                )


                uploaded_file = client.files.upload(

                    file=temp_mp3

                )


                print(
                    ">>> Gemini Files API upload成功"
                )


                print(
                    ">>> file name:",
                    getattr(
                        uploaded_file,
                        "name",
                        None
                    )
                )


                print(
                    ">>> file uri:",
                    getattr(
                        uploaded_file,
                        "uri",
                        None
                    )
                )


                print(
                    ">>> mime type:",
                    getattr(
                        uploaded_file,
                        "mime_type",
                        None
                    )
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
        # Gemini Transcribe
        #
        # Google公式仕様:
        #
        # audio_transcription_config=
        #     AudioTranscriptionConfig(
        #         language_codes=["ja-JP"],
        #         word_timestamp=True,
        #     )
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
                "[GEMINI] Transcribe"
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
                # Gemini 3.5 Transcribe
                # ==================================================

                response = client.models.generate_content(

                    model=GEMINI_MODEL,

                    contents=[
                        uploaded_file
                    ],

                    config=types.GenerateContentConfig(

                        audio_transcription_config=(
                            types.AudioTranscriptionConfig(

                                language_codes=[
                                    "ja-JP"
                                ],

                                word_timestamp=True

                            )
                        )

                    )

                )


                print(
                    ">>> Gemini Transcribe API成功"
                )


                # ==================================================
                # レスポンスデバッグ
                # ==================================================

                log_response_debug(
                    response
                )


                # ==================================================
                # word timestamp取得
                # ==================================================

                words = extract_timestamped_words(
                    response
                )


                print(
                    "[GEMINI] timestamp付き単語数:",
                    len(words)
                )


                if not words:

                    # --------------------------------------------------
                    # timestampが返らなかった場合の診断用
                    # --------------------------------------------------

                    response_text = getattr(
                        response,
                        "text",
                        None
                    )


                    print(
                        "[GEMINI] response.text:",
                        repr(response_text)[:3000]
                    )


                    raise RuntimeError(
                        "Geminiからword timestampが"
                        "返されませんでした"
                    )


                # ==================================================
                # SRT生成
                # ==================================================

                srt_text = words_to_srt(
                    words
                )


                srt_text = clean_srt_text(
                    srt_text
                )


                print(
                    "[GEMINI] SRT文字数:",
                    len(srt_text)
                )


                # ==================================================
                # SRTチェック
                # ==================================================

                validate_srt_text(
                    srt_text
                )


                print(
                    "=========================================="
                )

                print(
                    "[GEMINI] 解析完了"
                )

                print(
                    "[GEMINI] timestamp付き単語数:",
                    len(words)
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
                    ">>> Gemini Transcribeエラー"
                )

                print(
                    ">>> TYPE:",
                    type(error).__name__
                )

                print(
                    ">>> ERROR:",
                    repr(error)
                )


                retryable = (

                    is_retryable_gemini_error(
                        error
                    )

                    or

                    "INTERNAL"
                    in
                    str(error).upper()

                    or

                    "MALFORMED_RESPONSE"
                    in
                    str(error).upper()

                    or

                    "TIMESTAMP"
                    in
                    str(error).upper()

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


        if last_error is not None:

            raise last_error


        raise RuntimeError(
            "Gemini文字起こし処理が"
            "完了しませんでした"
        )


    finally:

        # ==================================================
        # Gemini Files API削除
        # ==================================================

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


        # ==================================================
        # 一時MP3削除
        #
        # 元MP3は削除しない。
        # ==================================================

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
