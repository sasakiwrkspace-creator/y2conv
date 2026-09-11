# ==========================================================
# FFmpeg stderr取得
#
# FFmpeg実行中のstderrを逐次取得する。
#
# 重要:
#   - stdoutはDEVNULL
#   - stderrだけを読み取る
#   - 最後のMAX_FFMPEG_LOG_LINES行だけ保持
#   - stderr読み取り終了後にcloseする
# ==========================================================

def collect_ffmpeg_output(
    process,
    output_lines
):

    log(
        "FFmpeg stderr読み取り開始"
    )

    if process is None:

        raise RuntimeError(
            "FFmpeg processがNoneです。"
        )

    if process.stderr is None:

        raise RuntimeError(
            "FFmpeg stderrがNoneです。"
        )

    try:

        while True:

            raw_line = (
                process.stderr.readline()
            )

            if raw_line == "":

                log(
                    "FFmpeg stderr EOF"
                )

                break

            line = raw_line.rstrip()

            if not line:

                continue

            output_lines.append(
                line
            )

            print(
                "[FFMPEG]",
                line,
                flush=True
            )

            # --------------------------------------------------
            # FFmpeg終了確認
            # --------------------------------------------------

            return_code = process.poll()

            if return_code is not None:

                log(
                    "FFmpeg process終了を検知: "
                    f"return_code={return_code}"
                )

                # --------------------------------------------------
                # 終了直前に残っているstderrを読む
                # --------------------------------------------------

                while True:

                    remaining_line = (
                        process.stderr.readline()
                    )

                    if remaining_line == "":

                        break

                    remaining_line = (
                        remaining_line.rstrip()
                    )

                    if not remaining_line:

                        continue

                    output_lines.append(
                        remaining_line
                    )

                    print(
                        "[FFMPEG]",
                        remaining_line,
                        flush=True
                    )

                break

    except Exception as error:

        log_exception(
            "FFmpeg stderr読み取り中に例外",
            error
        )

        raise

    finally:

        try:

            process.stderr.close()

        except Exception as error:

            log(
                f"stderr.close()失敗: {error}"
            )

    log(
        "FFmpeg stderr読み取り終了"
    )


# ==========================================================
# FFmpegプロセス安全終了
# ==========================================================

def terminate_process_safely(
    process
):

    if process is None:

        return

    try:

        if process.poll() is None:

            log(
                "FFmpeg process terminate()"
            )

            process.terminate()

            try:

                process.wait(
                    timeout=5
                )

            except subprocess.TimeoutExpired:

                log(
                    "terminate()後も終了しないため "
                    "kill()します。"
                )

                process.kill()

                process.wait(
                    timeout=5
                )

    except Exception as error:

        log(
            f"FFmpegプロセス終了処理失敗: {error}"
        )


# ==========================================================
# 字幕フィルター作成
#
# subtitles=
#     filename=SRT:
#     fontsdir=フォントディレクトリ
#
# force_styleを使用して字幕スタイルを指定する。
# ==========================================================

