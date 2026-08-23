// =====================================
// Subtitle Embed
// sub_embed.js
//
// 第2段階：サーバーアップロード確認
//
// MP4 / SRTを選択
// ↓
// アップロードボタン
// ↓
// POST /subtitle-upload
// ↓
// downloadsへ保存
//
// ※この段階では字幕焼き込みは行わない
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


        // =====================================
        // ステータス表示
        // =====================================

        function setStatus(message) {

            if (!statusElement) {

                return;

            }


            statusElement.textContent =
                message;


            statusElement.style.whiteSpace =
                "pre-line";

        }


        // =====================================
        // ファイルアップロード
        // =====================================

        async function uploadFile(file, type) {

            console.log(
                "[SUB EMBED] "
                + type
                + " アップロード開始:",
                file.name
            );


            // -------------------------------
            // FormData
            // -------------------------------

            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            // -------------------------------
            // API
            // -------------------------------

            let response;


            try {

                response =
                    await fetch(
                        "/subtitle-upload",
                        {
                            method: "POST",
                            body: formData
                        }
                    );

            } catch (error) {

                console.error(
                    "[SUB EMBED] "
                    + type
                    + " fetchエラー:",
                    error
                );

                throw new Error(
                    type
                    + "のアップロード通信に失敗しました。"
                );

            }


            // -------------------------------
            // JSON
            // -------------------------------

            let result;


            try {

                result =
                    await response.json();

            } catch (error) {

                console.error(
                    "[SUB EMBED] "
                    + type
                    + " JSON解析エラー:",
                    error
                );

                throw new Error(
                    type
                    + "アップロードAPIの応答を解析できませんでした。"
                );

            }


            console.log(
                "[SUB EMBED] "
                + type
                + " API response:",
                result
            );


            // -------------------------------
            // APIエラー
            // -------------------------------

            if (
                !response.ok ||
                !result.success
            ) {

                throw new Error(
                    result.message
                    ||
                    type
                    + "のアップロードに失敗しました。"
                );

            }


            // -------------------------------
            // 成功
            // -------------------------------

            console.log(
                "[SUB EMBED] "
                + type
                + " アップロード成功:",
                result.filename
            );


            return result;

        }


        // =====================================
        // アップロードボタン
        // =====================================

        uploadButton.addEventListener(
            "click",
            async function (event) {

                // =================================
                // デフォルト動作停止
                // =================================

                event.preventDefault();


                console.log(
                    "[SUB EMBED] "
                    + "アップロードボタンがクリックされました"
                );


                // =================================
                // 前回表示をクリア
                // =================================

                if (statusElement) {

                    statusElement.textContent =
                        "";

                }


                if (filesElement) {

                    filesElement.innerHTML =
                        "";

                }


                // =================================
                // ファイル取得
                // =================================

                let mp4File = null;

                let srtFile = null;


                if (
                    mp4Input &&
                    mp4Input.files &&
                    mp4Input.files.length > 0
                ) {

                    mp4File =
                        mp4Input.files[0];

                }


                if (
                    srtInput &&
                    srtInput.files &&
                    srtInput.files.length > 0
                ) {

                    srtFile =
                        srtInput.files[0];

                }


                // =================================
                // Console
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
                // 未選択確認
                // =================================

                if (!mp4File) {

                    setStatus(
                        "MP4ファイルを選択してください。"
                    );

                    console.warn(
                        "[SUB EMBED] "
                        + "MP4ファイルが選択されていません"
                    );

                    return;
                }


                if (!srtFile) {

                    setStatus(
                        "SRTファイルを選択してください。"
                    );

                    console.warn(
                        "[SUB EMBED] "
                        + "SRTファイルが選択されていません"
                    );

                    return;
                }


                // =================================
                // ボタン無効化
                // =================================

                uploadButton.disabled =
                    true;


                const originalText =
                    uploadButton.textContent;


                uploadButton.textContent =
                    "アップロード中...";


                try {

                    // =================================
                    // 開始表示
                    // =================================

                    setStatus(
                        "ファイルをアップロードしています..."
                    );


                    // =================================
                    // MP4アップロード
                    // =================================

                    setStatus(
                        "MP4をアップロードしています..."
                    );


                    const mp4Result =
                        await uploadFile(
                            mp4File,
                            "MP4"
                        );


                    // =================================
                    // SRTアップロード
                    // =================================

                    setStatus(
                        "SRTをアップロードしています..."
                    );


                    const srtResult =
                        await uploadFile(
                            srtFile,
                            "SRT"
                        );


                    // =================================
                    // 成功
                    // =================================

                    setStatus(
                        "アップロード完了しました。\n\n"
                        + "MP4: "
                        + mp4Result.filename
                        + "\n"
                        + "SRT: "
                        + srtResult.filename
                    );


                    // =================================
                    // ファイル一覧
                    // =================================

                    if (filesElement) {

                        filesElement.innerHTML =
                            "";


                        // -----------------------------
                        // MP4
                        // -----------------------------

                        const mp4Info =
                            document.createElement(
                                "div"
                            );


                        mp4Info.textContent =
                            "MP4: "
                            + mp4Result.filename
                            + " ("
                            + mp4Result.size
                            + " bytes)";


                        filesElement.appendChild(
                            mp4Info
                        );


                        // -----------------------------
                        // SRT
                        // -----------------------------

                        const srtInfo =
                            document.createElement(
                                "div"
                            );


                        srtInfo.textContent =
                            "SRT: "
                            + srtResult.filename
                            + " ("
                            + srtResult.size
                            + " bytes)";


                        filesElement.appendChild(
                            srtInfo
                        );

                    }


                    console.log(
                        "[SUB EMBED] "
                        + "MP4/SRTアップロード完了"
                    );


                    console.log(
                        "[SUB EMBED] MP4:",
                        mp4Result
                    );


                    console.log(
                        "[SUB EMBED] SRT:",
                        srtResult
                    );


                } catch (error) {

                    // =================================
                    // エラー
                    // =================================

                    console.error(
                        "[SUB EMBED] "
                        + "アップロードエラー:",
                        error
                    );


                    setStatus(
                        "アップロードに失敗しました。\n\n"
                        + error.message
                    );

                } finally {

                    // =================================
                    // ボタン復帰
                    // =================================

                    uploadButton.disabled =
                        false;


                    uploadButton.textContent =
                        originalText;

                }

            }
        );


        // =====================================
        // MP4選択イベント
        // =====================================

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
                            "[SUB EMBED] MP4選択:",
                            file.name
                        );


                        setStatus(
                            "MP4を選択しました。\n"
                            + file.name
                        );

                    }

                }
            );

        }


        // =====================================
        // SRT選択イベント
        // =====================================

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
                            "[SUB EMBED] SRT選択:",
                            file.name
                        );

                    }

                }
            );

        }


        // =====================================
        // 初期化完了
        // =====================================

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
