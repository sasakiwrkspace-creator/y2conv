// =====================================
// YouTube Converter - Status
// converter-status.js
//
// ・JOB STATUS確認
// ・HTMLへ現在の処理状態を表示
// ・queued / running / complete / error
// ・429 / 502 / 503 / 504 対応
// ・JOBなしの一時的な消失に対応
// ・ネットワークエラーでも変換を終了扱いにしない
// ・完了時に converter.js の showFiles()
// ・処理中は画面表示を変更しない
// ・実行開始時 / タイトル取得時 / 完了時 / エラー時だけ表示を変更
//
// 共通関数
// ・converter-utils.js
//
// メイン処理
// ・converter.js
//
// =====================================


// =====================================
// 変換状態
// =====================================

let statusCurrentJobId = null;

let statusTimer = null;

let statusRetryCount = 0;


// =====================================
// JOBなし最大リトライ
// =====================================

const MAX_JOB_NOT_FOUND_RETRY = 60;


// =====================================
// STATUS確認間隔
// =====================================

const STATUS_INTERVAL = 5;


// =====================================
// Rate Limit時
// =====================================

const RATE_LIMIT_INTERVAL = 15;


// =====================================
// Render一時エラー時
// =====================================

const RENDER_ERROR_INTERVAL = 10;


// =====================================
// JOBなし時
// =====================================

const JOB_NOT_FOUND_INTERVAL = 5;


// =====================================
// DOM取得
// =====================================

function getConvertButton() {

    return document.getElementById(
        "convertBtn"
    );

}


function getDownloadArea() {

    return document.getElementById(
        "downloadArea"
    );

}


function getStatusArea() {

    return document.getElementById(
        "conversion-status-area"
    );

}


// =====================================
// HTMLエスケープ
//
// 共通関数は converter-utils.js を使用
// =====================================

function escapeStatusHtml(
    value
) {

    if (
        window.converterUtils &&
        typeof
            window.converterUtils.escapeHtml ===
            "function"
    ) {

        return window.converterUtils.escapeHtml(
            value
        );

    }


    return String(
        value === null ||
        value === undefined
            ? ""
            : value
    );

}


// =====================================
// HTMLへ処理状況を表示
// =====================================

function updateStatus(
    message,
    type = "running"
) {

    const area =
        getStatusArea();


    if (!area) {

        console.warn(
            "[STATUS UI] conversion-status-area がありません"
        );

        return;

    }


    area.style.display =
        "block";


    area.className =
        "conversion-status-area conversion-status-" +
        type;


    area.innerHTML = `

        <div class="conversion-status-icon">

            ${getStatusIcon(type)}

        </div>

        <div class="conversion-status-message">

            ${escapeStatusHtml(message)}

        </div>

    `;

}


// =====================================
// ステータスアイコン
// =====================================

function getStatusIcon(
    type
) {

    if (
        type === "complete"
    ) {

        return "✓";

    }


    if (
        type === "error"
    ) {

        return "✕";

    }


    if (
        type === "waiting"
    ) {

        return "⏳";

    }


    return "●";

}


// =====================================
// 動画タイトル更新
// =====================================
//
// /status APIからタイトルを取得した場合、
// converterStateへ保存する。
//
// 画面表示については converter.js の
// converter-processing-status を使用する。
// =====================================

function updateVideoTitle(
    title
) {

    const videoTitle =
        String(
            title || ""
        ).trim();


    if (
        !videoTitle
    ) {

        return;

    }


    // =================================
    // converterStateへ保存
    // =================================

    if (
        window.converterState
    ) {

        window.converterState.currentVideoTitle =
            videoTitle;

    }


    console.log(
        "[STATUS] 動画タイトル取得:",
        videoTitle
    );


    // =================================
    // converter.js側の
    // 処理ステータスへ反映
    // =================================

    if (
        window.converterMain &&
        typeof
            window.converterMain.updateProcessingStatus ===
            "function"
    ) {

        window.converterMain.updateProcessingStatus(
            "convert",
            "ファイルを作成しています...",
            {

                title:
                    "実行中・・・",

                videoTitle:
                    videoTitle

            }
        );

    }

}


// =====================================
// 動画再生時間を保存
// =====================================

function updateVideoDuration(
    duration
) {

    if (
        duration === undefined ||
        duration === null ||
        duration === ""
    ) {

        return;

    }


    if (
        window.converterState
    ) {

        window.converterState.currentVideoDuration =
            duration;

    }


    console.log(
        "[STATUS] 動画再生時間:",
        duration
    );

}


// =====================================
// メイン処理ステータス表示
//
// converter.js側の
// converter-processing-status
// を使用する。
// =====================================

