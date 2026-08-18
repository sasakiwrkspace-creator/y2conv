// =====================================
// YouTube Converter - Utils
// converter-utils.js
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================
        // 数字入力
        // =====================================

        function setupNumericInput(element) {

            if (!element) {
                return;
            }


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

        setupNumericInput(
            document.getElementById(
                "start-hour"
            )
        );

        setupNumericInput(
            document.getElementById(
                "start-minute"
            )
        );

        setupNumericInput(
            document.getElementById(
                "start-second"
            )
        );

        setupNumericInput(
            document.getElementById(
                "end-hour"
            )
        );

        setupNumericInput(
            document.getElementById(
                "end-minute"
            )
        );

        setupNumericInput(
            document.getElementById(
                "end-second"
            )
        );



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


            // ---------------------------------
            // 旧UIにも対応
            // ---------------------------------

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

            let startTime =
                getTimeValue(
                    "start-time"
                );


            let endTime =
                getTimeValue(
                    "end-time"
                );


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
        // 時刻表示
        // =====================================

        function formatClock(date) {

            if (!date) {
                return "";
            }


            return date.toLocaleTimeString(
                "ja-JP",
                {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: false
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


            const minutes =
                Math.floor(
                    totalSeconds / 60
                );


            const remainSeconds =
                totalSeconds % 60;


            if (minutes === 0) {

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


            // ---------------------------------
            // すでに HH:MM:SS 形式ならそのまま
            // ---------------------------------

            if (
                typeof duration === "string" &&
                duration.includes(":")
            ) {

                const parts =
                    duration.split(":");


                if (parts.length === 3) {

                    const hours =
                        parseInt(
                            parts[0],
                            10
                        ) || 0;


                    const minutes =
                        parseInt(
                            parts[1],
                            10
                        ) || 0;


                    const seconds =
                        parseInt(
                            parts[2],
                            10
                        ) || 0;


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

            }


            // ---------------------------------
            // 秒数の場合
            // ---------------------------------

            const totalSeconds =
                parseInt(
                    duration,
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

            return String(value)
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

            return (
                "/download/"
                +
                encodeURIComponent(
                    filename
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


            // ---------------------------------
            // MP3
            // ---------------------------------

            if (
                outputFormat === "mp3"
            ) {

                return [
                    "mp3"
                ];

            }


            // ---------------------------------
            // MP4
            // ---------------------------------

            if (
                outputFormat === "mp4"
            ) {

                return [
                    "mp4"
                ];

            }


            // ---------------------------------
            // MP3 + MP4
            // ---------------------------------

            if (
                outputFormat === "mp3mp4"
            ) {

                return [
                    "mp3",
                    "mp4"
                ];

            }


            return [
                "mp3"
            ];

        }



        // =====================================
        // グローバル公開
        //
        // converter.js
        // converter-status.js
        // converter-gemini.js
        // から使用する
        // =====================================

        window.ConverterUtils = {

            setupNumericInput:
                setupNumericInput,

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

    }
);
