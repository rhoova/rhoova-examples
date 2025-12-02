def forward_position_trade(position,wb):
    p_type=list(wb[wb["trade_code"]==position]["type"])[0]
    forwardDefinition={}
    shortleg={}
    longleg={}
    #shortleg["notional"]=list(wb[wb["trade_code"]==position]["shortLegNotional"])[0]
    shortleg["currency"]=list(wb[wb["trade_code"]==position]["sellLegCurrency"])[0]
    shortleg["dayCounter"]=list(wb[wb["trade_code"]==position]["sellLegdayCounter"])[0]
    shortleg["calendar"]=list(wb[wb["trade_code"]==position]["sellLegcalendar"])[0]
    shortleg["businessDayConvention"]="ModifiedFollowing"
    shortleg["endOfMonth"]=True
    #longleg["notional"]=list(wb[wb["trade_code"]==position]["buyLegNotional"])[0]
    longleg["currency"]=list(wb[wb["trade_code"]==position]["buyLegCurrency"])[0]
    longleg["dayCounter"]=list(wb[wb["trade_code"]==position]["buyLegdayCounter"])[0]
    longleg["calendar"]=list(wb[wb["trade_code"]==position]["buyLegcalendar"])[0]
    longleg["businessDayConvention"]="ModifiedFollowing"
    longleg["endOfMonth"]=True
    forwardDefinition["shortLeg"]=shortleg
    forwardDefinition["longLeg"]=longleg
    forwardDefinition["type"]="FXForwardDefinition"
    forwardDefinition["calculator"]="fx_forward"
    forwardDefinition["maturityDate"]=list(wb[wb["trade_code"]==position]["maturityDate"])[0].strftime("%Y-%m-%d")
    forwardDefinition["shortLegDiscountCurve"]="TRYZC"
    forwardDefinition["longLegDiscountCurve"]="TRYZC"
    forwardDefinition["strike"]=list(wb[wb["trade_code"]==position]["strike"])[0]
    forwardDefinition["spotPrice"]=7.5109
    result=forwardDefinition 
    return result