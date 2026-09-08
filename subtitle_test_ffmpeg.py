# =====================================
# subtitle_test_ffmpeg.py
#
# FFmpeg字幕焼き込み単体テスト
#
# 固定ファイル:
#   downloads/test.mp4
#   downloads/test.srt
#
# 出力:
#   downloads/test_embed.mp4
# =====================================

from pathlib import Path
import os
import shutil
import subprocess
import tempfile

import config
import subtitle_font


# =====================================
# 設定
# =====================================

BASE_DIR = Path(config.BASE_DIR)

DOWNLOAD_DIR = Path(config.DOWNLOAD_DIR)

TEST_MP4_FILENAME = "test.mp4"

TEST_SRT_FILENAME = "test.srt"

OUTPUT_FILENAME = "test_embed.mp4"


# =====================================
# 起動ログ
# =====================================

print(
    "[SUBTITLE TEST] ==========================================",
    flush=True
)

print(
    "[SUBTITLE TEST] subtitle_test_ffmpeg.py MODULE LOAD COMPLETE",
    flush=True
)

print(
    "[SUBTITLE TEST] Current working directory:",
    Path.cwd(),
    flush=True
)

print(
    "[SUBTITLE TEST] DOWNLOAD_DIR:",
    DOWNLOAD_DIR,
    flush=True
)

print(
    "[SUBTITLE TEST] ==========================================",
    flush=True
)


# =====================================
# 入力ファイル
# =====================================

def get_test_files():

    mp4_path = (
        DOWNLOAD_DIR /
        TEST_MP4_FILENAME
    )

    srt_path = (
        DOWNLOAD_DIR /
        TEST_SRT_FILENAME
    )

    print(
        "[SUBTITLE TEST] 固定MP4:",
        mp4_path,
        flush=True
    )

    print(
        "[SUBTITLE TEST] 固定SRT:",
        srt_path,
        flush=True
    )

    return (
        mp4_path,
        srt_path
    )


# =====================================
# ファイル確認
# =====================================

def check_file(
    file_path,
    expected_extension
):

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] 入力ファイル確認開始",
        flush=True
    )

    file_path = Path(file_path)

    print(
        "[SUBTITLE TEST] file_path:",
        file_path,
        flush=True
    )

    print(
        "[SUBTITLE TEST] expected extension:",
        expected_extension,
        flush=True
    )

    try:

        resolved = file_path.resolve()

    except Exception:

        resolved = file_path

    print(
        "[SUBTITLE TEST] resolved path:",
        resolved,
        flush=True
    )

    if not resolved.exists():

        raise FileNotFoundError(
            f"ファイルが存在しません: {resolved}"
        )

    if not resolved.is_file():

        raise RuntimeError(
            f"ファイルではありません: {resolved}"
        )

    actual_extension = (
        resolved.suffix.lower()
    )

    print(
        "[SUBTITLE TEST] actual extension:",
        actual_extension,
        flush=True
    )

    if actual_extension != expected_extension:

        raise ValueError(
            f"拡張子が不正です: "
            f"{actual_extension} "
            f"(期待値: {expected_extension})"
        )

    size = resolved.stat().st_size

    print(
        "[SUBTITLE TEST] file size:",
        size,
        "bytes",
        flush=True
    )

    if size <= 0:

        raise RuntimeError(
            f"ファイルサイズが0です: {resolved}"
        )

    print(
        "[SUBTITLE TEST] 入力ファイル確認OK",
        flush=True
    )


# =====================================
# SRT UTF-8確認
# =====================================

def check_srt_utf8(
    srt_path
):

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] SRT UTF-8確認開始",
        flush=True
    )

    with open(
        srt_path,
        "r",
        encoding="utf-8"
    ) as f:

        text = f.read()

    print(
        "[SUBTITLE TEST] SRT先頭文字数:",
        len(text[:100]),
        flush=True
    )

    print(
        "[SUBTITLE TEST] SRT UTF-8確認OK",
        flush=True
    )


# =====================================
# FFmpeg確認
# =====================================

