// =====================================
// YouTube Converter - Gemini
// static/converter-gemini.js
//
// ・Gemini文字起こし
// ・SRTダウンロード
// ・SRT変換情報表示
// ・タイトル / 再生時間は converterState から取得
// ・SRT実行時間を正しく計測
//
// 表示仕様
// ・MP3 / MP4 / SRT のダウンロードボタンは横並び
// ・タイトルはダウンロードボタンの上には表示しない
// ・SRT処理情報は「処理詳細」の中に表示
// ・SRTボタンの追加は converterMain.addSrtInfo()
//   に統一して二重表示を防止
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


            return String(value ?? "")
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


        // =====================================
        // 時計
        // =====================================

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


        // =====================================
        // 経過時間
        // =====================================

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
                Math.max(
                    0,
                    Math.floor(
                        Number(seconds) || 0
                    )
                );


            const minutes =
                Math.floor(
                    totalSeconds / 60
                );


            const remainSeconds =
                totalSeconds % 60;


            if (
                minutes === 0
            ) {

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


        // =====================================
        // 再生時間
        // =====================================

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


            // ---------------------------------
            // HH:MM:SS
            // ---------------------------------

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


                // ---------------------------------
                // MM:SS
                // ---------------------------------

                if (
                    parts.length === 2
                ) {

                    const minutes =
                        parseInt(
                            parts[0],
                            10
                        ) || 0;


                    const seconds =
                        parseInt(
                            parts[1],
                            10
                        ) || 0;


                    const totalSeconds =
                        minutes * 60 +
                        seconds;


                    return formatDuration(
                        totalSeconds
                    );

                }

            }


            // =================================
            // 秒数
            // =================================

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


        // =====================================
        // ダウンロードURL
        // =====================================

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


            // =================================
            // SRT開始時刻
            //
            // Gemini API呼び出し直前に取得
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


            // =================================
            // ボタンチェック
            // =================================

            if (!geminiButton) {

                console.error(
                    "gemini-button が見つかりません"
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


            // =================================
            // 表示用経過秒数
            // =================================

            let seconds = 0;


            // =================================
            // 結果表示
            // =================================

            if (result) {

                result.style.display =
                    "block";


                result.textContent =
                    "文字起こし中... 0秒";

            }


            // =================================
            // 表示用タイマー
            //
            // 実際の処理時間計測には使用しない
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
                // レスポンス取得
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
                // SRT終了時刻
                //
                // APIレスポンスを受け取った時点
                // =================================

                const srtEnd =
                    new Date();


                // =================================
                // 成功
                // =================================

                if (data.success) {


                    // =================================
                    // 実測時間
                    //
                    // setIntervalの秒数ではなく、
                    // 開始～終了の実時間を使用する。
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
                    // サーバー側の秒数
                    //
                    // 比較用としてログだけ残す
                    // =================================

                    const responseSeconds =
                        Number(
                            data.seconds ??
                            data.elapsed_seconds
                        );


                    // =================================
                    // 最終採用時間
                    //
                    // ブラウザ実測時間を採用
                    // =================================

                    const finalSeconds =
                        actualElapsedSeconds;


                    // =================================
                    // 完了ログ
                    // =================================

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
                        "[GEMINI] 実測時間:",
                        actualElapsedSeconds,
                        "秒"
                    );

                    console.log(
                        "[GEMINI] サーバー報告時間:",
                        isNaN(
                            responseSeconds
                        )
                            ? "不明"
                            : responseSeconds +
                              "秒"
                    );

                    console.log(
                        "[GEMINI] 採用時間:",
                        finalSeconds,
                        "秒"
                    );

                    console.log(
                        "[GEMINI] SRT:",
                        data.srt_file ||
                        data.srt ||
                        data.file ||
                        ""
                    );

                    console.log(
                        "=========================================="
                    );


                    // =================================
                    // 結果非表示
                    // =================================

                    if (result) {

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


                // =================================
                // エラーログ
                // =================================

                console.error(
                    "Geminiエラー:",
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

                if (result) {

                    result.style.display =
                        "block";


                    result.textContent =
                        "エラー: "
                        +
                        (
                            error.message ||
                            "文字起こしに失敗しました"
                        );

                }

            }

        }


        // =====================================
        // SRT表示
        //
        // MP3 / MP4の「処理詳細」の中に追加
        //
        // SRTダウンロードボタンは
        // converter.js の addSrtInfo() に
        // 一元管理する。
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


            if (!srtFile) {

                console.error(
                    "SRTファイルがありません:",
                    data
                );

                return;

            }


            // =================================
            // 時刻補正
            // =================================

            if (!srtStart) {

                srtStart =
                    new Date();

            }


            if (!srtEnd) {

                srtEnd =
                    new Date();

            }


            // =================================
            // 実行時間補正
            //
            // 値が渡されなかった場合だけ
            // 開始～終了から計算する。
            // =================================

            if (
                srtSeconds ===
                undefined ||
                srtSeconds ===
                null ||
                isNaN(
                    Number(
                        srtSeconds
                    )
                )
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
            // APIレスポンスを優先し、
            // なければconverterState
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
            //
            // タイトルはここに表示する。
            // ダウンロードボタンの上には
            // 表示しない。
            // =================================

            const srtInfo = `

                <div class="conversion-info srt-conversion-info">

                    <div class="conversion-info-title">

                        ★SRT変換

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
            //
            // ここで
            //
            // ・SRT処理詳細
            // ・SRTダウンロードボタン
            //
            // を一括処理する。
            //
            // これによりGemini側と
            // converter.js側の二重追加を防ぐ。
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


                // =================================
                // converterMainが存在しない場合の
                // 最低限のフォールバック
                // =================================

                const buttonContainer =
                    document.getElementById(
                        "srt-download-button-container"
                    );


                if (
                    buttonContainer
                ) {

                    buttonContainer.innerHTML = `

                        <a
                            href="${escapeHtml(
                                makeDownloadUrl(
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

            }


            // =================================
            // converterStateへ保存
            // =================================

            if (
                window.converterState
            ) {

                window.converterState.currentSrtFile =
                    srtFile;

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
