// =====================================
// YouTube Converter - Status Manager
// =====================================

(function () {

    "use strict";


    // =====================================
    // グローバル名前空間
    // =====================================

    window.ConverterStatus =
        window.ConverterStatus || {};



    // =====================================
    // 内部状態
    // =====================================

    let currentJobId = null;

    let statusTimer = null;

    let stopped = false;


    // =====================================
    // 再試行状態
    //
    // 429 / jobなしの場合
    //
    // 15秒
    // ↓
    // 30秒
    // ↓
    // 60秒
    // ↓
    // 120秒
    //
    // 以降は120秒
    // =====================================

    const retryDelays = [
        15000,
        30000,
        60000,
        120000
    ];


    let retryIndex = 0;



    // =====================================
    // コールバック
    // =====================================

    let callbacks = {

        onRunning: null,

        onComplete: null,

        onError: null,

        onStatus: null,

        onRetry: null

    };



    // =====================================
    // ログ
    // =====================================

    function log() {

        console.log(
            "[ConverterStatus]",
            ...arguments
        );

    }



    // =====================================
    // 警告ログ
    // =====================================

    function warn() {

        console.warn(
            "[ConverterStatus]",
            ...arguments
        );

    }



    // =====================================
    // エラーログ
    // =====================================

    function errorLog() {

        console.error(
            "[ConverterStatus]",
            ...arguments
        );

    }



    // =====================================
    // タイマー停止
    // =====================================

    function clearStatusTimer() {

        if (statusTimer) {

            clearTimeout(
                statusTimer
            );

            statusTimer =
                null;

        }

    }



    // =====================================
    // 完全停止
    // =====================================

    function stop() {

        stopped =
            true;


        clearStatusTimer();


        currentJobId =
            null;


        retryIndex =
            0;


        log(
            "STATUS監視停止"
        );

    }



    // =====================================
    // 再試行時間取得
    // =====================================

    function getRetryDelay() {

        if (
            retryIndex < 0
        ) {

            retryIndex =
                0;

        }


        if (
            retryIndex >=
            retryDelays.length
        ) {

            return (
                retryDelays[
                    retryDelays.length - 1
                ]
            );

        }


        return (
            retryDelays[
                retryIndex
            ]
        );

    }



    // =====================================
    // 再試行時間を次へ進める
    // =====================================

    function increaseRetryIndex() {

        if (
            retryIndex <
            retryDelays.length - 1
        ) {

            retryIndex++;

        }

    }



    // =====================================
    // 正常通信ができたら
    // 再試行状態をリセット
    // =====================================

    function resetRetryIndex() {

        retryIndex =
            0;

    }



    // =====================================
    // 再試行予約
    // =====================================

    function scheduleRetry(
        reason
    ) {

        if (stopped) {

            return;

        }


        if (!currentJobId) {

            return;

        }


        clearStatusTimer();


        const delay =
            getRetryDelay();


        const seconds =
            Math.floor(
                delay / 1000
            );


        warn(
            reason,
            "→",
            seconds + "秒後にSTATUS再確認"
        );


        if (
            typeof callbacks.onRetry ===
            "function"
        ) {

            try {

                callbacks.onRetry(
                    {
                        reason:
                            reason,

                        delay:
                            delay,

                        seconds:
                            seconds,

                        retryIndex:
                            retryIndex
                    }
                );

            }
            catch (
                callbackError
            ) {

                errorLog(
                    "onRetry callback error:",
                    callbackError
                );

            }

        }


        statusTimer =
            setTimeout(
                function () {

                    if (stopped) {

                        return;

                    }


                    checkStatus();

                },
                delay
            );


        increaseRetryIndex();

    }



    // =====================================
    // 通常監視
    //
    // queued / running
    // =====================================

    function scheduleNormalCheck() {

        if (stopped) {

            return;

        }


        if (!currentJobId) {

            return;

        }


        clearStatusTimer();


        statusTimer =
            setTimeout(
                function () {

                    if (stopped) {

                        return;

                    }


                    checkStatus();

                },
                5000
            );

    }



    // =====================================
    // JSONレスポンス取得
    // =====================================

    async function readJsonResponse(
        response
    ) {

        const text =
            await response.text();


        if (!text) {

            return null;

        }


        try {

            return JSON.parse(
                text
            );

        }
        catch (
            parseError
        ) {

            errorLog(
                "STATUS JSON解析エラー:",
                parseError
            );


            errorLog(
                "STATUSレスポンス:",
                text
            );


            return null;

        }

    }



    // =====================================
    // STATUS確認
    // =====================================

    async function checkStatus() {

        if (stopped) {

            return;

        }


        if (!currentJobId) {

            return;

        }


        const jobId =
            currentJobId;


        try {

            log(
                "STATUS確認:",
                jobId
            );


            const response =
                await fetch(
                    `/status/${encodeURIComponent(jobId)}`,
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
                response.status ===
                429
            ) {

                warn(
                    "STATUS HTTP 429"
                );


                scheduleRetry(
                    "HTTP 429 Rate Limit / Cloudflare"
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

                warn(
                    "一時的なRenderエラー:",
                    response.status
                );


                // Render系は通常5秒後
                // ただし連続429の待機状態とは
                // 別扱いにする
                scheduleNormalCheck();


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
                        "STATUS取得に失敗しました"
                    )
                );

            }



            // =================================
            // JSON取得
            // =================================

            const data =
                await readJsonResponse(
                    response
                );


            if (!data) {

                warn(
                    "STATUSが空、またはJSONではありません"
                );


                scheduleNormalCheck();


                return;

            }



            // =================================
            // STATUSログ
            // =================================

            log(
                "STATUS:",
                data
            );



            // =================================
            // 正常なSTATUSを取得できた
            //
            // 429 / jobなし等で進んでいた
            // 再試行カウンタをリセット
            // =================================

            if (
                data.status !==
                "error"
            ) {

                resetRetryIndex();

            }



            // =================================
            // 外部通知
            // =================================

            if (
                typeof callbacks.onStatus ===
                "function"
            ) {

                try {

                    callbacks.onStatus(
                        data
                    );

                }
                catch (
                    callbackError
                ) {

                    errorLog(
                        "onStatus callback error:",
                        callbackError
                    );

                }

            }



            // =================================
            // 完了
            // =================================

            if (
                data.status ===
                "complete"
            ) {

                clearStatusTimer();


                const completedJobId =
                    currentJobId;


                currentJobId =
                    null;


                retryIndex =
                    0;


                log(
                    "STATUS complete:",
                    completedJobId
                );


                if (
                    typeof callbacks.onComplete ===
                    "function"
                ) {

                    try {

                        callbacks.onComplete(
                            data
                        );

                    }
                    catch (
                        callbackError
                    ) {

                        errorLog(
                            "onComplete callback error:",
                            callbackError
                        );

                    }

                }


                return;

            }



            // =====================================
            // エラー
            // =====================================

            if (
                data.status ===
                "error"
            ) {

                const message =
                    String(
                        data.message ||
                        ""
                    );


                // =================================
                // 「jobなし」は即失敗にしない
                //
                // Render上で一時的に
                // ジョブ情報が見えなくなる場合が
                // あるため再確認する
                // =================================

                if (
                    message.includes(
                        "jobなし"
                    ) ||
                    message.includes(
                        "job がありません"
                    ) ||
                    message.includes(
                        "Job not found"
                    ) ||
                    message.includes(
                        "job not found"
                    )
                ) {

                    warn(
                        "STATUS: jobなし",
                        "job_id:",
                        jobId
                    );


                    scheduleRetry(
                        "jobなし"
                    );


                    return;

                }



                // =================================
                // その他のエラー
                // =================================

                clearStatusTimer();


                const errorData =
                    data;


                currentJobId =
                    null;


                retryIndex =
                    0;


                errorLog(
                    "STATUS error:",
                    errorData
                );


                if (
                    typeof callbacks.onError ===
                    "function"
                ) {

                    try {

                        callbacks.onError(
                            errorData
                        );

                    }
                    catch (
                        callbackError
                    ) {

                        errorLog(
                            "onError callback error:",
                            callbackError
                        );

                    }

                }


                return;

            }



            // =================================
            // running
            // =================================

            if (
                data.status ===
                "running"
            ) {

                if (
                    typeof callbacks.onRunning ===
                    "function"
                ) {

                    try {

                        callbacks.onRunning(
                            data
                        );

                    }
                    catch (
                        callbackError
                    ) {

                        errorLog(
                            "onRunning callback error:",
                            callbackError
                        );

                    }

                }


                scheduleNormalCheck();


                return;

            }



            // =================================
            // queued
            // =================================

            if (
                data.status ===
                "queued"
            ) {

                if (
                    typeof callbacks.onRunning ===
                    "function"
                ) {

                    try {

                        callbacks.onRunning(
                            data
                        );

                    }
                    catch (
                        callbackError
                    ) {

                        errorLog(
                            "onRunning callback error:",
                            callbackError
                        );

                    }

                }


                scheduleNormalCheck();


                return;

            }



            // =================================
            // 不明なSTATUS
            // =================================

            warn(
                "未知のSTATUS:",
                data.status
            );


            scheduleNormalCheck();

        }
        catch (
            fetchError
        ) {

            errorLog(
                "変換状態確認エラー:",
                fetchError
            );


            // =================================
            // ネットワークエラー
            // =================================
            //
            // ここでは即エラーにせず
            // 5秒後に再確認
            // =================================

            scheduleNormalCheck();

        }

    }



    // =====================================
    // 監視開始
    // =====================================

    function start(
        jobId,
        options
    ) {

        // =================================
        // 既存監視を停止
        // =================================

        clearStatusTimer();


        currentJobId =
            jobId;


        stopped =
            false;


        retryIndex =
            0;



        // =================================
        // コールバック設定
        // =================================

        options =
            options || {};


        callbacks = {

            onRunning:
                typeof options.onRunning ===
                "function"
                    ? options.onRunning
                    : null,

            onComplete:
                typeof options.onComplete ===
                "function"
                    ? options.onComplete
                    : null,

            onError:
                typeof options.onError ===
                "function"
                    ? options.onError
                    : null,

            onStatus:
                typeof options.onStatus ===
                "function"
                    ? options.onStatus
                    : null,

            onRetry:
                typeof options.onRetry ===
                "function"
                    ? options.onRetry
                    : null

        };


        if (!currentJobId) {

            errorLog(
                "JOB IDがありません"
            );


            return;

        }


        log(
            "STATUS監視開始:",
            currentJobId
        );


        checkStatus();

    }



    // =====================================
    // 現在のJOB ID
    // =====================================

    function getJobId() {

        return currentJobId;

    }



    // =====================================
    // 再試行状態
    // =====================================

    function getRetryInfo() {

        return {

            retryIndex:
                retryIndex,

            nextDelay:
                getRetryDelay(),

            nextDelaySeconds:
                Math.floor(
                    getRetryDelay() / 1000
                )

        };

    }



    // =====================================
    // 外部公開
    // =====================================

    ConverterStatus.start =
        start;


    ConverterStatus.stop =
        stop;


    ConverterStatus.getJobId =
        getJobId;


    ConverterStatus.getRetryInfo =
        getRetryInfo;



    // =====================================
    // 読み込み確認
    // =====================================

    console.log(
        "converter-status.js loaded"
    );

})();
