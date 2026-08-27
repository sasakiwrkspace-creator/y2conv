// =====================================
// YouTube Converter - Status
// converter-status.js
//
// ステータス表示と処理時間管理を担当
//
// 使用:
// ・converter-utils.js
//
// 役割:
// ・処理開始
// ・処理中メッセージ
// ・リアルタイム処理時間表示
// ・処理完了
// ・エラー表示
// ・処理時間取得
// ・ステータスクリア
//
// converter.js は
// ステータス表示を直接操作せず、
// このファイルを使用する。
//
// 共通時間フォーマットは
// converter-utils.js を使用する。
// =====================================


(function () {

    "use strict";


    // =====================================
    // 初期化
    // =====================================

    function initializeConverterStatus() {


        // =================================
        // 二重初期化防止
        // =================================

        if (
            window.converterStatus &&
            window.converterStatus.__initialized
        ) {

            console.log(
                "[STATUS] already initialized"
            );

            return;

        }



        // =====================================
        // DOM
        // =====================================

        const statusElement =
            document.getElementById(
                "converter-status"
            );


        if (
            !statusElement
        ) {

            console.warn(
                "[STATUS] converter-status が見つかりません"
            );

        }



        // =====================================
        // 処理時間管理
        // =====================================

        let processingStartTime =
            null;


        let timerId =
            null;



        // =====================================
        // Utils取得
        // =====================================

        function getUtils() {

            return window.converterUtils || null;

        }



        // =====================================
        // 経過時間フォーマット
        //
        // converter-utils.jsを使用
        // =====================================

        function formatElapsed(
            seconds
        ) {

            const utils =
                getUtils();


            if (
                utils &&
                typeof utils.formatElapsed ===
                    "function"
            ) {

                return utils.formatElapsed(
                    seconds
                );

            }


            // ---------------------------------
            // Utilsがまだない場合の
            // フォールバック
            // ---------------------------------

            const safeSeconds =
                Math.max(
                    0,
                    Math.floor(
                        Number(seconds) || 0
                    )
                );


            return (
                safeSeconds +
                "秒"
            );

        }



        // =====================================
        // ステータスDOMへ表示
        // =====================================

        function setStatus(
            message,
            type
        ) {


            if (
                !statusElement
            ) {

                return;

            }



            // ---------------------------------
            // メッセージ
            // ---------------------------------

            statusElement.textContent =
                message;


            // ---------------------------------
            // 改行維持
            // ---------------------------------

            statusElement.style.whiteSpace =
                "pre-line";


            // ---------------------------------
            // 状態クラス削除
            // ---------------------------------

            statusElement.classList.remove(
                "error",
                "success"
            );


            // ---------------------------------
            // 状態クラス追加
            // ---------------------------------

            if (
                type
            ) {

                statusElement.classList.add(
                    type
                );

            }

        }



        // =====================================
        // 現在の経過秒取得
        // =====================================

        function getElapsedSeconds() {


            if (
                processingStartTime ===
                null
            ) {

                return 0;

            }


            return Math.max(

                0,

                Math.floor(

                    (
                        Date.now() -
                        processingStartTime
                    ) / 1000

                )

            );

        }



        // =====================================
        // 現在の経過時間文字列
        // =====================================

        function getElapsedText() {


            const seconds =
                getElapsedSeconds();


            return formatElapsed(
                seconds
            );

        }



        // =====================================
        // タイマー停止
        // =====================================

        function stopTimer() {


            if (
                timerId !== null
            ) {

                clearTimeout(
                    timerId
                );


                timerId =
                    null;

            }

        }



        // =====================================
        // タイマー更新
        // =====================================

        function updateTimer(
            message
        ) {


            // ---------------------------------
            // 処理終了済み
            // ---------------------------------

            if (
                processingStartTime ===
                null
            ) {

                timerId =
                    null;

                return;

            }



            // ---------------------------------
            // ステータス表示
            // ---------------------------------

            setStatus(

                message +
                "\n" +
                "処理時間: " +
                getElapsedText()

            );



            // ---------------------------------
            // 次回更新
            // ---------------------------------

            timerId =
                setTimeout(
                    function () {

                        updateTimer(
                            message
                        );

                    },
                    1000
                );

        }



        // =====================================
        // 処理開始
        // =====================================

        function start(
            message
        ) {


            // ---------------------------------
            // 前回タイマー停止
            // ---------------------------------

            stopTimer();



            // ---------------------------------
            // 開始時刻
            // ---------------------------------

            processingStartTime =
                Date.now();



            // ---------------------------------
            // 初回表示
            // ---------------------------------

            updateTimer(
                message
            );


            console.log(
                "[STATUS] start:",
                message
            );

        }



        // =====================================
        // 処理中メッセージ更新
        // =====================================

        function update(
            message
        ) {


            // ---------------------------------
            // 開始されていない場合
            // ---------------------------------

            if (
                processingStartTime ===
                null
            ) {

                return;

            }



            // ---------------------------------
            // 現在のタイマー停止
            // ---------------------------------

            stopTimer();



            // ---------------------------------
            // 即時表示
            // ---------------------------------

            setStatus(

                message +
                "\n" +
                "処理時間: " +
                getElapsedText()

            );



            // ---------------------------------
            // 次回更新
            // ---------------------------------

            timerId =
                setTimeout(
                    function () {

                        updateTimer(
                            message
                        );

                    },
                    1000
                );


            console.log(
                "[STATUS] update:",
                message
            );

        }



        // =====================================
        // 処理停止
        //
        // タイマーだけ停止
        // 開始時刻は保持
        // =====================================

        function stop() {


            stopTimer();


            console.log(
                "[STATUS] timer stopped"
            );

        }



        // =====================================
        // 完了
        // =====================================

        function success(
            message
        ) {


            // ---------------------------------
            // タイマー停止
            // ---------------------------------

            stopTimer();



            // ---------------------------------
            // 処理時間取得
            // ---------------------------------

            const seconds =
                getElapsedSeconds();


            const elapsedText =
                formatElapsed(
                    seconds
                );



            // ---------------------------------
            // 完了表示
            // ---------------------------------

            setStatus(

                message +
                "\n\n" +
                "処理時間: " +
                elapsedText,

                "success"

            );



            // ---------------------------------
            // 開始時刻リセット
            // ---------------------------------

            processingStartTime =
                null;



            console.log(
                "[STATUS] success:",
                {
                    message:
                        message,

                    seconds:
                        seconds,

                    text:
                        elapsedText
                }
            );



            // ---------------------------------
            // 結果
            // ---------------------------------

            return {

                seconds:
                    seconds,

                text:
                    elapsedText

            };

        }



        // =====================================
        // エラー
        // =====================================

        function error(
            message
        ) {


            // ---------------------------------
            // タイマー停止
            // ---------------------------------

            stopTimer();



            // ---------------------------------
            // 処理時間取得
            // ---------------------------------

            const seconds =
                getElapsedSeconds();


            const elapsedText =
                formatElapsed(
                    seconds
                );



            // ---------------------------------
            // エラー表示
            // ---------------------------------

            setStatus(

                message +
                "\n\n" +
                "エラー発生までの処理時間: " +
                elapsedText,

                "error"

            );



            // ---------------------------------
            // 開始時刻リセット
            // ---------------------------------

            processingStartTime =
                null;



            console.log(
                "[STATUS] error:",
                {
                    message:
                        message,

                    seconds:
                        seconds,

                    text:
                        elapsedText
                }
            );



            // ---------------------------------
            // 結果
            // ---------------------------------

            return {

                seconds:
                    seconds,

                text:
                    elapsedText

            };

        }



        // =====================================
        // クリア
        // =====================================

        function clear() {


            // ---------------------------------
            // タイマー停止
            // ---------------------------------

            stopTimer();



            // ---------------------------------
            // 開始時刻リセット
            // ---------------------------------

            processingStartTime =
                null;



            // ---------------------------------
            // DOMクリア
            // ---------------------------------

            if (
                statusElement
            ) {

                statusElement.textContent =
                    "";


                statusElement.classList.remove(
                    "error",
                    "success"
                );

            }



            console.log(
                "[STATUS] cleared"
            );

        }



        // =====================================
        // 処理中かどうか
        // =====================================

        function isProcessing() {

            return (
                processingStartTime !==
                null
            );

        }



        // =====================================
        // 開始時刻取得
        // =====================================

        function getStartTime() {


            if (
                processingStartTime ===
                null
            ) {

                return null;

            }


            return new Date(
                processingStartTime
            );

        }



        // =====================================
        // 公開オブジェクト
        // =====================================

        const status = {

            // ---------------------------------
            // 初期化済み
            // ---------------------------------

            __initialized:
                true,


            // ---------------------------------
            // 基本表示
            // ---------------------------------

            set:
                setStatus,


            // ---------------------------------
            // 処理開始
            // ---------------------------------

            start:
                start,


            // ---------------------------------
            // 処理中更新
            // ---------------------------------

            update:
                update,


            // ---------------------------------
            // タイマー停止
            // ---------------------------------

            stop:
                stop,


            // ---------------------------------
            // 完了
            // ---------------------------------

            success:
                success,


            // ---------------------------------
            // エラー
            // ---------------------------------

            error:
                error,


            // ---------------------------------
            // クリア
            // ---------------------------------

            clear:
                clear,


            // ---------------------------------
            // 経過時間
            // ---------------------------------

            getElapsedSeconds:
                getElapsedSeconds,


            getElapsedText:
                getElapsedText,


            // ---------------------------------
            // 状態
            // ---------------------------------

            isProcessing:
                isProcessing,


            // ---------------------------------
            // 開始時刻
            // ---------------------------------

            getStartTime:
                getStartTime

        };



        // =====================================
        // グローバル公開
        // =====================================

        window.converterStatus =
            status;


        window.ConverterStatus =
            status;



        // =====================================
        // 読み込み確認
        // =====================================

        console.log(
            "======================================"
        );


        console.log(
            "converter-status.js loaded"
        );


        console.log(
            "[STATUS] converterStatus:",
            window.converterStatus
        );


        console.log(
            "[STATUS] set:",
            typeof
                window.converterStatus.set
        );


        console.log(
            "[STATUS] start:",
            typeof
                window.converterStatus.start
        );


        console.log(
            "[STATUS] update:",
            typeof
                window.converterStatus.update
        );


        console.log(
            "[STATUS] stop:",
            typeof
                window.converterStatus.stop
        );


        console.log(
            "[STATUS] success:",
            typeof
                window.converterStatus.success
        );


        console.log(
            "[STATUS] error:",
            typeof
                window.converterStatus.error
        );


        console.log(
            "[STATUS] clear:",
            typeof
                window.converterStatus.clear
        );


        console.log(
            "[STATUS] getElapsedSeconds:",
            typeof
                window.converterStatus.getElapsedSeconds
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
            initializeConverterStatus,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeConverterStatus();

    }


})();
