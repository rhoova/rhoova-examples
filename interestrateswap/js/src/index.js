import "./index.css"

const rhoova = require("@rhoova/node-client");

const taskData = {
    "fixedLeg": {},
    "floatingLeg": {},
    "floatingLegForecastCurve": {},
    "discountCurve": {},
    "yieldData": {}
};

function createTaskResult() {
    let createTask = document.querySelector('#formIrs');

    let apiKey = null;
    let apiSecret = null;
    createTask.addEventListener("submit", (event)=>{
        event.preventDefault();

        let form = $('#formIrs');

        var arrayData = $(form).serializeArray();

        arrayData.forEach((data) => {
            let legString = "fixedLeg";
            let floatingString = "floatingLeg";
            if(data.name.includes("apiKey")){
                apiKey = data.value
            }else if(data.name.includes("apiSecret")){
                apiSecret = data.value
            }else if (data.name.includes("fixedLeg")) {
                if(data.name.includes("coupon") || data.name.includes("endOfMonth")){
                    taskData["fixedLeg"][data.name.substring(legString.length, data.name.length)] =
                        data.name.includes("endOfMonth") ? data.value==='true' : parseFloat(data.value)
                }else{
                    taskData["fixedLeg"][data.name.substring(legString.length, data.name.length)] = data.value
                }
            } else if (data.name.includes("floatingLeg")) {
                if(data.name.includes("spread") || data.name.includes("endOfMonth")){
                    taskData["floatingLeg"][data.name.substring(floatingString.length, data.name.length)] =
                        data.name.includes("endOfMonth") ? (data.value === 'true') : parseFloat(data.value)
                }else{
                    taskData["floatingLeg"][data.name.substring(floatingString.length, data.name.length)] = data.value
                }
            } else if (data.name.includes("forecastCurve") && data.value!=='') {
               tryParseJSONObject(data.value, "floatingLegForecastCurve" );
            } else if (data.name.includes("discountCurve") && data.value!=='') {
                tryParseJSONObject(data.value, "discountCurve" );
            } else if (data.name.includes("yieldData") && data.value!=='') {
                tryParseJSONObject(data.value, "yieldData" );
            } else {
                if(data.name==="notional"){
                    taskData[data.name] = parseInt(data.value)
                }else{
                    taskData[data.name] = data.value
                }
            }
        });
       //  apiKey: "wPJmuD1ABTqGiZVy6r5uz", apiSecret: "Fgnhnz2WfwGbFv3db_1fWStWjLqaX0a-"
        let client = new rhoova.RhoovaClient({apiKey: apiKey, apiSecret: apiSecret});

        client.createTask({data: taskData, calculationType: rhoova.CalculationType.IRS, waitResult: true}).then((result) => {
            document.getElementById("taskBody").innerHTML = "";
            $.each(JSON.parse(result.result).data,function(index, value){


                let tBody = '<tr><td>'+value.accrualEnd+'</td><td>'+value.accrualStart+'</td><td>'+value.cashflow+'</td>' +
                    '<td>'+value.cashflowPv+'</td><td>'+value.currency+'</td><td>'+value.discountFactor+'</td>' +
                    '<td>'+value.fixingDate+'</td><td>'+value.instrument+'</td><td>'+value.leg+'</td>' +
                    '<td>'+value.notional+'</td><td>'+value.payOrReceive+'</td><td>'+value.rate+'</td>' +
                    '<td>'+value.spread+'</td><td>'+value.termToMatByDay+'</td><td>'+value.termToMatByYear+'</td>' +
                    '<td>'+value.zeroRate+'</td></tr>';

                $('#taskBody').append(tBody);
                document.getElementById("taskResult").style.display = "block"
                document.getElementById("errorResult").style.display = "none"

            })
        }).catch(error => {
            console.log(error);
            document.getElementById("taskResult").style.display = "none"
            document.getElementById("errorMessage").innerHTML = "";
            document.getElementById("errorResult").style.display = "block"
            document.getElementById("errorMessage").innerHTML = JSON.stringify((error))
            console.log(error)
        });
    })
}
function tryParseJSONObject (data, label){

    try {
        let object = JSON.parse(data);
        if (object && typeof object === "object") {
           return  taskData[label] = JSON.parse(data)
        }
    }
    catch (e) {
        document.getElementById("taskResult").style.display = "none";
        document.getElementById("errorJsonMessage").innerHTML = label + " is not in json format" ;
        document.getElementById("jsonFormatControl").style.display = "block";
        throw new Error(e);
    }

}

document.body.appendChild(createTaskResult());