from rhoova_folder.inter_func import safe_strftime,extract_field
def bond_position_trade(position,wb):
    match = wb[wb["isin_code"] == position]
    if match.empty:
        raise ValueError(f"No bond found with ISIN {position}")
    p_type=list(wb[wb["isin_code"]==position]["type"])[0]
    #print(p_type)
    if p_type=="fixedratebond":
        fixedRateBondDefinition={}
        fixedRateBondDefinition["type"]="fixedRateBondDefinition"
        fixedRateBondDefinition["calculator"]="fixed_rate_bond"
        fixedRateBondDefinition["discountCurve"]=extract_field(wb, position, "discountcurve")
        fixedRateBondDefinition["issueDate"] = safe_strftime(extract_field(wb, position, "issueDate")) 
        fixedRateBondDefinition["maturityDate"] = safe_strftime(extract_field(wb, position, "maturityDate"))
        fixedRateBondDefinition["frequency"]=extract_field(wb, position, "frequency")
        fixedRateBondDefinition["coupon"]=extract_field(wb, position, "coupon")
        fixedRateBondDefinition["calendar"]=extract_field(wb, position, "calendar")
        fixedRateBondDefinition["currency"]=extract_field(wb, position, "currency")
        fixedRateBondDefinition["dateGeneration"]="Backward"
        fixedRateBondDefinition["dayCounter"]=extract_field(wb, position, "dayCounter")
        fixedRateBondDefinition["businessDayConvention"]="ModifiedFollowing"
        fixedRateBondDefinition["maturityDateConvention"]="ModifiedFollowing"
        fixedRateBondDefinition["redemption"]=100
        fixedRateBondDefinition["endOfMonth"]=True
        result=fixedRateBondDefinition
    elif p_type=="frn":
        frnDefinition={}
        frnDefinition["type"]="floatingBondDefinition"
        frnDefinition["calculator"]="floating_rate_bond"
        frnDefinition["discountCurve"]=extract_field(wb, position, "discountcurve")
        frnDefinition["issueDate"]=safe_strftime(extract_field(wb, position, "issueDate")) 
        frnDefinition["maturityDate"]=safe_strftime(extract_field(wb, position, "maturityDate"))
        frnDefinition["frequency"]=extract_field(wb, position, "frequency")
        frnDefinition["spread"]=extract_field(wb, position, "spread")
        frnDefinition["calendar"]=extract_field(wb, position, "calendar")
        frnDefinition["currency"]=extract_field(wb, position, "currency")
        frnDefinition["dateGeneration"]="Backward"
        frnDefinition["dayCounter"]=extract_field(wb, position, "dayCounter")
        frnDefinition["businessDayConvention"]="ModifiedFollowing"
        frnDefinition["maturityDateConvention"]="ModifiedFollowing"
        frnDefinition["redemption"]=100
        frnDefinition["endOfMonth"]=True
        frnDefinition["fixingDate"]=[]
        frnDefinition["fixingRate"]=[]
        result=frnDefinition   
    elif p_type == "tlrefindex":
        tlRefIndexBond={}
        tlRefIndexBond["type"]="tlRefIndexBondDefinition"
        tlRefIndexBond["calculator"]="tl_ref_index_bond"
        tlRefIndexBond["discountCurve"]=extract_field(wb, position, "discountcurve")
        tlRefIndexBond["spread"]=extract_field(wb, position, "spread")
        tlRefIndexBond["frequency"]=extract_field(wb, position, "frequency")
        tlRefIndexBond["maturityDate"]=safe_strftime(extract_field(wb, position, "maturityDate"))
        tlRefIndexBond["issueDate"]=safe_strftime(extract_field(wb, position, "issueDate"))
        tlRefIndexBond["businessDayConvention"]="ModifiedFollowing"
        tlRefIndexBond["maturityDateConvention"]="ModifiedFollowing"
        tlRefIndexBond["dateGeneration"]="Backward"
        tlRefIndexBond["calendar"]=extract_field(wb, position, "calendar")
        tlRefIndexBond["dayCounter"]= extract_field(wb, position, "dayCounter")
        tlRefIndexBond["endOfMonth"]=True
        tlRefIndexBond["currency"]=extract_field(wb, position, "currency")
        tlRefIndexBond["redemption"]=100
        tlRefIndexBond["fixingDate"]=["2025-02-13"]
        #tlRefIndexBond["fixingDate"]=extract_field(wb, position, "fixingDate")
        tlRefIndexBond["fixingRate"]=[extract_field(wb, position, "fixingRate")]
        result=tlRefIndexBond   
    else:
        raise ValueError(f"Unsupported bond type: {p_type}")
    return result