def check_ffmpeg():

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg確認開始",
        flush=True
    )

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    print(
        "[SUBTITLE TEST] shutil.which(ffmpeg):",
        ffmpeg_path,
        flush=True
    )

    if not ffmpeg_path:

        raise RuntimeError(
            "ffmpegが見つかりません。"
        )

    result = subprocess.run(
        [
            ffmpeg_path,
            "-version"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30
    )

    print(
        "[SUBTITLE TEST] FFmpeg version returncode:",
        result.returncode,
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg version:",
        result.stdout.splitlines()[0]
        if result.stdout
        else "",
        flush=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpegの起動確認に失敗しました。"
        )

    print(
        "[SUBTITLE TEST] FFmpeg確認完了",
        flush=True
    )

    return ffmpeg_path


# =====================================
# フォント検索
# =====================================

def find_font(
    requested_font
):

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] 日本語フォント検索開始",
        flush=True
    )

    print(
        "[SUBTITLE TEST] requested_font:",
        requested_font,
        flush=True
    )

    font_dirs = [

        Path(
            "/usr/share/fonts/opentype/noto"
        ),

        Path(
            "/usr/share/fonts/truetype/noto"
        ),

        Path(
            "/usr/share/fonts"
        )

    ]

    # fc-matchを優先
    fc_match = shutil.which(
        "fc-match"
    )

    if fc_match:

        try:

            result = subprocess.run(
                [
                    fc_match,
                    "-f",
                    "%{file}\n",
                    requested_font
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            path_text = (
                result.stdout.strip()
            )

            print(
                "[SUBTITLE TEST] fc-match:",
                path_text,
                flush=True
            )

            if path_text:

                path = Path(
                    path_text
                )

                if path.exists():

                    print(
                        "[SUBTITLE TEST] font path:",
                        path,
                        flush=True
                    )

                    return path

        except Exception as e:

            print(
                "[SUBTITLE TEST] fc-match ERROR:",
                repr(e),
                flush=True
            )

    # 手動検索
    for directory in font_dirs:

        if not directory.exists():

            continue

        for path in directory.rglob(
            "*.ttc"
        ):

            if (
                "NotoSansCJK" in
                path.name
            ):

                print(
                    "[SUBTITLE TEST] font path:",
                    path,
                    flush=True
                )

                return path

        for path in directory.rglob(
            "*.ttf"
        ):

            if (
                "NotoSansCJK" in
                path.name
            ):

                print(
                    "[SUBTITLE TEST] font path:",
                    path,
                    flush=True
                )

                return path

    raise RuntimeError(
        "日本語フォントが見つかりません。"
    )


# =====================================
# ASSカラー
# =====================================

def get_ass_color(
    color_name
):

    colors = {

        "白":
            "&H00FFFFFF",

        "黒":
            "&H00000000",

        "赤":
            "&H000000FF",

        "青":
            "&H00FF0000",

        "緑":
            "&H0000FF00",

        "黄":
            "&H0000FFFF"

    }

    return colors.get(
        color_name,
        "&H00FFFFFF"
    )


# =====================================
# 字幕フィルター
# =====================================

def build_video_filter(
    srt_path,
    subtitle_settings,
    font_path
):

    font_name = (
        subtitle_settings.get(
            "font",
            "Noto Sans CJK JP"
        )
    )

    text_color = (
        subtitle_settings.get(
            "text_color",
            "白"
        )
    )

    outline_color = (
        subtitle_settings.get(
            "outline_color",
            "青"
        )
    )

    outline_width = (
        subtitle_settings.get(
            "outline_width",
            5
        )
    )

    text_ass_color = get_ass_color(
        text_color
    )

    outline_ass_color = get_ass_color(
        outline_color
    )

    font_dir = font_path.parent

    # Windows等でパスに特殊文字が
    # 入っても可能な限り安全に扱う
    srt_text = str(
        srt_path
    ).replace(
        "\\",
        "/"
    )

    font_dir_text = str(
        font_dir
    ).replace(
        "\\",
        "/"
    )

    video_filter = (
        "subtitles="
        f"'{srt_text}'"
        ":fontsdir="
        f"'{font_dir_text}'"
        ":force_style="
        f"'FontName={font_name},"
        f"PrimaryColour={text_ass_color},"
        f"OutlineColour={outline_ass_color},"
        f"Outline={outline_width}'"
    )

    print(
        "[SUBTITLE TEST] 完成video_filter:",
        video_filter,
        flush=True
    )

    return video_filter


# =====================================
# FFmpeg実行
# =====================================

def run_ffmpeg(
    ffmpeg_path,
    mp4_path,
    output_path,
    video_filter
):

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpegコマンド生成",
        flush=True
    )

    command = [

        ffmpeg_path,

        "-y",

        "-nostdin",

        "-hide_banner",

        "-loglevel",
        "info",

        "-i",
        str(mp4_path),

        "-vf",
        video_filter,

        "-c:v",
        "libx264",

        "-threads",
        "1",

        "-preset",
        "ultrafast",

        "-crf",
        "23",

        "-c:a",
        "copy",

        "-movflags",
        "+faststart",

        str(output_path)

    ]

    print(
        "[SUBTITLE TEST] FFmpeg command:",
        " ".join(command),
        flush=True
    )

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg開始",
        flush=True
    )

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    print(
        "[SUBTITLE TEST] FFmpeg PID:",
        process.pid,
        flush=True
    )

    logs = []

    # ---------------------------------
    # FFmpegログをリアルタイム取得
    # ---------------------------------

    if process.stdout:

        for line in process.stdout:

            line = line.rstrip()

            if line:

                print(
                    "[FFMPEG]",
                    line,
                    flush=True
                )

                logs.append(
                    line
                )

    # ---------------------------------
    # FFmpeg終了待ち
    # ---------------------------------

    return_code = process.wait()

    print(
        "[SUBTITLE TEST] FFmpeg終了",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg returncode:",
        return_code,
        flush=True
    )

    # ---------------------------------
    # 出力確認
    # ---------------------------------

    output_path = Path(
        output_path
    )

    exists = output_path.exists()

    size = (
        output_path.stat().st_size
        if exists
        else 0
    )

    print(
        "[SUBTITLE TEST] output exists:",
        exists,
        flush=True
    )

    print(
        "[SUBTITLE TEST] output size:",
        size,
        "bytes",
        flush=True
    )

    if return_code != 0:

        error_text = "\n".join(
            logs[-100:]
        )

        raise RuntimeError(
            "FFmpeg字幕焼き込み失敗\n\n"
            f"returncode: {return_code}\n\n"
            f"FFmpeg LOG:\n{error_text}"
        )

    if not exists:

        raise RuntimeError(
            "FFmpegは終了しましたが、"
            "出力ファイルが存在しません。"
        )

    if size <= 0:

        raise RuntimeError(
            "FFmpegは終了しましたが、"
            "出力ファイルサイズが0です。"
        )

    return return_code