def make_subtitle_filter(
    srt_path,
    font_info=None,
    subtitle_settings=None
):

    log_start(
        "字幕フィルター作成開始"
    )

    # ======================================================
    # STEP 1: 字幕設定正規化
    # ======================================================

    subtitle_settings = (
        normalize_subtitle_settings(
            subtitle_settings
        )
    )

    log(
        f"make_subtitle_filter normalized settings: "
        f"{subtitle_settings!r}"
    )

    # ======================================================
    # STEP 2: SRTパス
    # ======================================================

    subtitle_path = (
        escape_ffmpeg_filter_path(
            srt_path
        )
    )

    log(
        f"字幕SRTパス: {subtitle_path}"
    )

    # ======================================================
    # STEP 3: 設定取得
    # ======================================================

    preset_name = (
        subtitle_settings.get(
            "preset_name"
        )
    )

    font = (
        subtitle_settings.get(
            "font"
        )
    )

    text_color_name = (
        subtitle_settings.get(
            "text_color"
        )
    )

    outline_color_name = (
        subtitle_settings.get(
            "outline_color"
        )
    )

    outline_width = (
        subtitle_settings.get(
            "outline_width"
        )
    )

    log(
        f"preset_name: {preset_name!r}"
    )

    log(
        f"font: {font!r}"
    )

    log(
        f"text_color: {text_color_name!r}"
    )

    log(
        f"outline_color: {outline_color_name!r}"
    )

    log(
        f"outline_width: {outline_width!r}"
    )

    # ======================================================
    # STEP 4: 必須設定確認
    # ======================================================

    if font is None:

        raise RuntimeError(
            "字幕フォントが設定されていません。"
        )

    if text_color_name is None:

        raise RuntimeError(
            "字幕文字色が設定されていません。"
        )

    if outline_color_name is None:

        raise RuntimeError(
            "字幕縁色が設定されていません。"
        )

    # ======================================================
    # STEP 5: outline_width
    # ======================================================

    try:

        outline_width = int(
            outline_width
        )

    except (
        ValueError,
        TypeError
    ) as error:

        raise RuntimeError(
            "字幕縁太さが不正です。"
        ) from error

    if outline_width < 0:

        raise RuntimeError(
            "字幕縁太さが0未満です。"
        )

    if outline_width > 10:

        raise RuntimeError(
            "字幕縁太さが10を超えています。"
        )

    # ======================================================
    # STEP 6: ASSカラー変換
    # ======================================================

    text_color = get_ass_color(
        text_color_name
    )

    outline_color = get_ass_color(
        outline_color_name
    )

    log(
        f"text_color ASS: {text_color}"
    )

    log(
        f"outline_color ASS: {outline_color}"
    )

    # ======================================================
    # STEP 7: FontName決定
    # ======================================================

    font_name = None

    if font_info:

        detected_family = (
            font_info.get(
                "family"
            )
        )

        if detected_family:

            detected_family = str(
                detected_family
            ).strip()

            if detected_family:

                font_name = (
                    detected_family
                )

    if not font_name:

        font_name = str(
            font
        ).strip()

    if not font_name:

        raise RuntimeError(
            "字幕フォント名を決定できませんでした。"
        )

    log(
        f"最終FontName: {font_name}"
    )

    # ======================================================
    # STEP 8: subtitles filter本体
    # ======================================================

    video_filter = (
        "subtitles='"
        +
        subtitle_path
        +
        "'"
    )

    # ======================================================
    # STEP 9: fontsdir
    # ======================================================

    if font_info:

        font_path = font_info.get(
            "path"
        )

        if font_path:

            font_path = Path(
                font_path
            ).resolve()

            log(
                f"font_info.path: {font_path}"
            )

            log(
                f"font_info.path exists: "
                f"{font_path.exists()}"
            )

            log(
                f"font_info.path is_file: "
                f"{font_path.is_file()}"
            )

            if font_path.is_file():

                font_directory = (
                    font_path.parent
                )

                font_directory_escaped = (
                    escape_ffmpeg_filter_path(
                        font_directory
                    )
                )

                video_filter += (
                    ":fontsdir='"
                    +
                    font_directory_escaped
                    +
                    "'"
                )

                log(
                    f"字幕フォントディレクトリ: "
                    f"{font_directory}"
                )

    # ======================================================
    # STEP 10: ASS style
    # ======================================================

    style_parts = [

        "FontName="
        +
        escape_ffmpeg_value(
            font_name
        ),

        "PrimaryColour="
        +
        text_color,

        "OutlineColour="
        +
        outline_color,

        "Outline="
        +
        str(
            outline_width
        ),

    ]

    force_style = ",".join(
        style_parts
    )

    log(
        f"force_style: {force_style}"
    )

    # ======================================================
    # STEP 11: force_styleを必ず追加
    # ======================================================

    video_filter += (
        ":force_style='"
        +
        force_style
        +
        "'"
    )

    # ======================================================
    # STEP 12: 最終診断
    # ======================================================

    log(
        "------------------------------------------"
    )

    log(
        "字幕フィルター最終確認"
    )

    log(
        f"preset_name: {preset_name!r}"
    )

    log(
        f"font: {font_name!r}"
    )

    log(
        f"text_color: {text_color_name!r}"
    )

    log(
        f"text_color ASS: {text_color}"
    )

    log(
        f"outline_color: {outline_color_name!r}"
    )

    log(
        f"outline_color ASS: {outline_color}"
    )

    log(
        f"outline_width: {outline_width}"
    )

    log(
        f"完成video_filter: {video_filter}"
    )

    log(
        "字幕フィルター作成完了"
    )

    log(
        "------------------------------------------"
    )

    return video_filter


