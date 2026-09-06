// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// タブ2専用
//
// =====================================
// 役割
// =====================================
//
// ・字幕フォント設定UI
// ・#subtitle-font-button の操作
// ・選択中設定の保持
// ・プリセット管理
// ・フォント選択
// ・文字色選択
// ・縁取り色選択
// ・縁取り太さ選択
// ・subtitle.js への設定提供
//
//
//
// ============================================================
// PYTHON ↔ JAVASCRIPT DATA CONTRACT
// ============================================================
//
// このセクションは、PythonとJavaScriptの
// 「受け渡し仕様」を定義する。
// 
// JS内部のUI・DOM・関数構成を大幅に変更しても、
// Pythonとのデータ連携では、この仕様を維持する。
//
//
// ------------------------------------------------------------
// Python側ファイル
// ------------------------------------------------------------
//
// subtitle_font.py
//
//
// ------------------------------------------------------------
// Python → JavaScript
// ------------------------------------------------------------
//
// Pythonから字幕フォント設定を渡す場合、
// 基本的に以下の意味を持つデータを使用する。
//
// {
//     "preset": "標準",
//     "font": "Noto Sans CJK JP",
//     "text_color": "白",
//     "outline_color": "青",
//     "outline_width": 5
// }
//
//
//
// ------------------------------------------------------------
// JavaScript内部データ
// ------------------------------------------------------------
//
// JS内部ではUI操作の都合上、camelCaseを使用してよい。
//
// {
//     preset:
//         "標準",
//
//     font:
//         "Noto Sans CJK JP",
//
//     textColor:
//         "白",
//
//     textColorHex:
//         "#FFFFFF",
//
//     outlineColor:
//         "青",
//
//     outlineColorHex:
//         "#0000FF",
//
//     outlineWidth:
//         5
// }
//
//
//
// ------------------------------------------------------------
// JavaScript → Python / subtitle.py
// ------------------------------------------------------------
//
// Python側へ渡す設定は以下のキーを使用する。
//
// {
//     "preset_name": "標準",
//     "font": "Noto Sans CJK JP",
//     "text_color": "白",
//     "text_color_hex": "#FFFFFF",
//     "outline_color": "青",
//     "outline_color_hex": "#0000FF",
//     "outline_width": 2
// }
//
//
// 【重要】
//
// Python側とのデータ交換では、
// 以下のsnake_caseキーを正式な外部インターフェースとする。
//
//     preset_name
//     font
//     text_color
//     text_color_hex
//     outline_color
//     outline_color_hex
//     outline_width
//
// JS内部のcamelCaseは自由に変更してよいが、
// getSettings() の戻り値では上記キーを維持する。
//
//
// ------------------------------------------------------------
// 各項目の意味
// ------------------------------------------------------------
//
// preset_name
//     現在選択されているプリセット名
//
//     例:
//         "標準"
//         "ゴシック"
//         "明朝"
//         "太字ゴシック"
//         "太字明朝"
//         "カスタム"
//
//
//
// font
//     字幕に使用するフォント名
//
//     例:
//         "Noto Sans CJK JP"
//         "Noto Serif CJK JP"
//         "IPAGothic"
//         "IPAMincho"
//
//     Python側ではFFmpeg / ASSのFontNameとして使用する。
//
//
//
// text_color
//     字幕文字の色名
//
//     例:
//         "白"
//         "黒"
//         "赤"
//         "青"
//         "黄"
//         "緑"
//         "オレンジ"
//         "水色"
//         "紫"
//
//
//
// text_color_hex
//     字幕文字色のHTML/CSSカラーコード
//
//     例:
//         "白" → "#FFFFFF"
//         "黒" → "#000000"
//         "赤" → "#FF0000"
//         "青" → "#0000FF"
//         "黄" → "#FFFF00"
//
//
//
// outline_color
//     字幕の縁取り色の色名
//
//
//
// outline_color_hex
//     字幕の縁取り色のHTML/CSSカラーコード
//
//
//
// outline_width
//     字幕の縁取り太さ
//
//     整数値で扱う。
//
//     Python側の仕様:
//         最小 0
//         最大 10
//
//     例:
//         0
//         1
//         2
//         3
//
//
// ------------------------------------------------------------
// カラー仕様
// ------------------------------------------------------------
//
// Python側のSUBTITLE_COLORSが正式なカラー定義。
// JS側で使用する色名は、Python側で認識可能な名前を使用する。
//
// 現在の正式カラー:
//
//     白
//     黒
//     赤
//     青
//     黄
//     緑
//     オレンジ
//     水色
//     紫
//
//
//
// ------------------------------------------------------------
// 初期値 / デフォルト値
// ------------------------------------------------------------
//
// Python:
//     DEFAULT_SUBTITLE_PRESET = "標準"
//
// 標準プリセット:
//
//     preset:
//         "標準"
//
//     font:
//         "Noto Sans CJK JP"
//
//     text_color:
//         "白"
//
//     outline_color:
//         "青"
//
//     outline_width:
//         2
//
//
//
// ------------------------------------------------------------
// JS初期値
// ------------------------------------------------------------
//
// JSの初期状態もPython側と一致させる。
//
//     selectedPreset = "標準"
//
//     textColor = "白"
//
//     outlineColor = "青"
//
//     outlineWidth = 2
//
//
//
// ------------------------------------------------------------
// データ連携で変更してはいけないもの
// ------------------------------------------------------------
//
// Pythonとの連携を維持する場合、以下の外部キー名を変更しない。
//
//     preset_name
//     font
//     text_color
//     text_color_hex
//     outline_color
//     outline_color_hex
//     outline_width
//
//
//
// ------------------------------------------------------------
// データ連携上の注意
// ------------------------------------------------------------
//
// 1.
// JS内部の変数名は変更可能。
//
// 例:
//     textColor
//     →
//     currentTextColor
//
// ただし getSettings() の戻り値は変更しない。
//
//
// 2.
// UIのHTML構造は変更可能。
//
//
// 3.
// CSSクラス名は変更可能。
//
//
// 4.
// ダイアログの構成は変更可能。
//
//
// 5.
// プリセットボタンの実装方法は変更可能。
//
//
// 6.
// Python側へ渡すデータの意味と外部キーは維持する。
//
//
// ============================================================
// subtitle.js から使用する公開API
// ============================================================
//
// window.subtitleFont.getPreset()
//
//     現在のプリセット名を取得。
//
//
// window.subtitleFont.setPreset("ゴシック")
//
//     プリセットを変更。
//
//
// window.subtitleFont.getPresets()
//
//     利用可能なプリセット一覧を取得。
//
//
// window.subtitleFont.getSettings()
//
//     Python / subtitle.js連携用の現在設定を取得。
//
//     戻り値:
//
//     {
//         "preset_name": "標準",
//         "font": "Noto Sans CJK JP",
//         "text_color": "白",
//         "text_color_hex": "#FFFFFF",
//         "outline_color": "青",
//         "outline_color_hex": "#0000FF",
//         "outline_width": 2
//     }
//
//
// window.subtitleFont.setDisabled(true)
//
//     UIを無効化。
//
//
// window.subtitleFont.isDisabled()
//
//     UIが無効状態か取得。
//
//
// window.subtitleFont.update()
//
//     ボタン表示を更新。
//
//
// ============================================================
// FFmpeg / ASS連携について
// ============================================================
//
// JSはFFmpegのforce_styleを直接生成しない。
//
// JS:
//     色名
//     HEX
//     フォント名
//     縁太さ
//
// ↓
//
// subtitle.py
//
// ↓
//
// Python側でASS / FFmpeg用の値へ変換する。
//
//
// Python側では、例えば:
//
//     font
//     text_color
//     outline_color
//     outline_width
//
// を使用して字幕処理を行う。
//
//
// ============================================================
// このコメントより下のJS実装について
// ============================================================
//
// このコメントは「データ契約」であり、
// UI実装そのものを規定するものではない。
//
// 将来的に:
//
// ・UIを変更
// ・ダイアログを変更
// ・CSSを変更
// ・プリセットUIを変更
// ・ラジオボタンを変更
// ・selectを変更
// ・関数を分割
// ・関数を統合
// ・DOM構造を変更
//
// しても、Pythonとの受け渡し仕様を維持する限り、
// subtitle.js / subtitle.pyとの連携を維持できる。
//
//
//
// ============================================================
// ここから実装
// ============================================================


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


            "ゴシック": {

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


            "明朝": {

                font:
                    "Noto Serif CJK JP",

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


            "太字ゴシック": {

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
                    "青",

                outlineColorHex:
                    "#0000FF",

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
                "#FF0000",

            "青":
                "#0000FF",

            "黄":
                "#FFFF00",

            "緑":
                "#00FF00",

            "オレンジ":
                "#FFA500",

            "水色":
                "#00FFFF",

            "紫":
                "#800080"

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
            "黄"

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


                            const allLabels =
                                group.querySelectorAll(
                                    ".subtitle-font-radio-label"
                                );


                            allLabels.forEach(
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

                        "Noto Sans CJK JP",

                        "Noto Sans JP",

                        "Noto Serif CJK JP",

                        "Noto Serif JP",

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
                        0;

                }


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
            //
            // ★ Python / subtitle.jsとの
            //    外部データインターフェース
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
