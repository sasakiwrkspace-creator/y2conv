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


        // =====================================
        // 共通：安全にJSONを取得
        // =====================================

        async function fetchJson(
            url,
            options = {}
        ){

            const response =
                await fetch(
                    url,
                    options
                );


            // ---------------------------------
            // HTTPエラー
            // ---------------------------------

            if(!response.ok){

                const text =
                    await response.text();

                throw new Error(
                    "HTTP "
                    + response.status
                    + " "
                    + response.statusText
                    + (
                        text
                        ? " : " + text.substring(0, 500)
                        : ""
                    )
                );

            }


            // ---------------------------------
            // レスポンス本文取得
            // ---------------------------------

            const text =
                await response.text();


            // ---------------------------------
            // 空レスポンス
            // ---------------------------------

            if(!text || !text.trim()){

                throw new Error(
                    "サーバーから空のレスポンスが返されました"
                );

            }


            // ---------------------------------
            // JSON解析
            // ---------------------------------

            try{

                return JSON.parse(
                    text
                );

            }
            catch(error){

                console.error(
                    "JSON解析失敗:",
                    error
                );

                console.error(
                    "URL:",
                    url
                );

                console.error(
                    "HTTP:",
                    response.status
                );

                console.error(
                    "Response:",
                    text
                );

                throw new Error(
                    "サーバーから正しいJSONが返されませんでした"
                );

            }

        }


        // =====================================
        // YouTube確認
        // =====================================


        if(checkButton){

            checkButton.addEventListener(
                "click",
                checkVideo
            );

        }


        // -------------------------------------
        // Enterキーで確認
        // -------------------------------------

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


        // =====================================
        // YouTube情報確認
        // =====================================

        async function checkVideo(){

            const url =
                urlInput.value.trim();


            if(!url){

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }


            checkButton.disabled =
                true;


            checkButton.textContent =
                "確認中...";


            try{

                const data =
                    await fetchJson(
                        "/check",
                        {

                            method:
                                "POST",

                            headers:{
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({
                                    url:url
                                })

                        }
                    );


                console.log(
                    "/check response:",
                    data
                );


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
                        "YouTube情報の取得に失敗しました"
                    );

                }

            }
            catch(error){

                console.error(
                    "checkVideo error:",
                    error
                );


                alert(
                    "確認エラー:\n"
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


        // =====================================
        // 変換開始ボタン
        // =====================================


        if(convertButton){

            convertButton.addEventListener(
                "click",
                startConvert
            );

        }


        // =====================================
        // 変換開始
        // =====================================

        async function startConvert(){

            const url =
                urlInput.value.trim();


            if(!url){

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }


            const outputs =
                [];


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


            // ---------------------------------
            // 既存タイマー停止
            // ---------------------------------

            if(convertTimer){

                clearInterval(
                    convertTimer
                );

                convertTimer =
                    null;

            }


            // ---------------------------------
            // ボタン状態
            // ---------------------------------

            convertButton.disabled =
                true;


            convertSeconds =
                0;


            convertButton.textContent =
                "変換中 0秒";


            // ---------------------------------
            // 経過時間
            // ---------------------------------

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


                console.log(
                    "変換開始:",
                    {
                        url:url,
                        outputs:outputs,
                        start_time:startTime,
                        end_time:endTime
                    }
                );


                const data =
                    await fetchJson(
                        "/convert",
                        {

                            method:
                                "POST",

                            headers:{
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    url:url,

                                    outputs:
                                        outputs,

                                    start_time:
                                        startTime,

                                    end_time:
                                        endTime

                                })

                        }
                    );


                console.log(
                    "/convert response:",
                    data
                );


                if(data.success){

                    currentJobId =
                        data.job_id;


                    if(!currentJobId){

                        throw new Error(
                            "job_idがサーバーから返されませんでした"
                        );

                    }


                    console.log(
                        "JOB ID:",
                        currentJobId
                    );


                    // ---------------------------------
                    // 状態確認開始
                    // ---------------------------------

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

                console.error(
                    "startConvert error:",
                    error
                );


                stopConvertTimer();


                convertButton.disabled =
                    false;


                convertButton.textContent =
                    "変換開始";


                alert(
                    "変換開始エラー:\n"
                    + error.message
                );

            }

        }


        // =====================================
        // 変換タイマー停止
        // =====================================

        function stopConvertTimer(){

            if(convertTimer){

                clearInterval(
                    convertTimer
                );

                convertTimer =
                    null;

            }

        }


        // =====================================
        // 変換ボタンを初期状態に戻す
        // =====================================

        function resetConvertButton(){

            stopConvertTimer();


            if(convertButton){

                convertButton.disabled =
                    false;

                convertButton.style.display =
                    "";

                convertButton.textContent =
                    "変換開始";

            }

        }


        // =====================================
        // 状態確認
        // =====================================

        async function checkStatus(){

            if(!currentJobId){

                console.error(
                    "currentJobIdがありません"
                );

                resetConvertButton();

                return;

            }


            try{

                console.log(
                    "STATUS CHECK:",
                    currentJobId
                );


                const data =
                    await fetchJson(
                        "/status/"
                        + encodeURIComponent(
                            currentJobId
                        )
                    );


                console.log(
                    "/status response:",
                    data
                );


                // ---------------------------------
                // complete
                // ---------------------------------

                if(
                    data.status ===
                    "complete"
                ){

                    stopConvertTimer();


                    convertButton.style.display =
                        "none";


                    showFiles(
                        data.files || []
                    );


                    return;

                }


                // ---------------------------------
                // error
                // ---------------------------------

                if(
                    data.status ===
                    "error"
                ){

                    stopConvertTimer();


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


                // ---------------------------------
                // queued / running
                // ---------------------------------

                if(
                    data.status ===
                    "queued"
                    ||
                    data.status ===
                    "running"
                ){

                    setTimeout(
                        checkStatus,
                        3000
                    );


                    return;

                }


                // ---------------------------------
                // 不明なstatus
                // ---------------------------------

                console.warn(
                    "未知のstatus:",
                    data.status
                );


                setTimeout(
                    checkStatus,
                    3000
                );

            }
            catch(error){

                console.error(
                    "checkStatus error:",
                    error
                );


                stopConvertTimer();


                if(convertButton){

                    convertButton.disabled =
                        false;

                    convertButton.textContent =
                        "変換開始";

                }


                alert(
                    "変換状態の確認に失敗しました。\n\n"
                    + error.message
                    + "\n\n"
                    + "Renderのログで /status/"
                    + currentJobId
                    + " のレスポンスを確認してください。"
                );

            }

        }


        // =====================================
        // ダウンロード表示
        // =====================================

        function showFiles(files){

            console.log(
                "完成ファイル:",
                files
            );


            if(!downloadArea){

                console.error(
                    "downloadAreaが見つかりません"
                );

                return;

            }


            let html = `

                <div class="download-buttons">

            `;


            let mp3File = "";


            // ---------------------------------
            // MP3検索
            // ---------------------------------

            files.forEach(
                function(file){

                    if(
                        typeof file === "string"
                        &&
                        file.toLowerCase().endsWith(
                            ".mp3"
                        )
                    ){

                        mp3File =
                            file;

                    }

                }
            );


            // ---------------------------------
            // Gemini用MP3ファイル名
            // ---------------------------------

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );


            if(
                geminiFile
                &&
                mp3File
            ){

                geminiFile.value =
                    mp3File;

            }


            // ---------------------------------
            // ファイル一覧
            // ---------------------------------

            files.forEach(
                function(file){

                    if(
                        typeof file !== "string"
                    ){

                        return;

                    }


                    // =============================
                    // MP3
                    // =============================

                    if(
                        file.toLowerCase().endsWith(
                            ".mp3"
                        )
                    ){

                        html += `

                            <a
                                href="/download/${encodeURIComponent(file)}"
                                download
                            >

                                <button
                                    type="button"
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


                    // =============================
                    // MP4
                    // =============================

                    else if(
                        file.toLowerCase().endsWith(
                            ".mp4"
                        )
                    ){

                        html += `

                            <a
                                href="/download/${encodeURIComponent(file)}"
                                download
                            >

                                <button
                                    type="button"
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


            downloadArea.innerHTML =
                html;


            // =====================================
            // SRTエリア
            // =====================================

            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if(
                srtArea
                &&
                mp3File
            ){

                srtArea.style.display =
                    "block";

            }
            else if(srtArea){

                srtArea.style.display =
                    "none";

            }


            // =====================================
            // SRT展開ボタン
            // =====================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );


            const srtContent =
                document.getElementById(
                    "srt-content"
                );


            if(
                toggle
                &&
                srtContent
            ){

                toggle.addEventListener(
                    "click",
                    function(){

                        if(
                            srtContent.style.display ===
                            "none"
                            ||
                            !srtContent.style.display
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


        // =====================================
        // Gemini文字起こし
        // =====================================

        const geminiButton =
            document.getElementById(
                "gemini-button"
            );


        if(geminiButton){

            geminiButton.addEventListener(
                "click",
                async function(){

                    const geminiFileElement =
                        document.getElementById(
                            "gemini-file"
                        );


                    const file =
                        geminiFileElement
                        ? geminiFileElement.value.trim()
                        : "";


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


                    if(!result){

                        alert(
                            "gemini-resultが見つかりません"
                        );

                        return;

                    }


                    let seconds =
                        0;


                    result.style.display =
                        "block";


                    result.textContent =
                        "文字起こし中... 0秒";


                    geminiButton.disabled =
                        true;


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

                        const data =
                            await fetchJson(
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


                        clearInterval(
                            timer
                        );


                        console.log(
                            "/gemini-transcribe response:",
                            data
                        );


                        if(data.success){

                            // ---------------------------------
                            // テキスト非表示
                            // ---------------------------------

                            result.style.display =
                                "none";


                            // ---------------------------------
                            // 既存SRTボタン削除
                            // ---------------------------------

                            const oldButton =
                                document.getElementById(
                                    "gemini-srt-download"
                                );


                            if(oldButton){

                                oldButton.remove();

                            }


                            // ---------------------------------
                            // SRTダウンロードボタン
                            // ---------------------------------

                            if(data.srt_file){

                                const srtButton =
                                    document.createElement(
                                        "a"
                                    );


                                srtButton.id =
                                    "gemini-srt-download";


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
                                    <button
                                        type="button"
                                        class="download-button"
                                    >
                                        srt
                                    </button>
                                    `;


                                result.parentNode.appendChild(
                                    srtButton
                                );

                            }
                            else{

                                result.style.display =
                                    "block";


                                result.textContent =
                                    "SRTファイルが返されませんでした";

                            }

                        }
                        else{

                            result.style.display =
                                "block";


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
                            "Gemini error:",
                            error
                        );


                        result.style.display =
                            "block";


                        result.textContent =
                            "エラー: "
                            + error.message;

                    }
                    finally{

                        geminiButton.disabled =
                            false;

                    }

                }
            );

        }

    }
);
