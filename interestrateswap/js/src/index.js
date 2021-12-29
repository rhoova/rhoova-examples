import "./index.css"

const rhoova = require("@rhoova/node-client");

function createTaskResult() {
    let createTask = document.querySelector('#formIrs');

    createTask.addEventListener("submit", (event)=>{
        event.preventDefault();

        let form = $('#formIrs');

        var arrayData = $(form).serializeArray();

        let taskData = {
            "fixedLeg": {},
            "floatingLeg": {},
            "floatingLegForecastCurve": {},
            "discountCurve": {},
            "yieldData": {}
        };
        arrayData.forEach((data) => {
            let legString = "fixedLeg";
            let floatingString = "floatingLeg";
            if (data.name.includes("fixedLeg")) {
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
                taskData["floatingLegForecastCurve"] = JSON.parse(data.value)
            } else if (data.name.includes("discountCurve") && data.value!=='') {
                taskData["discountCurve"] = JSON.parse(data.value)
            } else if (data.name.includes("yieldData") && data.value!=='') {
                taskData["yieldData"] = JSON.parse(data.value)
            } else {
                if(data.name==="notional"){
                    taskData[data.name] = parseInt(data.value)
                }else{
                    taskData[data.name] = data.value
                }
            }
        });

        let client = new rhoova.RhoovaClient({apiKey: "wPJmuD1ABTqGiZVy6r5uz", apiSecret: "Fgnhnz2WfwGbFv3db_1fWStWjLqaX0a-"});

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


document.body.appendChild(createTaskResult());