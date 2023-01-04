import sys
from rhoova.Client import *
import json
import pandas as pd
import xlwings as xw
import numpy as np


def irscalculation():
    wb = xw.Book('interestrateswap.xlsm')

    inputsheet = wb.sheets['IRS']
    apikey = inputsheet.range('apikey').value
    apisecret = inputsheet.range('apisecret').value

    config = ClientConfig(apikey, apisecret)
    api = Api(config)

    yielddatasheet = wb.sheets['yielddata']
    selectyielddata = yielddatasheet.used_range.value
    yielddata = pd.DataFrame(selectyielddata[1:], columns=selectyielddata[0])
    yielddata['valuationDate'] = yielddata['valuationDate'].astype(str)
    yielddata['maturityDate'] = yielddata['maturityDate'].astype(str)
    yielddata = yielddata.replace(np.nan, '', regex=True)
    yielddata = yielddata.replace("NaT", '', regex=True)

    yieldcurves = yieldcurvesetup(wb)
    discountCurvedefinition = yieldcurves.get('discountCurvedefinition')
    floatingLegForecastCurvedefinition = yieldcurves.get('floatingLegForecastCurvedefinition')
    inputs = getinputs(wb)
    valuationDate = inputs.get('valuationDate').strftime("%Y-%m-%d")
    maturityDate = inputs.get('maturityDate').strftime("%Y-%m-%d")
    settlementDate = inputs.get('settlementDate').strftime("%Y-%m-%d")
    startDate = inputs.get('startDate').strftime("%Y-%m-%d")
    notional = inputs.get('notional')
    currency = inputs.get('currency')
    fixedRate = inputs.get('fixedRate')
    spread = inputs.get('spread')
    fixedLegdefinition = inputs.get('fixedLegdefinition')
    payorreceive = inputs.get('payOrReceive')
    floatingLegdefinition = inputs.get('floatingLegdefinition')
    irsresult = api.createTask(CalculationType.INTEREST_RATES_SWAP,
                               {
                                   "valuationDate": valuationDate,
                                   "settlementDate": settlementDate,
                                   "maturityDate": maturityDate,
                                   "startDate": startDate,
                                   "currency": currency,
                                   "notional": notional,
                                   "spread": spread,
                                   "fixedRate": fixedRate,
                                   "fixedLeg": fixedLegdefinition,
                                   "floatingLeg": floatingLegdefinition,
                                   "discountCurve": discountCurvedefinition,
                                   "floatingLegForecastCurve": floatingLegForecastCurvedefinition,
                                   "yieldData": yielddata.to_dict('r')
                               }, True)
    printresult(wb, irsresult, payorreceive)


