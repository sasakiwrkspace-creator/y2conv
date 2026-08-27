// =====================================
// YouTube Converter - Gemini
// static/converter-gemini.js
//
// converter-utils.js を基準として使用
//
// ・Gemini文字起こし
// ・SRTダウンロード
// ・SRT変換情報表示
// ・タイトル / 再生時間は converterState から取得
// ・SRT実行時間をブラウザ実測
//
// 表示仕様
// ・MP3 / MP4 / SRT のダウンロードボタンは横並び
// ・タイトルはダウンロードボタンの上には表示しない
// ・SRT処理情報は「処理詳細」の中に表示
//
// 共通関数は converter-utils.js を使用
// =====================================


(function () {

    "use strict";


    // =====================================
    // Gemini初期化
    // =====================================

    function initializeConverterGemini() {


        // =====================================
        // 二重初期化防止
        // =====================================

        if (
            window.converterGemini &&
            window.converterGemini.__initialized
        ) {

            console.log(
                "[GEMINI] already initialized"
            );

            return;

        }


        // =====================================
        // converterUtils確認
        // =====================================

        if (
            !window.converterUtils
        ) {

            console.error(
                "[GEMINI] converterUtils がありません"
            );

            return;

        }


        const utils =
            window.converterUtils;


        // =====================================
        // 共通関数確認
        // =====================================

        const requiredFunctions = [

            "escapeHtml",
            "formatClock",
            "formatElapsed",
            "formatDuration",
            "makeDownloadUrl"

        ];


        for (
            const functionName
            of requiredFunctions
        ) {

            if (
                typeof utils[functionName] !==
                "function"
            ) {

                console.error(
                    "[GEMINI] converterUtils." +
                    functionName +
                    " がありません"
                );

                return;

            }

        }


        // =====================================
        // DOM取得
        // =====================================

        function getGeminiButton() {

            return document.getElementById(
                "gemini-button"
            );

        }


        function getGeminiFileElement() {

            return document.getElementById(
                "gemini-file"
            );

        }


        function getGeminiResult() {

            return document.getElementById(
                "gemini-result"
            );

        }


        // =====================================
        // converterState
        // =====================================

        function getCurrentVideoTitle() {

            if (
                window.converterState
            ) {

                return (
                    window.converterState.currentVideoTitle ||
                    ""
                );

            }


            return "";

        }


        function getCurrentVideoDuration() {

            if (
                window.converterState
            ) {

                return (
                    window.converterState.currentVideoDuration ||
                    ""
                );

            }


            return "";

        }


        // =====================================
        // SRTファイル保存
        // =====================================

        function saveCurrentSrtFile(
            srtFile
        ) {

            if (
                !window.converterState
            ) {

                return;

            }


            window.converterState.currentSrtFile =
                srtFile;

        }


        // =====================================
        // SRT経過時間表示
        // =====================================

        function getSrtElapsedSeconds(
            startTime
        ) {

            if (!startTime) {

                return 0;

            }


            return Math.max(
                0,
                Math.floor(
                    (
                        Date.now() -
                        startTime.getTime()
                    ) / 1000
                )
            );

        }


        // =====================================
        // Gemini開始
        // =====================================

        async function startGemini() {


            // =================================
            // 開始時刻
            // =================================

            const srtStart =
                new Date();


            // =================================
            // DOM
            // =================================

            const geminiButton =
                getGeminiButton();


            const geminiFileElement =
                getGeminiFileElement();


            const result =
                getGeminiResult();


            // =================================
            // ファイル
            // =================================

            const file =
                geminiFileElement
                    ? geminiFileElement.value.trim()
                    : "";


            // =================================
            // MP3チェック
            // =================================

            if (
                !file
            ) {

                alert(
                    "MP3ファイルがありません"
                );

                return;

            }


            // =================================
            // ボタンチェック
            // =================================

            if (
                !geminiButton
            ) {

                console.error(
                    "[GEMINI] gemini-button が見つかりません"
                );

                return;

            }


            // =================================
            // 開始ログ
            // =================================

            console.log(
                "=========================================="
            );

            console.log(
                "[GEMINI] 文字起こし開始"
            );

            console.log(
                "[GEMINI] 開始時刻:",
                utils.formatClock(
                    srtStart
                )
            );

            console.log(
                "[GEMINI] ファイル:",
                file
            );

            console.log(
                "[GEMINI] タイトル:",
                getCurrentVideoTitle()
            );

            console.log(
                "[GEMINI] 再生時間:",
                getCurrentVideoDuration()
            );

            console.log(
                "=========================================="
            );


            // =================================
            // ボタン状態
            // =================================

            geminiButton.disabled =
                true;


            geminiButton.textContent =
                "文字起こし中...";


            // =================================
            // 結果表示
            // =================================

            if (
                result
            ) {

                result.style.display =
                    "block";


                result.textContent =
                    "文字起こし中... 0秒";

            }


            // =================================
            // タイマー
            // =================================

            let timerId =
                null;


            function updateTimer() {

                const elapsedSeconds =
                    getSrtElapsedSeconds(
                        srtStart
                    );


                if (
                    result
                ) {

                    result.textContent =
                        "文字起こし中... "
                        +
                        utils.formatElapsed(
                            elapsedSeconds
                        );

                }


                timerId =
                    setTimeout(
                        updateTimer,
                        1000
                    );

            }


            updateTimer();


            try {


                // =================================
                // Gemini API
                // =================================

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
                                        file

                                })

                        }
                    );


                // =================================
                // HTTPエラー
                // =================================

                if (
                    !response.ok
                ) {

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


                if (
                    !text
                ) {

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
                catch (
                    error
                ) {

                    console.error(
                        "[GEMINI] JSON解析エラー:",
                        error
                    );

                    console.error(
                        "[GEMINI] レスポンス:",
                        text
                    );


                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }


                // =================================
                // タイマー停止
                // =================================

                if (
                    timerId !==
                    null
                ) {

                    clearTimeout(
                        timerId
                    );


                    timerId =
                        null;

                }


                // =================================
                // 成功
                // =================================

                if (
                    data.success
                ) {


                    // =================================
                    // 終了時刻
                    // =================================

                    const srtEnd =
                        new Date();


                    // =================================
                    // ブラウザ実測時間
                    // =================================

                    const actualElapsedSeconds =
                        Math.max(
                            0,
                            Math.floor(
                                (
                                    srtEnd.getTime() -
                                    srtStart.getTime()
                                ) / 1000
                            )
                        );


                    // =================================
                    // サーバー報告時間
                    // =================================

                    const responseSeconds =
                        Number(
                            data.seconds ??
                            data.elapsed_seconds
                        );


                    // =================================
                    // 最終採用時間
                    // =================================

                    const finalSeconds =
                        actualElapsedSeconds;


                    // =================================
                    // ログ
                    // =================================

                    console.log(
                        "=========================================="
                    );

                    console.log(
                        "[GEMINI] 文字起こし完了"
                    );

                    console.log(
                        "[GEMINI] 開始:",
                        utils.formatClock(
                            srtStart
                        )
                    );

                    console.log(
                        "[GEMINI] 終了:",
                        utils.formatClock(
                            srtEnd
                        )
                    );

                    console.log(
                        "[GEMINI] 実測時間:",
                        actualElapsedSeconds,
                        "秒"
                    );

                    console.log(
                        "[GEMINI] サーバー報告時間:",
                        responseSeconds,
                        "秒"
                    );

                    console.log(
                        "[GEMINI] 採用時間:",
                        finalSeconds,
                        "秒"
                    );

                    console.log(
                        "[GEMINI] SRT:",
                        data.srt_file
                    );

                    console.log(
                        "=========================================="
                    );


                    // =================================
                    // 結果非表示
                    // =================================

                    if (
                        result
                    ) {

                        result.style.display =
                            "none";

                    }


                    // =================================
                    // Geminiボタン非表示
                    // =================================

                    geminiButton.style.display =
                        "none";


                    // =================================
                    // SRT表示
                    // =================================

                    showSrtDownload(
                        data,
                        srtStart,
                        srtEnd,
                        finalSeconds
                    );


                    return;

                }


                // =================================
                // Gemini失敗
                // =================================

                geminiButton.disabled =
                    false;


                geminiButton.textContent =
                    "Geminiで文字起こし";


                if (
                    result
                ) {

                    result.style.display =
                        "block";


                    result.textContent =
                        data.message ||
                        "文字起こしに失敗しました";

                }

            }
            catch (
                error
            ) {


                // =================================
                // タイマー停止
                // =================================

                if (
                    timerId !==
                    null
                ) {

                    clearTimeout(
                        timerId
                    );


                    timerId =
                        null;

                }


                // =================================
                // エラーログ
                // =================================

                console.error(
                    "[GEMINI] エラー:",
                    error
                );


                // =================================
                // ボタン復帰
                // =================================

                geminiButton.disabled =
                    false;


                geminiButton.textContent =
                    "Geminiで文字起こし";


                // =================================
                // エラー表示
                // =================================

                if (
                    result
                ) {

                    result.style.display =
                        "block";


                    result.textContent =
                        "エラー: "
                        +
                        (
                            error &&
                            error.message
                                ? error.message
                                : "不明なエラー"
                        );

                }

            }

        }


        // =====================================
        // SRT表示
        // =====================================

        function showSrtDownload(
            data,
            srtStart,
            srtEnd,
            srtSeconds
        ) {


            // =================================
            // SRTファイル
            // =================================

            const srtFile =
                data.srt_file ||
                data.srt ||
                data.file ||
                "";


            if (
                !srtFile
            ) {

                console.error(
                    "[GEMINI] SRTファイルがありません:",
                    data
                );

                return;

            }


            // =================================
            // 時刻補正
            // =================================

            if (
                !srtStart
            ) {

                srtStart =
                    new Date();

            }


            if (
                !srtEnd
            ) {

                srtEnd =
                    new Date();

            }


            // =================================
            // 実行時間補正
            // =================================

            if (
                srtSeconds ===
                undefined ||
                srtSeconds ===
                null
            ) {

                srtSeconds =
                    Math.max(
                        0,
                        Math.floor(
                            (
                                srtEnd.getTime() -
                                srtStart.getTime()
                            ) / 1000
                        )
                    );

            }


            // =================================
            // タイトル
            // =================================

            const title =
                data.title ||
                data.video_title ||
                getCurrentVideoTitle() ||
                "不明";


            // =================================
            // 再生時間
            // =================================

            const duration =
                data.duration ||
                data.video_duration ||
                getCurrentVideoDuration() ||
                "不明";


            // =================================
            // SRT処理詳細
            // =================================

            const srtInfo = `

                <div class="conversion-info srt-conversion-info">

                    <div class="conversion-info-title">
                        ★SRT変換
                    </div>

                    <div>
                        タイトル：
                        ${utils.escapeHtml(
                            title
                        )}
                    </div>

                    <div>
                        再生時間：
                        ${utils.escapeHtml(
                            utils.formatDuration(
                                duration
                            )
                        )}
                    </div>

                    <div>
                        実行開始：
                        ${utils.escapeHtml(
                            utils.formatClock(
                                srtStart
                            )
                        )}
                    </div>

                    <div>
                        実行終了：
                        ${utils.escapeHtml(
                            utils.formatClock(
                                srtEnd
                            )
                        )}

                        （${utils.escapeHtml(
                            utils.formatElapsed(
                                srtSeconds
                            )
                        )}）

                    </div>

                </div>

            `;


            // =================================
            // converter.jsへ通知
            // =================================

            if (
                window.converterMain &&
                typeof
                    window.converterMain.addSrtInfo ===
                    "function"
            ) {

                console.log(
                    "[GEMINI] converterMain.addSrtInfo()"
                );


                window.converterMain.addSrtInfo(
                    srtInfo,
                    srtFile
                );

            }
            else {

                console.error(
                    "[GEMINI] converterMain.addSrtInfo がありません"
                );

            }


            // =================================
            // converterStateへ保存
            // =================================

            saveCurrentSrtFile(
                srtFile
            );


            // =================================
            // SRTダウンロードボタン
            //
            // converterMain側で生成する。
            // 念のため既存コンテナがあれば
            // 直接更新する。
            // =================================

            const buttonContainer =
                document.getElementById(
                    "srt-download-button-container"
                );


            if (
                buttonContainer &&
                !window.converterMain
            ) {

                buttonContainer.innerHTML = `

                    <a
                        href="${utils.escapeHtml(
                            utils.makeDownloadUrl(
                                srtFile
                            )
                        )}"
                        download
                        class="download-button"
                        id="srt-download-button"
                    >
                        srt
                    </a>

                `;

            }


            // =================================
            // ログ
            // =================================

            console.log(
                "[SRT DISPLAY]",
                {

                    title:
                        title,

                    duration:
                        duration,

                    srtStart:
                        srtStart,

                    srtEnd:
                        srtEnd,

                    srtSeconds:
                        srtSeconds,

                    srtFile:
                        srtFile

                }
            );

        }


        // =====================================
        // Geminiボタン
        // =====================================

        const geminiButton =
            getGeminiButton();


        if (
            geminiButton &&
            geminiButton.dataset.geminiInitialized !==
                "true"
        ) {

            geminiButton.dataset.geminiInitialized =
                "true";


            geminiButton.addEventListener(
                "click",
                startGemini
            );

        }


        // =====================================
        // 共通オブジェクト
        // =====================================

        const gemini = {

            __initialized:
                true,

            start:
                startGemini,

            showSrtDownload:
                showSrtDownload,

            getCurrentVideoTitle:
                getCurrentVideoTitle,

            getCurrentVideoDuration:
                getCurrentVideoDuration

        };


        // =====================================
        // グローバル公開
        // =====================================

        window.converterGemini =
            gemini;


        window.ConverterGemini =
            gemini;


        // =====================================
        // 旧互換
        // =====================================

        window.startGemini =
            startGemini;


        window.showSrtDownload =
            showSrtDownload;


        // =====================================
        // 読み込み確認
        // =====================================

        console.log(
            "======================================"
        );

        console.log(
            "converter-gemini.js loaded"
        );

        console.log(
            "[GEMINI] converterUtils:",
            window.converterUtils
        );

        console.log(
            "[GEMINI] start:",
            typeof window.converterGemini.start
        );

        console.log(
            "[GEMINI] showSrtDownload:",
            typeof window.converterGemini.showSrtDownload
        );

        console.log(
            "======================================"
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
            initializeConverterGemini,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeConverterGemini();

    }


})();
