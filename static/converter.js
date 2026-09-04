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
