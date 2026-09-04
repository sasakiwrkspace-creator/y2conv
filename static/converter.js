// =====================================
// YouTube Converter
// converter.js
//
// 履歴保持版
//
// 役割:
// ・YouTube URL受付
// ・MP3 / MP4変換API実行
// ・job_idによる処理状況監視
// ・MP3 / MP4ダウンロード表示
// ・MP3完成後のSRT/Gemini処理表示
// ・処理詳細表示
// ・過去のステータスを消さずに下へ追加
//
// 注意:
// ・converterUtils.js は使用しない
// ・converterStatus.js は使用しない
// ・タブ2の処理には触れない
// ・タブ1の実行ボタンは #convertBtn
// ・上側ステータスはタイトル表示
// ・処理詳細は折り畳み表示
// ・Part 1/3 + Part 2/3 + Part 3/3で完成
// =====================================


(function () {

    "use strict";


    // =====================================
    // 初期化
    // =====================================

    function initializeConverter() {

        console.log(
            "[CONVERTER] 初期化開始"
        );


        // =====================================
        // DOM
        // =====================================

        const urlInput =
            document.getElementById(
                "youtube-url"
            );


        const convertButton =
            document.getElementById(
                "convertBtn"
            );


        const conversionStatusArea =
            document.getElementById(
                "conversion-status-area"
            );


        const downloadArea =
            document.getElementById(
                "downloadArea"
            );


        // =====================================
        // 必須DOM確認
        // =====================================

        if (!urlInput) {

            console.error(
                "[CONVERTER] #youtube-url が見つかりません"
            );

            return;

        }


        if (!convertButton) {

            console.error(
                "[CONVERTER] #convertBtn が見つかりません"
            );

            return;

        }


        if (!conversionStatusArea) {

            console.warn(
                "[CONVERTER] #conversion-status-area が見つかりません"
            );

        }


        if (!downloadArea) {

            console.warn(
                "[CONVERTER] #downloadArea が見つかりません"
            );

        }


        // =====================================
        // State
        // =====================================

        const converterState = {

            currentVideoTitle:
                "",

            currentVideoDuration:
                "",

            currentVideoUrl:
                "",

            currentMp3File:
                "",

            currentMp4File:
                "",

            currentSrtFile:
                "",

            currentJobId:
                "",

            currentJobStatus:
                "",

            currentJob:
                null,

            isProcessing:
                false,


            // ---------------------------------
            // 現在のMP3/MP4処理
            // ---------------------------------

            mp3Process:
                {

                    startTime:
                        null,

                    endTime:
                        null

                },


            // ---------------------------------
            // SRT処理
            // ---------------------------------

            srtProcess:
                {

                    startTime:
                        null,

                    endTime:
                        null

                },


            // ---------------------------------
            // ステータス履歴
            // ---------------------------------

            statusHistory:
                []

        };


        window.converterState =
            converterState;


        // =====================================
        // 現在の履歴ブロック
        // =====================================

        let currentHistoryBlock =
            null;


        let currentHistoryStatusArea =
            null;


        let currentHistoryDetails =
            null;


        let currentHistoryDetailsBody =
            null;


        let currentHistoryMp3Details =
            null;


        let currentHistorySrtDetails =
            null;


        // =====================================
        // HTMLエスケープ
        // =====================================

        function escapeHtml(
            value
        ) {

            const div =
                document.createElement(
                    "div"
                );


            div.textContent =
                String(
                    value ?? ""
                );


            return div.innerHTML;

        }


        // =====================================
        // 時計
        // =====================================

        function formatClock(
            date
        ) {

            if (!date) {

                return "不明";

            }


            const hours =
                String(
                    date.getHours()
                ).padStart(
                    2,
                    "0"
                );


            const minutes =
                String(
                    date.getMinutes()
                ).padStart(
                    2,
                    "0"
                );


            const seconds =
                String(
                    date.getSeconds()
                ).padStart(
                    2,
                    "0"
                );


            return (
                hours +
                ":" +
                minutes +
                ":" +
                seconds
            );

        }


        // =====================================
        // 経過時間
        // =====================================

        function formatElapsed(
            seconds
        ) {

            const total =
                Math.max(
                    0,
                    Math.floor(
                        Number(seconds) || 0
                    )
                );


            const hours =
                Math.floor(
                    total / 3600
                );


            const minutes =
                Math.floor(
                    (total % 3600) / 60
                );


            const secs =
                total % 60;


            if (hours > 0) {

                return (
                    hours +
                    "時間 " +
                    minutes +
                    "分 " +
                    secs +
                    "秒"
                );

            }


            if (minutes > 0) {

                return (
                    minutes +
                    "分 " +
                    secs +
                    "秒"
                );

            }


            return (
                secs +
                "秒"
            );

        }


        // =====================================
        // 再生時間
        // =====================================

        function formatDuration(
            duration
        ) {

            if (
                duration === null ||
                duration === undefined ||
                duration === ""
            ) {

                return "不明";

            }


            const total =
                Math.max(
                    0,
                    Math.floor(
                        Number(duration) || 0
                    )
                );


            const hours =
                Math.floor(
                    total / 3600
                );


            const minutes =
                Math.floor(
                    (total % 3600) / 60
                );


            const seconds =
                total % 60;


            if (hours > 0) {

                return (
                    String(hours).padStart(
                        2,
                        "0"
                    ) +
                    ":" +
                    String(minutes).padStart(
                        2,
                        "0"
                    ) +
                    ":" +
                    String(seconds).padStart(
                        2,
                        "0"
                    )
                );

            }


            return (
                String(minutes).padStart(
                    2,
                    "0"
                ) +
                ":" +
                String(seconds).padStart(
                    2,
                    "0"
                )
            );

        }


        // =====================================
        // 時間入力取得
        // =====================================

        function getTimeValue(
            hourId,
            minuteId,
            secondId
        ) {

            const hourInput =
                document.getElementById(
                    hourId
                );


            const minuteInput =
                document.getElementById(
                    minuteId
                );


            const secondInput =
                document.getElementById(
                    secondId
                );


            const hour =
                hourInput
                    ? hourInput.value.trim()
                    : "";


            const minute =
                minuteInput
                    ? minuteInput.value.trim()
                    : "";


            const second =
                secondInput
                    ? secondInput.value.trim()
                    : "";


            if (
                !hour &&
                !minute &&
                !second
            ) {

                return null;

            }


            const h =
                Number(
                    hour || 0
                );


            const m =
                Number(
                    minute || 0
                );


            const s =
                Number(
                    second || 0
                );


            if (
                !Number.isFinite(h) ||
                !Number.isFinite(m) ||
                !Number.isFinite(s)
            ) {

                return null;

            }


            return (
                h * 3600 +
                m * 60 +
                s
            );

        }


        // =====================================
        // 時間範囲
        // =====================================

        function getTimeRange() {

            const start =
                getTimeValue(
                    "start-hour",
                    "start-minute",
                    "start-second"
                );


            const end =
                getTimeValue(
                    "end-hour",
                    "end-minute",
                    "end-second"
                );


            return {

                start_time:
                    start,

                end_time:
                    end

            };

        }


        // =====================================
        // 出力形式
        // =====================================

        function getSelectedOutputs() {

            const checked =
                document.querySelectorAll(
                    'input[name="output-format"]:checked'
                );


            const outputs =
                [];


            checked.forEach(
                function (input) {

                    const value =
                        String(
                            input.value || ""
                        ).toLowerCase();


                    if (
                        value === "mp3"
                    ) {

                        outputs.push(
                            "mp3"
                        );

                    }
                    else if (
                        value === "mp4"
                    ) {

                        outputs.push(
                            "mp4"
                        );

                    }
                    else if (
                        value === "subtitle_mp4"
                    ) {

                        outputs.push(
                            "mp4"
                        );

                    }

                }
            );


            return [
                ...new Set(
                    outputs
                )
            ];

        }


        // =====================================
        // ダウンロードURL
        // =====================================

        function makeDownloadUrl(
            filename
        ) {

            if (!filename) {

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
        // 上側ステータス
        //
        // タイトルだけを表示
        // =====================================

        function setStatus(
            message,
            type
        ) {

            const text =
                String(
                    message || ""
                );


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    text;


                conversionStatusArea.style.whiteSpace =
                    "pre-line";


                conversionStatusArea.style.display =
                    text
                        ? "block"
                        : "none";


                if (type === "error") {

                    conversionStatusArea.style.color =
                        "#b00020";

                }
                else if (
                    type === "success"
                ) {

                    conversionStatusArea.style.color =
                        "#176b2c";

                }
                else {

                    conversionStatusArea.style.color =
                        "#222";

                }

            }


            console.log(
                "[CONVERTER] STATUS:",
                text
            );

        }


        // =====================================
        // 処理進捗
        //
        // 上側ステータスは上書きしない。
        // 履歴側へ追加する。
        // =====================================

        function setProgress(
            message,
            type
        ) {

            const text =
                String(
                    message || ""
                );


            console.log(
                "[CONVERTER] PROGRESS:",
                text
            );


            if (
                !text
            ) {

                return;

            }


            appendHistoryStatus(
                text,
                type || "processing"
            );

        }


        // =====================================
        // 履歴へステータス追加
        //
        // 同じメッセージの連続追加を防止
        // =====================================

        function appendHistoryStatus(
            message,
            type
        ) {

            const text =
                String(
                    message || ""
                );


            if (!text) {

                return;

            }


            if (
                !currentHistoryStatusArea
            ) {

                console.warn(
                    "[CONVERTER] 履歴ステータス領域がありません:",
                    text
                );

                return;

            }


            const lastMessage =
                currentHistoryStatusArea.dataset.lastMessage ||
                "";


            if (
                lastMessage === text
            ) {

                return;

            }


            const statusElement =
                document.createElement(
                    "div"
                );


            statusElement.className =
                "converter-status-history-item";


            if (type) {

                statusElement.dataset.type =
                    type;

            }


            statusElement.textContent =
                text;


            currentHistoryStatusArea.appendChild(
                statusElement
            );


            currentHistoryStatusArea.dataset.lastMessage =
                text;


            converterState.statusHistory.push({

                time:
                    new Date(),

                message:
                    text,

                type:
                    type || "processing"

            });


            console.log(
                "[CONVERTER] 履歴追加:",
                text
            );

        }


        // =====================================
        // 履歴ブロック作成
        // =====================================

        function createHistoryBlock() {

            if (!downloadArea) {

                return null;

            }


            const block =
                document.createElement(
                    "div"
                );


            block.className =
                "converter-history-block";


            // ---------------------------------
            // ステータス
            // ---------------------------------

            const statusArea =
                document.createElement(
                    "div"
                );


            statusArea.className =
                "converter-status-history"
                ;


            // ---------------------------------
            // 処理詳細
            // ---------------------------------

            const details =
                document.createElement(
                    "details"
                );


            details.className =
                "conversion-details";


            details.open =
                false;


            const summary =
                document.createElement(
                    "summary"
                );


            summary.textContent =
                "処理詳細";


            details.appendChild(
                summary
            );


            const detailsBody =
                document.createElement(
                    "div"
                );


            detailsBody.className =
                "conversion-details-body";


            // ---------------------------------
            // MP3詳細
            // ---------------------------------

            const mp3Details =
                document.createElement(
                    "div"
                );


            mp3Details.className =
                "conversion-detail-section";


            // ---------------------------------
            // SRT詳細
            // ---------------------------------

            const srtDetails =
                document.createElement(
                    "div"
                );


            srtDetails.className =
                "conversion-detail-section";


            detailsBody.appendChild(
                mp3Details
            );


            detailsBody.appendChild(
                srtDetails
            );


            details.appendChild(
                detailsBody
            );


            block.appendChild(
                statusArea
            );


            block.appendChild(
                details
            );


            downloadArea.appendChild(
                block
            );


            currentHistoryBlock =
                block;


            currentHistoryStatusArea =
                statusArea;


            currentHistoryDetails =
                details;


            currentHistoryDetailsBody =
                detailsBody;


            currentHistoryMp3Details =
                mp3Details;


            currentHistorySrtDetails =
                srtDetails;


            return block;

        }


        // =====================================
        // 新しい実行履歴開始
        // =====================================

        function startNewHistory() {

            currentHistoryBlock =
                null;


            currentHistoryStatusArea =
                null;


            currentHistoryDetails =
                null;


            currentHistoryDetailsBody =
                null;


            currentHistoryMp3Details =
                null;


            currentHistorySrtDetails =
                null;


            const block =
                createHistoryBlock();


            if (!block) {

                return;

            }


            appendHistoryStatus(
                "新しい変換を開始します。",
                "start"
            );

        }


        // =====================================
        // 処理詳細表示
        // =====================================

        function renderConversionDetails() {

            if (
                !currentHistoryMp3Details
            ) {

                return;

            }


            const startTime =
                converterState.mp3Process.startTime;


            const endTime =
                converterState.mp3Process.endTime;


            let elapsedText =
                "処理中...";


            if (
                startTime &&
                endTime
            ) {

                const elapsed =
                    Math.max(

                        0,

                        Math.floor(

                            (
                                endTime.getTime() -
                                startTime.getTime()
                            ) / 1000

                        )

                    );


                elapsedText =
                    formatElapsed(
                        elapsed
                    );

            }


            const statusText =
                converterState.currentJobStatus
                    ? converterState.currentJobStatus
                    : "";


            currentHistoryMp3Details.innerHTML = `

                <div class="conversion-detail-title">
                    【mp4作成 / mp3作成】
                </div>

                <div>
                    再生時間：
                    ${escapeHtml(
                        formatDuration(
                            converterState.currentVideoDuration
                        )
                    )}
                </div>

                <div>
                    実行開始：
                    ${escapeHtml(
                        formatClock(
                            startTime
                        )
                    )}
                </div>

                <div>
                    実行終了：
                    ${escapeHtml(
                        formatClock(
                            endTime
                        )
                    )}
                </div>

                <div>
                    処理時間：
                    ${escapeHtml(
                        elapsedText
                    )}
                </div>

                ${
                    statusText
                        ? `
                            <div>
                                処理状態：
                                ${escapeHtml(
                                    statusText
                                )}
                            </div>
                          `
                        : ""
                }

            `;


            // =================================
            // SRT詳細
            // =================================

            if (
                !currentHistorySrtDetails
            ) {

                return;

            }


            const hasSrtProcess =
                converterState.srtProcess.startTime !== null;


            if (!hasSrtProcess) {

                currentHistorySrtDetails.style.display =
                    "none";

                return;

            }


            currentHistorySrtDetails.style.display =
                "block";


            const srtStartTime =
                converterState.srtProcess.startTime;


            const srtEndTime =
                converterState.srtProcess.endTime;


            let srtElapsedText =
                "処理中...";


            if (
                srtStartTime &&
                srtEndTime
            ) {

                const srtElapsed =
                    Math.max(

                        0,

                        Math.floor(

                            (
                                srtEndTime.getTime() -
                                srtStartTime.getTime()
                            ) / 1000

                        )

                    );


                srtElapsedText =
                    formatElapsed(
                        srtElapsed
                    );

            }


            currentHistorySrtDetails.innerHTML = `

                <div class="conversion-detail-title">
                    【srt作成】
                </div>

                <div>
                    再生時間：
                    ${escapeHtml(
                        formatDuration(
                            converterState.currentVideoDuration
                        )
                    )}
                </div>

                <div>
                    実行開始：
                    ${escapeHtml(
                        formatClock(
                            srtStartTime
                        )
                    )}
                </div>

                <div>
                    実行終了：
                    ${escapeHtml(
                        formatClock(
                            srtEndTime
                        )
                    )}
                </div>

                <div>
                    処理時間：
                    ${escapeHtml(
                        srtElapsedText
                    )}
                </div>

            `;

        }


        // =====================================
        // 処理詳細へ進捗追加
        // =====================================

        function updateConversionProgress(
            message
        ) {

            if (
                !currentHistoryMp3Details
            ) {

                return;

            }


            const text =
                String(
                    message || ""
                );


            if (!text) {

                return;

            }


            const progress =
                document.createElement(
                    "div"
                );


            progress.className =
                "conversion-progress";


            progress.textContent =
                text;


            currentHistoryMp3Details.appendChild(
                progress
            );

        }


        // =====================================
        // Part 2/3へ続く
        // =====================================
// =====================================
// Part 2 / 3
// YouTube Converter
// =====================================


// =====================================
// ダウンロードURL
// =====================================

function makeDownloadUrl(filename) {

    if (!filename) {
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
// 処理詳細DOM
// =====================================

let conversionDetails = null;

let conversionDetailsBody = null;

let mp3DetailsArea = null;

let mp4DetailsArea = null;

let srtDetailsArea = null;


// =====================================
// 処理詳細作成
//
// ★重要
// 過去の処理詳細を削除しない。
// 新しい処理を下へ追加する。
// =====================================

function createConversionDetails() {

    if (!downloadArea) {
        return;
    }

    // ---------------------------------
    // 今回の処理用コンテナ
    // ---------------------------------

    conversionDetails =
        document.createElement(
            "details"
        );

    conversionDetails.className =
        "conversion-details";

    conversionDetails.open =
        false;


    // ---------------------------------
    // summary
    // ---------------------------------

    const summary =
        document.createElement(
            "summary"
        );

    summary.textContent =
        "処理詳細";


    conversionDetails.appendChild(
        summary
    );


    // ---------------------------------
    // body
    // ---------------------------------

    conversionDetailsBody =
        document.createElement(
            "div"
        );

    conversionDetailsBody.className =
        "conversion-details-body";


    // ---------------------------------
    // MP3
    // ---------------------------------

    mp3DetailsArea =
        document.createElement(
            "div"
        );

    mp3DetailsArea.className =
        "conversion-detail-section";


    // ---------------------------------
    // MP4
    // ---------------------------------

    mp4DetailsArea =
        document.createElement(
            "div"
        );

    mp4DetailsArea.className =
        "conversion-detail-section";


    // ---------------------------------
    // SRT
    // ---------------------------------

    srtDetailsArea =
        document.createElement(
            "div"
        );

    srtDetailsArea.className =
        "conversion-detail-section";


    // ---------------------------------
    // 追加
    // ---------------------------------

    conversionDetailsBody.appendChild(
        mp3DetailsArea
    );

    conversionDetailsBody.appendChild(
        mp4DetailsArea
    );

    conversionDetailsBody.appendChild(
        srtDetailsArea
    );


    conversionDetails.appendChild(
        conversionDetailsBody
    );


    // =================================
    // ★ここが重要
    //
    // downloadArea.innerHTML = ""
    // は絶対にしない。
    //
    // appendChildで下へ追加する。
    // =================================

    downloadArea.appendChild(
        conversionDetails
    );


    renderConversionDetails();


    console.log(
        "[CONVERTER] 新しい処理詳細を追加"
    );

}


// =====================================
// 経過時間取得
// =====================================

function calculateElapsed(
    startTime,
    endTime
) {

    if (
        !startTime ||
        !endTime
    ) {

        return null;

    }


    return Math.max(

        0,

        Math.floor(

            (
                endTime.getTime() -
                startTime.getTime()
            ) / 1000

        )

    );

}


// =====================================
// MP3詳細描画
// =====================================

function renderMp3Details() {

    if (!mp3DetailsArea) {
        return;
    }


    const startTime =
        converterState.mp3Process.startTime;


    const endTime =
        converterState.mp3Process.endTime;


    let elapsedText =
        "処理中...";


    const elapsed =
        calculateElapsed(
            startTime,
            endTime
        );


    if (elapsed !== null) {

        elapsedText =
            formatElapsed(
                elapsed
            );

    }


    const status =
        converterState.currentJobStatus ||
        "";


    const title =
        converterState.currentVideoTitle ||
        "不明";


    mp3DetailsArea.innerHTML = `

        <div class="conversion-detail-title">
            【mp3作成】
        </div>

        <div>
            タイトル：
            ${escapeHtml(title)}
        </div>

        <div>
            再生時間：
            ${escapeHtml(
                formatDuration(
                    converterState.currentVideoDuration
                )
            )}
        </div>

        <div>
            実行開始：
            ${escapeHtml(
                formatClock(
                    startTime
                )
            )}
        </div>

        <div>
            実行終了：
            ${escapeHtml(
                formatClock(
                    endTime
                )
            )}
        </div>

        <div>
            処理時間：
            ${escapeHtml(
                elapsedText
            )}
        </div>

        ${
            status
                ? `
                    <div>
                        処理状態：
                        ${escapeHtml(status)}
                    </div>
                  `
                : ""
        }

    `;

}


// =====================================
// MP4詳細描画
// =====================================

function renderMp4Details() {

    if (!mp4DetailsArea) {
        return;
    }


    const startTime =
        converterState.mp4Process
            ? converterState.mp4Process.startTime
            : converterState.mp3Process.startTime;


    const endTime =
        converterState.mp4Process
            ? converterState.mp4Process.endTime
            : converterState.mp3Process.endTime;


    let elapsedText =
        "処理中...";


    const elapsed =
        calculateElapsed(
            startTime,
            endTime
        );


    if (elapsed !== null) {

        elapsedText =
            formatElapsed(
                elapsed
            );

    }


    const status =
        converterState.currentJobStatus ||
        "";


    const title =
        converterState.currentVideoTitle ||
        "不明";


    mp4DetailsArea.innerHTML = `

        <div class="conversion-detail-title">
            【mp4作成】
        </div>

        <div>
            タイトル：
            ${escapeHtml(title)}
        </div>

        <div>
            再生時間：
            ${escapeHtml(
                formatDuration(
                    converterState.currentVideoDuration
                )
            )}
        </div>

        <div>
            実行開始：
            ${escapeHtml(
                formatClock(
                    startTime
                )
            )}
        </div>

        <div>
            実行終了：
            ${escapeHtml(
                formatClock(
                    endTime
                )
            )}
        </div>

        <div>
            処理時間：
            ${escapeHtml(
                elapsedText
            )}
        </div>

        ${
            status
                ? `
                    <div>
                        処理状態：
                        ${escapeHtml(status)}
                    </div>
                  `
                : ""
        }

    `;

}


// =====================================
// SRT詳細描画
// =====================================

function renderSrtDetails() {

    if (!srtDetailsArea) {
        return;
    }


    const hasSrt =
        converterState.srtProcess &&
        converterState.srtProcess.startTime;


    if (!hasSrt) {

        srtDetailsArea.style.display =
            "none";

        return;

    }


    srtDetailsArea.style.display =
        "block";


    const startTime =
        converterState.srtProcess.startTime;


    const endTime =
        converterState.srtProcess.endTime;


    let elapsedText =
        "処理中...";


    const elapsed =
        calculateElapsed(
            startTime,
            endTime
        );


    if (elapsed !== null) {

        elapsedText =
            formatElapsed(
                elapsed
            );

    }


    srtDetailsArea.innerHTML = `

        <div class="conversion-detail-title">
            【srt作成】
        </div>

        <div>
            再生時間：
            ${escapeHtml(
                formatDuration(
                    converterState.currentVideoDuration
                )
            )}
        </div>

        <div>
            実行開始：
            ${escapeHtml(
                formatClock(
                    startTime
                )
            )}
        </div>

        <div>
            実行終了：
            ${escapeHtml(
                formatClock(
                    endTime
                )
            )}
        </div>

        <div>
            処理時間：
            ${escapeHtml(
                elapsedText
            )}
        </div>

    `;

}


// =====================================
// 処理詳細表示
// =====================================

function renderConversionDetails() {

    if (!conversionDetailsBody) {
        return;
    }


    renderMp3Details();

    renderMp4Details();

    renderSrtDetails();

}


// =====================================
// 処理詳細ステータス追加
//
// ★重要
// 上書きしない。
// 下へ追加する。
// =====================================

function updateConversionProgress(
    message
) {

    if (!conversionDetailsBody) {
        return;
    }


    if (!message) {
        return;
    }


    // ---------------------------------
    // 今回のMP3詳細へ追加
    // ---------------------------------

    if (mp3DetailsArea) {

        const progress =
            document.createElement(
                "div"
            );


        progress.className =
            "conversion-progress";


        progress.textContent =
            String(
                message
            );


        mp3DetailsArea.appendChild(
            progress
        );

    }


    console.log(
        "[CONVERTER] 詳細:",
        message
    );

}


// =====================================
// 処理状態を追加表示
//
// 例:
//
// 動画情報を取得しています...
// 変換処理中...
// 処理状態: processing
// mp4 ダウンロード中...
// =====================================

function appendProgressMessage(
    message
) {

    if (!message) {
        return;
    }


    updateConversionProgress(
        message
    );

}


// =====================================
// ダウンロードボタン
// =====================================

function addDownloadButton(
    filename,
    type
) {

    if (!downloadArea) {
        return;
    }


    if (!filename) {
        return;
    }


    const safeFilename =
        String(
            filename
        );


    const normalizedType =
        String(
            type || ""
        ).toLowerCase();


    // =================================
    // 既存確認
    // =================================

    const existing =
        Array.from(
            downloadArea.querySelectorAll(
                "[data-filename]"
            )
        ).find(
            function (element) {

                return (
                    element.dataset.filename ===
                    safeFilename
                );

            }
        );


    if (existing) {

        return;

    }


    // =================================
    // リンク
    // =================================

    const link =
        document.createElement(
            "a"
        );


    link.href =
        makeDownloadUrl(
            safeFilename
        );


    link.download =
        safeFilename;


    link.className =
        "download-button";


    link.dataset.filename =
        safeFilename;


    link.textContent =
        "[" +
        normalizedType.toUpperCase() +
        "]";


    // =================================
    // MP3
    // =================================

    if (
        normalizedType ===
        "mp3"
    ) {

        createMp3GeminiControl(
            safeFilename,
            link
        );


        return;

    }


    // =================================
    // MP4
    // =================================

    downloadArea.appendChild(
        link
    );


    console.log(
        "[CONVERTER] ダウンロード追加:",
        safeFilename
    );

}


// =====================================
// MP3 Gemini UI
// =====================================

function createMp3GeminiControl(
    filename,
    mp3Link
) {

    if (!downloadArea) {
        return;
    }


    if (!filename) {
        return;
    }


    const safeFilename =
        String(
            filename
        );


    // =================================
    // 二重作成防止
    // =================================

    const existing =
        Array.from(
            downloadArea.querySelectorAll(
                "[data-gemini-filename]"
            )
        ).find(
            function (element) {

                return (
                    element.dataset.geminiFilename ===
                    safeFilename
                );

            }
        );


    if (existing) {

        return;

    }


    // =================================
    // container
    // =================================

    const container =
        document.createElement(
            "div"
        );


    container.className =
        "mp3-gemini-container";


    container.dataset.geminiFilename =
        safeFilename;


    // =================================
    // header
    // =================================

    const header =
        document.createElement(
            "div"
        );


    header.className =
        "mp3-gemini-header";


    header.style.display =
        "flex";


    header.style.alignItems =
        "center";


    header.style.flexWrap =
        "nowrap";


    header.style.gap =
        "8px";


    // =================================
    // MP3
    // =================================

    if (mp3Link) {

        header.appendChild(
            mp3Link
        );

    }


    // =================================
    // 開閉
    // =================================

    const toggleButton =
        document.createElement(
            "button"
        );


    toggleButton.type =
        "button";


    toggleButton.className =
        "mp3-gemini-toggle";


    toggleButton.textContent =
        "▼";


    toggleButton.setAttribute(
        "aria-expanded",
        "false"
    );


    toggleButton.setAttribute(
        "aria-label",
        "SRT作成メニューを開く"
    );


    // =================================
    // Geminiボタン
    // =================================

    const srtButton =
        document.createElement(
            "button"
        );


    srtButton.type =
        "button";


    srtButton.className =
        "gemini-srt-button";


    srtButton.textContent =
        "geminiへ(srt)";


    srtButton.style.display =
        "none";


    // =================================
    // SRT
    // =================================

    const srtDownloadArea =
        document.createElement(
            "span"
        );


    srtDownloadArea.className =
        "gemini-srt-download";


    // =================================
    // 結果
    // =================================

    const resultArea =
        document.createElement(
            "div"
        );


    resultArea.className =
        "gemini-srt-result";


    resultArea.style.display =
        "none";


    // =================================
    // 開閉イベント
    // =================================

    toggleButton.addEventListener(
        "click",
        function () {

            const isOpen =
                toggleButton.getAttribute(
                    "aria-expanded"
                ) ===
                "true";


            if (isOpen) {

                toggleButton.textContent =
                    "▼";


                toggleButton.setAttribute(
                    "aria-expanded",
                    "false"
                );


                srtButton.style.display =
                    "none";

            }
            else {

                toggleButton.textContent =
                    "▲";


                toggleButton.setAttribute(
                    "aria-expanded",
                    "true"
                );


                srtButton.style.display =
                    "inline-block";

            }

        }
    );


    // =================================
    // Gemini
    // =================================

    srtButton.addEventListener(
        "click",
        function () {

            createSrtWithGemini(

                safeFilename,

                srtButton,

                resultArea,

                srtDownloadArea

            );

        }
    );


    // =================================
    // 組み立て
    // =================================

    header.appendChild(
        toggleButton
    );


    header.appendChild(
        srtButton
    );


    header.appendChild(
        srtDownloadArea
    );


    container.appendChild(
        header
    );


    container.appendChild(
        resultArea
    );


    // =================================
    // ★既存を消さずに追加
    // =================================

    downloadArea.appendChild(
        container
    );


    console.log(
        "[CONVERTER] MP3 Gemini UI追加:",
        safeFilename
    );

}


// =====================================
// SRT作成
// =====================================

async function createSrtWithGemini(
    filename,
    button,
    resultArea,
    srtDownloadArea
) {

    if (!filename) {
        return;
    }


    if (
        button.dataset.processing ===
        "true"
    ) {

        return;

    }


    button.dataset.processing =
        "true";


    button.disabled =
        true;


    // =================================
    // SRT開始
    // =================================

    converterState.srtProcess.startTime =
        new Date();


    converterState.srtProcess.endTime =
        null;


    converterState.currentSrtFile =
        "";


    renderConversionDetails();


    appendProgressMessage(
        "GeminiへMP3を送信しています..."
    );


    console.log(
        "[CONVERTER] Gemini開始:",
        filename
    );


    try {

        const response =
            await fetch(
                "/gemini-transcribe",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            file:
                                filename

                        })

                }
            );


        const data =
            await readJsonResponse(
                response
            );


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(

                data.message ||
                "Gemini文字起こしに失敗しました。"

            );

        }


        // =================================
        // 完了
        // =================================

        converterState.srtProcess.endTime =
            new Date();


        if (
            data.srt_file
        ) {

            converterState.currentSrtFile =
                data.srt_file;


            if (srtDownloadArea) {

                const link =
                    document.createElement(
                        "a"
                    );


                link.href =
                    makeDownloadUrl(
                        data.srt_file
                    );


                link.download =
                    data.srt_file;


                link.className =
                    "download-button";


                link.textContent =
                    "[SRT]";


                srtDownloadArea.appendChild(
                    link
                );

            }

        }


        renderConversionDetails();


        appendProgressMessage(
            "SRT作成完了"
        );


        console.log(
            "[CONVERTER] SRT完了"
        );

    }
    catch (error) {

        converterState.srtProcess.endTime =
            new Date();


        const message =
            error &&
            error.message
                ? error.message
                : "不明なエラー";


        if (resultArea) {

            resultArea.textContent =
                "SRT作成に失敗しました。\n" +
                message;


            resultArea.style.display =
                "block";


            resultArea.style.color =
                "#b00020";

        }


        appendProgressMessage(
            "SRT作成に失敗しました。\n" +
            message
        );


        renderConversionDetails();

    }
    finally {

        button.dataset.processing =
            "false";


        button.disabled =
            false;

    }

}
// =====================================
// Part 3 / 3
// YouTube Converter
// =====================================


// =====================================
// HTTP JSON
// =====================================

async function readJsonResponse(
    response
) {

    const text =
        await response.text();


    let data;


    try {

        data =
            text
                ? JSON.parse(text)
                : null;

    }
    catch (error) {

        throw new Error(

            "サーバーからJSONではない応答が返されました。" +
            "\nHTTP " +
            response.status +
            "\n" +
            text.substring(
                0,
                500
            )

        );

    }


    if (!data) {

        throw new Error(
            "サーバーから空の応答が返されました。"
        );

    }


    return data;

}


// =====================================
// 動画情報取得
// =====================================

async function getVideoInfo(
    url
) {

    console.log(
        "[CONVERTER] 動画情報取得開始"
    );


    const response =
        await fetch(
            "/video-info",
            {

                method:
                    "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify({

                        url:
                            url

                    })

            }
        );


    const data =
        await readJsonResponse(
            response
        );


    if (
        !response.ok ||
        !data.success
    ) {

        throw new Error(

            data.message ||
            "動画情報の取得に失敗しました。"

        );

    }


    console.log(
        "[CONVERTER] 動画情報取得完了:",
        data
    );


    return data;

}


