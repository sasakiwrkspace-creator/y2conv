// =====================================
// YouTube Converter - Status
// converter-status.js
//
// ・JOB STATUS確認
// ・queued / running / complete / error
// ・429 / 502 / 503 / 504 対応
// ・JOBなしの一時的な消失に対応
// ・完了時に converter.js の showFiles()
// ・converter.js から
//   window.converterStatus.start(jobId)
//   で開始する
// =====================================


// =====================================
// 変換状態
// =====================================

let statusCurrentJobId = null;

let statusTimer = null;

let statusRetryCount = 0;


// =====================================
// 最大リトライ
//
// JOBなしが永久に続く場合に
// 無限リクエストにならないようにする
// =====================================

const MAX_JOB_NOT_FOUND_RETRY = 12;


// =====================================
// 次回確認時間
// =====================================

const STATUS_INTERVAL = 5000;

const RATE_LIMIT_INTERVAL = 15000;


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
// タイマー停止
//
// 実際の変換タイマーは
// converter.js が管理する
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
// STATUS確認開始
// =====================================

function start(
    jobId
) {

    // ---------------------------------
    // 既存ポーリング停止
    // ---------------------------------

    stopStatusPolling();


    // ---------------------------------
    // JOB ID
    // ---------------------------------

    setJobId(
        jobId
    );


    if (!statusCurrentJobId) {

        console.error(
            "STATUS開始失敗: JOB IDがありません"
        );

        return;

    }


    console.log(
        "STATUS監視開始:",
        statusCurrentJobId
    );


    // ---------------------------------
    // 即時確認
    // ---------------------------------

    checkStatus();

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
        // 429 Rate Limit
        // =================================

        if (
            response.status === 429
        ) {

            console.warn(
                "STATUS 429: Rate Limit / Cloudflare"
            );


            scheduleStatusCheck(
                RATE_LIMIT_INTERVAL
            );


            return;

        }



        // =================================
        // Render一時エラー
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


            scheduleStatusCheck(
                STATUS_INTERVAL
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
        // レスポンス取得
        // =================================

        const text =
            await response.text();


        if (!text) {

            console.warn(
                "STATUS: 空レスポンス"
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


            console.error(
                "STATUSレスポンス:",
                text
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
                statusRetryCount
            );


            // ---------------------------------
            // 一時的なJOB取得失敗
            // ---------------------------------

            if (
                statusRetryCount <=
                MAX_JOB_NOT_FOUND_RETRY
            ) {

                scheduleStatusCheck(
                    STATUS_INTERVAL
                );


                return;

            }


            // ---------------------------------
            // 一定回数を超えた場合
            // ---------------------------------

            console.error(
                "JOBなしが続いたためSTATUS監視を終了します"
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


            const downloadArea =
                getDownloadArea();


            if (downloadArea) {

                downloadArea.innerHTML = `
                    <div class="download-error">
                        変換JOBを確認できなくなりました。
                        しばらくしてから再度実行してください。
                    </div>
                `;

            }


            return;

        }



        // =================================
        // JOB正常取得
        //
        // JOBなしカウンターをリセット
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
        // queued
        // =================================

        if (
            data.status === "queued"
        ) {

            console.log(
                "JOB待機中:",
                jobId
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

            console.log(
                "JOB変換中:",
                jobId
            );


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


            // ---------------------------------
            // STATUS停止
            // ---------------------------------

            stopStatusPolling();


            // ---------------------------------
            // メインタイマー停止
            // ---------------------------------

            stopMainTimer();


            // ---------------------------------
            // ボタン非表示
            // ---------------------------------

            const button =
                getConvertButton();


            if (button) {

                button.style.display =
                    "none";

            }


            // ---------------------------------
            // ファイル
            // ---------------------------------

            const files =
                Array.isArray(
                    data.files
                )
                    ? data.files
                    : [];


            // ---------------------------------
            // converter.jsへ
            // ---------------------------------

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
                data.message ||
                "変換中にエラーが発生しました"
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
        //
        // 変換JOB自体を終了扱いにしない
        // ---------------------------------

        scheduleStatusCheck(
            STATUS_INTERVAL
        );

    }

}


// =====================================
// 外部公開
//
// converter.js は
//
// window.converterStatus.start()
// 
// を使用する
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
        getJobId

};


// =====================================
// 大文字版も互換用に残す
//
// 既存コードが
// window.ConverterStatus
// を使っていても動くようにする
// =====================================

window.ConverterStatus =
    window.converterStatus;


// =====================================
// 読み込み確認
// =====================================

console.log(
    "converter-status.js loaded"
);
