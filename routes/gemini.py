import os
import uuid
import shutil
import tempfile
import time

from dotenv import load_dotenv
from flask import request, jsonify
from google import genai

from config import DOWNLOAD_DIR


# ==========================================================
# Gemini API設定
# ==========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY が設定されていません"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==========================================================
# Geminiモデル
#
# ※ 現在使用しているモデル名をここで指定。
# ==========================================================

GEMINI_MODEL = "gemini-3.5-flash"


# ==========================================================
# Gemini APIリトライ設定
#
# 429 / 500 / 502 / 503 / 504
# などの一時的なエラーが発生した場合、
# 少し待ってから再試行する。
#
# 最大3回
# ==========================================================

GEMINI_MAX_RETRIES = 3


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
        "timeout"

    ]


    for code in retryable_codes:

        if code in error_text:

            return True


    return False


# ==========================================================
# Geminiレスポンス詳細ログ
#
# response.text が空だった場合に、
# candidates / prompt_feedback /
# usage_metadata などを確認する。
# ==========================================================

def log_gemini_response_details(
    response
):

    print(
        "=========================================="
    )

    print(
        "Geminiレスポンス詳細"
    )

    print(
        "=========================================="
    )


    # ------------------------------------------------------
    # response type
    # ------------------------------------------------------

    try:

        print(
            "response type:",
            type(response).__name__
        )

    except Exception as e:

        print(
            "response type取得失敗:",
            repr(e)
        )


    # ------------------------------------------------------
    # response repr
    # ------------------------------------------------------

    try:

        print(
            "response repr:"
        )

        print(
            repr(response)
        )

    except Exception as e:

        print(
            "response repr取得失敗:",
            repr(e)
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
            "response.text:"
        )

        print(
            repr(response_text)
        )

    except Exception as e:

        print(
            "response.text取得失敗:",
            repr(e)
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

        print(
            "candidates:"
        )

        print(
            repr(candidates)
        )

    except Exception as e:

        print(
            "candidates取得失敗:",
            repr(e)
        )


    # ------------------------------------------------------
    # candidates詳細
    # ------------------------------------------------------

    try:

        candidates = getattr(
            response,
            "candidates",
            None
        )


        if candidates:

            print(
                "candidate count:",
                len(candidates)
            )


            for index, candidate in enumerate(
                candidates
            ):

                print(
                    "------------------------------------------"
                )

                print(
                    "candidate:",
                    index
                )

                print(
                    "candidate repr:"
                )

                print(
                    repr(candidate)
                )


                try:

                    finish_reason = getattr(
                        candidate,
                        "finish_reason",
                        None
                    )

                    print(
                        "finish_reason:",
                        repr(finish_reason)
                    )

                except Exception as e:

                    print(
                        "finish_reason取得失敗:",
                        repr(e)
                    )


                try:

                    content = getattr(
                        candidate,
                        "content",
                        None
                    )

                    print(
                        "content:"
                    )

                    print(
                        repr(content)
                    )

                except Exception as e:

                    print(
                        "content取得失敗:",
                        repr(e)
                    )

        else:

            print(
                "candidateはありません"
            )

    except Exception as e:

        print(
            "candidates詳細取得失敗:",
            repr(e)
        )


    # ------------------------------------------------------
    # prompt_feedback
    # ------------------------------------------------------

    try:

        prompt_feedback = getattr(
            response,
            "prompt_feedback",
            None
        )

        print(
            "prompt_feedback:"
        )

        print(
            repr(prompt_feedback)
        )

    except Exception as e:

        print(
            "prompt_feedback取得失敗:",
            repr(e)
        )


    # ------------------------------------------------------
    # usage_metadata
    # ------------------------------------------------------

    try:

        usage_metadata = getattr(
            response,
            "usage_metadata",
            None
        )

        print(
            "usage_metadata:"
        )

        print(
            repr(usage_metadata)
        )

    except Exception as e:

        print(
            "usage_metadata取得失敗:",
            repr(e)
        )


    print(
        "=========================================="
    )


# ==========================================================
# GeminiへMP3送信
#
# 重要:
#
# Gemini側では時間を一切判断しない。
#
# MP3のカット処理も一切行わない。
#
# /convert
#     ↓
# 指定時間にカット済みMP3
#     ↓
# gemini.py
#     ↓
# MP3全体をGeminiへ送信
#     ↓
# SRT
#
# という構成。
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

            f"MP3がありません: "
            f"{mp3_path}"

        )


    if not os.path.isfile(
        mp3_path
    ):

        raise ValueError(
            "指定されたパスはファイルではありません"
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
    #
    # 元MP3:
    #
    # 日本語タイトル.mp3
    #
    # ↓
    #
    # /tmp/gemini_audio_UUID.mp3
    #
    # Gemini upload
    #
    # 元MP3は変更・削除しない。
    # ======================================================

    temp_mp3 = os.path.join(

        tempfile.gettempdir(),

        "gemini_audio_"
        + uuid.uuid4().hex
        + ".mp3"

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
            "Gemini upload用一時MP3:",
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
            "Gemini送信用MP3サイズ:",
            temp_size,
            "bytes"
        )


        # ==================================================
        # Gemini Files API
        # ==================================================

        print(
            ">>> Gemini Files API upload開始"
        )


        try:

            uploaded_file = client.files.upload(

                file=temp_mp3

            )


            print(
                ">>> Gemini Files API upload成功"
            )

            print(
                ">>> uploaded_file:",
                repr(uploaded_file)
            )


        except Exception as e:

            print(
                ">>> Gemini Files API upload失敗"
            )

            print(
                ">>> TYPE:",
                type(e).__name__
            )

            print(
                ">>> ERROR:",
                repr(e)
            )

            raise


        # ==================================================
        # アップロード結果確認
        # ==================================================

        if uploaded_file is None:

            raise RuntimeError(
                "Gemini Files APIからアップロード結果が返されませんでした"
            )


        # ==================================================
        # Geminiプロンプト
        #
        # 重要:
        #
        # Geminiに時間範囲を判断させない。
        #
        # 渡されたMP3全体を文字起こしする。
        # ==================================================

        prompt = """
この音声ファイル全体を日本語で正確に文字起こししてください。

重要:

・このMP3に含まれている音声を最初から最後まで対象にする
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
・各字幕に時間情報を付ける
・SRT形式で出力する
・説明文を書かない
・前置きを書かない
・後書きを書かない
・Markdownのコードブロックを使用しない
・```srt を付けない

このMP3はすでに必要な時間範囲に変換済みです。

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
"""


        # ==================================================
        # Gemini generate_content
        #
        # 502 / 503 / 504 / 429
        # などの場合は自動リトライ
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
                    "Gemini generate_content"
                )

                print(
                    "試行:",
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
                    ">>> Gemini generate_content成功"
                )


                break


            except Exception as e:

                print(
                    ">>> Gemini generate_content失敗"
                )

                print(
                    ">>> TYPE:",
                    type(e).__name__
                )

                print(
                    ">>> ERROR:",
                    repr(e)
                )


                # ------------------------------------------
                # リトライ可能か確認
                # ------------------------------------------

                retryable = (

                    is_retryable_gemini_error(
                        e
                    )

                )


                print(
                    ">>> リトライ対象:",
                    retryable
                )


                # ------------------------------------------
                # 最大リトライ回数
                # ------------------------------------------

                if (

                    attempt
                    >=
                    GEMINI_MAX_RETRIES

                ):

                    print(
                        ">>> 最大リトライ回数に到達しました"
                    )

                    raise


                # ------------------------------------------
                # リトライ対象外
                # ------------------------------------------

                if not retryable:

                    print(
                        ">>> 一時的エラーではないため"
                        "リトライしません"
                    )

                    raise


                # ------------------------------------------
                # 待機
                #
                # 1回目: 3秒
                # 2回目: 6秒
                # ------------------------------------------

                wait_seconds = (
                    attempt * 3
                )


                print(
                    ">>>",
                    wait_seconds,
                    "秒待って再試行します"
                )


                time.sleep(
                    wait_seconds
                )


        # ==================================================
        # レスポンス確認
        # ==================================================

        if response is None:

            raise RuntimeError(
                "Geminiからレスポンスが返されませんでした"
            )


        # ==================================================
        # response.text取得
        # ==================================================

        response_text = None


        try:

            response_text = getattr(
                response,
                "text",
                None
            )

        except Exception as e:

            print(
                "Gemini response.text取得エラー"
            )

            print(
                "TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                repr(e)
            )


        # ==================================================
        # テキストが取得できた場合
        # ==================================================

        if response_text:

            response_text = str(
                response_text
            ).strip()


        if response_text:

            print(
                "=========================================="
            )

            print(
                "Gemini解析完了"
            )

            print(
                "Gemini結果文字数:",
                len(response_text)
            )

            print(
                "=========================================="
            )


            return response_text


        # ==================================================
        # response.text が空の場合
        #
        # 原因調査用に詳細ログを出す。
        # ==================================================

        print(
            "=========================================="
        )

        print(
            "Gemini結果が空です"
        )

        print(
            "response.text は空でした"
        )

        print(
            "=========================================="
        )


        log_gemini_response_details(
            response
        )


        raise RuntimeError(

            "Gemini結果が空です。"
            "Geminiのcandidates / "
            "prompt_feedback / "
            "finish_reasonを確認してください。"

        )


    finally:

        # ==================================================
        # Gemini用一時MP3削除
        #
        # 元MP3は絶対に削除しない。
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


            except Exception as e:

                print(

                    "WARNING: "
                    "Gemini一時MP3削除失敗:",
                    repr(e)

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
# 日本語タイトルでも問題なし。
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
            "SRTとして保存するテキストが空です"
        )


    srt_text = str(
        srt_text
    ).strip()


    if not srt_text:

        raise ValueError(
            "SRTとして保存するテキストが空です"
        )


    srt_path = (

        os.path.splitext(
            mp3_path
        )[0]

        + ".srt"

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
            "SRTファイルが作成されませんでした: "
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

        raise IOError(
            "SRTファイルが0 bytesです: "
            +
            srt_path
        )


    print(
        "SRT保存:",
        srt_path
    )

    print(
        "SRTサイズ:",
        srt_size,
        "bytes"
    )


    return srt_path


# ==========================================================
# Flask Route
#
# /gemini-transcribe
#
# 重要:
#
# Gemini側では時間指定を一切処理しない。
#
# start_time
# end_time
# original_start_time
# original_end_time
#
# などが送信されても使用しない。
#
# 必要なのはMP3ファイル名だけ。
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
            # ファイル名をbasenameに限定
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
            # downloadsの絶対パス
            #
            # config.pyのDOWNLOAD_DIRを使用
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
            # MP3サイズ確認
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
            # Gemini送信開始ログ
            #
            # 時間情報は使用しない。
            # ==================================================

            print(
                "=========================================="
            )

            print(
                "Gemini送信準備"
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
                "時間カット:",
                "なし"
            )

            print(
                "時間指定:",
                "使用しない"
            )

            print(
                "GeminiへMP3全体を送信"
            )

            print(
                "=========================================="
            )


            # ==================================================
            # Gemini
            #
            # convert.pyが作成したMP3を
            # そのままGeminiへ送信する。
            #
            # Gemini側ではカットしない。
            # ==================================================

            srt_text = transcribe_mp3(

                mp3_path

            )


            # ==================================================
            # SRT保存
            #
            # sample.mp3
            #
            # ↓
            #
            # sample.srt
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
                "Gemini文字起こし完了"
            )

            print(
                "MP3:",
                mp3_path
            )

            print(
                "SRT:",
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


        except Exception as e:

            print(
                "=========================================="
            )

            print(
                "Gemini ERROR"
            )

            print(
                "TYPE:",
                type(e).__name__
            )

            print(
                "ERROR:",
                str(e)
            )

            print(
                "REPR:",
                repr(e)
            )

            print(
                "=========================================="
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500
