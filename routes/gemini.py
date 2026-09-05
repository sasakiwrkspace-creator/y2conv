# ==========================================================
# gemini.py
#
# Gemini 音声文字起こし
#
# 役割:
#   MP3 -> Gemini Files API -> Gemini -> SRT形式文字起こし
# ==========================================================

import os
import re
import uuid
import shutil
import tempfile
import time

from dotenv import load_dotenv
from flask import request, jsonify
from google import genai
from google.genai import types

from config import DOWNLOAD_DIR

# ==========================================================
# 環境変数
# ==========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY が設定されていません")

# ==========================================================
# Gemini Client
# ==========================================================

client = genai.Client(api_key=GEMINI_API_KEY)

# 推奨モデル例: gemini-2.5-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ==========================================================
# 設定値
# ==========================================================

GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
GEMINI_RETRY_WAIT_SECONDS = int(os.getenv("GEMINI_RETRY_WAIT_SECONDS", "3"))
GEMINI_FILE_WAIT_SECONDS = int(os.getenv("GEMINI_FILE_WAIT_SECONDS", "2"))
GEMINI_FILE_MAX_WAIT = int(os.getenv("GEMINI_FILE_MAX_WAIT", "60"))
MIN_SRT_TEXT_LENGTH = int(os.getenv("MIN_SRT_TEXT_LENGTH", "5"))

# ==========================================================
# リトライ対象エラー判定
# ==========================================================

def is_retryable_gemini_error(error):
    error_text = str(error).lower()
    retryable_codes = [
        "408", "409", "429", "500", "502", "503", "504",
        "too many requests", "rate limit", "temporarily unavailable",
        "service unavailable", "bad gateway", "gateway timeout",
        "internal server error", "timeout", "timed out",
        "deadline exceeded", "resource exhausted", "connection reset",
        "connection aborted", "connection error"
    ]
    return any(code in error_text for code in retryable_codes)

# ==========================================================
# デバッグ・レスポンス解析
# ==========================================================

def log_response_debug(response):
    print("==========================================")
    print("[GEMINI] RESPONSE DEBUG")
    print("response type:", type(response).__name__)

    try:
        response_text = getattr(response, "text", None)
        if response_text is None:
            print("response.text: None")
        else:
            print("response.text length:", len(str(response_text)))
            print("response.text preview:", str(response_text)[:500])
    except Exception as error:
        print("response.text取得エラー:", repr(error))

    try:
        candidates = getattr(response, "candidates", None)
        if candidates is None:
            print("candidates: None")
        else:
            print("candidates count:", len(candidates))
            for index, candidate in enumerate(candidates):
                finish_reason = getattr(candidate, "finish_reason", None)
                safety_ratings = getattr(candidate, "safety_ratings", None)
                print(f"candidate[{index}] finish_reason:", finish_reason)
                print(f"candidate[{index}] safety_ratings:", safety_ratings)
    except Exception as error:
        print("candidates解析ログエラー:", repr(error))

    print("==========================================")

def extract_response_text(response):
    if response is None:
        return ""

    try:
        response_text = getattr(response, "text", None)
        if response_text:
            text_str = str(response_text).strip()
            if text_str:
                return text_str
    except Exception as error:
        print("[GEMINI] response.text取得失敗:", repr(error))

    try:
        candidates = getattr(response, "candidates", None)
        if candidates:
            collected_parts = []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                if not content:
                    continue
                parts = getattr(content, "parts", None)
                if not parts:
                    continue
                for part in parts:
                    part_text = getattr(part, "text", None)
                    if part_text:
                        collected_parts.append(str(part_text))
            if collected_parts:
                return "\n".join(collected_parts).strip()
    except Exception as error:
        print("[GEMINI] candidatesからのテキスト取得失敗:", repr(error))

    return ""

# ==========================================================
# SRT整形・検証
# ==========================================================

def clean_srt_text(text):
    if not text:
        return ""
    
    text = str(text).strip()
    # Markdownコードブロック削除
    text = re.sub(r"^\s*```(?:srt|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```\s*$", "", text, flags=re.IGNORECASE)
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    
    # 最初の字幕番号(数字のみの行)まで前置きをスキップ
    match = re.search(r"(?m)^\s*\d+\s*$", text)
    if match:
        text = text[match.start():]

    return text.strip()

def validate_srt_text(srt_text):
    if not srt_text:
        raise ValueError("Gemini結果が空です")

    text = str(srt_text).strip()
    if len(text) < MIN_SRT_TEXT_LENGTH:
        raise ValueError(f"Gemini結果が短すぎます: {len(text)}文字")

    timestamp_pattern = re.compile(
        r"\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}"
    )
    if not timestamp_pattern.search(text):
        raise ValueError("Gemini結果にSRTの時間情報が含まれていません")

    if not re.search(r"(?m)^\s*\d+\s*$", text):
        raise ValueError("Gemini結果にSRT字幕番号が含まれていません")

    return True

# ==========================================================
# Files API 状態管理
# ==========================================================

