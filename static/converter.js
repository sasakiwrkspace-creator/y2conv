// =====================================
// YouTube Converter
// converter.js
//
// タブ1：YouTube変換専用
//
// 役割:
// ・YouTube URL受付
// ・動画情報取得
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
            "[CONVERTER] youtube-url:",
            urlInput
        );


        console.log(
            "[CONVERTER] convertBtn:",
            convertButton
        );


        console.log(
            "[CONVERTER] status:",
            statusElement
        );


        console.log(
            "[CONVERTER] conversion-status-area:",
            conversionStatusArea
        );


        console.log(
            "[CONVERTER] downloadArea:",
            downloadArea
        );


        // =====================================
        // 必須DOM確認
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
        // ステータス表示
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


            if (type === "error") {

                statusElement.style.color =
                    "#c00";

            }
            else if (type === "success") {

                statusElement.style.color =
                    "#087f23";

            }
            else {

                statusElement.style.color =
                    "#222";

            }

        }


        // =====================================
        // 処理状況表示
        // =====================================

        function setProgress(
            message
        ) {

            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    message;


                conversionStatusArea.style.whiteSpace =
                    "pre-line";


                conversionStatusArea.style.display =
                    "block";

            }


            setStatus(
                message
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
        // 時間フォーマット
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
                    Number(seconds) || 0
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
        // 再生時間表示
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


            // 数値秒
            if (
                typeof duration ===
                "number"
            ) {

                const total =
                    Math.max(
                        0,
                        Math.floor(duration)
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
                        String(hours).padStart(2, "0") +
                        ":" +
                        String(minutes).padStart(2, "0") +
                        ":" +
                        String(seconds).padStart(2, "0")
                    );

                }


                return (
                    String(minutes).padStart(2, "0") +
                    ":" +
                    String(seconds).padStart(2, "0")
                );

            }


            return String(
                duration
            );

        }


        // =====================================
        // 時間入力取得
        //
        // [00]時[00]分[00]秒
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


            // 全部空なら指定なし
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


            // 秒に変換
            return (
                h * 3600 +
                m * 60 +
                s
            );

        }


        // =====================================
        // 時間範囲取得
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
        // 出力形式取得
        // =====================================

        function getSelectedOutputs() {

            const radios =
                document.querySelectorAll(
                    'input[name="output-format"]:checked'
                );


            const outputs = [];


            radios.forEach(
                function (radio) {

                    if (
                        radio.value ===
                        "mp3"
                    ) {

                        outputs.push(
                            "mp3"
                        );

                    }
                    else if (
                        radio.value ===
                        "mp4"
                    ) {

                        outputs.push(
                            "mp4"
                        );

                    }
                    else if (
                        radio.value ===
                        "subtitle_mp4"
                    ) {

                        /*
                         * 字幕MP4は
                         * タブ2側で作成するため、
                         * YouTube変換APIには
                         * mp4として送る。
                         */
                        outputs.push(
                            "mp4"
                        );

                    }

                }
            );


            /*
             * 重複削除
             */

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
        // =====================================

        function addDownloadButton(
            filename,
            type
        ) {

            if (!downloadArea) {

                console.warn(
                    "[CONVERTER] downloadArea がありません"
                );

                return;

            }


            if (!filename) {

                return;

            }


            const existing =
                Array.from(
                    downloadArea.children
                ).some(
                    function (element) {

                        return (
                            element.dataset &&
                            element.dataset.filename ===
                            String(filename)
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
                    filename
                );


            link.download =
                String(filename);


            link.className =
                "download-button";


            link.dataset.filename =
                String(filename);


            link.textContent =
                "[" +
                String(type) +
                "]";


            downloadArea.appendChild(
                link
            );


            console.log(
                "[CONVERTER] ダウンロードボタン追加:",
                filename
            );

        }


        // =====================================
        // 結果クリア
        // =====================================

        function clearResults() {

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    "";

            }


            if (statusElement) {

                statusElement.textContent =
                    "";

            }


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


            let data;


            try {

                data =
                    await response.json();

            }
            catch (error) {

                throw new Error(
                    "動画情報APIからJSONを取得できませんでした。"
                );

            }


            console.log(
                "[CONVERTER] /video-info:",
                data
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
                "[CONVERTER] /convert:",
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


            let data;


            try {

                data =
                    await response.json();

            }
            catch (error) {

                throw new Error(
                    "変換APIからJSONを取得できませんでした。"
                );

            }


            console.log(
                "[CONVERTER] /convert response:",
                data
            );


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "変換に失敗しました。"
                );

            }


            if (!data.job_id) {

                throw new Error(
                    "変換APIからjob_idが返されませんでした。"
                );

            }


            converterState.currentJobId =
                data.job_id;


            return data;

        }


        // =====================================
        // Jobステータス取得
        // =====================================

        async function getJobStatus(
            jobId
        ) {

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


            let data;


            try {

                data =
                    await response.json();

            }
            catch (error) {

                throw new Error(
                    "ステータスAPIからJSONを取得できませんでした。"
                );

            }


            if (!response.ok) {

                throw new Error(
                    data.message ||
                    "ジョブステータス取得に失敗しました。"
                );

            }


            return data;

        }


        // =====================================
        // Jobステータス表示
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


            const lines = [];


            if (job.status) {

                lines.push(
                    "処理状態: " +
                    job.status
                );

            }


            if (job.title) {

                lines.push(
                    "タイトル: " +
                    job.title
                );

            }


            if (job.duration_text) {

                lines.push(
                    "処理対象時間: " +
                    job.duration_text
                );

            }


            if (files.mp3) {

                let text =
                    "MP3: " +
                    (
                        files.mp3.status ||
                        "unknown"
                    );


                if (
                    files.mp3.filename
                ) {

                    text +=
                        " (" +
                        files.mp3.filename +
                        ")";

                }


                lines.push(
                    text
                );

            }


            if (files.mp4) {

                let text =
                    "MP4: " +
                    (
                        files.mp4.status ||
                        "unknown"
                    );


                if (
                    files.mp4.filename
                ) {

                    text +=
                        " (" +
                        files.mp4.filename +
                        ")";

                }


                lines.push(
                    text
                );

            }


            if (
                job.execution_seconds_text
            ) {

                lines.push(
                    "処理時間: " +
                    job.execution_seconds_text
                );

            }


            if (job.message) {

                lines.push(
                    "メッセージ: " +
                    job.message
                );

            }


            setProgress(
                lines.join(
                    "\n"
                )
            );


            // =================================
            // MP3完成
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
            // MP4完成
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
        // 処理詳細
        // =====================================

        function addConversionInfo(
            startTime,
            endTime
        ) {

            if (!downloadArea) {

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


            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "conversion-details";


            wrapper.innerHTML = `

                <div>
                    変換完了
                </div>

                <div>
                    タイトル：
                    ${escapeHtml(
                        converterState.currentVideoTitle ||
                        "不明"
                    )}
                </div>

                <div>
                    再生時間：
                    ${escapeHtml(
                        formatDuration(
                            converterState.currentVideoDuration
                        )
                    )}
                </div>

                <div>
                    実行開始：
                    ${escapeHtml(
                        formatClock(
                            startTime
                        )
                    )}
                </div>

                <div>
                    実行終了：
                    ${escapeHtml(
                        formatClock(
                            endTime
                        )
                    )}
                </div>

                <div>
                    処理時間：
                    ${escapeHtml(
                        formatElapsed(
                            elapsed
                        )
                    )}
                </div>

            `;


            downloadArea.appendChild(
                wrapper
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

                return;

            }


            // =================================
            // URL
            // =================================

            const url =
                urlInput.value.trim();


            if (!url) {

                setStatus(
                    "YouTube URLを入力してください。",
                    "error"
                );

                urlInput.focus();

                return;

            }


            // =================================
            // 処理開始
            // =================================

            converterState.isProcessing =
                true;


            converterState.currentVideoUrl =
                url;


            clearResults();


            convertButton.disabled =
                true;


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


            // =================================
            // STEP 1
            // 動画情報
            // =================================

            setProgress(
                "動画情報を取得しています..."
            );


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
                    info.duration ||
                    info.video_duration ||
                    "不明";


                console.log(
                    "[CONVERTER] 動画情報:",
                    info
                );


                // =================================
                // STEP 2
                // 出力形式
                // =================================

                const outputs =
                    getSelectedOutputs();


                if (
                    !outputs.length
                ) {

                    throw new Error(
                        "出力形式を選択してください。"
                    );

                }


                const timeRange =
                    getTimeRange();


                console.log(
                    "[CONVERTER] outputs:",
                    outputs
                );


                console.log(
                    "[CONVERTER] timeRange:",
                    timeRange
                );


                // =================================
                // STEP 3
                // 変換開始
                // =================================

                setProgress(
                    "変換ジョブを開始しています..."
                );


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

                setProgress(

                    "変換処理中...\n" +
                    "Job ID: " +
                    jobId

                );


                const completedJob =
                    await waitForJob(
                        jobId
                    );


                // =================================
                // STEP 5
                // 最終結果
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
                // ファイル存在確認
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


                addConversionInfo(
                    startTime,
                    endTime
                );


                let completeMessage =
                    "変換が完了しました。";


                if (
                    hasMp3 &&
                    hasMp4
                ) {

                    completeMessage =
                        "MP3 / MP4 の変換が完了しました。";

                }
                else if (hasMp3) {

                    completeMessage =
                        "MP3の変換が完了しました。";

                }
                else if (hasMp4) {

                    completeMessage =
                        "MP4の変換が完了しました。";

                }


                if (
                    completedJob.execution_seconds_text
                ) {

                    completeMessage +=
                        "\n" +
                        completedJob.execution_seconds_text;

                }


                if (conversionStatusArea) {

                    conversionStatusArea.textContent =
                        completeMessage;

                }


                setStatus(
                    completeMessage,
                    "success"
                );


                console.log(
                    "[CONVERTER] 変換完了"
                );


                console.log(
                    "[CONVERTER] Job:",
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


                setStatus(

                    "変換中にエラーが発生しました。\n" +
                    message,

                    "error"

                );


                if (
                    conversionStatusArea
                ) {

                    conversionStatusArea.textContent =
                        "変換中にエラーが発生しました。\n" +
                        message;

                }

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
            convertButton.dataset.converterBound ===
            "true"
        ) {

            console.log(
                "[CONVERTER] 既にイベント登録済み"
            );

        }
        else {

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


        // =====================================
        // Enterキー
        //
        // URL入力欄でEnterを押しても実行
        // =====================================

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


        // =====================================
        // 時間入力
        //
        // 数字以外を除去
        // =====================================

        const timeInputs =
            document.querySelectorAll(
                ".time-input"
            );


        timeInputs.forEach(
            function (input) {

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