// =====================================
// 変換API
// =====================================

async function convertVideo(
    url,
    outputs,
    timeRange
) {

    console.log(
        "[CONVERTER] /convert 開始"
    );


    const requestBody = {

        url:
            url,

        outputs:
            outputs,

        start_time:
            timeRange.start_time,

        end_time:
            timeRange.end_time

    };


    console.log(
        "[CONVERTER] convert request:",
        requestBody
    );


    const response =
        await fetch(
            "/convert",
            {

                method:
                    "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(
                        requestBody
                    )

            }
        );


    const data =
        await readJsonResponse(
            response
        );


    if (
        !response.ok ||
        !data.success
    ) {

        throw new Error(

            data.message ||
            "変換APIでエラーが発生しました。"

        );

    }


    if (!data.job_id) {

        throw new Error(
            "変換APIからjob_idが返されませんでした。"
        );

    }


    converterState.currentJobId =
        data.job_id;


    console.log(
        "[CONVERTER] job_id:",
        data.job_id
    );


    return data;

}


// =====================================
// Jobステータス取得
// =====================================

async function getJobStatus(
    jobId
) {

    const response =
        await fetch(
            "/status/" +
            encodeURIComponent(
                jobId
            ),
            {

                method:
                    "GET",

                cache:
                    "no-store"

            }
        );


    const data =
        await readJsonResponse(
            response
        );


    if (!response.ok) {

        throw new Error(

            data.message ||
            "ジョブステータス取得に失敗しました。"

        );

    }


    return data;

}


