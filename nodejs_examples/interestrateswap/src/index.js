import('./index.css')

var jsonData = require('./yieldcurve.json')
var yieldData = require('./yieldData.json')
//console.log(JSON.stringify(yieldData))

const rhoova = require('@rhoova/node-client')

const taskData = {
	fixedLeg: {},
	floatingLeg: {},
	floatingLegForecastCurve: {},
	discountCurve: {},
	yieldData: {}
}

const yieldcurveData = {
	yieldCurve: {},
	yieldData: {}
}

function createTaskResult() {
	let createTask = document.querySelector('#formIrs')
	let apiKey = null
	let apiSecret = null
	createTask.addEventListener('submit', (event) => {
		event.preventDefault()

		let form = $('#formIrs')

		var arrayData = $(form).serializeArray()
		document.getElementById('loadingIcon').style.display = 'inline-block'
		document.getElementById('errorResult').style.display = 'none'
		arrayData.forEach((data) => {
			let legString = 'fixedLeg'
			let floatingString = 'floatingLeg'
			if (data.name.includes('apiKey')) {
				apiKey = data.value
			} else if (data.name.includes('apiSecret')) {
				apiSecret = data.value
			} else if (data.name.includes('fixedLeg')) {
				if (data.name.includes('coupon') || data.name.includes('endOfMonth')) {
					taskData['fixedLeg'][data.name.substring(legString.length, data.name.length)] = data.name.includes('endOfMonth') ? data.value === 'true' : parseFloat(data.value)
				} else {
					taskData['fixedLeg'][data.name.substring(legString.length, data.name.length)] = data.value
				}
			} else if (data.name.includes('floatingLeg')) {
				if (data.name.includes('spread') || data.name.includes('endOfMonth')) {
					taskData['floatingLeg'][data.name.substring(floatingString.length, data.name.length)] = data.name.includes('endOfMonth') ? data.value === 'true' : parseFloat(data.value)
				} else {
					taskData['floatingLeg'][data.name.substring(floatingString.length, data.name.length)] = data.value
				}
			} else if (data.name.includes('forecastCurve') && data.value !== '') {
				var forecastval = []
				forecastval.push(data.value)
				forecastval.forEach((forecastValue) => {
					if (jsonData[forecastValue]) data.value = JSON.stringify(jsonData[forecastValue])
				})
				isJSONObject(data.value, 'floatingLegForecastCurve')
			} else if (data.name.includes('discountCurve') && data.value !== '') {
				var discval = []
				discval.push(data.value)
				discval.forEach((discountValue) => {
					if (jsonData[discountValue]) data.value = JSON.stringify(jsonData[discountValue])
				})
				isJSONObject(data.value, 'discountCurve')
			} else if (data.name.includes('yieldData')) {
				data.value = JSON.stringify(yieldData)
				isJSONObject(data.value, 'yieldData')
			} else {
				if (data.name === 'notional') {
					taskData[data.name] = parseInt(data.value)
				} else {
					taskData[data.name] = data.value
				}
			}
		})

		let client = new rhoova.RhoovaClient({ apiKey: apiKey, apiSecret: apiSecret })

		client
			.createTask({ data: taskData, calculationType: rhoova.CalculationType.IRS, waitResult: true })
			.then((result) => {
				document.getElementById('taskBody').innerHTML = ''
				document.getElementById('taskPropertiesBody').innerHTML = ''
				document.getElementById('loadingIcon').style.display = 'none'
				if (result.error) {
					document.getElementById('taskResult').style.display = 'none'
					document.getElementById('errorMessage').innerHTML = ''
					document.getElementById('errorResult').style.display = 'block'
					document.getElementById('errorMessage').innerHTML = JSON.stringify(result.error)
				} else {
					document.getElementById('loadingIcon').style.display = 'none'
					$.each(JSON.parse(result.result).data, function (index, value) {
						let tBody = '<tr><td>' + value.accrualEnd + '</td><td>' + value.accrualStart + '</td><td>' + value.cashflow + '</td>' + '<td>' + value.cashflowPv + '</td><td>' + value.currency + '</td><td>' + value.discountFactor + '</td>' + '<td>' + value.fixingDate + '</td><td>' + value.instrument + '</td><td>' + value.leg + '</td>' + '<td>' + value.notional + '</td><td>' + value.payOrReceive + '</td><td>' + value.rate + '</td>' + '<td>' + value.spread + '</td><td>' + value.termToMatByDay + '</td><td>' + value.termToMatByYear + '</td>' + '<td>' + value.zeroRate + '</td></tr>'
						$('#taskBody').append(tBody)
						document.getElementById('taskResult').style.display = 'block'
						document.getElementById('taskPropertiesResult').style.display = 'block'
						document.getElementById('errorResult').style.display = 'none'
					})
					let resultData = JSON.parse(result.result)
					var cells = document.getElementById('taskPropertiesTable')
					let tPropertiesBody = '<td>' + resultData.pv + '</td><td>' + resultData.fixedLegPv + '</td><td>' + resultData.floatingLegPv + '</td>' + '<td>' + resultData.PV01 + '</td><td>' + resultData.DV01 + '</td><td>' + resultData.fairRate + '</td>' + '<td>' + resultData.fairSpread + '</td><td>' + resultData.spread + '</td><td>' + resultData.impliedQuote + '</td>'
					$('#taskPropertiesBody').append(tPropertiesBody)
				}
			})
			.catch((error) => {
				document.getElementById('loadingIcon').style.display = 'none'
				document.getElementById('taskResult').style.display = 'none'
				document.getElementById('errorMessage').innerHTML = ''
				document.getElementById('errorResult').style.display = 'block'
				document.getElementById('errorMessage').innerHTML = JSON.stringify(error)
				console.log(error)
			})

		yieldcurveData['valuationDate'] = taskData.valuationDate
		yieldcurveData['yieldData'] = taskData.yieldData
		yieldcurveData['yieldCurve'] = taskData.discountCurve

		client
			.createTask({ data: yieldcurveData, calculationType: rhoova.CalculationType.YIELD_CURVE, waitResult: true })
			.then((result) => {
				let resultData = JSON.parse(result.result)
				let yValues = []
				let xValues = []
				resultData.zeroRates.forEach((data) => {
					yValues.push(100 * data.rate)
					xValues.push(data.date)
				})
				let kanvas = document.getElementById('line-chart')
				let grafik = new Chart(kanvas, {
					type: 'line',
					data: {
						labels: xValues,
						datasets: [
							{
								label: 'Zero Rates',
								data: yValues,
								borderColor: ['rgba(255, 100, 10, 120)'],
								fill: false,
								borderWidth: 1
							}
						]
					},
					options: {
						scales: {
							xAxes: [
								{
									ticks: {
										fontColor: '#CCC' // this here
									}
								}
							],
							yAxes: [
								{
									ticks: {
										fontColor: '#CCC' // this here
									}
								}
							]
						}
					}
				})
			})
			.catch((error) => {
				console.log(error)
			})
	})
}

function isJSONObject(data, label) {
	try {
		JSON.parse(data)
		if (document.activeElement.id === 'randomizeAndSubmitIrs' && label === 'yieldData') {
			taskData[label] = randomizeData(JSON.parse(data))
		} else if (document.activeElement.id === 'submitIrs' && label === 'yieldData') {
			taskData[label] = JSON.parse(data)
		} else {
			taskData[label] = JSON.parse(data)
		}
	} catch (e) {
		document.getElementById('loadingIcon').style.display = 'none'
		document.getElementById('taskResult').style.display = 'none'
		document.getElementById('errorMessage').innerHTML = ''
		document.getElementById('errorResult').style.display = 'block'
		document.getElementById('errorMessage').innerHTML = 'Invalid ' + label + ' object'
		throw new Error(e)
	}
}

function randomizeData(data) {
	data.forEach((item, index) => {
		item.value = Math.floor(Math.random() * item.value + 0.01 - item.value - 0.01) * 0.0025
		data[index] = item
	})

	return data
}

document.body.appendChild(createTaskResult())
