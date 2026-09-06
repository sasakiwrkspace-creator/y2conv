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
// ・文字色 / 縁色の管理
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
//   window.subtitleFont.setDisabled(true)
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
        // Python subtitle_font.py と対応
        //
        // HEX:
        // UI表示用
        //
        // ASS:
        // FFmpeg / ASS用
        // =====================================

        const SUBTITLE_COLORS = {

            "白": {
                hex: "#FFFFFF",
                ass: "&H00FFFFFF"
            },

            "黒": {
                hex: "#000000",
                ass: "&H00000000"
            },

            "赤": {
                hex: "#FF0000",
                ass: "&H000000FF"
            },

            "青": {
                hex: "#0000FF",
                ass: "&H00FF0000"
            },

            "緑": {
                hex: "#00FF00",
                ass: "&H0000FF00"
            },

            "黄": {
                hex: "#FFFF00",
                ass: "&H0000FFFF"
            },

            "オレンジ": {
                hex: "#FFA500",
                ass: "&H0000A5FF"
            },

            "水色": {
                hex: "#00FFFF",
                ass: "&H00FFFF00"
            },

            "紫": {
                hex: "#800080",
                ass: "&H00800080"
            }

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


        let isDisabled =
            false;


        // =====================================
        // プリセットから設定作成
        // =====================================

        function createSettingsFromPreset(
            presetName
        ) {

            const preset =
                FONT_PRESETS[presetName];


            if (!preset) {

                return {

                    font:
                        "Noto Sans CJK JP",

                    textColor:
                        "白",

                    textColorHex:
                        "#FFFFFF",

                    textColorAss:
                        "&H00FFFFFF",

                    outlineColor:
                        "黒",

                    outlineColorHex:
                        "#000000",

                    outlineColorAss:
                        "&H00000000",

                    outlineWidth:
                        2

                };

            }


            return {

                font:
                    preset.font,

                textColor:
                    preset.textColor,

                textColorHex:
                    getColorHex(
                        preset.textColor
                    ),

                textColorAss:
                    getColorAss(
                        preset.textColor
                    ),

                outlineColor:
                    preset.outlineColor,

                outlineColorHex:
                    getColorHex(
                        preset.outlineColor
                    ),

                outlineColorAss:
                    getColorAss(
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

            if (
                SUBTITLE_COLORS[colorName]
            ) {

                return SUBTITLE_COLORS[
                    colorName
                ].hex;

            }


            return "#FFFFFF";

        }


        // =====================================
        // 色 → ASS
        // =====================================

        function getColorAss(
            colorName
        ) {

            if (
                SUBTITLE_COLORS[colorName]
            ) {

                return SUBTITLE_COLORS[
                    colorName
                ].ass;

            }


            return "&H00FFFFFF";

        }


        // =====================================
        // 色 → 表示文字
        //
        // 例:
        // ● 白  #FFFFFF
        // =====================================

        function getColorDisplayText(
            colorName
        ) {

            const hex =
                getColorHex(
                    colorName
                );


            return (
                "● " +
                colorName +
                "  " +
                hex
            );

        }


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


            dot.textContent =
                "●";


            dot.style.display =
                "inline-block";


            dot.style.color =
                color;


            dot.style.fontSize =
                "18px";


            dot.style.lineHeight =
                "1";


            dot.style.marginRight =
                "6px";


            dot.style.verticalAlign =
                "middle";


            // 白色の場合でも見えるように
            // 黒い薄い影を付ける
            if (
                String(color).toUpperCase() ===
                "#FFFFFF"
            ) {

                dot.style.textShadow =
                    "0 0 0.5px #000000";

            }


            return dot;

        }


        // =====================================
        // ボタン表示
        // =====================================

        function updateButton() {

            // ---------------------------------
            // ボタン文字
            // ---------------------------------

            fontButton.textContent =
                "字幕フォント";


            // ---------------------------------
            // title
            // ---------------------------------

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
            // 色をCSS変数として保持
            // ---------------------------------

            fontButton.style.setProperty(

                "--subtitle-text-color",

                selectedSettings.textColorHex

            );


            fontButton.style.setProperty(

                "--subtitle-outline-color",

                selectedSettings.outlineColorHex

            );


            // ---------------------------------
            // 無効状態
            // ---------------------------------

            fontButton.disabled =
                isDisabled;

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
        // カラー選択表示
        //
        // select自体にはブラウザ制約があるため
        // selectの横に
        //
        // ● 白 #FFFFFF
        //
        // の表示を作る。
        // =====================================

        function createColorSelector(
            labelText,
            options,
            value
        ) {

            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.style.display =
                "flex";


            wrapper.style.alignItems =
                "center";


            wrapper.style.gap =
                "8px";


            wrapper.style.width =
                "100%";


            const label =
                document.createElement(
                    "span"
                );


            label.className =
                "subtitle-font-dialog-label";


            label.style.minWidth =
                "70px";


            label.textContent =
                labelText;


            wrapper.appendChild(
                label
            );


            const colorPreview =
                document.createElement(
                    "span"
                );


            colorPreview.className =
                "subtitle-font-color-preview";


            colorPreview.style.display =
                "inline-flex";


            colorPreview.style.alignItems =
                "center";


            colorPreview.style.minWidth =
                "135px";


            colorPreview.style.fontSize =
                "14px";


            function updateColorPreview(
                colorName
            ) {

                colorPreview.innerHTML =
                    "";


                colorPreview.appendChild(

                    createColorDot(

                        getColorHex(
                            colorName
                        )

                    )

                );


                const name =
                    document.createElement(
                        "span"
                    );


                name.textContent =
                    colorName;


                colorPreview.appendChild(
                    name
                );


                const hex =
                    document.createElement(
                        "span"
                    );


                hex.textContent =
                    " " +
                    getColorHex(
                        colorName
                    );


                hex.style.marginLeft =
                    "5px";


                hex.style.fontSize =
                    "12px";


                hex.style.opacity =
                    "0.8";


                colorPreview.appendChild(
                    hex
                );

            }


            updateColorPreview(
                value
            );


            wrapper.appendChild(
                colorPreview
            );


            const select =
                createSelect(
                    options,
                    value
                );


            select.className =
                "subtitle-font-select";


            select.style.flex =
                "1";


            wrapper.appendChild(
                select
            );


            select.addEventListener(
                "change",
                function () {

                    updateColorPreview(
                        select.value
                    );

                    updatePreviewFromDialog();

                }
            );


            return {

                wrapper:
                    wrapper,

                select:
                    select,

                update:
                    updateColorPreview

            };

        }


        // =====================================
        // 設定値表示
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
        // ダイアログ用変数
        // =====================================

        let activeDialog =
            null;


        let activeDialogControls =
            null;


        // =====================================
        // ダイアログ
        // =====================================

        function selectFontPreset() {

            if (isDisabled) {

                return;

            }


            // ---------------------------------
            // 既存ダイアログがあれば閉じる
            // ---------------------------------

            if (activeDialog) {

                closeDialog();

            }


            // =================================
            // オーバーレイ
            // =================================

            const overlay =
                document.createElement(
                    "div"
                );


            overlay.className =
                "subtitle-font-dialog-overlay";


            // ---------------------------------
            // CSSをインラインでも指定
            //
            // style.cssがなくても
            // 画面中央に表示されるようにする。
            // ---------------------------------

            overlay.style.position =
                "fixed";


            overlay.style.top =
                "0";


            overlay.style.right =
                "0";


            overlay.style.bottom =
                "0";


            overlay.style.left =
                "0";


            overlay.style.width =
                "100vw";


            overlay.style.height =
                "100vh";


            overlay.style.zIndex =
                "999999";


            overlay.style.display =
                "flex";


            overlay.style.alignItems =
                "center";


            overlay.style.justifyContent =
                "center";


            overlay.style.backgroundColor =
                "rgba(0, 0, 0, 0.55)";


            overlay.style.padding =
                "20px";


            overlay.style.boxSizing =
                "border-box";


            overlay.style.overflow =
                "auto";


            // =================================
            // ダイアログ
            // =================================

            const dialog =
                document.createElement(
                    "div"
                );


            dialog.className =
                "subtitle-font-dialog";


            dialog.style.position =
                "relative";


            dialog.style.width =
                "min(520px, 100%)";


            dialog.style.maxWidth =
                "520px";


            dialog.style.maxHeight =
                "calc(100vh - 40px)";


            dialog.style.overflowY =
                "auto";


            dialog.style.background =
                "#ffffff";


            dialog.style.color =
                "#222222";


            dialog.style.borderRadius =
                "12px";


            dialog.style.padding =
                "24px";


            dialog.style.boxSizing =
                "border-box";


            dialog.style.boxShadow =
                "0 20px 60px rgba(0,0,0,0.35)";


            dialog.style.fontFamily =
                "sans-serif";


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


            title.style.fontSize =
                "20px";


            title.style.fontWeight =
                "bold";


            title.style.marginBottom =
                "20px";


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


            presetLabel.style.display =
                "flex";


            presetLabel.style.alignItems =
                "center";


            presetLabel.style.gap =
                "10px";


            presetLabel.style.marginBottom =
                "12px";


            const presetText =
                document.createElement(
                    "span"
                );


            presetText.textContent =
                "プリセット";


            presetText.style.minWidth =
                "80px";


            presetLabel.appendChild(
                presetText
            );


            const presetSelect =
                createSelect(

                    Object.keys(
                        FONT_PRESETS
                    ),

                    selectedPreset

                );


            presetSelect.className =
                "subtitle-font-select";


            presetSelect.style.flex =
                "1";


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


            fontLabel.style.display =
                "flex";


            fontLabel.style.alignItems =
                "center";


            fontLabel.style.gap =
                "10px";


            fontLabel.style.marginBottom =
                "12px";


            const fontText =
                document.createElement(
                    "span"
                );


            fontText.textContent =
                "フォント";


            fontText.style.minWidth =
                "80px";


            fontLabel.appendChild(
                fontText
            );


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


            fontSelect.style.flex =
                "1";


            fontLabel.appendChild(
                fontSelect
            );


            dialog.appendChild(
                fontLabel
            );


            // =================================
            // 文字色
            // =================================

            const textColorControl =
                createColorSelector(

                    "文字色",

                    Object.keys(
                        SUBTITLE_COLORS
                    ),

                    selectedSettings.textColor

                );


            textColorControl.wrapper.style
                .marginBottom =
                "12px";


            dialog.appendChild(
                textColorControl.wrapper
            );


            // =================================
            // 縁色
            // =================================

            const outlineColorControl =
                createColorSelector(

                    "縁色",

                    Object.keys(
                        SUBTITLE_COLORS
                    ),

                    selectedSettings.outlineColor

                );


            outlineColorControl.wrapper.style
                .marginBottom =
                "12px";


            dialog.appendChild(
                outlineColorControl.wrapper
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


            outlineWidthLabel.style.display =
                "flex";


            outlineWidthLabel.style.alignItems =
                "center";


            outlineWidthLabel.style.gap =
                "10px";


            outlineWidthLabel.style.marginBottom =
                "18px";


            const outlineWidthText =
                document.createElement(
                    "span"
                );


            outlineWidthText.textContent =
                "縁の太さ";


            outlineWidthText.style.minWidth =
                "80px";


            outlineWidthLabel.appendChild(
                outlineWidthText
            );


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


            outlineWidthInput.style.width =
                "100px";


            outlineWidthInput.style.boxSizing =
                "border-box";


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


            preview.style.marginTop =
                "10px";


            preview.style.marginBottom =
                "20px";


            preview.style.padding =
                "12px";


            preview.style.background =
                "#f5f5f5";


            preview.style.borderRadius =
                "8px";


            preview.style.border =
                "1px solid #dddddd";


            dialog.appendChild(
                preview
            );


            // =================================
            // プレビュー更新
            // =================================

            function getDialogSettings() {

                const textColor =
                    textColorControl.select.value;


                const outlineColor =
                    outlineColorControl.select.value;


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
                        0;

                }


                outlineWidth =
                    Math.max(
                        0,
                        Math.min(
                            outlineWidth,
                            10
                        )
                    );


                return {

                    font:
                        fontSelect.value,

                    textColor:
                        textColor,

                    textColorHex:
                        getColorHex(
                            textColor
                        ),

                    textColorAss:
                        getColorAss(
                            textColor
                        ),

                    outlineColor:
                        outlineColor,

                    outlineColorHex:
                        getColorHex(
                            outlineColor
                        ),

                    outlineColorAss:
                        getColorAss(
                            outlineColor
                        ),

                    outlineWidth:
                        outlineWidth

                };

            }


            function updatePreviewFromDialog() {

                if (!activeDialogControls) {

                    return;

                }


                const settings =
                    getDialogSettings();


                createSettingsPreview(

                    preview,

                    settings,

                    presetSelect.value

                );

            }


            // グローバル変数へ一時保存
            activeDialogControls = {

                getSettings:
                    getDialogSettings,

                presetSelect:
                    presetSelect,

                fontSelect:
                    fontSelect,

                textColorControl:
                    textColorControl,

                outlineColorControl:
                    outlineColorControl,

                outlineWidthInput:
                    outlineWidthInput

            };


            updatePreviewFromDialog();


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


                    textColorControl.select.value =
                        preset.textColor;


                    outlineColorControl.select.value =
                        preset.outlineColor;


                    outlineWidthInput.value =
                        preset.outlineWidth;


                    textColorControl.update(
                        preset.textColor
                    );


                    outlineColorControl.update(
                        preset.outlineColor
                    );


                    updatePreviewFromDialog();

                }
            );


            // =================================
            // フォント変更
            // =================================

            fontSelect.addEventListener(
                "change",
                function () {

                    updatePreviewFromDialog();

                }
            );


            // =================================
            // 縁太さ変更
            // =================================

            outlineWidthInput.addEventListener(
                "input",
                function () {

                    updatePreviewFromDialog();

                }
            );


            // =================================
            // ボタンエリア
            // =================================

            const buttonArea =
                document.createElement(
                    "div"
                );


            buttonArea.className =
                "subtitle-font-dialog-buttons";


            buttonArea.style.display =
                "flex";


            buttonArea.style.justifyContent =
                "flex-end";


            buttonArea.style.gap =
                "10px";


            buttonArea.style.marginTop =
                "10px";


            // =================================
            // キャンセル
            // =================================

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


            cancelButton.style.padding =
                "10px 18px";


            cancelButton.style.cursor =
                "pointer";


            // =================================
            // 決定
            // =================================

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


            okButton.style.padding =
                "10px 22px";


            okButton.style.cursor =
                "pointer";


            buttonArea.appendChild(
                cancelButton
            );


            buttonArea.appendChild(
                okButton
            );


            dialog.appendChild(
                buttonArea
            );


            // =================================
            // DOMへ追加
            // =================================

            overlay.appendChild(
                dialog
            );


            document.body.appendChild(
                overlay
            );


            activeDialog =
                overlay;


            // =================================
            // 閉じる
            // =================================

            function closeDialog() {

                document.removeEventListener(
                    "keydown",
                    keydownHandler
                );


                if (
                    activeDialog ===
                    overlay
                ) {

                    activeDialog =
                        null;

                }


                activeDialogControls =
                    null;


                if (
                    overlay.parentNode
                ) {

                    overlay.parentNode.removeChild(
                        overlay
                    );

                }

            }


            // =================================
            // キー操作
            // =================================

            function keydownHandler(
                event
            ) {

                if (
                    event.key ===
                    "Escape"
                ) {

                    event.preventDefault();

                    closeDialog();

                    return;

                }


                if (
                    event.key ===
                    "Enter"
                ) {

                    // number inputやselectの操作中に
                    // 意図しない決定を避ける
                    if (
                        event.target &&
                        (
                            event.target.tagName ===
                                "INPUT" ||
                            event.target.tagName ===
                                "SELECT"
                        )
                    ) {

                        return;

                    }


                    event.preventDefault();

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


                    const settings =
                        getDialogSettings();


                    selectedPreset =
                        presetName;


                    selectedSettings =
                        settings;


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
            // ダイアログクリック
            //
            // 背景へのクリック伝播を防止
            // =================================

            dialog.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

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


                event.stopPropagation();


                if (
                    isDisabled
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
            // 現在の設定
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

                        text_color_ass:
                            selectedSettings.textColorAss,

                        outline_color:
                            selectedSettings.outlineColor,

                        outline_color_hex:
                            selectedSettings.outlineColorHex,

                        outline_color_ass:
                            selectedSettings.outlineColorAss,

                        outline_width:
                            selectedSettings.outlineWidth

                    };

                },


            // ---------------------------------
            // プリセット変更
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
            // カラー一覧
            // ---------------------------------

            getColors:
                function () {

                    return Object.keys(
                        SUBTITLE_COLORS
                    );

                },


            // ---------------------------------
            // 色情報取得
            // ---------------------------------

            getColor:
                function (
                    colorName
                ) {

                    if (
                        !SUBTITLE_COLORS[
                            colorName
                        ]
                    ) {

                        return null;

                    }


                    return {

                        name:
                            colorName,

                        hex:
                            SUBTITLE_COLORS[
                                colorName
                            ].hex,

                        ass:
                            SUBTITLE_COLORS[
                                colorName
                            ].ass

                    };

                },


            // ---------------------------------
            // 有効 / 無効
            //
            // subtitle.jsから使用
            // ---------------------------------

            setDisabled:
                function (
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

                },


            // ---------------------------------
            // 無効状態取得
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
