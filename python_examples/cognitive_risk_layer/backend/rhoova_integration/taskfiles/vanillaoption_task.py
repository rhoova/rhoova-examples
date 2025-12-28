def create_vanilaoption_task(trade,position):
        trades={}
        trades["trade_id"]=trade.trade_id
        trades["settlementDate"]=trade.settlementDate.strftime("%Y-%m-%d")
        trades["notional"]=trade.notional
        trades["calculation_type"]=position.get("calculator")
        trades["maturityDate"]=position.get("maturityDate")
        trades["optionDefinition"]={}
        if trade.buysell=="Buy":
            trades["optionDefinition"]["longShort"]="Long"
        elif trade.buysell=="Sell":
            trades["optionDefinition"]["longShort"]="Short"  
        trades["optionDefinition"]["underlying"]=position.get("underlying") 
        trades["optionDefinition"]["currency"]=position.get("currency") 
        trades["optionDefinition"]["callPut"]=position.get("callPut") 
        trades["optionDefinition"]["exerciseType"]=position.get("exerciseType") 
        trades["optionDefinition"]["strike"]=position.get("strike") 
        trades["optionDefinition"]["calendar"]=position.get("calendar") 
        trades["optionDefinition"]["dayCounter"]=position.get("dayCounter") 
        trades["optionDefinition"]["optionStartDate"]=position.get("optionStartDate") 
        trades["optionDefinition"]["optionEndDate"]=position.get("optionEndDate") 
        trades["optionDefinition"]["businessDayConvention"]=position.get("businessDayConvention") 
        trades["optionDefinition"]["contractSize"]=position.get("contractSize") 
        trades["optionDefinition"]["spotAdjustment"]=position.get("spotAdjustment") 
        trades["optionDefinition"]["processType"]=position.get("processType") 
        trades["optionDefinition"]["method"]=position.get("method") 
        trades["optionDefinition"]["timeSteps"]=position.get("timeSteps") 
        trades["optionDefinition"]["timeGrid"]=position.get("timeGrid") 
        trades["optionDefinition"]["interestRate"]=position.get("interestRate") 
        trades["optionDefinition"]["riskFreeRate"]=position.get("riskFreeRate") 
        trades["optionDefinition"]["underlyingPrice"]=7.3406
        volatility={}
        volatility["bidask"]="mid"
        volatility["delta"]="25Delta"
        volatility["businessDayConvention"]="Following"
        trades["optionDefinition"]["volatility"]=volatility

        #trades[position.get("type")]=position
        return trades