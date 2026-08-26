// =====================================
// YouTube Converter
// converter.js
//
// メイン処理
// ・DOM初期化
// ・時間入力
// ・出力形式
// ・変換開始
// ・変換結果表示
// ・MP3 / MP4 / SRT ダウンロード表示
// ・字幕付きMP4ダウンロード表示
// ・MP3のGemini展開ボタン
// ・処理詳細表示
//
// 別ファイル
// ・converter-utils.js
// ・converter-status.js
// ・converter-gemini.js
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
        // グローバル参照
        //
        // 他ファイルからも利用できるようにする
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


                console.log(
                    "[TIME INPUT]",
                    prefix,
                    {
                        hour: h,
                        minute: m,
                        second: s
                    }
                );


                if (
                    !h &&
                    !m &&
                    !s
                ) {

                    return "";

                }


                const result =
                    window.converterUtils.makeTime(
                        h,
                        m,
                        s
                    );


                console.log(
                    "[TIME VALUE]",
                    prefix,
                    "=>",
                    result
                );


                return result;

            }



            // ---------------------------------
            // 旧UI対応
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


            const startTime =
                getTimeValue(
                    "start"
                );


            const endTime =
                getTimeValue(
                    "end"
                );


            console.log(
                "[TIME RANGE INPUT]",
                {
                    startTime:
                        startTime,

                    endTime:
                        endTime
                }
            );



            // ---------------------------------
            // 開始だけ指定
            // ---------------------------------

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



            // ---------------------------------
            // 終了だけ指定
            // 「最初から～20秒」
            // ---------------------------------

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



            // ---------------------------------
            // 開始・終了とも指定
            // ---------------------------------

            return {

                start_time:
                    startTime,

                end_time:
                    endTime

            };

        }



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
        // 変換タイマー開始
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
        // 変換タイマー停止
        // =====================================

        function stopConvertTimer() {


            if (convertTimer) {

                clearInterval(
                    convertTimer
                );


                convertTimer =
                    null;

            }


            convertEndTime =
                new Date();

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



            return [
                "mp3"
            ];

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



            const outputs =
                getSelectedOutputs();


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
                getTimeRange();



            // =================================
            // ログ
            // =================================

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



            console.log(
                "送信JSON:",
                JSON.stringify(
                    requestBody
                )
            );


            console.log(
                "======================================"
            );



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


                console.log(
                    "[CONVERT] POST /convert 開始"
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



                // =================================
                // HTTPエラー
                // =================================

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



                // =================================
                // レスポンス
                // =================================

                const text =
                    await response.text();


                console.log(
                    "[CONVERT] レスポンス本文:",
                    text
                );


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

                if (data.success) {


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



                    console.log(
                        "変換JOB:",
                        currentJobId
                    );


                    console.log(
                        "[CONVERT] JOB情報:",
                        {

                            job_id:
                                currentJobId,

                            title:
                                currentVideoTitle,

                            duration:
                                currentVideoDuration,

                            start_time:
                                timeRange.start_time,

                            end_time:
                                timeRange.end_time,

                            outputs:
                                outputs

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


                        console.log(
                            "[STATUS] 監視開始:",
                            currentJobId
                        );


                        window.converterStatus.start(
                            currentJobId
                        );

                    }
                    else {


                        console.error(
                            "converter-status.js が読み込まれていません"
                        );


                        console.error(
                            "[STATUS] window.converterStatus:",
                            window.converterStatus
                        );

                    }

                }
                else {


                    throw new Error(
                        data.message ||
                        "変換開始に失敗しました"
                    );

                }

            }
            catch (error) {


                stopConvertTimer();


                if (convertButton) {

                    convertButton.disabled =
                        false;


                    convertButton.style.display =
                        "";


                    convertButton.innerHTML =
                        "実行";

                }


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
                            convertEndTime

                    };

                }

        };



        // =====================================
        // 完成ファイル表示
        // =====================================

        function showFiles(
            files,
            data
        ) {


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
                            lower.endsWith(
                                ".mp3"
                            )
                        ) {

                            mp3File =
                                file;

                        }



                        if (
                            lower.endsWith(
                                ".mp4"
                            )
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
            // ファイルがない
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
            //
            // ダウンロードボタンの上に
            // 1回だけ表示
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
            //
            // グループ構成
            //
            // 🟧 字幕付きMP4
            //
            // 🟦 MP3 / MP4 / SRT
            // =================================

            let downloadHtml = `

                ${titleHtml}

                <div class="download-groups">


                    <!-- =========================
                         字幕付きMP4グループ
                         ========================= -->

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


                    <!-- =========================
                         通常ファイルグループ
                         ========================= -->

                    <div
                        class="download-group download-group-normal"
                    >

                        <div class="download-group-buttons">

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
            //
            // Gemini完了後に追加
            // =================================

            downloadHtml += `

                            <span
                                id="srt-download-button-container"
                            ></span>

                        </div>

                    </div>

                </div>

            `;



            // =================================
            // SRT情報
            // =================================

            downloadHtml += `

                <div
                    id="srt-download-info-placeholder"
                ></div>


                <div
                    id="srt-conversion-info"
                    style="display:none;"
                ></div>


                <div
                    id="srt-download-area"
                ></div>

            `;



            // =================================
            // 処理詳細
            // =================================

            let detailHtml =
                "";



            // =================================
            // MP3詳細
            // =================================

            if (mp3File) {


                detailHtml +=
                    createConversionInfo(
                        "MP3",
                        data || {}
                    );

            }



            // =================================
            // MP4詳細
            // =================================

            if (mp4File) {


                detailHtml +=
                    createConversionInfo(
                        "MP4",
                        data || {}
                    );

            }



            // =================================
            // SRT詳細
            //
            // Gemini完了後に追加
            // =================================

            detailHtml += `

                <div
                    id="srt-conversion-detail"
                    style="display:none;"
                ></div>

            `;



            // =================================
            // 字幕付きMP4詳細
            // =================================

            detailHtml += `

                <div
                    id="subtitle-embed-conversion-detail"
                    style="display:none;"
                ></div>

            `;



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
            // =================================

            setupGeminiExpandButton();



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


                restoreConvertButton();


                return;

            }



            // =================================
            // Gemini状態
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



            // =====================================
            // Gemini自動実行
            //
            // MP3 + MP4 の場合だけ自動実行
            //
            // MP3単独では自動実行しない
            // MP3のGeminiは▲から手動実行
            // =====================================

            if (
                mp3File &&
                mp4File &&
                typeof window.startGemini ===
                    "function"
            ) {


                console.log(
                    "=========================================="
                );


                console.log(
                    "[CONVERTER] MP3 / MP4変換完了"
                );


                console.log(
                    "[CONVERTER] Gemini自動実行開始"
                );


                console.log(
                    "[CONVERTER] MP3:",
                    mp3File
                );


                console.log(
                    "[CONVERTER] MP4:",
                    mp4File
                );


                console.log(
                    "=========================================="
                );



                setTimeout(
                    function () {

                        window.startGemini();

                    },
                    0
                );

            }
            else {


                console.log(
                    "[CONVERTER] Gemini自動実行なし"
                );


                console.log(
                    "[CONVERTER] MP3:",
                    mp3File
                );


                console.log(
                    "[CONVERTER] MP4:",
                    mp4File
                );

            }



            // =================================
            // 実行ボタン復帰
            // =================================

            restoreConvertButton();

        }



        // =====================================
        // Gemini展開ボタン設定
        //
        // MP3の右側に
        //
        // [mp3] ▲
        //
        // を表示
        //
        // ▲を押すと
        //
        // Geminiで文字起こし
        //
        // を展開
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
            // Gemini実行
            // ---------------------------------

            if (transcribeButton) {


                transcribeButton.addEventListener(
                    "click",
                    function () {


                        console.log(
                            "[GEMINI] 手動文字起こし開始"
                        );



                        if (
                            typeof window.startGemini ===
                            "function"
                        ) {


                            window.startGemini();

                        }
                        else {


                            console.error(
                                "[GEMINI] startGemini がありません"
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
        // SRT処理情報を追加
        //
        // converter-gemini.js から呼ばれる
        //
        // SRT情報は
        // 【処理詳細】の中へ追加する
        // =====================================

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



                // ---------------------------------
                // SRT処理情報
                // ---------------------------------

                srtInfo.innerHTML =
                    html;


                srtInfo.style.display =
                    "block";



                // ---------------------------------
                // 保存
                // ---------------------------------

                currentSrtFile =
                    srtFile || "";



                // ---------------------------------
                // SRTダウンロードボタン
                //
                // MP3 / MP4の横へ追加
                // ---------------------------------

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
        // 字幕付きMP4ダウンロードボタン追加
        //
        // 外部処理から呼び出し可能
        //
        // 使用例：
        //
        // window.converterMain.addSubtitleEmbedFile(
        //     "xxx_sub_embed.mp4"
        // );
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
                        字幕付
                    </a>

                `;

            };



        // =====================================
        // 字幕付きMP4情報追加
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
        //
        // タイトルはここでは表示しない
        //
        // タイトルはダウンロードボタンの
        // 上に1回だけ表示する
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
        // 初期状態
        // =====================================

        console.log(
            "converter.js loaded"
        );

    }
);
