import os
import pandas as pd
import numpy as np
import json

###########################################################
###########################################################
################Data directories#####################


directory = os.path.normpath(os.getcwd())
datadirectory=directory+"/data/yielddata/yielddata.csv"

yielddata = pd.read_csv(datadirectory)
yielddata = yielddata.replace(np.nan, '', regex=True) 

mdirectory = os.path.normpath(os.getcwd())
mdatadirectory=mdirectory+"/data/marketdata/marketdata.csv"

marketdata = pd.read_csv(mdatadirectory)
marketdata = marketdata.replace(np.nan, '', regex=True) 

vdirectory = os.path.normpath(os.getcwd())
vdatadirectory=directory+"/data/volatilitydata/swaptionvol.csv"

voldata = pd.read_csv(vdatadirectory)
voldata = voldata.replace(np.nan, '', regex=True) 



###########################################################
###########################################################
################Yield Curve Parameters#####################

confdir = os.path.normpath(os.getcwd())
configdirectory=confdir+"/config"

yieldcurveconfig=configdirectory+"/usdirs.json"
f = open (yieldcurveconfig, "r")
USD_IRS = json.loads(f.read())

yieldcurveconfig1=configdirectory+"/tryirs.json"
f = open (yieldcurveconfig1, "r")
TRY_IRS = json.loads(f.read())

yieldcurveconfig2=configdirectory+"/tryois.json"
f = open (yieldcurveconfig2, "r")
TRY_OIS = json.loads(f.read())


yieldcurveconfig3=configdirectory+"/usdois.json"
f = open (yieldcurveconfig3, "r")
USD_OIS = json.loads(f.read())


parallelshock=configdirectory+"/parallelshock50bp.json"
f = open (parallelshock, "r")
parallelshock = json.loads(f.read())

###########################################################
###########################################################
###########################################################


###########################################################
###########################################################
################Load Portfolio#############################

position_directory = os.path.normpath(os.getcwd() + os.sep + os.pardir )
fixedincome_def=position_directory+"/positionsdetail/bondsdefinition.xlsx"

#bondslist=pd.read_excel(fixedincome_def,engine='openpyxl')

positions=position_directory+"/FRTB/positions.xlsx"
positionslist=pd.read_excel(positions,engine='openpyxl')

###########################################################
###########################################################
###########################################################

rhoova_request={}

rhoova_request["valuationDate"]=None
rhoova_request["valuationCurrency"]=None
rhoova_request["timeBucket"]=None
rhoova_request["tasks"]=None

rhoova_request["id"]="FRTBDemo1"
rhoova_request["name"]="FRTBDemo"
rhoova_request["method"]="VaR"
rhoova_request["riskMethod"]="DELTANORMAL"
rhoova_request["horizon"]=252
rhoova_request["confidenceInterval"]=0.99
rhoova_request["returnType"]="NONE"
rhoova_request["trend"]=False
rhoova_request["calendar"]="Turkey"
rhoova_request["fillNa"]="BACKWARD"
rhoova_request["maxFillNaDays"]=5
rhoova_request["curves"]=[TRY_IRS,TRY_OIS,USD_IRS,USD_OIS]

rhoova_request["yieldData"]= yielddata.to_dict('records')
rhoova_request["marketData"]= marketdata.to_dict('records')
rhoova_request["volatilityData"]= voldata.to_dict('records')



###########################################################
###########################################################
################Regulatory RiskWeight#############################



regulatory_rw={"TRY":{"0D":0.000065,"1D":0.000065,"3M":0.000097,
               "6M":0.000079,"1Y":0.000091,"2Y":0.000103,
               "3Y":0.000148,"4Y":0.000248,"5Y":0.000314,"6Y":0.000425,
               "7Y":0.000486,"8Y":0.000565,"9Y":0.000619,"10Y":0.000612,
               "15Y":0.000795,"20Y":0.000879,"25Y":0.000922,
               "30Y":0.000891,"40Y":0.001186,"50Y":0.001499},
              "USD":{"0D":0.000065,"1D":0.000065,"3M":0.000097,
               "6M":0.000079,"1Y":0.000091,"2Y":0.000103,
               "3Y":0.000148,"4Y":0.000248,"5Y":0.000314,"6Y":0.000425,
               "7Y":0.000486,"8Y":0.000565,"9Y":0.000619,"10Y":0.000612,
               "15Y":0.000795,"20Y":0.000879,"25Y":0.000922,
               "30Y":0.000891,"40Y":0.001186,"50Y":0.001499}
              }


###########################################################
###########################################################
################Correlations#############################

correlations_dir = os.path.normpath(os.getcwd())
correlations_file=correlations_dir+"/correlations.json"
f = open (correlations_file, "r")
correlations = json.loads(f.read())