# ==========================================================
# FFmpeg実行直前パラメータ診断
# ==========================================================

def log_ffmpeg_parameters(
    command,
    video_filter,
    mp4_path,
    srt_path,
    output_path,
    temp_output_path,
    font_info,
    subtitle_settings
):
    """
    FFmpeg subprocess.Popen()直前に、
    実際に渡すパラメータをRenderログへ詳細表示する。
    """

    log_separator()

    log(
        "######## FFmpeg実行直前パラメータ診断 ########"
    )

    # ======================================================
    # 基本情報
    # ======================================================

    log(
        "----- BASIC PARAMETERS -----"
    )

    log(
        f"mp4_path       = {str(mp4_path)!r}"
    )

    log(
        f"srt_path       = {str(srt_path)!r}"
    )

    log(
        f"output_path    = {str(output_path)!r}"
    )

    log(
        f"temp_output    = {str(temp_output_path)!r}"
    )

    # ======================================================
    # フォント情報
    # ======================================================

    log(
        "----- FONT INFORMATION -----"
    )

    if font_info is None:

        log(
            "font_info = None"
        )

    else:

        log(
            f"font_info type = {type(font_info).__name__}"
        )

        log(
            f"font_info raw = {font_info!r}"
        )

        font_path = font_info.get(
            "path"
        )

        font_family = font_info.get(
            "family"
        )

        log(
            f"font_info.path   = {font_path!r}"
        )

        log(
            f"font_info.family = {font_family!r}"
        )

        if font_path:

            try:

                font_path_obj = Path(
                    font_path
                ).resolve()

                log(
                    f"font_path resolved = "
                    f"{font_path_obj!s}"
                )

                log(
                    f"font_path exists = "
                    f"{font_path_obj.exists()}"
                )

                log(
                    f"font_path is_file = "
                    f"{font_path_obj.is_file()}"
                )

                log(
                    f"font_path parent = "
                    f"{font_path_obj.parent!s}"
                )

                log(
                    f"font_path parent exists = "
                    f"{font_path_obj.parent.exists()}"
                )

            except Exception as error:

                log(
                    f"font_path確認失敗: {error}"
                )

    # ======================================================
    # subtitle_settings
    # ======================================================

    log(
        "----- SUBTITLE SETTINGS -----"
    )

    if subtitle_settings is None:

        log(
            "subtitle_settings = None"
        )

    else:

        log(
            f"subtitle_settings type = "
            f"{type(subtitle_settings).__name__}"
        )

        for key in SUBTITLE_SETTING_KEYS:

            value = subtitle_settings.get(
                key
            )

            log(
                f"subtitle_settings[{key!r}] = "
                f"{value!r}"
            )

    # ======================================================
    # video_filter
    # ======================================================

    log(
        "----- VIDEO FILTER -----"
    )

    log(
        f"video_filter type = "
        f"{type(video_filter).__name__}"
    )

    log(
        f"video_filter length = "
        f"{len(video_filter)}"
    )

    log(
        f"video_filter repr = "
        f"{video_filter!r}"
    )

    log(
        "video_filter raw:"
    )

    log(
        video_filter
    )

    # ======================================================
    # fontsdir診断
    # ======================================================

    log(
        "----- FONTDIR DIAGNOSTIC -----"
    )

    fontsdir_marker = ":fontsdir='"

    if fontsdir_marker in video_filter:

        fontsdir_start = (
            video_filter.find(
                fontsdir_marker
            )
            +
            len(fontsdir_marker)
        )

        fontsdir_end = (
            video_filter.find(
                "'",
                fontsdir_start
            )
        )

        if fontsdir_end >= 0:

            fontsdir_value = (
                video_filter[
                    fontsdir_start:
                    fontsdir_end
                ]
            )

            log(
                f"fontsdir extracted = "
                f"{fontsdir_value!r}"
            )

            log(
                f"fontsdir length = "
                f"{len(fontsdir_value)}"
            )

        else:

            log(
                "WARNING: fontsdirの終了'が"
                "見つかりません。"
            )

    else:

        log(
            "fontsdirはvideo_filterに"
            "含まれていません。"
        )

    # ======================================================
    # FFmpeg command
    # ======================================================

    log(
        "----- FFMPEG COMMAND -----"
    )

    log(
        f"command type = "
        f"{type(command).__name__}"
    )

    log(
        f"command length = "
        f"{len(command)}"
    )

    for index, item in enumerate(command):

        log(
            f"command[{index}] = {item!r}"
        )

    log(
        "----- FFMPEG COMMAND STRING -----"
    )

    log(
        command_to_string(
            command
        )
    )

    # ======================================================
    # subprocessに渡す値の型確認
    # ======================================================

    log(
        "----- COMMAND TYPE CHECK -----"
    )

    for index, item in enumerate(command):

        log(
            f"command[{index}] "
            f"type={type(item).__name__} "
            f"value={item!r}"
        )

    # ======================================================
    # 重要な引数を個別表示
    # ======================================================

    log(
        "----- IMPORTANT ARGUMENTS -----"
    )

    try:

        vf_index = command.index(
            "-vf"
        )

        vf_value = command[
            vf_index + 1
        ]

        log(
            f"-vf value = {vf_value!r}"
        )

    except (
        ValueError,
        IndexError
    ):

        log(
            "WARNING: -vf引数を取得できません。"
        )

    try:

        input_index = command.index(
            "-i"
        )

        input_value = command[
            input_index + 1
        ]

        log(
            f"-i value = {input_value!r}"
        )

    except (
        ValueError,
        IndexError
    ):

        log(
            "WARNING: -i引数を取得できません。"
        )

    # ======================================================
    # 最終診断
    # ======================================================

    log(
        "######## FFmpeg実行直前パラメータ診断 END ########"
    )

    log_separator()


