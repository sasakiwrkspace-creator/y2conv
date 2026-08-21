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
        // =====================================

        function escapeHtml(value) {

            if (
                window.converterUtils &&
                typeof
                    window.converterUtils.escapeHtml ===
                    "function"
            ) {

                return window.converterUtils.escapeHtml(
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
                window.converterUtils &&
                typeof
                    window.converterUtils.formatClock ===
                    "function"
            ) {

                return window.converterUtils.formatClock(
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
                window.converterUtils &&
                typeof
                    window.converterUtils.formatElapsed ===
                    "function"
            ) {

                return window.converterUtils.formatElapsed(
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
                window.converterUtils &&
                typeof
                    window.converterUtils.formatDuration ===
                    "function"
            ) {

                return window.converterUtils.formatDuration(
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

                    return (
                        String(
                            parseInt(
                                parts[0],
                                10
                            ) || 0
                        ).padStart(
                            2,
                            "0"
                        )
                        +
                        ":"
                        +
                        String(
                            parseInt(
                                parts[1],
                                10
                            ) || 0
                        ).padStart(
                            2,
                            "0"
                        )
                        +
                        ":"
                        +
                        String(
                            parseInt(
                                parts[2],
                                10
                            ) || 0
                        ).padStart(
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
                window.converterUtils &&
                typeof
                    window.converterUtils.makeDownloadUrl ===
                    "function"
            ) {

                return window.converterUtils.makeDownloadUrl(
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
        // Gemini開始
        // =====================================

        async function startGemini() {

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
            // タイマー
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
                // 成功
                // =================================

                if (data.success) {

                    const srtEnd =
                        new Date();


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
        // SRT表示
        //
        // MP3 / MP4の処理詳細の中に追加
        // =====================================

        function showSrtDownload(
            data,
            srtStart,
            srtEnd,
            srtSeconds
        ) {

            const srtFile =
                data.srt_file ||
                "";


            if (!srtFile) {

                console.error(
                    "SRTファイルがありません:",
                    data
                );

                return;

            }


            if (!srtStart) {

                srtStart =
                    new Date();

            }


            if (!srtEnd) {

                srtEnd =
                    new Date();

            }


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
            // converter.jsへ渡す
            // =================================

            if (
                window.converterMain &&
                typeof
                    window.converterMain.addSrtInfo ===
                    "function"
            ) {

                window.converterMain.addSrtInfo(
                    srtInfo,
                    srtFile
                );

            }
            else {

                console.error(
                    "converterMain.addSrtInfo がありません"
                );

            }


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
        //
        // MP3単独時の手動実行用
        // =====================================

        if (geminiButton) {

            geminiButton.addEventListener(
                "click",
                startGemini
            );

        }


        // =====================================
        // 外部公開
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
