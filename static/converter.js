// =====================================
// YouTube Converter JavaScript
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    function(){

        const urlInput =
            document.getElementById(
                "youtube-url"
            );

        const checkButton =
            document.getElementById(
                "check-button"
            );

        const convertButton =
            document.getElementById(
                "convertBtn"
            );

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );

        let currentJobId = null;

        let convertSeconds = 0;

        let convertTimer = null;


        // ================================
        // YouTube確認
        // ================================

        if(checkButton){

            checkButton.addEventListener(
                "click",
                checkVideo
            );

        }


        // ================================
        // Enterキーで確認
        // ================================

        if(urlInput){

            urlInput.addEventListener(
                "keydown",
                function(event){

                    if(event.key === "Enter"){

                        event.preventDefault();

                        checkVideo();

                    }

                }
            );

        }


        // ================================
        // YouTube確認
        // ================================

        async function checkVideo(){

            const url =
                urlInput.value.trim();


            if(!url){

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }


            checkButton.disabled = true;

            checkButton.textContent =
                "確認中...";


            try{

                const response =
                    await fetch(
                        "/check",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                "application/json"
                            },

                            body:
                            JSON.stringify({
                                url: url
                            })
                        }
                    );


                // --------------------------------
                // HTTPエラー確認
                // --------------------------------

                if(!response.ok){

                    const text =
                        await response.text();

                    console.error(
                        "確認HTTPエラー:",
                        response.status,
                        text
                    );

                    throw new Error(
                        "HTTP "
                        + response.status
                        + " : "
                        + (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )
                    );

                }


                // --------------------------------
                // 空レスポンス確認
                // --------------------------------

                const text =
                    await response.text();


                if(!text){

                    throw new Error(
                        "サーバーから空のレスポンスが返されました"
                    );

                }


                // --------------------------------
                // JSON解析
                // --------------------------------

                let data;

                try{

                    data =
                        JSON.parse(text);

                }
                catch(jsonError){

                    console.error(
                        "確認JSON解析エラー:",
                        jsonError
                    );

                    console.error(
                        "サーバーレスポンス:",
                        text
                    );

                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }


                if(data.success){

                    const convertArea =
                        document.getElementById(
                            "convert-area"
                        );

                    if(convertArea){

                        convertArea.style.display =
                            "block";

                    }


                    const filename =
                        document.getElementById(
                            "filename"
                        );

                    if(filename){

                        filename.value =
                            data.filename || "";

                    }


                    const endTime =
                        document.getElementById(
                            "end-time"
                        );

                    if(endTime){

                        endTime.value =
                            data.duration || "";

                    }

                }
                else{

                    alert(
                        data.message ||
                        "動画情報を取得できませんでした"
                    );

                }

            }
            catch(error){

                console.error(
                    "確認エラー:",
                    error
                );

                alert(
                    "確認エラー: "
                    + error.message
                );

            }
            finally{

                checkButton.disabled =
                    false;

                checkButton.textContent =
                    "確認";

            }

        }


        // ================================
        // 変換開始
        // ================================

        if(convertButton){

            convertButton.addEventListener(
                "click",
                startConvert
            );

        }


        async function startConvert(){

            const url =
                urlInput.value.trim();


            if(!url){

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }


            const outputs = [];


            document
                .querySelectorAll(
                    "input[name='output']:checked"
                )
                .forEach(
                    function(item){

                        outputs.push(
                            item.value
                        );

                    }
                );


            if(outputs.length === 0){

                alert(
                    "作成ファイルを選択してください"
                );

                return;

            }


            convertButton.disabled =
                true;


            convertSeconds = 0;


            convertButton.textContent =
                "変換中 0秒";


            if(convertTimer){

                clearInterval(
                    convertTimer
                );

            }


            convertTimer =
                setInterval(
                    function(){

                        convertSeconds++;


                        convertButton.textContent =
                            "変換中 "
                            + convertSeconds
                            + "秒";

                    },
                    1000
                );


            try{

                const startTimeElement =
                    document.getElementById(
                        "start-time"
                    );

                const endTimeElement =
                    document.getElementById(
                        "end-time"
                    );


                const startTime =
                    startTimeElement
                    ? startTimeElement.value.trim()
                    : "";


                const endTime =
                    endTimeElement
                    ? endTimeElement.value.trim()
                    : "";


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
                            JSON.stringify({

                                url: url,

                                outputs: outputs,

                                start_time:
                                    startTime,

                                end_time:
                                    endTime

                            })
                        }
                    );


                // --------------------------------
                // HTTPエラー確認
                // --------------------------------

                if(!response.ok){

                    const text =
                        await response.text();

                    console.error(
                        "変換HTTPエラー:",
                        response.status,
                        text
                    );

                    throw new Error(
                        "HTTP "
                        + response.status
                        + " : "
                        + (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )
                    );

                }


                // --------------------------------
                // 空レスポンス確認
                // --------------------------------

                const text =
                    await response.text();


                if(!text){

                    throw new Error(
                        "サーバーから空のレスポンスが返されました"
                    );

                }


                // --------------------------------
                // JSON解析
                // --------------------------------

                let data;

                try{

                    data =
                        JSON.parse(text);

                }
                catch(jsonError){

                    console.error(
                        "変換JSON解析エラー:",
                        jsonError
                    );

                    console.error(
                        "サーバーレスポンス:",
                        text
                    );

                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }


                if(data.success){

                    currentJobId =
                        data.job_id;


                    console.log(
                        "変換JOB:",
                        currentJobId
                    );


                    checkStatus();

                }
                else{

                    throw new Error(
                        data.message ||
                        "変換開始に失敗しました"
                    );

                }

            }
            catch(error){

                if(convertTimer){

                    clearInterval(
                        convertTimer
                    );

                    convertTimer =
                        null;

                }


                convertButton.disabled =
                    false;


                convertButton.textContent =
                    "変換開始";


                console.error(
                    "変換開始エラー:",
                    error
                );


                alert(
                    error.message
                );

            }

        }


        // ================================
        // 状態確認
        // ================================

        async function checkStatus(){

            if(!currentJobId){

                console.error(
                    "JOB IDがありません"
                );

                return;

            }


            try{

                const response =
                    await fetch(
                        `/status/${encodeURIComponent(currentJobId)}`,
                        {
                            method: "GET",

                            cache: "no-store"
                        }
                    );


                // --------------------------------
                // HTTPエラー
                // --------------------------------

                if(!response.ok){

                    const text =
                        await response.text();


                    console.error(
                        "ステータスHTTPエラー:",
                        response.status,
                        text
                    );


                    // --------------------------------
                    // 502 / 503 / 504 は
                    // 一時的なRenderエラーの可能性が
                    // あるため、すぐ終了させない
                    // --------------------------------

                    if(
                        response.status === 502 ||
                        response.status === 503 ||
                        response.status === 504
                    ){

                        console.warn(
                            "一時的なサーバーエラー。"
                            + "3秒後に再試行します。"
                        );


                        setTimeout(
                            checkStatus,
                            3000
                        );


                        return;

                    }


                    throw new Error(
                        "HTTP "
                        + response.status
                        + " : "
                        + (
                            text ||
                            "サーバーから空のレスポンスが返されました"
                        )
                    );

                }


                // --------------------------------
                // レスポンス本文取得
                // --------------------------------

                const text =
                    await response.text();


                if(!text){

                    console.warn(
                        "STATUSレスポンスが空です。"
                        + "3秒後に再試行します。"
                    );


                    setTimeout(
                        checkStatus,
                        3000
                    );


                    return;

                }


                // --------------------------------
                // JSON解析
                // --------------------------------

                let data;

                try{

                    data =
                        JSON.parse(text);

                }
                catch(jsonError){

                    console.error(
                        "STATUS JSON解析エラー:",
                        jsonError
                    );

                    console.error(
                        "STATUSレスポンス:",
                        text
                    );


                    // JSONでないレスポンスの場合も
                    // すぐに変換失敗にはしない

                    setTimeout(
                        checkStatus,
                        3000
                    );


                    return;

                }


                console.log(
                    "STATUS:",
                    data
                );


                // --------------------------------
                // 完了
                // --------------------------------

                if(
                    data.status === "complete"
                ){

                    if(convertTimer){

                        clearInterval(
                            convertTimer
                        );

                        convertTimer =
                            null;

                    }


                    convertButton.style.display =
                        "none";


                    showFiles(
                        Array.isArray(data.files)
                            ? data.files
                            : []
                    );


                    return;

                }


                // --------------------------------
                // 変換エラー
                // --------------------------------

                if(
                    data.status === "error"
                ){

                    if(convertTimer){

                        clearInterval(
                            convertTimer
                        );

                        convertTimer =
                            null;

                    }


                    convertButton.disabled =
                        false;


                    convertButton.textContent =
                        "変換開始";


                    alert(
                        data.message ||
                        "変換中にエラーが発生しました"
                    );


                    return;

                }


                // --------------------------------
                // queued / running
                // --------------------------------

                setTimeout(
                    checkStatus,
                    3000
                );


            }
            catch(error){

                console.error(
                    "変換状態確認エラー:",
                    error
                );


                // ネットワークエラーなどの場合も
                // 変換処理そのものを止めず、
                // 再度STATUSを確認する

                setTimeout(
                    checkStatus,
                    3000
                );

            }

        }


        // ================================
        // ダウンロード表示
        // ================================

        function showFiles(files){

            console.log(
                "完成ファイル:",
                files
            );


            let html = `

                <div class="download-buttons">

            `;


            let mp3File = "";


            files.forEach(
                function(file){

                    if(
                        file.endsWith(".mp3")
                    ){

                        mp3File = file;

                    }

                }
            );


            // --------------------------------
            // Gemini用mp3ファイル名セット
            // --------------------------------

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );


            if(
                geminiFile &&
                mp3File
            ){

                geminiFile.value =
                    mp3File;

            }


            // --------------------------------
            // ファイルボタン
            // --------------------------------

            files.forEach(
                function(file){

                    if(
                        file.endsWith(".mp3")
                    ){

                        html += `

                            <a
                                href="/download/${encodeURIComponent(file)}"
                                download
                            >

                                <button
                                    class="download-button"
                                >
                                    mp3
                                </button>

                            </a>

                            <button
                                type="button"
                                id="srt-toggle-button"
                                class="srt-toggle-button"
                            >
                                ▲
                            </button>

                        `;

                    }


                    else if(
                        file.endsWith(".mp4")
                    ){

                        html += `

                            <a
                                href="/download/${encodeURIComponent(file)}"
                                download
                            >

                                <button
                                    class="download-button"
                                >
                                    mp4
                                </button>

                            </a>

                        `;

                    }

                }
            );


            html += `

                </div>

            `;


            if(downloadArea){

                downloadArea.innerHTML =
                    html;

            }


            // ================================
            // SRT表示
            // ================================

            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if(
                srtArea &&
                mp3File
            ){

                srtArea.style.display =
                    "block";

            }
            else if(srtArea){

                srtArea.style.display =
                    "none";

            }


            // ================================
            // 展開ボタン
            // ================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );


            const srtContent =
                document.getElementById(
                    "srt-content"
                );


            if(
                toggle &&
                srtContent
            ){

                toggle.addEventListener(
                    "click",
                    function(){

                        if(
                            srtContent.style.display ===
                            "none"
                        ){

                            srtContent.style.display =
                                "block";

                            toggle.textContent =
                                "▲";

                        }
                        else{

                            srtContent.style.display =
                                "none";

                            toggle.textContent =
                                "▼";

                        }

                    }
                );

            }

        }


        // ================================
        // Gemini文字起こし
        // ================================

        const geminiButton =
            document.getElementById(
                "gemini-button"
            );


        if(geminiButton){

            geminiButton.addEventListener(
                "click",
                async function(){

                    const file =
                        document.getElementById(
                            "gemini-file"
                        )
                        .value
                        .trim();


                    if(!file){

                        alert(
                            "mp3ファイル名がありません"
                        );

                        return;

                    }


                    const result =
                        document.getElementById(
                            "gemini-result"
                        );


                    let seconds = 0;


                    result.textContent =
                        "文字起こし中... 0秒";


                    const timer =
                        setInterval(
                            function(){

                                seconds++;


                                result.textContent =
                                    "文字起こし中... "
                                    + seconds
                                    + "秒";

                            },
                            1000
                        );


                    try{

                        const response =
                            await fetch(
                                "/gemini-transcribe",
                                {

                                    method:
                                        "POST",

                                    headers:{
                                        "Content-Type":
                                        "application/json"
                                    },

                                    body:
                                    JSON.stringify({
                                        file:file
                                    })

                                }
                            );


                        if(!response.ok){

                            const text =
                                await response.text();


                            throw new Error(
                                "HTTP "
                                + response.status
                                + " : "
                                + (
                                    text ||
                                    "サーバーから空のレスポンスが返されました"
                                )
                            );

                        }


                        const text =
                            await response.text();


                        if(!text){

                            throw new Error(
                                "サーバーから空のレスポンスが返されました"
                            );

                        }


                        let data;


                        try{

                            data =
                                JSON.parse(text);

                        }
                        catch(jsonError){

                            console.error(
                                "Gemini JSON解析エラー:",
                                jsonError
                            );

                            console.error(
                                "Geminiレスポンス:",
                                text
                            );

                            throw new Error(
                                "サーバーから正しいJSONが返されませんでした"
                            );

                        }


                        clearInterval(
                            timer
                        );


                        if(data.success){

                            result.style.display =
                                "none";


                            const srtButton =
                                document.createElement(
                                    "a"
                                );


                            srtButton.href =
                                "/download/"
                                +
                                encodeURIComponent(
                                    data.srt_file
                                );


                            srtButton.download =
                                data.srt_file;


                            srtButton.innerHTML =
                                `
                                <button class="download-button">
                                    srt
                                </button>
                                `;


                            result.parentNode.appendChild(
                                srtButton
                            );

                        }
                        else{

                            result.textContent =
                                data.message ||
                                "文字起こしに失敗しました";

                        }


                    }
                    catch(error){

                        clearInterval(
                            timer
                        );


                        console.error(
                            "Geminiエラー:",
                            error
                        );


                        result.textContent =
                            "エラー: "
                            + error.message;

                    }

                }
            );

        }

    }
);

