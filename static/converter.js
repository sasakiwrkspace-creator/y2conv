// =====================================
// YouTube Converter - Main
// converter.js
//
// タブ1：YouTube変換
//
// 役割:
// ・YouTube URL受付
// ・動画情報取得
// ・変換API実行
// ・MP3 / MP4ダウンロード表示
// ・処理詳細表示
// ・converterState管理
//
// 注意:
// ・タブ1ではMP4/SRTファイルをアップロードしない
// ・タブ1の実行ボタンは #convertBtn
// ・タブ2のアップロード処理は sub_embed.js が担当
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
    // Converter初期化
    // =====================================

    function initializeConverterMain() {

        console.log(
            "[CONVERTER] initializeConverterMain() start"
        );


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

        // -------------------------------------
        // タブ1：YouTube URL
        // -------------------------------------

        const urlInput =
            document.getElementById(
                "youtube-url"
            );


        // -------------------------------------
        // タブ1：実行ボタン
        //
        // HTMLでは id="convertBtn"
        // -------------------------------------

        const convertButton =
            document.getElementById(
                "convertBtn"
            );


        // -------------------------------------
        // タブ1：ステータス
        // -------------------------------------

        const statusElement =
            document.getElementById(
                "status"
            );


        // -------------------------------------
        // タブ1：途中経過
        // -------------------------------------

        const conversionStatusArea =
            document.getElementById(
                "conversion-status-area"
            );


        // -------------------------------------
        // タブ1：ダウンロード
        //
        // HTMLでは downloadArea
        // -------------------------------------

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );


        // -------------------------------------
        // タブ1：字幕MP4エリア
        // -------------------------------------

        const subtitleMp4Area =
            document.getElementById(
                "subtitle-mp4-area"
            );


        const subtitleMp4Info =
            document.getElementById(
                "subtitle-mp4-info"
            );


        const subtitleMp4DownloadContainer =
            document.getElementById(
                "subtitle-mp4-download-container"
            );


        // -------------------------------------
        // デバッグ
        // -------------------------------------

        console.log(
            "[CONVERTER] urlInput =",
            urlInput
        );


        console.log(
            "[CONVERTER] convertButton =",
            convertButton
        );


        console.log(
            "[CONVERTER] statusElement =",
            statusElement
        );


        console.log(
            "[CONVERTER] conversionStatusArea =",
            conversionStatusArea
        );


        console.log(
            "[CONVERTER] downloadArea =",
            downloadArea
        );


        console.log(
            "[CONVERTER] subtitleMp4Area =",
            subtitleMp4Area
        );


        // =====================================
        // 必須DOM確認
        // =====================================

        if (!urlInput) {

            console.error(
                "[CONVERTER] " +
                "youtube-url が見つかりません"
            );

        }


        if (!convertButton) {

            console.error(
                "[CONVERTER] " +
                "convertBtn が見つかりません"
            );

        }


        // =====================================
        // ダウンロードURL
        // =====================================

        function makeDownloadUrl(
            filename
        ) {

            if (!filename) {

                return "";

            }


            if (
                utils &&
                typeof utils.makeDownloadUrl ===
                    "function"
            ) {

                return utils.makeDownloadUrl(
                    filename
                );

            }


            return (
                "/download/" +
                encodeURIComponent(
                    String(filename)
                )
            );

        }



        // =====================================
        // ダウンロードボタン追加
        // =====================================

        function addDownloadButton(
            filename,
            label
        ) {

            if (!downloadArea) {

                console.warn(
                    "[CONVERTER] " +
                    "downloadArea がありません"
                );

                return;

            }


            if (!filename) {

                console.warn(
                    "[CONVERTER] " +
                    "ダウンロードファイル名がありません"
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

            downloadArea.appendChild(
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
        // =====================================

        function addConversionInfo(
            html
        ) {

            if (!html) {

                return;

            }


            // ---------------------------------
            // 既存のHTML構造に対応
            //
            // conversion-details は
            // 現在のHTMLには存在しないため、
            // downloadAreaへ追加する。
            // ---------------------------------

            if (!downloadArea) {

                console.warn(
                    "[CONVERTER] " +
                    "downloadArea がありません"
                );

                return;

            }


            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "converter-conversion-info-wrapper";


            wrapper.innerHTML =
                html;


            downloadArea.appendChild(
                wrapper
            );


            console.log(
                "[CONVERTER] 処理詳細を追加しました"
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

            if (srtFile) {

                converterState.currentSrtFile =
                    srtFile;

            }


            // ---------------------------------
            // 処理詳細
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

            if (!filename) {

                return;

            }


            // ---------------------------------
            // State保存
            // ---------------------------------

            converterState.currentSubtitleEmbedFile =
                filename;


            // ---------------------------------
            // タブ1側には
            // 字幕付きMP4を追加表示
            // ---------------------------------

            addSubtitleMp4DownloadButton(
                filename
            );


            console.log(
                "[CONVERTER] " +
                "字幕付きMP4を追加:",
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

            if (!html) {

                return;

            }


            // ---------------------------------
            // 字幕MP4専用エリア
            // ---------------------------------

            if (subtitleMp4Info) {

                subtitleMp4Info.innerHTML =
                    html;

                if (subtitleMp4Area) {

                    subtitleMp4Area.style.display =
                        "block";

                }

            }
            else {

                // ---------------------------------
                // 念のため通常エリアへ
                // ---------------------------------

                addConversionInfo(
                    html
                );

            }


            console.log(
                "[CONVERTER] " +
                "字幕付きMP4情報を追加"
            );

        }



        // =====================================
        // 字幕付きMP4ダウンロードボタン
        // =====================================

        function addSubtitleMp4DownloadButton(
            filename
        ) {

            if (!filename) {

                return;

            }


            if (
                !subtitleMp4DownloadContainer
            ) {

                console.warn(
                    "[CONVERTER] " +
                    "subtitleMp4DownloadContainer がありません"
                );

                return;

            }


            // ---------------------------------
            // 既存ボタン削除
            // ---------------------------------

            subtitleMp4DownloadContainer.innerHTML =
                "";


            // ---------------------------------
            // URL
            // ---------------------------------

            const downloadUrl =
                makeDownloadUrl(
                    filename
                );


            // ---------------------------------
            // ボタン
            // ---------------------------------

            const link =
                document.createElement(
                    "a"
                );


            link.href =
                downloadUrl;


            link.download =
                filename;


            link.className =
                "download-button subtitle-mp4-download-button";


            link.textContent =
                "字幕付きMP4をダウンロード";


            subtitleMp4DownloadContainer.appendChild(
                link
            );


            // ---------------------------------
            // エリア表示
            // ---------------------------------

            if (subtitleMp4Area) {

                subtitleMp4Area.style.display =
                    "block";

            }


            console.log(
                "[CONVERTER] " +
                "字幕付きMP4ダウンロードボタン追加:",
                filename
            );

        }



        // =====================================
        // 結果クリア
        // =====================================

        function clearResults() {

            // ---------------------------------
            // ダウンロード欄
            // ---------------------------------

            if (downloadArea) {

                downloadArea.innerHTML =
                    "";

            }


            // ---------------------------------
            // 字幕MP4
            // ---------------------------------

            if (subtitleMp4Info) {

                subtitleMp4Info.innerHTML =
                    "";

            }


            if (
                subtitleMp4DownloadContainer
            ) {

                subtitleMp4DownloadContainer.innerHTML =
                    "";

            }


            if (subtitleMp4Area) {

                subtitleMp4Area.style.display =
                    "none";

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
        // ステータス補助
        // =====================================

        function setStatusText(
            message,
            type
        ) {

            // ---------------------------------
            // converter-status.jsを優先
            // ---------------------------------

            if (type === "error") {

                if (
                    status &&
                    typeof status.error ===
                        "function"
                ) {

                    status.error(
                        message
                    );

                    return;

                }

            }


            if (type === "success") {

                if (
                    status &&
                    typeof status.success ===
                        "function"
                ) {

                    status.success(
                        message
                    );

                    return;

                }

            }


            if (
                status &&
                typeof status.update ===
                    "function"
            ) {

                status.update(
                    message
                );

                return;

            }


            // ---------------------------------
            // fallback
            // ---------------------------------

            if (statusElement) {

                statusElement.textContent =
                    message;

            }

        }



        // =====================================
        // 途中経過表示
        // =====================================

        function setConversionProgress(
            message
        ) {

            if (
                conversionStatusArea
            ) {

                conversionStatusArea.style.display =
                    "block";


                conversionStatusArea.textContent =
                    message;


                conversionStatusArea.style.whiteSpace =
                    "pre-line";

            }


            setStatusText(
                message
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


            let data;


            try {

                data =
                    await response.json();

            }
            catch (error) {

                throw new Error(
                    "動画情報APIからJSONを取得できませんでした。"
                );

            }


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


            let data;


            try {

                data =
                    await response.json();

            }
            catch (error) {

                throw new Error(
                    "変換APIからJSONを取得できませんでした。"
                );

            }


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

            if (!filename) {

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

            if (!filename) {

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
        //
        // ★タブ1のメイン関数
        // =====================================

        async function startConversion() {

            console.log(
                "[CONVERTER] startConversion() called"
            );


            // =================================
            // 二重実行防止
            // =================================

            if (
                converterState.isProcessing
            ) {

                console.warn(
                    "[CONVERTER] " +
                    "既に変換処理中です"
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

            if (!url) {

                setStatusText(
                    "YouTube URLを入力してください。",
                    "error"
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

            if (convertButton) {

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
                "[CONVERTER] YouTube変換処理開始"
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

            setConversionProgress(
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
                // STEP 3
                // 変換
                // =================================

                setConversionProgress(
                    "動画を変換しています..."
                );


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
                // 完了
                // =================================

                setStatusText(
                    "変換が完了しました。",
                    "success"
                );


                if (
                    conversionStatusArea
                ) {

                    conversionStatusArea.textContent =
                        "変換が完了しました。";

                }


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


                setStatusText(

                    "変換中にエラーが発生しました。\n" +
                    message,

                    "error"

                );


                if (
                    conversionStatusArea
                ) {

                    conversionStatusArea.textContent =
                        "変換中にエラーが発生しました。\n" +
                        message;

                }

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

                if (convertButton) {

                    convertButton.disabled =
                        false;

                }


                console.log(
                    "[CONVERTER] startConversion() finished"
                );

            }

        }



        // =====================================
        // タブ1：変換ボタン
        //
        // ★重要
        //
        // HTML:
        // id="convertBtn"
        //
        // タブ2:
        // id="sub-embed-upload-button"
        //
        // 完全に別のイベント
        // =====================================

        if (convertButton) {

            convertButton.addEventListener(
                "click",
                startConversion
            );


            console.log(
                "[CONVERTER] ====================================="
            );


            console.log(
                "[CONVERTER] convertBtn 初期化完了"
            );


            console.log(
                "[CONVERTER] " +
                "YouTube変換ボタンのクリック待機中"
            );


            console.log(
                "[CONVERTER] ====================================="
            );

        }
        else {

            console.error(
                "[CONVERTER] " +
                "convertBtn がありません"
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
            // タブ1メイン処理
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
            "[CONVERTER] converter.js loaded"
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
