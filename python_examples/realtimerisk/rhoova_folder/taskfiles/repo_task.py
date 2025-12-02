def create_repo_task(trade,position):
        trades={}
        trades["trade_id"]=trade.trade_id
        trades["settlementDate"]=trade.settlementDate.strftime("%Y-%m-%d")
        trades["notional"]=trade.notional
        trades[position.get("type")]=position.get("type")
        trades["calculation_type"]=position.get("calculator")
        trades["settlementMoney"]=position.get("settlementMoney")
        trades["termMoney"]=position.get("termMoney")
        trades["repoSettlementDate"]= position.get("repoSettlementDate")
        trades["repoDeliveryDate"]= position.get("repoDeliveryDate")
        trades["repoType"]=position.get("repoType")
        trades["currency"]=position.get("currency")
        trades["dayCounter"]=position.get("dayCounter")
        trades["marginOrHaircut"]=position.get("marginOrHaircut")
        trades["marginOrHaircutRate"]=position.get("marginOrHaircutRate")
        trades["dirtyPrice"]=position.get("dirtyPrice")
        trades["exdividend"]=position.get("exdividend")
        trades["repoRate"]=position.get("repoRate")
        trades["collateral"]=position.get("collateral")
        return trades
 