// =====================================
// Jobステータス表示
// =====================================

function renderJobStatus(
    job
) {

    if (!job) {
        return;
    }


    converterState.currentJob =
        job;


    converterState.currentJobStatus =
        job.status || "";


    const files =
        job.files || {};


    console.log(
        "[CONVERTER] JOB STATUS:",
        job
    );


    // =================================
    // MP3
    // =================================

    if (
        files.mp3 &&
        files.mp3.status ===
            "complete" &&
        files.mp3.filename
    ) {

        converterState.currentMp3File =
            files.mp3.filename;


        addDownloadButton(
            files.mp3.filename,
            "mp3"
        );

    }


    // =================================
    // MP4
    // =================================

    if (
        files.mp4 &&
        files.mp4.status ===
            "complete" &&
        files.mp4.filename
    ) {

        converterState.currentMp4File =
            files.mp4.filename;


        addDownloadButton(
            files.mp4.filename,
            "mp4"
        );

    }


    // =================================
    // 上側ステータス
    //
    // タイトルは消さない。
    // =================================

    if (
        job.status &&
        job.status !== "complete"
    ) {

        appendProgressMessage(

            "処理状態: " +
            job.status

        );

    }


    // =================================
    // サーバーからメッセージ
    // =================================

    if (job.message) {

        appendProgressMessage(
            job.message
        );

    }


    // =================================
    // 処理時間
    // =================================

    if (
        job.execution_seconds_text
    ) {

        appendProgressMessage(

            "処理時間: " +
            job.execution_seconds_text

        );

    }


    renderConversionDetails();

}


