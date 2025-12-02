from typing import List, Dict

###################################################################################################
                                                                                                  #
from rhoova.Client import *                                                                       #   
#Register and get api key from https://app.rhoova.com/ for ClientConfig("api key", "api secret")  #
config = ClientConfig("gwr5J6VWP_VRV2SW5WqDg", "uldsvIkXREQN69mKzRPqwKH_XZIO7gZ3")                #
api = Api(config)                                                                                 # 
                                                                                                  #
###################################################################################################


def get_portfolio_result(portfoliodata: List[Dict]):
    try:    
        #print( api.createTask(CalculationType.PORTFOLIO, portfoliodata, True))
        res = api.createTask(CalculationType.PORTFOLIO, portfoliodata, True)
        if(res["result"]):
            result=json.loads(res["result"])
        else:
            print(res["result"])
    except RhoovaError as e:
        e.printPretty()
    return result  


