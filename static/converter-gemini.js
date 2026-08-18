// =====================================
// YouTube Converter - Gemini
// static/converter-gemini.js
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
        // converter.js が保存した状態を取得
        // =====================================

        function getCurrentVideoTitle() {

            return (
                window.currentVideoTitle ||
                ""
            );

        }


        function getCurrentVideoDuration() {

            return (
                window.currentVideoDuration ||
                ""
            );

        }



        // =====================================
        // Gemini開始
        // =====================================

        async function startGemini() {

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

                    if (result) {

                        result.style.display =
                            "none";

                    }


                    geminiButton.style.display =
                        "none";


                    showSrtDownload(
                        data
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
        // SRTダウンロード表示
        // =====================================

        function showSrtDownload(
            data
        ) {

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

                return;

            }



            // =================================
            // SRT変換時間
            // =================================

            const srtStart =
                new Date();


            const srtEnd =
                new Date();


            const srtSeconds =
                Number(
                    data.seconds ||
                    data.elapsed_seconds ||
                    0
                );



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
            // SRT変換情報
            // =================================

            const srtInfo = `

                <div class="conversion-info">

                    <div class="conversion-info-title">
                        【SRT変換】
                    </div>

                    <div>
                        タイトル：
                        ${escapeHtml(title)}
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

    }
);
