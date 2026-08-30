// =====================================
// YouTube Converter - Subtitle
// subtitle.js
//
// タブ2：ファイル変換
//
// 【上】
// MP3
// ↓
// Gemini
// ↓
// SRT
//
// 【下】
// MP4 + SRT
// ↓
// 字幕焼き込み
// ↓
// 字幕MP4
//
// 共通:
// ・処理状況
// ・処理時間
// ・ダウンロードエリア
//
// 重要:
// ・タブ1のconverter.jsには触れない
// ・#convertBtnには触れない
// ・タブ1のイベントを登録しない
// ・#status / #conversion-status-area / #downloadArea を使用
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


        // =====================================
        // 二重初期化防止
        // =====================================

        if (
            window.subtitleMain &&
            window.subtitleMain.__initialized
        ) {

            console.log(
                "[SUBTITLE] already initialized"
            );

            return;

        }


        // =====================================
        // DOM
        // =====================================

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


        // =====================================
        // 共通エリア
        // =====================================

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


        console.log(
            "[SUBTITLE] mp3Input:",
            mp3Input
        );

        console.log(
            "[SUBTITLE] mp3SelectButton:",
            mp3SelectButton
        );

        console.log(
            "[SUBTITLE] geminiButton:",
            geminiButton
        );

        console.log(
            "[SUBTITLE] mp4Input:",
            mp4Input
        );

        console.log(
            "[SUBTITLE] mp4SelectButton:",
            mp4SelectButton
        );

        console.log(
            "[SUBTITLE] srtInput:",
            srtInput
        );

        console.log(
            "[SUBTITLE] srtSelectButton:",
            srtSelectButton
        );

        console.log(
            "[SUBTITLE] subtitleMp4Button:",
            subtitleMp4Button
        );

        console.log(
            "[SUBTITLE] downloadArea:",
            downloadArea
        );


        // =====================================
        // 必須DOM確認
        // =====================================

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


        // =====================================
        // メインオブジェクト
        // =====================================

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

            isUploadingMp3:
                false,

            isGeminiProcessing:
                false,

            isUploadingMp4:
                false,

            isUploadingSrt:
                false,

            isSubtitleMp4Processing:
                false

        };


        window.subtitleState =
            subtitleState;


        // =====================================
        // Utils
        // =====================================

        const utils =
            window.converterUtils;


        // =====================================
        // タイマー
        // =====================================

        let elapsedTimerId =
            null;


        let processingStartTime =
            null;


        // =====================================
        // ステータス表示
        // =====================================

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


        // =====================================
        // 結果クリア
        //
        // 注意:
        // ダウンロードエリアは消さない。
        // 共通エリアとして結果を蓄積する。
        // =====================================

        function clearStatusOnly() {

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


        // =====================================
        // 処理開始
        // =====================================

        function startProcessing() {

            processingStartTime =
                Date.now();

            stopElapsedTimer();

        }


        // =====================================
        // 経過秒数
        // =====================================

        function getElapsedSeconds() {

            if (
                processingStartTime ===
                null
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


        // =====================================
        // 経過時間
        // =====================================

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


        // =====================================
        // タイマー停止
        // =====================================

        function stopElapsedTimer() {

            if (
                elapsedTimerId !==
                null
            ) {

                clearTimeout(
                    elapsedTimerId
                );

                elapsedTimerId =
                    null;

            }

        }


        // =====================================
        // タイマー開始
        // =====================================

        function startElapsedTimer(
            message
        ) {

            stopElapsedTimer();


            function updateTimer() {

                if (
                    processingStartTime ===
                    null
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
                        updateTimer,
                        1000
                    );

            }


            updateTimer();

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
        // ファイルアップロード
        // =====================================

        async function uploadFile(
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
                file.name
            );


            const response =
                await fetch(
                    "/subtitle-upload",
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
                        "ファイルのアップロードに失敗しました。"
                    )
                );

            }


            if (!data.filename) {

                throw new Error(
                    "アップロード後のファイル名を取得できませんでした。"
                );

            }


            return data;

        }


        // =====================================
        // Gemini → SRT
        // =====================================

        async function createSrtWithGemini(
            filename
        ) {

            if (!filename) {

                throw new Error(
                    "MP3ファイル名がありません。"
                );

            }


            const response =
                await fetch(
                    "/subtitle-gemini",
                    {

                        method:
                            "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify({

                                filename:
                                    filename

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
                        "GeminiによるSRT作成に失敗しました。"
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
                        "GeminiによるSRT作成に失敗しました。"
                    )
                );

            }


            if (!data.filename) {

                throw new Error(
                    "作成されたSRTファイル名を取得できませんでした。"
                );

            }


            return data;

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
                    "/subtitle-embed",
                    {

                        method:
                            "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify({

                                mp4_filename:
                                    mp4Filename,

                                srt_filename:
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


        // =====================================
        // ダウンロードURL
        // =====================================

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


        // =====================================
        // ダウンロードURL解決
        // =====================================

        function resolveDownloadUrl(
            filename,
            downloadUrl
        ) {

            if (
                typeof downloadUrl ===
                    "string" &&
                downloadUrl.trim()
            ) {

                return downloadUrl.trim();

            }


            return makeDownloadUrl(
                filename
            );

        }


        // =====================================
        // ダウンロードボタン
        //
        // 共通 #downloadArea に追加
        // =====================================

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


            const resolvedUrl =
                resolveDownloadUrl(
                    filename,
                    downloadUrl
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
                resolvedUrl;


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


            console.log(
                "[SUBTITLE] download button:",
                filename
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
        // MP4作成ボタン状態
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
                subtitleState.isSubtitleMp4Processing;

        }


        // =====================================
        // MP3選択
        //
        // 表示ボタン自体をファイル選択に使用
        // =====================================

        mp3SelectButton.addEventListener(
            "click",
            function () {

                mp3Input.click();

            }
        );


        // =====================================
        // MP3変更
        // =====================================

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
                    subtitleState.isUploadingMp3 ||
                    subtitleState.isGeminiProcessing;


                console.log(
                    "[SUBTITLE] MP3 selected:",
                    file
                );

            }
        );


        // =====================================
        // MP4選択
        // =====================================

        mp4SelectButton.addEventListener(
            "click",
            function () {

                mp4Input.click();

            }
        );


        // =====================================
        // MP4変更
        // =====================================

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
            function () {

                srtInput.click();

            }
        );


        // =====================================
        // SRT変更
        // =====================================

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
                    subtitleState.isUploadingMp3 ||
                    subtitleState.isGeminiProcessing
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


                subtitleState.isUploadingMp3 =
                    true;


                subtitleState.isGeminiProcessing =
                    true;


                geminiButton.disabled =
                    true;


                startProcessing();


                clearStatusOnly();


                try {

                    // =================================
                    // MP3アップロード
                    // =================================

                    startElapsedTimer(
                        "MP3をアップロードしています..."
                    );


                    const uploadResult =
                        await uploadFile(
                            file
                        );


                    subtitleState.mp3Filename =
                        uploadResult.filename;


                    // =================================
                    // Gemini
                    // =================================

                    startElapsedTimer(
                        "Geminiで音声を解析しています...\n" +
                        "しばらくお待ちください。"
                    );


                    const srtResult =
                        await createSrtWithGemini(
                            uploadResult.filename
                        );


                    subtitleState.generatedSrtFilename =
                        srtResult.filename;


                    stopElapsedTimer();


                    const elapsedText =
                        getElapsedText();


                    setStatus(

                        "SRTファイルの作成が完了しました。\n\n" +
                        elapsedText,

                        "success"

                    );


                    // =================================
                    // SRTダウンロード
                    // =================================

                    createDownloadButton(

                        "SRTをダウンロード",

                        srtResult.filename,

                        srtResult.download_url

                    );


                    console.log(
                        "[SUBTITLE] SRT作成完了:",
                        srtResult.filename
                    );

                }
                catch (error) {

                    stopElapsedTimer();


                    const elapsedText =
                        getElapsedText();


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
                        elapsedText,

                        "error"

                    );

                }
                finally {

                    stopElapsedTimer();


                    subtitleState.isUploadingMp3 =
                        false;


                    subtitleState.isGeminiProcessing =
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
                    subtitleState.isSubtitleMp4Processing
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


                subtitleState.isSubtitleMp4Processing =
                    true;


                subtitleMp4Button.disabled =
                    true;


                startProcessing();


                clearStatusOnly();


                try {

                    // =================================
                    // MP4アップロード
                    // =================================

                    startElapsedTimer(
                        "MP4をアップロードしています..."
                    );


                    const mp4Result =
                        await uploadFile(
                            mp4File
                        );


                    subtitleState.mp4Filename =
                        mp4Result.filename;


                    // =================================
                    // SRTアップロード
                    // =================================

                    startElapsedTimer(
                        "SRTをアップロードしています..."
                    );


                    const srtResult =
                        await uploadFile(
                            srtFile
                        );


                    subtitleState.srtFilename =
                        srtResult.filename;


                    // =================================
                    // 字幕焼き込み
                    // =================================

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


                    const elapsedText =
                        getElapsedText();


                    setStatus(

                        "字幕mp4の作成が完了しました。\n\n" +
                        elapsedText,

                        "success"

                    );


                    // =================================
                    // 字幕MP4ダウンロード
                    // =================================

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


                    const elapsedText =
                        getElapsedText();


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
                        elapsedText,

                        "error"

                    );

                }
                finally {

                    stopElapsedTimer();


                    subtitleState.isSubtitleMp4Processing =
                        false;


                    processingStartTime =
                        null;


                    updateSubtitleMp4Button();

                }

            }
        );


        // =====================================
        // 外部公開
        //
        // 将来 converter.js 等から
        // 関数として利用可能
        // =====================================

        mainObject.uploadFile =
            uploadFile;


        mainObject.createSrtWithGemini =
            createSrtWithGemini;


        mainObject.embedSubtitle =
            embedSubtitle;


        mainObject.clearResult =
            clearStatusOnly;


        mainObject.getState =
            function () {

                return subtitleState;

            };


        mainObject.addDownloadButton =
            createDownloadButton;


        // =====================================
        // 初期表示
        // =====================================

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
