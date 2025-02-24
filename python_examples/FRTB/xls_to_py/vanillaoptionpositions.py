def option_position_trade(position,wb):
    p_type=list(wb[wb["trade_code"]==position]["type"])[0]
    optionDefinition={}
    optionDefinition["underlying"]=list(wb[wb["trade_code"]==position]["underlying"])[0]
    optionDefinition["currency"]=list(wb[wb["trade_code"]==position]["currency"])[0]
    optionDefinition["callPut"]=list(wb[wb["trade_code"]==position]["callPut"])[0]
    optionDefinition["exerciseType"]=list(wb[wb["trade_code"]==position]["exerciseType"])[0]
    optionDefinition["strike"]=list(wb[wb["trade_code"]==position]["strike"])[0]
    optionDefinition["calendar"]=list(wb[wb["trade_code"]==position]["calendar"])[0]
    optionDefinition["dayCounter"]=list(wb[wb["trade_code"]==position]["dayCounter"])[0]
    optionDefinition["optionStartDate"]=list(wb[wb["trade_code"]==position]["optionStartDate"])[0].strftime("%Y-%m-%d")
    optionDefinition["optionEndDate"]=list(wb[wb["trade_code"]==position]["optionEndDate"])[0].strftime("%Y-%m-%d")
    optionDefinition["businessDayConvention"]="ModifiedFollowing"
    optionDefinition["contractSize"]=1
    optionDefinition["spotAdjustment"]=1
    optionDefinition["processType"]="GeneralizedBS"
    optionDefinition["timeSteps"]=800
    optionDefinition["timeGrid"]=10
    optionDefinition["method"]="Analytic"
    optionDefinition["interestRate"]=list(wb[wb["trade_code"]==position]["ir_curve"])[0]
    optionDefinition["riskFreeRate"]=list(wb[wb["trade_code"]==position]["rf_curve"])[0]
    optionDefinition["type"]="VanillaOptionDefinition"
    optionDefinition["calculator"]="vanilla_option"
    optionDefinition["maturityDate"]=list(wb[wb["trade_code"]==position]["maturityDate"])[0].strftime("%Y-%m-%d")
    optionDefinition["strike"]=list(wb[wb["trade_code"]==position]["strike"])[0]
    optionDefinition["underlyingPrice"]=7.5109
    result=optionDefinition 
    return result