# =====================================
# メイン
# =====================================

def run_ffmpeg_subtitle_test():

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    print(
        "[SUBTITLE TEST] FFmpeg字幕焼き込みテスト START",
        flush=True
    )

    print(
        "[SUBTITLE TEST] ==========================================",
        flush=True
    )

    # ---------------------------------
    # STEP 1
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 1: 固定入力ファイル決定",
        flush=True
    )

    mp4_path, srt_path = get_test_files()

    # ---------------------------------
    # STEP 2
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 2: MP4確認",
        flush=True
    )

    check_file(
        mp4_path,
        ".mp4"
    )

    # ---------------------------------
    # STEP 3
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 3: SRT確認",
        flush=True
    )

    check_file(
        srt_path,
        ".srt"
    )

    # ---------------------------------
    # STEP 4
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 4: SRT UTF-8確認",
        flush=True
    )

    check_srt_utf8(
        srt_path
    )

    # ---------------------------------
    # STEP 5
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 5: subtitle_font.py設定取得",
        flush=True
    )

    settings = (
        subtitle_font
        .get_default_subtitle_font_settings()
    )

    settings = (
        subtitle_font
        .select_subtitle_font(
            settings
        )
    )

    print(
        "[SUBTITLE TEST] 最終字幕設定:",
        settings,
        flush=True
    )

    # ---------------------------------
    # STEP 6
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 6: 出力先決定",
        flush=True
    )

    output_path = (
        DOWNLOAD_DIR /
        OUTPUT_FILENAME
    )

    print(
        "[SUBTITLE TEST] 最終出力:",
        output_path,
        flush=True
    )

    # ---------------------------------
    # 既存出力削除
    # ---------------------------------

    if output_path.exists():

        print(
            "[SUBTITLE TEST] 既存出力削除:",
            output_path,
            flush=True
        )

        output_path.unlink()

    # ---------------------------------
    # STEP 7
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 7: FFmpeg確認",
        flush=True
    )

    ffmpeg_path = check_ffmpeg()

    # ---------------------------------
    # STEP 8
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 8: 日本語フォント確認",
        flush=True
    )

    font_name = settings.get(
        "font",
        "Noto Sans CJK JP"
    )

    font_path = find_font(
        font_name
    )

    # ---------------------------------
    # STEP 9
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 9: 字幕フィルター生成",
        flush=True
    )

    video_filter = build_video_filter(
        srt_path,
        settings,
        font_path
    )

    # ---------------------------------
    # STEP 10
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 10: 入力サイズ確認",
        flush=True
    )

    input_size = mp4_path.stat().st_size

    print(
        "[SUBTITLE TEST] 入力MP4サイズ:",
        input_size,
        "bytes",
        flush=True
    )

    # ---------------------------------
    # STEP 11
    # 一時ファイル
    # ---------------------------------

    print(
        "[SUBTITLE TEST] STEP 11: 一時出力パス生成",
        flush=True
    )

    temp_fd, temp_name = tempfile.mkstemp(
        prefix=".test_embed.",
        suffix=".tmp.mp4",
        dir=str(DOWNLOAD_DIR)
    )

    os.close(
        temp_fd
    )

    temp_path = Path(
        temp_name
    )

    print(
        "[SUBTITLE TEST] 一時出力パス:",
        temp_path,
        flush=True
    )

    try:

        # ---------------------------------
        # STEP 12〜14
        # FFmpeg
        # ---------------------------------

        run_ffmpeg(
            ffmpeg_path,
            mp4_path,
            temp_path,
            video_filter
        )

        # ---------------------------------
        # STEP 15
        # 完成ファイルへ移動
        # ---------------------------------

        print(
            "[SUBTITLE TEST] STEP 15: 出力ファイル確定",
            flush=True
        )

        os.replace(
            temp_path,
            output_path
        )

        # ---------------------------------
        # 最終確認
        # ---------------------------------

        final_size = (
            output_path.stat().st_size
        )

        print(
            "[SUBTITLE TEST] ==========================================",
            flush=True
        )

        print(
            "[SUBTITLE TEST] FFmpeg字幕焼き込みテスト SUCCESS",
            flush=True
        )

        print(
            "[SUBTITLE TEST] 出力:",
            output_path,
            flush=True
        )

        print(
            "[SUBTITLE TEST] 出力サイズ:",
            final_size,
            "bytes",
            flush=True
        )

        print(
            "[SUBTITLE TEST] ==========================================",
            flush=True
        )

        return {
            "success": True,
            "message": (
                "FFmpeg字幕焼き込み成功"
            ),
            "input_mp4": str(
                mp4_path
            ),
            "input_srt": str(
                srt_path
            ),
            "output_mp4": str(
                output_path
            ),
            "output_size": final_size
        }

    finally:

        # 一時ファイルが残っていたら削除
        if temp_path.exists():

            try:

                temp_path.unlink()

                print(
                    "[SUBTITLE TEST] 一時ファイル削除:",
                    temp_path,
                    flush=True
                )

            except Exception as e:

                print(
                    "[SUBTITLE TEST] 一時ファイル削除失敗:",
                    repr(e),
                    flush=True
                )


# =====================================
# 直接実行
# =====================================

if __name__ == "__main__":

    result = run_ffmpeg_subtitle_test()

    print(
        result,
        flush=True
    )
