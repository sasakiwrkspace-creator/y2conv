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
// subtitle.jsから使用するAPI:
//
//   window.subtitleFont.getPreset()
//
//   window.subtitleFont.setPreset("ゴシック")
//
//   window.subtitleFont.getPresets()
//
//   window.subtitleFont.getSettings()
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
        // プリセット
        //
        // py側と同じ名前を使用する。
        // =====================================

        const FONT_PRESETS = {

            "標準": {

                font:
                    "Noto Sans CJK JP",

                textColor:
                    "白",

                textColorHex:
                    "#FFFFFF",

                outlineColor:
                    "黒",

                outlineColorHex:
                    "#000000",

                outlineWidth:
                    2

            },


            "ゴシック": {

                font:
                    "Noto Sans CJK JP",

                textColor:
                    "白",

                textColorHex:
                    "#FFFFFF",

                outlineColor:
                    "黒",

                outlineColorHex:
                    "#000000",

                outlineWidth:
                    2

            },


            "明朝": {

                font:
                    "Noto Serif CJK JP",

                textColor:
                    "白",

                textColorHex:
                    "#FFFFFF",

                outlineColor:
                    "黒",

                outlineColorHex:
                    "#000000",

                outlineWidth:
                    2

            },


            "太字ゴシック": {

                font:
                    "Noto Sans CJK JP",

                textColor:
                    "白",

                textColorHex:
                    "#FFFFFF",

                outlineColor:
                    "黒",

                outlineColorHex:
                    "#000000",

                outlineWidth:
                    3

            },


            "太字明朝": {

                font:
                    "Noto Serif CJK JP",

                textColor:
                    "白",

                textColorHex:
                    "#FFFFFF",

                outlineColor:
                    "黒",

                outlineColorHex:
                    "#000000",

                outlineWidth:
                    3

            }

        };


        // =====================================
        // State
        // =====================================

        let selectedPreset =
            "標準";


        let selectedSettings =
            {
                ...FONT_PRESETS[selectedPreset]
            };


        // =====================================
        // 色ドット
        // =====================================

        function createColorDot(
            color
        ) {

            const dot =
                document.createElement(
                    "span"
                );


            dot.className =
                "subtitle-font-color-dot";


            dot.style.backgroundColor =
                color;


            return dot;

        }


        // =====================================
        // ボタン表示
        //
        // ボタンそのものは
        // 「字幕フォント」
        //
        // 色だけ現在設定を表示。
        // =====================================

        function updateButton() {

            fontButton.textContent =
                "字幕フォント";


            fontButton.title =
                "字幕フォント: " +
                selectedPreset +
                " / " +
                selectedSettings.font +
                " / " +
                selectedSettings.textColor +
                " / " +
                selectedSettings.outlineColor +
                " / 縁 " +
                selectedSettings.outlineWidth;


            // ---------------------------------
            // 色表示
            // ---------------------------------

            fontButton.style.setProperty(
                "--subtitle-text-color",
                selectedSettings.textColorHex
            );


            fontButton.style.setProperty(
                "--subtitle-outline-color",
                selectedSettings.outlineColorHex
            );

        }


        // =====================================
        // select生成
        // =====================================

        function createSelect(
            options,
            value
        ) {

            const select =
                document.createElement(
                    "select"
                );


            options.forEach(
                function (optionValue) {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        optionValue;


                    option.textContent =
                        optionValue;


                    if (
                        optionValue ===
                        value
                    ) {

                        option.selected =
                            true;

                    }


                    select.appendChild(
                        option
                    );

                }
            );


            return select;

        }


        // =====================================
        // 設定値表示
        //
        // 「subtitle_font.jsから送る値が
        // セットされているか」の確認用。
        // =====================================

        function createSettingsPreview(
            container
        ) {

            container.innerHTML =
                "";


            const title =
                document.createElement(
                    "div"
                );


            title.className =
                "subtitle-font-preview-title";


            title.textContent =
                "現在の設定";


            container.appendChild(
                title
            );


            const values = [

                [
                    "プリセット",
                    selectedPreset
                ],

                [
                    "フォント",
                    selectedSettings.font
                ],

                [
                    "文字色",
                    selectedSettings.textColor
                ],

                [
                    "縁色",
                    selectedSettings.outlineColor
                ],

                [
                    "縁の太さ",
                    selectedSettings.outlineWidth
                ]

            ];


            values.forEach(
                function (item) {

                    const row =
                        document.createElement(
                            "div"
                        );


                    row.className =
                        "subtitle-font-preview-row";


                    const label =
                        document.createElement(
                            "span"
                        );


                    label.className =
                        "subtitle-font-preview-label";


                    label.textContent =
                        item[0];


                    const value =
                        document.createElement(
                            "span"
                        );


                    value.className =
                        "subtitle-font-preview-value";


                    value.textContent =
                        item[1];


                    row.appendChild(
                        label
                    );


                    row.appendChild(
                        value
                    );


                    container.appendChild(
                        row
                    );

                }
            );

        }


        // =====================================
        // ダイアログ
        // =====================================

        function selectFontPreset() {

            const overlay =
                document.createElement(
                    "div"
                );


            overlay.className =
                "subtitle-font-dialog-overlay";


            const dialog =
                document.createElement(
                    "div"
                );


            dialog.className =
                "subtitle-font-dialog";


            // =================================
            // タイトル
            // =================================

            const title =
                document.createElement(
                    "div"
                );


            title.className =
                "subtitle-font-dialog-title";


            title.textContent =
                "字幕フォント";


            dialog.appendChild(
                title
            );


            // =================================
            // プリセット
            // =================================

            const presetLabel =
                document.createElement(
                    "label"
                );


            presetLabel.className =
                "subtitle-font-dialog-label";


            presetLabel.textContent =
                "プリセット";


            const presetSelect =
                createSelect(

                    Object.keys(
                        FONT_PRESETS
                    ),

                    selectedPreset

                );


            presetSelect.className =
                "subtitle-font-select";


            presetLabel.appendChild(
                presetSelect
            );


            dialog.appendChild(
                presetLabel
            );


            // =================================
            // フォント
            // =================================

            const fontLabel =
                document.createElement(
                    "label"
                );


            fontLabel.className =
                "subtitle-font-dialog-label";


            fontLabel.textContent =
                "フォント";


            const fontSelect =
                createSelect(

                    [

                        "Noto Sans CJK JP",

                        "Noto Serif CJK JP"

                    ],

                    selectedSettings.font

                );


            fontSelect.className =
                "subtitle-font-select";


            fontLabel.appendChild(
                fontSelect
            );


            dialog.appendChild(
                fontLabel
            );


            // =================================
            // 文字色
            // =================================

            const textColorLabel =
                document.createElement(
                    "label"
                );


            textColorLabel.className =
                "subtitle-font-dialog-label";


            textColorLabel.textContent =
                "文字色";


            const textColorSelect =
                createSelect(

                    [

                        "白",

                        "黒",

                        "黄",

                        "赤",

                        "青"

                    ],

                    selectedSettings.textColor

                );


            textColorSelect.className =
                "subtitle-font-select";


            textColorLabel.appendChild(
                createColorDot(
                    selectedSettings.textColorHex
                )
            );


            textColorLabel.appendChild(
                textColorSelect
            );


            dialog.appendChild(
                textColorLabel
            );


            // =================================
            // 縁色
            // =================================

            const outlineColorLabel =
                document.createElement(
                    "label"
                );


            outlineColorLabel.className =
                "subtitle-font-dialog-label";


            outlineColorLabel.textContent =
                "縁色";


            const outlineColorSelect =
                createSelect(

                    [

                        "黒",

                        "白",

                        "黄",

                        "赤",

                        "青"

                    ],

                    selectedSettings.outlineColor

                );


            outlineColorSelect.className =
                "subtitle-font-select";


            outlineColorLabel.appendChild(
                createColorDot(
                    selectedSettings.outlineColorHex
                )
            );


            outlineColorLabel.appendChild(
                outlineColorSelect
            );


            dialog.appendChild(
                outlineColorLabel
            );


            // =================================
            // 縁の太さ
            // =================================

            const outlineWidthLabel =
                document.createElement(
                    "label"
                );


            outlineWidthLabel.className =
                "subtitle-font-dialog-label";


            outlineWidthLabel.textContent =
                "縁の太さ";


            const outlineWidthInput =
                document.createElement(
                    "input"
                );


            outlineWidthInput.type =
                "number";


            outlineWidthInput.min =
                "0";


            outlineWidthInput.max =
                "20";


            outlineWidthInput.step =
                "1";


            outlineWidthInput.value =
                selectedSettings.outlineWidth;


            outlineWidthInput.className =
                "subtitle-font-width-input";


            outlineWidthLabel.appendChild(
                outlineWidthInput
            );


            dialog.appendChild(
                outlineWidthLabel
            );


            // =================================
            // 現在の設定表示
            // =================================

            const preview =
                document.createElement(
                    "div"
                );


            preview.className =
                "subtitle-font-preview";


            dialog.appendChild(
                preview
            );


            function updatePreview() {

                createSettingsPreview(
                    preview
                );

            }


            updatePreview();


            // =================================
            // プリセット変更
            // =================================

            presetSelect.addEventListener(
                "change",
                function () {

                    const preset =
                        FONT_PRESETS[
                            presetSelect.value
                        ];


                    if (!preset) {

                        return;

                    }


                    fontSelect.value =
                        preset.font;


                    textColorSelect.value =
                        preset.textColor;


                    outlineColorSelect.value =
                        preset.outlineColor;


                    outlineWidthInput.value =
                        preset.outlineWidth;


                    updatePreview();

                }
            );


            // =================================
            // 手動変更
            // =================================

            fontSelect.addEventListener(
                "change",
                updatePreview
            );


            textColorSelect.addEventListener(
                "change",
                updatePreview
            );


            outlineColorSelect.addEventListener(
                "change",
                updatePreview
            );


            outlineWidthInput.addEventListener(
                "input",
                updatePreview
            );


            // =================================
            // ボタン
            // =================================

            const buttonArea =
                document.createElement(
                    "div"
                );


            buttonArea.className =
                "subtitle-font-dialog-buttons";


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


            buttonArea.appendChild(
                cancelButton
            );


            buttonArea.appendChild(
                okButton
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
            // 閉じる
            // =================================

            function closeDialog() {

                document.removeEventListener(
                    "keydown",
                    keydownHandler
                );


                if (
                    overlay.parentNode
                ) {

                    overlay.parentNode.removeChild(
                        overlay
                    );

                }

            }


            // =================================
            // キー
            // =================================

            function keydownHandler(
                event
            ) {

                if (
                    event.key ===
                    "Escape"
                ) {

                    closeDialog();

                }


                if (
                    event.key ===
                    "Enter"
                ) {

                    okButton.click();

                }

            }


            document.addEventListener(
                "keydown",
                keydownHandler
            );


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


                    const presetName =
                        presetSelect.value;


                    if (
                        !FONT_PRESETS[
                            presetName
                        ]
                    ) {

                        return;

                    }


                    selectedPreset =
                        presetName;


                    selectedSettings = {

                        font:
                            fontSelect.value,

                        textColor:
                            textColorSelect.value,

                        textColorHex:
                            getColorHex(
                                textColorSelect.value
                            ),

                        outlineColor:
                            outlineColorSelect.value,

                        outlineColorHex:
                            getColorHex(
                                outlineColorSelect.value
                            ),

                        outlineWidth:
                            Number(
                                outlineWidthInput.value
                            ) || 0

                    };


                    updateButton();


                    console.log(
                        "[SUBTITLE_FONT] settings selected:",
                        selectedPreset,
                        selectedSettings
                    );


                    closeDialog();

                }
            );


            // =================================
            // 背景クリック
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
            // フォーカス
            // =================================

            setTimeout(
                function () {

                    presetSelect.focus();

                },
                0
            );

        }


        // =====================================
        // 色 → HEX
        // =====================================

        function getColorHex(
            colorName
        ) {

            const colors = {

                "白":
                    "#FFFFFF",

                "黒":
                    "#000000",

                "黄":
                    "#FFFF00",

                "赤":
                    "#FF0000",

                "青":
                    "#0000FF"

            };


            return (
                colors[colorName] ||
                "#FFFFFF"
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
            // プリセット名
            // ---------------------------------

            getPreset:
                function () {

                    return selectedPreset;

                },


            // ---------------------------------
            // プリセット設定
            // ---------------------------------

            getSettings:
                function () {

                    return {

                        preset_name:
                            selectedPreset,

                        font:
                            selectedSettings.font,

                        text_color:
                            selectedSettings.textColor,

                        text_color_hex:
                            selectedSettings.textColorHex,

                        outline_color:
                            selectedSettings.outlineColor,

                        outline_color_hex:
                            selectedSettings.outlineColorHex,

                        outline_width:
                            selectedSettings.outlineWidth

                    };

                },


            // ---------------------------------
            // プリセット設定
            // ---------------------------------

            setPreset:
                function (
                    presetName
                ) {

                    if (
                        !FONT_PRESETS[
                            presetName
                        ]
                    ) {

                        throw new Error(
                            "存在しないフォントプリセットです: " +
                            presetName
                        );

                    }


                    selectedPreset =
                        presetName;


                    selectedSettings = {

                        ...FONT_PRESETS[
                            presetName
                        ]

                    };


                    updateButton();


                    console.log(
                        "[SUBTITLE_FONT] preset set:",
                        selectedPreset,
                        selectedSettings
                    );

                },


            // ---------------------------------
            // プリセット一覧
            // ---------------------------------

            getPresets:
                function () {

                    return Object.keys(
                        FONT_PRESETS
                    );

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