# ==========================================================
# FFmpegコマンド表示
# ==========================================================

def command_to_string(
    command
):

    return " ".join(
        str(item)
        for item in command
    )


# ==========================================================
# FFmpegログ整形
# ==========================================================

def make_ffmpeg_error_detail(
    lines
):

    if not lines:

        return (
            "FFmpegからエラー内容が"
            "返されませんでした。"
        )

    return "\n".join(
        lines
    )


# ==========================================================
# 一時ファイル削除
# ==========================================================

def remove_file_safely(
    file_path
):

    if not file_path:

        return

    try:

        path = Path(
            file_path
        )

    except Exception:

        return

    try:

        if path.exists():

            path.unlink()

            log(
                f"ファイル削除: {path}"
            )

    except Exception as error:

        log(
            f"ファイル削除失敗: {error}"
        )


# ==========================================================
# 字幕焼き込み本体
# ==========================================================

def embed_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    start_time = time.monotonic()

    log_start(
        "embed_subtitle() START"
    )

    process = None

    temp_output_path = None

    ffmpeg_output_lines = deque(
        maxlen=MAX_FFMPEG_LOG_LINES
    )

    try:

        # ==================================================
        # STEP 1
        # ==================================================

        log_start(
            "STEP 1: MP4入力確認"
        )

        mp4_path = validate_input_file(
            mp4_path,
            ".mp4"
        )

        log(
            f"MP4確認完了: {mp4_path}"
        )

        # ==================================================
        # STEP 2
        # ==================================================

        log_start(
            "STEP 2: SRT入力確認"
        )

        srt_path = validate_input_file(
            srt_path,
            ".srt"
        )

        log(
            f"SRT確認完了: {srt_path}"
        )

        # ==================================================
        # STEP 3
        # ==================================================

        log_start(
            "STEP 3: SRT UTF-8確認"
        )

        validate_srt_encoding(
            srt_path
        )

        log(
            "SRT UTF-8確認完了"
        )

        # ==================================================
        # STEP 4
        # ==================================================

        log_start(
            "STEP 4: 字幕設定正規化"
        )

        subtitle_settings = (
            normalize_subtitle_settings(
                subtitle_settings
            )
        )

        log(
            f"normalized subtitle settings: "
            f"{subtitle_settings!r}"
        )

        # ==================================================
        # STEP 5
        # ==================================================

        log_start(
            "STEP 5: 出力先決定"
        )

        if output_path:

            output_path = (
                Path(
                    output_path
                )
                .expanduser()
                .resolve()
            )

        else:

            output_path = (
                make_output_path(
                    mp4_path
                )
                .resolve()
            )

        log(
            f"最終output_path: {output_path}"
        )

        # ==================================================
        # 入力と出力が同じにならないようにする
        # ==================================================

        if output_path == mp4_path:

            log(
                "WARNING: 入力と出力が同じです。"
            )

            output_path = (
                make_output_path(
                    mp4_path
                )
                .resolve()
            )

            log(
                f"変更後output_path: {output_path}"
            )

        # ==================================================
        # STEP 6
        # ==================================================

        log_start(
            "STEP 6: 出力フォルダ確認"
        )

        try:

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

        except OSError as error:

            log_exception(
                "出力フォルダ作成失敗",
                error
            )

            raise RuntimeError(
                "出力フォルダを作成できません: "
                +
                str(error)
            ) from error

        log(
            "出力フォルダ確認完了"
        )

        # ==================================================
        # STEP 7
        # ==================================================

        log_start(
            "STEP 7: FFmpeg確認"
        )

        ffmpeg_path = check_ffmpeg()

        log(
            f"使用FFmpeg: {ffmpeg_path}"
        )

        # ==================================================
        # STEP 8
        # ==================================================

        log_start(
            "STEP 8: フォント確認"
        )

        font = (
            subtitle_settings.get(
                "font"
            )
        )

        log(
            f"選択フォント: {font}"
        )

        font_info = find_japanese_font(
            font
        )

        if font_info:

            log(
                "日本語字幕フォント:"
            )

            log(
                f"path: {font_info.get('path')}"
            )

            log(
                f"family: {font_info.get('family')}"
            )

        else:

            raise RuntimeError(
                "日本語字幕フォントが見つかりません。"
                "Render環境に日本語フォントを"
                "インストールしてください。"
            )

        # ==================================================
        # STEP 9
        # ==================================================

        log_start(
            "STEP 9: 字幕フィルター生成"
        )

        video_filter = make_subtitle_filter(

            srt_path,

            font_info,

            subtitle_settings

        )

        log(
            "STEP 9完了: 字幕フィルター生成OK"
        )

        # ==================================================
        # STEP 10
        # ==================================================

        log_start(
            "STEP 10: 入力MP4サイズ確認"
        )

        try:

            input_mp4_size = (
                mp4_path.stat().st_size
            )

        except OSError as error:

            log_exception(
                "入力MP4サイズ取得失敗",
                error
            )

            input_mp4_size = 0

        log(
            f"入力MP4サイズ: {input_mp4_size} bytes"
        )

        # ==================================================
        # STEP 11
        # ==================================================

        log_start(
            "STEP 11: 一時出力パス生成"
        )

        temp_output_path = (
            make_temp_output_path(
                output_path
            )
        )

        log(
            f"一時出力: {temp_output_path}"
        )

        # ==================================================
        # FFmpeg開始情報
        # ==================================================

        log_separator()

        log(
            "字幕焼き込み開始"
        )

        log(
            f"MP4: {mp4_path}"
        )

        log(
            f"SRT: {srt_path}"
        )

        log(
            f"出力: {output_path}"
        )

        log(
            f"一時出力: {temp_output_path}"
        )

        log(
            f"入力MP4サイズ: "
            f"{input_mp4_size} bytes"
        )

        log(
            f"FFmpeg threads: "
            f"{FFMPEG_THREADS}"
        )

        log(
            f"FFmpeg preset: "
            f"{FFMPEG_PRESET}"
        )

        log(
            f"FFmpeg CRF: "
            f"{FFMPEG_CRF}"
        )

        # ==================================================
        # STEP 12
        # ==================================================

        log_start(
            "STEP 12: FFmpegコマンド生成"
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
            FFMPEG_THREADS,

            "-preset",
            FFMPEG_PRESET,

            "-crf",
            FFMPEG_CRF,

            "-c:a",
            "copy",

            "-movflags",
            "+faststart",

            str(
                temp_output_path
            )

        ]

        log(
            f"FFmpeg command item count: "
            f"{len(command)}"
        )

        log(
            "FFmpeg video filter:"
        )

        log(
            video_filter
        )

        log(
            "FFmpeg command:"
        )

        log(
            command_to_string(
                command
            )
        )

        # ==================================================
        # STEP 13
        # ==================================================

        log_start(
            "STEP 13: FFmpeg subprocess.Popen開始"
        )

        try:

            process = subprocess.Popen(

                command,

                stdout=subprocess.DEVNULL,

                stderr=subprocess.PIPE,

                stdin=subprocess.DEVNULL,

                text=True,

                encoding="utf-8",

                errors="replace",

                bufsize=1

            )

        except OSError as error:

            log_exception(
                "FFmpeg subprocess.Popenに失敗しました。",
                error
            )

            raise RuntimeError(
                "FFmpeg実行中にエラーが発生しました: "
                +
                str(error)
            ) from error

        log(
            f"FFmpeg process started: PID={process.pid}"
        )

        # ==================================================
        # STEP 14
        # ==================================================

        log_start(
            "STEP 14: FFmpeg stderrログ取得開始"
        )

        collect_ffmpeg_output(
            process,
            ffmpeg_output_lines
        )

        log(
            "STEP 14完了: FFmpeg stderrログ取得終了"
        )

        log(
            f"保持しているFFmpegログ行数: "
            f"{len(ffmpeg_output_lines)}"
        )

        # ==================================================
        # STEP 15
        # ==================================================

        log_start(
            "STEP 15: FFmpeg終了状態確認"
        )

        return_code = process.wait()

        log(
            f"FFmpeg return code: {return_code}"
        )

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log(
            f"現在までの処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        # ==================================================
        # STEP 16
        # ==================================================

        if return_code != 0:

            log_start(
                "STEP 16: FFmpeg異常終了"
            )

            error_detail = (
                make_ffmpeg_error_detail(
                    ffmpeg_output_lines
                )
            )

            log(
                "FFmpeg最後のログ:"
            )

            log(
                error_detail
            )

            raise RuntimeError(

                "字幕焼き込みに失敗しました。"
                "\n\n"
                +
                error_detail
                +
                "\n\n"
                +
                "FFmpeg return code: "
                +
                str(return_code)
                +
                "\n"
                +
                "処理時間: "
                +
                format_elapsed_time(
                    elapsed_time
                )

            )

        log(
            "STEP 16完了: FFmpeg正常終了"
        )

        # ==================================================
        # STEP 17
        # ==================================================

        log_start(
            "STEP 17: 一時出力ファイル確認"
        )

        if not temp_output_path.exists():

            raise RuntimeError(

                "FFmpegは正常終了しましたが、"
                "一時出力ファイルが作成されていません。"

            )

        if not temp_output_path.is_file():

            raise RuntimeError(

                "FFmpegの一時出力先が"
                "ファイルではありません。"

            )

        try:

            output_size = (
                temp_output_path.stat().st_size
            )

        except OSError as error:

            raise RuntimeError(

                "一時出力ファイルを"
                "確認できませんでした: "
                +
                str(error)

            ) from error

        log(
            f"一時出力ファイルサイズ: "
            f"{output_size} bytes"
        )

        if output_size <= 0:

            raise RuntimeError(
                "FFmpeg出力ファイルのサイズが0です。"
            )

        log(
            "一時出力ファイル確認OK"
        )

        # ==================================================
        # STEP 18
        # ==================================================

        log_start(
            "STEP 18: 正式出力ファイル確認"
        )

        if output_path.exists():

            log(
                "既存の正式出力があります。"
            )

            try:

                if output_path.is_file():

                    output_path.unlink()

                else:

                    raise RuntimeError(
                        "既存の正式出力パスが"
                        "通常ファイルではありません。"
                    )

            except OSError as error:

                raise RuntimeError(

                    "既存の出力ファイルを"
                    "削除できませんでした: "
                    +
                    str(error)

                ) from error

            log(
                "既存の正式出力削除完了"
            )

        else:

            log(
                "既存の正式出力はありません"
            )

        # ==================================================
        # STEP 19
        # ==================================================

        log_start(
            "STEP 19: 一時ファイルを正式出力へ移動"
        )

        try:

            os.replace(

                str(
                    temp_output_path
                ),

                str(
                    output_path
                )

            )

        except OSError as error:

            raise RuntimeError(

                "字幕MP4を正式出力へ"
                "移動できませんでした: "
                +
                str(error)

            ) from error

        log(
            "os.replace()成功"
        )

        # ==================================================
        # STEP 20
        # ==================================================

        log_start(
            "STEP 20: 最終出力ファイル確認"
        )

        if not output_path.exists():

            raise RuntimeError(

                "正式な字幕MP4が"
                "作成されていません。"

            )

        if not output_path.is_file():

            raise RuntimeError(

                "正式出力先がファイルではありません。"

            )

        try:

            final_size = (
                output_path.stat().st_size
            )

        except OSError as error:

            raise RuntimeError(

                "正式出力ファイルを"
                "確認できませんでした: "
                +
                str(error)

            ) from error

        log(
            f"正式出力ファイルサイズ: "
            f"{final_size} bytes"
        )

        if final_size <= 0:

            remove_file_safely(
                output_path
            )

            raise RuntimeError(
                "正式出力ファイルのサイズが0です。"
            )

        # ==================================================
        # STEP 21
        # ==================================================

        log_start(
            "STEP 21: 一時ファイル残存確認"
        )

        if temp_output_path.exists():

            remove_file_safely(
                temp_output_path
            )

        else:

            log(
                "一時ファイルは残っていません"
            )

        # ==================================================
        # 完了
        # ==================================================

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log_start(
            "字幕焼き込み最終完了"
        )

        log(
            f"入力MP4: {mp4_path}"
        )

        log(
            f"入力SRT: {srt_path}"
        )

        log(
            f"出力ファイル: {output_path}"
        )

        log(
            f"サイズ: {final_size} bytes"
        )

        log(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        log(
            "embed_subtitle正常終了"
        )

        return output_path

    except Exception as error:

        # ==================================================
        # エラー時FFmpeg停止
        # ==================================================

        if process is not None:

            terminate_process_safely(
                process
            )

        # ==================================================
        # エラー時一時ファイル削除
        # ==================================================

        remove_file_safely(
            temp_output_path
        )

        log_exception(
            "embed_subtitle()で例外が発生しました。",
            error
        )

        raise


# ==========================================================
# 外部向け正式関数
# ==========================================================

def create_subtitle_mp4(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    log(
        "create_subtitle_mp4開始"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )

    log(
        f"create_subtitle_mp4完了: {result}"
    )

    return result


# ==========================================================
# 互換用別名
# ==========================================================

def create_burned_subtitle(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    log(
        "create_burned_subtitle開始"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )

    log(
        f"create_burned_subtitle完了: {result}"
    )

    return result


def burn_subtitles(
    mp4_path,
    srt_path,
    output_path=None,
    subtitle_settings=None
):

    log(
        "burn_subtitles開始"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        output_path,

        subtitle_settings

    )

    log(
        f"burn_subtitles完了: {result}"
    )

    return result


# ==========================================================
# downloads内から実行
# ==========================================================

def embed_from_downloads(
    mp4_filename,
    srt_filename,
    subtitle_settings=None
):

    log_separator()

    log(
        "embed_from_downloads開始"
    )

    log(
        f"mp4_filename input: {mp4_filename!r}"
    )

    log(
        f"srt_filename input: {srt_filename!r}"
    )

    # ======================================================
    # ファイル名だけを許可
    # ======================================================

    mp4_filename = Path(
        mp4_filename
    ).name

    srt_filename = Path(
        srt_filename
    ).name

    log(
        f"安全化後mp4_filename: {mp4_filename}"
    )

    log(
        f"安全化後srt_filename: {srt_filename}"
    )

    # ======================================================
    # DOWNLOADS_DIR確認
    # ======================================================

    try:

        DOWNLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    except OSError as error:

        log_exception(
            "DOWNLOADS_DIR作成に失敗しました。",
            error
        )

        raise

    mp4_path = (
        DOWNLOADS_DIR
        /
        mp4_filename
    )

    srt_path = (
        DOWNLOADS_DIR
        /
        srt_filename
    )

    log(
        f"downloads MP4: {mp4_path}"
    )

    log(
        f"downloads SRT: {srt_path}"
    )

    result = embed_subtitle(

        mp4_path,

        srt_path,

        subtitle_settings=subtitle_settings

    )

    log(
        f"embed_from_downloads完了: {result}"
    )

    log_separator()

    return result


# ==========================================================
# コマンドライン
# ==========================================================

def main():

    log(
        "##################################################"
    )

    log(
        "subtitle.py main()開始"
    )

    log(
        f"sys.argv: {sys.argv!r}"
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

    except Exception:

        pass

    log(
        f"DOWNLOAD_DIR config: {DOWNLOAD_DIR!r}"
    )

    log(
        f"DOWNLOADS_DIR: {DOWNLOADS_DIR}"
    )

    log(
        f"Environment SUBTITLE_FONT: "
        f"{os.environ.get('SUBTITLE_FONT')!r}"
    )

    if len(sys.argv) < 3:

        print()

        print(
            "使用方法:"
        )

        print(
            "python subtitle.py "
            "動画.mp4 字幕.srt"
        )

        print()

        return 1

    mp4_filename = (
        sys.argv[1]
    )

    srt_filename = (
        sys.argv[2]
    )

    log(
        f"CLI MP4: {mp4_filename!r}"
    )

    log(
        f"CLI SRT: {srt_filename!r}"
    )

    start_time = time.monotonic()

    try:

        # ==================================================
        # subtitle_font.pyから標準設定取得
        # ==================================================

        log(
            "STEP MAIN-1: "
            "subtitle_font.pyから標準設定取得開始"
        )

        subtitle_settings = (
            get_default_subtitle_font_settings()
        )

        if not isinstance(
            subtitle_settings,
            dict
        ):

            raise RuntimeError(
                "subtitle_font.pyの標準設定が"
                "dictではありません。"
            )

        log(
            "標準設定取得完了"
        )

        log(
            f"subtitle_settings: "
            f"{subtitle_settings!r}"
        )

        # ==================================================
        # 字幕焼き込み
        # ==================================================

        log(
            "STEP MAIN-2: embed_from_downloads開始"
        )

        output_path = (
            embed_from_downloads(

                mp4_filename,

                srt_filename,

                subtitle_settings

            )
        )

        log(
            "STEP MAIN-2完了"
        )

        log(
            f"output_path returned: {output_path}"
        )

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        print()

        print(
            "====================================="
        )

        print(
            "字幕焼き込み成功"
        )

        print(
            "====================================="
        )

        print(
            f"入力MP4: "
            f"{mp4_filename}"
        )

        print(
            f"入力SRT: "
            f"{srt_filename}"
        )

        print(
            f"preset_name: "
            f"{subtitle_settings.get('preset_name')}"
        )

        print(
            f"font: "
            f"{subtitle_settings.get('font')}"
        )

        print(
            f"text_color: "
            f"{subtitle_settings.get('text_color')}"
        )

        print(
            f"outline_color: "
            f"{subtitle_settings.get('outline_color')}"
        )

        print(
            f"outline_width: "
            f"{subtitle_settings.get('outline_width')}"
        )

        print(
            f"出力: "
            f"{output_path.name}"
        )

        print(
            f"出力パス: "
            f"{output_path}"
        )

        print(
            f"処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        print(
            "====================================="
        )

        print()

        log(
            "subtitle.py main()正常終了"
        )

        log(
            "##################################################"
        )

        return 0

    except Exception as error:

        elapsed_time = (
            time.monotonic()
            -
            start_time
        )

        log_exception(
            "main()で例外が発生しました。",
            error
        )

        log(
            f"例外発生時の処理時間: "
            f"{format_elapsed_time(elapsed_time)}"
        )

        print()

        print(
            "====================================="
        )

        print(
            "字幕焼き込み失敗"
        )

        print(
            "====================================="
        )

        print(
            str(error),
            file=sys.stderr
        )

        print(
            "処理時間: "
            +
            format_elapsed_time(
                elapsed_time
            ),
            file=sys.stderr
        )

        print(
            "====================================="
        )

        print()

        log(
            "subtitle.py main()異常終了"
        )

        log(
            "##################################################"
        )

        return 1


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    log(
        "=================================================="
    )

    log(
        "__main__実行開始"
    )

    log(
        f"PID: {os.getpid()}"
    )

    log(
        f"argv: {sys.argv!r}"
    )

    log(
        "=================================================="
    )

    exit_code = main()

    log(
        f"main() returned exit_code={exit_code}"
    )

    log(
        "__main__終了"
    )

    sys.exit(
        exit_code
    )
