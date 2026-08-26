// =====================================
// YouTube Converter
// converter.js
//
// メイン処理
//
// ・DOM初期化
// ・時間入力
// ・出力形式
// ・変換開始
// ・変換結果表示
// ・MP3 / MP4 ダウンロード表示
// ・字幕mp4処理結果表示
// ・MP3のGemini手動展開ボタン
// ・処理詳細表示
// ・HTML上の処理ステータス表示
//
// 別ファイル
// ・converter-utils.js
// ・converter-status.js
// ・converter-gemini.js
// ・sub_embed.js
//
// =====================================
//
// 【重要な仕様】
//
// mp3
//   ↓
//   YouTubeからMP3を作成
//   ↓
//   MP3ダウンロードボタン
//   ↓
//   MP3ボタン横に ▲
//   ↓
//   折り畳み状態
//   ↓
//   開くと「Geminiで文字起こし」
//
//
// mp4
//   ↓
//   YouTubeからMP4を作成
//   ↓
//   MP4ダウンロードボタンのみ
//
//
// 字幕mp4
//   ↓
//   MP3作成
//   ↓
//   MP4作成
//   ↓
//   MP3をGeminiへ自動送信
//   ↓
//   SRT作成
//   ↓
//   SRTダウンロードボタン
//   ↓
//   MP4 + SRTから字幕付きMP4作成
//   ↓
//   暖色系の「字幕付きMP4」ダウンロードボタン
//
// =====================================


