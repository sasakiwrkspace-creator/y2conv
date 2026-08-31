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
// ステータス表示:
// ・#conversion-status-area の1か所だけを使用
// ・#status は使用しない
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


        // -------------------------------------
        // ステータス表示はここ1か所だけ
        // -------------------------------------

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
            "[CONVERTER] conversion-status-area:",
            conversionStatusArea
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
        //
        // 重要:
        // #status は使用しない。
        //
        // すべて
        // #conversion-status-area
        // に一本化する。
        // =====================================

        function setStatus(
            message,
            type
        ) {

            const text =
                String(
                    message || ""
                );


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    text;

                conversionStatusArea.style.whiteSpace =
                    "pre-line";

                conversionStatusArea.style.display =
                    "block";


                if (type === "error") {

                    conversionStatusArea.style.color =
                        "#c00";

                }
                else if (
                    type === "success"
                ) {

                    conversionStatusArea.style.color =
                        "#087f23";

                }
                else {

                    conversionStatusArea.style.color =
                        "#222";

                }

            }


            console.log(
                "[CONVERTER] STATUS:",
                text
            );

        }


        // =====================================
        // 処理状況表示
        //
        // setStatus()だけを使用する。
        //
        // これによりステータス表示が
        // 2か所に分かれることを防止する。
        // =====================================

        function setProgress(
            message
        ) {

            setStatus(
                message,
                "progress"
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


            // ---------------------------------
            // 全部空なら指定なし
            // ---------------------------------

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


            // ---------------------------------
            // 数値確認
            // ---------------------------------

            if (
                !Number.isFinite(h) ||
                !Number.isFinite(m) ||
                !Number.isFinite(s)
            ) {

                return null;

            }


            // ---------------------------------
            // 秒へ変換
            // ---------------------------------

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

                        /*
                         * 字幕付きMP4は
                         * 現在のタブ1変換APIでは
                         * MP4として扱う。
                         */

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


            // ---------------------------------
            // 重複確認
            // ---------------------------------

            const existing =
                downloadArea.querySelector(
                    '[data-filename="' +
                    CSS.escape(
                        safeFilename
                    ) +
                    '"]'
                );


            if (existing) {

                return;

            }


            // ---------------------------------
            // リンク作成
            // ---------------------------------

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

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    "";

                conversionStatusArea.style.display =
                    "none";

                conversionStatusArea.style.color =
                    "#222";

            }


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


            const lines =
                [];


            // ---------------------------------
            // 状態
            // ---------------------------------

            if (job.status) {

                lines.push(
                    "処理状態: " +
                    job.status
                );

            }


            // ---------------------------------
            // タイトル
            // ---------------------------------

            if (job.title) {

                lines.push(
                    "タイトル: " +
                    job.title
                );

            }


            // ---------------------------------
            // 時間
            // ---------------------------------

            if (job.duration_text) {

                lines.push(
                    "処理対象時間: " +
                    job.duration_text
                );

            }


            // ---------------------------------
            // メッセージ
            // ---------------------------------

            if (job.message) {

                lines.push(
                    "メッセージ: " +
                    job.message
                );

            }


            // ---------------------------------
            // 実行時間
            // ---------------------------------

            if (
                job.execution_seconds_text
            ) {

                lines.push(
                    "処理時間: " +
                    job.execution_seconds_text
                );

            }


            // ---------------------------------
            // ファイル
            // ---------------------------------

            const files =
                job.files || {};


            if (files.mp3) {

                const mp3Status =
                    files.mp3.status ||
                    "unknown";


                lines.push(
                    "MP3: " +
                    mp3Status
                );

            }


            if (files.mp4) {

                const mp4Status =
                    files.mp4.status ||
                    "unknown";


                lines.push(
                    "MP4: " +
                    mp4Status
                );

            }


            // ---------------------------------
            // ここだけに表示
            // ---------------------------------

            setProgress(
                lines.join(
                    "\n"
                )
            );


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


                // ---------------------------------
                // 完了
                // ---------------------------------

                if (
                    job.status ===
                    "complete"
                ) {

                    return job;

                }


                // ---------------------------------
                // エラー
                // ---------------------------------

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

                setStatus(
                    "YouTube URLを入力してください。",
                    "error"
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

                setStatus(
                    "MP3またはMP4を選択してください。",
                    "error"
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


            // clearResults()後に再度true
            converterState.isProcessing =
                true;


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


            console.log(
                "[CONVERTER] outputs:",
                outputs
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
                    info.duration ??
                    info.video_duration ??
                    0;


                console.log(
                    "[CONVERTER] 動画情報取得完了:",
                    info
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


                addConversionInfo(
                    startTime,
                    endTime
                );


                let completeMessage;


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
                else {

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


                // ---------------------------------
                // 完了表示も1か所だけ
                // ---------------------------------

                setStatus(
                    completeMessage,
                    "success"
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


                // ---------------------------------
                // エラー表示も1か所だけ
                // ---------------------------------

                setStatus(

                    "変換中にエラーが発生しました。\n" +
                    message,

                    "error"

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
        //
        // converter.js側だけで管理する。
        // index.html側では登録しない。
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
