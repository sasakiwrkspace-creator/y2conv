// =====================================
// Subtitle Embed
// sub_embed.js
//
// MP4 + SRT
// ↓
// アップロード
// ↓
// 字幕焼き込み
// ↓
// xxx_sub_embed.mp4
// ↓
// ダウンロード
//
// 処理時間リアルタイム表示
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


        // =================================
        // DOM取得
        // =================================

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


        // =================================
        // DOM確認
        // =================================

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


        // =================================
        // 必須DOM確認
        // =================================

        if (!uploadButton) {

            console.error(
                "[SUB EMBED] ERROR: "
                + "sub-embed-upload-button が見つかりません"
            );

            return;
        }


        // =================================
        // 二重初期化防止
        // =================================

        if (
            uploadButton.dataset.subEmbedInitialized ===
            "true"
        ) {

            console.log(
                "[SUB EMBED] "
                + "アップロードボタンは既に初期化済みです"
            );

            return;
        }


        uploadButton.dataset.subEmbedInitialized =
            "true";


        // =================================
        // タイマー管理
        // =================================

        let elapsedTimerId = null;

        let processingStartTime = null;


        // =================================
        // ステータス表示
        // =================================

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


        // =================================
        // 前回表示クリア
        // =================================

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


        // =================================
        // 経過時間フォーマット
        // =================================

        function formatElapsedTime(
            milliseconds
        ) {

            const totalSeconds =
                Math.floor(
                    milliseconds / 1000
                );


            const hours =
                Math.floor(
                    totalSeconds / 3600
                );


            const minutes =
                Math.floor(
                    (totalSeconds % 3600) / 60
                );


            const seconds =
                totalSeconds % 60;


            if (hours > 0) {

                return (
                    hours +
                    "時間 " +
                    minutes +
                    "分 " +
                    seconds +
                    "秒"
                );

            }


            if (minutes > 0) {

                return (
                    minutes +
                    "分 " +
                    seconds +
                    "秒"
                );

            }


            return (
                seconds +
                "秒"
            );

        }


        // =================================
        // 経過時間テキスト
        // =================================

        function getElapsedText() {

            if (
                processingStartTime === null
            ) {

                return "処理時間: 0秒";

            }


            const elapsed =
                Date.now() -
                processingStartTime;


            return (
                "処理時間: " +
                formatElapsedTime(
                    elapsed
                )
            );

        }


        // =================================
        // リアルタイムタイマー停止
        // =================================

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


        // =================================
        // リアルタイムタイマー開始
        //
        // setIntervalではなく
        // setTimeoutを1回ずつ実行する
        // =================================

        function startElapsedTimer(
            message
        ) {

            stopElapsedTimer();


            function updateTimer() {

                if (
                    processingStartTime === null
                ) {

                    return;

                }


                const elapsedText =
                    getElapsedText();


                setStatus(

                    message +
                    "\n" +
                    elapsedText,

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
        // ファイルアップロード
        // =====================================

        async function uploadFile(
            file
        ) {

            console.log(
                "[SUB EMBED] アップロード開始:",
                file.name
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
                        method: "POST",
                        body: formData
                    }
                );


            let data = null;


            try {

                data =
                    await response.json();

            } catch (error) {

                console.error(
                    "[SUB EMBED] "
                    + "JSON解析エラー:",
                    error
                );

            }


            if (!response.ok) {

                const message =
                    data &&
                    data.message
                        ? data.message
                        : "アップロードに失敗しました。";


                throw new Error(
                    message
                );

            }


            if (
                !data ||
                data.success !== true
            ) {

                const message =
                    data &&
                    data.message
                        ? data.message
                        : "アップロードに失敗しました。";


                throw new Error(
                    message
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
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({

                            mp4_filename:
                                mp4Filename,

                            srt_filename:
                                srtFilename

                        })

                    }
                );


            let data = null;


            try {

                data =
                    await response.json();

            } catch (error) {

                console.error(
                    "[SUB EMBED] "
                    + "JSON解析エラー:",
                    error
                );

            }


            if (!response.ok) {

                const message =
                    data &&
                    data.message
                        ? data.message
                        : "字幕焼き込みに失敗しました。";


                throw new Error(
                    message
                );

            }


            if (
                !data ||
                data.success !== true
            ) {

                const message =
                    data &&
                    data.message
                        ? data.message
                        : "字幕焼き込みに失敗しました。";


                throw new Error(
                    message
                );

            }


            console.log(
                "[SUB EMBED] "
                + "字幕焼き込み完了:",
                data
            );


            return data;

        }


        // =====================================
        // ダウンロードボタン作成
        // =====================================

        function createDownloadButton(
            filename,
            downloadUrl
        ) {

            if (!filesElement) {

                return;
            }


            // ---------------------------------
            // セクション
            // ---------------------------------

            const section =
                document.createElement(
                    "div"
                );


            section.className =
                "sub-embed-download-section";


            // ---------------------------------
            // ラベル
            // ---------------------------------

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


            // ---------------------------------
            // ボタン
            // ---------------------------------

            const button =
                document.createElement(
                    "a"
                );


            button.className =
                "download-button";


            button.href =
                downloadUrl;


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

        }


        // =====================================
        // アップロードボタン
        // =====================================

        uploadButton.addEventListener(
            "click",
            async function (event) {

                event.preventDefault();


                console.log(
                    "[SUB EMBED] "
                    + "アップロードボタンがクリックされました"
                );


                // =================================
                // 前回のタイマー停止
                // =================================

                stopElapsedTimer();


                // =================================
                // 前回の結果をクリア
                // =================================

                clearPreviousResult();


                // =================================
                // 処理開始時間
                // =================================

                processingStartTime =
                    Date.now();


                console.log(
                    "[SUB EMBED] "
                    + "処理開始時間:",
                    new Date(
                        processingStartTime
                    ).toLocaleString()
                );


                // =================================
                // ファイル取得
                // =================================

                let mp4File = null;

                let srtFile = null;


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
                // 拡張子確認
                // =================================

                if (
                    !mp4File.name
                        .toLowerCase()
                        .endsWith(".mp4")
                ) {

                    processingStartTime =
                        null;

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
                        "[SUB EMBED] "
                        + "embed result:",
                        embedResult
                    );


                    // =================================
                    // 処理時間確定
                    // =================================

                    const elapsedTime =
                        Date.now() -
                        processingStartTime;


                    const elapsedText =
                        formatElapsedTime(
                            elapsedTime
                        );


                    // =================================
                    // タイマー停止
                    // =================================

                    stopElapsedTimer();


                    // =================================
                    // STEP 4
                    // 完了
                    // =================================

                    setStatus(

                        "字幕焼き込みが完了しました。\n\n" +
                        "処理時間: " +
                        elapsedText,

                        "success"

                    );


                    // =================================
                    // STEP 5
                    // ダウンロードボタン
                    // =================================

                    createDownloadButton(

                        embedResult.filename,

                        embedResult.download_url

                    );


                    console.log(
                        "[SUB EMBED] "
                        + "すべての処理が完了しました"
                    );


                } catch (error) {

                    // =================================
                    // タイマー停止
                    // =================================

                    stopElapsedTimer();


                    // =================================
                    // エラー時処理時間
                    // =================================

                    let elapsedText =
                        "0秒";


                    if (
                        processingStartTime !==
                        null
                    ) {

                        const elapsedTime =
                            Date.now() -
                            processingStartTime;


                        elapsedText =
                            formatElapsedTime(
                                elapsedTime
                            );

                    }


                    console.error(
                        "[SUB EMBED] "
                        + "処理エラー:",
                        error
                    );


                    console.error(
                        "[SUB EMBED] "
                        + "エラー発生までの時間:",
                        elapsedText
                    );


                    // =================================
                    // エラー表示
                    // =================================

                    setStatus(

                        "処理中にエラーが発生しました。\n" +
                        error.message +
                        "\n\n" +
                        "エラー発生までの処理時間: " +
                        elapsedText,

                        "error"

                    );


                } finally {

                    // =================================
                    // タイマー停止
                    // =================================

                    stopElapsedTimer();


                    // =================================
                    // 処理時間リセット
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
        // MP4選択イベント
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

                        const file =
                            this.files[0];


                        console.log(
                            "[SUB EMBED] "
                            + "MP4選択:",
                            file.name
                        );

                    }

                }
            );

        }


        // =====================================
        // SRT選択イベント
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

                        const file =
                            this.files[0];


                        console.log(
                            "[SUB EMBED] "
                            + "SRT選択:",
                            file.name
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
            "[SUB EMBED] "
            + "アップロードボタンのクリック待機中"
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
            "[SUB EMBED] "
            + "DOMContentLoaded 待機"
        );


        document.addEventListener(
            "DOMContentLoaded",
            initializeSubEmbed,
            {
                once: true
            }
        );

    } else {

        console.log(
            "[SUB EMBED] "
            + "DOMは既に読み込み済み"
        );


        initializeSubEmbed();

    }


})();