document.addEventListener(
    "DOMContentLoaded",
    function () {


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


        const downloadArea =
            document.getElementById(
                "downloadArea"
            );



        // =====================================
        // JOB
        // =====================================

        let currentJobId =
            null;



        // =====================================
        // 変換時間
        // =====================================

        let convertSeconds =
            0;


        let convertTimer =
            null;


        let convertStartTime =
            null;


        let convertEndTime =
            null;



        // =====================================
        // 動画情報
        // =====================================

        let currentVideoTitle =
            "";


        let currentVideoDuration =
            "";



        // =====================================
        // ファイル
        // =====================================

        let currentMp3File =
            "";


        let currentMp4File =
            "";


        let currentSrtFile =
            "";


        let currentSubEmbedFile =
            "";



        // =====================================
        // HTML処理ステータス
        // =====================================

        let currentProcessingStage =
            "";


        let currentProcessingMessage =
            "";



        // =====================================
        // ステータスHTMLを作成
        // =====================================

        function createProcessingStatusArea() {


            let area =
                document.getElementById(
                    "converter-processing-status"
                );


            if (area) {

                return area;

            }



            area =
                document.createElement(
                    "div"
                );


            area.id =
                "converter-processing-status";


            area.className =
                "converter-processing-status";



            area.innerHTML = `

                <div class="converter-processing-title-area">

                    <div
                        id="converter-processing-video-title"
                        class="converter-processing-video-title"
                    ></div>

                </div>


                <div
                    class="converter-processing-status-inner"
                >

                    <div
                        id="converter-processing-icon"
                        class="converter-processing-icon"
                    >
                        ⏳
                    </div>


                    <div
                        class="converter-processing-text"
                    >

                        <div
                            id="converter-processing-title"
                            class="converter-processing-title"
                        >
                            処理中
                        </div>


                        <div
                            id="converter-processing-message"
                            class="converter-processing-message"
                        >
                            準備しています...
                        </div>

                    </div>

                </div>

            `;



            // ---------------------------------
            // downloadAreaの直前へ配置
            // ---------------------------------

            if (downloadArea) {

                downloadArea.parentNode.insertBefore(
                    area,
                    downloadArea
                );

            }
            else if (convertButton) {

                convertButton.parentNode.insertBefore(
                    area,
                    convertButton.nextSibling
                );

            }
            else {

                document.body.appendChild(
                    area
                );

            }



            // ---------------------------------
            // CSS
            // ---------------------------------

            if (
                !document.getElementById(
                    "converter-processing-status-style"
                )
            ) {


                const style =
                    document.createElement(
                        "style"
                    );


                style.id =
                    "converter-processing-status-style";


                style.textContent = `

                    #converter-processing-status {

                        width: 100%;

                        box-sizing: border-box;

                        margin: 15px 0;

                        padding: 12px 15px;

                        border-radius: 8px;

                        background: #f5f7fa;

                        border: 1px solid #d9dee7;

                        color: #333;

                    }


                    .converter-processing-title-area {

                        width: 100%;

                        box-sizing: border-box;

                        margin-bottom: 10px;

                    }


                    .converter-processing-video-title {

                        font-size: 16px;

                        font-weight: bold;

                        line-height: 1.5;

                        color: #222;

                        word-break: break-word;

                    }


                    .converter-processing-status-inner {

                        display: flex;

                        align-items: center;

                        gap: 12px;

                    }


                    .converter-processing-icon {

                        width: 32px;

                        min-width: 32px;

                        height: 32px;

                        display: flex;

                        align-items: center;

                        justify-content: center;

                        font-size: 20px;

                    }


                    .converter-processing-text {

                        min-width: 0;

                        flex: 1;

                    }


                    .converter-processing-title {

                        font-weight: bold;

                        font-size: 15px;

                        margin-bottom: 3px;

                    }


                    .converter-processing-message {

                        font-size: 14px;

                        color: #666;

                        word-break: break-word;

                    }


                    #converter-processing-status.processing {

                        background: #f5f9ff;

                        border-color: #b9d4f5;

                    }


                    #converter-processing-status.success {

                        background: #f1faf3;

                        border-color: #a8ddb2;

                    }


                    #converter-processing-status.error {

                        background: #fff4f4;

                        border-color: #e6aaaa;

                    }


                    #converter-processing-status.retry {

                        background: #fffaf0;

                        border-color: #efd18b;

                    }

                `;


                document.head.appendChild(
                    style
                );

            }



            return area;

        }



        // =====================================
        // HTML処理ステータス表示
        // =====================================

        function updateProcessingStatus(
            stage,
            message,
            options
        ) {


            options =
                options || {};


            currentProcessingStage =
                stage || "";


            currentProcessingMessage =
                message || "";


            const area =
                createProcessingStatusArea();


            const icon =
                document.getElementById(
                    "converter-processing-icon"
                );


            const videoTitle =
                document.getElementById(
                    "converter-processing-video-title"
                );


            const title =
                document.getElementById(
                    "converter-processing-title"
                );


            const messageElement =
                document.getElementById(
                    "converter-processing-message"
                );



            if (
                !area ||
                !icon ||
                !title ||
                !messageElement ||
                !videoTitle
            ) {

                return;

            }



            // ---------------------------------
            // 動画タイトル
            // ---------------------------------

            const statusVideoTitle =
                options.videoTitle ||
                currentVideoTitle ||
                "";


            videoTitle.textContent =
                statusVideoTitle;



            // ---------------------------------
            // 初期値
            // ---------------------------------

            let statusIcon =
                "⏳";


            let statusTitle =
                "処理中";


            let statusClass =
                "processing";



            switch (
                stage
            ) {


                case "convert":

                    statusIcon =
                        "⏳";

                    statusTitle =
                        "変換中";

                    statusClass =
                        "processing";

                    break;



                case "mp3":

                    statusIcon =
                        "🎵";

                    statusTitle =
                        "MP3を作成中";

                    statusClass =
                        "processing";

                    break;



                case "mp4":

                    statusIcon =
                        "🎬";

                    statusTitle =
                        "MP4を作成中";

                    statusClass =
                        "processing";

                    break;



                case "gemini":

                    statusIcon =
                        "🤖";

                    statusTitle =
                        "Gemini解析中";

                    statusClass =
                        "processing";

                    break;



                case "srt":

                    statusIcon =
                        "📝";

                    statusTitle =
                        "字幕ファイル作成中";

                    statusClass =
                        "processing";

                    break;



                case "subtitle":

                    statusIcon =
                        "🎬";

                    statusTitle =
                        "字幕付きMP4を作成中";

                    statusClass =
                        "processing";

                    break;



                case "retry":

                    statusIcon =
                        "🔄";

                    statusTitle =
                        "再試行中";

                    statusClass =
                        "retry";

                    break;



                case "success":

                    statusIcon =
                        "✅";

                    statusTitle =
                        "処理完了";

                    statusClass =
                        "success";

                    break;



                case "error":

                    statusIcon =
                        "❌";

                    statusTitle =
                        "エラー";

                    statusClass =
                        "error";

                    break;



                default:

                    statusIcon =
                        "⏳";

                    statusTitle =
                        "処理中";

                    statusClass =
                        "processing";

                    break;

            }



            icon.textContent =
                statusIcon;


            title.textContent =
                options.title ||
                statusTitle;


            messageElement.textContent =
                message ||
                "";


            area.classList.remove(
                "processing",
                "success",
                "error",
                "retry"
            );


            area.classList.add(
                statusClass
            );


            area.style.display =
                "block";

        }



        // =====================================
        // ステータス非表示
        // =====================================

        function hideProcessingStatus() {


            const area =
                document.getElementById(
                    "converter-processing-status"
                );


            if (area) {

                area.style.display =
                    "none";

            }

        }



        // =====================================
        // ステータス完了
        // =====================================

        function showProcessingSuccess(
            message
        ) {


            updateProcessingStatus(
                "success",
                message ||
                    "すべての処理が完了しました。"
            );

        }



        // =====================================
        // ステータスエラー
        // =====================================

        function showProcessingError(
            message
        ) {


            updateProcessingStatus(
                "error",
                message ||
                    "処理中にエラーが発生しました。"
            );

        }



        // =====================================
        // グローバル状態
        // =====================================

        window.converterState = {


            get currentJobId() {

                return currentJobId;

            },


            set currentJobId(value) {

                currentJobId =
                    value;

            },


            get convertSeconds() {

                return convertSeconds;

            },


            set convertSeconds(value) {

                convertSeconds =
                    value;

            },


            get convertStartTime() {

                return convertStartTime;

            },


            set convertStartTime(value) {

                convertStartTime =
                    value;

            },


            get convertEndTime() {

                return convertEndTime;

            },


            set convertEndTime(value) {

                convertEndTime =
                    value;

            },


            get currentVideoTitle() {

                return currentVideoTitle;

            },


            set currentVideoTitle(value) {

                currentVideoTitle =
                    value;

            },


            get currentVideoDuration() {

                return currentVideoDuration;

            },


            set currentVideoDuration(value) {

                currentVideoDuration =
                    value;

            },


            get currentMp3File() {

                return currentMp3File;

            },


            set currentMp3File(value) {

                currentMp3File =
                    value;

            },


            get currentMp4File() {

                return currentMp4File;

            },


            set currentMp4File(value) {

                currentMp4File =
                    value;

            },


            get currentSrtFile() {

                return currentSrtFile;

            },


            set currentSrtFile(value) {

                currentSrtFile =
                    value;

            },


            get currentSubEmbedFile() {

                return currentSubEmbedFile;

            },


            set currentSubEmbedFile(value) {

                currentSubEmbedFile =
                    value;

            }

        };



        // =====================================
        // 時間入力
        // =====================================

        const numericInputIds = [

            "start-hour",
            "start-minute",
            "start-second",
            "end-hour",
            "end-minute",
            "end-second"

        ];


        numericInputIds.forEach(
            function (id) {


                const element =
                    document.getElementById(
                        id
                    );


                if (
                    element &&
                    window.converterUtils &&
                    typeof
                        window.converterUtils.setupNumericInput ===
                    "function"
                ) {

                    window.converterUtils.setupNumericInput(
                        element
                    );

                }

            }
        );



        // =====================================
        // 変換時間表示
        // =====================================

        function showConvertingState() {


            if (!convertButton) {

                return;

            }


            convertButton.innerHTML = `

                <span class="converting-text">

                    <span>
                        変換中
                    </span>

                    <span>
                        ${convertSeconds}秒
                    </span>

                </span>

            `;

        }



        // =====================================
        // タイマー開始
        // =====================================

        function startConvertTimer() {


            convertSeconds =
                0;


            convertStartTime =
                new Date();


            convertEndTime =
                null;


            if (convertTimer) {

                clearInterval(
                    convertTimer
                );

            }


            showConvertingState();


            convertTimer =
                setInterval(
                    function () {


                        convertSeconds++;


                        showConvertingState();


                    },
                    1000
                );

        }



        // =====================================
        // タイマー停止
        // =====================================

        function stopConvertTimer() {


            if (convertTimer) {

                clearInterval(
                    convertTimer
                );


                convertTimer =
                    null;

            }


            if (convertStartTime) {

                convertEndTime =
                    new Date();

            }

        }



        // =====================================
        // 変換ボタン
        // =====================================

        if (convertButton) {

            convertButton.addEventListener(
                "click",
                startConvert
            );

        }



        // =====================================
        // Enter
        // =====================================

        if (urlInput) {

            urlInput.addEventListener(
                "keydown",
                function (event) {


                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();


                        startConvert();

                    }

                }
            );

        }



        // =====================================
        // 変換開始
        // =====================================

        async function startConvert() {


            // ---------------------------------
            // 二重実行防止
            // ---------------------------------

            if (
                convertButton &&
                convertButton.disabled
            ) {

                return;

            }



            // ---------------------------------
            // 選択出力
            // ---------------------------------

            const outputs =
                window.converterUtils.getSelectedOutputs();



            // ---------------------------------
            // URL
            // ---------------------------------

            const url =
                urlInput
                    ? urlInput.value.trim()
                    : "";



            // ---------------------------------
            // URLチェック
            // ---------------------------------

            if (!url) {

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }



            // ---------------------------------
            // 出力形式チェック
            // ---------------------------------

            if (
                !outputs ||
                outputs.length === 0
            ) {

                alert(
                    "出力形式を選択してください"
                );

                return;

            }



            // ---------------------------------
            // 時間範囲
            // ---------------------------------

            const timeRange =
                window.converterUtils.getTimeRange();



            console.log(
                "======================================"
            );


            console.log(
                "[CONVERT REQUEST]"
            );


            console.log(
                "URL:",
                url
            );


            console.log(
                "開始時間:",
                timeRange.start_time
            );


            console.log(
                "終了時間:",
                timeRange.end_time
            );


            console.log(
                "出力:",
                outputs
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



            // =================================
            // 初期化
            // =================================

            currentJobId =
                null;


            currentVideoTitle =
                "";


            currentVideoDuration =
                "";


            currentMp3File =
                "";


            currentMp4File =
                "";


            currentSrtFile =
                "";


            currentSubEmbedFile =
                "";



            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }



            // =================================
            // Geminiリセット
            // =================================

            if (
                window.converterGemini &&
                typeof
                    window.converterGemini.hideArea ===
                "function"
            ) {

                window.converterGemini.hideArea();

            }


            if (
                window.converterGemini &&
                typeof
                    window.converterGemini.resetButton ===
                "function"
            ) {

                window.converterGemini.resetButton();

            }



            // =================================
            // ステータス開始
            // =================================

            updateProcessingStatus(
                "convert",
                "変換処理を開始しています..."
            );



            // =================================
            // 実行ボタン
            // =================================

            if (convertButton) {

                convertButton.disabled =
                    true;

            }


            startConvertTimer();



            // =================================
            // /convert
            // =================================

            try {


                updateProcessingStatus(
                    "convert",
                    "サーバーへ変換処理を送信しています..."
                );


                const requestStartTime =
                    Date.now();


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



                console.log(
                    "[CONVERT] レスポンス受信",
                    {
                        status:
                            response.status,

                        elapsed:
                            (
                                Date.now() -
                                requestStartTime
                            ) +
                            "ms"
                    }
                );



                if (!response.ok) {


                    const text =
                        await response.text();


                    throw new Error(

                        "HTTP "
                        +
                        response.status
                        +
                        " : "
                        +
                        (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )

                    );

                }



                const text =
                    await response.text();


                if (!text) {

                    throw new Error(
                        "サーバーから空のレスポンスが返されました"
                    );

                }



                let data;


                try {

                    data =
                        JSON.parse(
                            text
                        );

                }
                catch (error) {


                    console.error(
                        "JSON解析エラー:",
                        error
                    );


                    console.error(
                        "レスポンス:",
                        text
                    );


                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }



                console.log(
                    "[CONVERT] JSON:",
                    data
                );



                // =================================
                // JOB開始
                // =================================

                if (!data.success) {

                    throw new Error(
                        data.message ||
                        "変換開始に失敗しました"
                    );

                }



                currentJobId =
                    data.job_id;


                currentVideoTitle =
                    data.title ||
                    data.video_title ||
                    "";


                currentVideoDuration =
                    data.duration ||
                    data.video_duration ||
                    "";



                let initialMessage =
                    "ファイルを作成しています...";


                if (
                    outputs.includes("subtitle_mp4") ||
                    outputs.includes("mp3mp4")
                ) {

                    initialMessage =
                        "字幕mp4を作成しています...";

                }
                else if (
                    outputs.includes("mp3")
                ) {

                    initialMessage =
                        "MP3を作成しています...";

                }
                else if (
                    outputs.includes("mp4")
                ) {

                    initialMessage =
                        "MP4を作成しています...";

                }



                updateProcessingStatus(
                    "convert",
                    initialMessage,
                    {

                        title:
                            "実行中・・・",

                        videoTitle:
                            currentVideoTitle

                    }
                );



                // =================================
                // STATUS開始
                // =================================

                if (
                    window.converterStatus &&
                    typeof
                        window.converterStatus.start ===
                    "function"
                ) {


                    window.converterStatus.start(
                        currentJobId
                    );

                }
                else {


                    console.error(
                        "converter-status.js が読み込まれていません"
                    );


                    showProcessingError(
                        "処理状態監視機能を読み込めませんでした。"
                    );


                    restoreConvertButton();

                }

            }
            catch (error) {


                stopConvertTimer();


                showProcessingError(
                    error.message
                );


                restoreConvertButton();


                console.error(
                    "変換開始エラー:",
                    error
                );


                alert(
                    error.message
                );

            }

        }



        // =====================================
        // Gemini展開ボタン
        // =====================================

        function setupGeminiExpandButton() {


            const expandButton =
                document.getElementById(
                    "gemini-expand-button"
                );


            const expandArea =
                document.getElementById(
                    "gemini-expand-area"
                );


            const transcribeButton =
                document.getElementById(
                    "gemini-transcribe-button"
                );



            if (
                !expandButton ||
                !expandArea
            ) {

                return;

            }



            // ---------------------------------
            // 初期状態
            // ---------------------------------

            expandArea.style.display =
                "none";


            expandButton.textContent =
                "▲";


            expandButton.setAttribute(
                "aria-expanded",
                "false"
            );



            // ---------------------------------
            // ▲クリック
            // ---------------------------------

            expandButton.addEventListener(
                "click",
                function () {


                    const isHidden =
                        expandArea.style.display ===
                        "none";



                    if (isHidden) {


                        expandArea.style.display =
                            "block";


                        expandButton.textContent =
                            "▼";


                        expandButton.setAttribute(
                            "aria-expanded",
                            "true"
                        );

                    }
                    else {


                        expandArea.style.display =
                            "none";


                        expandButton.textContent =
                            "▲";


                        expandButton.setAttribute(
                            "aria-expanded",
                            "false"
                        );

                    }

                }
            );



            // ---------------------------------
            // Gemini手動実行
            // ---------------------------------

            if (transcribeButton) {


                transcribeButton.addEventListener(
                    "click",
                    function () {


                        console.log(
                            "[GEMINI] 手動文字起こし開始"
                        );


                        updateProcessingStatus(
                            "gemini",
                            "Geminiで文字起こしを開始しています..."
                        );



                        if (
                            typeof window.startGemini ===
                            "function"
                        ) {


                            window.startGemini();

                        }
                        else {


                            showProcessingError(
                                "Gemini機能を読み込めませんでした。"
                            );


                            alert(
                                "Gemini機能を読み込めませんでした。"
                            );

                        }

                    }
                );

            }

        }



        // =====================================
        // 実行ボタンを通常状態へ戻す
        // =====================================

        function restoreConvertButton() {


            if (!convertButton) {

                return;

            }


            convertButton.style.display =
                "";


            convertButton.disabled =
                false;


            convertButton.innerHTML =
                "実行";

        }



        // =====================================
        // SRT処理情報追加
        // =====================================

        window.converterMain =
            window.converterMain ||
            {};


        window.converterMain.addSrtInfo =
            function (
                html,
                srtFile
            ) {


                const content =
                    document.getElementById(
                        "conversion-details-content"
                    );


                const srtInfo =
                    document.getElementById(
                        "srt-conversion-detail"
                    );



                if (
                    !content ||
                    !srtInfo
                ) {

                    console.error(
                        "[SRT] 処理詳細領域がありません"
                    );

                    return;

                }



                srtInfo.innerHTML =
                    html;


                srtInfo.style.display =
                    "block";


                currentSrtFile =
                    srtFile || "";



                const buttonContainer =
                    document.getElementById(
                        "srt-download-button-container"
                    );


                if (
                    buttonContainer &&
                    srtFile
                ) {


                    buttonContainer.innerHTML = `

                        <a
                            href="${window.converterUtils.makeDownloadUrl(srtFile)}"
                            download
                            class="download-button download-button-normal"
                            id="srt-download-button"
                        >
                            srt
                        </a>

                    `;

                }

            };



        // =====================================
        // 字幕付きMP4ダウンロードボタン
        // =====================================

        window.converterMain.addSubtitleEmbedFile =
            function (
                file
            ) {


                if (!file) {

                    console.error(
                        "[SUB EMBED] ファイル名がありません"
                    );

                    return;

                }



                currentSubEmbedFile =
                    file;



                const container =
                    document.getElementById(
                        "subtitle-embed-download-container"
                    );


                if (!container) {

                    console.error(
                        "[SUB EMBED] ダウンロード領域がありません"
                    );

                    return;

                }



                container.innerHTML = `

                    <a
                        href="/subtitle-download/${encodeURIComponent(file)}"
                        download
                        class="download-button download-button-subtitle"
                        id="subtitle-embed-download-button"
                    >
                        字幕付きMP4
                    </a>

                `;



                // ---------------------------------
                // 字幕付きMP4作成完了
                // ---------------------------------

                updateProcessingStatus(
                    "success",
                    "字幕付きMP4の作成が完了しました。"
                );

            };



        // =====================================
        // 字幕付きMP4情報
        // =====================================

        window.converterMain.addSubtitleEmbedInfo =
            function (
                html
            ) {


                const detail =
                    document.getElementById(
                        "subtitle-embed-conversion-detail"
                    );


                if (!detail) {

                    console.error(
                        "[SUB EMBED] 処理詳細領域がありません"
                    );

                    return;

                }


                detail.innerHTML =
                    html;


                detail.style.display =
                    "block";

            };



        // =====================================
        // 変換情報HTML
        // =====================================

        function createConversionInfo(
            type,
            data,
            durationOverride
        ) {


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
                    ? window.converterUtils.formatClock(
                        convertStartTime
                    )
                    : "";


            const end =
                convertEndTime
                    ? window.converterUtils.formatClock(
                        convertEndTime
                    )
                    : "";



            return `

                <div class="conversion-info">

                    <div class="conversion-info-title">

                        ★${window.converterUtils.escapeHtml(
                            type
                        )}変換

                    </div>


                    <div>

                        再生時間：
                        ${window.converterUtils.escapeHtml(
                            window.converterUtils.formatDuration(
                                duration
                            )
                        )}

                    </div>


                    <div>

                        実行開始：
                        ${window.converterUtils.escapeHtml(
                            start
                        )}

                    </div>


                    <div>

                        実行終了：
                        ${window.converterUtils.escapeHtml(
                            end
                        )}

                        （${window.converterUtils.escapeHtml(
                            window.converterUtils.formatElapsed(
                                convertSeconds
                            )
                        )}）

                    </div>

                </div>

            `;

        }



        // =====================================
        // 完成ファイル表示
        // =====================================

        function showFiles(
            files,
            data
        ) {


            stopConvertTimer();



            if (!downloadArea) {

                return;

            }



            let mp3File =
                "";


            let mp4File =
                "";



            // =================================
            // files解析
            // =================================

            if (
                Array.isArray(files)
            ) {


                files.forEach(
                    function (file) {


                        if (
                            typeof file !== "string" ||
                            !file
                        ) {

                            return;

                        }


                        const lower =
                            file.toLowerCase();



                        if (
                            lower.endsWith(".mp3")
                        ) {

                            mp3File =
                                file;

                        }


                        if (
                            lower.endsWith(".mp4")
                        ) {

                            mp4File =
                                file;

                        }

                    }
                );

            }



            // =================================
            // 保存
            // =================================

            currentMp3File =
                mp3File;


            currentMp4File =
                mp4File;


            currentSubEmbedFile =
                "";



            // =================================
            // ファイルなし
            // =================================

            if (
                !mp3File &&
                !mp4File
            ) {


                downloadArea.innerHTML = `

                    <div class="download-error">

                        変換されたファイルがありません。

                    </div>

                `;


                showProcessingError(
                    "変換されたファイルがありません。"
                );


                restoreConvertButton();


                return;

            }



            // =================================
            // Gemini対象MP3
            // =================================

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );


            if (geminiFile) {

                geminiFile.value =
                    mp3File || "";

            }



            // =================================
            // 動画タイトル
            // =================================

            const displayTitle =
                data.title ||
                data.video_title ||
                currentVideoTitle ||
                "不明";


            const titleHtml = `

                <div class="download-video-title">

                    ${window.converterUtils.escapeHtml(
                        displayTitle
                    )}

                </div>

            `;



            // =================================
            // ダウンロードUI
            // =================================

            let downloadHtml = `

                ${titleHtml}

                <div class="download-groups">

            `;



            // =================================
            // 字幕付きMP4
            //
            // 最初に配置
            // 暖色系背景
            // =================================

            const selectedOutputs =
                window.converterUtils.getSelectedOutputs();


            const isSubtitleMp4 =
                selectedOutputs.includes(
                    "subtitle_mp4"
                ) ||
                selectedOutputs.includes(
                    "mp3mp4"
                );



            if (isSubtitleMp4) {


                downloadHtml += `

                    <div
                        class="download-group download-group-subtitle"
                        id="subtitle-download-group"
                    >

                        <div class="download-group-buttons">

                            <span
                                id="subtitle-embed-download-container"
                            ></span>

                        </div>

                    </div>

                `;

            }



            // =================================
            // 通常ダウンロード
            // =================================

            downloadHtml += `

                    <div
                        class="download-group download-group-normal"
                    >

                        <div
                            class="download-group-buttons"
                        >

            `;



            // =================================
            // MP3
            // =================================

            if (mp3File) {


                downloadHtml += `

                            <div
                                class="mp3-download-wrapper"
                                id="mp3-download-wrapper"
                            >

                                <a
                                    href="${window.converterUtils.makeDownloadUrl(mp3File)}"
                                    download
                                    class="download-button download-button-normal"
                                    id="mp3-download-button"
                                >
                                    mp3
                                </a>


                                <button
                                    type="button"
                                    class="gemini-expand-button"
                                    id="gemini-expand-button"
                                    aria-expanded="false"
                                    title="Geminiで文字起こし"
                                >
                                    ▲
                                </button>

                            </div>


                            <div
                                class="gemini-expand-area"
                                id="gemini-expand-area"
                                style="display:none;"
                            >

                                <button
                                    type="button"
                                    class="gemini-transcribe-button"
                                    id="gemini-transcribe-button"
                                >
                                    Geminiで文字起こし
                                </button>

                            </div>

                `;

            }



            // =================================
            // MP4
            // =================================

            if (mp4File) {


                downloadHtml += `

                            <a
                                href="${window.converterUtils.makeDownloadUrl(mp4File)}"
                                download
                                class="download-button download-button-normal"
                                id="mp4-download-button"
                            >
                                mp4
                            </a>

                `;

            }



            // =================================
            // SRT
            // =================================

            if (isSubtitleMp4) {


                downloadHtml += `

                            <span
                                id="srt-download-button-container"
                            ></span>

                `;

            }



            downloadHtml += `

                        </div>

                    </div>

                </div>

            `;



            // =================================
            // 処理詳細
            // =================================

            let detailHtml =
                "";



            // ---------------------------------
            // MP3詳細
            // ---------------------------------

            if (mp3File) {


                detailHtml +=
                    createConversionInfo(
                        "MP3",
                        data || {}
                    );

            }



            // ---------------------------------
            // MP4詳細
            // ---------------------------------

            if (mp4File) {


                detailHtml +=
                    createConversionInfo(
                        "MP4",
                        data || {}
                    );

            }



            // ---------------------------------
            // SRT詳細
            // ---------------------------------

            if (isSubtitleMp4) {


                detailHtml += `

                    <div
                        id="srt-conversion-detail"
                        style="display:none;"
                    ></div>

                `;

            }



            // ---------------------------------
            // 字幕付きMP4詳細
            // ---------------------------------

            if (isSubtitleMp4) {


                detailHtml += `

                    <div
                        id="subtitle-embed-conversion-detail"
                        style="display:none;"
                    ></div>

                `;

            }



            // =================================
            // 最終HTML
            // =================================

            downloadArea.innerHTML = `

                <div class="conversion-summary">

                    ${downloadHtml}

                </div>


                <div class="conversion-details">

                    <button
                        type="button"
                        id="conversion-details-toggle"
                        class="conversion-details-toggle"
                        aria-expanded="false"
                    >
                        【処理詳細】 ▼
                    </button>


                    <div
                        id="conversion-details-content"
                        class="conversion-details-content"
                        style="display:none;"
                    >

                        ${detailHtml}

                    </div>

                </div>

            `;



            // =================================
            // Gemini展開ボタン
            //
            // MP3がある場合のみ
            // =================================

            if (mp3File) {

                setupGeminiExpandButton();

            }



            // =================================
            // 処理詳細 開閉
            // =================================

            const detailsToggle =
                document.getElementById(
                    "conversion-details-toggle"
                );


            const detailsContent =
                document.getElementById(
                    "conversion-details-content"
                );


            if (
                detailsToggle &&
                detailsContent
            ) {


                detailsToggle.addEventListener(
                    "click",
                    function () {


                        const isHidden =
                            detailsContent.style.display ===
                            "none";


                        if (isHidden) {


                            detailsContent.style.display =
                                "block";


                            detailsToggle.textContent =
                                "【処理詳細】 ▲";


                            detailsToggle.setAttribute(
                                "aria-expanded",
                                "true"
                            );

                        }
                        else {


                            detailsContent.style.display =
                                "none";


                            detailsToggle.textContent =
                                "【処理詳細】 ▼";


                            detailsToggle.setAttribute(
                                "aria-expanded",
                                "false"
                            );

                        }

                    }
                );

            }



            // =================================
            // 旧Gemini領域
            // =================================

            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            const srtContent =
                document.getElementById(
                    "srt-content"
                );


            if (srtArea) {

                srtArea.style.display =
                    "none";

            }


            if (srtContent) {

                srtContent.style.display =
                    "none";

            }



            // =================================
            // MP3なし
            //
            // MP4単独
            // =================================

            if (!mp3File) {


                if (
                    window.converterGemini &&
                    typeof
                        window.converterGemini.hideArea ===
                    "function"
                ) {

                    window.converterGemini.hideArea();

                }


                showProcessingSuccess(
                    "MP4の作成が完了しました。"
                );


                restoreConvertButton();


                return;

            }



            // =================================
            // GeminiへMP3を登録
            //
            // 自動実行はここではしない
            // =================================

            if (
                window.converterGemini &&
                typeof
                    window.converterGemini.setFile ===
                "function"
            ) {


                window.converterGemini.setFile(
                    mp3File
                );

            }



            // =================================
            // 重要
            //
            // MP3単独
            // → Gemini自動実行なし
            //
            // 字幕mp4
            // → Gemini自動実行
            // =================================

            if (
                isSubtitleMp4 &&
                mp3File &&
                mp4File &&
                typeof window.startGemini ===
                    "function"
            ) {


                console.log(
                    "[CONVERTER] 字幕mp4処理"
                );


                console.log(
                    "[CONVERTER] MP3:",
                    mp3File
                );


                console.log(
                    "[CONVERTER] MP4:",
                    mp4File
                );


                updateProcessingStatus(
                    "gemini",
                    "MP3をGeminiへ送信して字幕を作成しています...",
                    {
                        videoTitle:
                            currentVideoTitle
                    }
                );



                setTimeout(
                    function () {

                        window.startGemini();

                    },
                    0
                );

            }
            else {


                // ---------------------------------
                // MP3単独
                //
                // Geminiは手動のみ
                // ---------------------------------

                if (
                    mp3File &&
                    !mp4File
                ) {


                    showProcessingSuccess(
                        "MP3の作成が完了しました。Geminiは「▲」から手動で実行できます。"
                    );

                }

            }



            // =================================
            // 実行ボタン復帰
            // =================================

            restoreConvertButton();

        }



        // =====================================
        // converterMain
        // =====================================

        window.converterMain = {


            // ---------------------------------
            // タイマー停止
            // ---------------------------------

            stopTimer:
                stopConvertTimer,



            // ---------------------------------
            // ファイル表示
            // ---------------------------------

            showFiles:
                showFiles,



            // ---------------------------------
            // HTML処理ステータス
            // ---------------------------------

            updateProcessingStatus:
                updateProcessingStatus,


            showProcessingSuccess:
                showProcessingSuccess,


            showProcessingError:
                showProcessingError,


            hideProcessingStatus:
                hideProcessingStatus,



            // ---------------------------------
            // 状態取得
            // ---------------------------------

            getState:
                function () {


                    return {

                        jobId:
                            currentJobId,

                        videoTitle:
                            currentVideoTitle,

                        videoDuration:
                            currentVideoDuration,

                        mp3File:
                            currentMp3File,

                        mp4File:
                            currentMp4File,

                        srtFile:
                            currentSrtFile,

                        subEmbedFile:
                            currentSubEmbedFile,

                        convertSeconds:
                            convertSeconds,

                        convertStartTime:
                            convertStartTime,

                        convertEndTime:
                            convertEndTime,

                        processingStage:
                            currentProcessingStage,

                        processingMessage:
                            currentProcessingMessage

                    };

                }

        };



        // =====================================
        // ダウンロードUI CSS
        // =====================================

        if (
            !document.getElementById(
                "converter-download-layout-style"
            )
        ) {


            const style =
                document.createElement(
                    "style"
                );


            style.id =
                "converter-download-layout-style";


            style.textContent = `

                /* =================================
                   ダウンロードボタン全体
                   ================================= */

                .download-group-buttons {

                    display: flex;

                    flex-direction: row;

                    align-items: center;

                    flex-wrap: wrap;

                    gap: 8px;

                }



                /* =================================
                   MP3 + Gemini
                   ================================= */

                .mp3-download-wrapper {

                    display: flex;

                    flex-direction: row;

                    align-items: center;

                    gap: 4px;

                    flex: 0 0 auto;

                }



                /* =================================
                   通常ダウンロード
                   ================================= */

                .download-button {

                    display: inline-flex;

                    align-items: center;

                    justify-content: center;

                    white-space: nowrap;

                    flex: 0 0 auto;

                }



                /* =================================
                   Gemini展開
                   ================================= */

                .gemini-expand-area {

                    flex-basis: 100%;

                    width: 100%;

                }



                .gemini-transcribe-button {

                    margin-top: 4px;

                }



                /* =================================
                   SRT
                   ================================= */

                #srt-download-button-container {

                    display: inline-flex;

                    align-items: center;

                    flex: 0 0 auto;

                }



                /* =================================
                   字幕付きMP4
                   ================================= */

                .download-group-subtitle {

                    width: 100%;

                    box-sizing: border-box;

                    margin-bottom: 10px;

                    padding: 10px;

                    border-radius: 8px;

                    background:
                        #fff1e6;

                    border:
                        1px solid #e8b28a;

                }



                .download-group-subtitle
                .download-group-buttons {

                    display: flex;

                    flex-direction: row;

                    align-items: center;

                    flex-wrap: wrap;

                    gap: 8px;

                }



                #subtitle-embed-download-container {

                    display: inline-flex;

                    align-items: center;

                    flex: 0 0 auto;

                }



                /* =================================
                   字幕付きMP4ボタン
                   ================================= */

                .download-button-subtitle {

                    background:
                        #e8894a;

                    border-color:
                        #d87532;

                    color:
                        #fff;

                }



                .download-button-subtitle:hover {

                    background:
                        #d87532;

                }



                /* =================================
                   通常グループ
                   ================================= */

                .download-group-normal {

                    width: 100%;

                }



                .download-group-normal
                .download-group-buttons {

                    display: flex;

                    flex-direction: row;

                    align-items: center;

                    flex-wrap: wrap;

                    gap: 8px;

                    width: 100%;

                }

            `;


            document.head.appendChild(
                style
            );

        }



        // =====================================
        // 初期状態
        // =====================================

        console.log(
            "converter.js loaded"
        );


        console.log(
            "[CONVERTER] 新仕様:"
        );


        console.log(
            "MP3       = MP3 + Gemini手動"
        );


        console.log(
            "MP4       = MP4のみ"
        );


        console.log(
            "字幕mp4   = MP3 + MP4 + 自動Gemini + SRT + 字幕付きMP4"
        );

    }
);
