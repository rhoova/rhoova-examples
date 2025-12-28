def create_irs_task(trade,position):
        trades={}
        trades["trade_id"]=trade.trade_id
        trades["settlementDate"]=trade.settlementDate.strftime("%Y-%m-%d")
        trades["notional"]=trade.notional
        trades["calculation_type"]=position.get("calculator")
        trades["discountCurve"]=position.get("discountCurve")
        trades["floatingLegForecastCurve"]=position.get("floatingLegForecastCurve")
        trades["fixedLeg"]=position.get("fixedleg")
        if trade.buysell=="Buy":
            trades["fixedLeg"]["payOrReceive"]="Receive"
        elif trade.buysell=="Sell":
            trades["fixedLeg"]["payOrReceive"]="Pay"    
        trades["floatingLeg"]=position.get("floatingleg")
        trades["startDate"]=position.get("startDate")
        trades["maturityDate"]=position.get("maturityDate")
        trades["currency"]=position.get("currency")
        return trades  