def getinputs(wb):
    inputsheet = wb.sheets['IRS']
    valuationDate = inputsheet.range('valuationDate').value
    maturityDate = inputsheet.range('maturityDate').value
    notional = inputsheet.range('notional').value
    currency = inputsheet.range('currency').value
    settlementDate = inputsheet.range('settlementDate').value
    startDate = inputsheet.range('startDate').value
    receiveleg = inputsheet.range('receiveleg').value

    fixedLegdefinition = {}
    floatingLegdefinition = {}

    if receiveleg == 'Fixed':
        fixedLegdefinition['frequency'] = inputsheet.range('receivelegfreq').value
        fixedLegdefinition['dayCounter'] = inputsheet.range('receivelegdayconvention').value
        fixedLegdefinition['coupon'] = inputsheet.range('receivelegfixedrate').value
        fixedLegdefinition['calendar'] = inputsheet.range('receivelegcalendar').value
        fixedLegdefinition['businessDayConvention'] = inputsheet.range('receivelegbdayconv').value
        fixedLegdefinition['maturityDayConvention'] = inputsheet.range('receivelegmatdayconv').value
        fixedLegdefinition['dateGeneration'] = inputsheet.range('receivelegdategen').value
        fixedLegdefinition['endOfMonth'] = inputsheet.range('receivelegeom').value
        fixedLegdefinition['payorreceive'] = 'Receive'
        floatingLegdefinition['frequency'] = inputsheet.range('paylegfreq').value
        floatingLegdefinition['dayCounter'] = inputsheet.range('paylegdayconvention').value
        floatingLegdefinition['spread'] = inputsheet.range('paylegspread').value
        floatingLegdefinition['calendar'] = inputsheet.range('paylegcalendar').value
        floatingLegdefinition['businessDayConvention'] = inputsheet.range('paylegbdayconv').value
        floatingLegdefinition['maturityDateConvention'] = inputsheet.range('paylegmatdayconv').value
        floatingLegdefinition['dateGeneration'] = inputsheet.range('paylegdategen').value
        floatingLegdefinition['endOfMonth'] = inputsheet.range('paylegeom').value
    elif receiveleg == 'Float':
        floatingLegdefinition['frequency'] = inputsheet.range('receivelegfreq').value
        floatingLegdefinition['dayCounter'] = inputsheet.range('receivelegdayconvention').value
        floatingLegdefinition['calendar'] = inputsheet.range('receivelegcalendar').value
        floatingLegdefinition['businessDayConvention'] = inputsheet.range('receivelegbdayconv').value
        floatingLegdefinition['maturityDateConvention'] = inputsheet.range('receivelegmatdayconv').value
        floatingLegdefinition['dateGeneration'] = inputsheet.range('receivelegdategen').value
        floatingLegdefinition['endOfMonth'] = inputsheet.range('receivelegeom').value
        floatingLegdefinition['spread'] = inputsheet.range('receivelegspread').value
        fixedLegdefinition['frequency'] = inputsheet.range('paylegfreq').value
        fixedLegdefinition['dayCounter'] = inputsheet.range('paylegdayconvention').value
        fixedLegdefinition['calendar'] = inputsheet.range('paylegcalendar').value
        fixedLegdefinition['businessDayConvention'] = inputsheet.range('paylegbdayconv').value
        fixedLegdefinition['maturityDateConvention'] = inputsheet.range('paylegmatdayconv').value
        fixedLegdefinition['dateGeneration'] = inputsheet.range('paylegdategen').value
        fixedLegdefinition['endOfMonth'] = inputsheet.range('paylegeom').value
        fixedLegdefinition['payOrReceive'] = 'Pay'
        fixedLegdefinition['coupon'] = inputsheet.range('paylegfixedrate').value

    inputs = {'valuationDate': valuationDate, 'maturityDate': maturityDate, 'notional': notional, 'currency': currency,
              'settlementDate': settlementDate, 'startDate': startDate,
              'fixedLegdefinition': fixedLegdefinition, 'floatingLegdefinition': floatingLegdefinition}

    # print(inputs)
    return inputs


def printresult(wb, result, payorreceive):
    irsto_json = json.loads(result["result"])
    # cashflow_df = pd.DataFrame(irsto_json.get('data')).set_index('fixingDate')
    cashflow_df = pd.DataFrame(irsto_json.get('data'))
    resultsheet = wb.sheets['IRS']

    resultsheet.range('A25').expand().clear_contents()

    resultsheet.range('npv').value = irsto_json.get('pv')
    resultsheet.range('fairspread').value = irsto_json.get('fairSpread')
    resultsheet.range('impliedquote').value = irsto_json.get('impliedQuote')

    if payorreceive == 'Receive':
        resultsheet.range('receivelegbps').value = irsto_json.get('fixedLegBps')
        resultsheet.range('receivelegnpv').value = irsto_json.get('fixedLegPv')
        resultsheet.range('paylegbps').value = irsto_json.get('floatingLegBps')
        resultsheet.range('paylegnpv').value = irsto_json.get('floatingLegPv')
    elif payorreceive == 'Pay':
        resultsheet.range('receivelegbps').value = irsto_json.get('floatingLegBps')
        resultsheet.range('receivelegnpv').value = irsto_json.get('floatingLegPv')
        resultsheet.range('paylegbps').value = irsto_json.get('fixedLegBps')
        resultsheet.range('paylegnpv').value = irsto_json.get('fixedLegPv')

    resultsheet["A24"].options(pd.DataFrame, header=1, index=True, expand='table').value = cashflow_df