// =====================================
// Job監視
// =====================================

async function waitForJob(
    jobId
) {

    const maxWaitMs =
        30 * 60 * 1000;


    const intervalMs =
        2000;


    const startedAt =
        Date.now();


    while (

        Date.now() -
        startedAt <
        maxWaitMs

    ) {

        const job =
            await getJobStatus(
                jobId
            );


        renderJobStatus(
            job
        );


        if (
            job.status ===
            "complete"
        ) {

            console.log(
                "[CONVERTER] JOB COMPLETE"
            );


            return job;

        }


        if (
            job.status ===
            "error"
        ) {

            throw new Error(

                job.message ||
                "変換処理中にエラーが発生しました。"

            );

        }


        await new Promise(
            function (resolve) {

                setTimeout(
                    resolve,
                    intervalMs
                );

            }
        );

    }


    throw new Error(
        "変換処理がタイムアウトしました。"
    );

}


// =====================================
// 結果クリア
//
// ★重要
//
// 新しい処理を開始するときに
// 「現在の実行状態」だけリセットする。
// 過去の履歴は消さない。
//
// downloadArea.innerHTML = ""
// は使用しない。
// =====================================

function clearCurrentState() {

    converterState.currentVideoTitle =
        "";

    converterState.currentVideoDuration =
        "";

    converterState.currentVideoUrl =
        "";

    converterState.currentMp3File =
        "";

    converterState.currentMp4File =
        "";

    converterState.currentSrtFile =
        "";

    converterState.currentJobId =
        "";

    converterState.currentJobStatus =
        "";

    converterState.currentJob =
        null;


    converterState.mp3Process = {

        startTime:
            null,

        endTime:
            null

    };


    converterState.mp4Process = {

        startTime:
            null,

        endTime:
            null

    };


    converterState.srtProcess = {

        startTime:
            null,

        endTime:
            null

    };


    conversionDetails =
        null;


    conversionDetailsBody =
        null;


    mp3DetailsArea =
        null;


    mp4DetailsArea =
        null;


    srtDetailsArea =
        null;

}


