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
#   Gemini 3.5 Transcribe
#     ↓
#   単語タイムスタンプ付き文字起こし
#     ↓
#   PythonでSRT生成
#
# ==========================================================
#
# 入口・出口は従来と同じ。
#
#   transcribe_mp3(mp3_path)
#       ↓
#   SRT文字列を返す
#
#   save_srt(mp3_path, srt_text)
#       ↓
#   .srtを保存
#
# subtitle_routes.py 側は変更不要。
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
# 音声文字起こし専用モデルを使用する。
#
# 環境変数 GEMINI_MODEL があればそれを使用。
#
# Renderでは、
#
# GEMINI_MODEL=gemini-3.5-transcribe
#
# を推奨。
# ==========================================================

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-transcribe"
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
# Files API待機設定
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

# 1字幕あたりのおおよその最大文字数。
#
# 日本語字幕では30～40文字程度を目安にする。
# ==========================================================

SRT_MAX_CHARS = int(
    os.getenv(
        "SRT_MAX_CHARS",
        "32"
    )
)


# 1字幕の最大表示時間。
# ==========================================================

SRT_MAX_DURATION = float(
    os.getenv(
        "SRT_MAX_DURATION",
        "5.0"
    )
)


# 単語間にこの秒数以上の無音があれば
# 字幕を区切る。
# ==========================================================

