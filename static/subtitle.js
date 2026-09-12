// =====================================
// YouTube Converter - Subtitle
// subtitle.js
//
// タブ2専用
//
// 重要:
// ・converterUtils.js は使用しない
// ・converter.js には触れない
// ・converterStatus.js には触れない
// ・#convertBtnには触れない
// ・タブ1のイベントを登録しない
// ・タブ1のDOMを操作しない
// ・/subtitle-* APIのみ使用
//
// フォント設定:
// ・フォントUIは subtitle_font.js が担当
// ・subtitle.js はフォントUIを直接操作しない
// ・subtitle_font.js から現在の設定を取得
// ・subtitle.js はFFmpegへ渡す設定だけを保持
// ・画面下にフォント設定を表示しない
//
// MP4 / SRT:
// ・ファイル選択と転送を分離
// ・MP4転送ボタンで /subtitle-upload-mp4
// ・SRT転送ボタンで /subtitle-upload-srt
// ・字幕mp4作成では転送済みファイルを使用
// ・新しいファイルを選択したら、古い転送済みファイルを無効化
// =====================================

(function () {

    "use strict";

    console.log(
        "[SUBTITLE] subtitle.js loaded"
    );


    // =====================================
    // 初期化
    // =====================================

    function initializeSubtitle() {

        console.log(
            "[SUBTITLE] initializeSubtitle() start"
        );


        // ---------------------------------
        // 二重初期化防止
        // ---------------------------------

        if (
            window.subtitleMain &&
            window.subtitleMain.__initialized
        ) {

            console.log(
                "[SUBTITLE] already initialized"
            );

            return;

        }


        // =================================
        // DOM
        // =================================

        const mp3Input =
            document.getElementById(
                "subtitle-mp3-input"
            );

        const mp3SelectButton =
            document.getElementById(
                "subtitle-mp3-select"
            );

        const geminiButton =
            document.getElementById(
                "gemini-send-button"
            );

        const mp4Input =
            document.getElementById(
                "subtitle-mp4-input"
            );

        const mp4SelectButton =
            document.getElementById(
                "subtitle-mp4-select"
            );

        const srtInput =
            document.getElementById(
                "subtitle-srt-input"
            );

        const srtSelectButton =
            document.getElementById(
                "subtitle-srt-select"
            );

        const subtitleMp4Button =
            document.getElementById(
                "subtitle-mp4-create-button"
            );

        const conversionStatusArea =
            document.getElementById(
                "conversion-status-area"
            );

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );


        // =================================
        // 転送ボタン
        // =================================

        const mp4UploadButton =
            document.getElementById(
                "subtitle-mp4-upload-button"
            );

        const srtUploadButton =
            document.getElementById(
                "subtitle-srt-upload-button"
            );


        // =================================
        // 必須DOM確認
        // =================================

        if (
            !mp3Input ||
            !mp3SelectButton ||
            !geminiButton ||
            !mp4Input ||
            !mp4SelectButton ||
            !srtInput ||
            !srtSelectButton ||
            !subtitleMp4Button
        ) {

            console.error(
                "[SUBTITLE] 必須DOMが見つかりません"
            );

            return;

        }


        // =================================
        // メインオブジェクト
        // =================================

        const mainObject = {

            __initialized:
                true

        };


        window.subtitleMain =
            mainObject;


        // =====================================
        // State
        // =====================================

        const subtitleState = {

            mp3File:
                null,

            mp3Filename:
                "",

            mp4File:
                null,

            mp4Filename:
                "",

            srtFile:
                null,

            srtFilename:
                "",

            uploadedMp4Filename:
                "",

            uploadedSrtFilename:
                "",

            generatedSrtFilename:
                "",

            generatedSubtitleMp4Filename:
                "",

            isProcessing:
                false

        };


        window.subtitleState =
            subtitleState;


        // =====================================
        // ファイル表示
        // =====================================

        function updateFileDisplay(
            button,
            file,
            emptyText
        ) {

            if (!button) {

                return;

            }


            if (file) {

                button.textContent =
                    file.name;

                button.title =
                    file.name;

            }
            else {

                button.textContent =
                    emptyText ||
                    "ファイルが選択されていません";

                button.title =
                    "";

            }

        }


        // =====================================
        // フォント設定取得
        // =====================================

        function getFontSettings() {

            if (
                window.subtitleFont &&
                typeof window.subtitleFont.getSettings ===
                    "function"
            ) {

                const settings =
                    window.subtitleFont.getSettings();


                if (
                    settings &&
                    typeof settings === "object"
                ) {

                    const outlineWidth =
                        Number(
                            settings.outline_width
                        );


                    const resolvedPresetName =
                        settings.preset_name ||
                        "標準";


                    const resolvedFont =
                        settings.font ||
                        "Noto Sans CJK JP";


                    const resolvedTextColor =
                        settings.text_color ||
                        "白";


                    const resolvedTextColorHex =
                        settings.text_color_hex ||
                        "#FFFFFF";


                    const resolvedOutlineColor =
                        settings.outline_color ||
                        "黒";


                    const resolvedOutlineColorHex =
                        settings.outline_color_hex ||
                        "#000000";


                    const resolvedOutlineWidth =
                        Number.isFinite(
                            outlineWidth
                        )
                            ? outlineWidth
                            : 2;


                    console.log(
                        "[SUBTITLE] font settings:",
                        {
                            preset_name:
                                resolvedPresetName,

                            font:
                                resolvedFont,

                            text_color:
                                resolvedTextColor,

                            text_color_hex:
                                resolvedTextColorHex,

                            outline_color:
                                resolvedOutlineColor,

                            outline_color_hex:
                                resolvedOutlineColorHex,

                            outline_width:
                                resolvedOutlineWidth
                        }
                    );


                    return {

                        preset_name:
                            resolvedPresetName,

                        font:
                            resolvedFont,

                        text_color:
                            resolvedTextColor,

                        text_color_hex:
                            resolvedTextColorHex,

                        outline_color:
                            resolvedOutlineColor,

                        outline_color_hex:
                            resolvedOutlineColorHex,

                        outline_width:
                            resolvedOutlineWidth

                    };

                }

            }


            return {

                preset_name:
                    "標準",

                font:
                    "Noto Sans CJK JP",

                text_color:
                    "白",

                text_color_hex:
                    "#FFFFFF",

                outline_color:
                    "黒",

                outline_color_hex:
                    "#000000",

                outline_width:
                    2

            };

        }


        // =====================================
        // 後方互換
        // =====================================

        function getFontPreset() {

            const settings =
                getFontSettings();


            return settings.preset_name;

        }


        // =====================================
        // フォントUI無効化
        // =====================================

        function setFontDisabled(
            disabled
        ) {

            if (
                window.subtitleFont &&
                typeof window.subtitleFont.setDisabled ===
                    "function"
            ) {

                window.subtitleFont.setDisabled(
                    disabled
                );

            }

        }


        // =====================================
        // タイマー
        // =====================================

        let elapsedTimerId =
            null;


        let processingStartTime =
            null;


        function formatElapsed(
            seconds
        ) {

            const total =
                Math.max(
                    0,
                    Math.floor(
                        Number(seconds) || 0
                    )
                );


            const hours =
                Math.floor(
                    total / 3600
                );


            const minutes =
                Math.floor(
                    (total % 3600) / 60
                );


            const secs =
                total % 60;


            if (hours > 0) {

                return (
                    hours +
                    "時間 " +
                    minutes +
                    "分 " +
                    secs +
                    "秒"
                );

            }


            if (minutes > 0) {

                return (
                    minutes +
                    "分 " +
                    secs +
                    "秒"
                );

            }


            return secs + "秒";

        }


        function stopElapsedTimer() {

            if (
                elapsedTimerId !== null
            ) {

                clearTimeout(
                    elapsedTimerId
                );


                elapsedTimerId =
                    null;

            }

        }


        function startProcessing() {

            processingStartTime =
                Date.now();


            stopElapsedTimer();

        }


        function getElapsedSeconds() {

            if (
                processingStartTime === null
            ) {

                return 0;

            }


            return Math.max(

                0,

                Math.floor(

                    (
                        Date.now() -
                        processingStartTime
                    ) / 1000

                )

            );

        }


        function getElapsedText() {

            return (
                "処理時間: " +
                formatElapsed(
                    getElapsedSeconds()
                )
            );

        }


        function startElapsedTimer(
            message
        ) {

            stopElapsedTimer();


            function update() {

                if (
                    processingStartTime === null
                ) {

                    elapsedTimerId =
                        null;

                    return;

                }


                setStatus(

                    message +
                    "\n" +
                    getElapsedText(),

                    null

                );


                elapsedTimerId =
                    setTimeout(
                        update,
                        1000
                    );

            }


            update();

        }


        // =====================================
        // ステータス
        // =====================================

        function setStatus(
            message,
            type
        ) {

            const text =
                String(
                    message || ""
                );


            if (!conversionStatusArea) {

                return;

            }


            conversionStatusArea.textContent =
                text;


            conversionStatusArea.style.whiteSpace =
                "pre-line";


            conversionStatusArea.classList.remove(
                "error",
                "success"
            );


            if (type) {

                conversionStatusArea.classList.add(
                    type
                );

            }

        }


        function clearStatus() {

            if (!conversionStatusArea) {

                return;

            }


            conversionStatusArea.textContent =
                "";


            conversionStatusArea.classList.remove(
                "error",
                "success"
            );

        }


        // =====================================
        // JSON解析
        // =====================================

        async function parseResponse(
            response
        ) {

            const text =
                await response.text();


            if (!text) {

                return null;

            }


            try {

                return JSON.parse(
                    text
                );

            }
            catch (error) {

                console.error(
                    "[SUBTITLE] JSON解析エラー:",
                    error
                );


                console.error(
                    "[SUBTITLE] response:",
                    text
                );


                return {

                    success:
                        false,

                    message:
                        text

                };

            }

        }


        // =====================================
        // APIエラー
        // =====================================

        function getResponseErrorMessage(
            data,
            defaultMessage
        ) {

            if (
                data &&
                typeof data.message ===
                    "string" &&
                data.message.trim()
            ) {

                return data.message.trim();

            }


            if (
                data &&
                typeof data.error ===
                    "string" &&
                data.error.trim()
            ) {

                return data.error.trim();

            }


            return defaultMessage;

        }


        // =====================================
        // FormDataアップロード
        // =====================================

        async function uploadToEndpoint(
            endpoint,
            file
        ) {

            if (!file) {

                throw new Error(
                    "アップロードするファイルがありません。"
                );

            }


            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            console.log(
                "[SUBTITLE] upload:",
                endpoint,
                file.name
            );


            const response =
                await fetch(
                    endpoint,
                    {

                        method:
                            "POST",

                        body:
                            formData

                    }
                );


            const data =
                await parseResponse(
                    response
                );


            if (!response.ok) {

                throw new Error(
                    getResponseErrorMessage(
                        data,
                        "ファイルのアップロードに失敗しました。"
                    )
                );

            }


            if (
                !data ||
                data.success !== true
            ) {

                throw new Error(
                    getResponseErrorMessage(
                        data,
                        "ファイル処理に失敗しました。"
                    )
                );

            }


            return data;

        }


        // =====================================
        // MP3 → SRT
        // =====================================

        async function createSrtWithGemini(
            file
        ) {

            if (!file) {

                throw new Error(
                    "MP3ファイルがありません。"
                );

            }


            return await uploadToEndpoint(
                "/subtitle-upload-mp3",
                file
            );

        }


        // =====================================
        // MP4アップロード
        // =====================================

        async function uploadMp4(
            file
        ) {

            return await uploadToEndpoint(
                "/subtitle-upload-mp4",
                file
            );

        }


        // =====================================
        // SRTアップロード
        // =====================================

        async function uploadSrt(
            file
        ) {

            return await uploadToEndpoint(
                "/subtitle-upload-srt",
                file
            );

        }


        // =====================================
        // 字幕焼き込み
        // =====================================
        
        async function embedSubtitle(
            mp4Filename,
            srtFilename
        ) {
        
            if (!mp4Filename) {
        
                throw new Error(
                    "転送済みMP4ファイルがありません。"
                );
        
            }
        
        
            if (!srtFilename) {
        
                throw new Error(
                    "転送済みSRTファイルがありません。"
                );
        
            }
        
        
            const fontSettings =
                getFontSettings();
        
        
            const requestBody = {
        
                mp4_file:
                    mp4Filename,
        
                srt_file:
                    srtFilename,
        
                font:
                    fontSettings.font,
        
                text_color:
                    fontSettings.text_color,
        
                text_color_hex:
                    fontSettings.text_color_hex,
        
                outline_color:
                    fontSettings.outline_color,
        
                outline_color_hex:
                    fontSettings.outline_color_hex,
        
                outline_width:
                    fontSettings.outline_width,
        
                preset_name:
                    fontSettings.preset_name
        
            };
        
        
            console.log(
                "[SUBTITLE] embed request:",
                requestBody
            );
        
        
            // =====================================
            // /subtitle-create-mp4 へJSON送信
            // =====================================
        
            const response =
                await fetch(
                    "/subtitle-create-mp4",
                    {
        
                        method:
                            "POST",
        
                        headers: {
                            "Content-Type":
                                "application/json"
                        },
        
                        body:
                            JSON.stringify(
                                requestBody
                            )
        
                    }
                );
        
        
            const data =
                await parseResponse(
                    response
                );
        
        
            if (!response.ok) {
        
                throw new Error(
                    getResponseErrorMessage(
                        data,
                        "字幕MP4の作成に失敗しました。"
                    )
                );
        
            }
        
        
            if (
                !data ||
                data.success !== true
            ) {
        
                throw new Error(
                    getResponseErrorMessage(
                        data,
                        "字幕MP4の作成に失敗しました。"
                    )
                );
        
            }
        
        
            const filename =
                data.subtitle_mp4_file ||
                data.filename ||
                data.output_file ||
                data.mp4_file;
        
        
            if (!filename) {
        
                throw new Error(
                    "作成された字幕MP4のファイル名を取得できませんでした。"
                );
        
            }
        
        
            console.log(
                "[SUBTITLE] subtitle MP4 created:",
                filename
            );
        
        
            console.log(
                "[SUBTITLE] subtitle MP4 response:",
                data
            );
        
        
            return {
        
                ...data,
        
                filename:
                    filename
        
            };
        
        }
        

        // =====================================
        // ダウンロードボタン
        // =====================================

        function createDownloadButton(
            label,
            filename,
            downloadUrl
        ) {

            if (!downloadArea) {

                return;

            }


            downloadArea.innerHTML =
                "";


            if (!filename) {

                return;

            }


            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.textContent =
                label ||
                "ダウンロード";


            button.className =
                "test-button";


            button.addEventListener(
                "click",
                function () {

                    let url =
                        downloadUrl;


                    if (!url) {

                        url =
                            "/downloads/" +
                            encodeURIComponent(
                                filename
                            );

                    }


                    const link =
                        document.createElement(
                            "a"
                        );


                    link.href =
                        url;


                    link.download =
                        filename;


                    document.body.appendChild(
                        link
                    );


                    link.click();


                    link.remove();

                }
            );


            downloadArea.appendChild(
                button
            );

        }


        // =====================================
        // MP4転送
        // =====================================

        async function transferMp4() {

            if (
                subtitleState.isProcessing
            ) {

                return;

            }


            const file =
                mp4Input.files &&
                mp4Input.files.length
                    ? mp4Input.files[0]
                    : null;


            if (!file) {

                setStatus(
                    "MP4ファイルを選択してください。",
                    "error"
                );

                return;

            }


            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".mp4")
            ) {

                setStatus(
                    "MP4ファイルを選択してください。",
                    "error"
                );

                return;

            }


            subtitleState.isProcessing =
                true;


            if (mp4UploadButton) {

                mp4UploadButton.disabled =
                    true;

            }


            if (srtUploadButton) {

                srtUploadButton.disabled =
                    true;

            }


            setFontDisabled(
                true
            );


            startProcessing();


            try {

                startElapsedTimer(
                    "MP4を転送しています..."
                );


                const result =
                    await uploadMp4(
                        file
                    );


                subtitleState.mp4File =
                    file;


                subtitleState.mp4Filename =
                    result.mp4_file ||
                    result.filename ||
                    file.name;


                subtitleState.uploadedMp4Filename =
                    subtitleState.mp4Filename;


                stopElapsedTimer();


                setStatus(

                    "MP4の転送が完了しました。\n\n" +
                    "MP4: " +
                    subtitleState.uploadedMp4Filename +
                    "\n\n" +
                    getElapsedText(),

                    "success"

                );

            }
            catch (error) {

                stopElapsedTimer();


                console.error(
                    "[SUBTITLE] MP4転送エラー:",
                    error
                );


                setStatus(

                    "MP4転送中にエラーが発生しました。\n" +
                    (
                        error &&
                        error.message
                            ? error.message
                            : "不明なエラー"
                    ) +
                    "\n\n" +
                    getElapsedText(),

                    "error"

                );

            }
            finally {

                stopElapsedTimer();


                subtitleState.isProcessing =
                    false;


                processingStartTime =
                    null;


                setFontDisabled(
                    false
                );


                if (mp4UploadButton) {

                    mp4UploadButton.disabled =
                        false;

                }


                if (srtUploadButton) {

                    srtUploadButton.disabled =
                        false;

                }


                updateSubtitleMp4Button();

            }

        }


        // =====================================
        // SRT転送
        // =====================================

        async function transferSrt() {

            if (
                subtitleState.isProcessing
            ) {

                return;

            }


            const file =
                srtInput.files &&
                srtInput.files.length
                    ? srtInput.files[0]
                    : null;


            if (!file) {

                setStatus(
                    "SRTファイルを選択してください。",
                    "error"
                );

                return;

            }


            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".srt")
            ) {

                setStatus(
                    "SRTファイルを選択してください。",
                    "error"
                );

                return;

            }


            subtitleState.isProcessing =
                true;


            if (mp4UploadButton) {

                mp4UploadButton.disabled =
                    true;

            }


            if (srtUploadButton) {

                srtUploadButton.disabled =
                    true;

            }


            setFontDisabled(
                true
            );


            startProcessing();


            try {

                startElapsedTimer(
                    "SRTを転送しています..."
                );


                const result =
                    await uploadSrt(
                        file
                    );


                subtitleState.srtFile =
                    file;


                subtitleState.srtFilename =
                    result.srt_file ||
                    result.filename ||
                    file.name;


                subtitleState.uploadedSrtFilename =
                    subtitleState.srtFilename;


                stopElapsedTimer();


                setStatus(

                    "SRTの転送が完了しました。\n\n" +
                    "SRT: " +
                    subtitleState.uploadedSrtFilename +
                    "\n\n" +
                    getElapsedText(),

                    "success"

                );

            }
            catch (error) {

                stopElapsedTimer();


                console.error(
                    "[SUBTITLE] SRT転送エラー:",
                    error
                );


                setStatus(

                    "SRT転送中にエラーが発生しました。\n" +
                    (
                        error &&
                        error.message
                            ? error.message
                            : "不明なエラー"
                    ) +
                    "\n\n" +
                    getElapsedText(),

                    "error"

                );

            }
            finally {

                stopElapsedTimer();


                subtitleState.isProcessing =
                    false;


                processingStartTime =
                    null;


                setFontDisabled(
                    false
                );


                if (mp4UploadButton) {

                    mp4UploadButton.disabled =
                        false;

                }


                if (srtUploadButton) {

                    srtUploadButton.disabled =
                        false;

                }


                updateSubtitleMp4Button();

            }

        }


        // =====================================
        // 字幕MP4ボタン状態
        // =====================================

        function updateSubtitleMp4Button() {

            const hasMp4 =
                !!subtitleState.uploadedMp4Filename;


            const hasSrt =
                !!subtitleState.uploadedSrtFilename;


            subtitleMp4Button.disabled =
                !hasMp4 ||
                !hasSrt ||
                subtitleState.isProcessing;

        }


        // =====================================
        // MP3選択
        // =====================================

        mp3SelectButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                mp3Input.click();

            }
        );


        mp3Input.addEventListener(
            "change",
            function () {

                const file =
                    this.files &&
                    this.files.length
                        ? this.files[0]
                        : null;


                subtitleState.mp3File =
                    file;


                subtitleState.mp3Filename =
                    file
                        ? file.name
                        : "";


                updateFileDisplay(
                    mp3SelectButton,
                    file,
                    "ファイルが選択されていません → mp3ファイルを選択してください"
                );


                geminiButton.disabled =
                    !file ||
                    subtitleState.isProcessing;

            }
        );


        // =====================================
        // MP4選択
        // =====================================

        mp4SelectButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                mp4Input.click();

            }
        );


        mp4Input.addEventListener(
            "change",
            function () {

                const file =
                    this.files &&
                    this.files.length
                        ? this.files[0]
                        : null;


                subtitleState.mp4File =
                    file;


                subtitleState.mp4Filename =
                    file
                        ? file.name
                        : "";


                // 新しいMP4を選択したら
                // 古い転送済みMP4を無効化

                subtitleState.uploadedMp4Filename =
                    "";


                updateFileDisplay(
                    mp4SelectButton,
                    file,
                    "ファイルが選択されていません → mp4ファイルを選択してください"
                );


                updateSubtitleMp4Button();

            }
        );


        // =====================================
        // SRT選択
        // =====================================

        srtSelectButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                srtInput.click();

            }
        );


        srtInput.addEventListener(
            "change",
            function () {

                const file =
                    this.files &&
                    this.files.length
                        ? this.files[0]
                        : null;


                subtitleState.srtFile =
                    file;


                subtitleState.srtFilename =
                    file
                        ? file.name
                        : "";


                // 新しいSRTを選択したら
                // 古い転送済みSRTを無効化

                subtitleState.uploadedSrtFilename =
                    "";


                updateFileDisplay(
                    srtSelectButton,
                    file,
                    "ファイルが選択されていません → srtファイルを選択してください"
                );


                updateSubtitleMp4Button();

            }
        );


        // =====================================
        // MP4転送ボタン
        // =====================================

        if (mp4UploadButton) {

            mp4UploadButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    transferMp4();

                }
            );

        }


        // =====================================
        // SRT転送ボタン
        // =====================================

        if (srtUploadButton) {

            srtUploadButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    transferSrt();

                }
            );

        }


        // =====================================
        // Gemini
        // =====================================

        geminiButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                const file =
                    mp3Input.files &&
                    mp3Input.files.length
                        ? mp3Input.files[0]
                        : null;


                if (!file) {

                    setStatus(
                        "MP3ファイルを選択してください。",
                        "error"
                    );

                    return;

                }


                if (
                    !file.name
                        .toLowerCase()
                        .endsWith(".mp3")
                ) {

                    setStatus(
                        "MP3ファイルを選択してください。",
                        "error"
                    );

                    return;

                }


                subtitleState.isProcessing =
                    true;


                geminiButton.disabled =
                    true;


                setFontDisabled(
                    true
                );


                startProcessing();


                try {

                    startElapsedTimer(
                        "MP3をアップロードしています..."
                    );


                    const result =
                        await createSrtWithGemini(
                            file
                        );


                    subtitleState.mp3Filename =
                        result.mp3_file ||
                        result.filename ||
                        file.name;


                    subtitleState.generatedSrtFilename =
                        result.srt_file ||
                        "";


                    stopElapsedTimer();


                    if (!result.srt_file) {

                        throw new Error(
                            "作成されたSRTファイル名を取得できませんでした。"
                        );

                    }


                    setStatus(

                        "SRTファイルの作成が完了しました。\n\n" +
                        "SRT: " +
                        result.srt_file +
                        "\n\n" +
                        getElapsedText(),

                        "success"

                    );


                    createDownloadButton(
                        "SRTをダウンロード",
                        result.srt_file,
                        result.download_url
                    );

                }
                catch (error) {

                    stopElapsedTimer();


                    console.error(
                        "[SUBTITLE] SRT作成エラー:",
                        error
                    );


                    setStatus(

                        "SRT作成中にエラーが発生しました。\n" +
                        (
                            error &&
                            error.message
                                ? error.message
                                : "不明なエラー"
                        ) +
                        "\n\n" +
                        getElapsedText(),

                        "error"

                    );

                }
                finally {

                    stopElapsedTimer();


                    subtitleState.isProcessing =
                        false;


                    processingStartTime =
                        null;


                    setFontDisabled(
                        false
                    );


                    geminiButton.disabled =
                        !(
                            mp3Input.files &&
                            mp3Input.files.length
                        );

                }

            }
        );


        // =====================================
        // 字幕MP4作成
        //
        // ・ここではアップロードしない
        // ・転送済みMP4/SRTだけを使用
        // ・/subtitle-create-mp4 を呼び出す
        // =====================================

        subtitleMp4Button.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                if (
                    subtitleState.isProcessing
                ) {

                    return;

                }


                const mp4Filename =
                    subtitleState.uploadedMp4Filename;


                const srtFilename =
                    subtitleState.uploadedSrtFilename;


                if (!mp4Filename) {

                    setStatus(
                        "先にMP4ファイルを転送してください。",
                        "error"
                    );

                    return;

                }


                if (!srtFilename) {

                    setStatus(
                        "先にSRTファイルを転送してください。",
                        "error"
                    );

                    return;

                }


                subtitleState.isProcessing =
                    true;


                subtitleMp4Button.disabled =
                    true;


                if (mp4UploadButton) {

                    mp4UploadButton.disabled =
                        true;

                }


                if (srtUploadButton) {

                    srtUploadButton.disabled =
                        true;

                }


                setFontDisabled(
                    true
                );


                startProcessing();


                try {

                    startElapsedTimer(

                        "字幕を動画に付けています...\n" +
                        "しばらくお待ちください。"

                    );


                    const embedResult =
                        await embedSubtitle(
                            mp4Filename,
                            srtFilename
                        );


                    subtitleState.generatedSubtitleMp4Filename =
                        embedResult.filename;


                    stopElapsedTimer();


                    setStatus(

                        "字幕mp4の作成が完了しました。\n\n" +
                        "ファイル: " +
                        embedResult.filename +
                        "\n\n" +
                        getElapsedText(),

                        "success"

                    );


                    createDownloadButton(

                        "字幕付きMP4をダウンロード",

                        embedResult.filename,

                        embedResult.download_url

                    );

                }
                catch (error) {

                    stopElapsedTimer();


                    console.error(
                        "[SUBTITLE] 字幕MP4作成エラー:",
                        error
                    );


                    setStatus(

                        "字幕mp4作成中にエラーが発生しました。\n" +
                        (
                            error &&
                            error.message
                                ? error.message
                                : "不明なエラー"
                        ) +
                        "\n\n" +
                        getElapsedText(),

                        "error"

                    );

                }
                finally {

                    stopElapsedTimer();


                    subtitleState.isProcessing =
                        false;


                    processingStartTime =
                        null;


                    setFontDisabled(
                        false
                    );


                    if (mp4UploadButton) {

                        mp4UploadButton.disabled =
                            false;

                    }


                    if (srtUploadButton) {

                        srtUploadButton.disabled =
                            false;

                    }


                    updateSubtitleMp4Button();

                }

            }
        );


        // =====================================
        // 外部公開
        // =====================================

        mainObject.createSrtWithGemini =
            createSrtWithGemini;


        mainObject.uploadMp4 =
            uploadMp4;


        mainObject.uploadSrt =
            uploadSrt;


        mainObject.transferMp4 =
            transferMp4;


        mainObject.transferSrt =
            transferSrt;


        mainObject.embedSubtitle =
            embedSubtitle;


        mainObject.createDownloadButton =
            createDownloadButton;


        mainObject.getState =
            function () {

                return subtitleState;

            };


        mainObject.getFontPreset =
            function () {

                return getFontPreset();

            };


        mainObject.getFontSettings =
            function () {

                return getFontSettings();

            };


        mainObject.clearResult =
            clearStatus;


        // =====================================
        // 初期表示
        // =====================================

        updateFileDisplay(
            mp3SelectButton,
            null,
            "mp3ファイルを選択してください"
        );


        updateFileDisplay(
            mp4SelectButton,
            null,
            "mp4ファイルを選択してください"
        );


        updateFileDisplay(
            srtSelectButton,
            null,
            "srtファイルを選択してください"
        );


        geminiButton.disabled =
            true;


        if (mp4UploadButton) {

            mp4UploadButton.disabled =
                false;

        }


        if (srtUploadButton) {

            srtUploadButton.disabled =
                false;

        }


        updateSubtitleMp4Button();


        console.log(
            "[SUBTITLE] initializeSubtitle() complete"
        );

    }


    // =====================================
    // DOMContentLoaded
    // =====================================

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializeSubtitle,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeSubtitle();

    }

})();
