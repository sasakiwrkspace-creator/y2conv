// =====================================
// YouTube Converter - Utils
// converter-utils.js
//
// 共通関数を一元管理するファイル
//
// 使用するファイル
// ・converter.js
// ・converter-status.js
// ・converter-gemini.js
// ・sub_embed.js
//
// 注意
// ・setupNumericInput()
// ・getTimeValue()
// ・getTimeRange()
// ・getSelectedOutputs()
// などの共通関数は、このファイルだけで管理する。
// =====================================


(function () {

    "use strict";


    // =====================================
    // Utils初期化
    // =====================================

    function initializeConverterUtils() {


        // =====================================
        // 二重初期化防止
        // =====================================

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
        // 数字入力
        // =====================================

        function setupNumericInput(element) {

            if (!element) {

                return;

            }


            // ---------------------------------
            // 二重イベント登録防止
            // ---------------------------------

            if (
                element.dataset.converterNumericInitialized ===
                "true"
            ) {

                return;

            }


            element.dataset.converterNumericInitialized =
                "true";


            // ---------------------------------
            // input
            // ---------------------------------

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


            // ---------------------------------
            // keydown
            // ---------------------------------

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


                    // ---------------------------------
                    // 編集・移動キー
                    // ---------------------------------

                    if (
                        allowedKeys.includes(
                            event.key
                        )
                    ) {

                        return;

                    }


                    // ---------------------------------
                    // Ctrl / Command
                    // ---------------------------------

                    if (
                        event.ctrlKey ||
                        event.metaKey
                    ) {

                        return;

                    }


                    // ---------------------------------
                    // 数字以外は禁止
                    // ---------------------------------

                    if (
                        !/^[0-9]$/.test(
                            event.key
                        )
                    ) {

                        event.preventDefault();

                    }

                }
            );


            // ---------------------------------
            // モバイル入力
            // ---------------------------------

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
        // 時間を HH:MM:SS にする
        // =====================================

        function makeTime(
            hour,
            minute,
            second
        ) {

            hour =
                parseInt(
                    hour || "0",
                    10
                ) || 0;


            minute =
                parseInt(
                    minute || "0",
                    10
                ) || 0;


            second =
                parseInt(
                    second || "0",
                    10
                ) || 0;


            return (

                String(hour).padStart(
                    2,
                    "0"
                )

                +

                ":"

                +

                String(minute).padStart(
                    2,
                    "0"
                )

                +

                ":"

                +

                String(second).padStart(
                    2,
                    "0"
                )

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


            // =================================
            // 新UI
            // =================================

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


                console.log(
                    "[UTILS] TIME INPUT:",
                    prefix,
                    {
                        hour: h,
                        minute: m,
                        second: s
                    }
                );


                // ---------------------------------
                // 全部空欄
                // ---------------------------------

                if (
                    !h &&
                    !m &&
                    !s
                ) {

                    return "";

                }


                const result =
                    makeTime(
                        h,
                        m,
                        s
                    );


                console.log(
                    "[UTILS] TIME RESULT:",
                    prefix,
                    result
                );


                return result;

            }


            // =================================
            // 旧UI
            // =================================

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
                getTimeValue(
                    "start"
                );


            const endTime =
                getTimeValue(
                    "end"
                );


            console.log(
                "[UTILS] TIME RANGE INPUT:",
                {
                    startTime:
                        startTime,

                    endTime:
                        endTime
                }
            );


            // =================================
            // 開始だけ指定
            // =================================

            if (
                startTime &&
                !endTime
            ) {

                const result = {

                    start_time:
                        startTime,

                    end_time:
                        ""

                };


                console.log(
                    "[UTILS] TIME RANGE:",
                    result
                );


                return result;

            }


            // =================================
            // 終了だけ指定
            // =================================

            if (
                !startTime &&
                endTime
            ) {

                const result = {

                    start_time:
                        "00:00:00",

                    end_time:
                        endTime

                };


                console.log(
                    "[UTILS] TIME RANGE:",
                    result
                );


                return result;

            }


            // =================================
            // 開始・終了とも指定
            // =================================

            const result = {

                start_time:
                    startTime,

                end_time:
                    endTime

            };


            console.log(
                "[UTILS] TIME RANGE:",
                result
            );


            return result;

        }


        // =====================================
        // 時刻表示
        // =====================================

        function formatClock(date) {

            if (!date) {

                return "";

            }


            if (
                !(date instanceof Date)
            ) {

                date =
                    new Date(
                        date
                    );

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
        // 経過時間表示
        // =====================================

        function formatElapsed(seconds) {

            const totalSeconds =
                Math.floor(
                    Number(seconds) || 0
                );


            const safeSeconds =
                Math.max(
                    0,
                    totalSeconds
                );


            const minutes =
                Math.floor(
                    safeSeconds / 60
                );


            const remainSeconds =
                safeSeconds % 60;


            if (
                minutes === 0
            ) {

                return (
                    remainSeconds +
                    "秒"
                );

            }


            return (

                minutes +
                "分" +

                remainSeconds +
                "秒"

            );

        }


        // =====================================
        // 再生時間を HH:MM:SS にする
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
                String(
                    duration
                ).trim();


            if (!value) {

                return "不明";

            }


            // =================================
            // HH:MM:SS
            // =================================

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
                        ).padStart(
                            2,
                            "0"
                        )

                        +

                        ":"

                        +

                        String(
                            Math.max(
                                0,
                                minutes
                            )
                        ).padStart(
                            2,
                            "0"
                        )

                        +

                        ":"

                        +

                        String(
                            Math.max(
                                0,
                                seconds
                            )
                        ).padStart(
                            2,
                            "0"
                        )

                    );

                }

            }


            // =================================
            // 秒数
            // =================================

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

                String(hours).padStart(
                    2,
                    "0"
                )

                +

                ":"

                +

                String(minutes).padStart(
                    2,
                    "0"
                )

                +

                ":"

                +

                String(seconds).padStart(
                    2,
                    "0"
                )

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
        // ダウンロードURL作成
        // =====================================

        function makeDownloadUrl(
            filename
        ) {

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
                    String(
                        filename
                    )
                )

            );

        }


        // =====================================
        // 選択されている出力形式
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


            console.log(
                "[UTILS] OUTPUT FORMAT:",
                outputFormat
            );


            if (
                outputFormat === "mp3"
            ) {

                return [
                    "mp3"
                ];

            }


            if (
                outputFormat === "mp4"
            ) {

                return [
                    "mp4"
                ];

            }


            if (
                outputFormat === "mp3mp4"
            ) {

                return [
                    "mp3",
                    "mp4"
                ];

            }


            console.warn(
                "[UTILS] Unknown output format:",
                outputFormat
            );


            return [
                "mp3"
            ];

        }


        // =====================================
        // 共通オブジェクト
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


        // =====================================
        // グローバル公開
        // =====================================

        window.ConverterUtils =
            utils;


        window.converterUtils =
            utils;


        // =====================================
        // DOM上の時間入力を初期化
        // =====================================

        setupTimeInputs();


        // =====================================
        // 確認ログ
        // =====================================

        console.log(
            "======================================"
        );

        console.log(
            "converter-utils.js loaded"
        );

        console.log(
            "[UTILS] ConverterUtils:",
            window.ConverterUtils
        );

        console.log(
            "[UTILS] converterUtils:",
            window.converterUtils
        );

        console.log(
            "[UTILS] setupNumericInput:",
            typeof window.converterUtils.setupNumericInput
        );

        console.log(
            "[UTILS] makeTime:",
            typeof window.converterUtils.makeTime
        );

        console.log(
            "[UTILS] getTimeValue:",
            typeof window.converterUtils.getTimeValue
        );

        console.log(
            "[UTILS] getTimeRange:",
            typeof window.converterUtils.getTimeRange
        );

        console.log(
            "[UTILS] getSelectedOutputs:",
            typeof window.converterUtils.getSelectedOutputs
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
