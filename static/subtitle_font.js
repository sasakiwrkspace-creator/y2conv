// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// タブ2専用
//
// 役割:
// ・字幕フォント選択UI
// ・#subtitle-font-button の操作
// ・選択中プリセットの保持
//
// 重要:
// ・converter.jsには触れない
// ・converterUtils.jsは使用しない
// ・converterStatus.jsには触れない
// ・タブ1のDOMを操作しない
// ・#convertBtnには触れない
// ・subtitle.jsの処理には直接介入しない
//
// subtitle.jsから使用するAPI:
//
//   window.subtitleFont.getPreset()
//
//   window.subtitleFont.setPreset("ゴシック")
//
//   window.subtitleFont.getPresets()
//
// =====================================

(function () {

    "use strict";


    console.log(
        "[SUBTITLE_FONT] subtitle_font.js loaded"
    );


    // =====================================
    // 初期化
    // =====================================

    function initializeSubtitleFont() {

        console.log(
            "[SUBTITLE_FONT] initialize start"
        );


        // ---------------------------------
        // 二重初期化防止
        // ---------------------------------

        if (
            window.subtitleFont &&
            window.subtitleFont.__initialized
        ) {

            console.log(
                "[SUBTITLE_FONT] already initialized"
            );

            return;

        }


        // =====================================
        // DOM
        // =====================================

        const fontButton =
            document.getElementById(
                "subtitle-font-button"
            );


        if (!fontButton) {

            console.warn(
                "[SUBTITLE_FONT] #subtitle-font-button がありません"
            );

            return;

        }


        // =====================================
        // フォントプリセット
        //
        // subtitle_font.py側と
        // 同じ名前を使用する。
        // =====================================

        const FONT_PRESETS = [

            "標準",

            "ゴシック",

            "明朝",

            "太字ゴシック",

            "太字明朝"

        ];


        // =====================================
        // State
        // =====================================

        let selectedPreset =
            "標準";


        // =====================================
        // ボタン表示更新
        // =====================================

        function updateButton() {

            const presetName =
                selectedPreset ||
                "標準";


            fontButton.textContent =
                presetName;


            fontButton.title =
                "字幕フォント: " +
                presetName;

        }


        // =====================================
        // セレクトダイアログ
        //
        // prompt()ではなく、
        // HTMLのselectを使用する。
        //
        // これにより
        // 「ダイアログのセレクトボックス」
        // として確実に選択できる。
        // =====================================

        function selectFontPreset() {

            // ---------------------------------
            // ダイアログ背景
            // ---------------------------------

            const overlay =
                document.createElement(
                    "div"
                );


            overlay.className =
                "subtitle-font-dialog-overlay";


            // ---------------------------------
            // ダイアログ本体
            // ---------------------------------

            const dialog =
                document.createElement(
                    "div"
                );


            dialog.className =
                "subtitle-font-dialog";


            // ---------------------------------
            // タイトル
            // ---------------------------------

            const title =
                document.createElement(
                    "div"
                );


            title.className =
                "subtitle-font-dialog-title";


            title.textContent =
                "字幕フォントを選択";


            // ---------------------------------
            // select
            // ---------------------------------

            const select =
                document.createElement(
                    "select"
                );


            select.className =
                "subtitle-font-select";


            select.name =
                "subtitle-font-preset";


            // ---------------------------------
            // option作成
            // ---------------------------------

            FONT_PRESETS.forEach(
                function (presetName) {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        presetName;


                    option.textContent =
                        presetName;


                    if (
                        presetName ===
                        selectedPreset
                    ) {

                        option.selected =
                            true;

                    }


                    select.appendChild(
                        option
                    );

                }
            );


            // ---------------------------------
            // ボタンエリア
            // ---------------------------------

            const buttonArea =
                document.createElement(
                    "div"
                );


            buttonArea.className =
                "subtitle-font-dialog-buttons";


            // ---------------------------------
            // キャンセル
            // ---------------------------------

            const cancelButton =
                document.createElement(
                    "button"
                );


            cancelButton.type =
                "button";


            cancelButton.className =
                "subtitle-font-dialog-cancel";


            cancelButton.textContent =
                "キャンセル";


            // ---------------------------------
            // 決定
            // ---------------------------------

            const okButton =
                document.createElement(
                    "button"
                );


            okButton.type =
                "button";


            okButton.className =
                "subtitle-font-dialog-ok";


            okButton.textContent =
                "決定";


            // ---------------------------------
            // DOM構築
            // ---------------------------------

            buttonArea.appendChild(
                cancelButton
            );


            buttonArea.appendChild(
                okButton
            );


            dialog.appendChild(
                title
            );


            dialog.appendChild(
                select
            );


            dialog.appendChild(
                buttonArea
            );


            overlay.appendChild(
                dialog
            );


            document.body.appendChild(
                overlay
            );


            // =================================
            // selectへフォーカス
            // =================================

            setTimeout(
                function () {

                    select.focus();

                },
                0
            );


            // =================================
            // 閉じる
            // =================================

            function closeDialog() {

                if (
                    overlay.parentNode
                ) {

                    overlay.parentNode.removeChild(
                        overlay
                    );

                }

            }


            // =================================
            // キャンセル
            // =================================

            cancelButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    closeDialog();

                }
            );


            // =================================
            // 決定
            // =================================

            okButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    const value =
                        select.value;


                    if (
                        !FONT_PRESETS.includes(
                            value
                        )
                    ) {

                        return;

                    }


                    selectedPreset =
                        value;


                    updateButton();


                    console.log(
                        "[SUBTITLE_FONT] preset selected:",
                        selectedPreset
                    );


                    closeDialog();

                }
            );


            // =================================
            // 背景クリック
            //
            // ダイアログ本体をクリックした場合は
            // 閉じない。
            // =================================

            overlay.addEventListener(
                "click",
                function (event) {

                    if (
                        event.target ===
                        overlay
                    ) {

                        closeDialog();

                    }

                }
            );


            // =================================
            // ESC
            // =================================

            function keydownHandler(
                event
            ) {

                if (
                    event.key ===
                    "Escape"
                ) {

                    closeDialog();

                    document.removeEventListener(
                        "keydown",
                        keydownHandler
                    );

                }

            }


            document.addEventListener(
                "keydown",
                keydownHandler
            );


            // =================================
            // ダイアログ終了時の後処理
            // =================================

            const originalClose =
                closeDialog;


            // ---------------------------------
            // select変更ログ
            // ---------------------------------

            select.addEventListener(
                "change",
                function () {

                    console.log(
                        "[SUBTITLE_FONT] select changed:",
                        select.value
                    );

                }
            );

        }


        // =====================================
        // フォントボタン
        // =====================================

        fontButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                if (
                    fontButton.disabled
                ) {

                    return;

                }


                selectFontPreset();

            }
        );


        // =====================================
        // 外部公開
        // =====================================

        const fontObject = {

            __initialized:
                true,


            // ---------------------------------
            // 現在のプリセット取得
            // ---------------------------------

            getPreset:
                function () {

                    return selectedPreset;

                },


            // ---------------------------------
            // プリセット設定
            // ---------------------------------

            setPreset:
                function (presetName) {

                    if (
                        !FONT_PRESETS.includes(
                            presetName
                        )
                    ) {

                        throw new Error(
                            "存在しないフォントプリセットです: " +
                            presetName
                        );

                    }


                    selectedPreset =
                        presetName;


                    updateButton();


                    console.log(
                        "[SUBTITLE_FONT] preset set:",
                        selectedPreset
                    );

                },


            // ---------------------------------
            // プリセット一覧
            // ---------------------------------

            getPresets:
                function () {

                    return FONT_PRESETS.slice();

                },


            // ---------------------------------
            // 表示更新
            // ---------------------------------

            update:
                updateButton

        };


        window.subtitleFont =
            fontObject;


        // =====================================
        // 初期表示
        // =====================================

        updateButton();


        console.log(
            "[SUBTITLE_FONT] initialize complete"
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
            initializeSubtitleFont,
            {
                once:
                    true
            }
        );

    }
    else {

        initializeSubtitleFont();

    }


})();
