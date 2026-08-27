// =====================================
// YouTube Converter - Utils
// converter-utils.js
//
// 共通関数のみを管理
//
// 使用:
// ・converter.js
// ・converter-status.js
// ・converter-gemini.js
// ・sub_embed.js
// =====================================

(function () {

    "use strict";


    // =====================================
    // 初期化
    // =====================================

    function initializeConverterUtils() {

        if (
            window.converterUtils &&
            window.converterUtils.__initialized
        ) {

            console.log(
                "[UTILS] already initialized"
            );

            return;

        }


        // =====================================
        // 数字入力設定
        // =====================================

        function setupNumericInput(element) {

            if (!element) {
                return;
            }


            if (
                element.dataset.converterNumericInitialized ===
                "true"
            ) {

                return;

            }


            element.dataset.converterNumericInitialized =
                "true";


            element.addEventListener(
                "input",
                function () {

                    this.value =
                        this.value.replace(
                            /[^0-9]/g,
                            ""
                        );

                }
            );


            element.addEventListener(
                "keydown",
                function (event) {

                    const allowedKeys = [

                        "Backspace",
                        "Delete",

                        "ArrowLeft",
                        "ArrowRight",

                        "ArrowUp",
                        "ArrowDown",

                        "Tab",

                        "Home",
                        "End"

                    ];


                    if (
                        allowedKeys.includes(
                            event.key
                        )
                    ) {

                        return;

                    }


                    if (
                        event.ctrlKey ||
                        event.metaKey
                    ) {

                        return;

                    }


                    if (
                        !/^[0-9]$/.test(
                            event.key
                        )
                    ) {

                        event.preventDefault();

                    }

                }
            );


            element.setAttribute(
                "inputmode",
                "numeric"
            );


            element.setAttribute(
                "pattern",
                "[0-9]*"
            );

        }


        // =====================================
        // 時間入力設定
        // =====================================

        function setupTimeInputs() {

            const inputIds = [

                "start-hour",
                "start-minute",
                "start-second",

                "end-hour",
                "end-minute",
                "end-second"

            ];


            inputIds.forEach(
                function (id) {

                    setupNumericInput(
                        document.getElementById(
                            id
                        )
                    );

                }
            );

        }


        // =====================================
        // 時間作成
        // =====================================

        function makeTime(
            hour,
            minute,
            second
        ) {

            const h =
                parseInt(
                    hour || "0",
                    10
                ) || 0;


            const m =
                parseInt(
                    minute || "0",
                    10
                ) || 0;


            const s =
                parseInt(
                    second || "0",
                    10
                ) || 0;


            return (

                String(h).padStart(2, "0")
                +
                ":"
                +
                String(m).padStart(2, "0")
                +
                ":"
                +
                String(s).padStart(2, "0")

            );

        }


        // =====================================
        // 時間取得
        // =====================================

        function getTimeValue(prefix) {

            const hour =
                document.getElementById(
                    prefix + "-hour"
                );


            const minute =
                document.getElementById(
                    prefix + "-minute"
                );


            const second =
                document.getElementById(
                    prefix + "-second"
                );


            if (
                hour ||
                minute ||
                second
            ) {

                const h =
                    hour
                        ? hour.value.trim()
                        : "";


                const m =
                    minute
                        ? minute.value.trim()
                        : "";


                const s =
                    second
                        ? second.value.trim()
                        : "";


                if (
                    !h &&
                    !m &&
                    !s
                ) {

                    return "";

                }


                return makeTime(
                    h,
                    m,
                    s
                );

            }


            const element =
                document.getElementById(
                    prefix
                );


            if (!element) {

                return "";

            }


            return element.value.trim();

        }


        // =====================================
        // 時間範囲
        // =====================================

        function getTimeRange() {

            const startTime =
                getTimeValue("start");


            const endTime =
                getTimeValue("end");


            if (
                startTime &&
                !endTime
            ) {

                return {

                    start_time:
                        startTime,

                    end_time:
                        ""

                };

            }


            if (
                !startTime &&
                endTime
            ) {

                return {

                    start_time:
                        "00:00:00",

                    end_time:
                        endTime

                };

            }


            return {

                start_time:
                    startTime,

                end_time:
                    endTime

            };

        }


        // =====================================
        // 時計表示
        // =====================================

        function formatClock(date) {

            if (!date) {

                return "";

            }


            if (
                !(date instanceof Date)
            ) {

                date =
                    new Date(date);

            }


            if (
                isNaN(
                    date.getTime()
                )
            ) {

                return "";

            }


            return date.toLocaleTimeString(
                "ja-JP",
                {

                    hour:
                        "2-digit",

                    minute:
                        "2-digit",

                    second:
                        "2-digit",

                    hour12:
                        false

                }
            );

        }


        // =====================================
        // 経過時間
        // =====================================

        function formatElapsed(seconds) {

            const totalSeconds =
                Math.max(
                    0,
                    Math.floor(
                        Number(seconds) || 0
                    )
                );


            const hours =
                Math.floor(
                    totalSeconds / 3600
                );


            const minutes =
                Math.floor(
                    (totalSeconds % 3600) / 60
                );


            const remainSeconds =
                totalSeconds % 60;


            if (hours > 0) {

                return (

                    hours +
                    "時間 " +
                    minutes +
                    "分 " +
                    remainSeconds +
                    "秒"

                );

            }


            if (minutes > 0) {

                return (

                    minutes +
                    "分" +
                    remainSeconds +
                    "秒"

                );

            }


            return (
                remainSeconds +
                "秒"
            );

        }


        // =====================================
        // 再生時間
        // =====================================

        function formatDuration(duration) {

            if (
                duration === null ||
                duration === undefined ||
                duration === ""
            ) {

                return "不明";

            }


            const value =
                String(duration).trim();


            if (!value) {

                return "不明";

            }


            // ---------------------------------
            // HH:MM:SS
            // ---------------------------------

            if (
                value.includes(":")
            ) {

                const parts =
                    value.split(":");


                if (
                    parts.length === 3
                ) {

                    const hours =
                        parseInt(
                            parts[0],
                            10
                        );


                    const minutes =
                        parseInt(
                            parts[1],
                            10
                        );


                    const seconds =
                        parseInt(
                            parts[2],
                            10
                        );


                    if (
                        Number.isNaN(hours) ||
                        Number.isNaN(minutes) ||
                        Number.isNaN(seconds)
                    ) {

                        return "不明";

                    }


                    return (

                        String(
                            Math.max(
                                0,
                                hours
                            )
                        ).padStart(2, "0")
                        +
                        ":"
                        +
                        String(
                            Math.max(
                                0,
                                minutes
                            )
                        ).padStart(2, "0")
                        +
                        ":"
                        +
                        String(
                            Math.max(
                                0,
                                seconds
                            )
                        ).padStart(2, "0")

                    );

                }

            }


            // ---------------------------------
            // 秒数
            // ---------------------------------

            const totalSeconds =
                parseInt(
                    value,
                    10
                );


            if (
                isNaN(totalSeconds) ||
                totalSeconds < 0
            ) {

                return "不明";

            }


            const hours =
                Math.floor(
                    totalSeconds / 3600
                );


            const minutes =
                Math.floor(
                    (totalSeconds % 3600) / 60
                );


            const seconds =
                totalSeconds % 60;


            return (

                String(hours).padStart(2, "0")
                +
                ":"
                +
                String(minutes).padStart(2, "0")
                +
                ":"
                +
                String(seconds).padStart(2, "0")

            );

        }


        // =====================================
        // HTMLエスケープ
        // =====================================

        function escapeHtml(value) {

            return String(

                value === null ||
                value === undefined
                    ? ""
                    : value

            )

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
        // ダウンロードURL
        // =====================================

        function makeDownloadUrl(filename) {

            if (
                filename === null ||
                filename === undefined ||
                filename === ""
            ) {

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
        // 出力形式
        // =====================================

        function getSelectedOutputs() {

            const selectedFormat =
                document.querySelector(
                    'input[name="output-format"]:checked'
                );


            const outputFormat =
                selectedFormat
                    ? selectedFormat.value
                    : "mp3";


            switch (
                outputFormat
            ) {

                case "mp4":

                    return ["mp4"];


                case "mp3mp4":

                    return [
                        "mp3",
                        "mp4"
                    ];


                case "mp3":

                default:

                    return ["mp3"];

            }

        }


        // =====================================
        // 公開
        // =====================================

        const utils = {

            __initialized:
                true,

            setupNumericInput:
                setupNumericInput,

            setupTimeInputs:
                setupTimeInputs,

            makeTime:
                makeTime,

            getTimeValue:
                getTimeValue,

            getTimeRange:
                getTimeRange,

            formatClock:
                formatClock,

            formatElapsed:
                formatElapsed,

            formatDuration:
                formatDuration,

            escapeHtml:
                escapeHtml,

            makeDownloadUrl:
                makeDownloadUrl,

            getSelectedOutputs:
                getSelectedOutputs

        };


        window.converterUtils =
            utils;


        window.ConverterUtils =
            utils;


        // =====================================
        // 時間入力初期化
        // =====================================

        setupTimeInputs();


        console.log(
            "[UTILS] converter-utils.js loaded"
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
            initializeConverterUtils,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeConverterUtils();

    }

})();
