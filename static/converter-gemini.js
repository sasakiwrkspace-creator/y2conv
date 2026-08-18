// =====================================
// YouTube Converter
// converter.js
//
// 全体の入口・共通状態・変換JOB管理
//
// 読み込むファイル
// -------------------------------------
// converter-time.js
// converter-download.js
// converter-gemini.js
// =====================================


import {
    setupTimeInputs,
    getTimeRange
} from "./converter-time.js";


import {
    showFiles,
    hideGeminiArea,
    resetGeminiButton,
    escapeHtml,
    makeDownloadUrl
} from "./converter-download.js";


import {
    startGemini,
    resetGeminiState
} from "./converter-gemini.js";



// =====================================
// DOMContentLoaded
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
        // JOB状態
        // =====================================

        let currentJobId =
            null;


        let convertSeconds =
            0;


        let convertTimer =
            null;


        let convertStartTime =
            null;


        let convertEndTime =
            null;


        let currentVideoTitle =
            "";


        let currentVideoDuration =
            "";


        let currentMp3File =
            "";


        let currentMp4File =
            "";



        // =====================================
        // 外部モジュールへ状態を渡す
        // =====================================

        window.converterState = {

            getJobId: function () {

                return currentJobId;

            },


            getVideoTitle: function () {

                return currentVideoTitle;

            },


            getVideoDuration: function () {

                return currentVideoDuration;

            },


            getConvertSeconds: function () {

                return convertSeconds;

            },


            getConvertStartTime: function () {

                return convertStartTime;

            },


            getConvertEndTime: function () {

                return convertEndTime;

            },


            getMp3File: function () {

                return currentMp3File;

            },


            getMp4File: function () {

                return currentMp4File;

            },


            setMp3File: function (value) {

                currentMp3File =
                    value || "";

            },


            setMp4File: function (value) {

                currentMp4File =
                    value || "";

            }

        };



        // =====================================
        // 時間入力
        // =====================================

        setupTimeInputs();



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
        // 変換中表示
        // =====================================

        function showConvertingState() {

            if (!convertButton) {
                return;
            }


            convertButton.innerHTML = `
                <span class="converting-text">
                    <span>変換中</span>
                    <span>${convertSeconds}秒</span>
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
        // 出力形式
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
        // 変換開始
        // =====================================

        async function startConvert() {

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



            // =================================
            // ダウンロード領域クリア
            // =================================

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }



            // =================================
            // Gemini領域を隠す
            // =================================

            hideGeminiArea();



            // =================================
            // Gemini状態リセット
            // =================================

            resetGeminiButton();

            resetGeminiState();



            // =================================
            // ボタン無効化
            // =================================

            if (convertButton) {

                convertButton.disabled =
                    true;

            }



            // =================================
            // タイマー開始
            // =================================

            startConvertTimer();



            try {

                // =================================
                // /convert
                // =================================

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



                // =================================
                // JSON
                // =================================

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

                if (
                    data.success
                ) {

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


                    // ---------------------------------
                    // STATUS監視開始
                    // ---------------------------------

                    checkStatus();

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
        // STATUS確認
        // =====================================

        async function checkStatus() {

            // ---------------------------------
            // JOB IDがない
            // ---------------------------------

            if (!currentJobId) {

                return;

            }



            try {

                const response =
                    await fetch(
                        `/status/${encodeURIComponent(currentJobId)}`,
                        {

                            method:
                                "GET",

                            cache:
                                "no-store"

                        }
                    );



                // =================================
                // 429
                // =================================

                if (
                    response.status === 429
                ) {

                    console.warn(
                        "STATUS 429: Rate Limit / Cloudflare"
                    );


                    setTimeout(
                        checkStatus,
                        15000
                    );


                    return;

                }



                // =================================
                // Render一時エラー
                // =================================

                if (
                    response.status === 502 ||
                    response.status === 503 ||
                    response.status === 504
                ) {

                    console.warn(
                        "一時的なRenderエラー:",
                        response.status
                    );


                    setTimeout(
                        checkStatus,
                        5000
                    );


                    return;

                }



                // =================================
                // その他HTTPエラー
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
                        text
                    );

                }



                // =================================
                // レスポンス
                // =================================

                const text =
                    await response.text();


                if (!text) {

                    setTimeout(
                        checkStatus,
                        5000
                    );


                    return;

                }



                // =================================
                // JSON
                // =================================

                let data;


                try {

                    data =
                        JSON.parse(
                            text
                        );

                }
                catch (error) {

                    console.error(
                        "STATUS JSON解析エラー:",
                        error
                    );


                    setTimeout(
                        checkStatus,
                        5000
                    );


                    return;

                }



                console.log(
                    "STATUS:",
                    data
                );



                // =================================
                // JOBなし
                //
                // ここが今回重要
                //
                // 「jobなし」が一時的に返っても
                // すぐ終了させず再確認する
                // =================================

                if (
                    data.status === "error" &&
                    data.message === "jobなし"
                ) {

                    console.warn(
                        "STATUS: jobなし"
                    );


                    setTimeout(
                        checkStatus,
                        5000
                    );


                    return;

                }



                // =================================
                // 完了
                // =================================

                if (
                    data.status === "complete"
                ) {

                    stopConvertTimer();


                    currentVideoTitle =
                        data.title ||
                        data.video_title ||
                        currentVideoTitle;


                    currentVideoDuration =
                        data.duration ||
                        data.video_duration ||
                        currentVideoDuration;



                    if (convertButton) {

                        convertButton.style.display =
                            "none";

                    }



                    showFiles(
                        Array.isArray(
                            data.files
                        )
                            ? data.files
                            : [],
                        data
                    );


                    return;

                }



                // =================================
                // エラー
                // =================================

                if (
                    data.status === "error"
                ) {

                    stopConvertTimer();


                    if (convertButton) {

                        convertButton.disabled =
                            false;


                        convertButton.innerHTML =
                            "実行";


                        convertButton.style.display =
                            "";

                    }


                    alert(
                        data.message ||
                        "変換中にエラーが発生しました"
                    );


                    return;

                }



                // =================================
                // queued / running
                // =================================

                setTimeout(
                    checkStatus,
                    5000
                );

            }
            catch (error) {

                console.error(
                    "変換状態確認エラー:",
                    error
                );


                // ---------------------------------
                // ネットワークエラー
                // ---------------------------------

                setTimeout(
                    checkStatus,
                    5000
                );

            }

        }



        // =====================================
        // Geminiボタン
        // =====================================

        const geminiButton =
            document.getElementById(
                "gemini-button"
            );


        if (geminiButton) {

            geminiButton.addEventListener(
                "click",
                function () {

                    startGemini();

                }
            );

        }



        // =====================================
        // デバッグ用
        // =====================================

        window.youtubeConverter = {

            getJobId: function () {

                return currentJobId;

            },


            getVideoTitle: function () {

                return currentVideoTitle;

            },


            getVideoDuration: function () {

                return currentVideoDuration;

            },


            getMp3File: function () {

                return currentMp3File;

            },


            getMp4File: function () {

                return currentMp4File;

            },


            getElapsedSeconds: function () {

                return convertSeconds;

            }

        };



    }
);
