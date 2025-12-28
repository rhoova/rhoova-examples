def create_bond_task(trade,position):
        trades={}
        trades["trade_id"]=trade.trade_id
        trades["settlementDate"]=trade.settlementDate.strftime("%Y-%m-%d")
        trades["notional"]=trade.notional
        trades["buySell"]=trade.buysell
        trades["calculation_type"]=position.get("calculator")
        trades["discountCurve"]=position.get("discountCurve")
        trades[position.get("type")]=position
        return trades