function updateMainProcessingStatus(
    message,
    type,
    options
) {

    if (
        !window.converterMain ||
        typeof
            window.converterMain.updateProcessingStatus !==
            "function"
    ) {

        return;

    }


    options =
        options || {};


    // =================================
    // 完了
    // =================================

    if (
        type === "complete"
    ) {

        window.converterMain.updateProcessingStatus(
            "success",
            message ||
                "処理が完了しました。",
            options
        );

        return;

    }


    // =================================
    // エラー
    // =================================

    if (
        type === "error"
    ) {

        window.converterMain.updateProcessingStatus(
            "error",
            message ||
                "処理中にエラーが発生しました。",
            options
        );

        return;

    }


    // =================================
    // 通常処理中
    // =================================

    window.converterMain.updateProcessingStatus(
        "convert",
        message ||
            "処理を実行中です...",
        {

            title:
                options.title ||
                "実行中・・・",

            videoTitle:
                options.videoTitle ||
                (
                    window.converterState
                        ? window.converterState.currentVideoTitle
                        : ""
                )

        }
    );

}


// =====================================
// 実行開始表示
// =====================================

function showRunningState() {

    console.log(
        "[STATUS UI] 実行中表示"
    );


    const state =
        window.converterState
            ? window.converterState
            : null;


    const videoTitle =
        state
            ? state.currentVideoTitle
            : "";


    updateMainProcessingStatus(
        "MP3 / MP4を作成しています...",
        "running",
        {

            title:
                "実行中・・・",

            videoTitle:
                videoTitle

        }
    );


    updateStatus(
        "MP3 / MP4を作成しています...",
        "running"
    );

}


// =====================================
// 完了表示
// =====================================

function showCompleteState(
    message
) {

    const finalMessage =
        message ||
        "MP3 / MP4の作成が完了しました。";


    console.log(
        "[STATUS UI] 完了表示:",
        finalMessage
    );


    const state =
        window.converterState
            ? window.converterState
            : null;


    updateMainProcessingStatus(
        finalMessage,
        "complete",
        {

            videoTitle:
                state
                    ? state.currentVideoTitle
                    : ""

        }
    );


    updateStatus(
        finalMessage,
        "complete"
    );

}


// =====================================
// エラー表示
// =====================================

function showErrorState(
    message
) {

    const finalMessage =
        message ||
        "変換中にエラーが発生しました。";


    console.error(
        "[STATUS UI] エラー表示:",
        finalMessage
    );


    const state =
        window.converterState
            ? window.converterState
            : null;


    updateMainProcessingStatus(
        finalMessage,
        "error",
        {

            videoTitle:
                state
                    ? state.currentVideoTitle
                    : ""

        }
    );


    updateStatus(
        finalMessage,
        "error"
    );

}


// =====================================
// 待機・接続エラー表示
//
// 処理そのものを終了しない。
// メインの「実行中・・・」表示も
// 変更しない。
// =====================================

function keepRunningDisplay() {

    console.log(
        "[STATUS UI] 実行中表示を維持"
    );

}


// =====================================
// メインタイマー停止
// =====================================

function stopMainTimer() {

    if (
        window.converterMain &&
        typeof
            window.converterMain.stopTimer ===
            "function"
    ) {

        window.converterMain.stopTimer();

    }

}


// =====================================
// 次回STATUS確認予約
// =====================================

function scheduleStatusCheck(
    seconds
) {

    if (
        statusTimer
    ) {

        clearTimeout(
            statusTimer
        );

    }


    statusTimer =
        setTimeout(
            function () {

                statusTimer =
                    null;

                checkStatus();

            },
            seconds * 1000
        );

}


// =====================================
// STATUS確認停止
// =====================================

function stopStatusPolling() {

    if (
        statusTimer
    ) {

        clearTimeout(
            statusTimer
        );

        statusTimer =
            null;

    }

}


// =====================================
// JOB ID設定
// =====================================

function setJobId(
    jobId
) {

    statusCurrentJobId =
        jobId || null;


    statusRetryCount =
        0;

}


// =====================================
// JOB ID取得
// =====================================

function getJobId() {

    return statusCurrentJobId;

}


// =====================================
// STATUS開始
// =====================================

function start(
    jobId
) {

    stopStatusPolling();


    setJobId(
        jobId
    );


    if (
        !statusCurrentJobId
    ) {

        console.error(
            "[STATUS] 開始失敗: JOB IDがありません"
        );


        showErrorState(
            "変換JOBを開始できませんでした。"
        );


        return;

    }


    console.log(
        "======================================"
    );


    console.log(
        "[STATUS] 監視開始"
    );


    console.log(
        "[STATUS] JOB ID:",
        statusCurrentJobId
    );


    console.log(
        "======================================"
    );


    // =================================
    // 実行開始時だけ画面表示
    // =================================

    showRunningState();


    // =================================
    // STATUS確認開始
    // =================================

    checkStatus();

}


