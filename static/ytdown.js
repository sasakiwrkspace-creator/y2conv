// =====================================
// YouTube時間指定ダウンロード
// ytdown.js
//
// 役割:
//   タブ1のYouTube変換専用
//
// 処理:
//
//   YouTube URL
//       ↓
//   開始時間
//       ↓
//   終了時間
//       ↓
//   mp3 / mp4
//       ↓
//   POST /ytdown
//       ↓
//   ytdown.py
//       ↓
//   yt-dlp
//       ↓
//   FFmpeg
//
// 対応:
//   mp3
//   mp4
//
// 時間:
//   HH:MM:SS
//
// 終了時間:
//   00:00:00 = 最後まで
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
            "[YTDOWN] start:",
            startHour,
            startMinute,
            startSecond
        );

        console.log(
            "[YTDOWN] end:",
            endHour,
            endMinute,
            endSecond
        );

        console.log(
            "[YTDOWN] statusArea:",
            statusArea
        );

        console.log(
            "[YTDOWN] downloadArea:",
            downloadArea
        );


        // =====================================
        // 必須DOM確認
        // =====================================

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
        // ダウンロードエリア削除
        // =====================================

        function clearDownloadArea() {

            if (!downloadArea) {

                return;

            }


            downloadArea.innerHTML = "";

        }


        // =====================================
        // 入力値取得
        // =====================================

        function getInputValue(
            element
        ) {

            if (!element) {

                return "00";

            }


            const value =
                element.value.trim();


            if (!value) {

                return "00";

            }


            return value;

        }


        // =====================================
        // 数値取得
        // =====================================

        function getNumber(
            element
        ) {

            const value =
                getInputValue(
                    element
                );


            const number =
                Number(
                    value
                );


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


            // ---------------------------------
            // 時
            // ---------------------------------

            if (
                hour < 0
            ) {

                alert(
                    label
                    +
                    "の時間が正しくありません。"
                );

                return false;

            }


            // ---------------------------------
            // 分
            // ---------------------------------

            if (
                minute < 0
                ||
                minute > 59
            ) {

                alert(
                    label
                    +
                    "の「分」は00～59で入力してください。"
                );

                return false;

            }


            // ---------------------------------
            // 秒
            // ---------------------------------

            if (
                second < 0
                ||
                second > 59
            ) {

                alert(
                    label
                    +
                    "の「秒」は00～59で入力してください。"
                );

                return false;

            }


            return true;

        }


        // =====================================
        // 時間を秒へ変換
        // =====================================

        function timeToSeconds(
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
        // 時間をHH:MM:SSへ変換
        // =====================================

        function timeToString(
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
                String(hour).padStart(
                    2,
                    "0"
                )
                +
                ":"
                +
                String(minute).padStart(
                    2,
                    "0"
                )
                +
                ":"
                +
                String(second).padStart(
                    2,
                    "0"
                )
            );

        }


        // =====================================
        // 出力形式取得
        // =====================================

        function getOutputFormat() {

            const selected =
                document.querySelector(
                    "input[name='output-format']:checked"
                );


            if (!selected) {

                return "mp3";

            }


            return selected.value;

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
            // ファイル名
            // =================================

            const filename =
                data.filename
                ||
                data.file
                ||
                "download";


            // =================================
            // ダウンロードURL
            // =================================
            //
            // ytdown.pyが返す
            // filenameだけではブラウザから
            // ダウンロードできない。
            //
            // そのため /files/... を使用する。
            //
            // ただしサーバー側で
            // download_url / urlを返した場合は
            // それを優先する。
            // =================================

            let downloadUrl =
                data.download_url
                ||
                data.url;


            if (!downloadUrl) {

                downloadUrl =
                    "/files/"
                    +
                    encodeURIComponent(
                        filename
                    );

            }


            console.log(
                "[YTDOWN] download URL:",
                downloadUrl
            );


            // =================================
            // リンク作成
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


            downloadArea.appendChild(
                link
            );

        }


        // =====================================
        // YouTubeダウンロード
        // =====================================

        async function downloadYoutube() {

            console.log(
                "=========================================="
            );

            console.log(
                "[YTDOWN] download start"
            );

            console.log(
                "=========================================="
            );


            // =================================
            // URL取得
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
            // URL簡易確認
            // =================================

            if (
                !url.includes(
                    "youtube.com"
                )
                &&
                !url.includes(
                    "youtu.be"
                )
            ) {

                alert(
                    "YouTubeのURLを入力してください。"
                );

                youtubeUrl.focus();

                return;

            }


            // =================================
            // 開始時間チェック
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


            // =================================
            // 終了時間チェック
            // =================================

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
            // 時間を秒へ変換
            // =================================

            const startSeconds =
                timeToSeconds(
                    startHour,
                    startMinute,
                    startSecond
                );


            const endSeconds =
                timeToSeconds(
                    endHour,
                    endMinute,
                    endSecond
                );


            // =================================
            // 時間文字列
            // =================================

            const startTime =
                timeToString(
                    startHour,
                    startMinute,
                    startSecond
                );


            const endTime =
                timeToString(
                    endHour,
                    endMinute,
                    endSecond
                );


            console.log(
                "[YTDOWN] startTime:",
                startTime
            );

            console.log(
                "[YTDOWN] endTime:",
                endTime
            );

            console.log(
                "[YTDOWN] startSeconds:",
                startSeconds
            );

            console.log(
                "[YTDOWN] endSeconds:",
                endSeconds
            );


            // =================================
            // 終了時間チェック
            //
            // 00:00:00の場合:
            //   最後まで
            //
            // それ以外:
            //   開始より後である必要がある。
            // =================================

            if (
                endSeconds > 0
                &&
                endSeconds <= startSeconds
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


            console.log(
                "[YTDOWN] format:",
                format
            );


            // =================================
            // 画面初期化
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


            const originalButtonText =
                convertButton.textContent;


            convertButton.textContent =
                "処理中...";


            try {

                // =================================
                // ytdown.pyへ送信
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
                    "[YTDOWN] request data:",
                    requestData
                );


                // =================================
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


                console.log(
                    "[YTDOWN] HTTP status:",
                    response.status
                );


                // =================================
                // レスポンス形式確認
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
                        "YouTubeダウンロードに失敗しました。"
                    );

                }


                // =================================
                // Python側エラー
                // =================================

                if (
                    data.success === false
                ) {

                    throw new Error(
                        data.message
                        ||
                        data.error
                        ||
                        "YouTubeダウンロードに失敗しました。"
                    );

                }


                // =================================
                // 成功
                // =================================

                setStatus(
                    "ダウンロードの準備ができました。"
                );


                // =================================
                // ダウンロードリンク
                // =================================

                createDownloadLink(
                    data
                );


                console.log(
                    "=========================================="
                );

                console.log(
                    "[YTDOWN] download completed"
                );

                console.log(
                    "=========================================="
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
                    "YouTubeダウンロードに失敗しました。"
                );

            }
            finally {

                // =================================
                // ボタン復帰
                // =================================

                convertButton.disabled =
                    false;


                convertButton.textContent =
                    originalButtonText;

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
        // URL欄 Enter
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
        // 時間入力
        //
        // 数字以外を削除
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


                // ---------------------------------
                // Enterで実行
                // ---------------------------------

                input.addEventListener(
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

            }
        );


        // =====================================
        // 初期状態
        // =====================================

        setStatus(
            ""
        );


        clearDownloadArea();


        console.log(
            "[YTDOWN] initialization complete"
        );

    }
);
