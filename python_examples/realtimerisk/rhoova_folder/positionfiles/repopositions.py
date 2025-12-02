from rhoova_folder.inter_func import safe_strftime,extract_field2
from rhoova_folder.positionfiles import bondpositions
import pandas as pd 
from openpyxl import load_workbook
import os
confdir = os.path.normpath(os.getcwd())
def repo_position_trade(position,wb):
    p_type=list(wb[wb["trade_code"]==position]["type"])[0]
    repoDefinition={}
    repoDefinition["type"]="repoDefinition"
    repoDefinition["repoType"]="RRepo"
    repoDefinition["calculator"]="repo"
    repoDefinition["settlementMoney"] = extract_field2(wb,position,"settlementMoney")
    repoDefinition["termMoney"] = extract_field2(wb,position,"termMoney")
    repoDefinition["repoSettlementDate"] = safe_strftime(extract_field2(wb,position,"repoSettlementDate")) 
    repoDefinition["repoDeliveryDate"] = safe_strftime(extract_field2(wb,position,"repoDeliveryDate"))
    repoDefinition["repoType"] = extract_field2(wb,position,"repoType")
    repoDefinition["currency"] = extract_field2(wb,position,"currency")
    repoDefinition["dayCounter"] = extract_field2(wb,position,"dayCounter")
    repoDefinition["notional"] = extract_field2(wb,position,"notional")
    repoDefinition["marginOrHaircut"] =  extract_field2(wb,position,"marginOrHaircut")
    repoDefinition["marginOrHaircutRate"] = extract_field2(wb,position,"marginOrHaircutRate")
    repoDefinition["dirtyPrice"] = extract_field2(wb,position,"dirtyPrice")
    repoDefinition["exdividend"] =extract_field2(wb,position,"exdividend")
    repoDefinition["repoRate"] =extract_field2(wb,position,"repoRate")
    #print(repoDefinition["repoRate"])
    collateral_file=confdir+"/rhoova_folder/positionsdetail/bondsdefinition.xlsx"
    wb_col = pd.read_excel(collateral_file)
    collateral_tmp=bondpositions.bond_position_trade(extract_field2(wb,position,"collateral"),wb_col)
    #collateral_tmp["discountCurve"]=position.get("discountCurve")
    #trades[position.get("type")]=position
    collateral={}
    collateral[collateral_tmp.get("type")]=collateral_tmp
    collateral["settlementDate"]=safe_strftime(extract_field2(wb,position,"repoSettlementDate"))
    collateral["discountCurve"]=collateral_tmp.get("discountCurve")
    repoDefinition["collateral"]=collateral
    return repoDefinition
