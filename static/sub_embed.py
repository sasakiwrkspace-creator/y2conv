// =====================================
// Subtitle Embed
// sub_embed.js
//
// 第1段階：アップロード動作確認
//
// MP4 / SRTを選択
// ↓
// アップロードボタン
// ↓
// ボタンが押されたことを画面とConsoleに表示
//
// ※この段階ではまだサーバーへのアップロードは行わない
// =====================================

(function () {

    "use strict";


    // =====================================
    // 読み込み確認
    // =====================================

    console.log(
        "[SUB EMBED] sub_embed.js loaded"
    );


    // =====================================
    // DOM読み込み後に初期化
    // =====================================

    function initializeSubEmbed() {

        console.log(
            "[SUB EMBED] initialize start"
        );


        // =================================
        // DOM取得
        // =================================

        const mp4Input =
            document.getElementById(
                "sub-embed-mp4"
            );


        const srtInput =
            document.getElementById(
                "sub-embed-srt"
            );


        const uploadButton =
            document.getElementById(
                "sub-embed-upload-button"
            );


        const statusElement =
            document.getElementById(
                "sub-embed-status"
            );


        const filesElement =
            document.getElementById(
                "sub-embed-files"
            );


        // =================================
        // DOM確認
        // =================================

        console.log(
            "[SUB EMBED] MP4 input:",
            mp4Input
        );


        console.log(
            "[SUB EMBED] SRT input:",
            srtInput
        );


        console.log(
            "[SUB EMBED] upload button:",
            uploadButton
        );


        console.log(
            "[SUB EMBED] status:",
            statusElement
        );


        console.log(
            "[SUB EMBED] files:",
            filesElement
        );


        // =================================
        // アップロードボタン確認
        // =================================

        if (!uploadButton) {

            console.error(
                "[SUB EMBED] アップロードボタンが見つかりません"
            );

            if (statusElement) {

                statusElement.textContent =
                    "エラー：アップロードボタンが見つかりません。";

            }

            return;
        }


        // =================================
        // アップロードボタン
        // =================================

        uploadButton.addEventListener(
            "click",
            function () {

                console.log(
                    "[SUB EMBED] アップロードボタンが押されました"
                );


                // =============================
                // 画面に確認メッセージ
                // =============================

                if (statusElement) {

                    statusElement.textContent =
                        "アップロードボタンが押されました";

                }


                // =============================
                // MP4確認
                // =============================

                let mp4File = null;


                if (
                    mp4Input &&
                    mp4Input.files &&
                    mp4Input.files.length > 0
                ) {

                    mp4File =
                        mp4Input.files[0];

                }


                // =============================
                // SRT確認
                // =============================

                let srtFile = null;


                if (
                    srtInput &&
                    srtInput.files &&
                    srtInput.files.length > 0
                ) {

                    srtFile =
                        srtInput.files[0];

                }


                // =============================
                // 選択ファイルConsole表示
                // =============================

                console.log(
                    "[SUB EMBED] MP4:",
                    mp4File
                );


                console.log(
                    "[SUB EMBED] SRT:",
                    srtFile
                );


                // =============================
                // ファイル選択状態を画面表示
                // =============================

                let message =
                    "アップロードボタンが押されました";


                if (mp4File) {

                    message +=
                        "\nMP4: " +
                        mp4File.name;

                } else {

                    message +=
                        "\nMP4: 未選択";

                }


                if (srtFile) {

                    message +=
                        "\nSRT: " +
                        srtFile.name;

                } else {

                    message +=
                        "\nSRT: 未選択";

                }


                if (statusElement) {

                    statusElement.textContent =
                        message;

                }


                // =============================
                // ファイル一覧表示
                // =============================

                if (filesElement) {

                    filesElement.innerHTML = "";


                    if (mp4File) {

                        const mp4Info =
                            document.createElement(
                                "div"
                            );


                        mp4Info.textContent =
                            "MP4: " +
                            mp4File.name;


                        filesElement.appendChild(
                            mp4Info
                        );

                    }


                    if (srtFile) {

                        const srtInfo =
                            document.createElement(
                                "div"
                            );


                        srtInfo.textContent =
                            "SRT: " +
                            srtFile.name;


                        filesElement.appendChild(
                            srtInfo
                        );

                    }

                }


                // =============================
                // 重要
                //
                // 現段階ではまだ
                // fetch() は実行しない
                //
                // まずボタンイベントが正常に
                // 動作するか確認する。
                // =============================

                console.log(
                    "[SUB EMBED] アップロード処理テスト終了"
                );

            }
        );


        // =================================
        // MP4選択イベント
        // =================================

        if (mp4Input) {

            mp4Input.addEventListener(
                "change",
                function () {

                    if (
                        this.files &&
                        this.files.length > 0
                    ) {

                        console.log(
                            "[SUB EMBED] MP4選択:",
                            this.files[0].name
                        );

                    } else {

                        console.log(
                            "[SUB EMBED] MP4選択解除"
                        );

                    }

                }
            );

        }


        // =================================
        // SRT選択イベント
        // =================================

        if (srtInput) {

            srtInput.addEventListener(
                "change",
                function () {

                    if (
                        this.files &&
                        this.files.length > 0
                    ) {

                        console.log(
                            "[SUB EMBED] SRT選択:",
                            this.files[0].name
                        );

                    } else {

                        console.log(
                            "[SUB EMBED] SRT選択解除"
                        );

                    }

                }
            );

        }


        // =================================
        // 初期化完了
        // =================================

        console.log(
            "[SUB EMBED] initialize complete"
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
            initializeSubEmbed
        );

    } else {

        initializeSubEmbed();

    }


})();
