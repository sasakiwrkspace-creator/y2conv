// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// 日本語字幕フォント設定
//
// ・フォント選択
// ・文字色選択
// ・縁取り色選択
// ・縁の太さ
// ・ユーザー登録プリセットとの連携
//
// プリセットそのものの管理・保存は font.js 側で行う。
// subtitle_font.js はプリセットを表示・適用するUIを担当する。
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
        // 初期値
        // =====================================

        const DEFAULT_SETTINGS = {

            preset_name:
                "",

            font:
                "Noto Sans CJK JP",

            text_color:
                "白",

            outline_color:
                "青",

            outline_width:
                3

        };


        // =====================================
        // State
        // =====================================

        let selectedPreset =
            DEFAULT_SETTINGS.preset_name;


        let selectedSettings = {

            ...DEFAULT_SETTINGS

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
                    : (
                        typeof source.presetName === "string"
                            ? source.presetName
                            : ""
                    );


            let font =
                typeof source.font === "string"
                    ? source.font.trim()
                    : DEFAULT_SETTINGS.font;


            if (
                !FONT_LIST.includes(
                    font
                )
            ) {

                font =
                    DEFAULT_SETTINGS.font;

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
                    DEFAULT_SETTINGS.text_color;

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
                    DEFAULT_SETTINGS.outline_color;

            }


            let outlineWidth =
                Number(
                    source.outline_width ??
                    source.outlineWidth ??
                    DEFAULT_SETTINGS.outline_width
                );


            if (
                !Number.isFinite(
                    outlineWidth
                )
            ) {

                outlineWidth =
                    DEFAULT_SETTINGS.outline_width;

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
        // プリセット取得
        //
        // font.js側のAPIに合わせて取得。
        //
        // 対応候補：
        //   window.font.getPresets()
        //   window.font.getPresetList()
        //   window.font.getSettings()
        //   window.fontPresets
        //   window.subtitleFontPresets
        //
        // =====================================

        function getRegisteredPresets() {

            try {

                // ---------------------------------
                // window.font.getPresets()
                // ---------------------------------

                if (
                    window.font &&
                    typeof window.font.getPresets ===
                    "function"
                ) {

                    const presets =
                        window.font.getPresets();

                    if (
                        Array.isArray(
                            presets
                        )
                    ) {

                        return presets;

                    }

                }


                // ---------------------------------
                // window.font.getPresetList()
                // ---------------------------------

                if (
                    window.font &&
                    typeof window.font.getPresetList ===
                    "function"
                ) {

                    const presets =
                        window.font.getPresetList();

                    if (
                        Array.isArray(
                            presets
                        )
                    ) {

                        return presets;

                    }

                }


                // ---------------------------------
                // window.fontPresets
                // ---------------------------------

                if (
                    Array.isArray(
                        window.fontPresets
                    )
                ) {

                    return window.fontPresets;

                }


                // ---------------------------------
                // window.subtitleFontPresets
                // ---------------------------------

                if (
                    Array.isArray(
                        window.subtitleFontPresets
                    )
                ) {

                    return window.subtitleFontPresets;

                }

            }
            catch (error) {

                console.warn(
                    "[SUBTITLE_FONT] プリセット取得エラー:",
                    error
                );

            }


            return [];

        }


        // =====================================
        // プリセット名取得
        // =====================================

        function getPresetName(
            preset
        ) {

            if (
                typeof preset === "string"
            ) {

                return preset;

            }


            if (
                !preset ||
                typeof preset !== "object"
            ) {

                return "";

            }


            return (
                preset.name ??
                preset.preset_name ??
                preset.presetName ??
                preset.title ??
                ""
            );

        }


        // =====================================
        // プリセット設定取得
        // =====================================

        function getPresetSettings(
            preset
        ) {

            if (
                !preset ||
                typeof preset !== "object"
            ) {

                return null;

            }


            if (
                preset.settings &&
                typeof preset.settings === "object"
            ) {

                return normalizeSettings({

                    ...preset.settings,

                    preset_name:
                        getPresetName(
                            preset
                        )

                });

            }


            return normalizeSettings({

                ...preset,

                preset_name:
                    getPresetName(
                        preset
                    )

            });

        }


        // =====================================
        // プリセットをfont.jsから適用
        // =====================================

        function applyPresetFromFontJS(
            presetName
        ) {

            try {

                // ---------------------------------
                // window.font.setPreset()
                // ---------------------------------

                if (
                    window.font &&
                    typeof window.font.setPreset ===
                    "function"
                ) {

                    const result =
                        window.font.setPreset(
                            presetName
                        );


                    // setPreset() が設定値を返す場合
                    if (
                        result &&
                        typeof result === "object"
                    ) {

                        const settings =
                            normalizeSettings({

                                ...result,

                                preset_name:
                                    presetName

                            });


                        selectedPreset =
                            presetName;


                        selectedSettings =
                            settings;


                        return true;

                    }


                    // setPreset後にgetSettings()
                    if (
                        typeof window.font.getSettings ===
                        "function"
                    ) {

                        const settings =
                            window.font.getSettings();


                        if (
                            settings &&
                            typeof settings === "object"
                        ) {

                            selectedPreset =
                                presetName;


                            selectedSettings =
                                normalizeSettings({

                                    ...settings,

                                    preset_name:
                                        presetName

                                });


                            return true;

                        }

                    }

                }

            }
            catch (error) {

                console.warn(
                    "[SUBTITLE_FONT] font.js preset apply error:",
                    error
                );

            }


            return false;

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


            const presetText =
                selectedPreset
                    ? selectedPreset
                    : "カスタム";


            fontButton.title =
                "字幕フォント: " +
                presetText +
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
        // 現在の設定プレビュー
        //
        // プレビュー文字を「現在の設定」ラベルより
        // 上に表示する。
        //
        // フォント・文字色・縁取り色・縁の太さを
        // 現在選択されている値で即時反映する。
        // =====================================
        
        function createSettingsPreview(
            container,
            settings,
            presetName
        ) {
        
            if (!container) {
        
                return;
        
            }
        
        
            // =================================
            // 一度すべて削除
            // =================================
        
            container.innerHTML =
                "";
        
        
            // =================================
            // プレビュー文字
            // =================================
        
            const previewText =
                document.createElement(
                    "div"
                );
        
        
            previewText.className =
                "subtitle-font-preview-text";
        
        
            previewText.textContent =
                "あいうえお ABC 123";
        
        
            // =================================
            // フォント
            // =================================
        
            previewText.style.fontFamily =
                FONT_CSS_MAP[
                    settings.font
                ] ||
                "sans-serif";
        
        
            // =================================
            // 文字色
            // =================================
        
            previewText.style.color =
                getColorHex(
                    settings.textColor
                );
        
        
            // =================================
            // 縁取り
            // =================================
        
            const outlineColor =
                getColorHex(
                    settings.outlineColor
                );
        
        
            const outlineWidth =
                Number(
                    settings.outlineWidth
                ) || 0;
        
        
            // =================================
            // 縁なし
            // =================================
        
            if (
                outlineWidth <= 0
            ) {
        
                previewText.style.textShadow =
                    "none";
        
            }
        
        
            // =================================
            // 縁あり
            // =================================
        
            else {
        
                const shadows = [];
        
        
                for (
                    let x = -outlineWidth;
                    x <= outlineWidth;
                    x++
                ) {
        
                    for (
                        let y = -outlineWidth;
                        y <= outlineWidth;
                        y++
                    ) {
        
                        // 中央の文字そのものは除外
                        if (
                            x === 0 &&
                            y === 0
                        ) {
        
                            continue;
        
                        }
        
        
                        shadows.push(
                            x + "px " +
                            y + "px 0 " +
                            outlineColor
                        );
        
                    }
        
                }
        
        
                previewText.style.textShadow =
                    shadows.join(", ");
        
            }
        
        
            // =================================
            // プレビュー文字を追加
            //
            // ★「現在の設定」より先
            // =================================
        
            container.appendChild(
                previewText
            );
        
        
            // =================================
            // 現在の設定ラベル
            // =================================
        
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
        
        
            // =================================
            // 現在の設定一覧
            // =================================
        
            const values = [
        
                [
                    "プリセット",
                    presetName ||
                    "カスタム"
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
            // 選択中表示
            // =================================

            const selected =
                document.createElement(
                    "div"
                );


            selected.className =
                "subtitle-font-listbox-selected";


            // =================================
            // 選択文字
            // =================================

            const selectedText =
                document.createElement(
                    "span"
                );


            selectedText.className =
                "subtitle-font-listbox-selected-text";


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
            // 表示更新
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
            // リスト閉じる
            // =================================

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


            // =================================
            // リスト開く
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


            // =================================
            // リスト開閉
            // =================================

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
            // 外部値設定
            // =================================

            wrapper.setValue =
                function (
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
        // 色ラジオグループ
        //
        // 重要：
        // input自体は機能として使用するが、
        // 見た目はCSSで非表示にする。
        //
        // 選択中は label.selected による
        // 青枠だけで表示する。
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


                    // ---------------------------------
                    // radio
                    // ---------------------------------

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


                    // ---------------------------------
                    // 色ドット
                    // ---------------------------------

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


                    // ---------------------------------
                    // 色名
                    // ---------------------------------

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


                    // ---------------------------------
                    // 初期選択
                    // ---------------------------------

                    if (
                        input.checked
                    ) {

                        label.classList.add(
                            "selected"
                        );

                    }


                    // ---------------------------------
                    // 変更
                    // ---------------------------------

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


            // =================================
            // 外部から選択状態変更
            // =================================

            group.setValue =
                function (
                    value
                ) {

                    const radios =
                        group.querySelectorAll(
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
                        group.querySelectorAll(
                            ".subtitle-font-radio-label"
                        );


                    labels.forEach(
                        function (label) {

                            const radio =
                                label.querySelector(
                                    "input[type='radio']"
                                );


                            label.classList.toggle(
                                "selected",
                                Boolean(
                                    radio &&
                                    radio.checked
                                )
                            );

                        }
                    );

                };


            // =================================
            // 現在値取得
            // =================================

            group.getValue =
                function () {

                    const radio =
                        group.querySelector(
                            "input[type='radio']:checked"
                        );


                    return radio
                        ? radio.value
                        : null;

                };


            return group;

        }


        // =====================================
        // プリセットボタン生成
        //
        // font.js側の登録セットを表示する。
        // 固定プリセットはここでは定義しない。
        //
        // =====================================

        function createPresetButtons(
            container,
            currentValues,
            updateValues,
            updatePreview
        ) {

            if (!container) {

                return;

            }


            container.innerHTML =
                "";


            const presets =
                getRegisteredPresets();


            if (
                !Array.isArray(
                    presets
                ) ||
                presets.length === 0
            ) {

                const empty =
                    document.createElement(
                        "div"
                    );


                empty.className =
                    "subtitle-font-preset-empty";


                empty.textContent =
                    "登録されているプリセットはありません";


                container.appendChild(
                    empty
                );


                return;

            }


            const presetButtons =
                document.createElement(
                    "div"
                );


            presetButtons.className =
                "subtitle-font-preset-buttons";


            presets.forEach(
                function (preset) {

                    const presetName =
                        getPresetName(
                            preset
                        );


                    if (!presetName) {

                        return;

                    }


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


                            // ---------------------------------
                            // まずfont.js側から適用を試す
                            // ---------------------------------

                            const applied =
                                applyPresetFromFontJS(
                                    presetName
                                );


                            if (
                                applied
                            ) {

                                currentValues.preset =
                                    selectedPreset;


                                currentValues.font =
                                    selectedSettings.font;


                                currentValues.textColor =
                                    selectedSettings.text_color;


                                currentValues.outlineColor =
                                    selectedSettings.outline_color;


                                currentValues.outlineWidth =
                                    selectedSettings.outline_width;

                            }
                            else {

                                // ---------------------------------
                                // プリセットデータから直接適用
                                // ---------------------------------

                                const settings =
                                    getPresetSettings(
                                        preset
                                    );


                                if (!settings) {

                                    return;

                                }


                                currentValues.preset =
                                    presetName;


                                currentValues.font =
                                    settings.font;


                                currentValues.textColor =
                                    settings.text_color;


                                currentValues.outlineColor =
                                    settings.outline_color;


                                currentValues.outlineWidth =
                                    settings.outline_width;

                            }


                            updateValues();


                            updatePreview();

                        }
                    );


                    presetButtons.appendChild(
                        button
                    );

                }
            );


            container.appendChild(
                presetButtons
            );

        }


        // =====================================
        // font.jsへ現在設定を渡す
        // =====================================

        function saveSettingsToFontJS(
            settings
        ) {

            try {

                // ---------------------------------
                // setSubtitleFontSettings()
                // ---------------------------------

                if (
                    window.font &&
                    typeof window.font.setSubtitleFontSettings ===
                    "function"
                ) {

                    window.font.setSubtitleFontSettings(
                        settings
                    );

                    return true;

                }


                // ---------------------------------
                // setSettings()
                // ---------------------------------

                if (
                    window.font &&
                    typeof window.font.setSettings ===
                    "function"
                ) {

                    window.font.setSettings(
                        settings
                    );

                    return true;

                }

            }
            catch (error) {

                console.warn(
                    "[SUBTITLE_FONT] font.js settings save error:",
                    error
                );

            }


            return false;

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

            const presetSection =
                document.createElement(
                    "div"
                );


            presetSection.className =
                "subtitle-font-dialog-label";


            const presetTitle =
                document.createElement(
                    "div"
                );


            presetTitle.className =
                "subtitle-font-dialog-label-title";


            presetTitle.textContent =
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
                "登録セットを表示 ▼";


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
                            ? "登録セットを表示 ▼"
                            : "登録セットを閉じる ▲";

                }
            );


            presetSection.appendChild(
                presetTitle
            );


            presetSection.appendChild(
                presetToggle
            );


            presetSection.appendChild(
                presetContainer
            );


            dialog.appendChild(
                presetSection
            );


            // =================================
            // フォント
            // =================================

            const fontRow =
                document.createElement(
                    "div"
                );


            fontRow.className =
                "subtitle-font-dialog-row";


            const fontLabel =
                document.createElement(
                    "span"
                );


            fontLabel.className =
                "subtitle-font-dialog-row-label";


            fontLabel.textContent =
                "フォント：";


            let fontListBox;


            fontListBox =
                createFontListBox(

                    FONT_LIST,

                    currentValues.font,

                    function (fontName) {

                        currentValues.font =
                            fontName;


                        currentValues.preset =
                            "";


                        updatePreview();

                    }

                );


            fontRow.appendChild(
                fontLabel
            );


            fontRow.appendChild(
                fontListBox
            );


            dialog.appendChild(
                fontRow
            );


            // =================================
            // 文字色
            // =================================

            const textColorRow =
                document.createElement(
                    "div"
                );


            textColorRow.className =
                "subtitle-font-dialog-row";


            const textColorTitle =
                document.createElement(
                    "span"
                );


            textColorTitle.className =
                "subtitle-font-dialog-row-label";


            textColorTitle.textContent =
                "文字色：";


            let textColorRadios;


            textColorRadios =
                createColorRadioGroup(

                    "subtitle-text-color",

                    TEXT_COLORS,

                    currentValues.textColor,

                    function (colorName) {

                        currentValues.textColor =
                            colorName;


                        currentValues.preset =
                            "";


                        updatePreview();

                    }

                );


            textColorRow.appendChild(
                textColorTitle
            );


            textColorRow.appendChild(
                textColorRadios
            );


            dialog.appendChild(
                textColorRow
            );


            // =================================
            // 縁取り色
            // =================================

            const outlineColorRow =
                document.createElement(
                    "div"
                );


            outlineColorRow.className =
                "subtitle-font-dialog-row";


            const outlineColorTitle =
                document.createElement(
                    "span"
                );


            outlineColorTitle.className =
                "subtitle-font-dialog-row-label";


            outlineColorTitle.textContent =
                "縁取り色：";


            let outlineColorRadios;


            outlineColorRadios =
                createColorRadioGroup(

                    "subtitle-outline-color",

                    OUTLINE_COLORS,

                    currentValues.outlineColor,

                    function (colorName) {

                        currentValues.outlineColor =
                            colorName;


                        currentValues.preset =
                            "";


                        updatePreview();

                    }

                );


            outlineColorRow.appendChild(
                outlineColorTitle
            );


            outlineColorRow.appendChild(
                outlineColorRadios
            );


            dialog.appendChild(
                outlineColorRow
            );


            // =================================
            // 縁の太さ
            // =================================

            const outlineWidthRow =
                document.createElement(
                    "div"
                );


            outlineWidthRow.className =
                "subtitle-font-dialog-row";


            const outlineWidthTitle =
                document.createElement(
                    "span"
                );


            outlineWidthTitle.className =
                "subtitle-font-dialog-row-label";


            outlineWidthTitle.textContent =
                "縁の太さ：";


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


            outlineWidthRow.appendChild(
                outlineWidthTitle
            );


            outlineWidthRow.appendChild(
                outlineWidthInput
            );


            dialog.appendChild(
                outlineWidthRow
            );


            // =================================
            // 現在の設定
            // =================================

            dialog.appendChild(
                preview
            );


            // =================================
            // 値更新
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


            function updateTextColorRadios(
                value
            ) {

                if (
                    textColorRadios &&
                    typeof textColorRadios.setValue ===
                    "function"
                ) {

                    textColorRadios.setValue(
                        value
                    );

                }

            }


            function updateOutlineColorRadios(
                value
            ) {

                if (
                    outlineColorRadios &&
                    typeof outlineColorRadios.setValue ===
                    "function"
                ) {

                    outlineColorRadios.setValue(
                        value
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


            // =================================
            // プレビュー更新
            // =================================

            function updatePreview() {

                let width =
                    Number(
                        currentValues.outlineWidth
                    );


                if (
                    !Number.isFinite(
                        width
                    )
                ) {

                    width =
                        DEFAULT_SETTINGS.outline_width;

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
                        !Number.isFinite(
                            width
                        )
                    ) {

                        width =
                            DEFAULT_SETTINGS.outline_width;

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
                        "";


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
                        !Number.isFinite(
                            width
                        )
                    ) {

                        width =
                            DEFAULT_SETTINGS.outline_width;

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


                    selectedSettings =
                        normalizeSettings({

                            preset_name:
                                selectedPreset,

                            font:
                                currentValues.font,

                            text_color:
                                currentValues.textColor,

                            outline_color:
                                currentValues.outlineColor,

                            outline_width:
                                width

                        });


                    // ---------------------------------
                    // font.js側へ通知
                    // ---------------------------------

                    saveSettingsToFontJS(
                        selectedSettings
                    );


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
            // 設定反映
            // ---------------------------------

            setSettings:
                function (
                    settings
                ) {

                    const normalized =
                        normalizeSettings(
                            settings
                        );


                    selectedPreset =
                        normalized.preset_name;


                    selectedSettings =
                        normalized;


                    updateButton();


                    console.log(
                        "[SUBTITLE_FONT] settings set:",
                        selectedSettings
                    );


                    return (
                        this.getSettings()
                    );

                },


            // ---------------------------------
            // プリセット設定
            //
            // font.js側のプリセットを使用
            // ---------------------------------

            setPreset:
                function (
                    presetName
                ) {

                    if (
                        !presetName
                    ) {

                        throw new Error(
                            "プリセット名が指定されていません"
                        );

                    }


                    // ---------------------------------
                    // font.js API
                    // ---------------------------------

                    if (
                        applyPresetFromFontJS(
                            presetName
                        )
                    ) {

                        updateButton();


                        return (
                            this.getSettings()
                        );

                    }


                    // ---------------------------------
                    // 登録済みプリセットを検索
                    // ---------------------------------

                    const presets =
                        getRegisteredPresets();


                    let foundPreset =
                        null;


                    presets.some(
                        function (preset) {

                            const name =
                                getPresetName(
                                    preset
                                );


                            if (
                                name ===
                                presetName
                            ) {

                                foundPreset =
                                    preset;

                                return true;

                            }


                            return false;

                        }
                    );


                    if (
                        !foundPreset
                    ) {

                        throw new Error(
                            "登録されていないプリセットです: " +
                            presetName
                        );

                    }


                    const settings =
                        getPresetSettings(
                            foundPreset
                        );


                    if (!settings) {

                        throw new Error(
                            "プリセット設定を取得できません: " +
                            presetName
                        );

                    }


                    selectedPreset =
                        presetName;


                    selectedSettings =
                        settings;


                    updateButton();


                    console.log(
                        "[SUBTITLE_FONT] preset set:",
                        selectedPreset,
                        selectedSettings
                    );


                    return (
                        this.getSettings()
                    );

                },


            // ---------------------------------
            // プリセット一覧
            // ---------------------------------

            getPresets:
                function () {

                    return getRegisteredPresets()
                        .map(
                            function (preset) {

                                return getPresetName(
                                    preset
                                );

                            }
                        )
                        .filter(
                            function (name) {

                                return Boolean(
                                    name
                                );

                            }
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
