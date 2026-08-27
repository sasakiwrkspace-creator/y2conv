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
//
// 役割:
// ・YouTube URL受付
// ・動画情報取得
// ・変換API実行
// ・MP3 / MP4ダウンロード表示
// ・処理詳細表示
// ・converterState管理
//
// 共通処理:
// ・converter-utils.js
//
// ステータス表示:
// ・converter-status.js
// =====================================


(function () {

    "use strict";


    // =====================================
    // Converter初期化
    // =====================================

    function initializeConverterMain() {


        // =================================
        // 二重初期化防止
        // =================================

        if (
            window.converterMain &&
            window.converterMain.__initialized
        ) {

            console.log(
                "[CONVERTER] already initialized"
            );

            return;

        }


        // =================================
        // Utils確認
        // =================================

        const utils =
            window.converterUtils;


        if (!utils) {

            console.error(
                "[CONVERTER] converterUtils がありません"
            );

            return;

        }


        // =================================
        // Status確認
        // =================================

        const status =
            window.converterStatus;


        if (!status) {

            console.error(
                "[CONVERTER] converterStatus がありません"
            );

            return;

        }


        // =====================================
        // Converter State
        // =====================================

        const converterState = {

            // ---------------------------------
            // 動画情報
            // ---------------------------------

            currentVideoTitle:
                "",

            currentVideoDuration:
                "",

            currentVideoUrl:
                "",


            // ---------------------------------
            // 変換ファイル
            // ---------------------------------

            currentMp3File:
                "",

            currentMp4File:
                "",

            currentSrtFile:
                "",

            currentSubtitleEmbedFile:
                "",


            // ---------------------------------
            // 処理状態
            // ---------------------------------

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
        //
        // URL生成はUtilsに集約
        // =====================================

        function makeDownloadUrl(
            filename
        ) {

            return utils.makeDownloadUrl(
                filename
            );

        }



        // =====================================
        // ダウンロードボタン追加
        //
        // converter.jsでは
        // DOMへの追加だけを担当
        // =====================================

        function addDownloadButton(
            filename,
            label
        ) {


            if (
                !filesElement
            ) {

                console.warn(
                    "[CONVERTER] converter-files がありません"
                );

                return;

            }


            if (
                !filename
            ) {

                console.warn(
                    "[CONVERTER] ダウンロードファイル名がありません"
                );

                return;

            }



            // ---------------------------------
            // リンク作成
            // ---------------------------------

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



            // ---------------------------------
            // 追加
            // ---------------------------------

            filesElement.appendChild(
                link
            );


            console.log(
                "[CONVERTER] ダウンロードボタン追加:",
                {
                    filename:
                        filename,

                    label:
                        label
                }
            );

        }



        // =====================================
        // 処理詳細追加
        //
        // HTMLをconverter.js側で
        // 管理する
        // =====================================

        function addConversionInfo(
            html
        ) {


            if (
                !detailElement
            ) {

                console.warn(
                    "[CONVERTER] conversion-details がありません"
                );

                return;

            }


            if (
                !html
            ) {

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
        // SRT情報追加
        //
        // converter-gemini.jsから使用
        // =====================================

        function addSrtInfo(
            html,
            srtFile
        ) {


            // ---------------------------------
            // SRTファイル保存
            // ---------------------------------

            if (
                srtFile
            ) {

                converterState.currentSrtFile =
                    srtFile;

            }


            // ---------------------------------
            // 処理詳細追加
            // ---------------------------------

            addConversionInfo(
                html
            );


            console.log(
                "[CONVERTER] SRT情報を追加:",
                srtFile
            );

        }



        // =====================================
        // 字幕付きMP4追加
        //
        // sub_embed.jsから使用
        // =====================================

        function addSubtitleEmbedFile(
            filename
        ) {


            if (
                !filename
            ) {

                return;

            }


            // ---------------------------------
            // State保存
            // ---------------------------------

            converterState.currentSubtitleEmbedFile =
                filename;


            // ---------------------------------
            // ダウンロードボタン
            // ---------------------------------

            addDownloadButton(

                filename,

                "字幕付きMP4をダウンロード"

            );


            console.log(
                "[CONVERTER] 字幕付きMP4を追加:",
                filename
            );

        }



        // =====================================
        // 字幕付きMP4処理詳細
        //
        // sub_embed.jsから使用
        // =====================================

        function addSubtitleEmbedInfo(
            html
        ) {


            addConversionInfo(
                html
            );


            console.log(
                "[CONVERTER] 字幕付きMP4情報を追加"
            );

        }



        // =====================================
        // 結果クリア
        // =====================================

        function clearResults() {


            // ---------------------------------
            // ダウンロード欄
            // ---------------------------------

            if (
                filesElement
            ) {

                filesElement.innerHTML =
                    "";

            }


            // ---------------------------------
            // 処理詳細
            // ---------------------------------

            if (
                detailElement
            ) {

                detailElement.innerHTML =
                    "";

            }


            // ---------------------------------
            // State
            // ---------------------------------

            converterState.currentMp3File =
                "";

            converterState.currentMp4File =
                "";

            converterState.currentSrtFile =
                "";

            converterState.currentSubtitleEmbedFile =
                "";


            console.log(
                "[CONVERTER] 結果をクリアしました"
            );

        }



        // =====================================
        // 動画情報取得
        // =====================================

        async function getVideoInfo(
            url
        ) {


            console.log(
                "[CONVERTER] 動画情報取得開始:",
                url
            );


            const response =
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



            // ---------------------------------
            // JSON取得
            // ---------------------------------

            const data =
                await response.json();



            // ---------------------------------
            // エラー
            // ---------------------------------

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(

                    data.message ||
                    "動画情報の取得に失敗しました。"

                );

            }



            console.log(
                "[CONVERTER] 動画情報取得完了:",
                data
            );


            return data;

        }



        // =====================================
        // 変換API
        // =====================================

        async function convertVideo(
            url,
            outputs,
            timeRange
        ) {


            console.log(
                "[CONVERTER] 変換開始:",
                {
                    url:
                        url,

                    outputs:
                        outputs,

                    timeRange:
                        timeRange
                }
            );


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
                                    timeRange

                            })

                    }
                );



            // ---------------------------------
            // JSON
            // ---------------------------------

            const data =
                await response.json();



            // ---------------------------------
            // エラー
            // ---------------------------------

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(

                    data.message ||
                    "変換に失敗しました。"

                );

            }



            console.log(
                "[CONVERTER] 変換完了:",
                data
            );


            return data;

        }



        // =====================================
        // MP3結果処理
        // =====================================

        function handleMp3Result(
            filename
        ) {


            if (
                !filename
            ) {

                return;

            }


            converterState.currentMp3File =
                filename;


            addDownloadButton(
                filename,
                "mp3"
            );


            console.log(
                "[CONVERTER] MP3:",
                filename
            );

        }



        // =====================================
        // MP4結果処理
        // =====================================

        function handleMp4Result(
            filename
        ) {


            if (
                !filename
            ) {

                return;

            }


            converterState.currentMp4File =
                filename;


            addDownloadButton(
                filename,
                "mp4"
            );


            console.log(
                "[CONVERTER] MP4:",
                filename
            );

        }



        // =====================================
        // 変換処理詳細作成
        // =====================================

        function createConversionInfo(
            startTime,
            endTime
        ) {


            const elapsed =
                Math.max(

                    0,

                    Math.floor(

                        (
                            endTime.getTime() -
                            startTime.getTime()
                        ) / 1000

                    )

                );



            const title =
                converterState.currentVideoTitle ||
                "不明";


            const duration =
                converterState.currentVideoDuration ||
                "不明";



            return `

                <div class="conversion-info">

                    <div class="conversion-info-title">

                        ★変換完了

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

        }



        // =====================================
        // 変換開始
        // =====================================

        async function startConversion() {


            // =================================
            // 二重実行防止
            // =================================

            if (
                converterState.isProcessing
            ) {

                console.warn(
                    "[CONVERTER] 既に変換処理中です"
                );

                return;

            }



            // =================================
            // URL取得
            // =================================

            const url =
                urlInput
                    ? urlInput.value.trim()
                    : "";



            // =================================
            // URL確認
            // =================================

            if (
                !url
            ) {

                status.error(
                    "YouTube URLを入力してください。"
                );

                return;

            }



            // =================================
            // 処理開始
            // =================================

            converterState.isProcessing =
                true;


            converterState.currentVideoUrl =
                url;


            clearResults();



            // =================================
            // ボタン無効化
            // =================================

            if (
                convertButton
            ) {

                convertButton.disabled =
                    true;

            }



            // =================================
            // 開始時間
            // =================================

            const startTime =
                new Date();



            console.log(
                "=========================================="
            );


            console.log(
                "[CONVERTER] 変換処理開始"
            );


            console.log(
                "[CONVERTER] 開始:",
                utils.formatClock(
                    startTime
                )
            );


            console.log(
                "[CONVERTER] URL:",
                url
            );


            console.log(
                "=========================================="
            );



            // =================================
            // 初期ステータス
            // =================================

            status.start(
                "動画情報を取得しています..."
            );



            try {


                // =================================
                // STEP 1
                // 動画情報
                // =================================

                const info =
                    await getVideoInfo(
                        url
                    );



                // =================================
                // Stateへ保存
                // =================================

                converterState.currentVideoTitle =
                    info.title ||
                    info.video_title ||
                    "不明";


                converterState.currentVideoDuration =
                    info.duration ||
                    info.video_duration ||
                    "不明";



                console.log(
                    "[CONVERTER] タイトル:",
                    converterState.currentVideoTitle
                );


                console.log(
                    "[CONVERTER] 再生時間:",
                    converterState.currentVideoDuration
                );



                // =================================
                // STEP 2
                // 出力形式
                // =================================

                const outputs =
                    utils.getSelectedOutputs();


                const timeRange =
                    utils.getTimeRange();



                console.log(
                    "[CONVERTER] 出力形式:",
                    outputs
                );


                console.log(
                    "[CONVERTER] 時間範囲:",
                    timeRange
                );



                // =================================
                // ステータス更新
                // =================================

                status.update(
                    "動画を変換しています..."
                );



                // =================================
                // STEP 3
                // 変換
                // =================================

                const data =
                    await convertVideo(

                        url,

                        outputs,

                        timeRange

                    );



                // =================================
                // STEP 4
                // MP3
                // =================================

                handleMp3Result(
                    data.mp3_file
                );



                // =================================
                // STEP 5
                // MP4
                // =================================

                handleMp4Result(
                    data.mp4_file
                );



                // =================================
                // STEP 6
                // 終了時間
                // =================================

                const endTime =
                    new Date();



                // =================================
                // STEP 7
                // 処理詳細
                // =================================

                const detailHtml =
                    createConversionInfo(

                        startTime,

                        endTime

                    );


                addConversionInfo(
                    detailHtml
                );



                // =================================
                // STEP 8
                // 完了ステータス
                // =================================

                status.success(
                    "変換が完了しました。"
                );



                // =================================
                // 完了ログ
                // =================================

                const elapsed =
                    Math.max(

                        0,

                        Math.floor(

                            (
                                endTime.getTime() -
                                startTime.getTime()
                            ) / 1000

                        )

                    );


                console.log(
                    "=========================================="
                );


                console.log(
                    "[CONVERTER] 変換処理完了"
                );


                console.log(
                    "[CONVERTER] 開始:",
                    utils.formatClock(
                        startTime
                    )
                );


                console.log(
                    "[CONVERTER] 終了:",
                    utils.formatClock(
                        endTime
                    )
                );


                console.log(
                    "[CONVERTER] 処理時間:",
                    utils.formatElapsed(
                        elapsed
                    )
                );


                console.log(
                    "[CONVERTER] MP3:",
                    converterState.currentMp3File
                );


                console.log(
                    "[CONVERTER] MP4:",
                    converterState.currentMp4File
                );


                console.log(
                    "=========================================="
                );

            }
            catch (
                error
            ) {


                // =================================
                // エラー
                // =================================

                console.error(
                    "[CONVERTER] エラー:",
                    error
                );


                const message =
                    (
                        error &&
                        error.message
                    )
                        ? error.message
                        : "不明なエラー";



                status.error(

                    "変換中にエラーが発生しました。\n" +
                    message

                );

            }
            finally {


                // =================================
                // 処理状態解除
                // =================================

                converterState.isProcessing =
                    false;



                // =================================
                // ボタン復帰
                // =================================

                if (
                    convertButton
                ) {

                    convertButton.disabled =
                        false;

                }

            }

        }



        // =====================================
        // 変換ボタン
        // =====================================

        if (
            convertButton
        ) {

            convertButton.addEventListener(
                "click",
                startConversion
            );


            console.log(
                "[CONVERTER] convert-button 初期化完了"
            );

        }
        else {

            console.warn(
                "[CONVERTER] convert-button がありません"
            );

        }



        // =====================================
        // 公開API
        // =====================================

        const main = {

            // ---------------------------------
            // 初期化済み
            // ---------------------------------

            __initialized:
                true,


            // ---------------------------------
            // メイン処理
            // ---------------------------------

            start:
                startConversion,


            // ---------------------------------
            // SRT
            // ---------------------------------

            addSrtInfo:
                addSrtInfo,


            // ---------------------------------
            // 字幕付きMP4
            // ---------------------------------

            addSubtitleEmbedFile:
                addSubtitleEmbedFile,


            addSubtitleEmbedInfo:
                addSubtitleEmbedInfo,


            // ---------------------------------
            // 処理詳細
            // ---------------------------------

            addConversionInfo:
                addConversionInfo,


            // ---------------------------------
            // 結果クリア
            // ---------------------------------

            clearResults:
                clearResults,


            // ---------------------------------
            // State取得
            // ---------------------------------

            getState:
                function () {

                    return converterState;

                }

        };



        // =====================================
        // グローバル公開
        // =====================================

        window.converterMain =
            main;


        window.ConverterMain =
            main;



        // =====================================
        // 読み込み確認
        // =====================================

        console.log(
            "======================================"
        );


        console.log(
            "converter.js loaded"
        );


        console.log(
            "[CONVERTER] converterUtils:",
            window.converterUtils
        );


        console.log(
            "[CONVERTER] converterStatus:",
            window.converterStatus
        );


        console.log(
            "[CONVERTER] converterState:",
            window.converterState
        );


        console.log(
            "[CONVERTER] start:",
            typeof
                window.converterMain.start
        );


        console.log(
            "[CONVERTER] addSrtInfo:",
            typeof
                window.converterMain.addSrtInfo
        );


        console.log(
            "[CONVERTER] addSubtitleEmbedFile:",
            typeof
                window.converterMain.addSubtitleEmbedFile
        );


        console.log(
            "[CONVERTER] addSubtitleEmbedInfo:",
            typeof
                window.converterMain.addSubtitleEmbedInfo
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
