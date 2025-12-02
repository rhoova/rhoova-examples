from rhoova_folder.inter_func import safe_strftime,extract_field2

def depo_position_trade(position,wb):
    p_type=list(wb[wb["trade_code"]==position]["type"])[0]
    depoDefinition={}
    depoDefinition["type"]="depositDefinition"
    depoDefinition["calculator"]="deposit"
    depoDefinition["interestRate"] = extract_field2(wb,position,"interestRate")
    depoDefinition["frequency"] = extract_field2(wb,position,"frequency")
    depoDefinition["maturityDate"] = safe_strftime(extract_field2(wb,position,"maturityDate"))  
    depoDefinition["currency"] = extract_field2(wb,position,"currency")
    depoDefinition["dayCounter"] = extract_field2(wb,position,"dayCounter")
    depoDefinition["calendar"] = extract_field2(wb,position,"calendar")
    depoDefinition["businessDayConvention"] =extract_field2(wb,position,"businessDayConvention")
    depoDefinition["maturityDateConvention"] = extract_field2(wb,position,"maturityDateConvention")
    depoDefinition["dateGeneration"] = extract_field2(wb,position,"dateGeneration")
    depoDefinition["endOfMonth"] =extract_field2(wb,position,"endOfMonth")
    return depoDefinition
