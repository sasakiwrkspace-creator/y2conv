// =====================================
// YouTube Converter JavaScript
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================
        // DOM
        // =====================================

        const urlInput =
            document.getElementById(
                "youtube-url"
            );

        const convertButton =
            document.getElementById(
                "convertBtn"
            );

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );

        const startTimeElement =
            document.getElementById(
                "start-time"
            );

        const endTimeElement =
            document.getElementById(
                "end-time"
            );

        let currentJobId = null;

        let convertSeconds = 0;

        let convertTimer = null;


        // =====================================
        // 数字以外を入力させない
        // =====================================

        function setupNumericInput(element) {

            if (!element) {
                return;
            }


            element.addEventListener(
                "input",
                function () {

                    this.value =
                        this.value.replace(
                            /[^0-9]/g,
                            ""
                        );

                }
            );


            element.addEventListener(
                "keydown",
                function (event) {

                    const allowedKeys = [
                        "Backspace",
                        "Delete",
                        "ArrowLeft",
                        "ArrowRight",
                        "ArrowUp",
                        "ArrowDown",
                        "Tab",
                        "Home",
                        "End"
                    ];


                    if (
                        allowedKeys.includes(
                            event.key
                        )
                    ) {
                        return;
                    }


                    if (
                        event.ctrlKey ||
                        event.metaKey
                    ) {
                        return;
                    }


                    if (
                        !/^[0-9]$/.test(
                            event.key
                        )
                    ) {

                        event.preventDefault();

                    }

                }
            );


            element.setAttribute(
                "inputmode",
                "numeric"
            );


            element.setAttribute(
                "pattern",
                "[0-9]*"
            );

        }


        setupNumericInput(
            startTimeElement
        );

        setupNumericInput(
            endTimeElement
        );


        // =====================================
        // 時間をHH:MM:SSへ変換
        // =====================================

        function makeTime(
            hour,
            minute,
            second
        ) {

            hour =
                hour || "0";

            minute =
                minute || "0";

            second =
                second || "0";


            hour =
                parseInt(
                    hour,
                    10
                ) || 0;


            minute =
                parseInt(
                    minute,
                    10
                ) || 0;


            second =
                parseInt(
                    second,
                    10
                ) || 0;


            return (
                String(hour).padStart(
                    2,
                    "0"
                )
                +
                ":"
                +
                String(minute).padStart(
                    2,
                    "0"
                )
                +
                ":"
                +
                String(second).padStart(
                    2,
                    "0"
                )
            );

        }


        // =====================================
        // 入力された時間を秒へ変換
        // =====================================

        function inputToSeconds(
            element
        ) {

            if (!element) {
                return null;
            }


            const value =
                element.value.trim();


            if (!value) {
                return null;
            }


            const seconds =
                parseInt(
                    value,
                    10
                );


            if (
                Number.isNaN(
                    seconds
                )
            ) {
                return null;
            }


            return seconds;

        }


        // =====================================
        // 時間入力を検証
        //
        // 現在のUIでは
        //
        // [00]時 [00]分 [00]秒
        //
        // それぞれのinputを想定。
        //
        // ただし、既存HTMLが1つのinputの場合も
        // 可能な限り対応する。
        // =====================================

        function getTimeValue(
            prefix
        ) {

            const hour =
                document.getElementById(
                    prefix + "-hour"
                );

            const minute =
                document.getElementById(
                    prefix + "-minute"
                );

            const second =
                document.getElementById(
                    prefix + "-second"
                );


            // ---------------------------------
            // 新UI
            // ---------------------------------

            if (
                hour ||
                minute ||
                second
            ) {

                const h =
                    hour
                        ? hour.value.trim()
                        : "";

                const m =
                    minute
                        ? minute.value.trim()
                        : "";

                const s =
                    second
                        ? second.value.trim()
                        : "";


                if (
                    !h &&
                    !m &&
                    !s
                ) {

                    return "";

                }


                return makeTime(
                    h,
                    m,
                    s
                );

            }


            // ---------------------------------
            // 旧UI
            // start-time / end-time
            // ---------------------------------

            const element =
                document.getElementById(
                    prefix
                );


            if (!element) {
                return "";
            }


            const value =
                element.value.trim();


            if (!value) {
                return "";
            }


            return value;

        }


        // =====================================
        // 時間範囲取得
        // =====================================

        function getTimeRange() {

            let startTime =
                getTimeValue(
                    "start-time"
                );


            let endTime =
                getTimeValue(
                    "end-time"
                );


            // =================================
            // 左だけ入力
            // → 開始～最後
            // =================================

            if (
                startTime &&
                !endTime
            ) {

                return {

                    start_time:
                        startTime,

                    end_time:
                        ""

                };

            }


            // =================================
            // 右だけ入力
            // → 00:00:00～終了
            // =================================

            if (
                !startTime &&
                endTime
            ) {

                startTime =
                    "00:00:00";


                return {

                    start_time:
                        startTime,

                    end_time:
                        endTime

                };

            }


            // =================================
            // 両方空欄
            // → カットなし
            // =================================

            if (
                !startTime &&
                !endTime
            ) {

                return {

                    start_time:
                        "",

                    end_time:
                        ""

                };

            }


            // =================================
            // 両方入力
            // =================================

            return {

                start_time:
                    startTime,

                end_time:
                    endTime

            };

        }


        // =====================================
        // URL + 実行
        // =====================================

        if (convertButton) {

            convertButton.addEventListener(
                "click",
                startConvert
            );

        }


        // =====================================
        // Enterキー
        // =====================================

        if (urlInput) {

            urlInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();

                        startConvert();

                    }

                }
            );

        }


        // =====================================
        // 変換開始
        // =====================================

        async function startConvert() {

            const url =
                urlInput
                    ? urlInput.value.trim()
                    : "";


            if (!url) {

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }


            // =================================
            // 時間範囲
            // =================================

            const timeRange =
                getTimeRange();


            console.log(
                "開始時間:",
                timeRange.start_time
            );


            console.log(
                "終了時間:",
                timeRange.end_time
            );


            // =================================
            // ボタン状態
            // =================================

            if (convertButton) {

                convertButton.disabled =
                    true;

                convertButton.textContent =
                    "変換中 0秒";

            }


            convertSeconds = 0;


            if (convertTimer) {

                clearInterval(
                    convertTimer
                );

            }


            convertTimer =
                setInterval(
                    function () {

                        convertSeconds++;


                        if (convertButton) {

                            convertButton.textContent =
                                "変換中 "
                                +
                                convertSeconds
                                +
                                "秒";

                        }

                    },
                    1000
                );


            // =================================
            // 以前の結果を消す
            // =================================

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }


            // =================================
            // Gemini部分を隠す
            // =================================

            hideGeminiArea();


            try {

                // =================================
                // /convert
                // =================================

                const response =
                    await fetch(
                        "/convert",
                        {

                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    url:
                                        url,

                                    outputs:
                                        ["mp3"],

                                    start_time:
                                        timeRange.start_time,

                                    end_time:
                                        timeRange.end_time

                                })

                        }
                    );


                // =================================
                // HTTPエラー
                // =================================

                if (!response.ok) {

                    const text =
                        await response.text();


                    console.error(
                        "変換HTTPエラー:",
                        response.status,
                        text
                    );


                    throw new Error(
                        "HTTP "
                        +
                        response.status
                        +
                        " : "
                        +
                        (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )
                    );

                }


                // =================================
                // レスポンス
                // =================================

                const text =
                    await response.text();


                if (!text) {

                    throw new Error(
                        "サーバーから空のレスポンスが返されました"
                    );

                }


                let data;


                try {

                    data =
                        JSON.parse(
                            text
                        );

                }
                catch (jsonError) {

                    console.error(
                        "変換JSON解析エラー:",
                        jsonError
                    );


                    console.error(
                        "サーバーレスポンス:",
                        text
                    );


                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }


                // =================================
                // JOB開始
                // =================================

                if (data.success) {

                    currentJobId =
                        data.job_id;


                    console.log(
                        "変換JOB:",
                        currentJobId
                    );


                    checkStatus();

                }
                else {

                    throw new Error(
                        data.message ||
                        "変換開始に失敗しました"
                    );

                }

            }
            catch (error) {

                stopConvertTimer();


                if (convertButton) {

                    convertButton.disabled =
                        false;

                    convertButton.textContent =
                        "実行";

                }


                console.error(
                    "変換開始エラー:",
                    error
                );


                alert(
                    error.message
                );

            }

        }


        // =====================================
        // タイマー停止
        // =====================================

        function stopConvertTimer() {

            if (convertTimer) {

                clearInterval(
                    convertTimer
                );

                convertTimer =
                    null;

            }

        }


        // =====================================
        // STATUS確認
        // =====================================

        async function checkStatus() {

            if (!currentJobId) {

                console.error(
                    "JOB IDがありません"
                );

                return;

            }


            try {

                const response =
                    await fetch(
                        `/status/${encodeURIComponent(currentJobId)}`,
                        {

                            method:
                                "GET",

                            cache:
                                "no-store"

                        }
                    );


                // =================================
                // 502 / 503 / 504
                // =================================

                if (!response.ok) {

                    const text =
                        await response.text();


                    console.error(
                        "ステータスHTTPエラー:",
                        response.status,
                        text
                    );


                    if (
                        response.status === 502 ||
                        response.status === 503 ||
                        response.status === 504
                    ) {

                        console.warn(
                            "一時的なサーバーエラー。"
                            +
                            "3秒後に再試行します。"
                        );


                        setTimeout(
                            checkStatus,
                            3000
                        );


                        return;

                    }


                    throw new Error(
                        "HTTP "
                        +
                        response.status
                        +
                        " : "
                        +
                        (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )
                    );

                }


                // =================================
                // レスポンス
                // =================================

                const text =
                    await response.text();


                if (!text) {

                    console.warn(
                        "STATUSレスポンスが空です。"
                        +
                        "3秒後に再試行します。"
                    );


                    setTimeout(
                        checkStatus,
                        3000
                    );


                    return;

                }


                let data;


                try {

                    data =
                        JSON.parse(
                            text
                        );

                }
                catch (jsonError) {

                    console.error(
                        "STATUS JSON解析エラー:",
                        jsonError
                    );


                    setTimeout(
                        checkStatus,
                        3000
                    );


                    return;

                }


                console.log(
                    "STATUS:",
                    data
                );


                // =================================
                // 完了
                // =================================

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
                        Array.isArray(
                            data.files
                        )
                            ? data.files
                            : []
                    );


                    return;

                }


                // =================================
                // エラー
                // =================================

                if (
                    data.status ===
                    "error"
                ) {

                    stopConvertTimer();


                    if (convertButton) {

                        convertButton.disabled =
                            false;

                        convertButton.textContent =
                            "実行";

                    }


                    alert(
                        data.message ||
                        "変換中にエラーが発生しました"
                    );


                    return;

                }


                // =================================
                // queued / running
                // =================================

                setTimeout(
                    checkStatus,
                    3000
                );

            }
            catch (error) {

                console.error(
                    "変換状態確認エラー:",
                    error
                );


                setTimeout(
                    checkStatus,
                    3000
                );

            }

        }


        // =====================================
        // Gemini領域を隠す
        // =====================================

        function hideGeminiArea() {

            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if (srtArea) {

                srtArea.style.display =
                    "none";

            }


            const srtContent =
                document.getElementById(
                    "srt-content"
                );


            if (srtContent) {

                srtContent.style.display =
                    "none";

            }

        }


        // =====================================
        // 完成ファイル表示
        // =====================================

        function showFiles(files) {

            console.log(
                "完成ファイル:",
                files
            );


            if (!downloadArea) {
                return;
            }


            let mp3File =
                "";


            // =================================
            // MP3検索
            // =================================

            files.forEach(
                function (file) {

                    if (
                        file
                            .toLowerCase()
                            .endsWith(
                                ".mp3"
                            )
                    ) {

                        mp3File =
                            file;

                    }

                }
            );


            // =================================
            // MP3がない
            // =================================

            if (!mp3File) {

                downloadArea.innerHTML = `
                    <div class="download-error">
                        MP3ファイルが作成されませんでした。
                    </div>
                `;

                return;

            }


            // =================================
            // Gemini対象ファイル
            // =================================

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );


            if (
                geminiFile
            ) {

                geminiFile.value =
                    mp3File;

            }


            // =================================
            // MP3表示
            // =================================

            downloadArea.innerHTML = `

                <div class="download-buttons">

                    <div class="mp3-download-row">

                        <span class="download-label">
                            MP3のダウンロード
                        </span>

                        <a
                            href="/download/${encodeURIComponent(mp3File)}"
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
                            aria-expanded="false"
                        >
                            ▼
                        </button>

                    </div>

                </div>

            `;


            // =================================
            // Gemini領域
            // 初期状態では非表示
            // =================================

            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if (srtArea) {

                srtArea.style.display =
                    "none";

            }


            const srtContent =
                document.getElementById(
                    "srt-content"
                );


            if (srtContent) {

                srtContent.style.display =
                    "none";

            }


            // =================================
            // ▼ボタン
            // =================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );


            if (
                toggle &&
                srtArea
            ) {

                toggle.addEventListener(
                    "click",
                    function () {

                        const isHidden =
                            srtArea.style.display ===
                            "none";


                        if (isHidden) {

                            srtArea.style.display =
                                "block";


                            if (srtContent) {

                                srtContent.style.display =
                                    "block";

                            }


                            toggle.textContent =
                                "▲";


                            toggle.setAttribute(
                                "aria-expanded",
                                "true"
                            );

                        }
                        else {

                            srtArea.style.display =
                                "none";


                            toggle.textContent =
                                "▼";


                            toggle.setAttribute(
                                "aria-expanded",
                                "false"
                            );

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
                startGemini
            );

        }


        // =====================================
        // Gemini開始
        // =====================================

        async function startGemini() {

            const geminiFileElement =
                document.getElementById(
                    "gemini-file"
                );


            const result =
                document.getElementById(
                    "gemini-result"
                );


            const file =
                geminiFileElement
                    ? geminiFileElement.value.trim()
                    : "";


            if (!file) {

                alert(
                    "MP3ファイルがありません"
                );

                return;

            }


            // =================================
            // 二重実行防止
            // =================================

            geminiButton.disabled =
                true;


            geminiButton.textContent =
                "文字起こし中...";


            let seconds = 0;


            if (result) {

                result.style.display =
                    "block";


                result.textContent =
                    "文字起こし中... 0秒";

            }


            const timer =
                setInterval(
                    function () {

                        seconds++;


                        if (result) {

                            result.textContent =
                                "文字起こし中... "
                                +
                                seconds
                                +
                                "秒";

                        }

                    },
                    1000
                );


            try {

                // =================================
                // Gemini API
                // =================================

                const response =
                    await fetch(
                        "/gemini-transcribe",
                        {

                            method:
                                "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    file:
                                        file

                                })

                        }
                    );


                // =================================
                // HTTPエラー
                // =================================

                if (!response.ok) {

                    const text =
                        await response.text();


                    throw new Error(
                        "HTTP "
                        +
                        response.status
                        +
                        " : "
                        +
                        (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )
                    );

                }


                // =================================
                // JSON
                // =================================

                const text =
                    await response.text();


                if (!text) {

                    throw new Error(
                        "サーバーから空のレスポンスが返されました"
                    );

                }


                let data;


                try {

                    data =
                        JSON.parse(
                            text
                        );

                }
                catch (jsonError) {

                    console.error(
                        "Gemini JSON解析エラー:",
                        jsonError
                    );


                    console.error(
                        "Geminiレスポンス:",
                        text
                    );


                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }


                clearInterval(
                    timer
                );


                // =================================
                // 成功
                // =================================

                if (
                    data.success
                ) {

                    if (result) {

                        result.style.display =
                            "none";

                    }


                    geminiButton.style.display =
                        "none";


                    const srtDownloadArea =
                        document.getElementById(
                            "srt-download-area"
                        );


                    if (
                        srtDownloadArea
                    ) {

                        srtDownloadArea.innerHTML = `

                            <div class="srt-download-row">

                                <span>
                                    SRTダウンロード
                                </span>

                                <a
                                    href="/download/${encodeURIComponent(data.srt_file)}"
                                    download
                                >

                                    <button
                                        type="button"
                                        class="download-button"
                                    >
                                        srt
                                    </button>

                                </a>

                            </div>

                        `;

                    }
                    else {

                        const newArea =
                            document.createElement(
                                "div"
                            );


                        newArea.id =
                            "srt-download-area";


                        newArea.innerHTML = `

                            <div class="srt-download-row">

                                <span>
                                    SRTダウンロード
                                </span>

                                <a
                                    href="/download/${encodeURIComponent(data.srt_file)}"
                                    download
                                >

                                    <button
                                        type="button"
                                        class="download-button"
                                    >
                                        srt
                                    </button>

                                </a>

                            </div>

                        `;


                        geminiButton.parentNode.appendChild(
                            newArea
                        );

                    }

                }
                else {

                    geminiButton.disabled =
                        false;


                    geminiButton.textContent =
                        "文字変換";


                    if (result) {

                        result.textContent =
                            data.message ||
                            "文字起こしに失敗しました";

                    }

                }

            }
            catch (error) {

                clearInterval(
                    timer
                );


                console.error(
                    "Geminiエラー:",
                    error
                );


                geminiButton.disabled =
                    false;


                geminiButton.textContent =
                    "文字変換";


                if (result) {

                    result.textContent =
                        "エラー: "
                        +
                        error.message;

                }

            }

        }

    }
);