// =====================================
// 新しい処理を開始
// =====================================

async function startConversion() {

    console.log(
        "[CONVERTER] 実行ボタン押下"
    );


    // =================================
    // 二重実行防止
    // =================================

    if (
        converterState.isProcessing
    ) {

        console.log(
            "[CONVERTER] すでに処理中です"
        );


        return;

    }


    // =================================
    // URL
    // =================================

    const url =
        urlInput.value.trim();


    if (!url) {

        setStatus(
            "YouTube URLを入力してください。",
            "error"
        );


        urlInput.focus();


        return;

    }


    // =================================
    // 出力形式
    // =================================

    const outputs =
        getSelectedOutputs();


    if (!outputs.length) {

        setStatus(
            "MP3またはMP4を選択してください。",
            "error"
        );


        return;

    }


    // =================================
    // 処理開始
    // =================================

    converterState.isProcessing =
        true;


    convertButton.disabled =
        true;


    // =================================
    // 現在状態だけリセット
    //
    // ★過去のdownloadAreaは消さない
    // =================================

    clearCurrentState();


    converterState.currentVideoUrl =
        url;


    // =================================
    // 上側ステータス
    // =================================

    setStatus(
        "動画情報を取得しています...",
        ""
    );


    // =================================
    // 今回の処理詳細を作成
    //
    // ★過去の履歴の下に追加
    // =================================

    createConversionDetails();


    appendProgressMessage(
        "動画情報を取得しています..."
    );


    try {

        // =================================
        // 動画情報
        // =================================

        const info =
            await getVideoInfo(
                url
            );


        converterState.currentVideoTitle =
            info.title ||
            info.video_title ||
            "不明";


        converterState.currentVideoDuration =
            info.duration ??
            info.video_duration ??
            0;


        // =================================
        // 上側にはタイトル
        // =================================

        setStatus(
            converterState.currentVideoTitle,
            ""
        );


        // =================================
        // 時間範囲
        // =================================

        const timeRange =
            getTimeRange();


        // =================================
        // 開始時刻
        // =================================

        const processStartTime =
            new Date();


        converterState.mp3Process.startTime =
            processStartTime;


        converterState.mp3Process.endTime =
            null;


        converterState.mp4Process.startTime =
            processStartTime;


        converterState.mp4Process.endTime =
            null;


        renderConversionDetails();


        appendProgressMessage(
            "変換処理を開始しています..."
        );


        // =================================
        // /convert
        // =================================

        const data =
            await convertVideo(

                url,

                outputs,

                timeRange

            );


        const jobId =
            data.job_id;


        converterState.currentJobId =
            jobId;


        // =================================
        // 監視開始
        // =================================

        appendProgressMessage(
            "変換処理中..."
        );


        const completedJob =
            await waitForJob(
                jobId
            );


        // =================================
        // 終了時刻
        // =================================

        const processEndTime =
            new Date();


        converterState.mp3Process.endTime =
            processEndTime;


        converterState.mp4Process.endTime =
            processEndTime;


        // =================================
        // 最終ファイル
        // =================================

        const files =
            completedJob.files ||
            {};


        // =================================
        // MP3
        // =================================

        if (
            files.mp3 &&
            files.mp3.filename
        ) {

            converterState.currentMp3File =
                files.mp3.filename;


            addDownloadButton(
                files.mp3.filename,
                "mp3"
            );


            appendProgressMessage(
                "mp3 ダウンロード準備完了"
            );

        }


        // =================================
        // MP4
        // =================================

        if (
            files.mp4 &&
            files.mp4.filename
        ) {

            converterState.currentMp4File =
                files.mp4.filename;


            addDownloadButton(
                files.mp4.filename,
                "mp4"
            );


            appendProgressMessage(
                "mp4 ダウンロード準備完了"
            );

        }


        // =================================
        // ファイル確認
        // =================================

        const hasMp3 =
            Boolean(
                converterState.currentMp3File
            );


        const hasMp4 =
            Boolean(
                converterState.currentMp4File
            );


        if (
            !hasMp3 &&
            !hasMp4
        ) {

            throw new Error(
                "変換は完了しましたが、作成されたファイルが確認できませんでした。"
            );

        }


        // =================================
        // 完了表示
        // =================================

        appendProgressMessage(
            "処理状態: complete"
        );


        renderConversionDetails();


        setStatus(
            converterState.currentVideoTitle,
            "success"
        );


        console.log(
            "[CONVERTER] 変換完了:",
            completedJob
        );

    }
    catch (error) {

        console.error(
            "[CONVERTER] エラー:",
            error
        );


        // =================================
        // 終了時刻
        // =================================

        const errorEndTime =
            new Date();


        if (
            converterState.mp3Process.startTime &&
            !converterState.mp3Process.endTime
        ) {

            converterState.mp3Process.endTime =
                errorEndTime;

        }


        if (
            converterState.mp4Process.startTime &&
            !converterState.mp4Process.endTime
        ) {

            converterState.mp4Process.endTime =
                errorEndTime;

        }


        renderConversionDetails();


        const message =
            error &&
            error.message
                ? error.message
                : "不明なエラー";


        appendProgressMessage(
            "処理エラー: " +
            message
        );


        setStatus(

            "変換中にエラーが発生しました。\n" +
            message,

            "error"

        );

    }
    finally {

        converterState.isProcessing =
            false;


        convertButton.disabled =
            false;


        console.log(
            "[CONVERTER] 処理終了"
        );

    }

}


