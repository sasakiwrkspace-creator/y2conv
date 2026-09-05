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
// ・#subtitle-font-button を使用
// ・選択中のプリセット名を保持
// ・字幕MP4作成時にpreset_nameをAPIへ送信
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
        // タブ2 DOMのみ取得
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


        const subtitleFontButton =
            document.getElementById(
                "subtitle-font-button"
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

            generatedSrtFilename:
                "",

            generatedSubtitleMp4Filename:
                "",

            fontPreset:
                "標準",

            isProcessing:
                false

        };


        window.subtitleState =
            subtitleState;


        // =====================================
        // フォントプリセット
        // =====================================

        const FONT_PRESETS = [

            "標準",

            "ゴシック",

            "明朝",

            "太字ゴシック",

            "太字明朝"

        ];


        // =====================================
        // フォントボタン表示更新
        // =====================================

        function updateFontButton() {

            if (!subtitleFontButton) {

                return;

            }


            const presetName =
                subtitleState.fontPreset ||
                "標準";


            subtitleFontButton.textContent =
                presetName;


            subtitleFontButton.title =
                "字幕フォント: " +
                presetName;

        }


        // =====================================
        // フォント選択
        // =====================================

        function selectFontPreset() {

            const currentIndex =
                FONT_PRESETS.indexOf(
                    subtitleState.fontPreset
                );


            const currentName =
                subtitleState.fontPreset ||
                "標準";


            const message =
                "字幕フォントを選択してください。\n\n" +
                FONT_PRESETS
                    .map(
                        function (name, index) {

                            return (
                                (index + 1) +
                                ". " +
                                name
                            );

                        }
                    )
                    .join("\n") +
                "\n\n" +
                "現在: " +
                currentName;


            const input =
                window.prompt(
                    message,
                    String(
                        currentIndex >= 0
                            ? currentIndex + 1
                            : 1
                    )
                );


            if (
                input === null
            ) {

                return;

            }


            const selectedNumber =
                Number(
                    String(
                        input
                    ).trim()
                );


            if (
                !Number.isInteger(
                    selectedNumber
                ) ||
                selectedNumber < 1 ||
                selectedNumber > FONT_PRESETS.length
            ) {

                alert(
                    "フォント番号が正しくありません。"
                );

                return;

            }


            subtitleState.fontPreset =
                FONT_PRESETS[
                    selectedNumber - 1
                ];


            updateFontButton();


            console.log(
                "[SUBTITLE] font preset selected:",
                subtitleState.fontPreset
            );

        }


        // =====================================
        // フォントボタン
        // =====================================

        if (subtitleFontButton) {

            subtitleFontButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    if (
                        subtitleState.isProcessing
                    ) {

                        return;

                    }


                    selectFontPreset();

                }
            );

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


            if (
                hours > 0
            ) {

                return (
                    hours +
                    "時間 " +
                    minutes +
                    "分 " +
                    secs +
                    "秒"
                );

            }


            if (
                minutes > 0
            ) {

                return (
                    minutes +
                    "分 " +
                    secs +
                    "秒"
                );

            }


            return (
                secs +
                "秒"
            );

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

            if (!conversionStatusArea) {

                return;

            }


            conversionStatusArea.textContent =
                String(
                    message || ""
                );


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


                return null;

            }

        }


        // =====================================
        // APIエラーメッセージ
        // =====================================

        function getResponseErrorMessage(
            data,
            defaultMessage
        ) {

            if (
                data &&
                typeof data.message === "string" &&
                data.message.trim()
            ) {

                return data.message.trim();

            }


            if (
                data &&
                typeof data.error === "string" &&
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
        //
        // /subtitle-upload-mp3 が
        // upload → Gemini → SRT保存まで行う。
        // =====================================

        async function createSrtWithGemini(
            file
        ) {

            if (!file) {

                throw new Error(
                    "MP3ファイルがありません。"
                );

            }


            const result =
                await uploadToEndpoint(
                    "/subtitle-upload-mp3",
                    file
                );


            if (!result.srt_file) {

                throw new Error(
                    "作成されたSRTファイル名を取得できませんでした。"
                );

            }


            return result;

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
        // 字幕MP4作成
        //
        // /subtitle-create-mp4
        //
        // preset_nameを必ず送信する。
        // =====================================

        async function embedSubtitle(
            mp4Filename,
            srtFilename
        ) {

            if (!mp4Filename) {

                throw new Error(
                    "MP4ファイル名がありません。"
                );

            }


            if (!srtFilename) {

                throw new Error(
                    "SRTファイル名がありません。"
                );

            }


            const presetName =
                subtitleState.fontPreset ||
                "標準";


            console.log(
                "[SUBTITLE] create subtitle MP4",
                {
                    mp4_file:
                        mp4Filename,

                    srt_file:
                        srtFilename,

                    preset_name:
                        presetName
                }
            );


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
                            JSON.stringify({

                                mp4_file:
                                    mp4Filename,

                                srt_file:
                                    srtFilename,

                                preset_name:
                                    presetName

                            })

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
                        "字幕焼き込みに失敗しました。"
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
                        "字幕焼き込みに失敗しました。"
                    )
                );

            }


            const filename =
                data.subtitle_mp4_file ||
                data.filename;


            if (!filename) {

                throw new Error(
                    "字幕付きMP4のファイル名を取得できませんでした。"
                );

            }


            return {

                ...data,

                filename:
                    filename

            };

        }


        // =====================================
        // ダウンロードURL
        //
        // 今回のsubtitle_routes.pyには
        // subtitle-download-mp4は存在しない。
        //
        // そのため既存の /download/ を使用する。
        // =====================================

        function makeDownloadUrl(
            filename
        ) {

            if (!filename) {

                return "";

            }


            return (
                "/download/" +
                encodeURIComponent(
                    String(filename)
                )
            );

        }


        // =====================================
        // ダウンロードボタン
        // =====================================

        function createDownloadButton(
            label,
            filename,
            downloadUrl
        ) {

            if (
                !downloadArea ||
                !filename
            ) {

                return;

            }


            const url =
                downloadUrl ||
                makeDownloadUrl(
                    filename
                );


            if (!url) {

                return;

            }


            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "subtitle-download-item";


            const button =
                document.createElement(
                    "a"
                );


            button.className =
                "download-button";


            button.href =
                url;


            button.download =
                filename;


            button.textContent =
                label;


            wrapper.appendChild(
                button
            );


            downloadArea.appendChild(
                wrapper
            );

        }


        // =====================================
        // ファイル表示
        // =====================================

        function updateFileDisplay(
            button,
            file,
            defaultText
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
                    defaultText;


                button.title =
                    "";

            }

        }


        // =====================================
        // 字幕MP4ボタン状態
        // =====================================

        function updateSubtitleMp4Button() {

            const hasMp4 =
                !!(
                    mp4Input.files &&
                    mp4Input.files.length
                );


            const hasSrt =
                !!(
                    srtInput.files &&
                    srtInput.files.length
                );


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


                updateFileDisplay(

                    mp4SelectButton,

                    file,

                    "MP4ファイルを選択してください"

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


                updateFileDisplay(

                    srtSelectButton,

                    file,

                    "SRTファイルを選択してください"

                );


                updateSubtitleMp4Button();

            }
        );


        // =====================================
        // Geminiボタン
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


                if (subtitleFontButton) {

                    subtitleFontButton.disabled =
                        true;

                }


                startProcessing();


                clearStatus();


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
                        result.srt_file;


                    stopElapsedTimer();


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


                    console.log(
                        "[SUBTITLE] SRT作成完了:",
                        result.srt_file
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


                const mp4File =
                    mp4Input.files &&
                    mp4Input.files.length
                        ? mp4Input.files[0]
                        : null;


                const srtFile =
                    srtInput.files &&
                    srtInput.files.length
                        ? srtInput.files[0]
                        : null;


                if (!mp4File) {

                    setStatus(
                        "MP4ファイルを選択してください。",
                        "error"
                    );

                    return;

                }


                if (!srtFile) {

                    setStatus(
                        "SRTファイルを選択してください。",
                        "error"
                    );

                    return;

                }


                if (
                    !mp4File.name
                        .toLowerCase()
                        .endsWith(".mp4")
                ) {

                    setStatus(
                        "MP4ファイルを選択してください。",
                        "error"
                    );

                    return;

                }


                if (
                    !srtFile.name
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


                subtitleMp4Button.disabled =
                    true;


                if (subtitleFontButton) {

                    subtitleFontButton.disabled =
                        true;

                }


                startProcessing();


                clearStatus();


                try {

                    // =================================
                    // MP4アップロード
                    // =================================

                    startElapsedTimer(
                        "MP4をアップロードしています..."
                    );


                    const mp4Result =
                        await uploadMp4(
                            mp4File
                        );


                    subtitleState.mp4Filename =
                        mp4Result.mp4_file ||
                        mp4Result.filename ||
                        mp4File.name;


                    // =================================
                    // SRTアップロード
                    // =================================

                    startElapsedTimer(
                        "SRTをアップロードしています..."
                    );


                    const srtResult =
                        await uploadSrt(
                            srtFile
                        );


                    subtitleState.srtFilename =
                        srtResult.srt_file ||
                        srtResult.filename ||
                        srtFile.name;


                    // =================================
                    // 字幕焼き込み
                    // =================================

                    startElapsedTimer(

                        "字幕を動画に付けています...\n" +
                        "しばらくお待ちください。"

                    );


                    const embedResult =
                        await embedSubtitle(

                            subtitleState.mp4Filename,

                            subtitleState.srtFilename

                        );


                    subtitleState.generatedSubtitleMp4Filename =
                        embedResult.filename;


                    stopElapsedTimer();


                    setStatus(

                        "字幕mp4の作成が完了しました。\n\n" +
                        "フォント: " +
                        subtitleState.fontPreset +
                        "\n\n" +
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


                    console.log(
                        "[SUBTITLE] 字幕MP4作成完了:",
                        embedResult.filename
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


                    if (subtitleFontButton) {

                        subtitleFontButton.disabled =
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

                return subtitleState.fontPreset;

            };


        mainObject.setFontPreset =
            function (presetName) {

                if (
                    !FONT_PRESETS.includes(
                        presetName
                    )
                ) {

                    throw new Error(
                        "存在しないフォントプリセットです: " +
                        presetName
                    );

                }


                subtitleState.fontPreset =
                    presetName;


                updateFontButton();

            };


        mainObject.clearResult =
            clearStatus;


        // =====================================
        // 初期表示
        // =====================================

        updateFontButton();


        updateFileDisplay(

            mp3SelectButton,

            null,

            "ファイルが選択されていません → mp3ファイルを選択してください"

        );


        updateFileDisplay(

            mp4SelectButton,

            null,

            "MP4ファイルを選択してください"

        );


        updateFileDisplay(

            srtSelectButton,

            null,

            "SRTファイルを選択してください"

        );


        geminiButton.disabled =
            true;


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
