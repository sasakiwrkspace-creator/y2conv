// =====================================
// YouTube Converter
// converter.js
//
// タブ1：YouTube変換専用
//
// 役割:
// ・YouTube URL受付
// ・MP3 / MP4 変換API実行
// ・subtitle_mp4選択時の字幕MP4連続処理API実行
// ・job_idによる処理状況監視
// ・MP3ダウンロード表示
// ・MP3からGeminiへ字幕SRT作成要求
// ・SRTダウンロード表示
// ・MP4ダウンロード表示
// ・字幕MP4ダウンロード表示
// ・処理詳細表示
// ・処理ログ表示
//
// 注意:
// ・converterUtils.js は使用しない
// ・converterStatus.js は使用しない
// ・タブ2の処理には触れない
// ・タブ1の実行ボタンは #convertBtn
// ・通常のMP3 / MP4処理は既存動作を維持する
// ・subtitle_mp4選択時はconvert.py側で
//   subtitle_mp4.pyへ処理を委譲する
// ・subtitle_mp4.pyが
//   MP4 → MP3 → SRT → 字幕MP4
//   の連続処理を担当する
//
// 表示仕様:
//
// 処理中:
//
//     動画タイトル
//
//     処理ログ
//     14:32:01  変換処理を開始します。
//     14:32:02  動画情報を取得しています...
//     14:32:04  動画情報の取得が完了しました。
//     14:32:05  変換ジョブを開始しました。
//     ...
//
// 正常終了後:
//
//     動画タイトル
//
//     [字幕MP4] [MP3] [MP4] [SRT]
//
//     ▼ 処理詳細
//         再生時間：...
//         実行開始：...
//         実行終了：...
//         処理時間：...
//
//         処理ログ
//         14:32:01 ...
//         14:32:02 ...
//
// エラー時:
//
//     処理ログはそのまま表示する。
//
// MP4 / 字幕MP4には
// 折り畳み・▲を付けない。
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

            currentSubtitleMp4File:
                "",

            currentJobId:
                "",

            currentJobStatus:
                "",

            currentJob:
                null,

            currentSrtJobId:
                "",

            currentSrtJobStatus:
                "",

            isSrtProcessing:
                false,

            isProcessing:
                false,

            processingLog:
                [],

            lastJobMessage:
                "",

            lastJobStatus:
                ""

        };


        window.converterState =
            converterState;


        // =====================================
        // 上側ステータス
        //
        // 上側にはタイトルだけ表示する。
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
        // 処理ログ用DOM作成
        //
        // 処理中はdownloadAreaへ直接表示。
        // 正常終了時に処理詳細の中へ移動する。
        // =====================================

        function ensureProcessingLogArea() {

            if (!downloadArea) {

                return null;

            }


            let logArea =
                downloadArea.querySelector(
                    ".conversion-log"
                );


            if (logArea) {

                return logArea;

            }


            const details =
                document.createElement(
                    "details"
                );


            details.className =
                "conversion-log";


            details.open =
                true;


            const summary =
                document.createElement(
                    "summary"
                );


            summary.className =
                "conversion-log-summary";


            summary.textContent =
                "処理ログ";


            details.appendChild(
                summary
            );


            const body =
                document.createElement(
                    "div"
                );


            body.className =
                "conversion-log-body";


            details.appendChild(
                body
            );


            // ---------------------------------
            // 処理中は先頭に表示
            // ---------------------------------

            downloadArea.prepend(
                details
            );


            return details;

        }


        // =====================================
        // 処理ログ追加
        // =====================================

        function addProcessingLog(
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


            const now =
                new Date();


            const clock =
                formatClock(
                    now
                );


            const lastIndex =
                converterState.processingLog.length - 1;


            const last =
                lastIndex >= 0
                    ? converterState.processingLog[
                        lastIndex
                    ]
                    : null;


            // ---------------------------------
            // 同じメッセージの連続追加を防止
            // ---------------------------------

            if (
                last &&
                last.message === text
            ) {

                return;

            }


            const entry = {

                time:
                    clock,

                message:
                    text,

                type:
                    type || "normal"

            };


            converterState.processingLog.push(
                entry
            );


            const details =
                ensureProcessingLogArea();


            if (!details) {

                console.log(
                    "[CONVERTER] LOG:",
                    clock,
                    text
                );

                return;

            }


            const body =
                details.querySelector(
                    ".conversion-log-body"
                );


            if (!body) {

                return;

            }


            const line =
                document.createElement(
                    "div"
                );


            line.className =
                "conversion-log-line";


            if (
                entry.type === "error"
            ) {

                line.classList.add(
                    "is-error"
                );

            }
            else if (
                entry.type === "success"
            ) {

                line.classList.add(
                    "is-success"
                );

            }


            const timeSpan =
                document.createElement(
                    "span"
                );


            timeSpan.className =
                "conversion-log-time";


            timeSpan.textContent =
                clock;


            const messageSpan =
                document.createElement(
                    "span"
                );


            messageSpan.className =
                "conversion-log-message";


            messageSpan.textContent =
                text;


            line.appendChild(
                timeSpan
            );


            line.appendChild(
                messageSpan
            );


            body.appendChild(
                line
            );


            body.scrollTop =
                body.scrollHeight;


            console.log(
                "[CONVERTER] LOG:",
                clock,
                text
            );

        }


        // =====================================
        // 処理ログクリア
        // =====================================

        function clearProcessingLog() {

            converterState.processingLog =
                [];


            converterState.lastJobMessage =
                "";


            converterState.lastJobStatus =
                "";


            if (!downloadArea) {

                return;

            }


            const logArea =
                downloadArea.querySelector(
                    ".conversion-log"
                );


            if (logArea) {

                logArea.remove();

            }

        }


        // =====================================
        // 処理ログを処理詳細へ移動
        //
        // 正常終了時に使用する。
        // =====================================

        function moveProcessingLogIntoDetails(
            details,
            detailBody
        ) {

            if (
                !details ||
                !detailBody
            ) {

                return;

            }


            const logArea =
                downloadArea
                    ? downloadArea.querySelector(
                        ".conversion-log"
                    )
                    : null;


            if (!logArea) {

                return;

            }


            // ---------------------------------
            // ログを処理詳細の中へ移動
            // ---------------------------------

            detailBody.appendChild(
                logArea
            );


            // ---------------------------------
            // 正常終了後はログを閉じた状態
            // ---------------------------------

            logArea.open =
                false;

        }


        // =====================================
        // Jobメッセージをログへ追加
        // =====================================

        function addJobMessageToLog(
            job
        ) {

            if (!job) {

                return;

            }


            const message =
                String(
                    job.message || ""
                ).trim();


            const status =
                String(
                    job.status || ""
                ).trim();


            // ---------------------------------
            // statusが変化した場合
            // ---------------------------------

            if (
                status &&
                status !==
                    converterState.lastJobStatus
            ) {

                converterState.lastJobStatus =
                    status;


                if (
                    status === "processing"
                ) {

                    addProcessingLog(
                        "変換処理を開始しました。"
                    );

                }
                else if (
                    status === "complete"
                ) {

                    addProcessingLog(
                        "変換処理が完了しました。",
                        "success"
                    );

                }
                else if (
                    status === "error"
                ) {

                    addProcessingLog(
                        "変換処理でエラーが発生しました。",
                        "error"
                    );

                }

            }


            // ---------------------------------
            // messageが変化した場合
            // ---------------------------------

            if (
                message &&
                message !==
                    converterState.lastJobMessage
            ) {

                converterState.lastJobMessage =
                    message;


                addProcessingLog(
                    message
                );

            }

        }


        // =====================================
        // 処理中ステータス
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


            addProcessingLog(
                text
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
                            "subtitle_mp4"
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
        // 通常ダウンロードリンク作成
        // =====================================

        function createDownloadLink(
            filename,
            label,
            className
        ) {

            const link =
                document.createElement(
                    "a"
                );


            link.href =
                makeDownloadUrl(
                    filename
                );


            link.download =
                String(filename);


            link.className =
                className ||
                "download-button";


            link.dataset.filename =
                String(filename);


            link.textContent =
                label;


            return link;

        }


        // =====================================
        // ダウンロード行取得
        // =====================================

        function ensureDownloadRow() {

            if (!downloadArea) {

                return null;

            }


            let row =
                downloadArea.querySelector(
                    ".download-row"
                );


            if (!row) {

                row =
                    document.createElement(
                        "div"
                    );


                row.className =
                    "download-row";


                downloadArea.appendChild(
                    row
                );

            }


            return row;

        }


        // =====================================
        // 既存ボタン検索
        // =====================================

        function hasDownloadButton(
            attributeName,
            filename
        ) {

            if (!downloadArea || !filename) {

                return false;

            }


            const safeFilename =
                String(
                    filename
                );


            const buttons =
                downloadArea.querySelectorAll(
                    ".download-row > *"
                );


            for (
                const button of buttons
            ) {

                if (
                    button.dataset &&
                    button.dataset[
                        attributeName
                    ] === safeFilename
                ) {

                    return true;

                }

            }


            return false;

        }


        // =====================================
        // ダウンロードボタン並び替え
        // =====================================

        function sortDownloadButtons() {

            if (!downloadArea) {

                return;

            }


            const row =
                downloadArea.querySelector(
                    ".download-row"
                );


            if (!row) {

                return;

            }


            const buttons =
                Array.from(
                    row.children
                );


            buttons.sort(
                function (a, b) {

                    const aOrder =
                        Number(
                            a.dataset.downloadOrder ||
                            999
                        );


                    const bOrder =
                        Number(
                            b.dataset.downloadOrder ||
                            999
                        );


                    return (
                        aOrder -
                        bOrder
                    );

                }
            );


            buttons.forEach(
                function (button) {

                    row.appendChild(
                        button
                    );

                }
            );

        }


        // =====================================
        // MP3ダウンロード
        //
        // 閉じた状態:
        //
        //     [MP3]ボタン ▲
        //
        // 展開:
        //
        //     [MP3] ▼
        //     [Geminiへ(字幕srt)]ボタン
        //
        // =====================================
        
        function addMp3Download(
            filename
        ) {
        
            if (!downloadArea || !filename) {
        
                return;
        
            }
        
        
            const safeFilename =
                String(
                    filename
                );
        
        
            if (
                hasDownloadButton(
                    "mp3Filename",
                    safeFilename
                )
            ) {
        
                return;
        
            }
        
        
            const row =
                ensureDownloadRow();
        
        
            if (!row) {
        
                return;
        
            }
        
        
            // =====================================
            // details
            // =====================================
        
            const details =
                document.createElement(
                    "details"
                );
        
        
            details.className =
                "download-details";
        
        
            details.dataset.mp3Filename =
                safeFilename;
        
        
            details.dataset.downloadOrder =
                "2";
        
        
            // =====================================
            // summary
            //
            // [MP3]ボタン ▲
            // =====================================
        
            const summary =
                document.createElement(
                    "summary"
                );
        
        
            summary.className =
                "download-summary";
        
        
            // =====================================
            // MP3ダウンロードボタン
            // =====================================
        
            const mp3Button =
                createDownloadLink(
                    safeFilename,
                    "[MP3]",
                    "download-button"
                );
        
        
            mp3Button.dataset.mp3Filename =
                safeFilename;
        
        
            // -------------------------------------
            // MP3ボタンを押したときは
            // detailsの開閉を発生させない
            // -------------------------------------
        
            mp3Button.addEventListener(
                "click",
                function (event) {
        
                    event.stopPropagation();
        
                }
            );
        
        
            summary.appendChild(
                mp3Button
            );
        
        
            // =====================================
            // ▲ / ▼
            // =====================================
        
            const arrow =
                document.createElement(
                    "span"
                );
        
        
            arrow.className =
                "download-arrow";
        
        
            arrow.textContent =
                "▲";
        
        
            summary.appendChild(
                arrow
            );
        
        
            details.appendChild(
                summary
            );
        
        
            // =====================================
            // 展開部分
            //
            // Geminiだけ表示
            // =====================================
        
            const body =
                document.createElement(
                    "div"
                );
        
        
            body.className =
                "download-details-body";
        
        
            const geminiButton =
                document.createElement(
                    "button"
                );
        
        
            geminiButton.type =
                "button";
        
        
            geminiButton.className =
                "gemini-srt-button";
        
        
            geminiButton.textContent =
                "Geminiへ(字幕srt)";
        
        
            geminiButton.dataset.mp3Filename =
                safeFilename;
        
        
            body.appendChild(
                geminiButton
            );
        
        
            details.appendChild(
                body
            );
        
        
            // =====================================
            // 開閉
            // =====================================
        
            details.addEventListener(
                "toggle",
                function () {
        
                    if (details.open) {
        
                        arrow.textContent =
                            "▼";
        
                    }
                    else {
        
                        arrow.textContent =
                            "▲";
        
                    }
        
                }
            );
        
        
            // =====================================
            // Gemini
            // =====================================
        
            geminiButton.addEventListener(
                "click",
                function () {
        
                    createSrtFromMp3(
                        safeFilename,
                        details,
                        geminiButton
                    );
        
                }
            );
        
        
            // =====================================
            // 追加
            // =====================================
        
            row.appendChild(
                details
            );
        
        
            sortDownloadButtons();
        
        
            console.log(
                "[CONVERTER] MP3ダウンロード追加:",
                safeFilename
            );
        
        }



        // =====================================
        // MP4ダウンロード
        // =====================================

        function addMp4Download(
            filename
        ) {

            if (!downloadArea || !filename) {

                return;

            }


            const safeFilename =
                String(
                    filename
                );


            if (
                hasDownloadButton(
                    "mp4Filename",
                    safeFilename
                )
            ) {

                return;

            }


            const row =
                ensureDownloadRow();


            if (!row) {

                return;

            }


            const link =
                createDownloadLink(
                    safeFilename,
                    "[MP4]",
                    "download-button"
                );


            link.dataset.mp4Filename =
                safeFilename;


            link.dataset.downloadOrder =
                "3";


            row.appendChild(
                link
            );


            sortDownloadButtons();


            console.log(
                "[CONVERTER] MP4ダウンロード追加:",
                safeFilename
            );

        }


        // =====================================
        // 字幕MP4ダウンロード
        // =====================================

        function addSubtitleMp4Download(
            filename
        ) {

            if (!downloadArea || !filename) {

                return;

            }


            const safeFilename =
                String(
                    filename
                );


            if (
                hasDownloadButton(
                    "subtitleMp4Filename",
                    safeFilename
                )
            ) {

                return;

            }


            const row =
                ensureDownloadRow();


            if (!row) {

                return;

            }


            const link =
                createDownloadLink(
                    safeFilename,
                    "[字幕MP4]",
                    "download-button"
                );


            link.dataset.subtitleMp4Filename =
                safeFilename;


            link.dataset.downloadOrder =
                "1";


            row.appendChild(
                link
            );


            sortDownloadButtons();


            console.log(
                "[CONVERTER] 字幕MP4ダウンロード追加:",
                safeFilename
            );

        }


        // =====================================
        // SRTダウンロード
        // =====================================

        function addSrtDownload(
            filename
        ) {

            if (!downloadArea || !filename) {

                return;

            }


            const safeFilename =
                String(
                    filename
                );


            if (
                hasDownloadButton(
                    "srtFilename",
                    safeFilename
                )
            ) {

                return;

            }


            const row =
                ensureDownloadRow();


            if (!row) {

                return;

            }


            const link =
                createDownloadLink(
                    safeFilename,
                    "[SRT]",
                    "download-button"
                );


            link.dataset.srtFilename =
                safeFilename;


            link.dataset.downloadOrder =
                "4";


            row.appendChild(
                link
            );


            sortDownloadButtons();


            console.log(
                "[CONVERTER] SRTダウンロード追加:",
                safeFilename
            );

        }


        // =====================================
        // MP3 → SRT作成
        // =====================================

        async function createSrtFromMp3(
            mp3Filename,
            details,
            button
        ) {

            if (
                converterState.isSrtProcessing
            ) {

                return;

            }


            if (!mp3Filename || !button) {

                return;

            }


            converterState.isSrtProcessing =
                true;


            button.disabled =
                true;


            const originalText =
                button.textContent;


            button.textContent =
                "SRT作成中...";


            try {

                addProcessingLog(
                    "Geminiへ字幕SRTの作成を開始します。"
                );


                setProgress(
                    "Geminiへ字幕SRTを作成しています..."
                );


                const response =
                    await fetch(
                        "/create-srt",
                        {

                            method:
                                "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify({

                                    filename:
                                        mp3Filename

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
                        "SRT作成に失敗しました。"

                    );

                }


                // =================================
                // SRTが即時返却された場合
                // =================================

                if (
                    data.filename
                ) {

                    converterState.currentSrtFile =
                        data.filename;


                    addSrtDownload(
                        data.filename
                    );


                    button.remove();


                    addProcessingLog(
                        "SRT作成が完了しました。",
                        "success"
                    );


                    setStatus(
                        converterState.currentVideoTitle,
                        "success"
                    );


                    console.log(
                        "[CONVERTER] SRT作成完了:",
                        data.filename
                    );


                    return;

                }


                // =================================
                // job_id方式
                // =================================

                if (
                    data.job_id
                ) {

                    converterState.currentSrtJobId =
                        data.job_id;


                    addProcessingLog(
                        "SRT作成ジョブを開始しました。"
                    );


                    const srtJob =
                        await waitForSrtJob(
                            data.job_id
                        );


                    const srtFile =
                        getSrtFilenameFromJob(
                            srtJob
                        );


                    if (!srtFile) {

                        throw new Error(
                            "SRT作成は完了しましたが、SRTファイルが確認できませんでした。"
                        );

                    }


                    converterState.currentSrtFile =
                        srtFile;


                    addSrtDownload(
                        srtFile
                    );


                    button.remove();


                    addProcessingLog(
                        "SRT作成が完了しました。",
                        "success"
                    );


                    setStatus(
                        converterState.currentVideoTitle,
                        "success"
                    );


                    console.log(
                        "[CONVERTER] SRT作成完了:",
                        srtJob
                    );


                    return;

                }


                throw new Error(
                    "SRT作成APIからfilenameまたはjob_idが返されませんでした。"
                );

            }
            catch (error) {

                console.error(
                    "[CONVERTER] SRT作成エラー:",
                    error
                );


                const message =
                    error &&
                    error.message
                        ? error.message
                        : "不明なエラー";


                addProcessingLog(
                    "SRT作成中にエラーが発生しました: " +
                    message,
                    "error"
                );


                setStatus(

                    "SRT作成中にエラーが発生しました。\n" +
                    message,

                    "error"

                );


                button.disabled =
                    false;


                button.textContent =
                    originalText;

            }
            finally {

                converterState.isSrtProcessing =
                    false;

            }

        }


        // =====================================
        // SRT Jobステータス
        // =====================================

        async function getSrtJobStatus(
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
                    "SRTジョブステータス取得に失敗しました。"

                );

            }


            return data;

        }


        // =====================================
        // SRT Job監視
        // =====================================

        async function waitForSrtJob(
            jobId
        ) {

            const maxWaitMs =
                30 * 60 * 1000;


            const intervalMs =
                2000;


            const startedAt =
                Date.now();


            let lastMessage =
                "";


            while (
                Date.now() -
                startedAt <
                maxWaitMs
            ) {

                const job =
                    await getSrtJobStatus(
                        jobId
                    );


                converterState.currentSrtJobStatus =
                    job.status || "";


                if (
                    job.message &&
                    job.message !== lastMessage
                ) {

                    lastMessage =
                        job.message;


                    addProcessingLog(
                        job.message
                    );

                }


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
                        "SRT作成中にエラーが発生しました。"

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
                "SRT作成処理がタイムアウトしました。"
            );

        }


        // =====================================
        // SRTファイル名取得
        // =====================================

        function getSrtFilenameFromJob(
            job
        ) {

            if (!job) {

                return "";

            }


            if (
                job.filename
            ) {

                return String(
                    job.filename
                );

            }


            if (
                job.srt_filename
            ) {

                return String(
                    job.srt_filename
                );

            }


            if (
                job.file &&
                job.file.filename
            ) {

                return String(
                    job.file.filename
                );

            }


            if (
                job.files &&
                job.files.srt &&
                job.files.srt.filename
            ) {

                return String(
                    job.files.srt.filename
                );

            }


            return "";

        }


        // =====================================
        // 結果クリア
        // =====================================

        function clearResults() {

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }


            if (conversionStatusArea) {

                conversionStatusArea.textContent =
                    "";


                conversionStatusArea.style.display =
                    "none";


                conversionStatusArea.style.color =
                    "#222";

            }


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


            converterState.currentSubtitleMp4File =
                "";


            converterState.currentJobId =
                "";


            converterState.currentJobStatus =
                "";


            converterState.currentJob =
                null;


            converterState.currentSrtJobId =
                "";


            converterState.currentSrtJobStatus =
                "";


            converterState.processingLog =
                [];


            converterState.lastJobMessage =
                "";


            converterState.lastJobStatus =
                "";

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


            console.log(
                "[CONVERTER] /convert request:",
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
        // Job内ファイルを表示
        // =====================================

        function renderJobFiles(
            job
        ) {

            if (!job) {

                return;

            }


            const files =
                job.files || {};


            // ---------------------------------
            // MP3
            // ---------------------------------

            if (
                files.mp3 &&
                files.mp3.status ===
                    "complete" &&
                files.mp3.filename
            ) {

                converterState.currentMp3File =
                    files.mp3.filename;


                addMp3Download(
                    files.mp3.filename
                );

            }


            // ---------------------------------
            // MP4
            // ---------------------------------

            if (
                files.mp4 &&
                files.mp4.status ===
                    "complete" &&
                files.mp4.filename
            ) {

                converterState.currentMp4File =
                    files.mp4.filename;


                addMp4Download(
                    files.mp4.filename
                );

            }


            // ---------------------------------
            // SRT
            // ---------------------------------

            if (
                files.srt &&
                files.srt.status ===
                    "complete" &&
                files.srt.filename
            ) {

                converterState.currentSrtFile =
                    files.srt.filename;


                addSrtDownload(
                    files.srt.filename
                );

            }


            // ---------------------------------
            // 字幕MP4
            // ---------------------------------

            if (
                files.subtitle_mp4 &&
                files.subtitle_mp4.status ===
                    "complete" &&
                files.subtitle_mp4.filename
            ) {

                converterState.currentSubtitleMp4File =
                    files.subtitle_mp4.filename;


                addSubtitleMp4Download(
                    files.subtitle_mp4.filename
                );

            }

        }


        // =====================================
        // Jobステータス処理
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


            addJobMessageToLog(
                job
            );


            renderJobFiles(
                job
            );


            // ---------------------------------
            // Jobエラー
            // ---------------------------------

            if (
                job.status ===
                "error"
            ) {

                if (
                    job.message
                ) {

                    addProcessingLog(
                        job.message,
                        "error"
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
        // 処理詳細
        //
        // 正常終了時に処理ログをここへ移動する。
        // =====================================

        function addConversionInfo(
            startTime,
            endTime
        ) {

            if (!downloadArea) {

                return;

            }


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


            const details =
                document.createElement(
                    "details"
                );


            details.className =
                "conversion-details";


            // ---------------------------------
            // 正常終了後は閉じた状態
            // ---------------------------------

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


            const detailBody =
                document.createElement(
                    "div"
                );


            detailBody.className =
                "conversion-details-body";


            detailBody.innerHTML = `

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
                        formatElapsed(
                            elapsed
                        )
                    )}
                </div>

            `;


            details.appendChild(
                detailBody
            );


            downloadArea.appendChild(
                details
            );


            // ---------------------------------
            // ここで処理中に表示していた
            // 処理ログを処理詳細の中へ移動
            // ---------------------------------

            moveProcessingLogIntoDetails(
                details,
                detailBody
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


            // =================================
            // subtitle_mp4単独選択も許可
            // =================================

            if (!outputs.length) {

                setStatus(
                    "MP3、MP4、または字幕MP4を選択してください。",
                    "error"
                );


                return;

            }


            converterState.isProcessing =
                true;


            clearResults();


            converterState.currentVideoUrl =
                url;


            convertButton.disabled =
                true;


            const startTime =
                new Date();


            try {

                // =================================
                // ログ開始
                // =================================

                addProcessingLog(
                    "変換処理を開始します。"
                );


                // =================================
                // 動画情報
                // =================================

                setProgress(
                    "動画情報を取得しています..."
                );


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
                // 変換開始
                // =================================

                setProgress(
                    "変換ジョブを開始しています..."
                );


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


                const completedJob =
                    await waitForJob(
                        jobId
                    );


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
                    files.mp3.status === "complete" &&
                    files.mp3.filename
                ) {
                
                    converterState.currentMp3File =
                        files.mp3.filename;
                
                    addMp3Download(
                        files.mp3.filename
                    );
                
                }
                
                
                // =================================
                // MP4
                // =================================
                
                if (
                    files.mp4 &&
                    files.mp4.status === "complete" &&
                    files.mp4.filename
                ) {
                
                    converterState.currentMp4File =
                        files.mp4.filename;
                
                    addMp4Download(
                        files.mp4.filename
                    );
                
                }
                
                
                // =================================
                // SRT
                // =================================
                
                if (
                    files.srt &&
                    files.srt.status === "complete" &&
                    files.srt.filename
                ) {
                
                    converterState.currentSrtFile =
                        files.srt.filename;
                
                    addSrtDownload(
                        files.srt.filename
                    );
                
                }
                
                
                // =================================
                // 字幕MP4
                // =================================
                
                if (
                    files.subtitle_mp4 &&
                    files.subtitle_mp4.status === "complete" &&
                    files.subtitle_mp4.filename
                ) {
                
                    converterState.currentSubtitleMp4File =
                        files.subtitle_mp4.filename;
                
                    addSubtitleMp4Download(
                        files.subtitle_mp4.filename
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
                
                const hasSrt =
                    Boolean(
                        converterState.currentSrtFile
                    );
                
                const hasSubtitleMp4 =
                    Boolean(
                        converterState.currentSubtitleMp4File
                    );
                
                
                if (
                    !hasMp3 &&
                    !hasMp4 &&
                    !hasSrt &&
                    !hasSubtitleMp4
                ) {
                
                    throw new Error(
                        "変換は完了しましたが、作成されたファイルが確認できませんでした。"
                    );
                
                }

                // =================================
                // 完了
                // =================================

                const endTime =
                    new Date();


                addConversionInfo(
                    startTime,
                    endTime
                );


                // =================================
                // 上側はタイトルだけ
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


                const message =
                    error &&
                    error.message
                        ? error.message
                        : "不明なエラー";


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