// =====================================
// 時間入力
// =====================================

function bindTimeInputs() {

    const timeInputs =
        document.querySelectorAll(
            ".time-input"
        );


    timeInputs.forEach(
        function (input) {

            if (
                input.dataset.converterTimeBound ===
                "true"
            ) {

                return;

            }


            input.addEventListener(
                "input",
                function () {

                    this.value =
                        this.value.replace(
                            /[^0-9]/g,
                            ""
                        );

                }
            );


            input.dataset.converterTimeBound =
                "true";

        }
    );

}


// =====================================
// イベント登録
// =====================================

function bindConverterEvents() {

    console.log(
        "[CONVERTER] イベント登録開始"
    );


    // =================================
    // 実行ボタン
    // =================================

    if (
        convertButton
    ) {

        if (
            convertButton.dataset.converterBound !==
            "true"
        ) {

            convertButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    console.log(
                        "[CONVERTER] #convertBtn click"
                    );


                    startConversion();

                }
            );


            convertButton.dataset.converterBound =
                "true";


            console.log(
                "[CONVERTER] #convertBtn 登録完了"
            );

        }

    }


    // =================================
    // Enter
    // =================================

    if (
        urlInput
    ) {

        if (
            urlInput.dataset.converterEnterBound !==
            "true"
        ) {

            urlInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key ===
                        "Enter"
                    ) {

                        event.preventDefault();


                        console.log(
                            "[CONVERTER] Enter"
                        );


                        startConversion();

                    }

                }
            );


            urlInput.dataset.converterEnterBound =
                "true";

        }

    }


    // =================================
    // 時間
    // =================================

    bindTimeInputs();


    console.log(
        "[CONVERTER] イベント登録完了"
    );

}


