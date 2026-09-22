// =====================================
// YouTube時間指定ダウンロード
// ytdown.js
//
// 役割:
//   タブ1のYouTube変換専用
//
// 処理:
//   YouTube URL
//       ↓
//   開始時間
//       ↓
//   終了時間
//       ↓
//   mp3 / mp4
//       ↓
//   /ytdown
//
// convert.jsは使用しない。
// =====================================


document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "[YTDOWN] initialization start"
        );


        // =====================================
        // DOM
        // =====================================

        const convertButton =
            document.getElementById(
                "convertBtn"
            );


        const youtubeUrl =
            document.getElementById(
                "youtube-url"
            );


        const startHour =
            document.getElementById(
                "start-hour"
            );


        const startMinute =
            document.getElementById(
                "start-minute"
            );


        const startSecond =
            document.getElementById(
                "start-second"
            );


        const endHour =
            document.getElementById(
                "end-hour"
            );


        const endMinute =
            document.getElementById(
                "end-minute"
            );


        const endSecond =
            document.getElementById(
                "end-second"
            );


        const statusArea =
            document.getElementById(
                "conversion-status-area"
            );


        const downloadArea =
            document.getElementById(
                "downloadArea"
            );


        // =====================================
        // DOM確認
        // =====================================

        console.log(
            "[YTDOWN] convertButton:",
            convertButton
        );

        console.log(
            "[YTDOWN] youtubeUrl:",
            youtubeUrl
        );

        console.log(
            "[YTDOWN] statusArea:",
            statusArea
        );

        console.log(
            "[YTDOWN] downloadArea:",
            downloadArea
        );


        if (!convertButton) {

            console.error(
                "[YTDOWN] #convertBtn がありません"
            );

            return;

        }


        if (!youtubeUrl) {

            console.error(
                "[YTDOWN] #youtube-url がありません"
            );

            return;

        }


        // =====================================
        // ステータス表示
        // =====================================

        function setStatus(
            message
        ) {

            if (!statusArea) {

                return;

            }


            statusArea.textContent =
                message;

        }


        // =====================================
        // ダウンロードエリアをクリア
        // =====================================

        function clearDownloadArea() {

            if (!downloadArea) {

                return;

            }


            downloadArea.innerHTML = "";

        }


        // =====================================
        // 数値化
        // =====================================

        function getNumber(
            element
        ) {

            if (!element) {

                return 0;

            }


            const value =
                element.value.trim();


            if (!value) {

                return 0;

            }


            const number =
                Number(value);


            if (
                !Number.isFinite(
                    number
                )
            ) {

                return 0;

            }


            return number;

        }


        // =====================================
        // 時間を秒へ変換
        // =====================================

        function getTimeInSeconds(
            hourElement,
            minuteElement,
            secondElement
        ) {

            const hour =
                getNumber(
                    hourElement
                );


            const minute =
                getNumber(
                    minuteElement
                );


            const second =
                getNumber(
                    secondElement
                );


            return (
                hour * 3600
                +
                minute * 60
                +
                second
            );

        }


        // =====================================
        // 時間入力チェック
        // =====================================

        function validateTime(
            hourElement,
            minuteElement,
            secondElement,
            label
        ) {

            const hour =
                getNumber(
                    hourElement
                );


            const minute =
                getNumber(
                    minuteElement
                );


            const second =
                getNumber(
                    secondElement
                );


            if (
                hour < 0
                ||
                minute < 0
                ||
                minute > 59
                ||
                second < 0
                ||
                second > 59
            ) {

                alert(
                    label
                    +
                    "の時間指定が正しくありません。"
                );

                return false;

            }


            return true;

        }


        // =====================================
        // 出力形式取得
        // =====================================

        function getOutputFormat() {

            const radio =
                document.querySelector(
                    "input[name='output-format']:checked"
                );


            if (!radio) {

                return "mp3";

            }


            return radio.value;

        }


        // =====================================
        // ダウンロードリンク作成
        // =====================================

        function createDownloadLink(
            data
        ) {

            if (!downloadArea) {

                return;

            }


            downloadArea.innerHTML = "";


            // =================================
            // filename
            // =================================

            const filename =
                data.filename
                ||
                "download";


            // =================================
            // URL
            // =================================

            let downloadUrl =
                data.download_url
                ||
                data.url;


            if (!downloadUrl) {

                console.warn(
                    "[YTDOWN] download URLがありません:",
                    data
                );

                return;

            }


            // =================================
            // リンク
            // =================================

            const link =
                document.createElement(
                    "a"
                );


            link.href =
                downloadUrl;


            link.download =
                filename;


            link.textContent =
                "ダウンロード";


            link.className =
                "download-button";


            link.target =
                "_blank";


            link.rel =
                "noopener";


            downloadArea.appendChild(
                link
            );

        }


        // =====================================
        // メイン処理
        // =====================================

        async function downloadYoutube() {

            console.log(
                "[YTDOWN] download start"
            );


            // =================================
            // 入力取得
            // =================================

            const url =
                youtubeUrl.value.trim();


            if (!url) {

                alert(
                    "YouTube URLを入力してください。"
                );

                youtubeUrl.focus();

                return;

            }


            // =================================
            // 時間チェック
            // =================================

            if (
                !validateTime(
                    startHour,
                    startMinute,
                    startSecond,
                    "開始時間"
                )
            ) {

                return;

            }


            if (
                !validateTime(
                    endHour,
                    endMinute,
                    endSecond,
                    "終了時間"
                )
            ) {

                return;

            }


            // =================================
            // 秒へ変換
            // =================================

            const startTime =
                getTimeInSeconds(
                    startHour,
                    startMinute,
                    startSecond
                );


            const endTime =
                getTimeInSeconds(
                    endHour,
                    endMinute,
                    endSecond
                );


            // =================================
            // 終了時間チェック
            //
            // 00:00:00の場合は
            // 終了時間未指定として扱う。
            // =================================

            if (
                endTime > 0
                &&
                endTime <= startTime
            ) {

                alert(
                    "終了時間は開始時間より後にしてください。"
                );

                return;

            }


            // =================================
            // 出力形式
            // =================================

            const format =
                getOutputFormat();


            if (
                format !== "mp3"
                &&
                format !== "mp4"
            ) {

                alert(
                    "出力形式が正しくありません。"
                );

                return;

            }


            // =================================
            // 表示
            // =================================

            clearDownloadArea();


            setStatus(
                "YouTube動画を処理しています..."
            );


            // =================================
            // ボタン無効化
            // =================================

            convertButton.disabled =
                true;


            const originalText =
                convertButton.textContent;


            convertButton.textContent =
                "処理中...";


            try {

                // =================================
                // リクエストデータ
                // =================================

                const requestData = {

                    url:
                        url,

                    start_time:
                        startTime,

                    end_time:
                        endTime,

                    format:
                        format

                };


                console.log(
                    "[YTDOWN] request:",
                    requestData
                );


                // =================================
                // ytdown.py
                //
                // Flask:
                //
                // POST /ytdown
                // =================================

                const response =
                    await fetch(
                        "/ytdown",
                        {

                            method:
                                "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify(
                                    requestData
                                )

                        }
                    );


                // =================================
                // レスポンス取得
                // =================================

                const contentType =
                    response.headers.get(
                        "content-type"
                    )
                    ||
                    "";


                let data;


                if (
                    contentType.includes(
                        "application/json"
                    )
                ) {

                    data =
                        await response.json();

                } else {

                    const text =
                        await response.text();


                    data = {

                        success:
                            response.ok,

                        message:
                            text

                    };

                }


                console.log(
                    "[YTDOWN] response:",
                    data
                );


                // =================================
                // HTTPエラー
                // =================================

                if (
                    !response.ok
                ) {

                    throw new Error(
                        data.message
                        ||
                        data.error
                        ||
                        "YouTube変換に失敗しました。"
                    );

                }


                // =================================
                // Python側success確認
                // =================================

                if (
                    data.success === false
                ) {

                    throw new Error(
                        data.message
                        ||
                        data.error
                        ||
                        "YouTube変換に失敗しました。"
                    );

                }


                // =================================
                // 成功
                // =================================

                setStatus(
                    data.message
                    ||
                    "ダウンロードの準備ができました。"
                );


                // =================================
                // ダウンロードリンク
                // =================================

                createDownloadLink(
                    data
                );


                console.log(
                    "[YTDOWN] download completed"
                );

            }
            catch (error) {

                console.error(
                    "[YTDOWN] ERROR:",
                    error
                );


                setStatus(
                    "処理に失敗しました。"
                );


                alert(
                    error.message
                    ||
                    "YouTube変換に失敗しました。"
                );

            }
            finally {

                // =================================
                // ボタン復帰
                // =================================

                convertButton.disabled =
                    false;


                convertButton.textContent =
                    originalText;


            }

        }


        // =====================================
        // 実行ボタン
        // =====================================

        convertButton.addEventListener(
            "click",
            function () {

                downloadYoutube();

            }
        );


        // =====================================
        // Enterキー
        //
        // URL入力欄でEnterを押した場合も
        // ダウンロードを実行する。
        // =====================================

        youtubeUrl.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key ===
                    "Enter"
                ) {

                    event.preventDefault();

                    downloadYoutube();

                }

            }
        );


        // =====================================
        // 数字以外を除去
        //
        // 時間入力を簡単にする。
        // =====================================

        const timeInputs = [

            startHour,
            startMinute,
            startSecond,
            endHour,
            endMinute,
            endSecond

        ];


        timeInputs.forEach(
            function (input) {

                if (!input) {

                    return;

                }


                input.addEventListener(
                    "input",
                    function () {

                        this.value =
                            this.value.replace(
                                /[^0-9]/g,
                                ""
                            );

                    }
                );

            }
        );


        // =====================================
        // 初期状態
        // =====================================

        console.log(
            "[YTDOWN] initialization complete"
        );

    }
);
