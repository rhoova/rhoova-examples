import pandas as pd
import os

# --- DİNAMİK DOSYA YOLU (GENERIC PATH FIX) ---
# 1. Bu dosyanın (forward_task.py) nerede olduğunu bul
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Bir üst klasöre çık (rhoova_integration klasörüne)
integration_dir = os.path.dirname(current_dir)

# 3. Hedef dosya yolunu oluştur (OS bağımsız)
target_path = os.path.join(integration_dir, "positionsdetail", "currencypair.xlsx")

# 4. Dosyayı Oku (Hata korumalı)
if os.path.exists(target_path):
    currencypair = pd.read_excel(target_path)
else:
    print(f"⚠️ UYARI: '{target_path}' bulunamadı. Forward hesaplamaları eksik olabilir.")
    currencypair = pd.DataFrame() # Boş dataframe dön ki sistem çökmesin
	
def create_swap_task(trade,position):
        longlegcurr=position.get("longLeg").get("currency")
        shortlegcurr=position.get("shortLeg").get("currency")
        transact=currencypair[currencypair["currencypair"].isin([longlegcurr+shortlegcurr,shortlegcurr+longlegcurr])]
        curr=list(transact.values)[0][0][:3]
        trades={}
        trades["trade_id"]=trade.trade_id
        trades["settlementDate"]=trade.settlementDate.strftime("%Y-%m-%d")
        #trades["notional"]=trade.notional
        #trades["buySell"]=row.buysell     
        trades["calculation_type"]=position.get("calculator")
        trades["shortLegDiscountCurve"]=position.get("shortLegDiscountCurve")
        trades["longLegDiscountCurve"]=position.get("longLegDiscountCurve")
        trades["shortLeg"]=position.get("shortLeg")
        trades["longLeg"]=position.get("longLeg")
        trades["spotPrice"]=position.get("spotPrice")
        if curr==longlegcurr:
            strike=position.get("strike")
        elif curr==shortlegcurr:
            strike=1/position.get("strike")
        if trade["buysell"]=="Buy":
            trades["longLeg"]["notional"]=trade["notional"]
            trades["shortLeg"]["notional"]=trade["notional"]*strike
            trades["longLeg"]["initialNominal"]=trade["notional"]*strike
            trades["shortLeg"]["initialNominal"]=trade["notional"]
        elif  trade["buysell"]=="Sell": 
            trades["shortLeg"]["notional"]=trade["notional"]*strike
            trades["longLeg"]["notional"]=trade["notional"]
            trades["longLeg"]["initialNominal"]=trade["notional"]
            trades["shortLeg"]["initialNominal"]=trade["notional"]*strike
        trades["maturityDate"]=position.get("maturityDate")
        trades["startDate"]=position.get("startDate")
        #trades["longLeg"]["initialNominal"]=10000000
        #trades["shortLeg"]["initialNominal"]=10000000
        return trades  