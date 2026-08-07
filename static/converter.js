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

        // ------------------------------
        // Enterキーで確認
        // ------------------------------

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

                            method:"POST",

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



                const data =
                    await response.json();



                if(data.success){


                    document
                    .getElementById(
                        "convert-area"
                    )
                    .style.display =
                    "block";



                    document
                    .getElementById(
                        "filename"
                    )
                    .value =
                    data.filename;



                    document
                    .getElementById(
                        "end-time"
                    )
                    .value =
                    data.duration;


                }
                else{


                    alert(
                        data.message
                    );

                }


            }
            catch(error){

                console.error(error);

                alert(
                    "確認エラー"
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



            convertButton.disabled = true;



            convertSeconds = 0;


            convertButton.textContent =
                "変換中 0秒";



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


                const response =
                    await fetch(
                        "/convert",
                        {

                            method:"POST",

                            headers:{
                                "Content-Type":
                                "application/json"
                            },

                            body:
                            JSON.stringify({

                                url:url,
                                outputs:outputs,
                                start_time: document.getElementById("start-time").value.trim(),
                                end_time: document.getElementById("end-time").value.trim()


                            })

                        }
                    );



                const data =
                    await response.json();



                if(data.success){


                    currentJobId =
                        data.job_id;


                    checkStatus();


                }
                else{


                    throw new Error(
                        data.message
                    );

                }


            }
            catch(error){


                clearInterval(
                    convertTimer
                );


                convertButton.disabled =
                    false;


                convertButton.textContent =
                    "変換開始";


                alert(
                    error.message
                );


            }


        }





        // ================================
        // 状態確認
        // ================================


        function checkStatus(){


            fetch(
                `/status/${currentJobId}`
            )

            .then(
                response =>
                    response.json()
            )

            .then(
                data =>{


                    if(
                        data.status === "complete"
                    ){


                        clearInterval(
                            convertTimer
                        );



                        // 変換開始ボタン非表示

                        convertButton.style.display =
                            "none";



                        showFiles(
                            data.files
                        );


                    }

                    else if(
                        data.status === "error"
                    ){


                        clearInterval(
                            convertTimer
                        );


                        alert(
                            data.message
                        );


                    }

                    else{


                        setTimeout(
                            checkStatus,
                            3000
                        );


                    }


                }
            );


        }





// ================================
// ダウンロード表示
// ================================

function showFiles(files){

    console.log(files);


    let html = `

    <div class="download-buttons">

    `;


    let mp3File = "";


    files.forEach(function(file){

        if(file.endsWith(".mp3")){

            mp3File = file;

        }

    });



    // Gemini用mp3ファイル名セット

    const geminiFile =
        document.getElementById(
            "gemini-file"
        );


    if(geminiFile && mp3File){

        geminiFile.value = mp3File;

    }




    files.forEach(function(file){



        if(file.endsWith(".mp3")){


            html += `


            <a
            href="/download/${encodeURIComponent(file)}"
            download>


            <button
            class="download-button">
            mp3
            </button>


            </a>



            <button
            type="button"
            id="srt-toggle-button"
            class="srt-toggle-button">
            ▲
            </button>


            `;


        }



        else if(file.endsWith(".mp4")){


            html += `


            <a
            href="/download/${encodeURIComponent(file)}"
            download>


            <button
            class="download-button">
            mp4
            </button>


            </a>


            `;


        }



    });



    html += `

    </div>

    `;



    downloadArea.innerHTML =
        html;




    // ================================
    // SRT表示
    // ================================


    const srtArea =
        document.getElementById(
            "srtArea"
        );


    if(srtArea && mp3File){

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



    if(toggle && srtContent){


        toggle.addEventListener(
            "click",
            function(){


                if(
                    srtContent.style.display === "none"
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
// Gemini 文字起こし
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

                            method:"POST",

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



                const data =
                    await response.json();



                clearInterval(
                    timer
                );



                if(data.success){


                    // テキスト非表示

                    result.style.display =
                        "none";



                    // SRTダウンロードボタン表示

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
                        data.message;


                }



            }
            catch(error){


                clearInterval(
                    timer
                );


                result.textContent =
                    "エラー: "
                    + error.message;


            }


        }
    );

}

});   // ← DOMContentLoaded終了
