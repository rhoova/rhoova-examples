def bond_position_trade(position,wb):
    p_type=list(wb[wb["isin_code"]==position]["type"])[0]
    if p_type=="fixedratebond":
        fixedRateBondDefinition={}
        fixedRateBondDefinition["type"]="fixedRateBondDefinition"
        fixedRateBondDefinition["calculator"]="fixed_rate_bond"
        fixedRateBondDefinition["discountCurve"]="TRYZC"
        fixedRateBondDefinition["issueDate"]=list(wb[wb["isin_code"]==position]["issueDate"])[0].strftime("%Y-%m-%d")
        fixedRateBondDefinition["maturityDate"]=list(wb[wb["isin_code"]==position]["maturityDate"])[0].strftime("%Y-%m-%d")
        fixedRateBondDefinition["frequency"]=list(wb[wb["isin_code"]==position]["frequency"])[0]
        fixedRateBondDefinition["coupon"]=list(wb[wb["isin_code"]==position]["coupon"])[0]
        fixedRateBondDefinition["calendar"]=list(wb[wb["isin_code"]==position]["calendar"])[0]
        fixedRateBondDefinition["currency"]=list(wb[wb["isin_code"]==position]["currency"])[0]
        fixedRateBondDefinition["dateGeneration"]="Backward"
        fixedRateBondDefinition["dayCounter"]=list(wb[wb["isin_code"]==position]["dayCounter"])[0]
        fixedRateBondDefinition["businessDayConvention"]="ModifiedFollowing"
        fixedRateBondDefinition["maturityDateConvention"]="ModifiedFollowing"
        fixedRateBondDefinition["redemption"]=100
        fixedRateBondDefinition["endOfMonth"]=True
        result=fixedRateBondDefinition
    elif p_type=="frn":
        frnDefinition={}
        frnDefinition["type"]="floatingBondDefinition"
        frnDefinition["calculator"]="floating_rate_bond"
        frnDefinition["discountCurve"]="TRYZC"
        frnDefinition["issueDate"]=list(wb[wb["isin_code"]==position]["issueDate"])[0].strftime("%Y-%m-%d")
        frnDefinition["maturityDate"]=list(wb[wb["isin_code"]==position]["maturityDate"])[0].strftime("%Y-%m-%d")
        frnDefinition["frequency"]=list(wb[wb["isin_code"]==position]["frequency"])[0]
        frnDefinition["spread"]=list(wb[wb["isin_code"]==position]["spread"])[0]
        frnDefinition["calendar"]=list(wb[wb["isin_code"]==position]["calendar"])[0]
        frnDefinition["currency"]=list(wb[wb["isin_code"]==position]["currency"])[0]
        frnDefinition["dateGeneration"]="Backward"
        frnDefinition["dayCounter"]=list(wb[wb["isin_code"]==position]["dayCounter"])[0]
        frnDefinition["businessDayConvention"]="ModifiedFollowing"
        frnDefinition["maturityDateConvention"]="ModifiedFollowing"
        frnDefinition["redemption"]=100
        frnDefinition["endOfMonth"]=True
        frnDefinition["fixingDate"]=[]
        frnDefinition["fixingRate"]=[]
        result=frnDefinition   
    return result