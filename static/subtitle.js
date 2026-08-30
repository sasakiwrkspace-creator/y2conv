// =====================================
// YouTube Converter - Subtitle
// subtitle.js
//
// タブ2：ファイル変換
//
// 役割:
// ・MP3ファイル選択
// ・MP3アップロード
// ・GeminiへMP3送信
// ・SRT取得
// ・MP4ファイル選択
// ・SRTファイル選択
// ・MP4 / SRTアップロード
// ・字幕付きMP4作成
// ・共通ダウンロードエリアへの結果表示
//
// 重要:
// ・タブ1のconverter.jsには触れない
// ・#convertBtnには触れない
// ・タブ1のイベントを登録しない
// ・将来タブ1から関数として呼び出せる構成
// =====================================

(function () {

    "use strict";


    // =====================================
    // 初期化
    // =====================================

    function initializeSubtitle() {

        console.log(
            "[SUBTITLE] initializeSubtitle() start"
        );


        // =================================
        // 二重初期化防止
        // =================================

        if (
            window.subtitleMain &&
            window.subtitleMain.__initialized
        ) {

            console.log(
                "[SUBTITLE] already initialized"
            );

            return;

        }


        // =====================================
        // DOM
        // =====================================

        const mp3FileInput =
            document.getElementById(
                "subtitle-mp3-file"
            );


        const mp3SelectButton =
            document.getElementById(
                "subtitle-mp3-select-button"
            );


        const geminiButton =
            document.getElementById(
                "subtitle-gemini-button"
            );


        const mp4FileInput =
            document.getElementById(
                "subtitle-mp4-file"
            );


        const mp4SelectButton =
            document.getElementById(
                "subtitle-mp4-select-button"
            );


        const srtFileInput =
            document.getElementById(
                "subtitle-srt-file"
            );


        const srtSelectButton =
            document.getElementById(
                "subtitle-srt-select-button"
            );


        const subtitleMp4Button =
            document.getElementById(
                "subtitle-mp4-create-button"
            );


        const mp3FileName =
            document.getElementById(
                "subtitle-mp3-file-name"
            );


        const mp4FileName =
            document.getElementById(
                "subtitle-mp4-file-name"
            );


        const srtFileName =
            document.getElementById(
                "subtitle-srt-file-name"
            );


        // =====================================
        // 共通ステータス
        // =====================================

        const statusElement =
            document.getElementById(
                "status"
            );


        const conversionStatusArea =
            document.getElementById(
                "conversion-status-area"
            );


        // =====================================
        // 共通ダウンロードエリア
        // =====================================

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );


        console.log(
            "[SUBTITLE] mp3FileInput:",
            mp3FileInput
        );


        console.log(
            "[SUBTITLE] geminiButton:",
            geminiButton
        );


        console.log(
            "[SUBTITLE] mp4FileInput:",
            mp4FileInput
        );


        console.log(
            "[SUBTITLE] srtFileInput:",
            srtFileInput
        );


        console.log(
            "[SUBTITLE] subtitleMp4Button:",
            subtitleMp4Button
        );


        console.log(
            "[SUBTITLE] downloadArea:",
            downloadArea
        );


        // =====================================
        // State
        // =====================================

        const subtitleState = {

            mp3File:
                null,

            mp3Filename:
                "",

            mp4File:
                null,

            mp4Filename:
                "",

            srtFile:
                null,

            srtFilename:
                "",

            generatedSrtFilename:
                "",

            generatedSubtitleMp4Filename:
                "",

            isUploadingMp3:
                false,

            isGeminiProcessing:
                false,

            isUploadingMp4:
                false,

            isUploadingSrt:
                false,

            isSubtitleMp4Processing:
                false

        };


        window.subtitleState =
            subtitleState;


        // =====================================
        // ステータス表示
        // =====================================

        function setStatus(
