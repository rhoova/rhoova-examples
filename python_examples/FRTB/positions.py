from Constants import *
import tradefiles
from xls_to_py import bondpositions,irspositions,vanillaoptionpositions
from create_task import bond_task,irs_task,vanillaoption_task


def get_trade_spec(trade_list):
    position_in_files=tradefiles.findFiles(strings=list(set(trade_list)), dir=position_directory+"/FRTB/position_data/",  subDirs=True, fileContent=True, fileExtensions=False)
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
    return trades_spec  


def loadpositions():
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
        elif position.get("type")=="IRSDefinition":
            trades=irs_task.create_irs_task(row,position)
            trades_list.append(trades)       
        elif position.get("type")=="FXForwardDefinition":
            trades=forward_task.create_forward_task(row,position)
            trades_list.append(trades)         
        elif position.get("type")=="FXSwapDefinition":
            trades=swap_task.create_swap_task(row,position)
            trades_list.append(trades)   
        if position.get("type")=="VanillaOptionDefinition":
            trades=vanillaoption_task.create_vanilaoption_task(row,position)
            trades_list.append(trades)  
    return trades_list
    