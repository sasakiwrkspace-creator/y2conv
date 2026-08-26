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


// =====================================
// HTML処理状況表示
// =====================================

function getStatusArea() {

    return document.getElementById(
        "conversion-status-area"
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

            ${escapeHtml(message)}

        </div>

    `;

}


// =====================================
// ステータスアイコン
// =====================================

function getStatusIcon(type) {

    if (type === "complete") {

        return "✓";

    }


    if (type === "error") {

        return "✕";

    }


    if (type === "waiting") {

        return "⏳";

    }


    return "●";

}


// =====================================
// HTMLエスケープ
// =====================================

function escapeHtml(value) {

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


    return String(value ?? "")
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
// タイマー停止
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

    if (statusTimer) {

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

    if (statusTimer) {

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


    if (!statusCurrentJobId) {

        console.error(
            "STATUS開始失敗: JOB IDがありません"
        );

        updateStatus(
            "変換JOBを開始できませんでした",
            "error"
        );

        return;

    }


    console.log(
        "STATUS監視開始:",
        statusCurrentJobId
    );


    updateStatus(
        "変換処理を開始しています...",
        "running"
    );


    checkStatus();

}


// =====================================
// 現在の処理ステージを表示
// =====================================
//
// バックエンドから
//
// stage
//
// が返ってきた場合はこちらを使用。
// =====================================

function updateStageFromData(
    data
) {

    const stage =
        data.stage ||
        data.current_stage ||
        data.step ||
        data.current_step ||
        "";


    if (!stage) {

        return false;

    }


    const stageMap = {

        "download":
            "動画をダウンロード中...",

        "downloading":
            "動画をダウンロード中...",

        "mp3":
            "MP3を作成中...",

        "mp3_creating":
            "MP3を作成中...",

        "creating_mp3":
            "MP3を作成中...",

        "mp4":
            "MP4を作成中...",

        "mp4_creating":
            "MP4を作成中...",

        "creating_mp4":
            "MP4を作成中...",

        "gemini":
            "字幕ファイル（Gemini）作成中...",

        "gemini_transcribe":
            "字幕ファイル（Gemini）作成中...",

        "srt":
            "字幕ファイル（SRT）作成中...",

        "subtitle":
            "字幕ファイル（SRT）作成中...",

        "subtitle_embed":
            "字幕付きMP4を作成中...",

        "complete":
            "変換完了"

    };


    const message =
        stageMap[stage];


    if (message) {

        updateStatus(
            message,
            stage === "complete"
                ? "complete"
                : "running"
        );

        return true;

    }


    // ---------------------------------
    // バックエンドが日本語を直接返す場合
    // ---------------------------------

    if (
        typeof stage === "string" &&
        stage.length > 0
    ) {

        updateStatus(
            stage,
            "running"
        );

        return true;

    }


    return false;

}


// =====================================
// STATUS確認
// =====================================

async function checkStatus() {

    const jobId =
        statusCurrentJobId;


    if (!jobId) {

        console.warn(
            "STATUS確認: JOB IDがありません"
        );

        return;

    }


    try {

        // =================================
        // STATUS API
        // =================================

        const response =
            await fetch(
                `/status/${encodeURIComponent(
                    jobId
                )}`,
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


        // =================================
        // 429
        // =================================

        if (
            response.status === 429
        ) {

            console.warn(
                "STATUS 429: Rate Limit"
            );


            updateStatus(
                "サーバーが混雑しています。再確認中...",
                "waiting"
            );


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
                "一時的なRenderエラー:",
                response.status
            );


            updateStatus(
                "サーバーとの接続を再確認しています...",
                "waiting"
            );


            scheduleStatusCheck(
                RENDER_ERROR_INTERVAL
            );


            return;

        }


        // =================================
        // その他HTTPエラー
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
        // レスポンス
        // =================================

        const text =
            await response.text();


        if (!text) {

            console.warn(
                "STATUS: 空レスポンス"
            );


            updateStatus(
                "変換状況を確認中...",
                "waiting"
            );


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
        catch (error) {

            console.error(
                "STATUS JSON解析エラー:",
                error
            );


            updateStatus(
                "変換状況を確認中...",
                "waiting"
            );


            scheduleStatusCheck(
                STATUS_INTERVAL
            );


            return;

        }


        console.log(
            "STATUS:",
            data
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
                "JOBなし:",
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

                updateStatus(
                    "変換状況を再確認しています...",
                    "waiting"
                );


                scheduleStatusCheck(
                    JOB_NOT_FOUND_INTERVAL
                );


                return;

            }


            console.error(
                "JOBなしが長時間継続しました"
            );


            stopMainTimer();


            const button =
                getConvertButton();


            if (button) {

                button.disabled =
                    false;

                button.style.display =
                    "";

                button.innerHTML =
                    "実行";

            }


            updateStatus(
                "変換JOBを長時間確認できませんでした。もう一度実行してください。",
                "error"
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
        // =================================

        if (
            data.title ||
            data.video_title
        ) {

            if (
                window.converterState
            ) {

                window.converterState.currentVideoTitle =
                    data.title ||
                    data.video_title ||
                    "";

            }

        }


        // =================================
        // 再生時間
        // =================================

        if (
            data.duration ||
            data.video_duration
        ) {

            if (
                window.converterState
            ) {

                window.converterState.currentVideoDuration =
                    data.duration ||
                    data.video_duration ||
                    "";

            }

        }


        // =================================
        // ステージ表示
        // =================================

        const stageDisplayed =
            updateStageFromData(
                data
            );


        // =================================
        // queued
        // =================================

        if (
            data.status === "queued"
        ) {

            updateStatus(
                "変換処理を待機中...",
                "waiting"
            );


            scheduleStatusCheck(
                STATUS_INTERVAL
            );


            return;

        }


        // =================================
        // running
        // =================================

        if (
            data.status === "running"
        ) {

            // stageが返っていなければ
            // 一般的な表示

            if (!stageDisplayed) {

                updateStatus(
                    "変換中...",
                    "running"
                );

            }


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
                "JOB完了:",
                jobId
            );


            stopStatusPolling();


            stopMainTimer();


            updateStatus(
                "MP3 / MP4変換完了",
                "complete"
            );


            const button =
                getConvertButton();


            if (button) {

                button.style.display =
                    "none";

            }


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
                    "JOBはcompleteですがfilesが空です"
                );

            }


            if (
                window.converterMain &&
                typeof
                    window.converterMain.showFiles ===
                    "function"
            ) {

                window.converterMain.showFiles(
                    files,
                    data
                );

            }
            else {

                console.error(
                    "converterMain.showFiles() がありません"
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
                "JOBエラー:",
                data.message
            );


            stopStatusPolling();


            stopMainTimer();


            const button =
                getConvertButton();


            if (button) {

                button.style.display =
                    "";

                button.disabled =
                    false;

                button.innerHTML =
                    "実行";

            }


            updateStatus(
                data.message ||
                "変換中にエラーが発生しました",
                "error"
            );


            alert(
                data.message ||
                "変換中にエラーが発生しました"
            );


            return;

        }


        // =================================
        // 不明なSTATUS
        // =================================

        console.warn(
            "未知のSTATUS:",
            data.status
        );


        updateStatus(
            "変換状況を確認中...",
            "waiting"
        );


        scheduleStatusCheck(
            STATUS_INTERVAL
        );


    }
    catch (error) {

        console.error(
            "変換状態確認エラー:",
            error
        );


        // ---------------------------------
        // ネットワークエラー
        // ---------------------------------

        updateStatus(
            "サーバーとの接続を再確認しています...",
            "waiting"
        );


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
        updateStatus

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
