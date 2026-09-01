// =====================================
// YouTube Converter
// converter.js
//
// タブ1：YouTube変換専用
//
// 役割:
// ・YouTube URL受付
// ・MP3 / MP4 変換API実行
// ・job_idによる処理状況監視
// ・MP3 / MP4ダウンロード表示
// ・処理詳細表示
//
// 注意:
// ・converterUtils.js は使用しない
// ・converterStatus.js は使用しない
// ・タブ2の処理には触れない
// ・タブ1の実行ボタンは #convertBtn
//
// ステータス構成:
// ・#conversion-status-area
//      → 上側。タイトルのみ
//
// ・#conversion-details-area
//      → 下側。詳細情報。折り畳み可能
//
// ・#downloadArea
//      → ダウンロードボタン専用
// =====================================


(function () {

    "use strict";


    // =====================================
    // 初期化
    // =====================================

    function initializeConverter() {

        console.log(
            "[CONVERTER] 初期化開始"
        );


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


        // =====================================
        // 上側ステータス
        //
        // タイトルのみ表示
        // =====================================

        const conversionStatusArea =
            document.getElementById(
                "conversion-status-area"
            );


        // =====================================
        // 下側詳細ステータス
        // =====================================

        const conversionDetailsArea =
            document.getElementById(
                "conversion-details-area"
            );


        const conversionDetailsContent =
            document.getElementById(
                "conversion-details-content"
            );


        // =====================================
        // ダウンロード
        // =====================================

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );


        console.log(
            "[CONVERTER] youtube-url:",
            urlInput
        );


        console.log(
            "[CONVERTER] convertBtn:",
            convertButton
        );


        console.log(
            "[CONVERTER] conversion-status-area:",
            conversionStatusArea
        );


        console.log(
            "[CONVERTER] conversion-details-area:",
            conversionDetailsArea
        );


        console.log(
            "[CONVERTER] conversion-details-content:",
            conversionDetailsContent
        );


        console.log(
            "[CONVERTER] downloadArea:",
            downloadArea
        );


        // =====================================
        // 必須DOM
        // =====================================

        if (!urlInput) {

            console.error(
                "[CONVERTER] #youtube-url が見つかりません"
            );

            return;

        }


        if (!convertButton) {

            console.error(
                "[CONVERTER] #convertBtn が見つかりません"
            );

            return;

        }


        if (!conversionStatusArea) {

            console.warn(
                "[CONVERTER] #conversion-status-area が見つかりません"
            );

        }


        if (!conversionDetailsArea) {

            console.warn(
                "[CONVERTER] #conversion-details-area が見つかりません"
            );

        }


        if (!conversionDetailsContent) {

            console.warn(
                "[CONVERTER] #conversion-details-content が見つかりません"
            );

        }


        // =====================================
        // State
        // =====================================

        const converterState = {

            currentVideoTitle:
                "",

            currentVideoDuration:
                "",

            currentVideoUrl:
                "",

            currentMp3File:
                "",

            currentMp4File:
                "",

            currentJobId:
                "",

            currentJobStatus:
                "",

            currentJob:
                null,

            isProcessing:
                false

        };


        window.converterState =
            converterState;


        // =====================================
        // 上側ステータス
        //
        // 原則としてタイトルだけ表示。
        // =====================================

        function setTitleStatus(
            title
        ) {

            const text =
                String(
                    title || ""
                );


            if (conversionStatusArea) {

                if (text) {

                    conversionStatusArea.textContent =
                        "タイトル： " +
                        text;

                    conversionStatusArea.style.display =
                        "block";

                    conversionStatusArea.style.color =
                        "#222";

                }
                else {

                    conversionStatusArea.textContent =
                        "";

                    conversionStatusArea.style.display =
                        "none";

                }


                conversionStatusArea.style.whiteSpace =
                    "pre-line";

            }


            console.log(
                "[CONVERTER] TITLE:",
                text
            );

        }


        // =====================================
        // エラー表示
        //
        // 正常終了時は使用しない。
        // =====================================

        function setErrorStatus(
            message
        ) {

            const text =
                String(
                    message || ""
                );


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    text;

                conversionStatusArea.style.display =
                    text
                        ? "block"
                        : "none";

                conversionStatusArea.style.color =
                    "#c00";

                conversionStatusArea.style.whiteSpace =
                    "pre-line";

            }


            console.log(
                "[CONVERTER] ERROR STATUS:",
                text
            );

        }


        // =====================================
        // HTMLエスケープ
        // =====================================

        function escapeHtml(
            value
        ) {

            const div =
                document.createElement(
                    "div"
                );


            div.textContent =
                String(
                    value ?? ""
                );


            return div.innerHTML;

        }


        // =====================================
        // 時計
        // =====================================

        function formatClock(
            date
        ) {

            const hours =
                String(
                    date.getHours()
                ).padStart(
                    2,
                    "0"
                );


            const minutes =
                String(
                    date.getMinutes()
                ).padStart(
                    2,
                    "0"
                );


            const seconds =
                String(
                    date.getSeconds()
                ).padStart(
                    2,
                    "0"
                );


            return (
                hours +
                ":" +
                minutes +
                ":" +
                seconds
            );

        }


        // =====================================
        // 経過時間
        // =====================================

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


            return (
                secs +
                "秒"
            );

        }


        // =====================================
        // 再生時間
        // =====================================

        function formatDuration(
            duration
        ) {

            if (
                duration === null ||
                duration === undefined ||
                duration === ""
            ) {

                return "不明";

            }


            const total =
                Math.max(
                    0,
                    Math.floor(
                        Number(duration) || 0
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


            const seconds =
                total % 60;


            if (hours > 0) {

                return (
                    String(hours).padStart(
                        2,
                        "0"
                    ) +
                    ":" +
                    String(minutes).padStart(
                        2,
                        "0"
                    ) +
                    ":" +
                    String(seconds).padStart(
                        2,
                        "0"
                    )
                );

            }


            return (
                String(minutes).padStart(
                    2,
                    "0"
                ) +
                ":" +
                String(seconds).padStart(
                    2,
                    "0"
                )
            );

        }


        // =====================================
        // 時間入力取得
        // =====================================

        function getTimeValue(
            hourId,
            minuteId,
            secondId
        ) {

            const hourInput =
                document.getElementById(
                    hourId
                );


            const minuteInput =
                document.getElementById(
                    minuteId
                );


            const secondInput =
                document.getElementById(
                    secondId
                );


            const hour =
                hourInput
                    ? hourInput.value.trim()
                    : "";


            const minute =
                minuteInput
                    ? minuteInput.value.trim()
                    : "";


            const second =
                secondInput
                    ? secondInput.value.trim()
                    : "";


            if (
                !hour &&
                !minute &&
                !second
            ) {

                return null;

            }


            const h =
                Number(
                    hour || 0
                );


            const m =
                Number(
                    minute || 0
                );


            const s =
                Number(
                    second || 0
                );


            if (
                !Number.isFinite(h) ||
                !Number.isFinite(m) ||
                !Number.isFinite(s)
            ) {

                return null;

            }


            return (
                h * 3600 +
                m * 60 +
                s
            );

        }


        // =====================================
        // 時間範囲
        // =====================================

        function getTimeRange() {

            const start =
                getTimeValue(
                    "start-hour",
                    "start-minute",
                    "start-second"
                );


            const end =
                getTimeValue(
                    "end-hour",
                    "end-minute",
                    "end-second"
                );


            console.log(
                "[CONVERTER] 時間範囲:",
                {
                    start:
                        start,

                    end:
                        end
                }
            );


            return {

                start_time:
                    start,

                end_time:
                    end

            };

        }


        // =====================================
        // 出力形式
        // =====================================

        function getSelectedOutputs() {

            const checked =
                document.querySelectorAll(
                    'input[name="output-format"]:checked'
                );


            const outputs =
                [];


            checked.forEach(
                function (input) {

                    const value =
                        String(
                            input.value || ""
                        ).toLowerCase();


                    if (
                        value === "mp3"
                    ) {

                        outputs.push(
                            "mp3"
                        );

                    }
                    else if (
                        value === "mp4"
                    ) {

                        outputs.push(
                            "mp4"
                        );

                    }
                    else if (
                        value === "subtitle_mp4"
                    ) {

                        outputs.push(
                            "mp4"
                        );

                    }

                }
            );


            return [
                ...new Set(
                    outputs
                )
            ];

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


            return (
                "/download/" +
                encodeURIComponent(
                    String(filename)
                )
            );

        }


        // =====================================
        // ダウンロードボタン
        //
        // ここにはボタンだけを追加する。
        // ステータス情報は追加しない。
        // =====================================

        function addDownloadButton(
            filename,
            type
        ) {

            if (!downloadArea) {

                console.warn(
                    "[CONVERTER] #downloadArea がありません"
                );

                return;

            }


            if (!filename) {

                return;

            }


            const safeFilename =
                String(
                    filename
                );


            const existing =
                Array.from(
                    downloadArea.querySelectorAll(
                        "[data-filename]"
                    )
                ).find(
                    function (element) {

                        return (
                            element.dataset.filename ===
                            safeFilename
                        );

                    }
                );


            if (existing) {

                return;

            }


            const link =
                document.createElement(
                    "a"
                );


            link.href =
                makeDownloadUrl(
                    safeFilename
                );


            link.download =
                safeFilename;


            link.className =
                "download-button";


            link.dataset.filename =
                safeFilename;


            link.textContent =
                "[" +
                String(type).toUpperCase() +
                "]";


            downloadArea.appendChild(
                link
            );


            console.log(
                "[CONVERTER] ダウンロードボタン追加:",
                {
                    filename:
                        safeFilename,

                    type:
                        type
                }
            );

        }


        // =====================================
        // 結果クリア
        // =====================================

        function clearResults() {

            // ---------------------------------
            // ダウンロード
            // ---------------------------------

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }


            // ---------------------------------
            // 上側ステータス
            // ---------------------------------

            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    "";

                conversionStatusArea.style.display =
                    "none";

                conversionStatusArea.style.color =
                    "#222";

            }


            // ---------------------------------
            // 下側詳細
            // ---------------------------------

            if (conversionDetailsContent) {

                conversionDetailsContent.innerHTML =
                    "";

            }


            if (conversionDetailsArea) {

                // 新しい処理開始時は閉じる
                conversionDetailsArea.open =
                    false;

                conversionDetailsArea.style.display =
                    "none";

            }


            // ---------------------------------
            // State
            // ---------------------------------

            converterState.currentVideoTitle =
                "";


            converterState.currentVideoDuration =
                "";


            converterState.currentMp3File =
                "";


            converterState.currentMp4File =
                "";


            converterState.currentJobId =
                "";


            converterState.currentJobStatus =
                "";


            converterState.currentJob =
                null;

        }


        // =====================================
        // HTTPレスポンスJSON取得
        // =====================================

        async function readJsonResponse(
            response
        ) {

            const text =
                await response.text();


            console.log(
                "[CONVERTER] HTTP:",
                response.status
            );


            console.log(
                "[CONVERTER] RESPONSE:",
                text
            );


            let data;


            try {

                data =
                    text
                        ? JSON.parse(text)
                        : null;

            }
            catch (error) {

                throw new Error(

                    "サーバーからJSONではない応答が返されました。" +
                    "\nHTTP " +
                    response.status +
                    "\n" +
                    text.substring(
                        0,
                        500
                    )

                );

            }


            if (!data) {

                throw new Error(
                    "サーバーから空の応答が返されました。"
                );

            }


            return data;

        }


        // =====================================
        // 動画情報取得
        // =====================================

        async function getVideoInfo(
            url
        ) {

            console.log(
                "[CONVERTER] /video-info 開始"
            );


            const response =
                await fetch(
                    "/video-info",
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
                                    url

                            })

                    }
                );


            const data =
                await readJsonResponse(
                    response
                );


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(

                    data.message ||
                    "動画情報の取得に失敗しました。"

                );

            }


            return data;

        }


        // =====================================
        // 変換API
        // =====================================

        async function convertVideo(
            url,
            outputs,
            timeRange
        ) {

            const requestBody = {

                url:
                    url,

                outputs:
                    outputs,

                start_time:
                    timeRange.start_time,

                end_time:
                    timeRange.end_time

            };


            console.log(
                "[CONVERTER] /convert request:",
                requestBody
            );


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
                            JSON.stringify(
                                requestBody
                            )

                    }
                );


            const data =
                await readJsonResponse(
                    response
                );


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(

                    data.message ||
                    "変換APIでエラーが発生しました。"

                );

            }


            if (!data.job_id) {

                throw new Error(
                    "変換APIからjob_idが返されませんでした。"
                );

            }


            converterState.currentJobId =
                data.job_id;


            console.log(
                "[CONVERTER] Job ID:",
                data.job_id
            );


            return data;

        }


        // =====================================
        // Jobステータス
        // =====================================

        async function getJobStatus(
            jobId
        ) {

            console.log(
                "[CONVERTER] /status:",
                jobId
            );


            const response =
                await fetch(
                    "/status/" +
                    encodeURIComponent(
                        jobId
                    ),
                    {

                        method:
                            "GET",

                        cache:
                            "no-store"

                    }
                );


            const data =
                await readJsonResponse(
                    response
                );


            if (!response.ok) {

                throw new Error(

                    data.message ||
                    "ジョブステータス取得に失敗しました。"

                );

            }


            return data;

        }


        // =====================================
        // Jobステータス保存
        //
        // 変換中は画面を何度も書き換えない。
        //
        // 最終的な詳細情報は完了時に
        // renderConversionDetails() で表示する。
        // =====================================

        function renderJobStatus(
            job
        ) {

            if (!job) {

                return;

            }


            converterState.currentJob =
                job;


            converterState.currentJobStatus =
                job.status || "";


            const files =
                job.files || {};


            // =================================
            // MP3
            // =================================

            if (
                files.mp3 &&
                files.mp3.status ===
                    "complete" &&
                files.mp3.filename
            ) {

                converterState.currentMp3File =
                    files.mp3.filename;


                addDownloadButton(
                    files.mp3.filename,
                    "mp3"
                );

            }


            // =================================
            // MP4
            // =================================

            if (
                files.mp4 &&
                files.mp4.status ===
                    "complete" &&
                files.mp4.filename
            ) {

                converterState.currentMp4File =
                    files.mp4.filename;


                addDownloadButton(
                    files.mp4.filename,
                    "mp4"
                );

            }


            console.log(
                "[CONVERTER] Job status:",
                {
                    status:
                        job.status,

                    title:
                        job.title,

                    duration:
                        job.duration_text,

                    message:
                        job.message,

                    execution:
                        job.execution_seconds_text,

                    files:
                        files
                }
            );

        }


        // =====================================
        // Job監視
        // =====================================

        async function waitForJob(
            jobId
        ) {

            const maxWaitMs =
                30 * 60 * 1000;


            const intervalMs =
                2000;


            const startedAt =
                Date.now();


            console.log(
                "[CONVERTER] Job監視開始:",
                jobId
            );


            while (
                Date.now() -
                startedAt <
                maxWaitMs
            ) {

                const job =
                    await getJobStatus(
                        jobId
                    );


                renderJobStatus(
                    job
                );


                console.log(
                    "[CONVERTER] Job status:",
                    job.status
                );


                if (
                    job.status ===
                    "complete"
                ) {

                    return job;

                }


                if (
                    job.status ===
                    "error"
                ) {

                    throw new Error(

                        job.message ||
                        "変換処理中にエラーが発生しました。"

                    );

                }


                await new Promise(
                    function (resolve) {

                        setTimeout(
                            resolve,
                            intervalMs
                        );

                    }
                );

            }


            throw new Error(
                "変換処理がタイムアウトしました。"
            );

        }


        // =====================================
        // 処理詳細表示
        //
        // 下側の <details> に表示する。
        //
        // ダウンロードエリアには
        // 絶対に追加しない。
        // =====================================

        function renderConversionDetails(
            startTime,
            endTime,
            completedJob
        ) {

            if (
                !conversionDetailsArea ||
                !conversionDetailsContent
            ) {

                console.warn(
                    "[CONVERTER] 詳細表示DOMがありません"
                );

                return;

            }


            const elapsed =
                Math.max(

                    0,

                    Math.floor(

                        (
                            endTime.getTime() -
                            startTime.getTime()
                        ) / 1000

                    )

                );


            const job =
                completedJob || {};


            const files =
                job.files || {};


            // =================================
            // サーバー側の情報を優先
            // =================================

            const title =
                job.title ||
                converterState.currentVideoTitle ||
                "不明";


            const duration =
                job.duration_text ||
                formatDuration(
                    converterState.currentVideoDuration
                );


            const executionSeconds =
                job.execution_seconds_text ||
                formatElapsed(
                    elapsed
                );


            const jobStatus =
                job.status ||
                converterState.currentJobStatus ||
                "complete";


            const message =
                job.message ||
                "";


            // =================================
            // ファイル状態
            // =================================

            const mp3Status =
                files.mp3 &&
                files.mp3.status
                    ? files.mp3.status
                    : "";


            const mp4Status =
                files.mp4 &&
                files.mp4.status
                    ? files.mp4.status
                    : "";


            // =================================
            // 詳細HTML
            // =================================

            let html = "";


            html +=
                "<div>" +
                "再生時間： " +
                escapeHtml(
                    duration
                ) +
                "</div>";


            html +=
                "<div>" +
                "実行開始： " +
                escapeHtml(
                    formatClock(
                        startTime
                    )
                ) +
                "</div>";


            html +=
                "<div>" +
                "実行終了： " +
                escapeHtml(
                    formatClock(
                        endTime
                    )
                ) +
                "</div>";


            html +=
                "<div>" +
                "処理時間： " +
                escapeHtml(
                    executionSeconds
                ) +
                "</div>";


            // =================================
            // 今後処理が増えても
            // ここへ追加できる。
            // =================================

            if (jobStatus) {

                html +=
                    "<div>" +
                    "処理状態： " +
                    escapeHtml(
                        jobStatus
                    ) +
                    "</div>";

            }


            if (mp3Status) {

                html +=
                    "<div>" +
                    "MP3： " +
                    escapeHtml(
                        mp3Status
                    ) +
                    "</div>";

            }


            if (mp4Status) {

                html +=
                    "<div>" +
                    "MP4： " +
                    escapeHtml(
                        mp4Status
                    ) +
                    "</div>";

            }


            if (message) {

                html +=
                    "<div>" +
                    "メッセージ： " +
                    escapeHtml(
                        message
                    ) +
                    "</div>";

            }


            conversionDetailsContent.innerHTML =
                html;


            // =================================
            // 表示
            //
            // 完了時は必ず閉じる。
            // =================================

            conversionDetailsArea.style.display =
                "block";


            conversionDetailsArea.open =
                false;


            console.log(
                "[CONVERTER] 処理詳細表示:",
                {
                    title:
                        title,

                    duration:
                        duration,

                    start:
                        formatClock(
                            startTime
                        ),

                    end:
                        formatClock(
                            endTime
                        ),

                    elapsed:
                        executionSeconds
                }
            );

        }


        // =====================================
        // メイン変換処理
        // =====================================

        async function startConversion() {

            console.log(
                "[CONVERTER] startConversion()"
            );


            // =================================
            // 二重実行防止
            // =================================

            if (
                converterState.isProcessing
            ) {

                console.warn(
                    "[CONVERTER] 既に処理中です"
                );

                return;

            }


            // =================================
            // URL
            // =================================

            const url =
                urlInput.value.trim();


            if (!url) {

                setErrorStatus(
                    "YouTube URLを入力してください。"
                );


                urlInput.focus();


                return;

            }


            // =================================
            // 出力形式
            // =================================

            const outputs =
                getSelectedOutputs();


            if (!outputs.length) {

                setErrorStatus(
                    "MP3またはMP4を選択してください。"
                );


                return;

            }


            // =================================
            // State
            // =================================

            converterState.isProcessing =
                true;


            converterState.currentVideoUrl =
                url;


            clearResults();


            // clearResults()後も
            // 現在のURLは保持する。
            converterState.currentVideoUrl =
                url;


            convertButton.disabled =
                true;


            // =================================
            // 実行開始時刻
            // =================================

            const startTime =
                new Date();


            console.log(
                "===================================="
            );


            console.log(
                "[CONVERTER] YouTube変換開始"
            );


            console.log(
                "[CONVERTER] URL:",
                url
            );


            console.log(
                "[CONVERTER] outputs:",
                outputs
            );


            // =================================
            // STEP 1
            // 動画情報
            // =================================

            try {

                const info =
                    await getVideoInfo(
                        url
                    );


                converterState.currentVideoTitle =
                    info.title ||
                    info.video_title ||
                    "不明";


                converterState.currentVideoDuration =
                    info.duration ??
                    info.video_duration ??
                    0;


                console.log(
                    "[CONVERTER] 動画情報取得完了:",
                    info
                );


                // ---------------------------------
                // 上側にはタイトルだけ表示
                // ---------------------------------

                setTitleStatus(
                    converterState.currentVideoTitle
                );


                // =================================
                // STEP 2
                // 時間
                // =================================

                const timeRange =
                    getTimeRange();


                console.log(
                    "[CONVERTER] 時間範囲:",
                    timeRange
                );


                // =================================
                // STEP 3
                // 変換開始
                // =================================

                const data =
                    await convertVideo(

                        url,

                        outputs,

                        timeRange

                    );


                const jobId =
                    data.job_id;


                converterState.currentJobId =
                    jobId;


                // =================================
                // STEP 4
                // Job監視
                // =================================

                const completedJob =
                    await waitForJob(
                        jobId
                    );


                // =================================
                // STEP 5
                // 最終ファイル
                // =================================

                const files =
                    completedJob.files ||
                    {};


                if (
                    files.mp3 &&
                    files.mp3.filename
                ) {

                    converterState.currentMp3File =
                        files.mp3.filename;


                    addDownloadButton(
                        files.mp3.filename,
                        "mp3"
                    );

                }


                if (
                    files.mp4 &&
                    files.mp4.filename
                ) {

                    converterState.currentMp4File =
                        files.mp4.filename;


                    addDownloadButton(
                        files.mp4.filename,
                        "mp4"
                    );

                }


                // =================================
                // ファイル確認
                // =================================

                const hasMp3 =
                    Boolean(
                        converterState.currentMp3File
                    );


                const hasMp4 =
                    Boolean(
                        converterState.currentMp4File
                    );


                if (
                    !hasMp3 &&
                    !hasMp4
                ) {

                    throw new Error(
                        "変換は完了しましたが、作成されたファイルが確認できませんでした。"
                    );

                }


                // =================================
                // STEP 6
                // 完了
                // =================================

                const endTime =
                    new Date();


                // ---------------------------------
                // 上側
                //
                // タイトルだけを維持
                // ---------------------------------

                setTitleStatus(
                    converterState.currentVideoTitle ||
                    completedJob.title ||
                    "不明"
                );


                // ---------------------------------
                // 下側
                //
                // 詳細情報を表示
                //
                // 完了時は閉じた状態
                // ---------------------------------

                renderConversionDetails(
                    startTime,
                    endTime,
                    completedJob
                );


                console.log(
                    "[CONVERTER] 変換完了:",
                    completedJob
                );

            }
            catch (error) {

                console.error(
                    "[CONVERTER] エラー:",
                    error
                );


                const message =
                    error &&
                    error.message
                        ? error.message
                        : "不明なエラー";


                setErrorStatus(

                    "変換中にエラーが発生しました。\n" +
                    message

                );

            }
            finally {

                converterState.isProcessing =
                    false;


                convertButton.disabled =
                    false;


                console.log(
                    "[CONVERTER] 処理終了"
                );

            }

        }


        // =====================================
        // クリックイベント
        // =====================================

        if (
            convertButton.dataset.converterBound !==
            "true"
        ) {

            convertButton.addEventListener(
                "click",
                startConversion
            );


            convertButton.dataset.converterBound =
                "true";


            console.log(
                "[CONVERTER] #convertBtn イベント登録完了"
            );

        }
        else {

            console.log(
                "[CONVERTER] #convertBtn は既に登録済み"
            );

        }


        // =====================================
        // Enterキー
        // =====================================

        if (
            urlInput.dataset.converterEnterBound !==
            "true"
        ) {

            urlInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key ===
                        "Enter"
                    ) {

                        event.preventDefault();

                        startConversion();

                    }

                }
            );


            urlInput.dataset.converterEnterBound =
                "true";

        }


        // =====================================
        // 時間入力
        // =====================================

        const timeInputs =
            document.querySelectorAll(
                ".time-input"
            );


        timeInputs.forEach(
            function (input) {

                if (
                    input.dataset.converterTimeBound ===
                    "true"
                ) {

                    return;

                }


                input.addEventListener(
                    "input",
                    function () {

                        this.value =
                            this.value.replace(
                                /[^0-9]/g,
                                ""
                            );

                    }
                );


                input.dataset.converterTimeBound =
                    "true";

            }
        );


        // =====================================
        // 公開API
        // =====================================

        const publicApi = {

            start:
                startConversion,

            clearResults:
                clearResults,

            getState:
                function () {

                    return converterState;

                }

        };


        window.converterMain =
            publicApi;


        window.ConverterMain =
            publicApi;


        console.log(
            "===================================="
        );


        console.log(
            "[CONVERTER] converter.js 読み込み完了"
        );


        console.log(
            "[CONVERTER] 実行ボタン待機中"
        );


        console.log(
            "===================================="
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
            initializeConverter,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeConverter();

    }


})();
