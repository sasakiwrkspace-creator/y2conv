// =====================================
// YouTube Converter
// converter.js
//
// タブ1：YouTube変換専用
//
// 役割:
// ・YouTube URL受付
// ・MP3 / MP4 変換API実行
// ・job_idによる処理状況監視
// ・MP3 / MP4ダウンロード表示
// ・MP3完成後のSRT/Gemini処理表示
// ・処理詳細表示
// ・ステータス履歴を下方向へ蓄積
//
// 注意:
// ・converterUtils.js は使用しない
// ・converterStatus.js は使用しない
// ・タブ2の処理には触れない
// ・タブ1の実行ボタンは #convertBtn
// ・上側ステータスは現在のタイトルのみ
// ・処理詳細は折り畳み表示
// ・過去のステータスは消去しない
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


            // =================================
            // ステータス履歴
            //
            // ここは clearResults() でも
            // 消去しない。
            // =================================

            statusHistory:
                [],


            // =================================
            // 現在の処理詳細ログ
            // =================================

            currentProgressHistory:
                [],


            // =================================
            // MP3処理時間
            // =================================

            mp3Process:
                {

                    startTime:
                        null,

                    endTime:
                        null

                },


            // =================================
            // SRT処理時間
            // =================================

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


        // =====================================
        // ステータス履歴DOM
        // =====================================

        let statusHistoryArea =
            null;


        // =====================================
        // ステータス履歴エリア作成
        // =====================================

        function createStatusHistoryArea() {

            if (!downloadArea) {

                return null;

            }


            // ---------------------------------
            // すでに存在する場合
            // ---------------------------------

            const existing =
                downloadArea.querySelector(
                    ".converter-status-history"
                );


            if (existing) {

                statusHistoryArea =
                    existing;

                return existing;

            }


            // ---------------------------------
            // 新規作成
            // ---------------------------------

            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "converter-status-history";


            wrapper.style.marginTop =
                "12px";


            wrapper.style.paddingTop =
                "8px";


            wrapper.style.borderTop =
                "1px solid #ddd";


            // ---------------------------------
            // タイトル
            // ---------------------------------

            const title =
                document.createElement(
                    "div"
                );


            title.className =
                "converter-status-history-title";


            title.textContent =
                "STATUS履歴";


            title.style.fontWeight =
                "bold";


            title.style.marginBottom =
                "6px";


            wrapper.appendChild(
                title
            );


            // ---------------------------------
            // 本体
            // ---------------------------------

            const body =
                document.createElement(
                    "div"
                );


            body.className =
                "converter-status-history-body";


            body.style.whiteSpace =
                "pre-line";


            body.style.fontSize =
                "0.95em";


            wrapper.appendChild(
                body
            );


            downloadArea.appendChild(
                wrapper
            );


            statusHistoryArea =
                wrapper;


            return wrapper;

        }


        // =====================================
        // ステータス履歴本体取得
        // =====================================

        function getStatusHistoryBody() {

            const area =
                createStatusHistoryArea();


            if (!area) {

                return null;

            }


            return area.querySelector(
                ".converter-status-history-body"
            );

        }


        // =====================================
        // ステータス履歴描画
        // =====================================

        function renderStatusHistory() {

            const body =
                getStatusHistoryBody();


            if (!body) {

                return;

            }


            body.innerHTML =
                "";


            converterState.statusHistory.forEach(
                function (item) {

                    const entry =
                        document.createElement(
                            "div"
                        );


                    entry.className =
                        "converter-status-history-entry";


                    const time =
                        formatClock(
                            item.time
                        );


                    const message =
                        String(
                            item.message || ""
                        );


                    entry.textContent =
                        time +
                        "  " +
                        message;


                    // -----------------------------
                    // 色
                    // -----------------------------

                    if (
                        item.type ===
                        "error"
                    ) {

                        entry.style.color =
                            "#b00020";

                    }
                    else if (
                        item.type ===
                        "success"
                    ) {

                        entry.style.color =
                            "#176b2c";

                    }
                    else {

                        entry.style.color =
                            "#222";

                    }


                    body.appendChild(
                        entry
                    );

                }
            );

        }


        // =====================================
        // ステータス履歴追加
        // =====================================

        function appendStatusHistory(
            message,
            type
        ) {

            const text =
                String(
                    message || ""
                ).trim();


            if (!text) {

                return;

            }


            converterState.statusHistory.push({

                time:
                    new Date(),

                message:
                    text,

                type:
                    type || ""

            });


            renderStatusHistory();


            console.log(
                "[CONVERTER] STATUS HISTORY:",
                text
            );

        }


        // =====================================
        // 上側ステータス
        //
        // ここは「現在の状態」だけを表示。
        // 過去ログはstatusHistoryへ保存。
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


                if (
                    type ===
                    "error"
                ) {

                    conversionStatusArea.style.color =
                        "#b00020";

                }
                else if (
                    type ===
                    "success"
                ) {

                    conversionStatusArea.style.color =
                        "#176b2c";

                }
                else {

                    conversionStatusArea.style.color =
                        "#222";

                }

            }


            // ---------------------------------
            // 履歴には追加
            // ---------------------------------

            appendStatusHistory(
                text,
                type
            );


            console.log(
                "[CONVERTER] STATUS:",
                text
            );

        }


        // =====================================
        // 処理中ステータス
        //
        // 上側は最新状態だけ。
        // 履歴は下側へ追加。
        // =====================================

        function setProgress(
            message
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


                conversionStatusArea.style.color =
                    "#222";

            }


            // ---------------------------------
            // 履歴追加
            // ---------------------------------

            appendStatusHistory(
                text,
                ""
            );


            console.log(
                "[CONVERTER] PROGRESS:",
                text
            );

        }


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
                        value ===
                        "mp3"
                    ) {

                        outputs.push(
                            "mp3"
                        );

                    }
                    else if (
                        value ===
                        "mp4"
                    ) {

                        outputs.push(
                            "mp4"
                        );

                    }
                    else if (
                        value ===
                        "subtitle_mp4"
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
        // 処理詳細DOM
        // =====================================

        let conversionDetails =
            null;


        let conversionDetailsBody =
            null;


        let mp3DetailsArea =
            null;


        let srtDetailsArea =
            null;


        // =====================================
        // 処理詳細作成
        // =====================================

        function createConversionDetails() {

            if (!downloadArea) {

                return;

            }


            // ---------------------------------
            // 既存削除
            //
            // 注意:
            // STATUS履歴は削除しない。
            // ---------------------------------

            const existing =
                downloadArea.querySelector(
                    ".conversion-details"
                );


            if (existing) {

                existing.remove();

            }


            conversionDetails =
                document.createElement(
                    "details"
                );


            conversionDetails.className =
                "conversion-details";


            conversionDetails.open =
                false;


            const summary =
                document.createElement(
                    "summary"
                );


            summary.textContent =
                "処理詳細";


            conversionDetails.appendChild(
                summary
            );


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
            // SRT
            // ---------------------------------

            srtDetailsArea =
                document.createElement(
                    "div"
                );


            srtDetailsArea.className =
                "conversion-detail-section";


            conversionDetailsBody.appendChild(
                mp3DetailsArea
            );


            conversionDetailsBody.appendChild(
                srtDetailsArea
            );


            conversionDetails.appendChild(
                conversionDetailsBody
            );


            // ---------------------------------
            // 履歴より先に追加
            // ---------------------------------

            downloadArea.appendChild(
                conversionDetails
            );


            renderConversionDetails();

        }


        // =====================================
        // 処理詳細表示
        // =====================================

        function renderConversionDetails() {

            if (
                !conversionDetailsBody
            ) {

                return;

            }


            // =================================
            // MP3詳細
            // =================================

            if (mp3DetailsArea) {

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
                        ? "処理状態：" +
                          converterState.currentJobStatus
                        : "";


                mp3DetailsArea.innerHTML = `

                    <div class="conversion-detail-title">
                        【mp3作成】
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
                                    ${escapeHtml(
                                        statusText
                                    )}
                                </div>
                              `
                            : ""
                    }

                `;


                // ---------------------------------
                // 現在処理の進行ログ
                // ---------------------------------

                if (
                    converterState.currentProgressHistory &&
                    converterState.currentProgressHistory.length
                ) {

                    converterState.currentProgressHistory.forEach(
                        function (message) {

                            const progress =
                                document.createElement(
                                    "div"
                                );


                            progress.className =
                                "conversion-progress";


                            progress.textContent =
                                String(
                                    message || ""
                                );


                            mp3DetailsArea.appendChild(
                                progress
                            );

                        }
                    );

                }

            }


            // =================================
            // SRT詳細
            // =================================

            if (srtDetailsArea) {

                const hasSrtProcess =
                    converterState.srtProcess.startTime !== null;


                if (!hasSrtProcess) {

                    srtDetailsArea.style.display =
                        "none";

                }
                else {

                    srtDetailsArea.style.display =
                        "block";


                    const startTime =
                        converterState.srtProcess.startTime;


                    const endTime =
                        converterState.srtProcess.endTime;


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

            }

        }


        // =====================================
        // 処理詳細ステータス
        // =====================================

        function updateConversionProgress(
            message
        ) {

            const text =
                String(
                    message || ""
                ).trim();


            if (!text) {

                return;

            }


            // ---------------------------------
            // 現在の処理履歴へ追加
            // ---------------------------------

            converterState.currentProgressHistory.push(
                text
            );


            // ---------------------------------
            // 再描画
            // ---------------------------------

            renderConversionDetails();

        }


        // =====================================
        // 次のPartで続く
        // =====================================
// =====================================
// YouTube Converter
// converter.js
//
// Part 2 / 3
//
// ・処理詳細
// ・ステータス履歴
// ・SRT/Gemini
// ・ダウンロードUI
// =====================================


// =====================================
// ステータス履歴
// =====================================
//
// 重要:
// setStatus() / setProgress() で
// 既存表示を上書きしない。
//
// 新しいステータスを下へ追加する。
//
// 例:
//
// STATUS: 運転上手な人が絶対にやらないこと【ずんだもん解説】
//
// 動画情報を取得しています... converter.js
// 変換処理中... converter.js
// 処理状態: processing
// mp4 ダウンロード中・・・
//
// 【処理状態】: processing
//
// 【mp4作成】
// ...
//
// 【mp3作成】
// ...
//
// =====================================

let statusHistoryArea = null;


// =====================================
// ステータス履歴エリア作成
// =====================================

function createStatusHistoryArea() {

    if (!conversionStatusArea) {

        return null;

    }


    // ---------------------------------
    // 既存の履歴エリアを探す
    // ---------------------------------

    let existing =
        conversionStatusArea.querySelector(
            ".converter-status-history"
        );


    if (existing) {

        statusHistoryArea =
            existing;

        return existing;

    }


    // ---------------------------------
    // 新規作成
    // ---------------------------------

    existing =
        document.createElement(
            "div"
        );


    existing.className =
        "converter-status-history";


    existing.style.whiteSpace =
        "pre-line";


    existing.style.display =
        "block";


    existing.style.width =
        "100%";


    existing.style.boxSizing =
        "border-box";


    conversionStatusArea.innerHTML =
        "";


    conversionStatusArea.appendChild(
        existing
    );


    statusHistoryArea =
        existing;


    return existing;

}


// =====================================
// ステータス1行追加
// =====================================

function appendStatus(
    message,
    type
) {

    const text =
        String(
            message || ""
        ).trim();


    if (!text) {

        return;

    }


    const area =
        createStatusHistoryArea();


    if (!area) {

        console.log(
            "[CONVERTER] STATUS:",
            text
        );

        return;

    }


    const line =
        document.createElement(
            "div"
        );


    line.className =
        "converter-status-line";


    line.textContent =
        text;


    // ---------------------------------
    // 色
    // ---------------------------------

    if (type === "error") {

        line.style.color =
            "#b00020";

    }
    else if (
        type === "success"
    ) {

        line.style.color =
            "#176b2c";

    }
    else {

        line.style.color =
            "#222";

    }


    area.appendChild(
        line
    );


    // ---------------------------------
    // 常に一番下を表示
    // ---------------------------------

    area.scrollTop =
        area.scrollHeight;


    console.log(
        "[CONVERTER] STATUS:",
        text
    );

}


// =====================================
// 上側ステータス
// =====================================
//
// タイトル表示専用。
// ここでは履歴を消さない。
//
// =====================================

function setStatus(
    message,
    type
) {

    const text =
        String(
            message || ""
        ).trim();


    if (!text) {

        return;

    }


    appendStatus(
        text,
        type
    );

}


// =====================================
// 処理中ステータス
// =====================================
//
// 以前:
//
// conversionStatusArea.textContent = text;
//
// これだと毎回上書きされる。
//
// 現在:
//
// appendStatus()
// で下へ追加する。
//
// =====================================

function setProgress(
    message
) {

    const text =
        String(
            message || ""
        ).trim();


    if (!text) {

        return;

    }


    appendStatus(
        text,
        ""
    );


    console.log(
        "[CONVERTER] PROGRESS:",
        text
    );

}


// =====================================
// 処理詳細DOM
// =====================================

let conversionDetails =
    null;


let conversionDetailsBody =
    null;


let mp3DetailsArea =
    null;


let srtDetailsArea =
    null;


// =====================================
// 処理詳細作成
// =====================================

function createConversionDetails() {

    if (!downloadArea) {

        return;

    }


    // ---------------------------------
    // 既存削除
    // ---------------------------------

    const existing =
        downloadArea.querySelector(
            ".conversion-details"
        );


    if (existing) {

        existing.remove();

    }


    conversionDetails =
        document.createElement(
            "details"
        );


    conversionDetails.className =
        "conversion-details";


    conversionDetails.open =
        false;


    const summary =
        document.createElement(
            "summary"
        );


    summary.textContent =
        "処理詳細";


    conversionDetails.appendChild(
        summary
    );


    conversionDetailsBody =
        document.createElement(
            "div"
        );


    conversionDetailsBody.className =
        "conversion-details-body";


    // =================================
    // MP3
    // =================================

    mp3DetailsArea =
        document.createElement(
            "div"
        );


    mp3DetailsArea.className =
        "conversion-detail-section";


    // =================================
    // SRT
    // =================================

    srtDetailsArea =
        document.createElement(
            "div"
        );


    srtDetailsArea.className =
        "conversion-detail-section";


    conversionDetailsBody.appendChild(
        mp3DetailsArea
    );


    conversionDetailsBody.appendChild(
        srtDetailsArea
    );


    conversionDetails.appendChild(
        conversionDetailsBody
    );


    downloadArea.appendChild(
        conversionDetails
    );


    renderConversionDetails();

}


// =====================================
// 処理詳細表示
// =====================================

function renderConversionDetails() {

    if (!conversionDetailsBody) {

        return;

    }


    // =================================
    // MP3詳細
    // =================================

    if (mp3DetailsArea) {

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
                ? "処理状態：" +
                  converterState.currentJobStatus
                : "";


        mp3DetailsArea.innerHTML = `

            <div class="conversion-detail-title">
                【mp3作成】
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
                            ${escapeHtml(
                                statusText
                            )}
                        </div>
                      `
                    : ""
            }

        `;

    }


    // =================================
    // SRT詳細
    // =================================

    if (srtDetailsArea) {

        const hasSrtProcess =
            converterState.srtProcess.startTime !== null;


        if (!hasSrtProcess) {

            srtDetailsArea.style.display =
                "none";

        }
        else {

            srtDetailsArea.style.display =
                "block";


            const startTime =
                converterState.srtProcess.startTime;


            const endTime =
                converterState.srtProcess.endTime;


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

    }

}


// =====================================
// 処理詳細ステータス追加
// =====================================

function updateConversionProgress(
    message
) {

    if (!mp3DetailsArea) {

        return;

    }


    const text =
        String(
            message || ""
        ).trim();


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


    mp3DetailsArea.appendChild(
        progress
    );


}


// =====================================
// SRT作成
//
// /gemini-transcribe
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

    const srtStartTime =
        new Date();


    converterState.srtProcess.startTime =
        srtStartTime;


    converterState.srtProcess.endTime =
        null;


    converterState.currentSrtFile =
        "";


    renderConversionDetails();


    setProgress(
        "GeminiへMP3を送信しています..."
    );


    updateConversionProgress(
        "GeminiへMP3を送信しています..."
    );


    console.log(
        "[CONVERTER] Gemini送信開始:",
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


        console.log(
            "[CONVERTER] Gemini処理完了:",
            data
        );


        // =================================
        // SRT終了
        // =================================

        const srtEndTime =
            new Date();


        converterState.srtProcess.endTime =
            srtEndTime;


        // =================================
        // SRTファイル
        // =================================

        if (
            data.srt_file
        ) {

            converterState.currentSrtFile =
                data.srt_file;


            if (
                srtDownloadArea
            ) {

                const existingSrt =
                    srtDownloadArea.querySelector(
                        "[data-srt-filename]"
                    );


                if (!existingSrt) {

                    const srtLink =
                        document.createElement(
                            "a"
                        );


                    srtLink.href =
                        makeDownloadUrl(
                            data.srt_file
                        );


                    srtLink.download =
                        data.srt_file;


                    srtLink.className =
                        "download-button";


                    srtLink.dataset.srtFilename =
                        data.srt_file;


                    srtLink.textContent =
                        "[SRT]";


                    srtDownloadArea.appendChild(
                        srtLink
                    );

                }

            }

        }


        // =================================
        // 完了メッセージは上書きしない
        // =================================

        setProgress(
            "SRT作成完了"
        );


        if (resultArea) {

            resultArea.textContent =
                "";


            resultArea.style.display =
                "none";

        }


        renderConversionDetails();


        console.log(
            "[CONVERTER] SRT作成完了"
        );

    }
    catch (error) {

        console.error(
            "[CONVERTER] Geminiエラー:",
            error
        );


        const srtEndTime =
            new Date();


        converterState.srtProcess.endTime =
            srtEndTime;


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


        setProgress(
            "SRT作成に失敗しました。\n" +
            message
        );


        updateConversionProgress(
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
// MP3用Gemini UI
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
    // 外側
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
    // ヘッダー
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
    // MP3リンク
    // =================================

    if (mp3Link) {

        header.appendChild(
            mp3Link
        );

    }


    // =================================
    // 開閉ボタン
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


    toggleButton.style.flex =
        "0 0 auto";


    toggleButton.style.whiteSpace =
        "nowrap";


    toggleButton.setAttribute(
        "aria-expanded",
        "false"
    );


    toggleButton.setAttribute(
        "aria-label",
        "SRT作成メニューを開く"
    );


    // =================================
    // SRTボタン
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


    srtButton.style.flex =
        "0 0 auto";


    srtButton.style.whiteSpace =
        "nowrap";


    // =================================
    // SRTダウンロード
    // =================================

    const srtDownloadArea =
        document.createElement(
            "span"
        );


    srtDownloadArea.className =
        "gemini-srt-download";


    srtDownloadArea.style.display =
        "inline-flex";


    srtDownloadArea.style.alignItems =
        "center";


    srtDownloadArea.style.gap =
        "8px";


    // =================================
    // エラー
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
    // 開閉
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

                srtButton.style.display =
                    "none";


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

            }
            else {

                srtButton.style.display =
                    "inline-block";


                toggleButton.textContent =
                    "▲";


                toggleButton.setAttribute(
                    "aria-expanded",
                    "true"
                );


                toggleButton.setAttribute(
                    "aria-label",
                    "SRT作成メニューを閉じる"
                );

            }

        }
    );


    // =================================
    // Gemini実行
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


    downloadArea.appendChild(
        container
    );


    console.log(
        "[CONVERTER] MP3 Gemini UI追加:",
        safeFilename
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
            type
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
    // ダウンロードリンク
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
        "[CONVERTER] ダウンロードボタン追加:",
        safeFilename
    );

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
            // 処理中
            // =================================

            if (
                job.status !== "complete"
            ) {

                const lines =
                    [];


                if (job.status) {

                    lines.push(
                        "処理状態: " +
                        job.status
                    );

                }


                if (job.message) {

                    lines.push(
                        job.message
                    );

                }


                if (
                    job.execution_seconds_text
                ) {

                    lines.push(
                        "処理時間: " +
                        job.execution_seconds_text
                    );

                }


                const progressMessage =
                    lines.join(
                        "\n"
                    );


                setProgress(
                    progressMessage
                );


                if (
                    conversionDetails
                ) {

                    updateConversionProgress(
                        progressMessage
                    );

                }

            }

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
        // メイン変換
        // =====================================

        async function startConversion() {

            if (
                converterState.isProcessing
            ) {

                return;

            }


            const url =
                urlInput.value.trim();


            if (!url) {

                appendStatus(
                    "YouTube URLを入力してください。",
                    "error"
                );


                urlInput.focus();


                return;

            }


            const outputs =
                getSelectedOutputs();


            if (!outputs.length) {

                appendStatus(
                    "MP3またはMP4を選択してください。",
                    "error"
                );


                return;

            }


            converterState.isProcessing =
                true;


            // =================================
            // 前回結果を消さない
            // =================================

            clearResults();


            converterState.currentVideoUrl =
                url;


            convertButton.disabled =
                true;


            // =================================
            // 新しい処理詳細
            // =================================

            createConversionDetails();


            // =================================
            // 開始
            // =================================

            appendStatus(
                "動画情報を取得しています...",
                "processing"
            );


            updateConversionProgress(
                "動画情報を取得しています..."
            );


            try {

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
                // タイトル表示
                // =================================

                appendStatus(
                    converterState.currentVideoTitle,
                    "title"
                );


                // =================================
                // 時間範囲
                // =================================

                const timeRange =
                    getTimeRange();


                // =================================
                // 変換開始時刻
                // =================================

                const mp3StartTime =
                    new Date();


                converterState.mp3Process.startTime =
                    mp3StartTime;


                converterState.mp3Process.endTime =
                    null;


                renderConversionDetails();


                updateConversionProgress(
                    "変換ジョブを開始しています..."
                );


                // =================================
                // 変換開始
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
                // Job監視
                // =================================

                appendStatus(
                    "変換処理中...",
                    "processing"
                );


                updateConversionProgress(
                    "変換処理中..."
                );


                const completedJob =
                    await waitForJob(
                        jobId
                    );


                // =================================
                // 終了時刻
                // =================================

                const mp3EndTime =
                    new Date();


                converterState.mp3Process.endTime =
                    mp3EndTime;


                renderConversionDetails();


                // =================================
                // 最終ファイル
                // =================================

                const files =
                    completedJob.files ||
                    {};


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

                }


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
                // 詳細更新
                // =================================

                renderConversionDetails();


                // =================================
                // 完了ステータス
                // =================================

                appendStatus(
                    "処理状態：complete",
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

                if (
                    converterState.mp3Process.startTime &&
                    !converterState.mp3Process.endTime
                ) {

                    converterState.mp3Process.endTime =
                        new Date();

                }


                renderConversionDetails();


                const message =
                    error &&
                    error.message
                        ? error.message
                        : "不明なエラー";


                appendStatus(

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
        // クリック
        // =====================================

        if (
            convertButton.dataset.converterBound !==
            "true"
        ) {

            convertButton.addEventListener(
                "click",
                startConversion
            );


            convertButton.dataset.converterBound =
                "true";

        }


        // =====================================
        // Enter
        // =====================================

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

                        startConversion();

                    }

                }
            );


            urlInput.dataset.converterEnterBound =
                "true";

        }


        // =====================================
        // 時間入力
        // =====================================

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


        // =====================================
        // 公開API
        // =====================================

        const publicApi = {

            start:
                startConversion,

            clearResults:
                clearResults,

            getState:
                function () {

                    return converterState;

                }

        };


        window.converterMain =
            publicApi;


        window.ConverterMain =
            publicApi;


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


})();
