import os
import uuid
import shutil
import tempfile
import subprocess

from dotenv import load_dotenv
from flask import request, jsonify
from google import genai

from paths import DOWNLOAD_DIR


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
# ==========================================================

GEMINI_MODEL = "gemini-3.5-flash"


# ==========================================================
# 時間文字列を秒へ変換
#
# 対応:
#
# 15
# 0:15
# 00:15
# 1:02:30
# 00:00:00
#
# ==========================================================

def time_to_seconds(
    time_string
):

    if time_string is None:

        return None


    time_string = str(
        time_string
    ).strip()


    if not time_string:

        return None


    try:

        parts = time_string.split(":")


        # ----------------------------------------------
        # 秒だけ
        # ----------------------------------------------

        if len(parts) == 1:

            seconds = int(
                parts[0]
            )

            if seconds < 0:

                raise ValueError

            return seconds


        # ----------------------------------------------
        # 分:秒
        # ----------------------------------------------

        if len(parts) == 2:

            minutes = int(
                parts[0]
            )

            seconds = int(
                parts[1]
            )


            if (
                minutes < 0
                or seconds < 0
                or seconds >= 60
            ):

                raise ValueError


            return (
                minutes * 60
                + seconds
            )


        # ----------------------------------------------
        # 時:分:秒
        # ----------------------------------------------

        if len(parts) == 3:

            hours = int(
                parts[0]
            )

            minutes = int(
                parts[1]
            )

            seconds = int(
                parts[2]
            )


            if (
                hours < 0
                or minutes < 0
                or seconds < 0
                or minutes >= 60
                or seconds >= 60
            ):

                raise ValueError


            return (
                hours * 3600
                + minutes * 60
                + seconds
            )


        raise ValueError(
            "時間形式が正しくありません"
        )


    except Exception as e:

        raise ValueError(

            f"時間指定が不正です: "
            f"{time_string}"

        ) from e


# ==========================================================
# 時間を正規化
#
# 重要:
#
# None
# ""
# 00:00:00
#
# はすべて「入力なし」として扱う。
# ==========================================================

def normalize_time(
    value
):

    if value is None:

        return None


    value = str(
        value
    ).strip()


    if not value:

        return None


    seconds = time_to_seconds(
        value
    )


    # ----------------------------------------------
    # 00:00:00 は入力なし
    # ----------------------------------------------

    if seconds == 0:

        return None


    return value


# ==========================================================
# 時間指定が変更されたか確認
#
# 00:00:00 と None は同じ扱い。
# ==========================================================

def is_time_changed(
    original_start_time,
    original_end_time,
    current_start_time,
    current_end_time
):

    original_start = time_to_seconds(
        normalize_time(
            original_start_time
        )
    )


    original_end = time_to_seconds(
        normalize_time(
            original_end_time
        )
    )


    current_start = time_to_seconds(
        normalize_time(
            current_start_time
        )
    )


    current_end = time_to_seconds(
        normalize_time(
            current_end_time
        )
    )


    return (

        original_start != current_start

        or

        original_end != current_end

    )


# ==========================================================
# MP3をGemini用にカット
#
# 元MP3:
#
# 日本語タイトル011112_011520.mp3
#
# ↓
#
# Gemini用:
#
# 日本語タイトル011112_011520_gemini_xxxxx.mp3
#
# 処理後にGemini用ファイルだけ削除する。
#
# 元MP3は削除しない。
# ==========================================================

