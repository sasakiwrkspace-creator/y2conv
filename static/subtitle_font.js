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
// ・文字色 / 縁取り色の選択
// ・プリセットの折り畳み / 展開
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
//   window.subtitleFont.update()
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
        // Python側のプリセットと
        // 同じ名前を使用する。
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

            }

        };


        // =====================================
        // カラー
        //
        // 表示名とHEXをここで管理。
        //
        // subtitle.js / Python側には
        // 名前とHEXの両方を渡せる。
        // =====================================

        const SUBTITLE_COLORS = {

            "黒":
                "#000000",

            "白":
                "#FFFFFF",

            "赤":
                "#FF0000",

            "青":
                "#0000FF",

            "緑":
                "#008000",

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
        // State
        // =====================================

        let selectedPreset =
            "標準";


        let selectedSettings = {

            font:
                FONT_PRESETS["標準"].font,

            textColor:
                FONT_PRESETS["標準"].textColor,

            textColorHex:
                SUBTITLE_COLORS[
                    FONT_PRESETS["標準"].textColor
                ],

            outlineColor:
                FONT_PRESETS["標準"].outlineColor,

            outlineColorHex:
                SUBTITLE_COLORS[
                    FONT_PRESETS["標準"].outlineColor
                ],

            outlineWidth:
                FONT_PRESETS["標準"].outlineWidth

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
                SUBTITLE_COLORS[
                    colorName
                ] ||
                "#FFFFFF"
            );

        }


        // =====================================
        // 色名正規化
        // =====================================

        function normalizeColorName(
            colorName,
            defaultColor
        ) {

            if (
                Object.prototype.hasOwnProperty.call(
                    SUBTITLE_COLORS,
                    colorName
                )
            ) {

                return colorName;

            }


            return defaultColor;

        }


        // =====================================
        // フォント名正規化
        // =====================================

        function normalizeFontName(
            fontName
        ) {

            if (
                fontName === null ||
                fontName === undefined
            ) {

                return null;

            }


            const value =
                String(
                    fontName
                ).trim();


            if (!value) {

                return null;

            }


            return value;

        }


        // =====================================
        // 縁太さ正規化
        // =====================================

        function normalizeOutlineWidth(
            value
        ) {

            let width =
                Number(
                    value
                );


            if (
                !Number.isFinite(
                    width
                )
            ) {

                width =
                    2;

            }


            width =
                Math.round(
                    width
                );


            width =
                Math.max(
                    0,
                    Math.min(
                        width,
                        10
                    )
                );


            return width;

        }


        // =====================================
        // 現在設定から色HEXを再構築
        // =====================================

        function refreshColorHex() {

            selectedSettings.textColorHex =
                getColorHex(
                    selectedSettings.textColor
                );


            selectedSettings.outlineColorHex =
                getColorHex(
                    selectedSettings.outlineColor
                );

        }


        // =====================================
        // 色ドット作成
        // =====================================

        function createColorDot(
            colorName,
            selected
        ) {

            const dot =
                document.createElement(
                    "span"
                );


            dot.className =
                "subtitle-font-color-dot";


            dot.style.backgroundColor =
                getColorHex(
                    colorName
                );


            // 白色でも見えるようにする
            dot.style.border =
                colorName === "白"
                    ? "1px solid #999"
                    : "1px solid rgba(0,0,0,0.25)";


            if (
                selected
            ) {

                dot.classList.add(
                    "selected"
                );

            }


            return dot;

        }


        // =====================================
        // 色ラジオボタン作成
        // =====================================

        function createColorRadio(
            groupName,
            colorName,
            currentValue
        ) {

            const label =
                document.createElement(
                    "label"
                );


            label.className =
                "subtitle-font-color-radio";


            const input =
                document.createElement(
                    "input"
                );


            input.type =
                "radio";


            input.name =
                groupName;


            input.value =
                colorName;


            input.checked =
                colorName === currentValue;


            const dot =
                createColorDot(

                    colorName,

                    colorName === currentValue

                );


            const text =
                document.createElement(
                    "span"
                );


            text.className =
                "subtitle-font-color-name";


            text.textContent =
                colorName;


            label.appendChild(
                input
            );


            label.appendChild(
                dot
            );


            label.appendChild(
                text
            );


            return {

                label:
                    label,

                input:
                    input,

                dot:
                    dot

            };

        }


        // =====================================
        // ボタン表示
        //
        // 現在の文字色を
        // ボタン文字色へ反映。
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
            // 文字色
            // ---------------------------------

            fontButton.style.color =
                selectedSettings.textColorHex;


            fontButton.style.setProperty(
                "--subtitle-text-color",
                selectedSettings.textColorHex
            );


            // ---------------------------------
            // 縁色
            // ---------------------------------

            fontButton.style.setProperty(
                "--subtitle-outline-color",
                selectedSettings.outlineColorHex
            );


            // ---------------------------------
            // 白文字の場合でも
            // 見やすくする。
            // ---------------------------------

            if (
                selectedSettings.textColor ===
                "白"
            ) {

                fontButton.style.textShadow =
                    "0 1px 2px rgba(0,0,0,0.6)";

            }
            else {

                fontButton.style.textShadow =
                    "none";

            }

        }


        // =====================================
        // select生成
        //
        // フォント選択用
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
        // ラベル作成
        // =====================================

        function createFieldLabel(
            text
        ) {

            const label =
                document.createElement(
                    "div"
                );


            label.className =
                "subtitle-font-dialog-label";


            label.textContent =
                text;


            return label;

        }


        // =====================================
        // 現在の設定表示
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
        // プリセットボタン
        // =====================================

        function createPresetButtons(
            container,
            presetSelect,
            fontSelect,
            textColorInputs,
            outlineColorInputs,
            outlineWidthInput,
            updatePreview,
            updateDialogTitle
        ) {

            container.innerHTML =
                "";


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


                    if (
                        presetName ===
                        selectedPreset
                    ) {

                        button.classList.add(
                            "selected"
                        );

                    }


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


                            // ---------------------------------
                            // プリセット名
                            // ---------------------------------

                            selectedPreset =
                                presetName;


                            presetSelect.value =
                                presetName;


                            // ---------------------------------
                            // フォント
                            // ---------------------------------

                            fontSelect.value =
                                preset.font;


                            // ---------------------------------
                            // 文字色
                            // ---------------------------------

                            textColorInputs.forEach(
                                function (item) {

                                    item.input.checked =
                                        item.input.value ===
                                        preset.textColor;

                                    item.dot.classList.toggle(
                                        "selected",
                                        item.input.checked
                                    );

                                }
                            );


                            // ---------------------------------
                            // 縁取り色
                            // ---------------------------------

                            outlineColorInputs.forEach(
                                function (item) {

                                    item.input.checked =
                                        item.input.value ===
                                        preset.outlineColor;

                                    item.dot.classList.toggle(
                                        "selected",
                                        item.input.checked
                                    );

                                }
                            );


                            // ---------------------------------
                            // 縁太さ
                            // ---------------------------------

                            outlineWidthInput.value =
                                preset.outlineWidth;


                            // ---------------------------------
                            // ダイアログ内設定
                            // ---------------------------------

                            selectedSettings = {

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
                                    normalizeOutlineWidth(
                                        preset.outlineWidth
                                    )

                            };


                            // ---------------------------------
                            // ボタンの選択表示
                            // ---------------------------------

                            Array.from(
                                container.children
                            ).forEach(
                                function (child) {

                                    child.classList.toggle(
                                        "selected",
                                        child === button
                                    );

                                }
                            );


                            // ---------------------------------
                            // タイトル色
                            // ---------------------------------

                            updateDialogTitle();


                            // ---------------------------------
                            // プレビュー
                            // ---------------------------------

                            updatePreview();


                            console.log(
                                "[SUBTITLE_FONT] preset selected:",
                                presetName,
                                selectedSettings
                            );

                        }
                    );


                    container.appendChild(
                        button
                    );

                }
            );

        }


        // =====================================
        // 字幕フォントダイアログ
        // =====================================

        function selectFontPreset() {

            if (
                isDisabled
            ) {

                return;

            }


            // =================================
            // Overlay
            // =================================

            const overlay =
                document.createElement(
                    "div"
                );


            overlay.className =
                "subtitle-font-dialog-overlay";


            // ---------------------------------
            // 重要:
            //
            // fixed表示をCSS側で確実にする。
            // ---------------------------------

            overlay.style.position =
                "fixed";


            overlay.style.inset =
                "0";


            overlay.style.zIndex =
                "99999";


            // =================================
            // Dialog
            // =================================

            const dialog =
                document.createElement(
                    "div"
                );


            dialog.className =
                "subtitle-font-dialog";


            dialog.setAttribute(
                "role",
                "dialog"
            );


            dialog.setAttribute(
                "aria-modal",
                "true"
            );


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
            // プリセット折り畳み
            // =================================

            const presetSection =
                document.createElement(
                    "div"
                );


            presetSection.className =
                "subtitle-font-preset-section";


            const presetHeader =
                document.createElement(
                    "button"
                );


            presetHeader.type =
                "button";


            presetHeader.className =
                "subtitle-font-preset-header";


            presetHeader.setAttribute(
                "aria-expanded",
                "false"
            );


            presetHeader.innerHTML =
                "<span>プリセット</span>" +
                "<span class=\"subtitle-font-preset-arrow\">▼</span>";


            const presetContainer =
                document.createElement(
                    "div"
                );


            presetContainer.className =
                "subtitle-font-preset-container";


            presetContainer.hidden =
                true;


            presetHeader.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    const expanded =
                        presetHeader.getAttribute(
                            "aria-expanded"
                        ) === "true";


                    presetHeader.setAttribute(
                        "aria-expanded",
                        String(
                            !expanded
                        )
                    );


                    presetContainer.hidden =
                        expanded;


                    const arrow =
                        presetHeader.querySelector(
                            ".subtitle-font-preset-arrow"
                        );


                    if (arrow) {

                        arrow.textContent =
                            expanded
                                ? "▼"
                                : "▲";

                    }

                }
            );


            presetSection.appendChild(
                presetHeader
            );


            presetSection.appendChild(
                presetContainer
            );


            dialog.appendChild(
                presetSection
            );


            // =================================
            // プリセットSelect
            //
            // 内部状態確認用
            // UI上では非表示。
            // =================================

            const presetSelect =
                createSelect(

                    Object.keys(
                        FONT_PRESETS
                    ),

                    selectedPreset

                );


            presetSelect.style.display =
                "none";


            dialog.appendChild(
                presetSelect
            );


            // =================================
            // フォント
            // =================================

            const fontField =
                document.createElement(
                    "div"
                );


            fontField.className =
                "subtitle-font-field";


            const fontLabel =
                createFieldLabel(
                    "フォント"
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


            fontField.appendChild(
                fontLabel
            );


            fontField.appendChild(
                fontSelect
            );


            dialog.appendChild(
                fontField
            );


            // =================================
            // 文字色
            // =================================

            const textColorField =
                document.createElement(
                    "div"
                );


            textColorField.className =
                "subtitle-font-color-field";


            const textColorTitle =
                createFieldLabel(
                    "文字色"
                );


            const textColorOptions =
                document.createElement(
                    "div"
                );


            textColorOptions.className =
                "subtitle-font-color-options";


            const textColorInputs =
                [];


            Object.keys(
                SUBTITLE_COLORS
            ).forEach(
                function (colorName) {

                    const item =
                        createColorRadio(

                            "subtitle-text-color",

                            colorName,

                            selectedSettings.textColor

                        );


                    textColorInputs.push(
                        item
                    );


                    textColorOptions.appendChild(
                        item.label
                    );


                    item.input.addEventListener(
                        "change",
                        function () {

                            if (
                                !item.input.checked
                            ) {

                                return;

                            }


                            selectedSettings.textColor =
                                item.input.value;


                            selectedSettings.textColorHex =
                                getColorHex(
                                    item.input.value
                                );


                            // ---------------------------------
                            // タイトル色を変更
                            // ---------------------------------

                            updateDialogTitle();


                            updateColorDotSelection(
                                textColorInputs
                            );


                            updatePreview();

                        }
                    );

                }
            );


            textColorField.appendChild(
                textColorTitle
            );


            textColorField.appendChild(
                textColorOptions
            );


            dialog.appendChild(
                textColorField
            );


            // =================================
            // 縁取り色
            // =================================

            const outlineColorField =
                document.createElement(
                    "div"
                );


            outlineColorField.className =
                "subtitle-font-color-field";


            const outlineColorTitle =
                createFieldLabel(
                    "縁取り色"
                );


            const outlineColorOptions =
                document.createElement(
                    "div"
                );


            outlineColorOptions.className =
                "subtitle-font-color-options";


            const outlineColorInputs =
                [];


            Object.keys(
                SUBTITLE_COLORS
            ).forEach(
                function (colorName) {

                    const item =
                        createColorRadio(

                            "subtitle-outline-color",

                            colorName,

                            selectedSettings.outlineColor

                        );


                    outlineColorInputs.push(
                        item
                    );


                    outlineColorOptions.appendChild(
                        item.label
                    );


                    item.input.addEventListener(
                        "change",
                        function () {

                            if (
                                !item.input.checked
                            ) {

                                return;

                            }


                            selectedSettings.outlineColor =
                                item.input.value;


                            selectedSettings.outlineColorHex =
                                getColorHex(
                                    item.input.value
                                );


                            updateColorDotSelection(
                                outlineColorInputs
                            );


                            updatePreview();

                        }
                    );

                }
            );


            outlineColorField.appendChild(
                outlineColorTitle
            );


            outlineColorField.appendChild(
                outlineColorOptions
            );


            dialog.appendChild(
                outlineColorField
            );


            // =================================
            // 縁の太さ
            // =================================

            const outlineWidthField =
                document.createElement(
                    "div"
                );


            outlineWidthField.className =
                "subtitle-font-field";


            const outlineWidthLabel =
                createFieldLabel(
                    "縁の太さ"
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


            outlineWidthField.appendChild(
                outlineWidthLabel
            );


            outlineWidthField.appendChild(
                outlineWidthInput
            );


            dialog.appendChild(
                outlineWidthField
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


            // =================================
            // タイトル更新
            //
            // 文字色に連動。
            // =================================

            function updateDialogTitle() {

                title.style.color =
                    selectedSettings.textColorHex;


                if (
                    selectedSettings.textColor ===
                    "白"
                ) {

                    title.style.textShadow =
                        "0 1px 2px rgba(0,0,0,0.7)";

                }
                else {

                    title.style.textShadow =
                        "none";

                }

            }


            // =================================
            // ラジオ色ドット更新
            // =================================

            function updateColorDotSelection(
                items
            ) {

                items.forEach(
                    function (item) {

                        item.dot.classList.toggle(
                            "selected",
                            item.input.checked
                        );

                    }
                );

            }


            // =================================
            // 設定値をUIから読み取る
            // =================================

            function syncSettingsFromDialog() {

                const selectedTextInput =
                    textColorInputs.find(
                        function (item) {

                            return item.input.checked;

                        }
                    );


                const selectedOutlineInput =
                    outlineColorInputs.find(
                        function (item) {

                            return item.input.checked;

                        }
                    );


                selectedSettings.font =
                    normalizeFontName(
                        fontSelect.value
                    ) ||
                    "Noto Sans CJK JP";


                if (
                    selectedTextInput
                ) {

                    selectedSettings.textColor =
                        selectedTextInput.input.value;

                }


                if (
                    selectedOutlineInput
                ) {

                    selectedSettings.outlineColor =
                        selectedOutlineInput.input.value;

                }


                selectedSettings.outlineWidth =
                    normalizeOutlineWidth(
                        outlineWidthInput.value
                    );


                refreshColorHex();

            }


            // =================================
            // プレビュー更新
            // =================================

            function updatePreview() {

                syncSettingsFromDialog();


                createSettingsPreview(
                    preview
                );


                updateDialogTitle();

            }


            // =================================
            // プリセットボタン生成
            // =================================

            createPresetButtons(

                presetContainer,

                presetSelect,

                fontSelect,

                textColorInputs,

                outlineColorInputs,

                outlineWidthInput,

                updatePreview,

                updateDialogTitle

            );


            // =================================
            // フォント変更
            // =================================

            fontSelect.addEventListener(
                "change",
                function () {

                    // 手動変更なので
                    // プリセット名は維持する。
                    updatePreview();

                }
            );


            // =================================
            // 縁太さ変更
            // =================================

            outlineWidthInput.addEventListener(
                "input",
                function () {

                    updatePreview();

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
            // Overlay → Dialog
            // =================================

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
            // キーボード
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

                    // 数値入力中のEnter以外
                    // 決定として扱う。

                    if (
                        event.target ===
                        outlineWidthInput
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


                    syncSettingsFromDialog();


                    // ---------------------------------
                    // プリセット名
                    // ---------------------------------

                    const presetName =
                        presetSelect.value ||
                        selectedPreset;


                    selectedPreset =
                        presetName;


                    // ---------------------------------
                    // 最終設定
                    // ---------------------------------

                    selectedSettings =
                        {

                            font:
                                selectedSettings.font,

                            textColor:
                                selectedSettings.textColor,

                            textColorHex:
                                getColorHex(
                                    selectedSettings.textColor
                                ),

                            outlineColor:
                                selectedSettings.outlineColor,

                            outlineColorHex:
                                getColorHex(
                                    selectedSettings.outlineColor
                                ),

                            outlineWidth:
                                normalizeOutlineWidth(
                                    selectedSettings.outlineWidth
                                )

                        };


                    // ---------------------------------
                    // ボタン更新
                    // ---------------------------------

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
            // 初期表示
            // =================================

            updateColorDotSelection(
                textColorInputs
            );


            updateColorDotSelection(
                outlineColorInputs
            );


            updateDialogTitle();


            updatePreview();


            // =================================
            // フォーカス
            // =================================

            setTimeout(
                function () {

                    presetHeader.focus();

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
                    fontButton.disabled ||
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
            // 現在設定
            //
            // subtitle.js → API送信用
            // ---------------------------------

            getSettings:
                function () {

                    refreshColorHex();


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


                    const preset =
                        FONT_PRESETS[
                            presetName
                        ];


                    selectedSettings = {

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
                            normalizeOutlineWidth(
                                preset.outlineWidth
                            )

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
            //
            // subtitle.jsから
            // 処理中に呼び出せる。
            // ---------------------------------

            setDisabled:
                function (
                    disabled
                ) {

                    isDisabled =
                        Boolean(
                            disabled
                        );


                    fontButton.disabled =
                        isDisabled;


                    fontButton.setAttribute(
                        "aria-disabled",
                        String(
                            isDisabled
                        )
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
