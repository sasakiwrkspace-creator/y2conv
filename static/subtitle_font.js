// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// 日本語字幕フォント設定
//
// フォント選択リストをカスタムリストボックス化。
// 各フォント名を、そのフォント自身で表示する。
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
        // フォント一覧
        // =====================================

        const FONT_LIST = [

            "Noto Sans CJK JP",

            "Noto Serif CJK JP",

            "Noto Sans JP",

            "Noto Serif JP",

            "IPAGothic",

            "IPAMincho"

        ];


        // =====================================
        // フォントCSS名
        // =====================================

        const FONT_CSS_MAP = {

            "Noto Sans CJK JP":
                "'Noto Sans CJK JP'",

            "Noto Serif CJK JP":
                "'Noto Serif CJK JP'",

            "Noto Sans JP":
                "'Noto Sans JP'",

            "Noto Serif JP":
                "'Noto Serif JP'",

            "IPAGothic":
                "'IPAGothic'",

            "IPAMincho":
                "'IPAMincho'"

        };


        // =====================================
        // プリセット
        //
        // 不要な重複プリセットは削除。
        //
        // 標準：
        //   白文字 + 青縁
        //
        // 赤文字：
        //   赤文字 + シアン縁
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
                    "青",

                outlineColorHex:
                    "#0000FF",

                outlineWidth:
                    5

            },


            "赤文字": {

                font:
                    "Noto Serif CJK JP",

                textColor:
                    "赤",

                textColorHex:
                    "#FF0000",

                outlineColor:
                    "シアン",

                outlineColorHex:
                    "#00FFFF",

                outlineWidth:
                    5

            }

        };


        // =====================================
        // 色
        // =====================================

        const COLOR_MAP = {

            "白":
                "#FFFFFF",

            "黒":
                "#000000",

            "赤":
                "#FF0000",

            "青":
                "#0000FF",

            "黄":
                "#FFFF00",

            "シアン":
                "#00FFFF"

        };


        const TEXT_COLORS = [

            "白",
            "黒",
            "赤",
            "青",
            "黄"

        ];


        const OUTLINE_COLORS = [

            "白",
            "黒",
            "赤",
            "青",
            "黄",
            "シアン"

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
        // 設定を正規化
        // =====================================

        function normalizeSettings(
            settings
        ) {

            const source =
                settings &&
                typeof settings === "object"
                    ? settings
                    : {};


            let presetName =
                typeof source.preset_name === "string"
                    ? source.preset_name
                    : "標準";


            if (
                presetName !== "カスタム" &&
                !FONT_PRESETS[presetName]
            ) {

                presetName =
                    "標準";

            }


            let font =
                typeof source.font === "string"
                    ? source.font.trim()
                    : "Noto Sans CJK JP";


            if (
                !FONT_LIST.includes(font)
            ) {

                font =
                    "Noto Sans CJK JP";

            }


            let textColor =
                typeof source.text_color === "string"
                    ? source.text_color
                    : source.textColor;


            if (
                !TEXT_COLORS.includes(
                    textColor
                )
            ) {

                textColor =
                    "白";

            }


            let outlineColor =
                typeof source.outline_color === "string"
                    ? source.outline_color
                    : source.outlineColor;


            if (
                !OUTLINE_COLORS.includes(
                    outlineColor
                )
            ) {

                outlineColor =
                    "青";

            }


            let outlineWidth =
                Number(
                    source.outline_width ??
                    source.outlineWidth ??
                    5
                );


            if (
                !Number.isFinite(
                    outlineWidth
                )
            ) {

                outlineWidth =
                    5;

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


            return {

                preset_name:
                    presetName,

                font:
                    font,

                text_color:
                    textColor,

                text_color_hex:
                    getColorHex(
                        textColor
                    ),

                outline_color:
                    outlineColor,

                outline_color_hex:
                    getColorHex(
                        outlineColor
                    ),

                outline_width:
                    outlineWidth

            };

        }


        // =====================================
        // ボタン色
        // =====================================

        function updateButtonColor() {

            fontButton.style.setProperty(
                "--subtitle-font-button-color",
                selectedSettings.text_color_hex
            );


            fontButton.style.color =
                selectedSettings.text_color_hex;

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
                selectedSettings.text_color +
                " / 縁取り色 " +
                selectedSettings.outline_color +
                " / 縁 " +
                selectedSettings.outline_width;


            fontButton.style.setProperty(
                "--subtitle-text-color",
                selectedSettings.text_color_hex
            );


            fontButton.style.setProperty(
                "--subtitle-outline-color",
                selectedSettings.outline_color_hex
            );


            updateButtonColor();


            fontButton.disabled =
                isDisabled;

        }


        // =====================================
        // 無効化
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
        // プレビュー
        // =====================================

        function createSettingsPreview(
            container,
            settings,
            presetName
        ) {

            if (!container) {

                return;

            }


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
                    "縁取り色",
                    settings.outlineColor
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
                        item[0] + "：";


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
        // フォントリストボックス
        // =====================================

        function createFontListBox(
            options,
            value,
            onChange
        ) {

            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "subtitle-font-listbox";


            wrapper.setAttribute(
                "role",
                "combobox"
            );


            wrapper.setAttribute(
                "aria-expanded",
                "false"
            );


            wrapper.setAttribute(
                "tabindex",
                "0"
            );


            // =================================
            // 選択中の表示
            // =================================

            const selected =
                document.createElement(
                    "div"
                );


            selected.className =
                "subtitle-font-listbox-selected";


            // =================================
            // 矢印
            // =================================

            const arrow =
                document.createElement(
                    "span"
                );


            arrow.className =
                "subtitle-font-listbox-arrow";


            arrow.textContent =
                "▼";


            // =================================
            // 選択文字
            // =================================

            const selectedText =
                document.createElement(
                    "span"
                );


            selectedText.className =
                "subtitle-font-listbox-selected-text";


            selected.appendChild(
                selectedText
            );


            selected.appendChild(
                arrow
            );


            wrapper.appendChild(
                selected
            );


            // =================================
            // リスト
            // =================================

            const list =
                document.createElement(
                    "div"
                );


            list.className =
                "subtitle-font-listbox-options";


            list.hidden =
                true;


            list.setAttribute(
                "role",
                "listbox"
            );


            wrapper.appendChild(
                list
            );


            let currentValue =
                value;


            // =================================
            // 選択表示更新
            // =================================

            function updateSelectedDisplay() {

                selectedText.textContent =
                    currentValue;


                selectedText.style.fontFamily =
                    FONT_CSS_MAP[
                        currentValue
                    ] ||
                    "sans-serif";

            }


            // =================================
            // 選択
            // =================================

            function selectValue(
                newValue
            ) {

                if (
                    !options.includes(
                        newValue
                    )
                ) {

                    return;

                }


                currentValue =
                    newValue;


                updateSelectedDisplay();


                const optionElements =
                    list.querySelectorAll(
                        ".subtitle-font-listbox-option"
                    );


                optionElements.forEach(
                    function (optionElement) {

                        const isSelected =
                            optionElement.dataset.value ===
                            currentValue;


                        optionElement.classList.toggle(
                            "selected",
                            isSelected
                        );


                        optionElement.setAttribute(
                            "aria-selected",
                            String(
                                isSelected
                            )
                        );

                    }
                );


                closeList();


                onChange(
                    currentValue
                );

            }


            // =================================
            // リスト開閉
            // =================================

            function openList() {

                if (
                    wrapper.classList.contains(
                        "disabled"
                    )
                ) {

                    return;

                }


                list.hidden =
                    false;


                wrapper.classList.add(
                    "open"
                );


                wrapper.setAttribute(
                    "aria-expanded",
                    "true"
                );

            }


            function closeList() {

                list.hidden =
                    true;


                wrapper.classList.remove(
                    "open"
                );


                wrapper.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }


            function toggleList() {

                if (
                    list.hidden
                ) {

                    openList();

                }
                else {

                    closeList();

                }

            }


            // =================================
            // 項目生成
            // =================================

            options.forEach(
                function (fontName) {

                    const option =
                        document.createElement(
                            "div"
                        );


                    option.className =
                        "subtitle-font-listbox-option";


                    option.dataset.value =
                        fontName;


                    option.setAttribute(
                        "role",
                        "option"
                    );


                    option.setAttribute(
                        "aria-selected",
                        String(
                            fontName ===
                            currentValue
                        )
                    );


                    option.textContent =
                        fontName;


                    // 各フォント自身で表示
                    option.style.fontFamily =
                        FONT_CSS_MAP[
                            fontName
                        ] ||
                        "sans-serif";


                    if (
                        fontName ===
                        currentValue
                    ) {

                        option.classList.add(
                            "selected"
                        );

                    }


                    option.addEventListener(
                        "click",
                        function (event) {

                            event.preventDefault();

                            event.stopPropagation();


                            selectValue(
                                fontName
                            );

                        }
                    );


                    list.appendChild(
                        option
                    );

                }
            );


            // =================================
            // クリック
            // =================================

            selected.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();


                    toggleList();

                }
            );


            // =================================
            // キーボード
            // =================================

            wrapper.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key ===
                        "Enter" ||
                        event.key ===
                        " "
                    ) {

                        event.preventDefault();

                        toggleList();

                        return;

                    }


                    if (
                        event.key ===
                        "Escape"
                    ) {

                        event.preventDefault();

                        closeList();

                        return;

                    }


                    if (
                        event.key ===
                        "ArrowDown"
                    ) {

                        event.preventDefault();

                        const index =
                            options.indexOf(
                                currentValue
                            );


                        const nextIndex =
                            Math.min(
                                options.length - 1,
                                index + 1
                            );


                        if (
                            options[nextIndex]
                        ) {

                            selectValue(
                                options[nextIndex]
                            );

                        }

                        return;

                    }


                    if (
                        event.key ===
                        "ArrowUp"
                    ) {

                        event.preventDefault();

                        const index =
                            options.indexOf(
                                currentValue
                            );


                        const previousIndex =
                            Math.max(
                                0,
                                index - 1
                            );


                        if (
                            options[previousIndex]
                        ) {

                            selectValue(
                                options[
                                    previousIndex
                                ]
                            );

                        }

                    }

                }
            );


            // =================================
            // 初期表示
            // =================================

            updateSelectedDisplay();


            // =================================
            // 外部から値変更
            // =================================

            wrapper.setValue =
                function (
                    newValue
                ) {

                    if (
                        options.includes(
                            newValue
                        )
                    ) {

                        currentValue =
                            newValue;


                        updateSelectedDisplay();


                        const optionElements =
                            list.querySelectorAll(
                                ".subtitle-font-listbox-option"
                            );


                        optionElements.forEach(
                            function (optionElement) {

                                const isSelected =
                                    optionElement.dataset.value ===
                                    currentValue;


                                optionElement.classList.toggle(
                                    "selected",
                                    isSelected
                                );


                                optionElement.setAttribute(
                                    "aria-selected",
                                    String(
                                        isSelected
                                    )
                                );

                            }
                        );

                    }

                };


            // =================================
            // 現在値取得
            // =================================

            wrapper.getValue =
                function () {

                    return currentValue;

                };


            // =================================
            // 無効化
            // =================================

            wrapper.setDisabled =
                function (
                    disabled
                ) {

                    const state =
                        Boolean(
                            disabled
                        );


                    wrapper.classList.toggle(
                        "disabled",
                        state
                    );


                    wrapper.setAttribute(
                        "aria-disabled",
                        String(
                            state
                        )
                    );

                };


            return wrapper;

        }


        // =====================================
        // 色ラジオ
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


                    text.className =
                        "subtitle-font-radio-text";


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


                    if (
                        input.checked
                    ) {

                        label.classList.add(
                            "selected"
                        );

                    }


                    input.addEventListener(
                        "change",
                        function () {

                            if (
                                !input.checked
                            ) {

                                return;

                            }


                            const labels =
                                group.querySelectorAll(
                                    ".subtitle-font-radio-label"
                                );


                            labels.forEach(
                                function (item) {

                                    item.classList.remove(
                                        "selected"
                                    );

                                }
                            );


                            label.classList.add(
                                "selected"
                            );


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
        // プリセットボタン
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
                    selectedSettings.text_color,

                outlineColor:
                    selectedSettings.outline_color,

                outlineWidth:
                    selectedSettings.outline_width

            };


            // =================================
            // プレビュー
            // =================================

            const preview =
                document.createElement(
                    "div"
                );


            preview.className =
                "subtitle-font-preview";


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


            // =================================
            // フォント選択用変数
            // =================================

            let fontListBox;


            // =================================
            // フォント変更反映
            // =================================

            function updateFontValue() {

                if (
                    fontListBox
                ) {

                    fontListBox.setValue(
                        currentValues.font
                    );

                }

            }


            // =================================
            // プリセット生成
            // =================================

            createPresetButtons(

                presetContainer,

                currentValues,

                function () {

                    updateFontValue();


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
                    "div"
                );


            fontLabel.className =
                "subtitle-font-dialog-label";


            fontLabel.textContent =
                "フォント";


            fontListBox =
                createFontListBox(

                    FONT_LIST,

                    currentValues.font,

                    function (fontName) {

                        currentValues.font =
                            fontName;


                        currentValues.preset =
                            "カスタム";


                        updatePreview();

                    }

                );


            fontLabel.appendChild(
                fontListBox
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


                const labels =
                    textColorRadios.querySelectorAll(
                        ".subtitle-font-radio-label"
                    );


                labels.forEach(
                    function (label) {

                        const radio =
                            label.querySelector(
                                "input[type='radio']"
                            );


                        if (
                            radio &&
                            radio.checked
                        ) {

                            label.classList.add(
                                "selected"
                            );

                        }
                        else {

                            label.classList.remove(
                                "selected"
                            );

                        }

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


                        currentValues.preset =
                            "カスタム";


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


                const labels =
                    outlineColorRadios.querySelectorAll(
                        ".subtitle-font-radio-label"
                    );


                labels.forEach(
                    function (label) {

                        const radio =
                            label.querySelector(
                                "input[type='radio']"
                            );


                        if (
                            radio &&
                            radio.checked
                        ) {

                            label.classList.add(
                                "selected"
                            );

                        }
                        else {

                            label.classList.remove(
                                "selected"
                            );

                        }

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


                        currentValues.preset =
                            "カスタム";


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
                "10";


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

            dialog.appendChild(
                preview
            );


            // =================================
            // プレビュー更新
            // =================================

            function updatePreview() {

                let width =
                    Number(
                        currentValues.outlineWidth
                    );


                if (
                    !Number.isFinite(width)
                ) {

                    width =
                        5;

                }


                width =
                    Math.max(
                        0,
                        Math.min(
                        10,
                            Math.round(
                                width
                            )
                        )
                    );


                const previewSettings = {

                    font:
                        currentValues.font,

                    textColor:
                        currentValues.textColor,

                    outlineColor:
                        currentValues.outlineColor,

                    outlineWidth:
                        width

                };


                createSettingsPreview(

                    preview,

                    previewSettings,

                    currentValues.preset

                );

            }


            updatePreview();


            // =================================
            // 縁太さ変更
            // =================================

            outlineWidthInput.addEventListener(
                "input",
                function () {

                    let width =
                        Number(
                            outlineWidthInput.value
                        );


                    if (
                        !Number.isFinite(width)
                    ) {

                        width =
                            5;

                    }


                    width =
                        Math.max(
                            0,
                            Math.min(
                                10,
                                Math.round(
                                    width
                                )
                            )
                        );


                    currentValues.outlineWidth =
                        width;


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
            // キーボード
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
                        (
                            event.target.tagName ===
                            "INPUT" ||
                            event.target.tagName ===
                            "SELECT"
                        )
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
                            5;

                    }


                    width =
                        Math.max(
                            0,
                            Math.min(
                                10,
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

                        text_color:
                            currentValues.textColor,

                        text_color_hex:
                            getColorHex(
                                currentValues.textColor
                            ),

                        outline_color:
                            currentValues.outlineColor,

                        outline_color_hex:
                            getColorHex(
                                currentValues.outlineColor
                            ),

                        outline_width:
                            width

                    };


                    updateButton();


                    console.log(
                        "[SUBTITLE_FONT] settings selected:",
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
        // 外部API
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
            // 設定取得
            // ---------------------------------

            getSettings:
                function () {

                    return {

                        preset_name:
                            selectedPreset,

                        font:
                            selectedSettings.font,

                        text_color:
                            selectedSettings.text_color,

                        text_color_hex:
                            selectedSettings.text_color_hex,

                        outline_color:
                            selectedSettings.outline_color,

                        outline_color_hex:
                            selectedSettings.outline_color_hex,

                        outline_width:
                            selectedSettings.outline_width

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

                        text_color:
                            preset.textColor,

                        text_color_hex:
                            preset.textColorHex,

                        outline_color:
                            preset.outlineColor,

                        outline_color_hex:
                            preset.outlineColorHex,

                        outline_width:
                            preset.outlineWidth

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


        // =====================================
        // window.subtitleFont
        // =====================================

        window.subtitleFont =
            fontObject;


        // =====================================
        // 初期表示
        // =====================================

        updateButton();


        // =====================================
        // 起動時デバッグ
        // =====================================

        console.log(
            "[SUBTITLE_FONT] initial settings:",
            window.subtitleFont.getSettings()
        );


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
