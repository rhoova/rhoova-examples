def create_depo_task(trade,position):
        trades={}
        trades["trade_id"]=trade.trade_id
        trades["capital"]=trade.notional
        trades["interestRate"]=position.get("interestRate")
        trades["frequency"]=position.get("frequency")
        trades["maturityDate"]=position.get("maturityDate")
        trades["calculation_type"]=position.get("calculator")
        trades["discountCurve"]="TRYOIS"
        depositdefinition={}
        depositdefinition["currency"]=position.get("currency")
        depositdefinition["dayCounter"]=position.get("dayCounter")
        depositdefinition["calendar"]=position.get("calendar")
        depositdefinition["businessDayConvention"]=position.get("businessDayConvention")
        depositdefinition["maturityDateConvention"]=position.get("maturityDateConvention")
        depositdefinition["dateGeneration"]=position.get("dateGeneration")
        depositdefinition["endOfMonth"]=position.get("endOfMonth")
        trades[position.get("type")]=depositdefinition
        return trades