// =====================================
// 公開API
// =====================================

function setupPublicApi() {

    const publicApi = {

        start:
            startConversion,

        clearResults:
            clearCurrentState,

        getState:
            function () {

                return converterState;

            }

    };


    window.converterMain =
        publicApi;


    window.ConverterMain =
        publicApi;

}


// =====================================
// 初期化
// =====================================

function initializeConverter() {

    console.log(
        "[CONVERTER] 初期化開始"
    );


    // =================================
    // DOM
    // =================================

    urlInput =
        document.getElementById(
            "youtube-url"
        );


    convertButton =
        document.getElementById(
            "convertBtn"
        );


    conversionStatusArea =
        document.getElementById(
            "conversion-status-area"
        );


    downloadArea =
        document.getElementById(
            "downloadArea"
        );


    // =================================
    // 必須DOM
    // =================================

    if (!urlInput) {

        console.error(
            "[CONVERTER] #youtube-url がありません"
        );

        return;

    }


    if (!convertButton) {

        console.error(
            "[CONVERTER] #convertBtn がありません"
        );

        return;

    }


    // =================================
    // State
    // =================================

    converterState =
        {

            currentVideoTitle:
                "",

            currentVideoDuration:
                "",

            currentVideoUrl:
                "",

            currentMp3File:
                "",

            currentMp4File:
                "",

            currentSrtFile:
                "",

            currentJobId:
                "",

            currentJobStatus:
                "",

            currentJob:
                null,

            isProcessing:
                false,

            mp3Process:
                {

                    startTime:
                        null,

                    endTime:
                        null

                },

            mp4Process:
                {

                    startTime:
                        null,

                    endTime:
                        null

                },

            srtProcess:
                {

                    startTime:
                        null,

                    endTime:
                        null

                }

        };


    window.converterState =
        converterState;


    // =================================
    // イベント
    // =================================

    bindConverterEvents();


    // =================================
    // 公開API
    // =================================

    setupPublicApi();


    console.log(
        "[CONVERTER] converter.js 読み込み完了"
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
        initializeConverter,
        {
            once:
                true
        }
    );

}
else {

    initializeConverter();

}