def wait_for_uploaded_file_ready(uploaded_file):
    if uploaded_file is None:
        raise ValueError("Gemini uploaded_file がありません")

    print(">>> Gemini uploaded file 状態確認開始")
    start_time = time.time()

    while True:
        state = getattr(uploaded_file, "state", None)
        state_name = str(getattr(state, "name", state or "UNKNOWN")).upper()
        print(">>> Gemini file state:", state_name)

        if "ACTIVE" in state_name or state_name == "UNKNOWN":
            print(">>> Gemini file ACTIVE (準備完了)")
            return uploaded_file

        if "FAILED" in state_name or "ERROR" in state_name:
            raise RuntimeError(f"Gemini Files APIのファイル処理失敗: {state_name}")

        if time.time() - start_time >= GEMINI_FILE_MAX_WAIT:
            raise TimeoutError(f"Files API処理タイムアウト (state={state_name})")

        print(f">>> Gemini file 処理中。{GEMINI_FILE_WAIT_SECONDS}秒待機します")
        time.sleep(GEMINI_FILE_WAIT_SECONDS)

        file_name = getattr(uploaded_file, "name", None)
        if file_name:
            try:
                uploaded_file = client.files.get(name=file_name)
            except Exception as error:
                print(">>> Gemini file state取得エラー:", repr(error))
                if is_retryable_gemini_error(error):
                    continue
                raise

# ==========================================================
# メイン文字起こし処理
# ==========================================================

def transcribe_mp3(mp3_path):
    mp3_path = os.path.abspath(str(mp3_path))

    if not os.path.isfile(mp3_path) or not mp3_path.lower().endswith(".mp3"):
        raise ValueError("有効なMP3ファイルを指定してください")

    mp3_size = os.path.getsize(mp3_path)
    if mp3_size <= 0:
        raise ValueError("MP3ファイルが0 bytesです")

    print("==========================================")
    print("[GEMINI] 解析開始")
    print("[GEMINI] MP3:", mp3_path)
    print("[GEMINI] MP3サイズ:", mp3_size, "bytes")
    print("[GEMINI] モデル:", GEMINI_MODEL)
    print("==========================================")

    # 日本語ファイル名回避のため一時パスを作成
    temp_mp3 = os.path.join(
        tempfile.gettempdir(), f"gemini_audio_{uuid.uuid4().hex}.mp3"
    )
    uploaded_file = None

    try:
        shutil.copy2(mp3_path, temp_mp3)

        # --------------------------------------------------
        # 1. Files API Upload (リトライ付き)
        # --------------------------------------------------
        print(">>> Gemini Files API upload開始")
        for upload_attempt in range(1, GEMINI_MAX_RETRIES + 1):
            try:
                uploaded_file = client.files.upload(file=temp_mp3)
                print(">>> Gemini Files API upload成功")
                break
            except Exception as error:
                print(f">>> Upload失敗 (試行 {upload_attempt}/{GEMINI_MAX_RETRIES}): {repr(error)}")
                retryable = is_retryable_gemini_error(error)
                if upload_attempt >= GEMINI_MAX_RETRIES or not retryable:
                    raise
                
                wait_sec = upload_attempt * GEMINI_RETRY_WAIT_SECONDS
                print(f">>> {wait_sec}秒待機してupload再試行")
                time.sleep(wait_sec)

        uploaded_file = wait_for_uploaded_file_ready(uploaded_file)

        # --------------------------------------------------
        # 2. プロンプト設定 (System Instruction を使用)
        # --------------------------------------------------
        system_instruction = (
            "あなたはプロの字幕作成AIです。提供された音声ファイルを正確に文字起こしし、"
            "指定されたSRTフォーマットのみを出力してください。挨拶、前置き、後書き、"
            "Markdownのコードブロック(```)などは絶対に出力に含めないでください。"
        )

        prompt = """渡されたMP3音声を最初から最後まですべて正確に日本語で文字起こしし、SRT形式テキストのみを出力してください。

SRT形式例:
1
00:00:00,000 --> 00:00:05,000
字幕文章

2
00:00:05,000 --> 00:00:10,000
字幕文章
"""

        # --------------------------------------------------
        # 3. Content Generation (リトライ付き)
        # --------------------------------------------------
        print(">>> Gemini generate_content開始")
        for attempt in range(1, GEMINI_MAX_RETRIES + 1):
            try:
                print(f"[GEMINI] generate_content 試行: {attempt}/{GEMINI_MAX_RETRIES}")
                
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[uploaded_file, prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1,  # フォーマットの揺れを防ぐため低く設定
                    )
                )

                print(">>> Gemini generate_content API成功")
                log_response_debug(response)

                raw_text = extract_response_text(response)
                
                if not raw_text:
                    print(">>> 空レスポンス受信")
                    if attempt >= GEMINI_MAX_RETRIES:
                        raise RuntimeError("Geminiからのレスポンス結果が空でした")
                    time.sleep(attempt * GEMINI_RETRY_WAIT_SECONDS)
                    continue

                srt_text = clean_srt_text(raw_text)
                validate_srt_text(srt_text)

                print("==========================================")
                print("[GEMINI] 解析完了")
                print("[GEMINI] SRT文字数:", len(srt_text))
                print("==========================================")

                return srt_text

            except Exception as error:
                print(f">>> generate_content失敗: {repr(error)}")
                retryable = is_retryable_gemini_error(error)

                if attempt >= GEMINI_MAX_RETRIES or not retryable:
                    raise error

                wait_sec = attempt * GEMINI_RETRY_WAIT_SECONDS
                print(f">>> リトライ対象エラーのため {wait_sec}秒待機して再試行")
                time.sleep(wait_sec)

    finally:
        # ローカル一時ファイルの削除
        if os.path.exists(temp_mp3):
            try:
                os.remove(temp_mp3)
            except Exception:
                pass
        
        # Gemini Files API のリモートファイル削除
        if uploaded_file and hasattr(uploaded_file, "name"):
            try:
                client.files.delete(name=uploaded_file.name)
                print(">>> リモートファイルのクリーンアップ完了")
            except Exception as clean_err:
                print(f">>> リモートファイル削除スキップ/失敗: {clean_err}")
