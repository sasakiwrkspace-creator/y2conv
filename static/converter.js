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
// ・ステータス履歴を下へ追加
//
// 注意:
// ・converterUtils.js は使用しない
// ・converterStatus.js は使用しない
// ・タブ2の処理には触れない
// ・タブ1の実行ボタンは #convertBtn
// ・上側ステータスはタイトルのみ
// ・処理詳細は折り畳み表示
// ・ステータス履歴は新しい処理開始時も消さない
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
            // 新しい処理でも消さない。
            // =================================

            statusHistory:
                [],


            // =================================
            // 処理進捗履歴
            //
            // 新しい処理でも消さない。
            // =================================

            progressHistory:
                [],


            // ---------------------------------
            // MP3処理時間
            // ---------------------------------

            mp3Process:
                {

                    startTime:
                        null,

                    endTime:
                        null

                },


            // ---------------------------------
            // SRT処理時間
            // ---------------------------------

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
        // 上側ステータス
        //
        // 上側は最新状態だけを表示。
        // 履歴は下側へ追加。
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


            // =================================
            // 履歴へ追加
            // =================================

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
        // 上側は最新状態。
        // 下側には履歴として追加。
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


            // =================================
            // 履歴へ追加
            // =================================

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

        }


        // =====================================
        // ステータス履歴表示
        //
        // downloadAreaの一番下へ追加。
        // =====================================

        function renderStatusHistory() {

            if (!downloadArea) {

                return;

            }


            let historyArea =
                downloadArea.querySelector(
                    ".converter-status-history"
                );


            // =================================
            // 初回作成
            // =================================

            if (!historyArea) {

                historyArea =
                    document.createElement(
                        "div"
                    );


                historyArea.className =
                    "converter-status-history";


                historyArea.style.marginTop =
                    "16px";


                historyArea.style.paddingTop =
                    "10px";


                historyArea.style.borderTop =
                    "1px solid #ddd";


                downloadArea.appendChild(
                    historyArea
                );

            }


            // =================================
            // いったん再描画
            // =================================

            historyArea.innerHTML =
                "";


            converterState.statusHistory.forEach(
                function (item) {

                    const entry =
                        document.createElement(
                            "div"
                        );


                    entry.className =
                        "converter-status-history-entry";


                    entry.style.marginBottom =
                        "4px";


                    entry.style.whiteSpace =
                        "pre-line";


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


                    const time =
                        formatClock(
                            item.time
                        );


                    entry.textContent =
                        time +
                        "  " +
                        item.message;


                    historyArea.appendChild(
                        entry
                    );

                }
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
            // 現在の処理詳細だけ削除
            //
            // ステータス履歴は削除しない。
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


                // =================================
                // 進捗履歴
                // =================================

                if (
                    converterState.progressHistory &&
                    converterState.progressHistory.length
                ) {

                    converterState.progressHistory.forEach(
                        function (message) {

                            const progress =
                                document.createElement(
                                    "div"
                                );


                            progress.className =
                                "conversion-progress";


                            progress.style.marginTop =
                                "4px";


                            progress.style.whiteSpace =
                                "pre-line";


                            progress.textContent =
                                message;


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
        //
        // 履歴として保存する。
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


            converterState.progressHistory.push(
                text
            );


            renderConversionDetails();

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
            // SRT開始時刻
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


            updateConversionProgress(
                "GeminiへMP3を送信しています..."
            );


            appendStatusHistory(
                "GeminiへMP3を送信しています...",
                ""
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
                // SRT終了時刻
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


                    // -----------------------------
                    // SRTダウンロードリンク
                    // -----------------------------

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
                // 結果エリア
                // =================================

                if (resultArea) {

                    resultArea.textContent =
                        "";


                    resultArea.style.display =
                        "none";

                }


                renderConversionDetails();


                appendStatusHistory(
                    "SRT作成完了",
                    "success"
                );


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


                renderConversionDetails();


                updateConversionProgress(
                    "SRT作成に失敗しました。\n" +
                    message
                );


                appendStatusHistory(
                    "SRT作成に失敗しました。\n" +
                    message,
                    "error"
                );

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
            // ダウンロード行
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
            // SRT操作ボタン
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
            // SRT結果表示
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
            // エラー表示
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


            // =================================
            // downloadAreaへ追加
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
        // 現在の結果だけクリア
        //
        // ★重要
        //
        // ステータス履歴は消さない。
        // =====================================

        function clearResults() {

            if (downloadArea) {

                const elementsToRemove =
                    downloadArea.querySelectorAll(
                        ".mp3-gemini-container, " +
                        ".download-button, " +
                        ".conversion-details"
                    );


                elementsToRemove.forEach(
                    function (element) {

                        element.remove();

                    }
                );

            }


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    "";


                conversionStatusArea.style.display =
                    "none";


                conversionStatusArea.style.color =
                    "#222";

            }


            conversionDetails =
                null;


            conversionDetailsBody =
                null;


            mp3DetailsArea =
                null;


            srtDetailsArea =
                null;


            // =================================
            // 現在の処理情報だけリセット
            //
            // statusHistory はリセットしない。
            // progressHistory は新しい処理用に
            // リセットする。
            // =================================

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


            converterState.progressHistory =
                [];


            converterState.mp3Process =
                {

                    startTime:
                        null,

                    endTime:
                        null

                };


            converterState.srtProcess =
                {

                    startTime:
                        null,

                    endTime:
                        null

                };


            // =================================
            // 履歴を再表示
            //
            // clearResults()でDOMから
            // 履歴が消えてしまった場合に備える。
            // =================================

            renderStatusHistory();

        }


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
        // 動画情報
        // =====================================

        async function getVideoInfo(
            url
        ) {

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


            return data;

        }


        // =====================================
        // Jobステータス
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


                if (progressMessage) {

                    setProgress(
                        progressMessage
                    );


                    // -----------------------------
                    // 処理詳細にも反映
                    // -----------------------------

                    if (
                        conversionDetails
                    ) {

                        updateConversionProgress(
                            progressMessage
                        );

                    }

                }

            }


            // =================================
            // 完了
            // =================================

            if (
                job.status ===
                "complete"
            ) {

                appendStatusHistory(
                    "処理状態: complete",
                    "success"
                );

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

                setStatus(
                    "YouTube URLを入力してください。",
                    "error"
                );


                urlInput.focus();


                return;

            }


            const outputs =
                getSelectedOutputs();


            if (!outputs.length) {

                setStatus(
                    "MP3またはMP4を選択してください。",
                    "error"
                );


                return;

            }


            converterState.isProcessing =
                true;


            // =================================
            // 現在の処理だけクリア
            //
            // 履歴は残す。
            // =================================

            clearResults();


            converterState.currentVideoUrl =
                url;


            convertButton.disabled =
                true;


            // =================================
            // 処理詳細を先に作る
            // =================================

            createConversionDetails();


            // =================================
            // 新しい処理開始を履歴に追加
            // =================================

            appendStatusHistory(
                "=====================================\n新しい変換処理開始",
                ""
            );


            // =================================
            // 動画情報
            // =================================

            setProgress(
                "動画情報を取得しています..."
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
                // 上側にはタイトルだけ表示
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
                // MP3 / MP4処理開始時刻
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

                setProgress(
                    "変換処理中..."
                );


                updateConversionProgress(
                    "変換処理中..."
                );


                const completedJob =
                    await waitForJob(
                        jobId
                    );


                // =================================
                // MP3 / MP4処理終了時刻
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
                // 処理詳細更新
                // =================================

                renderConversionDetails();


                // =================================
                // 完了履歴
                // =================================

                appendStatusHistory(
                    "変換処理完了",
                    "success"
                );


                // =================================
                // 完了
                // =================================

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


                // ---------------------------------
                // MP3処理が開始済みなら終了時刻を記録
                // ---------------------------------

                if (
                    converterState.mp3Process.startTime &&
                    !converterState.mp3Process.endTime
                ) {
