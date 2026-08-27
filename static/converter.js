// =====================================
// YouTube Converter - Main
// converter.js
//
// メイン変換処理を担当
//
// 使用:
// ・converter-utils.js
// ・converter-status.js
// ・converter-gemini.js
// ・sub_embed.js
// =====================================

(function () {

    "use strict";


    // =====================================
    // 初期化
    // =====================================

    function initializeConverterMain() {

        if (
            window.converterMain &&
            window.converterMain.__initialized
        ) {

            console.log(
                "[CONVERTER] already initialized"
            );

            return;

        }


        // =====================================
        // 共通関数
        // =====================================

        const utils =
            window.converterUtils;


        if (!utils) {

            console.error(
                "[CONVERTER] converterUtils がありません"
            );

            return;

        }


        // =====================================
        // Status
        // =====================================

        const status =
            window.converterStatus;


        if (!status) {

            console.error(
                "[CONVERTER] converterStatus がありません"
            );

            return;

        }


        // =====================================
        // State
        // =====================================

        const converterState = {

            currentVideoTitle:
                "",

            currentVideoDuration:
                "",

            currentVideoUrl:
                "",

            currentMp3File:
                "",

            currentMp4File:
                "",

            currentSrtFile:
                "",

            currentSubtitleEmbedFile:
                "",

            isProcessing:
                false

        };


        window.converterState =
            converterState;


        // =====================================
        // DOM
        // =====================================

        const urlInput =
            document.getElementById(
                "youtube-url"
            );


        const convertButton =
            document.getElementById(
                "convert-button"
            );


        const filesElement =
            document.getElementById(
                "converter-files"
            );


        const detailElement =
            document.getElementById(
                "conversion-details"
            );


        // =====================================
        // ダウンロードURL
        // =====================================

        function makeDownloadUrl(
            filename
        ) {

            return utils.makeDownloadUrl(
                filename
            );

        }


        // =====================================
        // ダウンロードボタン
        // =====================================

        function addDownloadButton(
            filename,
            label
        ) {

            if (
                !filesElement ||
                !filename
            ) {

                return;

            }


            const link =
                document.createElement(
                    "a"
                );


            link.href =
                makeDownloadUrl(
                    filename
                );


            link.download =
                filename;


            link.className =
                "download-button";


            link.textContent =
                label;


            filesElement.appendChild(
                link
            );

        }


        // =====================================
        // 処理詳細
        // =====================================

        function addConversionInfo(
            html
        ) {

            if (!detailElement) {
                return;
            }


            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.innerHTML =
                html;


            detailElement.appendChild(
                wrapper
            );

        }


        // =====================================
        // SRT情報
        // =====================================

        function addSrtInfo(
            html,
            srtFile
        ) {

            if (srtFile) {

                converterState.currentSrtFile =
                    srtFile;

            }


            addConversionInfo(
                html
            );

        }


        // =====================================
        // 字幕付きMP4
        // =====================================

        function addSubtitleEmbedFile(
            filename
        ) {

            if (!filename) {
                return;
            }


            converterState.currentSubtitleEmbedFile =
                filename;


            addDownloadButton(
                filename,
                "字幕付きMP4をダウンロード"
            );

        }


        // =====================================
        // 字幕付きMP4詳細
        // =====================================

        function addSubtitleEmbedInfo(
            html
        ) {

            addConversionInfo(
                html
            );

        }


        // =====================================
        // 結果クリア
        // =====================================

        function clearResults() {

            if (filesElement) {

                filesElement.innerHTML =
                    "";

            }


            if (detailElement) {

                detailElement.innerHTML =
                    "";

            }


            converterState.currentMp3File =
                "";

            converterState.currentMp4File =
                "";

            converterState.currentSrtFile =
                "";

            converterState.currentSubtitleEmbedFile =
                "";

        }


        // =====================================
        // 変換開始
        // =====================================

        async function startConversion() {

            if (
                converterState.isProcessing
            ) {

                return;

            }


            const url =
                urlInput
                    ? urlInput.value.trim()
                    : "";


            if (!url) {

                status.error(
                    "YouTube URLを入力してください。"
                );

                return;

            }


            converterState.isProcessing =
                true;


            clearResults();


            if (convertButton) {

                convertButton.disabled =
                    true;

            }


            converterState.currentVideoUrl =
                url;


            status.start(
                "動画情報を取得しています..."
            );


            const startTime =
                new Date();


            try {

                // =================================
                // ここで既存の動画情報APIを呼ぶ
                // =================================

                const infoResponse =
                    await fetch(
                        "/video-info",
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
                                        url

                                })

                        }
                    );


                const info =
                    await infoResponse.json();


                if (
                    !infoResponse.ok ||
                    !info.success
                ) {

                    throw new Error(

                        info.message ||
                        "動画情報の取得に失敗しました。"

                    );

                }


                converterState.currentVideoTitle =
                    info.title ||
                    info.video_title ||
                    "不明";


                converterState.currentVideoDuration =
                    info.duration ||
                    info.video_duration ||
                    "不明";


                // =================================
                // 出力形式
                // =================================

                const outputs =
                    utils.getSelectedOutputs();


                status.update(
                    "動画を変換しています..."
                );


                // =================================
                // 既存の変換APIをここへ
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

                                    time_range:
                                        utils.getTimeRange()

                                })

                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok ||
                    !data.success
                ) {

                    throw new Error(

                        data.message ||
                        "変換に失敗しました。"

                    );

                }


                // =================================
                // ファイル
                // =================================

                if (
                    data.mp3_file
                ) {

                    converterState.currentMp3File =
                        data.mp3_file;


                    addDownloadButton(
                        data.mp3_file,
                        "mp3"
                    );

                }


                if (
                    data.mp4_file
                ) {

                    converterState.currentMp4File =
                        data.mp4_file;


                    addDownloadButton(
                        data.mp4_file,
                        "mp4"
                    );

                }


                // =================================
                // 処理詳細
                // =================================

                const endTime =
                    new Date();


                const elapsed =
                    Math.floor(
                        (
                            endTime.getTime() -
                            startTime.getTime()
                        ) / 1000
                    );


                const detailHtml = `

                    <div class="conversion-info">

                        <div class="conversion-info-title">

                            ★変換完了

                        </div>

                        <div>

                            タイトル：
                            ${utils.escapeHtml(
                                converterState.currentVideoTitle
                            )}

                        </div>

                        <div>

                            再生時間：
                            ${utils.escapeHtml(
                                utils.formatDuration(
                                    converterState.currentVideoDuration
                                )
                            )}

                        </div>

                        <div>

                            実行開始：
                            ${utils.escapeHtml(
                                utils.formatClock(
                                    startTime
                                )
                            )}

                        </div>

                        <div>

                            実行終了：
                            ${utils.escapeHtml(
                                utils.formatClock(
                                    endTime
                                )
                            )}

                            （${utils.escapeHtml(
                                utils.formatElapsed(
                                    elapsed
                                )
                            )}）

                        </div>

                    </div>

                `;


                addConversionInfo(
                    detailHtml
                );


                status.success(
                    "変換が完了しました。"
                );

            }
            catch (error) {

                console.error(
                    "[CONVERTER] エラー:",
                    error
                );


                status.error(

                    "変換中にエラーが発生しました。\n" +
                    (
                        error &&
                        error.message
                            ? error.message
                            : "不明なエラー"
                    )

                );

            }
            finally {

                converterState.isProcessing =
                    false;


                if (convertButton) {

                    convertButton.disabled =
                        false;

                }

            }

        }


        // =====================================
        // ボタン
        // =====================================

        if (convertButton) {

            convertButton.addEventListener(
                "click",
                startConversion
            );

        }


        // =====================================
        // 公開API
        // =====================================

        const main = {

            __initialized:
                true,

            start:
                startConversion,

            addSrtInfo:
                addSrtInfo,

            addSubtitleEmbedFile:
                addSubtitleEmbedFile,

            addSubtitleEmbedInfo:
                addSubtitleEmbedInfo,

            addConversionInfo:
                addConversionInfo,

            clearResults:
                clearResults,

            getState:
                function () {
                    return converterState;
                }

        };


        window.converterMain =
            main;


        window.ConverterMain =
            main;


        console.log(
            "[CONVERTER] converter.js loaded"
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
            initializeConverterMain,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeConverterMain();

    }

})();