def cut_mp3_for_gemini(
    mp3_path,
    start_time,
    end_time
):

    print(
        "=========================================="
    )

    print(
        "Gemini用MP3カット開始"
    )

    print(
        "元MP3:",
        mp3_path
    )

    print(
        "開始:",
        start_time
    )

    print(
        "終了:",
        end_time
    )

    print(
        "=========================================="
    )


    if not os.path.exists(
        mp3_path
    ):

        raise FileNotFoundError(

            f"MP3がありません: "
            f"{mp3_path}"

        )


    start_time = normalize_time(
        start_time
    )

    end_time = normalize_time(
        end_time
    )


    start_seconds = time_to_seconds(
        start_time
    )

    end_seconds = time_to_seconds(
        end_time
    )


    if start_seconds is None:

        raise ValueError(
            "開始時間がありません"
        )


    if end_seconds is None:

        raise ValueError(
            "終了時間がありません"
        )


    if start_seconds < 0:

        raise ValueError(
            "開始時間は0以上にしてください"
        )


    if end_seconds <= start_seconds:

        raise ValueError(
            "終了時間は開始時間より後にしてください"
        )


    # ======================================================
    # Gemini用一時カットファイル
    #
    # UUIDを使って同時処理でも衝突しないようにする。
    # ======================================================

    base_name = os.path.splitext(
        mp3_path
    )[0]


    cut_file = (

        base_name
        + "_gemini_"
        + uuid.uuid4().hex
        + ".mp3"

    )


    # ======================================================
    # ffmpeg
    #
    # 正確なカットを優先して再エンコード。
    # ======================================================

    command = [

        "ffmpeg",

        "-y",

        "-ss",
        str(start_seconds),

        "-i",
        mp3_path,

        "-t",
        str(
            end_seconds
            - start_seconds
        ),

        "-vn",

        "-codec:a",
        "libmp3lame",

        "-b:a",
        "128k",

        cut_file

    ]


    print(
        "ffmpeg command:",
        command
    )


    result = subprocess.run(

        command,

        stdout=subprocess.DEVNULL,

        stderr=subprocess.PIPE,

        text=True

    )


    if result.returncode != 0:

        print(
            result.stderr
        )


        if os.path.exists(
            cut_file
        ):

            try:

                os.remove(
                    cut_file
                )

            except Exception:

                pass


        raise Exception(
            "Gemini用MP3カット失敗"
        )


    # ======================================================
    # 完成確認
    # ======================================================

    if not os.path.exists(
        cut_file
    ):

        raise Exception(
            "Gemini用MP3が作成されませんでした"
        )


    file_size = os.path.getsize(
        cut_file
    )


    if file_size <= 0:

        raise Exception(
            "Gemini用MP3が0 bytesです"
        )


    print(
        "=========================================="
    )

    print(
        "Gemini用MP3カット完了"
    )

    print(
        "ファイル:",
        cut_file
    )

    print(
        "サイズ:",
        file_size,
        "bytes"
    )

    print(
        "=========================================="
    )


    return cut_file


# ==========================================================
# GeminiへMP3送信
#
# 重要:
#
# 日本語タイトルのMP3を直接Geminiへ渡さない。
#
# 例:
#
# 日本語タイトル011112_011520.mp3
#
# ↓ コピー
#
# /tmp/gemini_audio_UUID.mp3
#
# ↓ Gemini upload
#
# ↓ 処理終了
#
# /tmpファイル削除
#
# ==========================================================

