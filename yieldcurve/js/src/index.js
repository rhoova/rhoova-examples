import "./index.css"

var yieldDataObject=require("./yieldData.json");
var analysisDateObject=require("./analysisDate.json");
var yieldCurveObject=require("./yieldcurve.json");

const rhoova = require("@rhoova/node-client");

const taskData = {
    "yieldCurve": {},
    "yieldData": {},
    "zeroRates": {},
    "forwardRates": {},
    "discountRates": {}
};

function createTaskResult() {
    let createTask = document.querySelector('#formYieldCurve');
    let apiKey = null;
    let apiSecret = null;
    createTask.addEventListener("submit", (event)=>{
        event.preventDefault();

        let form = $('#formYieldCurve');

        var arrayData = $(form).serializeArray();
        document.getElementById("loadingIcon").style.display = "inline-block";
        document.getElementById("errorResult").style.display = "none";
        arrayData.forEach((data) => {
            let zeroString = "zeroRates";
            let forwardString = "forwardRates";
            let discountString = "discountRates";
            if(data.name.includes("apiKey")){
                apiKey = data.value
            }else if(data.name.includes("apiSecret")){
                apiSecret = data.value
            }else if (data.name.includes("zeroRates")) {
                if(data.name.includes("zeroRatesanalysisDates")){
                    taskData["zeroRates"][data.name.substring(zeroString.length, data.name.length)] = (data.value).split(",")
                }else{
                    taskData["zeroRates"][data.name.substring(zeroString.length, data.name.length)] = data.value
                }
            } else if (data.name.includes("forwardRates")) {
                if (data.name.includes('forwardRatesstartEndDates')) {
                    if (data.value) {
                        isJSONObject(data.value, "startEndDates");
                    } else {
                        taskData["forwardRates"]["startEndDates"] = analysisDateObject
                    }

                }else{
                    taskData["forwardRates"][data.name.substring(forwardString.length, data.name.length)] = data.value
                }
            } else if (data.name.includes("discountRates") && data.value!=='') {
                taskData["discountRates"][data.name.substring(discountString.length, data.name.length)] = (data.value).split(",")
            }
            else if (data.name.includes("yieldCurve")) {
                if (data.value) {
                    isJSONObject(data.value, "yieldCurve");
                }else {
                    taskData["yieldCurve"] = yieldCurveObject
                }
            }
            else if (data.name.includes("yieldData")) {
                isJSONObject(data.value ? data.value : JSON.stringify(yieldDataObject), "yieldData")
            }
            else {
                    taskData[data.name] = data.value
            }
        });
        let client = new rhoova.RhoovaClient({apiKey: apiKey, apiSecret: apiSecret});
		client.createTask({data: taskData, calculationType: rhoova.CalculationType.YIELD_CURVE, waitResult: true}).then((result) => {
            document.getElementById("zeroResultBody").innerHTML = "";
            document.getElementById("forwardResultBody").innerHTML = "";
            document.getElementById("discountResultBody").innerHTML = "";
            document.getElementById("loadingIcon").style.display = "none";
		    if(result.error){
                document.getElementById("taskPropertiesResult").style.display = "none";
                document.getElementById("errorMessage").innerHTML = "";
                document.getElementById("errorResult").style.display = "block";
                document.getElementById("errorMessage").innerHTML = JSON.stringify((result.error));
            }else{
                document.getElementById("loadingIcon").style.display = "none";
                let resultData = JSON.parse(result.result);
                let yValues = [];
                let xValues  = [];
                resultData.zeroRates.forEach((data)=> {
                    yValues.push(data.rate);
                    xValues.push(data.date);
                    let tBody = '<tr><td>'+data.date+'</td><td>'+ data.rate+'</td></tr>';
                    $('#zeroResultBody').append(tBody);
                });
                resultData.forwardRates.forEach((data)=> {
                    let tBody = '<tr><td>'+data.date+'</td><td>'+ data.rate+'</td></tr>';
                    $('#forwardResultBody').append(tBody);
                });
                resultData.discountRates.forEach((data)=> {
                    let tBody = '<tr><td>'+data.date+'</td><td>'+ data.rate+'</td></tr>';
                    $('#discountResultBody').append(tBody);
                });
                resultData.yieldNodeData.forEach((data)=> {
                    let tBody = '<tr><td>'+data.date+'</td><td>'+ data.rate+'</td></tr>';
                    $('#nodeDataResultBody').append(tBody);
                });

                let kanvas = document.getElementById('line-chart');
                let grafik = new Chart(kanvas, {
                    type: 'line',
                    data: {
                        labels: xValues,
                        datasets: [{
                            label: 'Zero Rates',
                            data: yValues,
                            borderColor: [
                                'rgba(255, 100, 10, 120)'
                            ],
                            fill: false,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            xAxes: [{
                                ticks: {
                                    fontColor: "#CCC", // this here
                                },
                            }],
                            yAxes: [{
                                ticks: {
                                    fontColor: "#CCC", // this here
                                },
                            }],
                        }
                    }
                });

                document.getElementById("taskPropertiesResult").style.display = "block";
                document.getElementById("errorResult").style.display = "none"

            }

        }).catch(error => {
            document.getElementById("loadingIcon").style.display = "none";
            document.getElementById("errorMessage").innerHTML = "";
            document.getElementById("taskPropertiesResult").style.display = "none";
            document.getElementById("errorResult").style.display = "block";
            document.getElementById("errorMessage").innerHTML = JSON.stringify((error));
            console.log(error)
        });
    })
}

function isJSONObject(data, label) {
    try {
        JSON.parse(data);
        if (document.activeElement.id === "randomizeAndSubmit" && label === "yieldData") {
            taskData[label] = randomizeData(JSON.parse(data))
        } else if (document.activeElement.id === "submit" && label === "yieldData") {
            taskData[label] = JSON.parse(data)
        } else if (label === 'startEndDates'){
            taskData["forwardRates"][label] = JSON.parse(data)
        } else {
            taskData[label] = JSON.parse(data)
        }
    } catch (e) {
        document.getElementById("loadingIcon").style.display = "none";
        document.getElementById("taskPropertiesResult").style.display = "none";
        document.getElementById("errorMessage").innerHTML = "";
        document.getElementById("errorResult").style.display = "block";
        document.getElementById("errorMessage").innerHTML = "Invalid "+ label + " object";
        throw new Error(e);
    }

}

function randomizeData(data){
    data.forEach((item, index) => {
        item.value = Math.floor((Math.random() * item.value+0.01) - item.value-0.01) *  0.0025;
        data[index] = item;

    });

    return data;
}


document.body.appendChild(createTaskResult());