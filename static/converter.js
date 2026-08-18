// =====================================
// YouTube Converter
// converter.js
//
// メイン処理
//
// 構成
// -------------------------------------
// converter.js
// converter-gemini.js
// converter-status.js
// converter-utils.js
// =====================================


import {
    getSelectedOutputs,
    getTimeRange,
    setupNumericInputs,
    hideGeminiArea,
    resetGeminiButton,
    resetGeminiState
} from "./converter-utils.js";


import {
    startGemini
} from "./converter-gemini.js";


import {
    startStatusCheck,
    stopStatusCheck
} from "./converter-status.js";



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


        const geminiButton =
            document.getElementById(
                "gemini-button"
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



        // =====================================
        // Numeric Input
        // =====================================

        setupNumericInputs();



        // =====================================
        // 状態取得
        //
        // 他ファイルから参照できるようにする
        // =====================================

        window.converterState = {

            getJobId:
                function () {

                    return currentJobId;

                },


            getVideoTitle:
                function () {

                    return currentVideoTitle;

                },


            getVideoDuration:
                function () {

                    return currentVideoDuration;

                },


            getConvertSeconds:
                function () {

                    return convertSeconds;

                },


            getConvertStartTime:
                function () {

                    return convertStartTime;

                },


            getConvertEndTime:
                function () {

                    return convertEndTime;

                },


            getMp3File:
                function () {

                    return currentMp3File;

                },


            getMp4File:
                function () {

                    return currentMp4File;

                },


            setJobId:
                function (value) {

                    currentJobId =
                        value || null;

                },


            setVideoTitle:
                function (value) {

                    currentVideoTitle =
                        value || "";

                },


            setVideoDuration:
                function (value) {

                    currentVideoDuration =
                        value || "";

                },


            setMp3File:
                function (value) {

                    currentMp3File =
                        value || "";

                },


            setMp4File:
                function (value) {

                    currentMp4File =
                        value || "";

                },


            getDownloadArea:
                function () {

                    return downloadArea;

                },


            getConvertButton:
                function () {

                    return convertButton;

                }

        };



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

                convertTimer =
                    null;

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


            convertEndTime =
                new Date();

        }



        // =====================================
        // 変換開始
        // =====================================

        async function startConvert() {

            // ---------------------------------
            // 出力形式
            // ---------------------------------

            const outputs =
                getSelectedOutputs();



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
            // 出力チェック
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
            // 既存STATUS監視停止
            // =================================

            stopStatusCheck();



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
            // downloadArea
            // =================================

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }



            // =================================
            // Gemini領域
            // =================================

            hideGeminiArea();


            resetGeminiButton();


            resetGeminiState();



            // =================================
            // ボタン
            // =================================

            if (convertButton) {

                convertButton.disabled =
                    true;


                convertButton.style.display =
                    "";


                convertButton.innerHTML =
                    "実行";

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
                // JSON解析
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
                // JOB開始成功
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
                    // STATUS監視
                    // ---------------------------------

                    startStatusCheck();

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


                stopStatusCheck();



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
        // Gemini
        // =====================================

        if (geminiButton) {

            geminiButton.addEventListener(
                "click",
                function () {

                    startGemini();

                }
            );

        }



        // =====================================
        // STATUSから呼び出す関数
        //
        // converter-status.js が
        // window.converterCallbacks を
        // 使用する
        // =====================================

        window.converterCallbacks = {

            // ---------------------------------
            // タイマー停止
            // ---------------------------------

            stopConvertTimer:
                function () {

                    stopConvertTimer();

                },


            // ---------------------------------
            // タイマー秒数
            // ---------------------------------

            getConvertSeconds:
                function () {

                    return convertSeconds;

                },


            // ---------------------------------
            // 動画タイトル更新
            // ---------------------------------

            setVideoTitle:
                function (value) {

                    if (value) {

                        currentVideoTitle =
                            value;

                    }

                },


            // ---------------------------------
            // 動画時間更新
            // ---------------------------------

            setVideoDuration:
                function (value) {

                    if (
                        value !== undefined &&
                        value !== null &&
                        value !== ""
                    ) {

                        currentVideoDuration =
                            value;

                    }

                },


            // ---------------------------------
            // 完了処理
            // ---------------------------------

            onComplete:
                function (data) {

                    handleConversionComplete(
                        data
                    );

                },


            // ---------------------------------
            // エラー処理
            // ---------------------------------

            onError:
                function (message) {

                    handleConversionError(
                        message
                    );

                }

        };



        // =====================================
        // 変換完了
        // =====================================

        function handleConversionComplete(
            data
        ) {

            stopConvertTimer();


            stopStatusCheck();



            // =================================
            // 動画情報
            // =================================

            currentVideoTitle =
                data.title ||
                data.video_title ||
                currentVideoTitle;


            currentVideoDuration =
                data.duration ||
                data.video_duration ||
                currentVideoDuration;



            // =================================
            // ファイル取得
            // =================================

            const files =
                Array.isArray(
                    data.files
                )
                    ? data.files
                    : [];



            let mp3File =
                "";


            let mp4File =
                "";



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



            currentMp3File =
                mp3File;


            currentMp4File =
                mp4File;



            // =================================
            // Gemini用MP3
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
            // ダウンロード表示
            //
            // converter-utils.js 側
            // =================================

            if (
                typeof window.showConversionFiles ===
                "function"
            ) {

                window.showConversionFiles(
                    files,
                    data
                );

            }



            // =================================
            // converter-download.js が
            // window経由で登録されていない場合
            // =================================

            if (
                !window.showConversionFiles
            ) {

                console.error(
                    "showConversionFiles が登録されていません"
                );

            }



            // =================================
            // 完了後ボタン
            // =================================

            if (convertButton) {

                convertButton.style.display =
                    "none";

            }

        }



        // =====================================
        // 変換エラー
        // =====================================

        function handleConversionError(
            message
        ) {

            stopConvertTimer();


            stopStatusCheck();



            if (convertButton) {

                convertButton.disabled =
                    false;


                convertButton.style.display =
                    "";


                convertButton.innerHTML =
                    "実行";

            }



            alert(
                message ||
                "変換中にエラーが発生しました"
            );

        }



        // =====================================
        // 外部からJOB IDを取得
        // =====================================

        window.getCurrentJobId =
            function () {

                return currentJobId;

            };



        // =====================================
        // デバッグ
        // =====================================

        window.youtubeConverter = {

            getJobId:
                function () {

                    return currentJobId;

                },


            getVideoTitle:
                function () {

                    return currentVideoTitle;

                },


            getVideoDuration:
                function () {

                    return currentVideoDuration;

                },


            getMp3File:
                function () {

                    return currentMp3File;

                },


            getMp4File:
                function () {

                    return currentMp4File;

                },


            getElapsedSeconds:
                function () {

                    return convertSeconds;

                }

        };


    }
);
