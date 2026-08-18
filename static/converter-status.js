// =====================================
// YouTube Converter
// converter-status.js
//
// STATUS監視専用
//
// ・/status/{job_id}
// ・queued
// ・running
// ・complete
// ・error
// ・429
// ・502 / 503 / 504
// ・jobなし
// =====================================

(function () {

    "use strict";


    // =====================================
    // 設定
    // =====================================

    const STATUS_INTERVAL =
        5000;


    const RATE_LIMIT_INTERVAL =
        15000;


    const SERVER_ERROR_INTERVAL =
        5000;


    // =====================================
    // 監視中かどうか
    // =====================================

    let monitoring = false;


    // =====================================
    // 現在監視しているJOB
    // =====================================

    let monitoringJobId = null;


    // =====================================
    // タイマー
    // =====================================

    let statusTimer = null;


    // =====================================
    // jobなし対策
    //
    // 1回だけなら一時的な可能性があるので
    // すぐ終了しない。
    //
    // ただし連続するとJOB消失と判断する。
    // =====================================

    let jobNotFoundCount = 0;


    const MAX_JOB_NOT_FOUND =
        3;



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
    // 次回STATUS確認
    // =====================================

    function scheduleStatus(
        delay
    ) {

        clearStatusTimer();


        if (!monitoring) {
            return;
        }


        statusTimer =
            setTimeout(
                function () {

                    checkStatus();

                },
                delay
            );

    }



    // =====================================
    // STATUS監視開始
    // =====================================

    function start(
        jobId
    ) {

        // ---------------------------------
        // JOB ID確認
        // ---------------------------------

        if (!jobId) {

            console.error(
                "STATUS監視開始失敗: job_idがありません"
            );

            return;

        }


        // ---------------------------------
        // 以前の監視停止
        // ---------------------------------

        clearStatusTimer();


        // ---------------------------------
        // 初期化
        // ---------------------------------

        monitoring =
            true;


        monitoringJobId =
            jobId;


        jobNotFoundCount =
            0;


        console.log(
            "STATUS監視開始:",
            jobId
        );


        // ---------------------------------
        // すぐ1回確認
        // ---------------------------------

        checkStatus();

    }



    // =====================================
    // STATUS監視停止
    // =====================================

    function stop() {

        monitoring =
            false;


        monitoringJobId =
            null;


        jobNotFoundCount =
            0;


        clearStatusTimer();


        console.log(
            "STATUS監視停止"
        );

    }



    // =====================================
    // STATUS確認
    // =====================================

    async function checkStatus() {

        // ---------------------------------
        // 監視状態確認
        // ---------------------------------

        if (!monitoring) {
            return;
        }


        if (!monitoringJobId) {

            console.warn(
                "STATUS監視: job_idがありません"
            );

            stop();

            return;

        }


        const jobId =
            monitoringJobId;



        try {

            // =================================
            // STATUS API
            // =================================

            const response =
                await fetch(

                    "/status/"
                    +
                    encodeURIComponent(
                        jobId
                    ),

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


                scheduleStatus(
                    RATE_LIMIT_INTERVAL
                );


                return;

            }



            // =================================
            // Render一時エラー
            //
            // 502
            // 503
            // 504
            // =================================

            if (

                response.status === 502 ||
                response.status === 503 ||
                response.status === 504

            ) {

                console.warn(
                    "一時的なサーバーエラー:",
                    response.status
                );


                scheduleStatus(
                    SERVER_ERROR_INTERVAL
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
                        "STATUS取得に失敗しました"
                    )

                );

            }



            // =================================
            // レスポンス取得
            // =================================

            const text =
                await response.text();


            // ---------------------------------
            // 空レスポンス
            // ---------------------------------

            if (!text) {

                console.warn(
                    "STATUS: 空レスポンス"
                );


                scheduleStatus(
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


                // 一時的なレスポンス異常として
                // 監視を継続

                scheduleStatus(
                    STATUS_INTERVAL
                );


                return;

            }



            // =================================
            // ログ
            // =================================

            console.log(
                "STATUS:",
                data
            );



            // =================================
            // jobなし
            // =================================

            if (

                data.status ===
                    "error" &&

                (
                    data.message ===
                        "jobなし" ||

                    data.message ===
                        "Job not found" ||

                    data.message ===
                        "job not found"

                )

            ) {

                jobNotFoundCount++;


                console.warn(

                    "STATUS: jobなし",

                    jobNotFoundCount
                    +
                    "/"
                    +
                    MAX_JOB_NOT_FOUND

                );


                // ---------------------------------
                // まだJOB消失と確定しない
                // ---------------------------------

                if (
                    jobNotFoundCount <
                    MAX_JOB_NOT_FOUND
                ) {

                    scheduleStatus(
                        STATUS_INTERVAL
                    );


                    return;

                }



                // ---------------------------------
                // JOB消失確定
                // ---------------------------------

                console.error(
                    "STATUS: JOBが見つからない状態が続いています"
                );


                stop();


                if (
                    window.converterMain &&
                    typeof
                        window.converterMain.stopTimer ===
                        "function"
                ) {

                    window.converterMain.stopTimer();

                }


                resetConvertButton();


                alert(
                    "変換JOBが見つからなくなりました。"
                    +
                    "\n"
                    +
                    "もう一度「実行」してください。"
                );


                return;

            }



            // =====================================
            // jobなし以外の正常レスポンス
            //
            // ここまで来たらカウントをリセット
            // =====================================

            jobNotFoundCount =
                0;



            // =================================
            // complete
            // =================================

            if (

                data.status ===
                    "complete"

            ) {

                console.log(
                    "STATUS: 変換完了"
                );


                stop();


                // ---------------------------------
                // メイン側のタイマー停止
                // ---------------------------------

                if (
                    window.converterMain &&
                    typeof
                        window.converterMain.stopTimer ===
                        "function"
                ) {

                    window.converterMain.stopTimer();

                }



                // ---------------------------------
                // 動画情報更新
                // ---------------------------------

                if (
                    window.converterState
                ) {

                    if (
                        data.title ||
                        data.video_title
                    ) {

                        window.converterState.currentVideoTitle =

                            data.title ||
                            data.video_title ||
                            window.converterState.currentVideoTitle;

                    }


                    if (
                        data.duration ||
                        data.video_duration
                    ) {

                        window.converterState.currentVideoDuration =

                            data.duration ||
                            data.video_duration ||
                            window.converterState.currentVideoDuration;

                    }

                }



                // ---------------------------------
                // ボタン非表示
                // ---------------------------------

                const convertButton =
                    document.getElementById(
                        "convertBtn"
                    );


                if (convertButton) {

                    convertButton.style.display =
                        "none";

                }



                // ---------------------------------
                // ファイル表示
                // ---------------------------------

                const files =
                    Array.isArray(
                        data.files
                    )
                        ? data.files
                        : [];


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
                        "converterMain.showFiles がありません"
                    );

                }


                return;

            }



            // =================================
            // error
            // =================================

            if (

                data.status ===
                    "error"

            ) {

                stop();


                if (
                    window.converterMain &&
                    typeof
                        window.converterMain.stopTimer ===
                        "function"
                ) {

                    window.converterMain.stopTimer();

                }


                resetConvertButton();


                const message =
                    data.message ||
                    "変換中にエラーが発生しました";


                console.error(
                    "STATUS ERROR:",
                    message
                );


                alert(
                    message
                );


                return;

            }



            // =================================
            // queued
            // =================================

            if (

                data.status ===
                    "queued"

            ) {

                console.log(
                    "STATUS: queued"
                );


                scheduleStatus(
                    STATUS_INTERVAL
                );


                return;

            }



            // =================================
            // running
            // =================================

            if (

                data.status ===
                    "running"

            ) {

                console.log(
                    "STATUS: running"
                );


                scheduleStatus(
                    STATUS_INTERVAL
                );


                return;

            }



            // =================================
            // status不明
            // =================================

            console.warn(
                "STATUS: 未知のstatus:",
                data.status
            );


            // ---------------------------------
            // statusが不明でも
            // すぐエラーにはしない
            // ---------------------------------

            scheduleStatus(
                STATUS_INTERVAL
            );

        }
        catch (error) {

            // =================================
            // ネットワークエラー
            // =================================

            console.error(
                "変換状態確認エラー:",
                error
            );


            // ---------------------------------
            // 監視は継続
            // ---------------------------------

            if (monitoring) {

                scheduleStatus(
                    STATUS_INTERVAL
                );

            }

        }

    }



    // =====================================
    // 実行ボタンを初期状態へ
    // =====================================

    function resetConvertButton() {

        const convertButton =
            document.getElementById(
                "convertBtn"
            );


        if (!convertButton) {
            return;
        }


        convertButton.style.display =
            "";


        convertButton.disabled =
            false;


        convertButton.innerHTML =
            "実行";

    }



    // =====================================
    // 外部公開
    // =====================================

    window.converterStatus = {

        start:
            start,

        stop:
            stop,

        check:
            checkStatus

    };


    // =====================================
    // 読み込み確認
    // =====================================

    console.log(
        "converter-status.js loaded"
    );

})();
