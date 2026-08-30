// =====================================
// Subtitle Embed
// subtitle.js
//
// MP4 + SRT
// ↓
// アップロード
// ↓
// 字幕焼き込み
// ↓
// xxx_subtitle.mp4
// ↓
// ダウンロード
//
// ・処理時間リアルタイム表示
// ・MP4 / SRT の選択確認
// ・二重実行防止
// ・エラー処理
// ・converter.js の字幕付きMP4表示にも対応
//
// 使用:
// ・converter-utils.js
// ・converter.js
// =====================================

(function () {

    "use strict";


    // =====================================
    // 読み込み確認
    // =====================================

    console.log(
        "[SUB EMBED] ====================================="
    );

    console.log(
        "[SUB EMBED] sub_embed.js loaded"
    );

    console.log(
        "[SUB EMBED] ====================================="
    );


    // =====================================
    // 初期化
    // =====================================

    function initializeSubEmbed() {

        console.log(
            "[SUB EMBED] initializeSubEmbed() start"
        );


        // =====================================
        // DOM
        // =====================================

        const mp4Input =
            document.getElementById(
                "sub-embed-mp4"
            );


        const srtInput =
            document.getElementById(
                "sub-embed-srt"
            );


        const uploadButton =
            document.getElementById(
                "sub-embed-upload-button"
            );


        const statusElement =
            document.getElementById(
                "sub-embed-status"
            );


        const filesElement =
            document.getElementById(
                "sub-embed-files"
            );


        console.log(
            "[SUB EMBED] mp4Input =",
            mp4Input
        );

        console.log(
            "[SUB EMBED] srtInput =",
            srtInput
        );

        console.log(
            "[SUB EMBED] uploadButton =",
            uploadButton
        );

        console.log(
            "[SUB EMBED] statusElement =",
            statusElement
        );

        console.log(
            "[SUB EMBED] filesElement =",
            filesElement
        );


        // =====================================
        // 必須DOM
        // =====================================

        if (!uploadButton) {

            console.error(
                "[SUB EMBED] ERROR: " +
                "sub-embed-upload-button が見つかりません"
            );

            return;

        }


        // =====================================
        // 二重初期化防止
        // =====================================

        if (
            uploadButton.dataset.subEmbedInitialized ===
            "true"
        ) {

            console.log(
                "[SUB EMBED] " +
                "アップロードボタンは既に初期化済みです"
            );

            return;

        }


        uploadButton.dataset.subEmbedInitialized =
            "true";


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
        // ステータス
        // =====================================

        function setStatus(
            message,
            type
        ) {

            if (!statusElement) {

                return;

            }


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


        // =====================================
        // 結果クリア
        // =====================================

        function clearPreviousResult() {

            if (statusElement) {

                statusElement.textContent =
                    "";


                statusElement.classList.remove(
                    "error",
                    "success"
                );

            }


            if (filesElement) {

                filesElement.innerHTML =
                    "";

            }

        }


        // =====================================
        // 経過時間
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
        // 経過時間テキスト
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
        // JSONレスポンス
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
                    "[SUB EMBED] JSON解析エラー:",
                    error
                );


                console.error(
                    "[SUB EMBED] レスポンス:",
                    text
                );


                return null;

            }

        }


        // =====================================
        // エラーメッセージ
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


            console.log(
                "[SUB EMBED] アップロード開始:",
                file.name
            );


            console.log(
                "[SUB EMBED] ファイルサイズ:",
                file.size
            );


            const formData =
                new FormData();


            formData.append(
                "file",
                file
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
                        "アップロードに失敗しました。"
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
                        "アップロードに失敗しました。"
                    )
                );

            }


            if (
                !data.filename
            ) {

                throw new Error(
                    "アップロードされたファイル名を取得できませんでした。"
                );

            }


            console.log(
                "[SUB EMBED] アップロード完了:",
                data
            );


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


            console.log(
                "[SUB EMBED] 字幕焼き込み開始"
            );


            console.log(
                "[SUB EMBED] MP4:",
                mp4Filename
            );


            console.log(
                "[SUB EMBED] SRT:",
                srtFilename
            );


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


            if (
                !data.filename
            ) {

                throw new Error(
                    "字幕付きMP4のファイル名を取得できませんでした。"
                );

            }


            console.log(
                "[SUB EMBED] 字幕焼き込み完了:",
                data
            );


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
        // =====================================

        function createDownloadButton(
            filename,
            downloadUrl
        ) {

            if (!filesElement) {

                console.warn(
                    "[SUB EMBED] filesElement がありません"
                );

                return;

            }


            if (!filename) {

                console.error(
                    "[SUB EMBED] " +
                    "ダウンロードファイル名がありません"
                );

                return;

            }


            const resolvedUrl =
                resolveDownloadUrl(
                    filename,
                    downloadUrl
                );


            const section =
                document.createElement(
                    "div"
                );


            section.className =
                "sub-embed-download-section";


            const label =
                document.createElement(
                    "div"
                );


            label.className =
                "sub-embed-download-label";


            label.textContent =
                "字幕付き動画";


            section.appendChild(
                label
            );


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
                "字幕付きMP4をダウンロード";


            section.appendChild(
                button
            );


            filesElement.appendChild(
                section
            );


            console.log(
                "[SUB EMBED] ダウンロードボタン追加:",
                {
                    filename:
                        filename,

                    downloadUrl:
                        resolvedUrl
                }
            );

        }


        // =====================================
        // converter.jsへ通知
        // =====================================

        function notifyConverterMain(
            filename
        ) {

            if (!filename) {

                return;

            }


            if (
                window.converterMain &&
                typeof
                    window.converterMain.addSubtitleEmbedFile ===
                    "function"
            ) {

                console.log(
                    "[SUB EMBED] " +
                    "converterMainへ字幕付きMP4を通知:",
                    filename
                );


                window.converterMain.addSubtitleEmbedFile(
                    filename
                );

            }

        }


        // =====================================
        // converter.jsへ詳細通知
        // =====================================

        function notifyConverterDetail(
            html
        ) {

            if (!html) {

                return;

            }


            if (
                window.converterMain &&
                typeof
                    window.converterMain.addSubtitleEmbedInfo ===
                    "function"
            ) {

                console.log(
                    "[SUB EMBED] " +
                    "converterMainへ処理詳細を通知"
                );


                window.converterMain.addSubtitleEmbedInfo(
                    html
                );

            }

        }


        // =====================================
        // 字幕付きMP4詳細HTML
        // =====================================

        function createConversionDetail(
            startTime,
            endTime,
            elapsedText
        ) {

            let title =
                "不明";


            let duration =
                "不明";


            if (
                window.converterState
            ) {

                title =
                    window.converterState.currentVideoTitle ||
                    "不明";


                duration =
                    window.converterState.currentVideoDuration ||
                    "不明";

            }


            let formattedDuration =
                duration;


            let formattedStart =
                startTime
                    ? startTime.toLocaleTimeString(
                        "ja-JP",
                        {

                            hour:
                                "2-digit",

                            minute:
                                "2-digit",

                            second:
                                "2-digit",

                            hour12:
                                false

                        }
                    )
                    : "";


            let formattedEnd =
                endTime
                    ? endTime.toLocaleTimeString(
                        "ja-JP",
                        {

                            hour:
                                "2-digit",

                            minute:
                                "2-digit",

                            second:
                                "2-digit",

                            hour12:
                                false

                        }
                    )
                    : "";


            if (
                utils &&
                typeof utils.formatDuration ===
                    "function"
            ) {

                formattedDuration =
                    utils.formatDuration(
                        duration
                    );

            }


            if (
                utils &&
                typeof utils.formatClock ===
                    "function"
            ) {

                formattedStart =
                    startTime
                        ? utils.formatClock(
                            startTime
                        )
                        : "";


                formattedEnd =
                    endTime
                        ? utils.formatClock(
                            endTime
                        )
                        : "";

            }


            if (
                utils &&
                typeof utils.escapeHtml ===
                    "function"
            ) {

                title =
                    utils.escapeHtml(
                        title
                    );


                formattedDuration =
                    utils.escapeHtml(
                        formattedDuration
                    );


                formattedStart =
                    utils.escapeHtml(
                        formattedStart
                    );


                formattedEnd =
                    utils.escapeHtml(
                        formattedEnd
                    );


                elapsedText =
                    utils.escapeHtml(
                        elapsedText
                    );

            }


            return `

                <div class="conversion-info subtitle-embed-conversion-info">

                    <div class="conversion-info-title">

                        ★字幕付きMP4変換

                    </div>


                    <div>

                        タイトル：
                        ${title}

                    </div>


                    <div>

                        再生時間：
                        ${formattedDuration}

                    </div>


                    <div>

                        実行開始：
                        ${formattedStart}

                    </div>


                    <div>

                        実行終了：
                        ${formattedEnd}

                        （${elapsedText}）

                    </div>

                </div>

            `;

        }


        // =====================================
        // アップロードボタン
        // =====================================

        uploadButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                console.log(
                    "[SUB EMBED] " +
                    "アップロードボタンがクリックされました"
                );


                // =================================
                // 前回タイマー停止
                // =================================

                stopElapsedTimer();


                // =================================
                // 前回結果クリア
                // =================================

                clearPreviousResult();


                // =================================
                // 処理開始
                // =================================

                processingStartTime =
                    Date.now();


                const processStartDate =
                    new Date(
                        processingStartTime
                    );


                console.log(
                    "[SUB EMBED] 処理開始時間:",
                    processStartDate.toLocaleString()
                );


                // =================================
                // ファイル取得
                // =================================

                let mp4File =
                    null;


                let srtFile =
                    null;


                if (
                    mp4Input &&
                    mp4Input.files &&
                    mp4Input.files.length > 0
                ) {

                    mp4File =
                        mp4Input.files[0];

                }


                if (
                    srtInput &&
                    srtInput.files &&
                    srtInput.files.length > 0
                ) {

                    srtFile =
                        srtInput.files[0];

                }


                console.log(
                    "[SUB EMBED] MP4:",
                    mp4File
                );


                console.log(
                    "[SUB EMBED] SRT:",
                    srtFile
                );


                // =================================
                // MP4確認
                // =================================

                if (!mp4File) {

                    processingStartTime =
                        null;


                    setStatus(
                        "MP4ファイルを選択してください。",
                        "error"
                    );


                    return;

                }


                // =================================
                // SRT確認
                // =================================

                if (!srtFile) {

                    processingStartTime =
                        null;


                    setStatus(
                        "SRTファイルを選択してください。",
                        "error"
                    );


                    return;

                }


                // =================================
                // MP4拡張子確認
                // =================================

                if (
                    !mp4File.name
                        .toLowerCase()
                        .endsWith(
                            ".mp4"
                        )
                ) {

                    processingStartTime =
                        null;


                    setStatus(
                        "MP4ファイルを選択してください。",
                        "error"
                    );


                    return;

                }


                // =================================
                // SRT拡張子確認
                // =================================

                if (
                    !srtFile.name
                        .toLowerCase()
                        .endsWith(
                            ".srt"
                        )
                ) {

                    processingStartTime =
                        null;


                    setStatus(
                        "SRTファイルを選択してください。",
                        "error"
                    );


                    return;

                }


                // =================================
                // ボタン無効化
                // =================================

                uploadButton.disabled =
                    true;


                // =================================
                // ログ
                // =================================

                console.log(
                    "[SUB EMBED] ====================================="
                );

                console.log(
                    "[SUB EMBED] 処理開始"
                );

                console.log(
                    "[SUB EMBED] MP4:",
                    mp4File.name
                );

                console.log(
                    "[SUB EMBED] MP4 size:",
                    mp4File.size
                );

                console.log(
                    "[SUB EMBED] SRT:",
                    srtFile.name
                );

                console.log(
                    "[SUB EMBED] SRT size:",
                    srtFile.size
                );

                console.log(
                    "[SUB EMBED] ====================================="
                );


                try {

                    // =================================
                    // STEP 1
                    // MP4アップロード
                    // =================================

                    startElapsedTimer(
                        "MP4をアップロードしています..."
                    );


                    const mp4Result =
                        await uploadFile(
                            mp4File
                        );


                    console.log(
                        "[SUB EMBED] MP4 upload result:",
                        mp4Result
                    );


                    // =================================
                    // STEP 2
                    // SRTアップロード
                    // =================================

                    startElapsedTimer(
                        "SRTをアップロードしています..."
                    );


                    const srtResult =
                        await uploadFile(
                            srtFile
                        );


                    console.log(
                        "[SUB EMBED] SRT upload result:",
                        srtResult
                    );


                    // =================================
                    // STEP 3
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


                    console.log(
                        "[SUB EMBED] embed result:",
                        embedResult
                    );


                    // =================================
                    // 完了時刻
                    // =================================

                    const processingEndDate =
                        new Date();


                    // =================================
                    // 処理時間
                    // =================================

                    const elapsedSeconds =
                        processingStartTime !==
                        null

                            ? Math.floor(
                                (
                                    Date.now() -
                                    processingStartTime
                                ) / 1000
                            )

                            : 0;


                    const elapsedText =
                        utils &&
                        typeof utils.formatElapsed ===
                            "function"

                            ? utils.formatElapsed(
                                elapsedSeconds
                            )

                            : elapsedSeconds +
                              "秒";


                    // =================================
                    // タイマー停止
                    // =================================

                    stopElapsedTimer();


                    // =================================
                    // 完了表示
                    // =================================

                    setStatus(

                        "字幕焼き込みが完了しました。\n\n" +
                        "処理時間: " +
                        elapsedText,

                        "success"

                    );


                    // =================================
                    // ダウンロードURL
                    // =================================

                    const downloadUrl =
                        resolveDownloadUrl(

                            embedResult.filename,

                            embedResult.download_url

                        );


                    // =================================
                    // ダウンロードボタン
                    // =================================

                    createDownloadButton(

                        embedResult.filename,

                        downloadUrl

                    );


                    // =================================
                    // converter.jsへ通知
                    // =================================

                    notifyConverterMain(
                        embedResult.filename
                    );


                    // =================================
                    // 処理詳細
                    // =================================

                    const detailHtml =
                        createConversionDetail(

                            processStartDate,

                            processingEndDate,

                            elapsedText

                        );


                    notifyConverterDetail(
                        detailHtml
                    );


                    // =================================
                    // 完了ログ
                    // =================================

                    console.log(
                        "[SUB EMBED] ====================================="
                    );

                    console.log(
                        "[SUB EMBED] すべての処理が完了しました"
                    );

                    console.log(
                        "[SUB EMBED] 開始:",
                        processStartDate
                    );

                    console.log(
                        "[SUB EMBED] 終了:",
                        processingEndDate
                    );

                    console.log(
                        "[SUB EMBED] 処理時間:",
                        elapsedText
                    );

                    console.log(
                        "[SUB EMBED] ファイル:",
                        embedResult.filename
                    );

                    console.log(
                        "[SUB EMBED] ダウンロードURL:",
                        downloadUrl
                    );

                    console.log(
                        "[SUB EMBED] ====================================="
                    );

                }
                catch (error) {

                    // =================================
                    // タイマー停止
                    // =================================

                    stopElapsedTimer();


                    // =================================
                    // エラー処理時間
                    // =================================

                    const elapsedSeconds =
                        getElapsedSeconds();


                    const elapsedText =
                        utils &&
                        typeof utils.formatElapsed ===
                            "function"

                            ? utils.formatElapsed(
                                elapsedSeconds
                            )

                            : elapsedSeconds +
                              "秒";


                    // =================================
                    // エラーログ
                    // =================================

                    console.error(
                        "[SUB EMBED] 処理エラー:",
                        error
                    );


                    console.error(
                        "[SUB EMBED] " +
                        "エラー発生までの時間:",
                        elapsedText
                    );


                    // =================================
                    // エラー表示
                    // =================================

                    setStatus(

                        "処理中にエラーが発生しました。\n" +
                        (
                            error &&
                            error.message
                                ? error.message
                                : "不明なエラー"
                        ) +
                        "\n\n" +
                        "エラー発生までの処理時間: " +
                        elapsedText,

                        "error"

                    );

                }
                finally {

                    // =================================
                    // タイマー停止
                    // =================================

                    stopElapsedTimer();


                    // =================================
                    // 時間リセット
                    // =================================

                    processingStartTime =
                        null;


                    // =================================
                    // ボタン再有効化
                    // =================================

                    uploadButton.disabled =
                        false;

                }

            }

        );


        // =====================================
        // MP4選択
        // =====================================

        if (mp4Input) {

            mp4Input.addEventListener(
                "change",
                function () {

                    console.log(
                        "[SUB EMBED] MP4 change"
                    );


                    if (
                        this.files &&
                        this.files.length > 0
                    ) {

                        console.log(
                            "[SUB EMBED] MP4選択:",
                            this.files[0].name
                        );

                    }

                }
            );

        }


        // =====================================
        // SRT選択
        // =====================================

        if (srtInput) {

            srtInput.addEventListener(
                "change",
                function () {

                    console.log(
                        "[SUB EMBED] SRT change"
                    );


                    if (
                        this.files &&
                        this.files.length > 0
                    ) {

                        console.log(
                            "[SUB EMBED] SRT選択:",
                            this.files[0].name
                        );

                    }

                }
            );

        }


        // =====================================
        // 初期化完了
        // =====================================

        console.log(
            "[SUB EMBED] initializeSubEmbed() complete"
        );


        console.log(
            "[SUB EMBED] " +
            "アップロードボタンのクリック待機中"
        );

    }


    // =====================================
    // DOMContentLoaded
    // =====================================

    if (
        document.readyState ===
        "loading"
    ) {

        console.log(
            "[SUB EMBED] " +
            "DOMContentLoaded 待機"
        );


        document.addEventListener(
            "DOMContentLoaded",
            initializeSubEmbed,
            {
                once:
                    true
            }
        );

    }
    else {

        console.log(
            "[SUB EMBED] " +
            "DOMは既に読み込み済み"
        );


        initializeSubEmbed();

    }


})();
