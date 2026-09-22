/*
 * ytdown.js
 *
 * YouTube動画の時間指定ダウンロード専用
 *
 * 対応：
 * - YouTube URL
 * - 開始時間
 * - 終了時間
 * - MP3 / MP4
 *
 * 使用するHTML要素：
 *
 * #youtube-url
 *
 * #start-hour
 * #start-minute
 * #start-second
 *
 * #end-hour
 * #end-minute
 * #end-second
 *
 * #convertBtn
 *
 * #conversion-status-area
 * #downloadArea
 *
 */


document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "[YTDOWN] initialization start"
        );


        // =====================================
        // DOM
        // =====================================

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


        const convertButton =
            document.getElementById(
                "convertBtn"
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
            "[YTDOWN] youtubeUrl:",
            youtubeUrl
        );

        console.log(
            "[YTDOWN] convertButton:",
            convertButton
        );


        // =====================================
        // 時間を秒へ変換
        // =====================================

        function getTime(
            hour,
            minute,
            second
        ) {

            const h =
                parseInt(
                    hour.value || "0",
                    10
                );


            const m =
                parseInt(
                    minute.value || "0",
                    10
                );


            const s =
                parseInt(
                    second.value || "0",
                    10
                );


            if (
                isNaN(h) ||
                isNaN(m) ||
                isNaN(s)
            ) {

                return null;

            }


            if (
                h < 0 ||
                m < 0 ||
                m > 59 ||
                s < 0 ||
                s > 59
            ) {

                return null;

            }


            return (
                h * 3600 +
                m * 60 +
                s
            );

        }


        // =====================================
        // 時間入力を数字だけにする
        // =====================================

        function setupTimeInput(
            input
        ) {

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


        setupTimeInput(startHour);
        setupTimeInput(startMinute);
        setupTimeInput(startSecond);

        setupTimeInput(endHour);
        setupTimeInput(endMinute);
        setupTimeInput(endSecond);


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
        // ダウンロード処理
        // =====================================

        async function downloadVideo() {

            console.log(
                "[YTDOWN] download start"
            );


            // ---------------------------------
            // URL
            // ---------------------------------

            const url =
                youtubeUrl
                    ? youtubeUrl.value.trim()
                    : "";


            if (!url) {

                setStatus(
                    "YouTube URLを入力してください。"
                );

                return;

            }


            // ---------------------------------
            // 時間
            // ---------------------------------

            const startTime =
                getTime(
                    startHour,
                    startMinute,
                    startSecond
                );


            const endTime =
                getTime(
                    endHour,
                    endMinute,
                    endSecond
                );


            if (
                startTime === null ||
                endTime === null
            ) {

                setStatus(
                    "時間を正しく入力してください。"
                );

                return;

            }


            if (
                endTime <= startTime
            ) {

                setStatus(
                    "終了時間は開始時間より後にしてください。"
                );

                return;

            }


            // ---------------------------------
            // 出力形式
            // ---------------------------------

            const format =
                getOutputFormat();


            console.log(
                "[YTDOWN] URL:",
                url
            );


            console.log(
                "[YTDOWN] start:",
                startTime
            );


            console.log(
                "[YTDOWN] end:",
                endTime
            );


            console.log(
                "[YTDOWN] format:",
                format
            );


            // ---------------------------------
            // UI
            // ---------------------------------

            clearDownloadArea();

            setStatus(
                "ダウンロード処理を開始しています..."
            );


            if (convertButton) {

                convertButton.disabled =
                    true;

            }


            try {

                // =================================
                // APIへ送信
                // =================================

                const response =
                    await fetch(
                        "/convert",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    {
                                        url: url,

                                        start:
                                            startTime,

                                        end:
                                            endTime,

                                        format:
                                            format
                                    }
                                )
                        }
                    );


                console.log(
                    "[YTDOWN] response:",
                    response.status
                );


                // =================================
                // エラー
                // =================================

                if (!response.ok) {

                    let errorMessage =
                        "ダウンロードに失敗しました。";


                    try {

                        const errorData =
                            await response.json();


                        if (
                            errorData &&
                            errorData.error
                        ) {

                            errorMessage =
                                errorData.error;

                        }

                    }
                    catch (error) {

                        console.log(
                            "[YTDOWN] error response is not JSON"
                        );

                    }


                    throw new Error(
                        errorMessage
                    );

                }


                // =================================
                // レスポンス
                // =================================

                const data =
                    await response.json();


                console.log(
                    "[YTDOWN] response data:",
                    data
                );


                // =================================
                // ダウンロードURL
                // =================================

                if (
                    data.download_url
                ) {

                    const link =
                        document.createElement(
                            "a"
                        );


                    link.href =
                        data.download_url;


                    link.textContent =
                        "ダウンロード";


                    link.className =
                        "download-link";


                    link.download = "";


                    if (downloadArea) {

                        downloadArea.appendChild(
                            link
                        );

                    }


                    setStatus(
                        "変換が完了しました。"
                    );


                }
                else if (
                    data.filename
                ) {

                    const link =
                        document.createElement(
                            "a"
                        );


                    link.href =
                        "/download/" +
                        encodeURIComponent(
                            data.filename
                        );


                    link.textContent =
                        "ダウンロード";


                    link.className =
                        "download-link";


                    link.download =
                        data.filename;


                    if (downloadArea) {

                        downloadArea.appendChild(
                            link
                        );

                    }


                    setStatus(
                        "変換が完了しました。"
                    );

                }
                else {

                    setStatus(
                        "変換は完了しましたが、ダウンロード先が見つかりません。"
                    );

                }

            }
            catch (error) {

                console.error(
                    "[YTDOWN] error:",
                    error
                );


                setStatus(
                    error.message ||
                    "ダウンロード中にエラーが発生しました。"
                );

            }
            finally {

                if (convertButton) {

                    convertButton.disabled =
                        false;

                }


                console.log(
                    "[YTDOWN] download finished"
                );

            }

        }


        // =====================================
        // 実行ボタン
        // =====================================

        if (convertButton) {

            convertButton.addEventListener(
                "click",
                downloadVideo
            );

        }


        // =====================================
        // Enterキー
        // URL入力欄でEnter
        // =====================================

        if (youtubeUrl) {

            youtubeUrl.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key ===
                        "Enter"
                    ) {

                        event.preventDefault();

                        downloadVideo();

                    }

                }
            );

        }


        console.log(
            "[YTDOWN] initialization complete"
        );

    }
);
