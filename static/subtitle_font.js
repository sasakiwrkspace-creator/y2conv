// =====================================
// YouTube Converter - Subtitle Font
// subtitle_font.js
//
// タブ2専用
//
// 役割:
// ・字幕フォント選択UI
// ・#subtitle-font-button の操作
// ・字幕フォント設定ダイアログ
// ・プリセット管理
// ・文字色 / 縁色 / 縁太さ / フォント管理
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
        // カラー設定
        //
        // subtitle_font.py の
        // SUBTITLE_COLORS と対応。
        //
        // hex:
        //   CSS表示用
        //
        // =====================================

        const SUBTITLE_COLORS = {

            "白": {
                hex: "#FFFFFF"
            },

            "黒": {
                hex: "#000000"
            },

            "赤": {
                hex: "#FF0000"
            },

            "青": {
                hex: "#0000FF"
            },

            "黄": {
                hex: "#FFFF00"
            },

            "緑": {
                hex: "#00FF00"
            },

            "オレンジ": {
                hex: "#FFA500"
            },

            "水色": {
                hex: "#00FFFF"
            },

            "紫": {
                hex: "#800080"
            }

        };


        // =====================================
        // UI基本カラー
        //
        // 現在は5色。
        // =====================================

        const BASIC_COLORS = [

            "白",

            "黒",

            "赤",

            "青",

            "黄"

        ];


        // =====================================
        // フォント一覧
        //
        // subtitle_font.py と対応。
        // =====================================

        const AVAILABLE_FONTS = [

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

        ];


        // =====================================
        // プリセット
        //
        // subtitle_font.py と同じ名前を使用。
        //
        // ここは将来的にAPIから取得する
        // ことも可能。
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
        // ダイアログ管理
        //
        // 重要:
        //
        // ダイアログを毎回増やさない。
        // 現在表示中のダイアログを1個だけ管理する。
        // =====================================

        let activeDialog = null;


        // =====================================
        // 設定コピー
        // =====================================

        function cloneSettings(
            settings
        ) {

            return {

                font:
                    settings.font,

                textColor:
                    settings.textColor,

                textColorHex:
                    settings.textColorHex,

                outlineColor:
                    settings.outlineColor,

                outlineColorHex:
                    settings.outlineColorHex,

                outlineWidth:
                    settings.outlineWidth

            };

        }


        // =====================================
        // プリセットから設定作成
        // =====================================

        function createSettingsFromPreset(
            presetName
        ) {

            const preset =
                FONT_PRESETS[
                    presetName
                ];


            if (!preset) {

                return {

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

        }


        // =====================================
        // 太さ正規化
        // =====================================

        function normalizeOutlineWidth(
            value
        ) {

            let number =
                Number(
                    value
                );


            if (
                !Number.isFinite(
                    number
                )
            ) {

                number = 2;

            }


            number =
                Math.round(
                    number
                );


            number =
                Math.max(
                    0,
                    Math.min(
                        number,
                        10
                    )
                );


            return number;

        }


        // =====================================
        // HEX取得
        // =====================================

        function getColorHex(
            colorName
        ) {

            if (
                SUBTITLE_COLORS[
                    colorName
                ]
            ) {

                return (
                    SUBTITLE_COLORS[
                        colorName
                    ].hex
                );

            }


            return "#FFFFFF";

        }


        // =====================================
        // カラー情報取得
        // =====================================

        function getColorInfo(
            colorName
        ) {

            return {

                name:
                    colorName,

                hex:
                    getColorHex(
                        colorName
                    )

            };

        }


        // =====================================
        // 「字幕フォント」表示更新
        //
        // 今回の重要関数。
        //
        // パラメータが変わったときに
        // この関数を呼び出す。
        // =====================================

        function updateSubtitleFontLabel(
            settings = selectedSettings
        ) {

            if (!settings) {

                return;

            }


            const font =
                settings.font ||
                "Noto Sans CJK JP";


            const textColor =
                settings.textColor ||
                "白";


            const outlineColor =
                settings.outlineColor ||
                "黒";


            const outlineWidth =
                normalizeOutlineWidth(
                    settings.outlineWidth
                );


            // ---------------------------------
            // ボタン名
            //
            // ボタン本体は
            // 「字幕フォント」
            // のまま。
            // ---------------------------------

            fontButton.textContent =
                "字幕フォント";


            // ---------------------------------
            // title
            //
            // マウスを乗せた場合の詳細。
            // ---------------------------------

            fontButton.title =
                "フォント: " +
                font +
                " / 文字色: " +
                textColor +
                " / 縁色: " +
                outlineColor +
                " / 縁: " +
                outlineWidth;


            // ---------------------------------
            // CSS変数
            // ---------------------------------

            fontButton.style.setProperty(

                "--subtitle-text-color",

                getColorHex(
                    textColor
                )

            );


            fontButton.style.setProperty(

                "--subtitle-outline-color",

                getColorHex(
                    outlineColor
                )

            );


            console.log(
                "[SUBTITLE_FONT] label updated:",
                font,
                textColor,
                outlineColor,
                outlineWidth
            );

        }


        // =====================================
        // 色ドット生成
        // =====================================

        function createColorDot(
            colorName
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


            dot.title =
                colorName +
                " " +
                getColorHex(
                    colorName
                );


            return dot;

        }


        // =====================================
        // 色ボタン生成
        // =====================================

        function createColorButton(
            colorName,
            selectedColor,
            onClick
        ) {

            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.className =
                "subtitle-font-color-button";


            button.dataset.color =
                colorName;


            // ---------------------------------
            // 選択状態
            // ---------------------------------

            if (
                colorName ===
                selectedColor
            ) {

                button.classList.add(
                    "selected"
                );

            }


            // ---------------------------------
            // ●
            // ---------------------------------

            button.appendChild(
                createColorDot(
                    colorName
                )
            );


            // ---------------------------------
            // 色名
            // ---------------------------------

            const name =
                document.createElement(
                    "span"
                );


            name.className =
                "subtitle-font-color-name";


            name.textContent =
                colorName;


            button.appendChild(
                name
            );


            // ---------------------------------
            // HEX
            //
            // 小さく表示。
            // ---------------------------------

            const hex =
                document.createElement(
                    "span"
                );


            hex.className =
                "subtitle-font-color-hex";


            hex.textContent =
                getColorHex(
                    colorName
                );


            button.appendChild(
                hex
            );


            // ---------------------------------
            // title
            // ---------------------------------

            button.title =
                colorName +
                " " +
                getColorHex(
                    colorName
                );


            // ---------------------------------
            // click
            // ---------------------------------

            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    onClick(
                        colorName
                    );

                }
            );


            return button;

        }


        // =====================================
        // フォントselect生成
        // =====================================

        function createFontSelect(
            currentFont
        ) {

            const select =
                document.createElement(
                    "select"
                );


            select.className =
                "subtitle-font-select";


            AVAILABLE_FONTS.forEach(
                function (fontName) {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        fontName;


                    option.textContent =
                        fontName;


                    if (
                        fontName ===
                        currentFont
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
        // 設定行生成
        //
        // ラベルと値を1行にする。
        // =====================================

        function createSettingRow(
            labelText,
            valueText,
            valueColor = null
        ) {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "subtitle-font-setting-row";


            const label =
                document.createElement(
                    "div"
                );


            label.className =
                "subtitle-font-setting-label";


            label.textContent =
                labelText;


            const value =
                document.createElement(
                    "div"
                );


            value.className =
                "subtitle-font-setting-value";


            if (valueColor) {

                const dot =
                    createColorDot(
                        valueColor
                    );


                value.appendChild(
                    dot
                );

            }


            const text =
                document.createElement(
                    "span"
                );


            text.textContent =
                valueText;


            value.appendChild(
                text
            );


            row.appendChild(
                label
            );


            row.appendChild(
                value
            );


            return row;

        }


        // =====================================
        // 現在の設定表示
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


            container.appendChild(

                createSettingRow(

                    "プリセット",

                    presetName

                )

            );


            container.appendChild(

                createSettingRow(

                    "フォント",

                    settings.font

                )

            );


            container.appendChild(

                createSettingRow(

                    "文字色",

                    settings.textColor,

                    settings.textColor

                )

            );


            container.appendChild(

                createSettingRow(

                    "縁色",

                    settings.outlineColor,

                    settings.outlineColor

                )

            );


            container.appendChild(

                createSettingRow(

                    "縁の太さ",

                    String(
                        settings.outlineWidth
                    )

                )

            );

        }


        // =====================================
        // プリセットエリア
        //
        // 展開 / 折り畳み
        // =====================================

        function createPresetArea(
            dialog,
            workingSettings,
            closeDialog
        ) {

            const area =
                document.createElement(
                    "div"
                );


            area.className =
                "subtitle-font-preset-area";


            // ---------------------------------
            // ヘッダー
            // ---------------------------------

            const header =
                document.createElement(
                    "div"
                );


            header.className =
                "subtitle-font-preset-header";


            const label =
                document.createElement(
                    "span"
                );


            label.className =
                "subtitle-font-dialog-label";


            label.textContent =
                "プリセット";


            const toggleButton =
                document.createElement(
                    "button"
                );


            toggleButton.type =
                "button";


            toggleButton.className =
                "subtitle-font-preset-toggle";


            toggleButton.textContent =
                "プリセット ▼";


            header.appendChild(
                label
            );


            header.appendChild(
                toggleButton
            );


            area.appendChild(
                header
            );


            // ---------------------------------
            // プリセットボタン群
            // ---------------------------------

            const buttonArea =
                document.createElement(
                    "div"
                );


            buttonArea.className =
                "subtitle-font-preset-buttons";


            buttonArea.hidden =
                true;


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


                            // ---------------------------------
                            // プリセットを正式適用
                            //
                            // プリセットは
                            // 「決定」を押さなくても
                            // クリック時点で適用する。
                            // ---------------------------------

                            selectedPreset =
                                presetName;


                            selectedSettings =
                                createSettingsFromPreset(
                                    presetName
                                );


                            updateSubtitleFontLabel();


                            console.log(
                                "[SUBTITLE_FONT] preset applied:",
                                presetName,
                                selectedSettings
                            );


                            // ---------------------------------
                            // ダイアログを閉じる
                            // ---------------------------------

                            closeDialog();

                        }
                    );


                    buttonArea.appendChild(
                        button
                    );

                }
            );


            area.appendChild(
                buttonArea
            );


            // ---------------------------------
            // 展開 / 折り畳み
            // ---------------------------------

            toggleButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();


                    buttonArea.hidden =
                        !buttonArea.hidden;


                    if (
                        buttonArea.hidden
                    ) {

                        toggleButton.textContent =
                            "プリセット ▼";

                    }
                    else {

                        toggleButton.textContent =
                            "プリセット ▲";

                    }

                }
            );


            dialog.appendChild(
                area
            );

        }


        // =====================================
        // ダイアログ生成
        // =====================================

        function openSubtitleFontDialog() {

            // ---------------------------------
            // 既に開いている場合
            // ---------------------------------

            if (activeDialog) {

                return;

            }


            // =================================
            // 編集用コピー
            //
            // 決定するまで正式設定を変更しない。
            // =================================

            const workingSettings =
                cloneSettings(
                    selectedSettings
                );


            let workingPreset =
                selectedPreset;


            // =================================
            // overlay
            // =================================

            const overlay =
                document.createElement(
                    "div"
                );


            overlay.className =
                "subtitle-font-dialog-overlay";


            // =================================
            // dialog
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
            // プリセット
            // =================================

            createPresetArea(

                dialog,

                workingSettings,

                function () {

                    closeDialog();

                }

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
                    "label"
                );


            fontLabel.className =
                "subtitle-font-dialog-row-label";


            fontLabel.textContent =
                "フォント";


            const fontSelect =
                createFontSelect(
                    workingSettings.font
                );


            fontRow.appendChild(
                fontLabel
            );


            fontRow.appendChild(
                fontSelect
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
                "subtitle-font-dialog-row subtitle-font-color-row";


            const textColorLabel =
                document.createElement(
                    "div"
                );


            textColorLabel.className =
                "subtitle-font-dialog-row-label";


            textColorLabel.textContent =
                "文字色";


            const textColorButtons =
                document.createElement(
                    "div"
                );


            textColorButtons.className =
                "subtitle-font-color-buttons";


            BASIC_COLORS.forEach(
                function (colorName) {

                    const button =
                        createColorButton(

                            colorName,

                            workingSettings.textColor,

                            function (color) {

                                workingSettings.textColor =
                                    color;


                                workingSettings.textColorHex =
                                    getColorHex(
                                        color
                                    );


                                updateColorSelection(
                                    textColorButtons,
                                    color
                                );


                                updatePreview();

                            }

                        );


                    textColorButtons.appendChild(
                        button
                    );

                }
            );


            textColorRow.appendChild(
                textColorLabel
            );


            textColorRow.appendChild(
                textColorButtons
            );


            dialog.appendChild(
                textColorRow
            );


            // =================================
            // 縁色
            // =================================

            const outlineColorRow =
                document.createElement(
                    "div"
                );


            outlineColorRow.className =
                "subtitle-font-dialog-row subtitle-font-color-row";


            const outlineColorLabel =
                document.createElement(
                    "div"
                );


            outlineColorLabel.className =
                "subtitle-font-dialog-row-label";


            outlineColorLabel.textContent =
                "縁取り色";


            const outlineColorButtons =
                document.createElement(
                    "div"
                );


            outlineColorButtons.className =
                "subtitle-font-color-buttons";


            BASIC_COLORS.forEach(
                function (colorName) {

                    const button =
                        createColorButton(

                            colorName,

                            workingSettings.outlineColor,

                            function (color) {

                                workingSettings.outlineColor =
                                    color;


                                workingSettings.outlineColorHex =
                                    getColorHex(
                                        color
                                    );


                                updateColorSelection(
                                    outlineColorButtons,
                                    color
                                );


                                updatePreview();

                            }

                        );


                    outlineColorButtons.appendChild(
                        button
                    );

                }
            );


            outlineColorRow.appendChild(
                outlineColorLabel
            );


            outlineColorRow.appendChild(
                outlineColorButtons
            );


            dialog.appendChild(
                outlineColorRow
            );


            // =================================
            // 縁取り太さ
            // =================================

            const outlineWidthRow =
                document.createElement(
                    "div"
                );


            outlineWidthRow.className =
                "subtitle-font-dialog-row";


            const outlineWidthLabel =
                document.createElement(
                    "label"
                );


            outlineWidthLabel.className =
                "subtitle-font-dialog-row-label";


            outlineWidthLabel.textContent =
                "縁取りの太さ";


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
                workingSettings.outlineWidth;


            outlineWidthInput.className =
                "subtitle-font-width-input";


            outlineWidthRow.appendChild(
                outlineWidthLabel
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
            // プレビュー更新
            // =================================

            function updatePreview() {

                createSettingsPreview(

                    preview,

                    workingSettings,

                    workingPreset

                );

            }


            // =================================
            // 色選択状態更新
            // =================================

            function updateColorSelection(
                container,
                selectedColor
            ) {

                const buttons =
                    container.querySelectorAll(
                        ".subtitle-font-color-button"
                    );


                buttons.forEach(
                    function (button) {

                        if (
                            button.dataset.color ===
                            selectedColor
                        ) {

                            button.classList.add(
                                "selected"
                            );

                        }
                        else {

                            button.classList.remove(
                                "selected"
                            );

                        }

                    }
                );

            }


            // =================================
            // フォント変更
            // =================================

            fontSelect.addEventListener(
                "change",
                function () {

                    workingSettings.font =
                        fontSelect.value;


                    // ---------------------------------
                    // 手動変更なので
                    // プリセット名はカスタム扱い。
                    // ---------------------------------

                    workingPreset =
                        "カスタム";


                    updatePreview();

                }
            );


            // =================================
            // 太さ変更
            // =================================

            outlineWidthInput.addEventListener(
                "input",
                function () {

                    workingSettings.outlineWidth =
                        normalizeOutlineWidth(
                            outlineWidthInput.value
                        );


                    workingPreset =
                        "カスタム";


                    updatePreview();

                }
            );


            // =================================
            // 初期プレビュー
            // =================================

            updatePreview();


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
            // overlayへ追加
            // =================================

            overlay.appendChild(
                dialog
            );


            document.body.appendChild(
                overlay
            );


            // =================================
            // activeDialog
            // =================================

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

                    // number / select の
                    // Enterによる誤決定を避ける。
                    if (
                        event.target ===
                        outlineWidthInput
                    ) {

                        return;

                    }

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


                    console.log(
                        "[SUBTITLE_FONT] dialog cancelled"
                    );


                    // ---------------------------------
                    // workingSettingsは破棄。
                    // selectedSettingsは変更しない。
                    // ---------------------------------

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


                    // ---------------------------------
                    // 太さを最終正規化
                    // ---------------------------------

                    workingSettings.outlineWidth =
                        normalizeOutlineWidth(
                            outlineWidthInput.value
                        );


                    // ---------------------------------
                    // 正式反映
                    // ---------------------------------

                    selectedSettings =
                        cloneSettings(
                            workingSettings
                        );


                    selectedPreset =
                        workingPreset;


                    // ---------------------------------
                    // メイン画面更新
                    // ---------------------------------

                    updateSubtitleFontLabel();


                    console.log(
                        "[SUBTITLE_FONT] settings confirmed:",
                        selectedPreset,
                        selectedSettings
                    );


                    closeDialog();

                }
            );


            // =================================
            // 背景クリック
            //
            // 背景だけクリックした場合は
            // キャンセル扱い。
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

                    fontSelect.focus();

                },
                0
            );

        }


        // =====================================
        // 字幕フォントボタン
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


                openSubtitleFontDialog();

            }
        );


        // =====================================
        // 外部公開
        // =====================================

        const fontObject = {

            __initialized:
                true,


            // ---------------------------------
            // 現在のプリセット
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
                            getColorHex(
                                selectedSettings.textColor
                            ),

                        outline_color:
                            selectedSettings.outlineColor,

                        outline_color_hex:
                            getColorHex(
                                selectedSettings.outlineColor
                            ),

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


                    updateSubtitleFontLabel();


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
                function () {

                    updateSubtitleFontLabel();

                },


            // ---------------------------------
            // ダイアログを開く
            //
            // 必要ならsubtitle.jsから
            // 呼び出せる。
            // ---------------------------------

            open:
                function () {

                    openSubtitleFontDialog();

                },


            // ---------------------------------
            // ダイアログが開いているか
            // ---------------------------------

            isOpen:
                function () {

                    return (
                        activeDialog !==
                        null
                    );

                }

        };


        window.subtitleFont =
            fontObject;


        // =====================================
        // 初期表示
        // =====================================

        updateSubtitleFontLabel();


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