SRT_PAUSE_THRESHOLD = float(
    os.getenv(
        "SRT_PAUSE_THRESHOLD",
        "0.8"
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
# 時間文字列を秒に変換
#
# 例:
#
# 0.100s
# 1.500s
# 12.345s
# ==========================================================

def offset_to_seconds(
    value
):

    if value is None:

        return None


    text = str(
        value
    ).strip()


    if not text:

        return None


    # ------------------------------------------------------
    # 末尾の s
    # ------------------------------------------------------

    text = text.rstrip(
        "sS"
    ).strip()


    # ------------------------------------------------------
    # 数値
    # ------------------------------------------------------

    try:

        return float(
            text
        )

    except Exception:

        return None


# ==========================================================
# 秒 → SRT時間
#
# 例:
#
# 0
# ↓
# 00:00:00,000
#
# ==========================================================

def seconds_to_srt_time(
    seconds
):

    if seconds is None:

        seconds = 0


    try:

        seconds = float(
            seconds
        )

    except Exception:

        seconds = 0


    if seconds < 0:

        seconds = 0


    milliseconds = int(
        round(
            seconds * 1000
        )
    )


    hours = (
        milliseconds
        // 3600000
    )


    milliseconds %= 3600000


    minutes = (
        milliseconds
        // 60000
    )


    milliseconds %= 60000


    secs = (
        milliseconds
        // 1000
    )


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
# Google Gemini 3.5 Transcribe の
# audio_transcription.words を解析する。
# ==========================================================

def extract_word_transcriptions(
    response
):

    words = []


    if response is None:

        return words


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

            transcription = getattr(
                part,
                "audio_transcription",
                None
            )


            if transcription is None:

                continue


            speaker = getattr(
                transcription,
                "speaker_label",
                ""
            )


            transcription_words = getattr(
                transcription,
                "words",
                None
            )


            if not transcription_words:

                continue


            for word_info in transcription_words:

                word = getattr(
                    word_info,
                    "word",
                    ""
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


                word = str(
                    word or ""
                ).strip()


                start = offset_to_seconds(
                    start_offset
                )


                end = offset_to_seconds(
                    end_offset
                )


                if not word:

                    continue


                if start is None:

                    continue


                if end is None:

                    end = start


                if end < start:

                    end = start


                words.append({

                    "word":
                        word,

                    "start":
                        start,

                    "end":
                        end,

                    "speaker":
                        str(
                            speaker or ""
                        )

                })


    return words


# ==========================================================
# 文字起こしテキスト取得
#
# タイムスタンプが取れなかった場合の
# フォールバックとして使用。
# ==========================================================

def extract_response_text(
    response
):

    if response is None:

        return ""


    try:

        response_text = getattr(
            response,
            "text",
            None
        )


        if response_text:

            return str(
                response_text
            ).strip()


    except Exception as error:

        print(
            "[GEMINI] response.text取得失敗:",
            repr(error)
        )


    return ""


# ==========================================================
# SRT生成
#
# Geminiの単語タイムスタンプから
# Python側でSRTを作る。
# ==========================================================

def words_to_srt(
    words
):

    if not words:

        raise ValueError(
            "Geminiから単語タイムスタンプを取得できませんでした"
        )


    subtitles = []


    current_words = []


    current_start = None
    current_end = None


    def flush_current():

        nonlocal current_words
        nonlocal current_start
        nonlocal current_end


        if not current_words:

            return


        text = ""


        for item in current_words:

            word = item["word"]


            # ----------------------------------------------
            # 日本語では基本的に単語間へスペースを入れない。
            #
            # ただし英数字同士などの場合は
            # Gemini側のスペースを尊重する。
            # ----------------------------------------------

            if not text:

                text = word

            else:

                previous = text[-1:]

                first = word[:1]


                if (

                    previous
                    and
                    first
                    and
                    (
                        previous.isascii()
                        and
                        first.isascii()
                    )

                ):

                    text += " " + word

                else:

                    text += word


        text = text.strip()


        if not text:

            current_words = []
            current_start = None
            current_end = None

            return


        # --------------------------------------------------
        # 最低表示時間を確保
        # --------------------------------------------------

        start = (
            current_start
            if current_start is not None
            else 0
        )


        end = (
            current_end
            if current_end is not None
            else start + 0.5
        )


        if end <= start:

            end = start + 0.5


        # --------------------------------------------------
        # SRT追加
        # --------------------------------------------------

        subtitles.append({

            "start":
                start,

            "end":
                end,

            "text":
                text

        })


        current_words = []
        current_start = None
        current_end = None


    # ======================================================
    # 単語を字幕単位にまとめる
    # ======================================================

    for word_info in words:

        word = word_info["word"]

        start = word_info["start"]

        end = word_info["end"]


        if current_start is None:

            current_start = start
            current_end = end
            current_words = [
                word_info
            ]

            continue


        current_text = ""


        for item in current_words:

            item_word = item["word"]


            if not current_text:

                current_text = item_word

            else:

                previous = current_text[-1:]
                first = item_word[:1]


                if (

                    previous
                    and
                    first
                    and
                    previous.isascii()
                    and
                    first.isascii()

                ):

                    current_text += (
                        " "
                        +
                        item_word
                    )

                else:

                    current_text += item_word


        # --------------------------------------------------
        # 今回の単語を追加した場合の文字数
        # --------------------------------------------------

        candidate_text = current_text


        if candidate_text:

            previous = candidate_text[-1:]
            first = word[:1]


            if (

                previous
                and
                first
                and
                previous.isascii()
                and
                first.isascii()

            ):

                candidate_text += (
                    " "
                    +
                    word
                )

            else:

                candidate_text += word

        else:

            candidate_text = word


        candidate_duration = (
            end
            -
            current_start
        )


        pause = (
            start
            -
            current_end
        )


        # --------------------------------------------------
        # 区切り判定
        # --------------------------------------------------

        should_split = False


        # 長すぎる字幕
        if len(candidate_text) > SRT_MAX_CHARS:

            should_split = True


        # 表示時間が長すぎる
        if candidate_duration > SRT_MAX_DURATION:

            should_split = True


        # 単語間の無音が長い
        if pause >= SRT_PAUSE_THRESHOLD:

            should_split = True


        # --------------------------------------------------
        # 区切る
        # --------------------------------------------------

        if should_split:

            flush_current()


            current_words = [
                word_info
            ]

            current_start = start
            current_end = end


        else:

            current_words.append(
                word_info
            )

            current_end = end


    # ------------------------------------------------------
    # 最後の字幕
    # ------------------------------------------------------

    flush_current()


    if not subtitles:

        raise ValueError(
            "SRT字幕を生成できませんでした"
        )


    # ======================================================
    # SRT本文
    # ======================================================

    srt_lines = []


    for index, subtitle in enumerate(

        subtitles,

        start=1

    ):

        start_time = seconds_to_srt_time(
            subtitle["start"]
        )


        end_time = seconds_to_srt_time(
            subtitle["end"]
        )


        text = subtitle["text"].strip()


        srt_lines.append(
            str(index)
        )


        srt_lines.append(

            f"{start_time} --> {end_time}"

        )


        srt_lines.append(
            text
        )


        srt_lines.append(
            ""
        )


    return "\n".join(
        srt_lines
    ).strip()


# ==========================================================
# SRT簡易チェック
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


    if len(text) < 5:

        raise ValueError(
            "生成されたSRTが短すぎます"
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
            "SRTの時間情報がありません"
        )


    if not re.search(

        r"(?m)^\s*\d+\s*$",

        text

    ):

        raise ValueError(
            "SRT字幕番号がありません"
        )


    return True


# ==========================================================
# Gemini Files API状態取得
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
# Gemini Files APIアップロード後の状態確認
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


    current_state = get_uploaded_file_state(
        uploaded_file
    )


    if current_state is None:

        print(
            ">>> uploaded_file.state を取得できません。"
            "そのまま処理を続行します。"
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


        if "ACTIVE" in state_name:

            print(
                ">>> Gemini file ACTIVE"
            )

            return uploaded_file


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
                ">>> Gemini file state取得エラー:",
                repr(error)
            )


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
#
# 入口:
#
#   transcribe_mp3(mp3_path)
#
# 出口:
#
#   SRT文字列
#
# subtitle_routes.py は変更不要。
# ==========================================================

def transcribe_mp3(
    mp3_path
):

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
    # 日本語ファイル名対策
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
        # 一時MP3
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

        print(
            ">>> Gemini Files API upload開始"
        )


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


                break


            except Exception as error:

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
                    "秒待って再試行します"
                )


                time.sleep(
                    wait_seconds
                )


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
        # Gemini Transcribe
        #
        # ここが今回の変更部分。
        #
        # SRTそのものをGeminiに生成させない。
        #
        # Geminiには、
        #
        #   音声
        #   ↓
        #   文字起こし
        #   ↓
        #   word timestamp
        #
        # を担当させる。
        #
        # SRTはPython側で生成する。
        # ==================================================

        print(
            ">>> Gemini Transcribe開始"
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
                    "[GEMINI] Transcribe"
                )

                print(
                    "[GEMINI] 試行:",
                    f"{attempt}/{GEMINI_MAX_RETRIES}"
                )

                print(
                    "[GEMINI] モデル:",
                    GEMINI_MODEL
                )

                print(
                    "------------------------------------------"
                )


                # --------------------------------------------------
                # 日本語固定
                #
                # word_timestamp=True
                # --------------------------------------------------

                response = client.models.generate_content(

                    model=GEMINI_MODEL,

                    contents=[
                        uploaded_file
                    ],

                    config=types.GenerateContentConfig(

                        audio_transcription_config=
                            types.AudioTranscriptionConfig(

                                language_codes=[
                                    "ja-JP"
                                ],

                                word_timestamp=True

                            )

                    )

                )


                print(
                    ">>> Gemini Transcribe API成功"
                )


                # --------------------------------------------------
                # response.text
                # --------------------------------------------------

                response_text = extract_response_text(
                    response
                )


                print(
                    ">>> Gemini transcript length:",
                    len(response_text)
                )


                # --------------------------------------------------
                # word timestamp
                # --------------------------------------------------

                words = extract_word_transcriptions(
                    response
                )


                print(
                    ">>> Gemini word timestamp count:",
                    len(words)
                )


                # --------------------------------------------------
                # word timestampからSRT生成
                # --------------------------------------------------

                if words:

                    srt_text = words_to_srt(
                        words
                    )


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
                        "[GEMINI] transcript文字数:",
                        len(response_text)
                    )

                    print(
                        "[GEMINI] word数:",
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


                # --------------------------------------------------
                # timestampがない場合
                # --------------------------------------------------

                print(
                    ">>> Geminiからword timestampが返されませんでした"
                )


                if response_text:

                    print(
                        ">>> transcript自体は取得できています"
                    )

                    print(
                        ">>> transcript preview:",
                        response_text[:1000]
                    )


                if attempt >= GEMINI_MAX_RETRIES:

                    raise RuntimeError(

                        "Gemini文字起こしは成功しましたが、"
                        "SRT生成に必要なタイムスタンプが"
                        "取得できませんでした"

                    )


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


            except Exception as error:

                print(
                    ">>> Gemini Transcribe失敗"
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
                    attempt
                    >=
                    GEMINI_MAX_RETRIES
                ):

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
                        "Gemini uploaded file削除:",
                        uploaded_name
                    )


                    client.files.delete(

                        name=uploaded_name

                    )


                    print(
                        "Gemini uploaded file削除完了"
                    )


            except Exception as error:

                print(

                    "Gemini uploaded file削除失敗:",
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

                    "Gemini一時MP3削除失敗:",
                    repr(error)

                )


# ==========================================================
# SRT保存
#
# 入口:
#
#   mp3_path
#   srt_text
#
# 出口:
#
#   srt_path
#
# ==========================================================

def save_srt(
    mp3_path,
    srt_text
):

    mp3_path = os.path.abspath(
        str(mp3_path)
    )


    # ======================================================
    # SRT本文確認
    # ======================================================

    if not srt_text:

        raise ValueError(
            "保存するSRT本文が空です"
        )


    srt_text = str(
        srt_text
    ).strip()


    if not srt_text:

        raise ValueError(
            "SRT本文が空です"
        )


    # ======================================================
    # SRT確認
    # ======================================================

    validate_srt_text(
        srt_text
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
# 既存のルートを維持。
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
