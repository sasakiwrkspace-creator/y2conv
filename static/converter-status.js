// =====================================
// YouTube Converter - Status
// converter-status.js
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================
        // Utils
        // =====================================

        const Utils =
            window.ConverterUtils || {};


        // =====================================
        // 変換状態
        // =====================================

        let currentJobId = null;

        let currentVideoTitle = "";

        let currentVideoDuration = "";

        let currentMp3File = "";

        let currentMp4File = "";



        // =====================================
        // 変換タイマー
        // =====================================

        let convertSeconds = 0;

        let convertTimer = null;

        let convertStartTime = null;

        let convertEndTime = null;



        // =====================================
        // DOM
        // =====================================

        const convertButton =
            document.getElementById(
                "convertBtn"
            );

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );



        // =====================================
        // 変換ボタン表示
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
        // JOB ID設定
        // =====================================

        function setJobId(jobId) {

            currentJobId =
                jobId || null;

        }



        // =====================================
        // JOB ID取得
        // =====================================

        function getJobId() {

            return currentJobId;

        }



        // =====================================
        // 動画情報設定
        // =====================================

        function setVideoInfo(
            title,
            duration
        ) {

            if (title) {

                currentVideoTitle =
                    title;

            }


            if (
                duration !== undefined &&
                duration !== null &&
                duration !== ""
            ) {

                currentVideoDuration =
                    duration;

            }

        }



        // =====================================
        // 動画タイトル取得
        // =====================================

        function getVideoTitle() {

            return currentVideoTitle;

        }



        // =====================================
        // 動画再生時間取得
        // =====================================

        function getVideoDuration() {

            return currentVideoDuration;

        }



        // =====================================
        // ファイル情報設定
        // =====================================

        function setFiles(
            mp3File,
            mp4File
        ) {

            currentMp3File =
                mp3File || "";

            currentMp4File =
                mp4File || "";

        }



        // =====================================
        // MP3ファイル取得
        // =====================================

        function getMp3File() {

            return currentMp3File;

        }



        // =====================================
        // MP4ファイル取得
        // =====================================

        function getMp4File() {

            return currentMp4File;

        }



        // =====================================
        // 完了時の変換情報表示
        // =====================================

        function createConversionInfo(
            type,
            data,
            durationOverride
        ) {

            data =
                data || {};


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
                convertStartTime &&
                Utils.formatClock
                    ? Utils.formatClock(
                        convertStartTime
                    )
                    : "";


            const end =
                convertEndTime &&
                Utils.formatClock
                    ? Utils.formatClock(
                        convertEndTime
                    )
                    : "";


            const elapsed =
                Utils.formatElapsed
                    ? Utils.formatElapsed(
                        convertSeconds
                    )
                    : (
                        convertSeconds +
                        "秒"
                    );


            const escape =
                Utils.escapeHtml
                    ? Utils.escapeHtml
                    : function (value) {
                        return String(value);
                    };


            const formatDuration =
                Utils.formatDuration
                    ? Utils.formatDuration
                    : function (value) {
                        return String(value);
                    };


            return `
                <div class="conversion-info">

                    <div class="conversion-info-title">
                        【${escape(type)}変換】
                    </div>

                    <div>
                        タイトル：${escape(title)}
                    </div>

                    <div>
                        再生時間：${escape(
                            formatDuration(duration)
                        )}
                    </div>

                    <div>
                        実行開始：${escape(start)}
                    </div>

                    <div>
                        実行終了：${escape(end)}
                        （${escape(elapsed)}）
                    </div>

                </div>
            `;

        }



        // =====================================
        // ダウンロードURL
        // =====================================

        function makeDownloadUrl(
            filename
        ) {

            if (
                Utils.makeDownloadUrl
            ) {

                return Utils.makeDownloadUrl(
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
        // 完了ファイル解析
        // =====================================

        function parseFiles(
            files
        ) {

            let mp3File = "";

            let mp4File = "";


            if (
                !Array.isArray(files)
            ) {

                return {

                    mp3File:
                        mp3File,

                    mp4File:
                        mp4File

                };

            }


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


            return {

                mp3File:
                    mp3File,

                mp4File:
                    mp4File

            };

        }



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


            data =
                data || {};


            const parsed =
                parseFiles(
                    files
                );


            currentMp3File =
                parsed.mp3File;


            currentMp4File =
                parsed.mp4File;


            // =================================
            // ファイルなし
            // =================================

            if (
                !currentMp3File &&
                !currentMp4File
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
            // Gemini用MP3
            // =================================

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );


            if (geminiFile) {

                geminiFile.value =
                    currentMp3File || "";

            }



            // =================================
            // HTML
            // =================================

            let html = "";



            // =================================
            // MP3
            // =================================

            if (currentMp3File) {

                html += `

                    ${createConversionInfo(
                        "MP3",
                        data
                    )}

                    <div class="download-section">

                        <div class="download-label">
                            MP3のダウンロード
                        </div>

                        <div class="mp3-button-row">

                            <a
                                href="${makeDownloadUrl(
                                    currentMp3File
                                )}"
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

            if (currentMp4File) {

                html += `

                    ${createConversionInfo(
                        "MP4",
                        data
                    )}

                    <div class="download-section">

                        <div class="download-label">
                            MP4のダウンロード
                        </div>

                        <div class="mp4-button-row">

                            <a
                                href="${makeDownloadUrl(
                                    currentMp4File
                                )}"
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

            if (!currentMp3File) {

                if (
                    window.ConverterGemini &&
                    window.ConverterGemini.hideGeminiArea
                ) {

                    window.ConverterGemini.hideGeminiArea();

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

        }



        // =====================================
        // STATUS確認
        // =====================================

        async function checkStatus() {

            if (!currentJobId) {

                return;

            }


            try {

                const response =
                    await fetch(
                        `/status/${encodeURIComponent(
                            currentJobId
                        )}`,
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
                        "HTTP " +
                        response.status +
                        " : " +
                        (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )
                    );

                }



                // =================================
                // JSON取得
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
                // =================================

                if (
                    data.status === "error" &&
                    data.message === "jobなし"
                ) {

                    console.warn(
                        "JOBが存在しません:",
                        currentJobId
                    );


                    /*
                     * ここが重要。
                     *
                     * 変換開始直後に一時的に
                     * JOB情報を取得できない場合が
                     * あるため、即座にエラー終了せず
                     * 少し待って再確認します。
                     */

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
                    data.status ===
                    "complete"
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
                    data.status ===
                    "error"
                ) {

                    stopConvertTimer();


                    if (convertButton) {

                        convertButton.style.display =
                            "";

                        convertButton.disabled =
                            false;

                        convertButton.innerHTML =
                            "実行";

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


                /*
                 * ネットワークエラーや
                 * Renderの一時的な切断では
                 * 変換JOBそのものを終了扱いにしない。
                 */

                setTimeout(
                    checkStatus,
                    5000
                );

            }

        }



        // =====================================
        // グローバル公開
        // =====================================

        window.ConverterStatus = {

            checkStatus:
                checkStatus,

            startConvertTimer:
                startConvertTimer,

            stopConvertTimer:
                stopConvertTimer,

            setJobId:
                setJobId,

            getJobId:
                getJobId,

            setVideoInfo:
                setVideoInfo,

            getVideoTitle:
                getVideoTitle,

            getVideoDuration:
                getVideoDuration,

            setFiles:
                setFiles,

            getMp3File:
                getMp3File,

            getMp4File:
                getMp4File,

            createConversionInfo:
                createConversionInfo,

            showFiles:
                showFiles

        };

    }
);
