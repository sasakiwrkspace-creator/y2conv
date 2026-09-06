// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// タブ2専用
//
// 役割:
// ・字幕フォント選択UI
// ・#subtitle-font-button の操作
// ・選択中設定の保持
// ・色名 / HEXコードの管理
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
        // カラー定義
        //
        // Python側の色名と一致させる。
        // =====================================

        const SUBTITLE_COLORS = {

            "白":
                "#FFFFFF",

            "黒":
                "#000000",

            "赤":
                "#FF0000",

            "青":
                "#0000FF",

            "緑":
                "#00FF00",

            "黄":
                "#FFFF00",

            "オレンジ":
                "#FFA500",

            "水色":
                "#00FFFF",

            "紫":
                "#800080"

        };


        // =====================================
        // フォントプリセット
        // =====================================

        const FONT_PRESETS = {

            "標準": {

                font:
                    "Noto Sans CJK JP",

                textColor:
                    "白",

                outlineColor:
                    "黒",

                outlineWidth:
                    2

            },


            "ゴシック": {

                font:
                    "Noto Sans CJK JP",

                textColor:
                    "白",

                outlineColor:
                    "黒",

                outlineWidth:
                    2

            },


            "明朝": {

                font:
                    "Noto Serif CJK JP",

                textColor:
                    "白",

                outlineColor:
                    "黒",

                outlineWidth:
                    2

            },


            "太字ゴシック": {

                font:
                    "Noto Sans CJK JP",

                textColor:
                    "白",

                outlineColor:
                    "黒",

                outlineWidth:
                    3

            },


            "太字明朝": {

                font:
                    "Noto Serif CJK JP",

                textColor:
                    "白",

                outlineColor:
                    "黒",

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
            createSettingsFromPreset(
                selectedPreset
            );


        // =====================================
        // プリセットから設定作成
        // =====================================

        function createSettingsFromPreset(
            presetName
        ) {

            const preset =
                FONT_PRESETS[presetName] ||
                FONT_PRESETS["標準"];


            return {

                font:
                    preset.font,

                textColor:
                    preset.textColor,

                textColorHex:
                    getColorHex(
                        preset.textColor
                    ),

                outlineColor:
                    preset.outlineColor,

                outlineColorHex:
                    getColorHex(
                        preset.outlineColor
                    ),

                outlineWidth:
                    preset.outlineWidth

            };

        }


        // =====================================
        // 色 → HEX
        // =====================================

        function getColorHex(
            colorName
        ) {

            return (
                SUBTITLE_COLORS[colorName] ||
                "#FFFFFF"
            );

        }


        // =====================================
        // 色ドット作成
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


            dot.textContent =
                "●";


            dot.style.color =
                color;


            dot.style.marginRight =
                "6px";


            dot.setAttribute(
                "aria-hidden",
                "true"
            );


            return dot;

        }


        // =====================================
        // 色名表示用
        //
        // 例:
        // ● 赤
        // =====================================

        function createColorOption(
            select,
            colorName
        ) {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                colorName;


            option.textContent =
                "● " +
                colorName;


            if (
                colorName ===
                select.dataset.selectedColor
            ) {

                option.selected =
                    true;

            }


            select.appendChild(
                option
            );

        }


        // =====================================
        // 色Select作成
        // =====================================

        function createColorSelect(
            colors,
            value
        ) {

            const select =
                document.createElement(
                    "select"
                );


            select.className =
                "subtitle-font-select";


            select.dataset.selectedColor =
                value;


            colors.forEach(
                function (colorName) {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        colorName;


                    option.textContent =
                        "● " +
                        colorName;


                    if (
                        colorName ===
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
        // 通常Select作成
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
                " / " +
                selectedSettings.textColor +
                " / " +
                selectedSettings.outlineColor +
                " / 縁 " +
                selectedSettings.outlineWidth;

        }


        // =====================================
        // 設定値表示
        //
        // 項目：値
        // =====================================

        function createSettingsPreview(
            container,
            settings,
            presetName
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
                    presetName
                ],

                [
                    "フォント",
                    settings.font
                ],

                [
                    "文字色",
                    settings.textColor
                ],

                [
                    "文字色コード",
                    settings.textColorHex
                ],

                [
                    "縁色",
                    settings.outlineColor
                ],

                [
                    "縁色コード",
                    settings.outlineColorHex
                ],

                [
                    "縁の太さ",
                    settings.outlineWidth
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
        // フォントダイアログ
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

                        "Noto Sans JP",

                        "Noto Serif CJK JP",

                        "Noto Serif JP",

                        "IPAexGothic",

                        "IPAGothic",

                        "IPAexMincho",

                        "IPAMincho",

                        "VL Gothic",

                        "TakaoGothic"

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


            const textColorDot =
                createColorDot(
                    getColorHex(
                        selectedSettings.textColor
                    )
                );


            const textColorSelect =
                createColorSelect(

                    Object.keys(
                        SUBTITLE_COLORS
                    ),

                    selectedSettings.textColor

                );


            textColorLabel.appendChild(
                textColorDot
            );


            textColorLabel.appendChild(
                textColorSelect
            );


            dialog.appendChild(
                textColorLabel
            );


            // =================================
            // 文字色コード
            // =================================

            const textColorCodeLabel =
                document.createElement(
                    "label"
                );


            textColorCodeLabel.className =
                "subtitle-font-dialog-label";


            textColorCodeLabel.textContent =
                "文字色コード";


            const textColorCode =
                document.createElement(
                    "span"
                );


            textColorCode.className =
                "subtitle-font-color-code";


            textColorCode.textContent =
                getColorHex(
                    selectedSettings.textColor
                );


            textColorCodeLabel.appendChild(
                textColorCode
            );


            dialog.appendChild(
                textColorCodeLabel
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


            const outlineColorDot =
                createColorDot(
                    getColorHex(
                        selectedSettings.outlineColor
                    )
                );


            const outlineColorSelect =
                createColorSelect(

                    Object.keys(
                        SUBTITLE_COLORS
                    ),

                    selectedSettings.outlineColor

                );


            outlineColorLabel.appendChild(
                outlineColorDot
            );


            outlineColorLabel.appendChild(
                outlineColorSelect
            );


            dialog.appendChild(
                outlineColorLabel
            );


            // =================================
            // 縁色コード
            // =================================

            const outlineColorCodeLabel =
                document.createElement(
                    "label"
                );


            outlineColorCodeLabel.className =
                "subtitle-font-dialog-label";


            outlineColorCodeLabel.textContent =
                "縁色コード";


            const outlineColorCode =
                document.createElement(
                    "span"
                );


            outlineColorCode.className =
                "subtitle-font-color-code";


            outlineColorCode.textContent =
                getColorHex(
                    selectedSettings.outlineColor
                );


            outlineColorCodeLabel.appendChild(
                outlineColorCode
            );


            dialog.appendChild(
                outlineColorCodeLabel
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
                "10";


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

                const textColor =
                    textColorSelect.value;


                const outlineColor =
                    outlineColorSelect.value;


                textColorDot.style.color =
                    getColorHex(
                        textColor
                    );


                outlineColorDot.style.color =
                    getColorHex(
                        outlineColor
                    );


                textColorCode.textContent =
                    getColorHex(
                        textColor
                    );


                outlineColorCode.textContent =
                    getColorHex(
                        outlineColor
                    );


                createSettingsPreview(

                    preview,

                    {

                        font:
                            fontSelect.value,

                        textColor:
                            textColor,

                        textColorHex:
                            getColorHex(
                                textColor
                            ),

                        outlineColor:
                            outlineColor,

                        outlineColorHex:
                            getColorHex(
                                outlineColor
                            ),

                        outlineWidth:
                            Number(
                                outlineWidthInput.value
                            ) || 0

                    },

                    presetSelect.value

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

                    if (
                        document.activeElement ===
                        outlineWidthInput
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


                    const presetName =
                        presetSelect.value;


                    if (
                        !FONT_PRESETS[
                            presetName
                        ]
                    ) {

                        return;

                    }


                    let outlineWidth =
                        Number(
                            outlineWidthInput.value
                        );


                    if (
                        !Number.isFinite(
                            outlineWidth
                        )
                    ) {

                        outlineWidth =
                            2;

                    }


                    outlineWidth =
                        Math.max(
                            0,
                            Math.min(
                                10,
                                Math.round(
                                    outlineWidth
                                )
                            )
                        );


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
                            outlineWidth

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
            // 現在の全設定
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


                    selectedSettings =
                        createSettingsFromPreset(
                            presetName
                        );


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
            // ボタン表示更新
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