def transcribe_mp3(
    mp3_path
):

    mp3_path = os.path.abspath(
        mp3_path
    )


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


    print(
        "=========================================="
    )

    print(
        "Gemini解析開始"
    )

    print(
        "元MP3:",
        mp3_path
    )

    print(
        "Geminiモデル:",
        GEMINI_MODEL
    )

    print(
        "=========================================="
    )


    # ======================================================
    # 日本語ファイル名対策
    #
    # UUIDを使用して完全に別名の一時ファイルを作る。
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
        # 日本語ファイル名から英数字ファイル名へコピー
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
        # Gemini Files API
        # ==================================================

        uploaded_file = client.files.upload(

            file=temp_mp3

        )


        print(
            "Gemini upload完了"
        )


        # ==================================================
        # プロンプト
        # ==================================================

        prompt = """
この音声ファイルを日本語で正確に文字起こししてください。

SRT字幕ファイルとして使用します。

以下の形式で出力してください。

1
00:00:00,000 --> 00:00:05,000
字幕文章

2
00:00:05,000 --> 00:00:10,000
字幕文章

条件:

・音声の内容を日本語で文字起こしする
・文章を省略しない
・要約しない
・可能な限り正確に聞き取る
・各字幕に時間情報を付ける
・SRT形式のみ出力する
・説明文を書かない
・Markdownのコードブロックを使用しない
・```srt を付けない
・前置きや後書きを書かない
"""


        # ==================================================
        # Gemini
        # ==================================================

        response = client.models.generate_content(

            model=GEMINI_MODEL,

            contents=[

                uploaded_file,

                prompt

            ]

        )


        if not response:

            raise Exception(
                "Geminiからレスポンスがありません"
            )


        if not response.text:

            raise Exception(
                "Gemini結果が空です"
            )


        print(
            "Gemini解析完了"
        )


        return response.text


    finally:

        # ==================================================
        # ローカルのGemini用一時MP3削除
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


    print(
        "SRT保存:",
        srt_path
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
            # paths.pyのDOWNLOAD_DIRを使用
            # ==================================================

            download_root = os.path.abspath(
                DOWNLOAD_DIR
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
            # MP3確認
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
            # 元の時間
            #
            # convert.pyから渡された時間
            # ==================================================

            original_start_time = data.get(
                "original_start_time"
            )


            original_end_time = data.get(
                "original_end_time"
            )


            # ==================================================
            # 現在の時間
            #
            # UIから渡された時間
            # ==================================================

            current_start_time = data.get(
                "start_time"
            )


            current_end_time = data.get(
                "end_time"
            )


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
                "元開始:",
                original_start_time
            )

            print(
                "元終了:",
                original_end_time
            )

            print(
                "現在開始:",
                current_start_time
            )

            print(
                "現在終了:",
                current_end_time
            )

            print(
                "=========================================="
            )


            # ==================================================
            # 時間変更判定
            #
            # 00:00:00 = 未入力
            # ==================================================

            time_changed = is_time_changed(

                original_start_time,

                original_end_time,

                current_start_time,

                current_end_time

            )


            print(
                "時間指定変更:",
                time_changed
            )


            # ==================================================
            # Geminiへ送るMP3
            #
            # 通常:
            #
            # 元MP3
            #
            # 時間変更あり:
            #
            # 一時カットMP3
            # ==================================================

            gemini_mp3_path = mp3_path

            temporary_gemini_file = None


            try:

                # ==================================================
                # 時間変更あり
                # ==================================================

                if time_changed:

                    current_start_time = normalize_time(
                        current_start_time
                    )

                    current_end_time = normalize_time(
                        current_end_time
                    )


                    # ------------------------------------------------
                    # 変更後が両方なしなら元MP3を使用
                    # ------------------------------------------------

                    if (
                        current_start_time is None
                        and current_end_time is None
                    ):

                        print(
                            "変更後の時間指定なし"
                        )

                        print(
                            "→ 元MP3をそのまま使用"
                        )


                    # ------------------------------------------------
                    # 開始だけの場合
                    # ------------------------------------------------

                    elif (
                        current_start_time is not None
                        and current_end_time is None
                    ):

                        raise ValueError(
                            "終了時間を入力してください"
                        )


                    # ------------------------------------------------
                    # 終了だけの場合
                    # ------------------------------------------------

                    elif (
                        current_start_time is None
                        and current_end_time is not None
                    ):

                        current_start_time = "00:00:00"


                        gemini_mp3_path = cut_mp3_for_gemini(

                            mp3_path,

                            current_start_time,

                            current_end_time

                        )


                        temporary_gemini_file = (
                            gemini_mp3_path
                        )


                    # ------------------------------------------------
                    # 開始・終了あり
                    # ------------------------------------------------

                    else:

                        gemini_mp3_path = cut_mp3_for_gemini(

                            mp3_path,

                            current_start_time,

                            current_end_time

                        )


                        temporary_gemini_file = (
                            gemini_mp3_path
                        )


                # ==================================================
                # 時間変更なし
                # ==================================================

                else:

                    print(
                        "時間変更なし"
                    )

                    print(
                        "→ 元MP3をそのままGeminiへ送信"
                    )


                # ==================================================
                # Gemini
                # ==================================================

                srt_text = transcribe_mp3(

                    gemini_mp3_path

                )


                # ==================================================
                # SRT
                #
                # 元MP3:
                #
                # sample.mp3
                #
                # ↓
                #
                # sample.srt
                #
                # カットMP3の場合:
                #
                # 一時ファイル名ではなく
                # 元MP3の名前でSRTを保存する。
                # ==================================================

                srt_path = save_srt(

                    mp3_path,

                    srt_text

                )


                # ==================================================
                # 完了
                # ==================================================

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

                    "time_changed":
                        time_changed,

                    "text":
                        "Gemini文字起こし完了"

                })


            finally:

                # ==================================================
                # Gemini用カットMP3削除
                #
                # 元MP3は絶対に削除しない。
                # ==================================================

                if (

                    temporary_gemini_file

                    and

                    os.path.exists(
                        temporary_gemini_file
                    )

                ):

                    try:

                        os.remove(
                            temporary_gemini_file
                        )


                        print(
                            "Gemini用カットMP3削除:",
                            temporary_gemini_file
                        )


                    except Exception as e:

                        print(

                            "WARNING: "
                            "Gemini用カットMP3削除失敗:",
                            repr(e)

                        )


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
                "=========================================="
            )


            return jsonify({

                "success":
                    False,

                "message":
                    str(e)

            }), 500
