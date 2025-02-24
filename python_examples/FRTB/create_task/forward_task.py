import pandas as pd

currencypair=pd.read_excel("/Users/serdar/Desktop/Portfolio/Banking/positionsdetail/currencypair.xlsx")

def create_forward_task(trade,position):
        longlegcurr=position.get("longLeg").get("currency")
        shortlegcurr=position.get("shortLeg").get("currency")
        transact=currencypair[currencypair["currencypair"].isin([longlegcurr+shortlegcurr,shortlegcurr+longlegcurr])]
        curr=list(transact.values)[0][0][:3]
        trades={}
        trades["trade_id"]=trade.trade_id
        trades["settlementDate"]=trade.settlementDate.strftime("%Y-%m-%d")
        #trades["notional"]=trade.notional
        #trades["buySell"]=row.buysell     
        trades["calculation_type"]=position.get("calculator")
        trades["shortLegDiscountCurve"]=position.get("shortLegDiscountCurve")
        trades["longLegDiscountCurve"]=position.get("longLegDiscountCurve")
        trades["shortLeg"]=position.get("shortLeg")
        trades["longLeg"]=position.get("longLeg")
        trades["spotPrice"]=position.get("spotPrice")
        if curr==longlegcurr:
            strike=position.get("strike")
        elif curr==shortlegcurr:
            strike=1/position.get("strike")
        if trade["buysell"]=="Buy":
            trades["longLeg"]["notional"]=trade["notional"]
            trades["shortLeg"]["notional"]=trade["notional"]*strike
        elif  trade["buysell"]=="Sell": 
            trades["shortLeg"]["notional"]=trade["notional"]*strike
            trades["longLeg"]["notional"]=trade["notional"]

        trades["maturityDate"]=position.get("maturityDate")
        return trades  