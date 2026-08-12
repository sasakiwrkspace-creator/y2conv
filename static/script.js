// =====================================
// YouTube Converter JavaScript
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    function(){

        console.log(
            "================================"
        );

        console.log(
            "YouTube Converter JavaScript 起動"
        );

        console.log(
            "================================"
        );


        // =================================
        // DOM
        // =================================

        const urlInput =
            document.getElementById(
                "youtube-url"
            );

        const convertButton =
            document.getElementById(
                "convertBtn"
            );

        const downloadArea =
            document.getElementById(
                "downloadArea"
            );


        // =================================
        // DOM確認
        // =================================

        console.log(
            "youtube-url:",
            urlInput
        );

        console.log(
            "convertBtn:",
            convertButton
        );

        console.log(
            "downloadArea:",
            downloadArea
        );


        // =================================
        // Job
        // =================================

        let currentJobId = null;


        // =================================
        // MP3変換タイマー
        // =================================

        let convertSeconds = 0;

        let convertTimer = null;


        // =================================
        // Gemini用
        //
        // MP3作成時の時間を保存
        // =================================

        let originalStartTime = "";

        let originalEndTime = "";


        // =================================
        // 画面上の処理状況表示
        // =================================

        let convertStatus = null;


        function createConvertStatus(){

            if(convertStatus){

                return;

            }


            convertStatus =
                document.createElement(
                    "div"
                );


            convertStatus.id =
                "convert-status";


            convertStatus.style.marginTop =
                "10px";


            convertStatus.style.padding =
                "8px";


            convertStatus.style.fontSize =
                "14px";


            convertStatus.style.color =
                "#555";


            if(convertButton){

                convertButton.parentNode
                    .insertBefore(
                        convertStatus,
                        convertButton.nextSibling
                    );

            }

        }


        function setConvertStatus(
            message
        ){

            createConvertStatus();


            if(convertStatus){

                convertStatus.textContent =
                    message;

            }


            console.log(
                "[STATUS]",
                message
            );

        }


        // =================================
        // 時間入力
        // =================================

        function setupTimeInput(
            element
        ){

            if(!element){

                return;

            }


            element.addEventListener(
                "input",
                function(){

                    this.value =
                        this.value.replace(
                            /[^0-9]/g,
                            ""
                        );


                    if(
                        this.value.length > 2
                    ){

                        this.value =
                            this.value.substring(
                                0,
                                2
                            );

                    }

                }
            );


            element.addEventListener(
                "paste",
                function(event){

                    event.preventDefault();


                    const text =
                        (
                            event.clipboardData ||
                            window.clipboardData
                        )
                        .getData("text");


                    const numbers =
                        text.replace(
                            /[^0-9]/g,
                            ""
                        )
                        .substring(
                            0,
                            2
                        );


                    this.value =
                        numbers;

                }
            );

        }


        setupTimeInput(
            document.getElementById(
                "start-hour"
            )
        );

        setupTimeInput(
            document.getElementById(
                "start-minute"
            )
        );

        setupTimeInput(
            document.getElementById(
                "start-second"
            )
        );

        setupTimeInput(
            document.getElementById(
                "end-hour"
            )
        );

        setupTimeInput(
            document.getElementById(
                "end-minute"
            )
        );

        setupTimeInput(
            document.getElementById(
                "end-second"
            )
        );


        // =================================
        // 時間入力値を正規化
        // =================================

        function normalizeTimeInputs(){

            const startMinute =
                document.getElementById(
                    "start-minute"
                );

            const startSecond =
                document.getElementById(
                    "start-second"
                );

            const endMinute =
                document.getElementById(
                    "end-minute"
                );

            const endSecond =
                document.getElementById(
                    "end-second"
                );


            if(
                startMinute &&
                startMinute.value !== "" &&
                Number(startMinute.value) > 59
            ){

                startMinute.value =
                    "59";

            }


            if(
                startSecond &&
                startSecond.value !== "" &&
                Number(startSecond.value) > 59
            ){

                startSecond.value =
                    "59";

            }


            if(
                endMinute &&
                endMinute.value !== "" &&
                Number(endMinute.value) > 59
            ){

                endMinute.value =
                    "59";

            }


            if(
                endSecond &&
                endSecond.value !== "" &&
                Number(endSecond.value) > 59
            ){

                endSecond.value =
                    "59";

            }

        }


        // =================================
        // 時間取得
        // =================================

        function getTimeValues(){

            normalizeTimeInputs();


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


            const sh =
                startHour &&
                startHour.value !== ""
                    ? Number(
                        startHour.value
                    )
                    : 0;


            const sm =
                startMinute &&
                startMinute.value !== ""
                    ? Number(
                        startMinute.value
                    )
                    : 0;


            const ss =
                startSecond &&
                startSecond.value !== ""
                    ? Number(
                        startSecond.value
                    )
                    : 0;


            const eh =
                endHour &&
                endHour.value !== ""
                    ? Number(
                        endHour.value
                    )
                    : 0;


            const em =
                endMinute &&
                endMinute.value !== ""
                    ? Number(
                        endMinute.value
                    )
                    : 0;


            const es =
                endSecond &&
                endSecond.value !== ""
                    ? Number(
                        endSecond.value
                    )
                    : 0;


            const startTotal =
                (
                    sh * 3600
                )
                +
                (
                    sm * 60
                )
                +
                ss;


            const endTotal =
                (
                    eh * 3600
                )
                +
                (
                    em * 60
                )
                +
                es;


            return {

                startTotal:
                    startTotal,

                endTotal:
                    endTotal,

                startText:
                    formatTime(
                        sh,
                        sm,
                        ss
                    ),

                endText:
                    formatTime(
                        eh,
                        em,
                        es
                    )

            };

        }


        // =================================
        // HH:MM:SS
        // =================================

        function formatTime(
            hour,
            minute,
            second
        ){

            return (

                String(hour)
                    .padStart(2, "0")

                + ":"

                + String(minute)
                    .padStart(2, "0")

                + ":"

                + String(second)
                    .padStart(2, "0")

            );

        }


        // =================================
        // 時間範囲
        // =================================

        function getTimeRange(){

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


            const hasStart =
                (
                    startHour &&
                    startHour.value !== ""
                )
                ||
                (
                    startMinute &&
                    startMinute.value !== ""
                )
                ||
                (
                    startSecond &&
                    startSecond.value !== ""
                );


            const hasEnd =
                (
                    endHour &&
                    endHour.value !== ""
                )
                ||
                (
                    endMinute &&
                    endMinute.value !== ""
                )
                ||
                (
                    endSecond &&
                    endSecond.value !== ""
                );


            // =================================
            // 時間指定なし
            // =================================

            if(
                !hasStart &&
                !hasEnd
            ){

                return {

                    enabled:
                        false,

                    startTime:
                        "",

                    endTime:
                        ""

                };

            }


            const values =
                getTimeValues();


            // =================================
            // 終了時間だけ
            // =================================

            if(
                !hasStart &&
                hasEnd
            ){

                if(
                    values.endTotal <= 0
                ){

                    throw new Error(
                        "終了時間を入力してください"
                    );

                }


                return {

                    enabled:
                        true,

                    startTime:
                        "00:00:00",

                    endTime:
                        values.endText

                };

            }


            // =================================
            // 開始時間だけ
            // =================================

            if(
                hasStart &&
                !hasEnd
            ){

                throw new Error(
                    "終了時間を入力してください"
                );

            }


            // =================================
            // 開始 >= 終了
            // =================================

            if(
                values.startTotal >=
                values.endTotal
            ){

                throw new Error(
                    "終了時間は開始時間より後にしてください"
                );

            }


            return {

                enabled:
                    true,

                startTime:
                    values.startText,

                endTime:
                    values.endText

            };

        }


        // =================================
        // URL Enter
        // =================================

        if(urlInput){

            urlInput.addEventListener(
                "keydown",
                function(event){

                    if(
                        event.key === "Enter"
                    ){

                        event.preventDefault();

                        console.log(
                            "URL Enter検知"
                        );

                        startConvert();

                    }

                }
            );

        }


        // =================================
        // 実行ボタン
        // =================================

        if(convertButton){

            convertButton.addEventListener(
                "click",
                function(event){

                    event.preventDefault();

                    console.log(
                        "================================"
                    );

                    console.log(
                        "実行ボタン CLICK"
                    );

                    console.log(
                        "================================"
                    );


                    startConvert();

                }
            );

        }
        else{

            console.error(
                "convertBtn が見つかりません"
            );

        }


        // =================================
        // MP3変換開始
        // =================================

        async function startConvert(){

            console.log(
                "startConvert() 開始"
            );


            const url =
                urlInput
                ? urlInput.value.trim()
                : "";


            console.log(
                "入力URL:",
                url
            );


            if(!url){

                alert(
                    "YouTube URLを入力してください"
                );

                return;

            }


            // =================================
            // 時間範囲
            // =================================

            let timeRange;


            try{

                timeRange =
                    getTimeRange();

            }
            catch(error){

                alert(
                    error.message
                );

                return;

            }


            console.log(
                "時間範囲:",
                timeRange
            );


            // =================================
            // ボタン
            // =================================

            if(convertButton){

                convertButton.disabled =
                    true;

                convertButton.textContent =
                    "実行中 0秒";

            }


            // =================================
            // タイマー開始
            // =================================

            convertSeconds =
                0;


            if(convertTimer){

                clearInterval(
                    convertTimer
                );

            }


            convertTimer =
                setInterval(
                    function(){

                        convertSeconds++;


                        if(convertButton){

                            convertButton.textContent =
                                "実行中 "
                                +
                                convertSeconds
                                +
                                "秒";

                        }


                        setConvertStatus(
                            "MP3変換中... "
                            +
                            convertSeconds
                            +
                            "秒"
                        );


                    },
                    1000
                );


            setConvertStatus(
                "MP3変換を開始しています... 0秒"
            );


            // =================================
            // 前回表示削除
            // =================================

            if(downloadArea){

                downloadArea.innerHTML =
                    "";

            }


            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if(srtArea){

                srtArea.style.display =
                    "none";

            }


            try{

                console.log(
                    "================================"
                );

                console.log(
                    "MP3変換開始"
                );

                console.log(
                    "URL:",
                    url
                );

                console.log(
                    "時間指定:",
                    timeRange
                );

                console.log(
                    "================================"
                );


                setConvertStatus(
                    "MP3変換リクエスト送信中..."
                );


                // =================================
                // /convert
                // =================================

                const response =
                    await fetch(
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

                                    url:
                                        url,

                                    outputs:
                                        [
                                            "mp3"
                                        ],

                                    start_time:
                                        timeRange.startTime,

                                    end_time:
                                        timeRange.endTime

                                })

                        }
                    );


                console.log(
                    "/convert response:",
                    response.status
                );


                // =================================
                // HTTPエラー
                // =================================

                if(!response.ok){

                    const text =
                        await response.text();


                    throw new Error(
                        "HTTP "
                        +
                        response.status
                        +
                        " : "
                        +
                        (
                            text ||
                            "サーバーエラー"
                        )
                    );

                }


                setConvertStatus(
                    "MP3変換ジョブを確認しています..."
                );


                // =================================
                // JSON
                // =================================

                const text =
                    await response.text();


                console.log(
                    "/convert response text:",
                    text
                );


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
                catch(error){

                    console.error(
                        "JSON解析エラー:",
                        error
                    );


                    console.error(
                        "レスポンス:",
                        text
                    );


                    throw new Error(
                        "サーバーから正しいJSONが返されませんでした"
                    );

                }


                console.log(
                    "/convert JSON:",
                    data
                );


                // =================================
                // Job開始
                // =================================

                if(data.success){

                    currentJobId =
                        data.job_id;


                    if(!currentJobId){

                        throw new Error(
                            "JOB IDが返されませんでした"
                        );

                    }


                    // =================================
                    // MP3作成時の時間を保存
                    // =================================

                    originalStartTime =
                        timeRange.startTime;

                    originalEndTime =
                        timeRange.endTime;


                    console.log(
                        "MP3作成時 開始:",
                        originalStartTime
                    );

                    console.log(
                        "MP3作成時 終了:",
                        originalEndTime
                    );


                    console.log(
                        "MP3 JOB:",
                        currentJobId
                    );


                    setConvertStatus(
                        "MP3変換中... JOB: "
                        +
                        currentJobId
                        +
                        " / "
                        +
                        convertSeconds
                        +
                        "秒"
                    );


                    checkStatus();

                }
                else{

                    throw new Error(
                        data.message ||
                        "MP3作成を開始できませんでした"
                    );

                }

            }
            catch(error){

                stopConvertTimer();


                if(convertButton){

                    convertButton.disabled =
                        false;

                    convertButton.textContent =
                        "実行";

                }


                setConvertStatus(
                    "MP3変換エラー"
                );


                console.error(
                    "MP3変換エラー:",
                    error
                );


                alert(
                    error.message
                );

            }

        }


        // =================================
        // タイマー停止
        // =================================

        function stopConvertTimer(){

            if(convertTimer){

                clearInterval(
                    convertTimer
                );

                convertTimer =
                    null;

            }

        }


        // =================================
        // JOB状態確認
        // =================================

        async function checkStatus(){

            if(!currentJobId){

                console.error(
                    "JOB IDがありません"
                );

                return;

            }


            console.log(
                "JOB状態確認:",
                currentJobId
            );


            try{

                const response =
                    await fetch(
                        "/status/"
                        +
                        encodeURIComponent(
                            currentJobId
                        ),
                        {

                            method:
                                "GET",

                            cache:
                                "no-store"

                        }
                    );


                console.log(
                    "STATUS HTTP:",
                    response.status
                );


                // =================================
                // HTTPエラー
                // =================================

                if(!response.ok){

                    const text =
                        await response.text();


                    console.warn(
                        "STATUS ERROR:",
                        response.status,
                        text
                    );


                    if(
                        response.status === 502 ||
                        response.status === 503 ||
                        response.status === 504
                    ){

                        setConvertStatus(
                            "サーバー一時エラー。再確認中... "
                            +
                            convertSeconds
                            +
                            "秒"
                        );


                        setTimeout(
                            checkStatus,
                            3000
                        );


                        return;

                    }


                    throw new Error(
                        "HTTP "
                        +
                        response.status
                        +
                        " : "
                        +
                        (
                            text ||
                            "サーバーエラー"
                        )
                    );

                }


                // =================================
                // 本文
                // =================================

                const text =
                    await response.text();


                if(!text){

                    setConvertStatus(
                        "状態確認の応答が空です。再確認中... "
                        +
                        convertSeconds
                        +
                        "秒"
                    );


                    setTimeout(
                        checkStatus,
                        3000
                    );


                    return;

                }


                let data;


                try{

                    data =
                        JSON.parse(text);

                }
                catch(error){

                    console.error(
                        "STATUS JSON解析エラー:",
                        error
                    );


                    setConvertStatus(
                        "状態確認データを解析できません。再確認中..."
                    );


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


                // =================================
                // 画面表示
                // =================================

                setConvertStatus(
                    "MP3変換中... "
                    +
                    convertSeconds
                    +
                    "秒 / 状態: "
                    +
                    (
                        data.status ||
                        "unknown"
                    )
                );


                // =================================
                // 完了
                // =================================

                if(
                    data.status ===
                    "complete"
                ){

                    stopConvertTimer();


                    setConvertStatus(
                        "MP3変換完了！ "
                        +
                        convertSeconds
                        +
                        "秒"
                    );


                    if(convertButton){

                        convertButton.style.display =
                            "none";

                    }


                    showFiles(
                        Array.isArray(
                            data.files
                        )
                        ? data.files
                        : []
                    );


                    return;

                }


                // =================================
                // エラー
                // =================================

                if(
                    data.status ===
                    "error"
                ){

                    stopConvertTimer();


                    if(convertButton){

                        convertButton.disabled =
                            false;

                        convertButton.textContent =
                            "実行";

                    }


                    setConvertStatus(
                        "MP3変換エラー"
                    );


                    alert(
                        data.message ||
                        "MP3作成中にエラーが発生しました"
                    );


                    return;

                }


                // =================================
                // queued / running
                // =================================

                setTimeout(
                    checkStatus,
                    3000
                );

            }
            catch(error){

                console.error(
                    "状態確認エラー:",
                    error
                );


                setConvertStatus(
                    "状態確認エラー。再確認中... "
                    +
                    convertSeconds
                    +
                    "秒"
                );


                setTimeout(
                    checkStatus,
                    3000
                );

            }

        }


        // =================================
        // 完成ファイル表示
        // =================================

        function showFiles(
            files
        ){

            console.log(
                "完成ファイル:",
                files
            );


            let mp3File =
                "";


            files.forEach(
                function(file){

                    if(
                        file &&
                        file
                            .toLowerCase()
                            .endsWith(".mp3")
                    ){

                        mp3File =
                            file;

                    }

                }
            );


            // =================================
            // MP3なし
            // =================================

            if(!mp3File){

                if(downloadArea){

                    downloadArea.innerHTML =
                        `
                        <div>
                            MP3ファイルが作成されませんでした
                        </div>
                        `;

                }


                return;

            }


            // =================================
            // Gemini用ファイル名
            // =================================

            const geminiFile =
                document.getElementById(
                    "gemini-file"
                );


            if(geminiFile){

                geminiFile.value =
                    mp3File;

            }


            // =================================
            // MP3表示
            // =================================

            if(downloadArea){

                downloadArea.innerHTML =
                    `

                    <div
                        class="download-buttons"
                    >

                        <span>
                            MP3のダウンロード
                        </span>


                        <a
                            href="/download/${encodeURIComponent(mp3File)}"
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
                            aria-label="Gemini文字起こしを表示"
                        >
                            ▲
                        </button>

                    </div>

                    `;

            }


            // =================================
            // Gemini部分
            // =================================

            const srtArea =
                document.getElementById(
                    "srtArea"
                );


            if(srtArea){

                srtArea.style.display =
                    "none";

            }


            // =================================
            // ▲ボタン
            // =================================

            const toggle =
                document.getElementById(
                    "srt-toggle-button"
                );


            if(toggle){

                toggle.addEventListener(
                    "click",
                    function(){

                        if(!srtArea){

                            return;

                        }


                        if(
                            srtArea.style.display ===
                            "none"
                        ){

                            srtArea.style.display =
                                "block";


                            toggle.textContent =
                                "▼";

                        }
                        else{

                            srtArea.style.display =
                                "none";


                            toggle.textContent =
                                "▲";

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

                    console.log(
                        "Geminiボタン CLICK"
                    );


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


                    // =================================
                    // 現在の時間
                    // =================================

                    let currentTimeRange;


                    try{

                        currentTimeRange =
                            getTimeRange();

                    }
                    catch(error){

                        alert(
                            error.message
                        );

                        return;

                    }


                    console.log(
                        "================================"
                    );

                    console.log(
                        "Gemini文字起こし開始"
                    );

                    console.log(
                        "MP3:",
                        file
                    );

                    console.log(
                        "MP3作成時 開始:",
                        originalStartTime
                    );

                    console.log(
                        "MP3作成時 終了:",
                        originalEndTime
                    );

                    console.log(
                        "Gemini実行時 開始:",
                        currentTimeRange.startTime
                    );

                    console.log(
                        "Gemini実行時 終了:",
                        currentTimeRange.endTime
                    );

                    console.log(
                        "================================"
                    );


                    const result =
                        document.getElementById(
                            "gemini-result"
                        );


                    let seconds =
                        0;


                    if(result){

                        result.style.display =
                            "block";

                        result.textContent =
                            "文字起こし中... 0秒";

                    }


                    geminiButton.disabled =
                        true;


                    geminiButton.textContent =
                        "文字変換中...";


                    const timer =
                        setInterval(
                            function(){

                                seconds++;


                                if(result){

                                    result.textContent =
                                        "文字起こし中... "
                                        +
                                        seconds
                                        +
                                        "秒";

                                }

                            },
                            1000
                        );


                    try{

                        // =================================
                        // Gemini API
                        // =================================

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

                                            file:
                                                file,

                                            original_start_time:
                                                originalStartTime,

                                            original_end_time:
                                                originalEndTime,

                                            start_time:
                                                currentTimeRange.startTime,

                                            end_time:
                                                currentTimeRange.endTime

                                        })

                                }
                            );


                        console.log(
                            "Gemini HTTP:",
                            response.status
                        );


                        if(!response.ok){

                            const text =
                                await response.text();


                            throw new Error(
                                "HTTP "
                                +
                                response.status
                                +
                                " : "
                                +
                                (
                                    text ||
                                    "Geminiサーバーエラー"
                                )
                            );

                        }


                        const text =
                            await response.text();


                        if(!text){

                            throw new Error(
                                "Geminiから空のレスポンスが返されました"
                            );

                        }


                        let data;


                        try{

                            data =
                                JSON.parse(text);

                        }
                        catch(error){

                            console.error(
                                "Gemini JSON解析エラー:",
                                error
                            );

                            console.error(
                                "Geminiレスポンス:",
                                text
                            );


                            throw new Error(
                                "Geminiから正しいJSONが返されませんでした"
                            );

                        }


                        clearInterval(
                            timer
                        );


                        // =================================
                        // 成功
                        // =================================

                        if(data.success){

                            if(result){

                                result.style.display =
                                    "none";

                            }


                            geminiButton.style.display =
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
                                <button
                                    type="button"
                                    class="download-button"
                                >
                                    srt
                                </button>
                                `;


                            if(
                                geminiButton.parentNode
                            ){

                                geminiButton.parentNode
                                    .appendChild(
                                        srtButton
                                    );

                            }


                            console.log(
                                "Gemini文字起こし完了"
                            );

                            console.log(
                                "Gemini使用MP3:",
                                data.mp3_file
                            );

                            console.log(
                                "時間変更:",
                                data.time_changed
                            );

                        }
                        else{

                            geminiButton.disabled =
                                false;


                            geminiButton.textContent =
                                "Geminiで文字起こし";


                            if(result){

                                result.textContent =
                                    data.message ||
                                    "文字起こしに失敗しました";

                            }

                        }

                    }
                    catch(error){

                        clearInterval(
                            timer
                        );


                        geminiButton.disabled =
                            false;


                        geminiButton.textContent =
                            "Geminiで文字起こし";


                        console.error(
                            "Geminiエラー:",
                            error
                        );


                        if(result){

                            result.textContent =
                                "エラー: "
                                +
                                error.message;

                        }

                    }

                }
            );

        }
        else{

            console.warn(
                "gemini-button が見つかりません"
            );

        }


    }
);
