// =====================================
// YouTube Converter - Gemini
// static/converter-gemini.js
//
// ・Gemini文字起こし
// ・SRTダウンロード
// ・SRT変換情報表示
// ・タイトル / 再生時間は converterState から取得
// ・SRT実行時間を正しく計測
// =====================================


document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =====================================
        // DOM
        // =====================================

        const geminiButton =
            document.getElementById(
                "gemini-button"
            );



        // =====================================
        // 共通関数
        // converter-utils.js が読み込まれている
        // 前提
        // =====================================

        function escapeHtml(value) {

            if (
                typeof window.escapeHtml ===
                "function"
            ) {

                return window.escapeHtml(
                    value
                );

            }


            return String(value)
                .replace(
                    /&/g,
                    "&amp;"
                )
                .replace(
                    /</g,
                    "&lt;"
                )
                .replace(
                    />/g,
                    "&gt;"
                )
                .replace(
                    /"/g,
                    "&quot;"
                )
                .replace(
                    /'/g,
                    "&#039;"
                );

        }



        function formatClock(date) {

            if (
                typeof window.formatClock ===
                "function"
            ) {

                return window.formatClock(
                    date
                );

            }


            if (!date) {

                return "";

            }


            return date.toLocaleTimeString(
                "ja-JP",
                {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: false
                }
            );

        }



        function formatElapsed(seconds) {

            if (
                typeof window.formatElapsed ===
                "function"
            ) {

                return window.formatElapsed(
                    seconds
                );

            }


            const totalSeconds =
                Math.floor(
                    Number(seconds) || 0
                );


            const minutes =
                Math.floor(
                    totalSeconds / 60
                );


            const remainSeconds =
                totalSeconds % 60;


            if (minutes === 0) {

                return (
                    remainSeconds +
                    "秒"
                );

            }


            return (
                minutes +
                "分" +
                remainSeconds +
                "秒"
            );

        }



        function formatDuration(duration) {

            if (
                typeof window.formatDuration ===
                "function"
            ) {

                return window.formatDuration(
                    duration
                );

            }


            if (
                duration === null ||
                duration === undefined ||
                duration === ""
            ) {

                return "不明";

            }


            if (
                typeof duration === "string" &&
                duration.includes(":")
            ) {

                const parts =
                    duration.split(":");


                if (
                    parts.length === 3
                ) {

                    const hours =
                        parseInt(
                            parts[0],
                            10
                        ) || 0;


                    const minutes =
                        parseInt(
                            parts[1],
                            10
                        ) || 0;


                    const seconds =
                        parseInt(
                            parts[2],
                            10
                        ) || 0;


                    return (
                        String(hours).padStart(
                            2,
                            "0"
                        )
                        +
                        ":"
                        +
                        String(minutes).padStart(
                            2,
                            "0"
                        )
                        +
                        ":"
                        +
                        String(seconds).padStart(
                            2,
                            "0"
                        )
                    );

                }

            }


            const totalSeconds =
                parseInt(
                    duration,
                    10
                );


            if (
                isNaN(totalSeconds) ||
                totalSeconds < 0
            ) {

                return "不明";

            }


            const hours =
                Math.floor(
                    totalSeconds / 3600
                );


            const minutes =
                Math.floor(
                    (totalSeconds % 3600) / 60
                );


            const seconds =
                totalSeconds % 60;


            return (
                String(hours).padStart(
                    2,
                    "0"
                )
                +
                ":"
                +
                String(minutes).padStart(
                    2,
                    "0"
                )
                +
                ":"
                +
                String(seconds).padStart(
                    2,
                    "0"
                )
            );

        }



        function makeDownloadUrl(filename) {

            if (
                typeof window.makeDownloadUrl ===
                "function"
            ) {

                return window.makeDownloadUrl(
                    filename
                );

            }


            return (
                "/download/" +
                encodeURIComponent(
                    filename
                )
            );

        }



        // =====================================
        // 共通状態
        //
        // converter.js が
        // window.converterState に保存している
        // 情報を取得する
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
        // Gemini開始
        // =====================================

        async function startGemini() {


            // =================================
            // SRT / Gemini 実行開始時刻
            //
            // ここで取得する
            // =================================

            const srtStart =
                new Date();



            // =================================
            // DOM
            // =================================

            const geminiFileElement =
                document.getElementById(
                    "gemini-file"
                );


            const result =
                document.getElementById(
                    "gemini-result"
                );


            const file =
                geminiFileElement
                    ? geminiFileElement.value.trim()
                    : "";



            // =================================
            // MP3チェック
            // =================================

            if (!file) {

                alert(
                    "MP3ファイルがありません"
                );

                return;

            }


            if (!geminiButton) {

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
                formatClock(
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


            let seconds = 0;


            if (result) {

                result.style.display =
                    "block";


                result.textContent =
                    "文字起こし中... 0秒";

            }



            // =================================
            // 文字起こしタイマー
            // =================================

            const timer =
                setInterval(
                    function () {

                        seconds++;


                        if (result) {

                            result.textContent =
                                "文字起こし中... "
                                +
                                seconds
                                +
                                "秒";

                        }

                    },
                    1000
                );



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
                        "Gemini JSON解析エラー:",
                        error
                    );


                    console.error(
                        "Geminiレスポンス:",
                        text
                    );


                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }



                // =================================
                // タイマー停止
                // =================================

                clearInterval(
                    timer
                );



                // =================================
                // Gemini成功
                // =================================

                if (data.success) {


                    // ---------------------------------
                    // 完了時刻
                    // ---------------------------------

                    const srtEnd =
                        new Date();


                    // ---------------------------------
                    // 実際の経過時間
                    //
                    // Gemini APIが秒数を返していない場合は
                    // start → end から計算
                    // ---------------------------------

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


                    // ---------------------------------
                    // Gemini側から秒数が返っていれば使用
                    // ---------------------------------

                    const responseSeconds =
                        Number(
                            data.seconds ??
                            data.elapsed_seconds
                        );


                    const finalSeconds =
                        Number.isFinite(
                            responseSeconds
                        ) &&
                        responseSeconds >= 0
                            ? responseSeconds
                            : actualElapsedSeconds;



                    // ---------------------------------
                    // 完了ログ
                    // ---------------------------------

                    console.log(
                        "=========================================="
                    );

                    console.log(
                        "[GEMINI] 文字起こし完了"
                    );

                    console.log(
                        "[GEMINI] 開始:",
                        formatClock(
                            srtStart
                        )
                    );

                    console.log(
                        "[GEMINI] 終了:",
                        formatClock(
                            srtEnd
                        )
                    );

                    console.log(
                        "[GEMINI] 実行時間:",
                        finalSeconds,
                        "秒"
                    );

                    console.log(
                        "[GEMINI] タイトル:",
                        data.title ||
                        data.video_title ||
                        getCurrentVideoTitle()
                    );

                    console.log(
                        "[GEMINI] 再生時間:",
                        data.duration ||
                        data.video_duration ||
                        getCurrentVideoDuration()
                    );

                    console.log(
                        "[GEMINI] SRT:",
                        data.srt_file
                    );

                    console.log(
                        "=========================================="
                    );



                    if (result) {

                        result.style.display =
                            "none";

                    }


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


                if (result) {

                    result.style.display =
                        "block";


                    result.textContent =
                        data.message ||
                        "文字起こしに失敗しました";

                }

            }
            catch (error) {


                // =================================
                // タイマー停止
                // =================================

                clearInterval(
                    timer
                );


                console.error(
                    "Geminiエラー:",
                    error
                );


                geminiButton.disabled =
                    false;


                geminiButton.textContent =
                    "Geminiで文字起こし";


                if (result) {

                    result.style.display =
                        "block";


                    result.textContent =
                        "エラー: "
                        +
                        error.message;

                }

            }

        }



        // =====================================
        // SRTダウンロード表示
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
                "";



            // =================================
            // SRTファイルチェック
            // =================================

            if (!srtFile) {

                console.error(
                    "SRTファイルがレスポンスにありません:",
                    data
                );

                return;

            }



            // =================================
            // SRTエリア
            // =================================

            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if (!srtArea) {

                console.error(
                    "srtArea がありません"
                );

                return;

            }



            // =================================
            // 開始時刻保険
            // =================================

            if (!srtStart) {

                srtStart =
                    new Date();

            }



            // =================================
            // 終了時刻保険
            // =================================

            if (!srtEnd) {

                srtEnd =
                    new Date();

            }



            // =================================
            // 実行時間保険
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
            //
            // 優先順位
            //
            // 1. Geminiレスポンス
            // 2. converterState
            // 3. 不明
            // =================================

            const title =
                data.title ||
                data.video_title ||
                getCurrentVideoTitle() ||
                "不明";



            // =================================
            // 再生時間
            //
            // 優先順位
            //
            // 1. Geminiレスポンス
            // 2. converterState
            // 3. 不明
            // =================================

            const duration =
                data.duration ||
                data.video_duration ||
                getCurrentVideoDuration() ||
                "不明";



            // =================================
            // 確認ログ
            // =================================

            console.log(
                "[SRT DISPLAY]"
            );

            console.log(
                "title:",
                title
            );

            console.log(
                "duration:",
                duration
            );

            console.log(
                "srtStart:",
                srtStart
            );

            console.log(
                "srtEnd:",
                srtEnd
            );

            console.log(
                "srtSeconds:",
                srtSeconds
            );



            // =================================
            // SRT変換情報
            // =================================

            const srtInfo = `

                <div class="conversion-info">

                    <div class="conversion-info-title">
                        【SRT変換】
                    </div>

                    <div>
                        タイトル：
                        ${escapeHtml(
                            title
                        )}
                    </div>

                    <div>
                        再生時間：
                        ${escapeHtml(
                            formatDuration(
                                duration
                            )
                        )}
                    </div>

                    <div>
                        実行開始：
                        ${escapeHtml(
                            formatClock(
                                srtStart
                            )
                        )}
                    </div>

                    <div>
                        実行終了：
                        ${escapeHtml(
                            formatClock(
                                srtEnd
                            )
                        )}
                        （${escapeHtml(
                            formatElapsed(
                                srtSeconds
                            )
                        )}）
                    </div>

                </div>

            `;



            // =================================
            // ダウンロードHTML
            // =================================

            const downloadHtml = `

                ${srtInfo}

                <div class="srt-download-section">

                    <div class="download-label">
                        SRTダウンロード
                    </div>

                    <div class="srt-button-row">

                        <a
                            href="${makeDownloadUrl(
                                srtFile
                            )}"
                            download
                            class="download-button"
                        >
                            srt
                        </a>

                    </div>

                </div>

            `;



            // =================================
            // SRTダウンロード領域
            // =================================

            let srtDownloadArea =
                document.getElementById(
                    "srt-download-area"
                );


            if (!srtDownloadArea) {

                srtDownloadArea =
                    document.createElement(
                        "div"
                    );


                srtDownloadArea.id =
                    "srt-download-area";


                srtArea.appendChild(
                    srtDownloadArea
                );

            }



            // =================================
            // HTML反映
            // =================================

            srtDownloadArea.innerHTML =
                downloadHtml;



            // =================================
            // SRTエリア表示
            // =================================

            srtArea.style.display =
                "block";



            // =================================
            // SRT内容表示
            // =================================

            const srtContent =
                document.getElementById(
                    "srt-content"
                );


            if (srtContent) {

                srtContent.style.display =
                    "block";

            }



            // =================================
            // ▼ → ▲
            // =================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );


            if (toggle) {

                toggle.textContent =
                    "▲";


                toggle.setAttribute(
                    "aria-expanded",
                    "true"
                );

            }

        }



        // =====================================
        // Geminiボタンイベント
        // =====================================

        if (geminiButton) {

            geminiButton.addEventListener(
                "click",
                startGemini
            );

        }



        // =====================================
        // 外部から使用できるようにする
        // =====================================

        window.startGemini =
            startGemini;


        window.showSrtDownload =
            showSrtDownload;



        // =====================================
        // 読み込み確認
        // =====================================

        console.log(
            "converter-gemini.js loaded"
        );

    }
);
