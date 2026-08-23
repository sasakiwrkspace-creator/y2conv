// =====================================
// Subtitle Embed
// sub_embed.js
//
// 第1段階：アップロードボタン動作確認
//
// MP4 / SRTを選択
// ↓
// アップロードボタン
// ↓
// 画面に確認メッセージ表示
//
// ※この段階ではサーバーへのアップロードは行わない
// =====================================

(function () {

    "use strict";


    // =====================================
    // 読み込み確認
    // =====================================

    console.log(
        "[SUB EMBED] ====================================="
    );

    console.log(
        "[SUB EMBED] sub_embed.js loaded"
    );

    console.log(
        "[SUB EMBED] ====================================="
    );


    // =====================================
    // 初期化
    // =====================================

    function initializeSubEmbed() {

        console.log(
            "[SUB EMBED] initializeSubEmbed() start"
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
            "[SUB EMBED] mp4Input =",
            mp4Input
        );


        console.log(
            "[SUB EMBED] srtInput =",
            srtInput
        );


        console.log(
            "[SUB EMBED] uploadButton =",
            uploadButton
        );


        console.log(
            "[SUB EMBED] statusElement =",
            statusElement
        );


        console.log(
            "[SUB EMBED] filesElement =",
            filesElement
        );


        // =================================
        // 必須DOM確認
        // =================================

        if (!uploadButton) {

            console.error(
                "[SUB EMBED] ERROR: "
                + "sub-embed-upload-button が見つかりません"
            );


            if (statusElement) {

                statusElement.textContent =
                    "エラー：アップロードボタンが見つかりません。";

            }


            return;
        }


        // =================================
        // 既にイベント登録済みか確認
        //
        // 二重登録防止
        // =================================

        if (
            uploadButton.dataset.subEmbedInitialized ===
            "true"
        ) {

            console.log(
                "[SUB EMBED] "
                + "アップロードボタンは既に初期化済みです"
            );

            return;
        }


        uploadButton.dataset.subEmbedInitialized =
            "true";


        // =================================
        // アップロードボタン
        // =================================

        uploadButton.addEventListener(
            "click",
            function (event) {

                // =================================
                // 前回の表示をクリア
                // =================================
                
                if (statusElement) {
                
                    statusElement.textContent = "";
                
                }
                
                
                if (filesElement) {
                
                    filesElement.innerHTML = "";
                
                }
                
                console.log(
                    "[SUB EMBED] "
                    + "アップロードボタンがクリックされました"
                );


                // =================================
                // デフォルト動作停止
                // =================================

                event.preventDefault();


                // =================================
                // MP4取得
                // =================================

                let mp4File = null;


                if (
                    mp4Input &&
                    mp4Input.files &&
                    mp4Input.files.length > 0
                ) {

                    mp4File =
                        mp4Input.files[0];

                }


                // =================================
                // SRT取得
                // =================================

                let srtFile = null;


                if (
                    srtInput &&
                    srtInput.files &&
                    srtInput.files.length > 0
                ) {

                    srtFile =
                        srtInput.files[0];

                }


                // =================================
                // Console表示
                // =================================

                console.log(
                    "[SUB EMBED] MP4:",
                    mp4File
                );


                console.log(
                    "[SUB EMBED] SRT:",
                    srtFile
                );


                // =================================
                // ファイル未選択確認
                // =================================

                if (!mp4File) {

                    console.warn(
                        "[SUB EMBED] "
                        + "MP4ファイルが選択されていません"
                    );

                }


                if (!srtFile) {

                    console.warn(
                        "[SUB EMBED] "
                        + "SRTファイルが選択されていません"
                    );

                }


                // =================================
                // 確認メッセージ作成
                // =================================

                let message =
                    "アップロードボタンが押されました。";


                message +=
                    "\n";


                message +=
                    "\nMP4: ";


                if (mp4File) {

                    message +=
                        mp4File.name;

                } else {

                    message +=
                        "未選択";

                }


                message +=
                    "\nSRT: ";


                if (srtFile) {

                    message +=
                        srtFile.name;

                } else {

                    message +=
                        "未選択";

                }


                // =================================
                // 画面へ表示
                // =================================

                if (statusElement) {

                    statusElement.textContent =
                        message;


                    // 改行を表示できるようにする
                    statusElement.style.whiteSpace =
                        "pre-line";

                }


                // =================================
                // ファイル一覧表示
                // =================================

                if (filesElement) {

                    filesElement.innerHTML =
                        "";


                    // -----------------------------
                    // MP4
                    // -----------------------------

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


                    // -----------------------------
                    // SRT
                    // -----------------------------

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


                // =================================
                // 処理完了Console
                // =================================

                console.log(
                    "[SUB EMBED] "
                    + "アップロードボタン処理完了"
                );


                console.log(
                    "[SUB EMBED] "
                    + "※現在はサーバーへのアップロードは行いません"
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

                    console.log(
                        "[SUB EMBED] MP4 change"
                    );


                    if (
                        this.files &&
                        this.files.length > 0
                    ) {

                        const file =
                            this.files[0];


                        console.log(
                            "[SUB EMBED] "
                            + "MP4選択:",
                            file.name
                        );


                        if (statusElement) {

                            statusElement.textContent =
                                "MP4を選択しました。\n"
                                +
                                file.name;

                            statusElement.style.whiteSpace =
                                "pre-line";

                        }

                    } else {

                        console.log(
                            "[SUB EMBED] "
                            + "MP4選択解除"
                        );

                    }

                }
            );

        } else {

            console.warn(
                "[SUB EMBED] "
                + "MP4 input が見つかりません"
            );

        }


        // =================================
        // SRT選択イベント
        // =================================

        if (srtInput) {

            srtInput.addEventListener(
                "change",
                function () {

                    console.log(
                        "[SUB EMBED] SRT change"
                    );


                    if (
                        this.files &&
                        this.files.length > 0
                    ) {

                        const file =
                            this.files[0];


                        console.log(
                            "[SUB EMBED] "
                            + "SRT選択:",
                            file.name
                        );


                    } else {

                        console.log(
                            "[SUB EMBED] "
                            + "SRT選択解除"
                        );

                    }

                }
            );

        } else {

            console.warn(
                "[SUB EMBED] "
                + "SRT input が見つかりません"
            );

        }


        // =================================
        // 初期化完了
        // =================================

        console.log(
            "[SUB EMBED] initializeSubEmbed() complete"
        );


        console.log(
            "[SUB EMBED] "
            + "アップロードボタンのクリック待機中"
        );

    }


    // =====================================
    // DOMContentLoaded
    // =====================================

    if (
        document.readyState ===
        "loading"
    ) {

        console.log(
            "[SUB EMBED] "
            + "DOMContentLoaded 待機"
        );


        document.addEventListener(
            "DOMContentLoaded",
            initializeSubEmbed,
            {
                once: true
            }
        );

    } else {

        console.log(
            "[SUB EMBED] "
            + "DOMは既に読み込み済み"
        );


        initializeSubEmbed();

    }


})();
