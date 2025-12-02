import tradefiles
from rhoova_folder.positionfiles import bondpositions,irspositions,forwardpositions,swappositions,vanillaoptionpositions,repopositions,depopositions
from rhoova_folder.taskfiles import bond_task, repo_task,depo_task
from rhoova_folder.rhoova_func import get_portfolio_result

from rhoova_folder.Constants import *


import warnings
warnings.filterwarnings("ignore")



def get_trade_spec(trade_list):
    position_in_files= tradefiles.findFiles(strings=list(set(trade_list)), dir=position_directory + "/rhoova_folder/positionsdetail/", subDirs=True, fileContent=True, fileExtensions=False)
    trades_spec={}
    for key,values in position_in_files.items():
        #wb = pd.read_excel(values) 
        wb = pd.read_excel(values)
        if "bondsdefinition" in values:
            trades_spec[key]=bondpositions.bond_position_trade(key,wb)
        elif  "irsdefinition" in values: 
            trades_spec[key]=irspositions.irs_position_trade(key,wb)
        elif  "forwarddefinition" in values: 
            trades_spec[key]=forwardpositions.forward_position_trade(key,wb)
        elif  "swapdefinition" in values: 
            trades_spec[key]=swappositions.swap_position_trade(key,wb)
        elif  "vanillaoptiondefinition" in values: 
            trades_spec[key]=vanillaoptionpositions.option_position_trade(key,wb)
        elif  "repodefinition" in values: 
            trades_spec[key]=repopositions.repo_position_trade(key,wb)
        elif  "depodefinition" in values: 
            trades_spec[key]=depopositions.depo_position_trade(key,wb)
    return trades_spec  
        
def loadportfolio(valuationdate,valuationcurrency,method):
    
        trades_file=[]
        for index,row in positionslist.iterrows():
            trades_file.append(row.isin_code)

        trade_def=get_trade_spec(list(set(trades_file)))
        trades_list=[]
        trades={}
        for index,row in positionslist.iterrows():
            position=trade_def.get(row.isin_code)
            if position.get("type")=="fixedRateBondDefinition":  
                trades=bond_task.create_bond_task(row,position)
                trades_list.append(trades)
            elif position.get("type")=="floatingBondDefinition":  
                trades=bond_task.create_bond_task(row,position)
                trades_list.append(trades) 
            elif position.get("type")=="tlRefIndexBondDefinition":  
                trades=bond_task.create_bond_task(row,position)
                trades_list.append(trades)     
            elif position.get("type")=="repoDefinition":  
                trades=repo_task.create_repo_task(row,position)
                trades_list.append(trades) 
            elif position.get("type")=="depositDefinition":  
                trades=depo_task.create_depo_task(row,position)
                trades_list.append(trades) 
            #elif position.get("type")=="IRSDefinition":
            #    trades=irs_task.create_irs_task(row,position)
            #    trades_list.append(trades)       
            #elif position.get("type")=="FXForwardDefinition":
            #    trades=forward_task.create_forward_task(row,position)
            #    trades_list.append(trades)         
            #elif position.get("type")=="FXSwapDefinition":
            #    trades=swap_task.create_swap_task(row,position)
            #    trades_list.append(trades)   
            #if position.get("type")=="VanillaOptionDefinition":
            #    trades=vanillaoption_task.create_vanilaoption_task(row,position)
            #    trades_list.append(trades)
        #print(trades_list)
        riskdata = {
          "id": "PORTFOLIO1",
          "name": "PORTFOLIO 1",
          "method": method,
          "forRisk": False,
          "valuationDate": valuationdate,
          "valuationCurrency":valuationcurrency,
          "tasks": trades_list,
          "curves": [TRYOIS],
          "yieldData": yielddata.to_dict('records'),
          "marketData":marketdata.to_dict('records'),
          "volatilityData":voldata.to_dict('records'),

        }

        #result=get_portfolio_result(riskdata)

        #return pd.DataFrame(result.get("cashflows"))   
        return riskdata
    
def get_rhoova_cashflows(riskdata):
    result=get_portfolio_result(riskdata)
    return pd.DataFrame(result.get("cashflows"))   
    
def get_rhoova_pv(riskdata,yielddata=None):
    #print(yielddata)
    #riskdata["yieldData"]=yielddata.to_dict('records')
    #print(riskdata)
    result=get_portfolio_result(riskdata)
    return result.get("total_present_value")