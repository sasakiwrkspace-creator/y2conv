// =====================================
// YouTube Converter - Main
// converter.js
//
// タブ1：YouTube変換
//
// 役割:
// ・YouTube URL受付
// ・動画情報取得
// ・変換API実行
// ・job_idによる処理状況監視
// ・MP3 / MP4ダウンロード表示
// ・処理詳細表示
// ・converterState管理
//
// 注意:
// ・タブ1ではMP4/SRTファイルをアップロードしない
// ・タブ1の実行ボタンは #convertBtn
// ・タブ2のアップロード処理は sub_embed.js が担当
//
// 使用:
// ・converter-utils.js
// ・converter-status.js
// ・converter-gemini.js
// ・sub_embed.js
// =====================================


(function () {

    "use strict";


    // =====================================
    // Converter初期化
    // =====================================

    function initializeConverterMain() {

        console.log(
            "[CONVERTER] initializeConverterMain() start"
        );


        // =================================
        // 二重初期化防止
        // =================================

        if (
            window.converterMain &&
            window.converterMain.__initialized
        ) {

            console.log(
                "[CONVERTER] already initialized"
            );

            return;

        }


        // =================================
        // Utils確認
        // =================================

        const utils =
            window.converterUtils;


        if (!utils) {

            console.error(
                "[CONVERTER] converterUtils がありません"
            );

            return;

        }


        // =================================
        // Status確認
        // =================================

        const status =
            window.converterStatus;


        if (!status) {

            console.error(
                "[CONVERTER] converterStatus がありません"
            );

            return;

        }


        // =====================================
        // Converter State
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

            currentSrtFile:
                "",

            currentSubtitleEmbedFile:
                "",

            isProcessing:
                false,

            currentJobId:
                "",

            currentJobStatus:
                "",

            currentJob:
                null

        };


        window.converterState =
            converterState;


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


        const subtitleMp4Area =
            document.getElementById(
                "subtitle-mp4-area"
            );


        const subtitleMp4Info =
            document.getElementById(
                "subtitle-mp4-info"
            );


        const subtitleMp4DownloadContainer =
            document.getElementById(
                "subtitle-mp4-download-container"
            );


        console.log(
            "[CONVERTER] urlInput =",
            urlInput
        );


        console.log(
            "[CONVERTER] convertButton =",
            convertButton
        );


        console.log(
            "[CONVERTER] statusElement =",
            statusElement
        );


        console.log(
            "[CONVERTER] conversionStatusArea =",
            conversionStatusArea
        );


        console.log(
            "[CONVERTER] downloadArea =",
            downloadArea
        );


        console.log(
            "[CONVERTER] subtitleMp4Area =",
            subtitleMp4Area
        );


        // =====================================
        // 必須DOM確認
        // =====================================

        if (!urlInput) {

            console.error(
                "[CONVERTER] youtube-url が見つかりません"
            );

        }


        if (!convertButton) {

            console.error(
                "[CONVERTER] convertBtn が見つかりません"
            );

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
        // ダウンロードボタン追加
        // =====================================

        function addDownloadButton(
            filename,
            label
        ) {

            if (!downloadArea) {

                console.warn(
                    "[CONVERTER] downloadArea がありません"
                );

                return;

            }


            if (!filename) {

                console.warn(
                    "[CONVERTER] ダウンロードファイル名がありません"
                );

                return;

            }


            // ---------------------------------
            // 同じファイルの重複防止
            // ---------------------------------

            const existing =
                downloadArea.querySelector(
                    `[data-filename="${CSS.escape(
                        String(filename)
                    )}"]`
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
                filename;


            link.className =
                "download-button";


            link.dataset.filename =
                filename;


            link.textContent =
                label;


            downloadArea.appendChild(
                link
            );


            console.log(
                "[CONVERTER] ダウンロードボタン追加:",
                {
                    filename:
                        filename,

                    label:
                        label
                }
            );

        }


        // =====================================
        // 処理詳細追加
        // =====================================

        function addConversionInfo(
            html
        ) {

            if (!html) {

                return;

            }


            if (!downloadArea) {

                console.warn(
                    "[CONVERTER] downloadArea がありません"
                );

                return;

            }


            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "converter-conversion-info-wrapper";


            wrapper.innerHTML =
                html;


            downloadArea.appendChild(
                wrapper
            );


            console.log(
                "[CONVERTER] 処理詳細を追加しました"
            );

        }


        // =====================================
        // SRT情報追加
        // =====================================

        function addSrtInfo(
            html,
            srtFile
        ) {

            if (srtFile) {

                converterState.currentSrtFile =
                    srtFile;

            }


            addConversionInfo(
                html
            );


            console.log(
                "[CONVERTER] SRT情報を追加:",
                srtFile
            );

        }


        // =====================================
        // 字幕付きMP4追加
        // =====================================

        function addSubtitleEmbedFile(
            filename
        ) {

            if (!filename) {

                return;

            }


            converterState.currentSubtitleEmbedFile =
                filename;


            addSubtitleMp4DownloadButton(
                filename
            );


            console.log(
                "[CONVERTER] 字幕付きMP4を追加:",
                filename
            );

        }


        // =====================================
        // 字幕付きMP4処理詳細
        // =====================================

        function addSubtitleEmbedInfo(
            html
        ) {

            if (!html) {

                return;

            }


            if (subtitleMp4Info) {

                subtitleMp4Info.innerHTML =
                    html;


                if (subtitleMp4Area) {

                    subtitleMp4Area.style.display =
                        "block";

                }

            }
            else {

                addConversionInfo(
                    html
                );

            }


            console.log(
                "[CONVERTER] 字幕付きMP4情報を追加"
            );

        }


        // =====================================
        // 字幕付きMP4ダウンロードボタン
        // =====================================

        function addSubtitleMp4DownloadButton(
            filename
        ) {

            if (!filename) {

                return;

            }


            if (
                !subtitleMp4DownloadContainer
            ) {

                console.warn(
                    "[CONVERTER] " +
                    "subtitleMp4DownloadContainer がありません"
                );

                return;

            }


            subtitleMp4DownloadContainer.innerHTML =
                "";


            const downloadUrl =
                makeDownloadUrl(
                    filename
                );


            const link =
                document.createElement(
                    "a"
                );


            link.href =
                downloadUrl;


            link.download =
                filename;


            link.className =
                "download-button subtitle-mp4-download-button";


            link.textContent =
                "字幕付きMP4をダウンロード";


            subtitleMp4DownloadContainer.appendChild(
                link
            );


            if (subtitleMp4Area) {

                subtitleMp4Area.style.display =
                    "block";

            }


            console.log(
                "[CONVERTER] 字幕付きMP4ダウンロードボタン追加:",
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


            if (subtitleMp4Info) {

                subtitleMp4Info.innerHTML =
                    "";

            }


            if (
                subtitleMp4DownloadContainer
            ) {

                subtitleMp4DownloadContainer.innerHTML =
                    "";

            }


            if (subtitleMp4Area) {

                subtitleMp4Area.style.display =
                    "none";

            }


            converterState.currentMp3File =
                "";

            converterState.currentMp4File =
                "";

            converterState.currentSrtFile =
                "";

            converterState.currentSubtitleEmbedFile =
                "";

            converterState.currentJobId =
                "";

            converterState.currentJobStatus =
                "";

            converterState.currentJob =
                null;


            console.log(
                "[CONVERTER] 結果をクリアしました"
            );

        }


        // =====================================
        // ステータス補助
        // =====================================

        function setStatusText(
            message,
            type
        ) {

            if (type === "error") {

                if (
                    status &&
                    typeof status.error ===
                        "function"
                ) {

                    status.error(
                        message
                    );

                    return;

                }

            }


            if (type === "success") {

                if (
                    status &&
                    typeof status.success ===
                        "function"
                ) {

                    status.success(
                        message
                    );

                    return;

                }

            }


            if (
                status &&
                typeof status.update ===
                    "function"
            ) {

                status.update(
                    message
                );

                return;

            }


            if (statusElement) {

                statusElement.textContent =
                    message;

            }

        }


        // =====================================
        // 途中経過表示
        // =====================================

        function setConversionProgress(
            message
        ) {

            if (
                conversionStatusArea
            ) {

                conversionStatusArea.style.display =
                    "block";


                conversionStatusArea.textContent =
                    message;


                conversionStatusArea.style.whiteSpace =
                    "pre-line";

            }


            setStatusText(
                message
            );

        }


        // =====================================
        // 動画情報取得
        // =====================================

        async function getVideoInfo(
            url
        ) {

            console.log(
                "[CONVERTER] 動画情報取得開始:",
                url
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


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(

                    data.message ||
                    "動画情報の取得に失敗しました。"

                );

            }


            console.log(
                "[CONVERTER] 動画情報取得完了:",
                data
            );


            return data;

        }


        // =====================================
        // 変換API
        //
        // ★重要
        //
        // /convert はファイルを直接返さず、
        // job_id を返す。
        // =====================================

        async function convertVideo(
            url,
            outputs,
            timeRange
        ) {

            console.log(
                "[CONVERTER] 変換開始:",
                {
                    url:
                        url,

                    outputs:
                        outputs,

                    timeRange:
                        timeRange
                }
            );


            // ---------------------------------
            // 時間範囲をAPI形式へ変換
            // ---------------------------------

            let startTime = null;
            let endTime = null;


            if (timeRange) {

                if (
                    typeof timeRange ===
                        "object"
                ) {

                    startTime =
                        timeRange.start_time ??
                        timeRange.start ??
                        null;

                    endTime =
                        timeRange.end_time ??
                        timeRange.end ??
                        null;

                }

            }


            console.log(
                "[CONVERTER] API時間:",
                {
                    start_time:
                        startTime,

                    end_time:
                        endTime
                }
            );


            // ---------------------------------
            // JSON
            // ---------------------------------

            const requestBody = {

                url:
                    url,

                outputs:
                    outputs,

                start_time:
                    startTime,

                end_time:
                    endTime

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


            console.log(
                "[CONVERTER] JOB ID:",
                data.job_id
            );


            return data;

        }


        // =====================================
        // Job Status取得
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
        // Job Status表示
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


            // ---------------------------------
            // Job全体
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
            // 再生時間
            // ---------------------------------

            if (job.duration_text) {

                lines.push(
                    "処理対象時間: " +
                    job.duration_text
                );

            }


            // ---------------------------------
            // MP3
            // ---------------------------------

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


            // ---------------------------------
            // MP4
            // ---------------------------------

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
            // エラー
            // ---------------------------------

            if (job.message) {

                lines.push(
                    "メッセージ: " +
                    job.message
                );

            }


            // ---------------------------------
            // 画面表示
            // ---------------------------------

            setConversionProgress(
                lines.join("\n")
            );


            // =================================
            // 完成ファイル
            // =================================

            if (
                files.mp3 &&
                files.mp3.status ===
                    "complete" &&
                files.mp3.filename
            ) {

                handleMp3Result(
                    files.mp3.filename
                );

            }


            if (
                files.mp4 &&
                files.mp4.status ===
                    "complete" &&
                files.mp4.filename
            ) {

                handleMp4Result(
                    files.mp4.filename
                );

            }

        }


        // =====================================
        // Job完了待ち
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


            let lastStatus =
                "";


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


                if (
                    job.status !==
                    lastStatus
                ) {

                    console.log(
                        "[CONVERTER] Job status:",
                        job.status
                    );


                    lastStatus =
                        job.status;

                }


                // ---------------------------------
                // 完了
                // ---------------------------------

                if (
                    job.status ===
                        "complete"
                ) {

                    console.log(
                        "[CONVERTER] Job COMPLETE:",
                        job
                    );


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


                // ---------------------------------
                // 待機
                // ---------------------------------

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
        // MP3結果処理
        // =====================================

        function handleMp3Result(
            filename
        ) {

            if (!filename) {

                return;

            }


            converterState.currentMp3File =
                filename;


            addDownloadButton(
                filename,
                "MP3をダウンロード"
            );


            console.log(
                "[CONVERTER] MP3:",
                filename
            );

        }


        // =====================================
        // MP4結果処理
        // =====================================

        function handleMp4Result(
            filename
        ) {

            if (!filename) {

                return;

            }


            converterState.currentMp4File =
                filename;


            addDownloadButton(
                filename,
                "MP4をダウンロード"
            );


            console.log(
                "[CONVERTER] MP4:",
                filename
            );

        }


        // =====================================
        // 変換処理詳細作成
        // =====================================

        function createConversionInfo(
            startTime,
            endTime
        ) {

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


            const title =
                converterState.currentVideoTitle ||
                "不明";


            const duration =
                converterState.currentVideoDuration ||
                "不明";


            return `

                <div class="conversion-info">

                    <div class="conversion-info-title">

                        ★変換完了

                    </div>


                    <div>

                        タイトル：
                        ${utils.escapeHtml(
                            title
                        )}

                    </div>


                    <div>

                        再生時間：
                        ${utils.escapeHtml(
                            utils.formatDuration(
                                duration
                            )
                        )}

                    </div>


                    <div>

                        実行開始：
                        ${utils.escapeHtml(
                            utils.formatClock(
                                startTime
                            )
                        )}

                    </div>


                    <div>

                        実行終了：
                        ${utils.escapeHtml(
                            utils.formatClock(
                                endTime
                            )
                        )}

                        （${utils.escapeHtml(
                            utils.formatElapsed(
                                elapsed
                            )
                        )}）

                    </div>

                </div>

            `;

        }


        // =====================================
        // 変換開始
        // =====================================

        async function startConversion() {

            console.log(
                "[CONVERTER] startConversion() called"
            );


            // =================================
            // 二重実行防止
            // =================================

            if (
                converterState.isProcessing
            ) {

                console.warn(
                    "[CONVERTER] 既に変換処理中です"
                );

                return;

            }


            // =================================
            // URL
            // =================================

            const url =
                urlInput
                    ? urlInput.value.trim()
                    : "";


            if (!url) {

                setStatusText(
                    "YouTube URLを入力してください。",
                    "error"
                );

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


            if (convertButton) {

                convertButton.disabled =
                    true;

            }


            const startTime =
                new Date();


            console.log(
                "=========================================="
            );


            console.log(
                "[CONVERTER] YouTube変換処理開始"
            );


            console.log(
                "[CONVERTER] 開始:",
                utils.formatClock(
                    startTime
                )
            );


            console.log(
                "[CONVERTER] URL:",
                url
            );


            console.log(
                "=========================================="
            );


            setConversionProgress(
                "動画情報を取得しています..."
            );


            try {

                // =================================
                // STEP 1
                // 動画情報
                // =================================

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
                    "[CONVERTER] タイトル:",
                    converterState.currentVideoTitle
                );


                console.log(
                    "[CONVERTER] 再生時間:",
                    converterState.currentVideoDuration
                );


                // =================================
                // STEP 2
                // 出力形式
                // =================================

                const outputs =
                    utils.getSelectedOutputs();


                const timeRange =
                    utils.getTimeRange();


                console.log(
                    "[CONVERTER] 出力形式:",
                    outputs
                );


                console.log(
                    "[CONVERTER] 時間範囲:",
                    timeRange
                );


                if (
                    !Array.isArray(outputs) ||
                    outputs.length === 0
                ) {

                    throw new Error(
                        "MP3またはMP4の出力形式を選択してください。"
                    );

                }


                // =================================
                // STEP 3
                // Job開始
                // =================================

                setConversionProgress(
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

                setConversionProgress(

                    "変換処理中...\n" +
                    "Job ID: " +
                    jobId +
                    "\n" +
                    "状態を確認しています..."

                );


                const completedJob =
                    await waitForJob(
                        jobId
                    );


                // =================================
                // STEP 5
                // 最終ファイル取得
                // =================================

                const finalFiles =
                    completedJob.files ||
                    {};


                if (
                    finalFiles.mp3 &&
                    finalFiles.mp3.filename
                ) {

                    handleMp3Result(
                        finalFiles.mp3.filename
                    );

                }


                if (
                    finalFiles.mp4 &&
                    finalFiles.mp4.filename
                ) {

                    handleMp4Result(
                        finalFiles.mp4.filename
                    );

                }


                // =================================
                // STEP 6
                // 完成ファイル確認
                // =================================

                let hasFile =
                    false;


                if (
                    converterState.currentMp3File
                ) {

                    hasFile =
                        true;

                }


                if (
                    converterState.currentMp4File
                ) {

                    hasFile =
                        true;

                }


                if (!hasFile) {

                    throw new Error(
                        "変換は完了しましたが、ダウンロード可能なファイル名が返されませんでした。"
                    );

                }


                // =================================
                // STEP 7
                // 終了時間
                // =================================

                const endTime =
                    new Date();


                // =================================
                // STEP 8
                // 処理詳細
                // =================================

                const detailHtml =
                    createConversionInfo(

                        startTime,

                        endTime

                    );


                addConversionInfo(
                    detailHtml
                );


                // =================================
                // STEP 9
                // 完了
                // =================================

                setStatusText(
                    "変換が完了しました。",
                    "success"
                );


                if (
                    conversionStatusArea
                ) {

                    conversionStatusArea.textContent =
                        "変換が完了しました。\n" +
                        (
                            completedJob.execution_seconds_text ||
                            ""
                        );

                }


                // =================================
                // 完了ログ
                // =================================

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


                console.log(
                    "=========================================="
                );


                console.log(
                    "[CONVERTER] 変換処理完了"
                );


                console.log(
                    "[CONVERTER] Job ID:",
                    jobId
                );


                console.log(
                    "[CONVERTER] 開始:",
                    utils.formatClock(
                        startTime
                    )
                );


                console.log(
                    "[CONVERTER] 終了:",
                    utils.formatClock(
                        endTime
                    )
                );


                console.log(
                    "[CONVERTER] 処理時間:",
                    utils.formatElapsed(
                        elapsed
                    )
                );


                console.log(
                    "[CONVERTER] MP3:",
                    converterState.currentMp3File
                );


                console.log(
                    "[CONVERTER] MP4:",
                    converterState.currentMp4File
                );


                console.log(
                    "[CONVERTER] Job:",
                    completedJob
                );


                console.log(
                    "=========================================="
                );

            }
            catch (error) {

                console.error(
                    "[CONVERTER] エラー:",
                    error
                );


                const message =
                    (
                        error &&
                        error.message
                    )
                        ? error.message
                        : "不明なエラー";


                setStatusText(

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


                if (convertButton) {

                    convertButton.disabled =
                        false;

                }


                console.log(
                    "[CONVERTER] startConversion() finished"
                );

            }

        }


        // =====================================
        // タブ1：変換ボタン
        // =====================================

        if (convertButton) {

            convertButton.addEventListener(
                "click",
                startConversion
            );


            console.log(
                "[CONVERTER] ====================================="
            );


            console.log(
                "[CONVERTER] convertBtn 初期化完了"
            );


            console.log(
                "[CONVERTER] YouTube変換ボタンのクリック待機中"
            );


            console.log(
                "[CONVERTER] ====================================="
            );

        }
        else {

            console.error(
                "[CONVERTER] convertBtn がありません"
            );

        }


        // =====================================
        // 公開API
        // =====================================

        const main = {

            __initialized:
                true,

            start:
                startConversion,

            addSrtInfo:
                addSrtInfo,

            addSubtitleEmbedFile:
                addSubtitleEmbedFile,

            addSubtitleEmbedInfo:
                addSubtitleEmbedInfo,

            addConversionInfo:
                addConversionInfo,

            clearResults:
                clearResults,

            getState:
                function () {

                    return converterState;

                }

        };


        // =====================================
        // グローバル公開
        // =====================================

        window.converterMain =
            main;


        window.ConverterMain =
            main;


        // =====================================
        // 読み込み確認
        // =====================================

        console.log(
            "======================================"
        );


        console.log(
            "[CONVERTER] converter.js loaded"
        );


        console.log(
            "[CONVERTER] converterUtils:",
            window.converterUtils
        );


        console.log(
            "[CONVERTER] converterStatus:",
            window.converterStatus
        );


        console.log(
            "[CONVERTER] converterState:",
            window.converterState
        );


        console.log(
            "[CONVERTER] start:",
            typeof
                window.converterMain.start
        );


        console.log(
            "[CONVERTER] addSrtInfo:",
            typeof
                window.converterMain.addSrtInfo
        );


        console.log(
            "[CONVERTER] addSubtitleEmbedFile:",
            typeof
                window.converterMain.addSubtitleEmbedFile
        );


        console.log(
            "[CONVERTER] addSubtitleEmbedInfo:",
            typeof
                window.converterMain.addSubtitleEmbedInfo
        );


        console.log(
            "======================================"
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
            initializeConverterMain,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeConverterMain();

    }


})();
