// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// タブ2専用
//
// 役割:
// ・字幕フォント設定UI
// ・#subtitle-font-button の操作
// ・選択中設定の保持
// ・プリセット管理
// ・文字色 / 縁取り色の選択
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
//   window.subtitleFont.setDisabled(true / false)
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
        // =====================================

        const FONT_PRESETS = {

            "標準": {

                font:
                    "IPAGothic",

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
                    "IPAGothic",

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
                    "IPAMincho",

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
                    "IPAGothic",

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
                    "IPAMincho",

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
        // 色
        // =====================================

        const COLOR_MAP = {

            "黒":
                "#000000",

            "白":
                "#FFFFFF",

            "赤":
                "#FF0000"

        };


        const TEXT_COLORS = [

            "黒",
            "白",
            "赤"

        ];


        const OUTLINE_COLORS = [

            "黒",
            "白",
            "赤"

        ];


        // =====================================
        // State
        // =====================================

        let selectedPreset =
            "標準";


        let selectedSettings = {

            ...FONT_PRESETS[
                selectedPreset
            ]

        };


        let isDisabled =
            false;


        // =====================================
        // 色HEX取得
        // =====================================

        function getColorHex(
            colorName
        ) {

            return (
                COLOR_MAP[colorName] ||
                "#FFFFFF"
            );

        }


        // =====================================
        // タイトル色
        //
        // 文字色に合わせて
        // 「字幕フォント」の色を変更。
        // =====================================

        function updateButtonColor() {

            fontButton.style.setProperty(
                "--subtitle-font-button-color",
                selectedSettings.textColorHex
            );


            fontButton.style.color =
                selectedSettings.textColorHex;

        }


        // =====================================
        // ボタン表示
        // =====================================

        function updateButton() {

            fontButton.textContent =
                "字幕フォント";


            fontButton.title =
                "字幕フォント: " +
                selectedPreset +
                " / " +
                selectedSettings.font +
                " / 文字色 " +
                selectedSettings.textColor +
                " / 縁取り色 " +
                selectedSettings.outlineColor +
                " / 縁 " +
                selectedSettings.outlineWidth;


            fontButton.style.setProperty(
                "--subtitle-text-color",
                selectedSettings.textColorHex
            );


            fontButton.style.setProperty(
                "--subtitle-outline-color",
                selectedSettings.outlineColorHex
            );


            updateButtonColor();


            fontButton.disabled =
                isDisabled;

        }


        // =====================================
        // setDisabled
        // =====================================

        function setDisabled(
            disabled
        ) {

            isDisabled =
                Boolean(
                    disabled
                );


            updateButton();


            console.log(
                "[SUBTITLE_FONT] disabled:",
                isDisabled
            );

        }


        // =====================================
        // 設定プレビュー
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
                    "縁取り色",
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
                        item[0] +
                        "：";


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
        // ラジオボタン生成
        //
        // 表示:
        //
        // ●黒  ●白  ●赤
        //
        // =====================================

        function createColorRadioGroup(
            name,
            colors,
            selectedColor,
            onChange
        ) {

            const group =
                document.createElement(
                    "div"
                );


            group.className =
                "subtitle-font-radio-group";


            colors.forEach(
                function (colorName) {

                    const label =
                        document.createElement(
                            "label"
                        );


                    label.className =
                        "subtitle-font-radio-label";


                    const input =
                        document.createElement(
                            "input"
                        );


                    input.type =
                        "radio";


                    input.name =
                        name;


                    input.value =
                        colorName;


                    input.checked =
                        colorName ===
                        selectedColor;


                    const dot =
                        document.createElement(
                            "span"
                        );


                    dot.className =
                        "subtitle-font-radio-dot";


                    dot.style.backgroundColor =
                        getColorHex(
                            colorName
                        );


                    const text =
                        document.createElement(
                            "span"
                        );


                    text.textContent =
                        colorName;


                    const hex =
                        document.createElement(
                            "span"
                        );


                    hex.className =
                        "subtitle-font-radio-hex";


                    hex.textContent =
                        getColorHex(
                            colorName
                        );


                    label.appendChild(
                        input
                    );


                    label.appendChild(
                        dot
                    );


                    label.appendChild(
                        text
                    );


                    label.appendChild(
                        hex
                    );


                    input.addEventListener(
                        "change",
                        function () {

                            if (!input.checked) {

                                return;

                            }


                            onChange(
                                colorName
                            );

                        }
                    );


                    group.appendChild(
                        label
                    );

                }
            );


            return group;

        }


        // =====================================
        // プリセットボタン生成
        // =====================================

        function createPresetButtons(
            container,
            currentValues,
            updateValues,
            updatePreview
        ) {

            const presetArea =
                document.createElement(
                    "div"
                );


            presetArea.className =
                "subtitle-font-preset-area";


            const presetButtons =
                document.createElement(
                    "div"
                );


            presetButtons.className =
                "subtitle-font-preset-buttons";


            Object.keys(
                FONT_PRESETS
            ).forEach(
                function (presetName) {

                    const button =
                        document.createElement(
                            "button"
                        );


                    button.type =
                        "button";


                    button.className =
                        "subtitle-font-preset-button";


                    button.textContent =
                        presetName;


                    button.addEventListener(
                        "click",
                        function (event) {

                            event.preventDefault();


                            const preset =
                                FONT_PRESETS[
                                    presetName
                                ];


                            if (!preset) {

                                return;

                            }


                            currentValues.preset =
                                presetName;


                            currentValues.font =
                                preset.font;


                            currentValues.textColor =
                                preset.textColor;


                            currentValues.outlineColor =
                                preset.outlineColor;


                            currentValues.outlineWidth =
                                preset.outlineWidth;


                            updateValues();


                            updatePreview();

                        }
                    );


                    presetButtons.appendChild(
                        button
                    );

                }
            );


            presetArea.appendChild(
                presetButtons
            );


            container.appendChild(
                presetArea
            );

        }


        // =====================================
        // ダイアログ
        // =====================================

        function selectFontPreset() {

            if (isDisabled) {

                return;

            }


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
            // 作業用値
            // =================================

            const currentValues = {

                preset:
                    selectedPreset,

                font:
                    selectedSettings.font,

                textColor:
                    selectedSettings.textColor,

                outlineColor:
                    selectedSettings.outlineColor,

                outlineWidth:
                    selectedSettings.outlineWidth

            };


            // =================================
            // プリセット
            // =================================

            const presetLabel =
                document.createElement(
                    "div"
                );


            presetLabel.className =
                "subtitle-font-dialog-label";


            presetLabel.textContent =
                "プリセット";


            const presetToggle =
                document.createElement(
                    "button"
                );


            presetToggle.type =
                "button";


            presetToggle.className =
                "subtitle-font-preset-toggle";


            presetToggle.textContent =
                "プリセットを表示 ▼";


            const presetContainer =
                document.createElement(
                    "div"
                );


            presetContainer.className =
                "subtitle-font-preset-container";


            presetContainer.hidden =
                true;


            presetToggle.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    const isOpen =
                        !presetContainer.hidden;


                    presetContainer.hidden =
                        isOpen;


                    presetToggle.textContent =
                        isOpen
                            ? "プリセットを表示 ▼"
                            : "プリセットを閉じる ▲";

                }
            );


            presetLabel.appendChild(
                presetToggle
            );


            dialog.appendChild(
                presetLabel
            );


            createPresetButtons(

                presetContainer,

                currentValues,

                function () {

                    fontSelect.value =
                        currentValues.font;


                    updateTextColorRadios(
                        currentValues.textColor
                    );


                    updateOutlineColorRadios(
                        currentValues.outlineColor
                    );


                    outlineWidthInput.value =
                        currentValues.outlineWidth;

                },

                updatePreview

            );


            dialog.appendChild(
                presetContainer
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

                        "IPAGothic",

                        "IPAMincho"

                    ],

                    currentValues.font

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

            const textColorSection =
                document.createElement(
                    "div"
                );


            textColorSection.className =
                "subtitle-font-dialog-label";


            const textColorTitle =
                document.createElement(
                    "div"
                );


            textColorTitle.textContent =
                "文字色";


            textColorSection.appendChild(
                textColorTitle
            );


            let textColorRadios;


            function updateTextColorRadios(
                value
            ) {

                currentValues.textColor =
                    value;


                if (!textColorRadios) {

                    return;

                }


                const radios =
                    textColorRadios.querySelectorAll(
                        "input[type='radio']"
                    );


                radios.forEach(
                    function (radio) {

                        radio.checked =
                            radio.value ===
                            value;

                    }
                );

            }


            textColorRadios =
                createColorRadioGroup(

                    "subtitle-text-color",

                    TEXT_COLORS,

                    currentValues.textColor,

                    function (colorName) {

                        currentValues.textColor =
                            colorName;


                        updatePreview();

                    }

                );


            textColorSection.appendChild(
                textColorRadios
            );


            dialog.appendChild(
                textColorSection
            );


            // =================================
            // 縁取り色
            // =================================

            const outlineColorSection =
                document.createElement(
                    "div"
                );


            outlineColorSection.className =
                "subtitle-font-dialog-label";


            const outlineColorTitle =
                document.createElement(
                    "div"
                );


            outlineColorTitle.textContent =
                "縁取り色";


            outlineColorSection.appendChild(
                outlineColorTitle
            );


            let outlineColorRadios;


            function updateOutlineColorRadios(
                value
            ) {

                currentValues.outlineColor =
                    value;


                if (!outlineColorRadios) {

                    return;

                }


                const radios =
                    outlineColorRadios.querySelectorAll(
                        "input[type='radio']"
                    );


                radios.forEach(
                    function (radio) {

                        radio.checked =
                            radio.value ===
                            value;

                    }
                );

            }


            outlineColorRadios =
                createColorRadioGroup(

                    "subtitle-outline-color",

                    OUTLINE_COLORS,

                    currentValues.outlineColor,

                    function (colorName) {

                        currentValues.outlineColor =
                            colorName;


                        updatePreview();

                    }

                );


            outlineColorSection.appendChild(
                outlineColorRadios
            );


            dialog.appendChild(
                outlineColorSection
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
                currentValues.outlineWidth;


            outlineWidthInput.className =
                "subtitle-font-width-input";


            outlineWidthLabel.appendChild(
                outlineWidthInput
            );


            dialog.appendChild(
                outlineWidthLabel
            );


            // =================================
            // 現在の設定
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

                const previewSettings = {

                    font:
                        currentValues.font,

                    textColor:
                        currentValues.textColor,

                    outlineColor:
                        currentValues.outlineColor,

                    outlineWidth:
                        Number(
                            outlineWidthInput.value
                        ) || 0

                };


                const oldSettings =
                    selectedSettings;


                const oldPreset =
                    selectedPreset;


                selectedSettings = {

                    ...oldSettings,

                    ...previewSettings

                };


                selectedPreset =
                    currentValues.preset;


                createSettingsPreview(
                    preview
                );


                selectedSettings =
                    oldSettings;


                selectedPreset =
                    oldPreset;

            }


            updatePreview();


            // =================================
            // 手動変更
            // =================================

            fontSelect.addEventListener(
                "change",
                function () {

                    currentValues.font =
                        fontSelect.value;


                    currentValues.preset =
                        "カスタム";


                    updatePreview();

                }
            );


            outlineWidthInput.addEventListener(
                "input",
                function () {

                    currentValues.outlineWidth =
                        Number(
                            outlineWidthInput.value
                        ) || 0;


                    currentValues.preset =
                        "カスタム";


                    updatePreview();

                }
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

                    return;

                }


                if (
                    event.key ===
                    "Enter"
                ) {

                    if (
                        event.target &&
                        event.target.tagName ===
                            "INPUT"
                    ) {

                        return;

                    }


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


                    let width =
                        Number(
                            outlineWidthInput.value
                        );


                    if (
                        !Number.isFinite(width)
                    ) {

                        width =
                            0;

                    }


                    width =
                        Math.max(
                            0,
                            Math.min(
                                20,
                                Math.round(
                                    width
                                )
                            )
                        );


                    selectedPreset =
                        currentValues.preset;


                    selectedSettings = {

                        font:
                            currentValues.font,

                        textColor:
                            currentValues.textColor,

                        textColorHex:
                            getColorHex(
                                currentValues.textColor
                            ),

                        outlineColor:
                            currentValues.outlineColor,

                        outlineColorHex:
                            getColorHex(
                                currentValues.outlineColor
                            ),

                        outlineWidth:
                            width

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

                    presetToggle.focus();

                },
                0
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
                    isDisabled ||
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
            // 設定
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
            // 無効化
            // ---------------------------------

            setDisabled:
                setDisabled,


            // ---------------------------------
            // 無効状態
            // ---------------------------------

            isDisabled:
                function () {

                    return isDisabled;

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