def yieldcurvesetup(wb):
    yieldcurvedef = wb.sheets['yieldcurve']

    discountCurvedefinition = {}
    depo = {}
    fra = {}
    irs = {}

    discountCurvedefinition['period'] = yieldcurvedef.range('fixedlegdiscountcurveperiod').value
    discountCurvedefinition['settlementDays'] = int(yieldcurvedef.range('fixedlegdiscountcurvesettlementday').value)
    discountCurvedefinition['intpMethod'] = yieldcurvedef.range('fixedlegdiscountcurveintpmethod').value
    discountCurvedefinition['currency'] = yieldcurvedef.range('fixedlegdiscountcurvecurrency').value
    discountCurvedefinition['calendar'] = yieldcurvedef.range('fixedlegdiscountcurvecalendar').value
    discountCurvedefinition['dayCounter'] = yieldcurvedef.range('fixedlegdiscountcurvedaycount').value

    depo['businessDayConvention'] = yieldcurvedef.range('fixedlegdiscountcurvedepobdayconv').value
    depo['dayCounter'] = yieldcurvedef.range('fixedlegdiscountcurvedepodaycount').value

    fra['businessDayConvention'] = yieldcurvedef.range('fixedlegdiscountcurvefrabdayconv').value
    fra['dayCounter'] = yieldcurvedef.range('fixedlegdiscountcurvefradaycount').value

    irs['frequency'] = yieldcurvedef.range('fixedlegdiscountcurveirsfreq').value
    irs['businessDayConvention'] = yieldcurvedef.range('fixedlegdiscountcurveirsbdayconv').value
    irs['dayCounter'] = yieldcurvedef.range('fixedlegdiscountcurveirsdaycount').value

    discountCurvedefinition['instruments'] = {"DEPO": depo, 'FRA': fra, 'IRS': irs}

    floatingLegForecastCurvedefinition = {}
    depo = {}
    fra = {}
    irs = {}

    floatingLegForecastCurvedefinition['period'] = yieldcurvedef.range('forecastcurveperiod').value
    floatingLegForecastCurvedefinition['settlementDays'] = int(yieldcurvedef.range('forecastcurvesettlementday').value)
    floatingLegForecastCurvedefinition['intpMethod'] = yieldcurvedef.range('forecastcurveintpmethod').value
    floatingLegForecastCurvedefinition['currency'] = yieldcurvedef.range('forecastcurvecurrency').value
    floatingLegForecastCurvedefinition['calendar'] = yieldcurvedef.range('forecastcurvecalendar').value
    floatingLegForecastCurvedefinition['dayCounter'] = yieldcurvedef.range('forecastcurvedaycount').value

    depo['businessDayConvention'] = yieldcurvedef.range('fixedlegdiscountcurvedepobdayconv').value
    depo['dayCounter'] = yieldcurvedef.range('fixedlegdiscountcurvedepodaycount').value

    fra['businessDayConvention'] = yieldcurvedef.range('fixedlegdiscountcurvefrabdayconv').value
    fra['dayCounter'] = yieldcurvedef.range('fixedlegdiscountcurvefradaycount').value

    irs['frequency'] = yieldcurvedef.range('fixedlegdiscountcurveirsfreq').value
    irs['businessDayConvention'] = yieldcurvedef.range('fixedlegdiscountcurveirsbdayconv').value
    irs['dayCounter'] = yieldcurvedef.range('fixedlegdiscountcurveirsdaycount').value

    floatingLegForecastCurvedefinition['instruments'] = {"DEPO": depo, 'FRA': fra, 'IRS': irs}
    yieldcurves = {'discountCurvedefinition': discountCurvedefinition,
                   'floatingLegForecastCurvedefinition': floatingLegForecastCurvedefinition}
    return yieldcurves



