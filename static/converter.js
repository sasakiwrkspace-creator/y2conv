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
            document.getElementById("youtube-url");

        const convertButton =
            document.getElementById("convertBtn");

        const downloadArea =
            document.getElementById("downloadArea");

        let currentJobId = null;

        let convertSeconds = 0;

        let convertTimer = null;

        let convertStartTime = null;

        let convertEndTime = null;

        let currentVideoTitle = "";

        let currentVideoDuration = "";

        let currentMp3File = "";



        // =====================================
        // 数字入力
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



        // =====================================
        // 時間入力設定
        // =====================================

        setupNumericInput(
            document.getElementById(
                "start-hour"
            )
        );

        setupNumericInput(
            document.getElementById(
                "start-minute"
            )
        );

        setupNumericInput(
            document.getElementById(
                "start-second"
            )
        );

        setupNumericInput(
            document.getElementById(
                "end-hour"
            )
        );

        setupNumericInput(
            document.getElementById(
                "end-minute"
            )
        );

        setupNumericInput(
            document.getElementById(
                "end-second"
            )
        );



        // =====================================
        // 時間を HH:MM:SS にする
        // =====================================

        function makeTime(
            hour,
            minute,
            second
        ) {

            hour =
                parseInt(
                    hour || "0",
                    10
                ) || 0;


            minute =
                parseInt(
                    minute || "0",
                    10
                ) || 0;


            second =
                parseInt(
                    second || "0",
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
        // 時間取得
        // =====================================

        function getTimeValue(prefix) {

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
            // 旧UIにも対応
            // ---------------------------------

            const element =
                document.getElementById(
                    prefix
                );


            if (!element) {
                return "";
            }


            return element.value.trim();

        }



        // =====================================
        // 時間範囲
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


            if (
                !startTime &&
                endTime
            ) {

                return {

                    start_time:
                        "00:00:00",

                    end_time:
                        endTime

                };

            }


            return {

                start_time:
                    startTime,

                end_time:
                    endTime

            };

        }



        // =====================================
        // 時刻表示
        // =====================================

        function formatClock(date) {

            if (!date) {
                return "";
            }


            return date.toLocaleTimeString(
                "ja-JP",
                {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: false
                }
            );

        }



        // =====================================
        // 経過時間表示
        // =====================================

        function formatElapsed(seconds) {

            const minutes =
                Math.floor(
                    seconds / 60
                );


            const remainSeconds =
                seconds % 60;


            if (minutes === 0) {

                return (
                    remainSeconds +
                    "秒"
                );

            }


            return (
                minutes +
                "分" +
                remainSeconds +
                "秒"
            );

        }



        // =====================================
        // 変換ボタン表示
        // =====================================

        function showConvertingState() {

            if (!convertButton) {
                return;
            }


            // <br>を使わずHTML要素で2行表示
            convertButton.innerHTML = `
                <span class="converting-text">
                    <span>変換中</span>
                    <span>${convertSeconds}秒</span>
                </span>
            `;

        }



        // =====================================
        // 変換タイマー
        // =====================================

        function startConvertTimer() {

            convertSeconds = 0;

            convertStartTime =
                new Date();


            if (convertTimer) {

                clearInterval(
                    convertTimer
                );

            }


            showConvertingState();


            convertTimer =
                setInterval(
                    function () {

                        convertSeconds++;

                        showConvertingState();

                    },
                    1000
                );

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


            convertEndTime =
                new Date();

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
        // Enter
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


            // ---------------------------------
            // 初期化
            // ---------------------------------

            currentJobId =
                null;

            currentVideoTitle =
                "";

            currentVideoDuration =
                "";

            currentMp3File =
                "";


            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }


            hideGeminiArea();


            // ---------------------------------
            // ボタン
            // ---------------------------------

            if (convertButton) {

                convertButton.disabled =
                    true;

            }


            startConvertTimer();



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
                catch (error) {

                    console.error(
                        "JSON解析エラー:",
                        error
                    );


                    console.error(
                        "レスポンス:",
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


                    // サーバーが返す場合に取得
                    currentVideoTitle =
                        data.title ||
                        data.video_title ||
                        "";


                    currentVideoDuration =
                        data.duration ||
                        data.video_duration ||
                        "";


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

                    convertButton.innerHTML =
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
        // STATUS確認
        // =====================================

        async function checkStatus() {

            if (!currentJobId) {
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


                if (!response.ok) {

                    const text =
                        await response.text();


                    if (
                        response.status === 502 ||
                        response.status === 503 ||
                        response.status === 504
                    ) {

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
                        text
                    );

                }


                const text =
                    await response.text();


                if (!text) {

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
                catch (error) {

                    console.error(
                        "STATUS JSON解析エラー:",
                        error
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


                    // STATUSから情報を取得
                    currentVideoTitle =
                        data.title ||
                        data.video_title ||
                        currentVideoTitle;


                    currentVideoDuration =
                        data.duration ||
                        data.video_duration ||
                        currentVideoDuration;


                    if (convertButton) {

                        convertButton.style.display =
                            "none";

                    }


                    showFiles(
                        Array.isArray(
                            data.files
                        )
                            ? data.files
                            : [],
                        data
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

                        convertButton.innerHTML =
                            "実行";

                    }


                    alert(
                        data.message ||
                        "変換中にエラーが発生しました"
                    );


                    return;

                }



                // =================================
                // 実行中
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
        // 変換情報HTML
        // =====================================

        function createConversionInfo(
            type,
            data
        ) {

            const title =
                data.title ||
                data.video_title ||
                currentVideoTitle ||
                "不明";


            const duration =
                data.duration ||
                data.video_duration ||
                currentVideoDuration ||
                "不明";


            const start =
                convertStartTime
                    ? formatClock(
                        convertStartTime
                    )
                    : "";


            const end =
                convertEndTime
                    ? formatClock(
                        convertEndTime
                    )
                    : "";


            return `
                <div class="conversion-info">

                    <div class="conversion-info-title">
                        【${type}変換】
                    </div>

                    <div>
                        タイトル：${escapeHtml(title)}
                    </div>

                    <div>
                        再生時間：${escapeHtml(
                            String(duration)
                        )}
                    </div>

                    <div>
                        実行開始：${start}
                    </div>

                    <div>
                        実行終了：${end}
                        （${formatElapsed(
                            convertSeconds
                        )}）
                    </div>

                </div>
            `;

        }



        // =====================================
        // HTMLエスケープ
        // =====================================

        function escapeHtml(value) {

            return String(value)
                .replace(
                    /&/g,
                    "&amp;"
                )
                .replace(
                    /</g,
                    "&lt;"
                )
                .replace(
                    />/g,
                    "&gt;"
                )
                .replace(
                    /"/g,
                    "&quot;"
                )
                .replace(
                    /'/g,
                    "&#039;"
                );

        }



        // =====================================
        // 完成ファイル表示
        // =====================================

        function showFiles(
            files,
            data
        ) {

            if (!downloadArea) {
                return;
            }


            let mp3File =
                "";


            files.forEach(
                function (file) {

                    if (
                        typeof file === "string" &&
                        file
                            .toLowerCase()
                            .endsWith(".mp3")
                    ) {

                        mp3File =
                            file;

                    }

                }
            );


            if (!mp3File) {

                downloadArea.innerHTML = `
                    <div class="download-error">
                        MP3ファイルが作成されませんでした。
                    </div>
                `;

                return;

            }


            currentMp3File =
                mp3File;



            // =================================
            // Gemini対象ファイル
            // =================================

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );


            if (geminiFile) {

                geminiFile.value =
                    mp3File;

            }



            // =================================
            // MP3表示
            // =================================

            downloadArea.innerHTML = `

                ${createConversionInfo(
                    "MP3",
                    data || {}
                )}

                <div class="download-section">

                    <div class="download-label">
                        MP3のダウンロード
                    </div>

                    <div class="mp3-button-row">

                        <a
                            href="/download/${encodeURIComponent(mp3File)}"
                            download
                            class="download-button"
                        >
                            mp3
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
        // Geminiボタン
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
                catch (error) {

                    console.error(
                        "Gemini JSON解析エラー:",
                        error
                    );


                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }


                clearInterval(
                    timer
                );



                // =================================
                // Gemini成功
                // =================================

                if (data.success) {

                    if (result) {

                        result.style.display =
                            "none";

                    }


                    geminiButton.style.display =
                        "none";


                    showSrtDownload(
                        data
                    );

                }
                else {

                    geminiButton.disabled =
                        false;


                    geminiButton.textContent =
                        "文字変換";


                    if (result) {

                        result.style.display =
                            "block";


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

                    result.style.display =
                        "block";


                    result.textContent =
                        "エラー: "
                        +
                        error.message;

                }

            }

        }



        // =====================================
        // SRTダウンロード表示
        // =====================================

        function showSrtDownload(data) {

            const srtFile =
                data.srt_file ||
                "";


            if (!srtFile) {

                return;

            }


            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if (!srtArea) {

                return;

            }


            // ---------------------------------
            // SRT変換時間
            // ---------------------------------

            const srtStart =
                new Date();


            const srtEnd =
                new Date();


            // Gemini処理時間も表示
            // data.seconds があれば使用
            const srtSeconds =
                Number(
                    data.seconds ||
                    data.elapsed_seconds ||
                    0
                );


            const title =
                data.title ||
                data.video_title ||
                currentVideoTitle ||
                "不明";


            const duration =
                data.duration ||
                data.video_duration ||
                currentVideoDuration ||
                "不明";


            const srtInfo = `

                <div class="conversion-info">

                    <div class="conversion-info-title">
                        【SRT変換】
                    </div>

                    <div>
                        タイトル：${escapeHtml(title)}
                    </div>

                    <div>
                        再生時間：${escapeHtml(
                            String(duration)
                        )}
                    </div>

                    <div>
                        実行開始：
                        ${formatClock(srtStart)}
                    </div>

                    <div>
                        実行終了：
                        ${formatClock(srtEnd)}
                        （${formatElapsed(
                            srtSeconds
                        )}）
                    </div>

                </div>

            `;


            const downloadHtml = `

                ${srtInfo}

                <div class="srt-download-section">

                    <div class="download-label">
                        SRTダウンロード
                    </div>

                    <div class="srt-button-row">

                        <a
                            href="/download/${encodeURIComponent(srtFile)}"
                            download
                            class="download-button"
                        >
                            srt
                        </a>

                    </div>

                </div>

            `;


            // =================================
            // srt-download-areaがある場合
            // =================================

            let srtDownloadArea =
                document.getElementById(
                    "srt-download-area"
                );


            if (!srtDownloadArea) {

                srtDownloadArea =
                    document.createElement(
                        "div"
                    );


                srtDownloadArea.id =
                    "srt-download-area";


                srtArea.appendChild(
                    srtDownloadArea
                );

            }


            srtDownloadArea.innerHTML =
                downloadHtml;


            srtArea.style.display =
                "block";



            const srtContent =
                document.getElementById(
                    "srt-content"
                );


            if (srtContent) {

                srtContent.style.display =
                    "block";

            }



            // =================================
            // ▼ボタンを▲へ
            // =================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );


            if (toggle) {

                toggle.textContent =
                    "▲";


                toggle.setAttribute(
                    "aria-expanded",
                    "true"
                );

            }

        }

    }
);
