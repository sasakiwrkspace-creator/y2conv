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

        let currentJobId = null;


        // =====================================
        // 変換時間
        // =====================================

        let convertSeconds = 0;

        let convertTimer = null;

        let convertStartTime = null;

        let convertEndTime = null;


        // =====================================
        // 動画情報
        // =====================================

        let currentVideoTitle = "";

        let currentVideoDuration = "";


        // =====================================
        // ファイル
        // =====================================

        let currentMp3File = "";

        let currentMp4File = "";



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
                currentJobId = value;
            },


            get convertSeconds() {
                return convertSeconds;
            },

            set convertSeconds(value) {
                convertSeconds = value;
            },


            get convertStartTime() {
                return convertStartTime;
            },

            set convertStartTime(value) {
                convertStartTime = value;
            },


            get convertEndTime() {
                return convertEndTime;
            },

            set convertEndTime(value) {
                convertEndTime = value;
            },


            get currentVideoTitle() {
                return currentVideoTitle;
            },

            set currentVideoTitle(value) {
                currentVideoTitle = value;
            },


            get currentVideoDuration() {
                return currentVideoDuration;
            },

            set currentVideoDuration(value) {
                currentVideoDuration = value;
            },


            get currentMp3File() {
                return currentMp3File;
            },

            set currentMp3File(value) {
                currentMp3File = value;
            },


            get currentMp4File() {
                return currentMp4File;
            },

            set currentMp4File(value) {
                currentMp4File = value;
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
        //
        // converter-utils.js の
        // makeTime() を利用
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


                return window.converterUtils.makeTime(
                    h,
                    m,
                    s
                );

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

            convertSeconds = 0;


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
            // ボタン
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
                                JSON.stringify({

                                    url:
                                        url,

                                    outputs:
                                        outputs,

                                    start_time:
                                        timeRange.start_time,

                                    end_time:
                                        timeRange.end_time

                                })

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
        // 完了処理
        //
        // converter-status.js から呼ばれる
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
            // 状態
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


                if (convertButton) {

                    convertButton.style.display =
                        "";


                    convertButton.disabled =
                        false;


                    convertButton.innerHTML =
                        "実行";

                }


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
            // ダウンロードHTML
            // =================================

            let html =
                "";



            // =================================
            // MP3
            // =================================

            if (mp3File) {

                html += `

                    ${createConversionInfo(
                        "MP3",
                        data || {}
                    )}

                    <div class="download-section">

                        <div class="download-label">
                            MP3のダウンロード
                        </div>

                        <div class="mp3-button-row">

                            <a
                                href="${window.converterUtils.makeDownloadUrl(mp3File)}"
                                download
                                class="download-button"
                            >
                                mp3
                            </a>

                            <button
                                type="button"
                                id="srt-toggle-button"
                                class="srt-toggle-button"
                                aria-expanded="false"
                            >
                                ▼
                            </button>

                        </div>

                    </div>

                `;

            }



            // =================================
            // MP4
            // =================================

            if (mp4File) {

                html += `

                    ${createConversionInfo(
                        "MP4",
                        data || {}
                    )}

                    <div class="download-section">

                        <div class="download-label">
                            MP4のダウンロード
                        </div>

                        <div class="mp4-button-row">

                            <a
                                href="${window.converterUtils.makeDownloadUrl(mp4File)}"
                                download
                                class="download-button"
                            >
                                mp4
                            </a>

                        </div>

                    </div>

                `;

            }



            // =================================
            // HTML反映
            // =================================

            downloadArea.innerHTML =
                html;



            // =================================
            // Gemini領域
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


                return;

            }



            // =================================
            // ▼ボタン
            // =================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );


            if (
                toggle &&
                srtArea
            ) {

                toggle.addEventListener(
                    "click",
                    function () {

                        const isHidden =
                            srtArea.style.display ===
                            "none";


                        if (isHidden) {

                            srtArea.style.display =
                                "block";


                            if (srtContent) {

                                srtContent.style.display =
                                    "block";

                            }


                            toggle.textContent =
                                "▲";


                            toggle.setAttribute(
                                "aria-expanded",
                                "true"
                            );

                        }
                        else {

                            srtArea.style.display =
                                "none";


                            toggle.textContent =
                                "▼";


                            toggle.setAttribute(
                                "aria-expanded",
                                "false"
                            );

                        }

                    }
                );

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

        }



        // =====================================
        // 変換情報HTML
        // =====================================

        function createConversionInfo(
            type,
            data,
            durationOverride
        ) {

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

                        【${window.converterUtils.escapeHtml(type)}変換】

                    </div>


                    <div>

                        タイトル：
                        ${window.converterUtils.escapeHtml(title)}

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
                        ${window.converterUtils.escapeHtml(start)}

                    </div>


                    <div>

                        実行終了：
                        ${window.converterUtils.escapeHtml(end)}

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
