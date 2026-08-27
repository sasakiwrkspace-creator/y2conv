// =====================================
// YouTube Converter - Status
// converter-status.js
//
// ステータス表示と処理時間管理を担当
// =====================================

(function () {

    "use strict";


    function initializeConverterStatus() {

        if (
            window.converterStatus &&
            window.converterStatus.__initialized
        ) {

            console.log(
                "[STATUS] already initialized"
            );

            return;

        }


        const statusElement =
            document.getElementById(
                "converter-status"
            );


        let processingStartTime =
            null;


        let timerId =
            null;


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


            statusElement.classList.remove(
                "error",
                "success"
            );


            if (type) {

                statusElement.classList.add(
                    type
                );

            }

        }


        // =====================================
        // 開始
        // =====================================

        function start(message) {

            stop();


            processingStartTime =
                Date.now();


            update(message);

        }


        // =====================================
        // 更新
        // =====================================

        function update(message) {

            if (
                processingStartTime === null
            ) {

                return;

            }


            const elapsed =
                Math.floor(
                    (
                        Date.now() -
                        processingStartTime
                    ) / 1000
                );


            const utils =
                window.converterUtils;


            const elapsedText =
                utils &&
                typeof utils.formatElapsed ===
                    "function"

                    ? utils.formatElapsed(
                        elapsed
                    )

                    : elapsed + "秒";


            setStatus(

                message +
                "\n" +
                "処理時間: " +
                elapsedText

            );


            timerId =
                setTimeout(
                    function () {

                        update(message);

                    },
                    1000
                );

        }


        // =====================================
        // 停止
        // =====================================

        function stop() {

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
        // 経過秒
        // =====================================

        function getElapsedSeconds() {

            if (
                processingStartTime === null
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
        // 完了
        // =====================================

        function success(message) {

            stop();


            const elapsed =
                getElapsedSeconds();


            const utils =
                window.converterUtils;


            const elapsedText =
                utils &&
                typeof utils.formatElapsed ===
                    "function"

                    ? utils.formatElapsed(
                        elapsed
                    )

                    : elapsed + "秒";


            setStatus(

                message +
                "\n\n" +
                "処理時間: " +
                elapsedText,

                "success"

            );


            processingStartTime =
                null;


            return {

                seconds:
                    elapsed,

                text:
                    elapsedText

            };

        }


        // =====================================
        // エラー
        // =====================================

        function error(message) {

            stop();


            const elapsed =
                getElapsedSeconds();


            const utils =
                window.converterUtils;


            const elapsedText =
                utils &&
                typeof utils.formatElapsed ===
                    "function"

                    ? utils.formatElapsed(
                        elapsed
                    )

                    : elapsed + "秒";


            setStatus(

                message +
                "\n\n" +
                "エラー発生までの処理時間: " +
                elapsedText,

                "error"

            );


            processingStartTime =
                null;


            return {

                seconds:
                    elapsed,

                text:
                    elapsedText

            };

        }


        // =====================================
        // クリア
        // =====================================

        function clear() {

            stop();


            processingStartTime =
                null;


            if (statusElement) {

                statusElement.textContent =
                    "";

                statusElement.classList.remove(
                    "error",
                    "success"
                );

            }

        }


        // =====================================
        // 公開
        // =====================================

        const status = {

            __initialized:
                true,

            set:
                setStatus,

            start:
                start,

            update:
                update,

            stop:
                stop,

            success:
                success,

            error:
                error,

            clear:
                clear,

            getElapsedSeconds:
                getElapsedSeconds

        };


        window.converterStatus =
            status;


        window.ConverterStatus =
            status;


        console.log(
            "[STATUS] converter-status.js loaded"
        );

    }


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
