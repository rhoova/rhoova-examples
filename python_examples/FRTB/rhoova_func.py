###################################################################################################
                                                                                                  #
from rhoova.Client import *                                                                       #   
#Register and get api key from https://app.rhoova.com/ for ClientConfig("api key", "api secret")  #
config = ClientConfig("", "")                #
api = Api(config)                                                                                 # 
                                                                                                  #
###################################################################################################


def get_result(riskdata):
    try:
        res = api.createTask(CalculationType.PORTFOLIO, riskdata, True)
        if(res["result"]):
            result=json.loads(res["result"])
        else:
            print(res["result"])
    except RhoovaError as e:
        e.printPretty()
    return result  