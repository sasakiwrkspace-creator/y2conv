// =====================================
// YouTube Converter - Utilities
// =====================================

(function () {

    "use strict";


    // =====================================
    // グローバル名前空間
    // =====================================

    window.ConverterUtils = window.ConverterUtils || {};



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



        // =================================
        // 旧UIにも対応
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
                "start-time"
            );


        const endTime =
            getTimeValue(
                "end-time"
            );


        // =================================
        // 開始だけ指定
        // =================================

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



        // =================================
        // 終了だけ指定
        // =================================

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



        // =================================
        // 両方指定 / 両方空
        // =================================

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



        // =================================
        // すでに HH:MM:SS 形式
        // =================================

        if (
            typeof duration === "string" &&
            duration.includes(":")
        ) {

            const parts =
                duration.split(":");


            if (
                parts.length === 3
            ) {

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



        // =================================
        // 秒数の場合
        // =================================

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
    // 変換情報HTML
    // =====================================

    function createConversionInfo(
        type,
        data,
        currentVideoTitle,
        currentVideoDuration,
        convertStartTime,
        convertEndTime,
        convertSeconds,
        durationOverride
    ) {

        data =
            data || {};


        const title =
            data.title ||
            data.video_title ||
            currentVideoTitle ||
            "不明";


        const duration =
            durationOverride !== undefined &&
            durationOverride !== null &&
            durationOverride !== ""
                ? durationOverride
                : (
                    data.duration ||
                    data.video_duration ||
                    currentVideoDuration ||
                    "不明"
                );


        const start =
            convertStartTime
                ? formatClock(
                    convertStartTime
                )
                : "";


        const end =
            convertEndTime
                ? formatClock(
                    convertEndTime
                )
                : "";


        return `
            <div class="conversion-info">

                <div class="conversion-info-title">
                    【${escapeHtml(type)}変換】
                </div>

                <div>
                    タイトル：${escapeHtml(title)}
                </div>

                <div>
                    再生時間：${escapeHtml(
                        formatDuration(duration)
                    )}
                </div>

                <div>
                    実行開始：${escapeHtml(start)}
                </div>

                <div>
                    実行終了：${escapeHtml(end)}
                    （${escapeHtml(
                        formatElapsed(
                            convertSeconds
                        )
                    )}）
                </div>

            </div>
        `;

    }



    // =====================================
    // 外部公開
    // =====================================

    ConverterUtils.setupNumericInput =
        setupNumericInput;


    ConverterUtils.makeTime =
        makeTime;


    ConverterUtils.getTimeValue =
        getTimeValue;


    ConverterUtils.getTimeRange =
        getTimeRange;


    ConverterUtils.formatClock =
        formatClock;


    ConverterUtils.formatElapsed =
        formatElapsed;


    ConverterUtils.formatDuration =
        formatDuration;


    ConverterUtils.escapeHtml =
        escapeHtml;


    ConverterUtils.makeDownloadUrl =
        makeDownloadUrl;


    ConverterUtils.createConversionInfo =
        createConversionInfo;



    // =====================================
    // 読み込み確認
    // =====================================

    console.log(
        "converter-utils.js loaded"
    );

})();
