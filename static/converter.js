// =====================================
// YouTube Converter JavaScript
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const urlInput =
            document.getElementById(
                "youtube-url"
            );

        const checkButton =
            document.getElementById(
                "check-button"
            );

        const convertButton =
            document.getElementById(
                "convertBtn"
            );

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );

        let currentJobId = null;

        // =====================================
        // 確認用タイマー
        // =====================================

        let checkSeconds = 0;
        let checkTimer = null;

        // =====================================
        // 変換用タイマー
        // =====================================

        let convertSeconds = 0;
        let convertTimer = null;

        // =====================================
        // 確認タイマー停止
        // =====================================

        function stopCheckTimer() {

            if (checkTimer) {

                clearInterval(
                    checkTimer
                );

                checkTimer = null;

            }

        }

        // =====================================
        // 変換タイマー停止
        // =====================================

        function stopConvertTimer() {

            if (convertTimer) {

                clearInterval(
                    convertTimer
                );

                convertTimer = null;

            }

        }

        // =====================================
        // HTTPエラー確認
        // =====================================

        async function parseResponse(response) {

            const text =
                await response.text();

            if (!response.ok) {

                throw new Error(
                    "HTTP "
                    + response.status
                    + " : "
                    + (
                        text
                            ? text.substring(0, 500)
                            : "サーバーから応答がありません"
                    )
                );

            }

            if (!text) {

                throw new Error(
                    "サーバーから空の応答が返されました"
                );

            }

            try {

                return JSON.parse(
                    text
                );

            }
            catch (error) {

                console.error(
                    "JSON parse error:",
                    error
                );

                console.error(
                    "Response:",
                    text
                );

                throw new Error(
                    "サーバーから正しいJSON応答が返されませんでした"
                );

            }

        }

        // =====================================
        // YouTube確認ボタン
        // =====================================

        if (checkButton) {

            checkButton.addEventListener(
                "click",
                checkVideo
            );

        }

        // =====================================
        // Enterキーで確認
        // =====================================

        if (urlInput) {

            urlInput.addEventListener(
                "keydown",
                function (event) {

                    if (event.key === "Enter") {

                        event.preventDefault();

                        checkVideo();

                    }

                }
            );

        }

        // =====================================
        // YouTube確認
        // =====================================

        async function checkVideo() {

            const url =
                urlInput.value.trim();

            if (!url) {

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }

            // ---------------------------------
            // 既存タイマー停止
            // ---------------------------------

            stopCheckTimer();

            // ---------------------------------
            // ボタン状態
            // ---------------------------------

            checkButton.disabled =
                true;

            checkSeconds = 0;

            checkButton.textContent =
                "確認中 0秒";

            // ---------------------------------
            // 確認タイマー開始
            // ---------------------------------

            checkTimer =
                setInterval(
                    function () {

                        checkSeconds++;

                        checkButton.textContent =
                            "確認中 "
                            + checkSeconds
                            + "秒";

                    },
                    1000
                );

            try {

                const response =
                    await fetch(
                        "/check",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    url: url
                                })
                        }
                    );

                const data =
                    await parseResponse(
                        response
                    );

                // ---------------------------------
                // 成功
                // ---------------------------------

                if (data.success) {

                    const convertArea =
                        document.getElementById(
                            "convert-area"
                        );

                    if (convertArea) {

                        convertArea.style.display =
                            "block";

                    }

                    const filename =
                        document.getElementById(
                            "filename"
                        );

                    if (
                        filename
                        && data.filename !== undefined
                    ) {

                        filename.value =
                            data.filename;

                    }

                    const endTime =
                        document.getElementById(
                            "end-time"
                        );

                    if (
                        endTime
                        && data.duration !== undefined
                    ) {

                        endTime.value =
                            data.duration;

                    }

                }
                else {

                    throw new Error(
                        data.message
                        || "YouTube情報の確認に失敗しました"
                    );

                }

            }
            catch (error) {

                console.error(
                    "checkVideo error:",
                    error
                );

                alert(
                    error.message
                    || "確認エラー"
                );

            }
            finally {

                // ---------------------------------
                // 必ずタイマー停止
                // ---------------------------------

                stopCheckTimer();

                // ---------------------------------
                // ボタン復帰
                // ---------------------------------

                checkButton.disabled =
                    false;

                checkButton.textContent =
                    "確認";

            }

        }

        // =====================================
        // 変換ボタン
        // =====================================

        if (convertButton) {

            convertButton.addEventListener(
                "click",
                startConvert
            );

        }

        // =====================================
        // 変換開始
        // =====================================

        async function startConvert() {

            const url =
                urlInput.value.trim();

            const outputs =
                [];

            document
                .querySelectorAll(
                    "input[name='output']:checked"
                )
                .forEach(
                    function (item) {

                        outputs.push(
                            item.value
                        );

                    }
                );

            if (!url) {

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }

            if (outputs.length === 0) {

                alert(
                    "作成ファイルを選択してください"
                );

                return;

            }

            // ---------------------------------
            // 確認タイマー停止
            // ---------------------------------

            stopCheckTimer();

            // ---------------------------------
            // 変換タイマー停止
            // ---------------------------------

            stopConvertTimer();

            // ---------------------------------
            // ボタン状態
            // ---------------------------------

            convertButton.disabled =
                true;

            convertSeconds = 0;

            convertButton.textContent =
                "変換中 0秒";

            // ---------------------------------
            // 変換タイマー開始
            // ---------------------------------

            convertTimer =
                setInterval(
                    function () {

                        convertSeconds++;

                        convertButton.textContent =
                            "変換中 "
                            + convertSeconds
                            + "秒";

                    },
                    1000
                );

            try {

                const startTimeElement =
                    document.getElementById(
                        "start-time"
                    );

                const endTimeElement =
                    document.getElementById(
                        "end-time"
                    );

                const startTime =
                    startTimeElement
                        ? startTimeElement.value.trim()
                        : "";

                const endTime =
                    endTimeElement
                        ? endTimeElement.value.trim()
                        : "";

                // ---------------------------------
                // /convert
                // ---------------------------------

                const response =
                    await fetch(
                        "/convert",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    url: url,

                                    outputs:
                                        outputs,

                                    start_time:
                                        startTime,

                                    end_time:
                                        endTime

                                })
                        }
                    );

                const data =
                    await parseResponse(
                        response
                    );

                // ---------------------------------
                // Job開始成功
                // ---------------------------------

                if (data.success) {

                    currentJobId =
                        data.job_id;

                    if (!currentJobId) {

                        throw new Error(
                            "Job IDが返されませんでした"
                        );

                    }

                    checkStatus();

                }
                else {

                    throw new Error(
                        data.message
                        || "変換を開始できませんでした"
                    );

                }

            }
            catch (error) {

                console.error(
                    "startConvert error:",
                    error
                );

                stopConvertTimer();

                convertButton.disabled =
                    false;

                convertButton.textContent =
                    "変換開始";

                alert(
                    error.message
                    || "変換開始エラー"
                );

            }

        }

        // =====================================
        // 状態確認
        // =====================================

        async function checkStatus() {

            if (!currentJobId) {

                stopConvertTimer();

                if (convertButton) {

                    convertButton.disabled =
                        false;

                    convertButton.textContent =
                        "変換開始";

                }

                return;

            }

            try {

                const response =
                    await fetch(
                        `/status/${encodeURIComponent(currentJobId)}`,
                        {
                            method: "GET",
                            cache: "no-store"
                        }
                    );

                const data =
                    await parseResponse(
                        response
                    );

                console.log(
                    "Job status:",
                    data
                );

                // ---------------------------------
                // 完了
                // ---------------------------------

                if (
                    data.status ===
                    "complete"
                ) {

                    stopConvertTimer();

                    if (convertButton) {

                        convertButton.style.display =
                            "none";

                    }

                    showFiles(
                        data.files || []
                    );

                    return;

                }

                // ---------------------------------
                // エラー
                // ---------------------------------

                if (
                    data.status ===
                    "error"
                ) {

                    stopConvertTimer();

                    if (convertButton) {

                        convertButton.disabled =
                            false;

                        convertButton.textContent =
                            "変換開始";

                    }

                    alert(
                        data.message
                        || "変換中にエラーが発生しました"
                    );

                    return;

                }

                // ---------------------------------
                // queued / running
                // ---------------------------------

                setTimeout(
                    checkStatus,
                    3000
                );

            }
            catch (error) {

                console.error(
                    "checkStatus error:",
                    error
                );

                stopConvertTimer();

                if (convertButton) {

                    convertButton.disabled =
                        false;

                    convertButton.textContent =
                        "変換開始";

                }

                alert(
                    "変換状態の確認に失敗しました。\n\n"
                    + error.message
                );

            }

        }

        // =====================================
        // ダウンロード表示
        // =====================================

        function showFiles(files) {

            console.log(
                "Completed files:",
                files
            );

            if (!downloadArea) {

                return;

            }

            let html = `
                <div class="download-buttons">
            `;

            let mp3File = "";

            // ---------------------------------
            // MP3検索
            // ---------------------------------

            files.forEach(
                function (file) {

                    if (
                        typeof file === "string"
                        && file.toLowerCase().endsWith(".mp3")
                    ) {

                        mp3File = file;

                    }

                }
            );

            // ---------------------------------
            // Gemini用MP3ファイル名
            // ---------------------------------

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );

            if (
                geminiFile
                && mp3File
            ) {

                geminiFile.value =
                    mp3File;

            }

            // ---------------------------------
            // ファイルボタン
            // ---------------------------------

            files.forEach(
                function (file) {

                    if (
                        typeof file !== "string"
                    ) {

                        return;

                    }

                    if (
                        file
                            .toLowerCase()
                            .endsWith(".mp3")
                    ) {

                        html += `

                            <a
                                href="/download/${encodeURIComponent(file)}"
                                download
                            >
                                <button
                                    type="button"
                                    class="download-button"
                                >
                                    mp3
                                </button>
                            </a>

                            <button
                                type="button"
                                id="srt-toggle-button"
                                class="srt-toggle-button"
                            >
                                ▲
                            </button>

                        `;

                    }

                    else if (
                        file
                            .toLowerCase()
                            .endsWith(".mp4")
                    ) {

                        html += `

                            <a
                                href="/download/${encodeURIComponent(file)}"
                                download
                            >
                                <button
                                    type="button"
                                    class="download-button"
                                >
                                    mp4
                                </button>
                            </a>

                        `;

                    }

                }
            );

            html += `
                </div>
            `;

            downloadArea.innerHTML =
                html;

            // =================================
            // SRT表示
            // =================================

            const srtArea =
                document.getElementById(
                    "srtArea"
                );

            if (
                srtArea
                && mp3File
            ) {

                srtArea.style.display =
                    "block";

            }
            else if (srtArea) {

                srtArea.style.display =
                    "none";

            }

            // =================================
            // SRT展開ボタン
            // =================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );

            const srtContent =
                document.getElementById(
                    "srt-content"
                );

            if (
                toggle
                && srtContent
            ) {

                toggle.addEventListener(
                    "click",
                    function () {

                        if (
                            srtContent.style.display ===
                            "none"
                            ||
                            srtContent.style.display ===
                            ""
                        ) {

                            srtContent.style.display =
                                "block";

                            toggle.textContent =
                                "▲";

                        }
                        else {

                            srtContent.style.display =
                                "none";

                            toggle.textContent =
                                "▼";

                        }

                    }
                );

            }

        }

        // =====================================
        // Gemini文字起こし
        // =====================================

        const geminiButton =
            document.getElementById(
                "gemini-button"
            );

        if (geminiButton) {

            geminiButton.addEventListener(
                "click",
                async function () {

                    const geminiFileElement =
                        document.getElementById(
                            "gemini-file"
                        );

                    const file =
                        geminiFileElement
                            ? geminiFileElement.value.trim()
                            : "";

                    if (!file) {

                        alert(
                            "mp3ファイル名がありません"
                        );

                        return;

                    }

                    const result =
                        document.getElementById(
                            "gemini-result"
                        );

                    if (!result) {

                        return;

                    }

                    let seconds = 0;

                    result.style.display =
                        "block";

                    result.textContent =
                        "文字起こし中... 0秒";

                    geminiButton.disabled =
                        true;

                    const timer =
                        setInterval(
                            function () {

                                seconds++;

                                result.textContent =
                                    "文字起こし中... "
                                    + seconds
                                    + "秒";

                            },
                            1000
                        );

                    try {

                        const response =
                            await fetch(
                                "/gemini-transcribe",
                                {
                                    method: "POST",

                                    headers: {
                                        "Content-Type":
                                            "application/json"
                                    },

                                    body:
                                        JSON.stringify({
                                            file: file
                                        })
                                }
                            );

                        const data =
                            await parseResponse(
                                response
                            );

                        clearInterval(
                            timer
                        );

                        geminiButton.disabled =
                            false;

                        if (data.success) {

                            // -------------------------
                            // テキスト非表示
                            // -------------------------

                            result.style.display =
                                "none";

                            // -------------------------
                            // SRTボタン
                            // -------------------------

                            const srtButton =
                                document.createElement(
                                    "a"
                                );

                            srtButton.href =
                                "/download/"
                                +
                                encodeURIComponent(
                                    data.srt_file
                                );

                            srtButton.download =
                                data.srt_file;

                            srtButton.innerHTML = `
                                <button
                                    type="button"
                                    class="download-button"
                                >
                                    srt
                                </button>
                            `;

                            result.parentNode.appendChild(
                                srtButton
                            );

                        }
                        else {

                            result.textContent =
                                data.message
                                || "文字起こしに失敗しました";

                        }

                    }
                    catch (error) {

                        clearInterval(
                            timer
                        );

                        geminiButton.disabled =
                            false;

                        console.error(
                            "Gemini error:",
                            error
                        );

                        result.textContent =
                            "エラー: "
                            + (
                                error.message
                                || "文字起こしに失敗しました"
                            );

                    }

                }
            );

        }

    }
);