// =====================================
// STATUS確認
// =====================================

async function checkStatus() {

    const jobId =
        statusCurrentJobId;


    if (
        !jobId
    ) {

        console.warn(
            "[STATUS] JOB IDがありません"
        );


        return;

    }


    console.log(
        "[STATUS] 確認:",
        jobId
    );


    try {

        // =================================
        // STATUS API
        // =================================

        const statusUrl =
            `/status/${encodeURIComponent(
                jobId
            )}`;


        console.log(
            "[STATUS REQUEST]",
            statusUrl
        );


        const response =
            await fetch(
                statusUrl,
                {

                    method:
                        "GET",

                    cache:
                        "no-store",

                    headers: {

                        "Cache-Control":
                            "no-cache",

                        "Pragma":
                            "no-cache"

                    }

                }
            );


        console.log(
            "[STATUS RESPONSE]",
            {

                status:
                    response.status,

                ok:
                    response.ok,

                url:
                    response.url

            }
        );


        // =================================
        // 429 Rate Limit
        // =================================

        if (
            response.status === 429
        ) {

            console.warn(
                "[STATUS] 429 Rate Limit"
            );


            keepRunningDisplay();


            scheduleStatusCheck(
                RATE_LIMIT_INTERVAL
            );


            return;

        }


        // =================================
        // 502 / 503 / 504
        // =================================

        if (
            response.status === 502 ||
            response.status === 503 ||
            response.status === 504
        ) {

            console.warn(
                "[STATUS] 一時的なRenderエラー:",
                response.status
            );


            keepRunningDisplay();


            scheduleStatusCheck(
                RENDER_ERROR_INTERVAL
            );


            return;

        }


        // =================================
        // その他HTTPエラー
        // =================================

        if (
            !response.ok
        ) {

            const text =
                await response.text();


            console.error(
                "[STATUS] HTTPエラー:",
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
        // レスポンス本文
        // =================================

        const text =
            await response.text();


        console.log(
            "[STATUS RAW RESPONSE]",
            text
        );


        if (
            !text
        ) {

            console.warn(
                "[STATUS] 空レスポンス"
            );


            keepRunningDisplay();


            scheduleStatusCheck(
                STATUS_INTERVAL
            );


            return;

        }


        // =================================
        // JSON
        // =================================

        let data;


        try {

            data =
                JSON.parse(
                    text
                );

        }
        catch (
            error
        ) {

            console.error(
                "[STATUS] JSON解析エラー:",
                error
            );


            console.error(
                "[STATUS] レスポンス:",
                text
            );


            // JSONエラーでもJOB終了扱いにしない

            keepRunningDisplay();


            scheduleStatusCheck(
                STATUS_INTERVAL
            );


            return;

        }


        console.log(
            "======================================"
        );


        console.log(
            "[STATUS DATA]",
            data
        );


        console.log(
            "status:",
            data.status
        );


        console.log(
            "stage:",
            data.stage ||
            data.current_stage ||
            data.step ||
            data.current_step ||
            ""
        );


        console.log(
            "title:",
            data.title ||
            data.video_title ||
            ""
        );


        console.log(
            "duration:",
            data.duration ||
            data.video_duration ||
            ""
        );


        console.log(
            "files:",
            data.files
        );


        console.log(
            "======================================"
        );


        // =================================
        // JOBなし
        // =================================

        if (
            data.status === "error" &&
            data.message === "jobなし"
        ) {

            statusRetryCount++;


            console.warn(
                "[STATUS] JOBなし:",
                jobId,
                "retry:",
                statusRetryCount,
                "/",
                MAX_JOB_NOT_FOUND_RETRY
            );


            if (
                statusRetryCount <=
                MAX_JOB_NOT_FOUND_RETRY
            ) {

                keepRunningDisplay();


                scheduleStatusCheck(
                    JOB_NOT_FOUND_INTERVAL
                );


                return;

            }


            // =================================
            // 長時間JOBなし
            // =================================

            console.error(
                "[STATUS] JOBなしが長時間継続しました"
            );


            stopStatusPolling();


            stopMainTimer();


            const button =
                getConvertButton();


            if (
                button
            ) {

                button.disabled =
                    false;

                button.style.display =
                    "";

                button.innerHTML =
                    "実行";

            }


            showErrorState(
                "変換JOBを長時間確認できませんでした。もう一度実行してください。"
            );


            return;

        }


        // =================================
        // 正常JOB取得
        // =================================

        statusRetryCount =
            0;


        // =================================
        // タイトル
        //
        // STATUSで取得できた瞬間に
        // converterStateへ保存し、
        // converter.jsの表示へ反映
        // =================================

        const videoTitle =
            data.title ||
            data.video_title ||
            "";


        if (
            videoTitle
        ) {

            updateVideoTitle(
                videoTitle
            );

        }


        // =================================
        // 再生時間
        // =================================

        const videoDuration =
            data.duration ||
            data.video_duration ||
            "";


        if (
            videoDuration
        ) {

            updateVideoDuration(
                videoDuration
            );

        }


        // =================================
        // queued
        //
        // 画面表示は変更しない
        // =================================

        if (
            data.status === "queued"
        ) {

            console.log(
                "[STATUS] queued"
            );


            keepRunningDisplay();


            scheduleStatusCheck(
                STATUS_INTERVAL
            );


            return;

        }


        // =================================
        // running
        //
        // 画面表示は変更しない
        // =================================

        if (
            data.status === "running"
        ) {

            console.log(
                "[STATUS] running"
            );


            keepRunningDisplay();


            scheduleStatusCheck(
                STATUS_INTERVAL
            );


            return;

        }


        // =================================
        // complete
        // =================================

        if (
            data.status === "complete"
        ) {

            console.log(
                "======================================"
            );


            console.log(
                "[STATUS] JOB完了:",
                jobId
            );


            console.log(
                "[STATUS] files:",
                data.files
            );


            console.log(
                "======================================"
            );


            // =================================
            // STATUS停止
            // =================================

            stopStatusPolling();


            // =================================
            // メインタイマー停止
            // =================================

            stopMainTimer();


            // =================================
            // 最新タイトル取得
            // =================================

            const completedTitle =
                data.title ||
                data.video_title ||
                (
                    window.converterState
                        ? window.converterState.currentVideoTitle
                        : ""
                );


            if (
                completedTitle
            ) {

                if (
                    window.converterState
                ) {

                    window.converterState.currentVideoTitle =
                        completedTitle;

                }

            }


            // =================================
            // 完了表示
            // =================================

            showCompleteState(
                "MP3 / MP4の作成が完了しました。"
            );


            // =================================
            // ボタン非表示
            // =================================

            const button =
                getConvertButton();


            if (
                button
            ) {

                button.style.display =
                    "none";

            }


            // =================================
            // files
            // =================================

            const files =
                Array.isArray(
                    data.files
                )
                    ? data.files
                    : [];


            if (
                files.length === 0
            ) {

                console.warn(
                    "[STATUS] JOBはcompleteですがfilesが空です"
                );

            }


            // =================================
            // converter.js
            // showFiles()
            // =================================

            if (
                window.converterMain &&
                typeof
                    window.converterMain.showFiles ===
                    "function"
            ) {

                console.log(
                    "[STATUS] converterMain.showFiles() 実行"
                );


                window.converterMain.showFiles(
                    files,
                    data
                );

            }
            else {

                console.error(
                    "[STATUS] converterMain.showFiles() がありません"
                );

            }


            return;

        }


        // =================================
        // error
        // =================================

        if (
            data.status === "error"
        ) {

            console.error(
                "======================================"
            );


            console.error(
                "[STATUS] JOBエラー:",
                data.message
            );


            console.error(
                "[STATUS] DATA:",
                data
            );


            console.error(
                "======================================"
            );


            stopStatusPolling();


            stopMainTimer();


            const button =
                getConvertButton();


            if (
                button
            ) {

                button.style.display =
                    "";

                button.disabled =
                    false;

                button.innerHTML =
                    "実行";

            }


            showErrorState(
                data.message ||
                "変換中にエラーが発生しました。"
            );


            alert(
                data.message ||
                "変換中にエラーが発生しました。"
            );


            return;

        }


        // =================================
        // 不明なSTATUS
        // =================================

        console.warn(
            "[STATUS] 未知のSTATUS:",
            data.status
        );


        // 未知のSTATUSでも終了扱いにしない

        keepRunningDisplay();


        scheduleStatusCheck(
            STATUS_INTERVAL
        );

    }

    catch (
        error
    ) {

        console.error(
            "======================================"
        );


        console.error(
            "[STATUS] 変換状態確認エラー:",
            error
        );


        console.error(
            "======================================"
        );


        // =================================
        // ネットワークエラー
        //
        // 変換終了扱いにしない
        // =================================

        keepRunningDisplay();


        scheduleStatusCheck(
            STATUS_INTERVAL
        );

    }

}


// =====================================
// 外部公開
// =====================================

window.converterStatus = {

    start:
        start,

    checkStatus:
        checkStatus,

    stop:
        stopStatusPolling,

    setJobId:
        setJobId,

    getJobId:
        getJobId,

    updateStatus:
        updateStatus,

    updateVideoTitle:
        updateVideoTitle,

    updateVideoDuration:
        updateVideoDuration

};


// =====================================
// 大文字版互換
// =====================================

window.ConverterStatus =
    window.converterStatus;


// =====================================
// 読み込み確認
// =====================================

console.log(
    "converter-status.js loaded"
);
