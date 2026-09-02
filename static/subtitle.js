// =====================================
// YouTube Converter - Subtitle
// subtitle.js
//
// タブ2専用
//
// 重要:
// ・タブ1のconverter.jsには触れない
// ・#convertBtnには触れない
// ・タブ1のイベントを登録しない
// ・タブ1のDOMを操作しない
// ・/subtitle-* APIのみ使用
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


        const statusElement =
            document.getElementById(
                "status"
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


        // =================================
        // State
        // =================================

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

            isProcessing:
                false

        };


        window.subtitleState =
            subtitleState;


        // =================================
        // Utils
        // =================================

        const utils =
            window.converterUtils;


        // =================================
        // タイマー
        // =================================

        let elapsedTimerId =
            null;


        let processingStartTime =
            null;


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

            const seconds =
                getElapsedSeconds();


            if (
                utils &&
                typeof utils.formatElapsed ===
                    "function"
            ) {

                return (
                    "処理時間: " +
                    utils.formatElapsed(
                        seconds
                    )
                );

            }


            return (
                "処理時間: " +
                seconds +
                "秒"
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


        // =================================
        // ステータス
        // =================================

        function setStatus(
            message,
            type
        ) {

            if (statusElement) {

                statusElement.textContent =
                    message;

                statusElement.style.whiteSpace =
                    "pre-line";

                statusElement.classList.remove(
                    "error",
                    "success"
                );


                if (type) {

                    statusElement.classList.add(
                        type
                    );

                }

            }


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    message;

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

        }


        function clearStatus() {

            if (statusElement) {

                statusElement.textContent =
                    "";

                statusElement.classList.remove(
                    "error",
                    "success"
                );

            }


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    "";

                conversionStatusArea.classList.remove(
                    "error",
                    "success"
                );

            }

        }


        // =================================
        // JSON解析
        // =================================

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


        // =================================
        // APIエラーメッセージ
        // =================================

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


        // =================================
        // 共通POST FormData
        // =================================

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


        // =================================
        // MP3 → SRT
        //
        // タブ2専用
        // =================================

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


        // =================================
        // MP4アップロード
        // =================================

        async function uploadMp4(
            file
        ) {

            return await uploadToEndpoint(

                "/subtitle-upload-mp4",

                file

            );

        }


        // =================================
        // SRTアップロード
        // =================================

        async function uploadSrt(
            file
        ) {

            return await uploadToEndpoint(

                "/subtitle-upload-srt",

                file

            );

        }


        // =================================
        // 字幕MP4
        // =================================

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
                                    srtFilename

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


            if (!data.filename) {

                throw new Error(
                    "字幕付きMP4のファイル名を取得できませんでした。"
                );

            }


            return data;

        }


        // =================================
        // ダウンロードURL
        // =================================

        function makeDownloadUrl(
            filename
        ) {

            if (!filename) {

                return "";

            }


            if (
                utils &&
                typeof utils.makeDownloadUrl ===
                    "function"
            ) {

                return utils.makeDownloadUrl(
                    filename
                );

            }


            return (
                "/download/" +
                encodeURIComponent(
                    String(filename)
                )
            );

        }


        // =================================
        // ダウンロードボタン
        // =================================

        function createDownloadButton(
            label,
            filename,
            downloadUrl
        ) {

            if (!downloadArea) {

                return;

            }


            if (!filename) {

                return;

            }


            const url =
                downloadUrl ||
                makeDownloadUrl(
                    filename
                );


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


        // =================================
        // ファイル表示
        // =================================

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


        // =================================
        // 字幕MP4ボタン状態
        // =================================

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


        // =================================
        // MP3選択
        //
        // タブ2のボタンだけ
        // =================================

        mp3SelectButton.addEventListener(
            "click",
            function () {

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


        // =================================
        // MP4選択
        // =================================

        mp4SelectButton.addEventListener(
            "click",
            function () {

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


        // =================================
        // SRT選択
        // =================================

        srtSelectButton.addEventListener(
            "click",
            function () {

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


        // =================================
        // Geminiボタン
        //
        // タブ2専用
        // =================================

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


                startProcessing();


                clearStatus();


                try {

                    // ---------------------------------
                    // MP3 → Gemini → SRT
                    // ---------------------------------

                    startElapsedTimer(
                        "MP3をアップロードしています..."
                    );


                    const result =
                        await createSrtWithGemini(
                            file
                        );


                    subtitleState.mp3Filename =
                        result.mp3_file ||
                        result.filename;


                    subtitleState.generatedSrtFilename =
                        result.srt_file;


                    stopElapsedTimer();


                    setStatus(

                        "SRTファイルの作成が完了しました。\n\n" +
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


        // =================================
        // 字幕MP4作成
        //
        // MP4 + SRTをアップロードして
        // 字幕MP4を作成
        // =================================

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


                startProcessing();


                clearStatus();


                try {

                    // ---------------------------------
                    // MP4アップロード
                    // ---------------------------------

                    startElapsedTimer(
                        "MP4をアップロードしています..."
                    );


                    const mp4Result =
                        await uploadMp4(
                            mp4File
                        );


                    subtitleState.mp4Filename =
                        mp4Result.filename;


                    // ---------------------------------
                    // SRTアップロード
                    // ---------------------------------

                    startElapsedTimer(
                        "SRTをアップロードしています..."
                    );


                    const srtResult =
                        await uploadSrt(
                            srtFile
                        );


                    subtitleState.srtFilename =
                        srtResult.filename;


                    // ---------------------------------
                    // 字幕焼き込み
                    // ---------------------------------

                    startElapsedTimer(

                        "字幕を動画に付けています...\n" +
                        "しばらくお待ちください。"

                    );


                    const embedResult =
                        await embedSubtitle(

                            mp4Result.filename,

                            srtResult.filename

                        );


                    subtitleState.generatedSubtitleMp4Filename =
                        embedResult.filename;


                    stopElapsedTimer();


                    setStatus(

                        "字幕mp4の作成が完了しました。\n\n" +
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


                    updateSubtitleMp4Button();

                }

            }
        );


        // =================================
        // 外部公開
        //
        // ここでは「関数を公開するだけ」。
        //
        // タブ1のイベント登録はしない。
        // =================================

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


        mainObject.clearResult =
            clearStatus;


        // =================================
        // 初期表示
        // =================================

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
