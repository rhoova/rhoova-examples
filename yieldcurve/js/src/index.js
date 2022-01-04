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
                if (data.value) {
                    isJSONObject(data.value, "yieldData")
                }else {
                    taskData["yieldData"] = yieldDataObject
                }

            }
            else {
                    taskData[data.name] = data.value
            }
        });
        let client = new rhoova.RhoovaClient({apiKey: apiKey, apiSecret: apiSecret});
		client.createTask({data: taskData, calculationType: rhoova.CalculationType.YIELD_CURVE, waitResult: true}).then((result) => {
            if(result.error){
                console.log(result.error)
            }else{
                document.getElementById("loadingIcon").style.display = "none";
                let resultData = JSON.parse(result.result);
                console.log("result", resultData);
                let yValues = [];
                let xValues  = [];
                resultData.zeroRates.forEach((data)=> {
                    yValues.push(data.rate);
                    xValues.push(data.date);
                });
                var myBarChart = new Chart(document.getElementById("bar-chart"), {
                    type: 'line',
                    data: {
                        labels: valuelabel,
                        datasets: [
                            {
                                label: "Population (millions)",
                                backgroundColor: "#3e95cd",
                                data: valuedata,

                            }
                        ]
                    },
                    options: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: 'Predicted world population (millions) in 2050'
                        },
                        scales: {
                            xAxes: [{
                                gridLines: {
                                    display:false
                                }
                            }],
                            yAxes: [{
                                gridLines: {
                                    display:false,
                                    drawBorder: false
                                },
                                ticks: {
                                    display: false
                                }
                            }]
                        },
                        plugins: {
                            datalabels: {
                                color: 'white',
                                display: function(context) {
                                    console.log("Algo: "+context);
                                    return context.dataset.data[context.dataIndex] > 15;
                                },
                                font: {
                                    weight: 'bold'
                                },
                                formatter: function(value, context) {
                                    return context.dataIndex + ': ' + Math.round(value*100) + '%';
                                }
                            }
                        }
                    }
                });
            //    let ctx = document.getElementById('myChart').getContext(2);

                console.log(document.getElementById('bar-chart').value);
             //   document.getElementById('mycanvas').data2.value= yValues;


            }

        }).catch(error => {
            document.getElementById("loadingIcon").style.display = "none";
            document.getElementById("errorMessage").innerHTML = "";
            document.getElementById("errorResult").style.display = "block";
            document.getElementById("errorMessage").innerHTML = JSON.stringify((error));
            console.log(error)
        });
    })
}

function isJSONObject(data, label) {
    try {
        if (document.activeElement.id === "randomizeAndSubmit" && label === "yieldData") {
            taskData[label] = randomizeData(JSON.parse(data))
        } else if (document.activeElement.id === "submit" && label === "yieldData") {
            taskData[label] = JSON.parse(data)
        } if (label === 'startEndDates'){
            taskData["forwardRates"][label] = JSON.parse(data)
        } else {
            taskData[label] = JSON.parse(data)
        }
    } catch (e) {
        document.getElementById("loadingIcon").style.display = "none";
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