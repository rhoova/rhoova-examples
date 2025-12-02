import os
import pandas as pd
import numpy as np
import json


###########################################################
###########################################################
################Yield Curve Parameters#####################

confdir = os.path.normpath(os.getcwd())
configdirectory=confdir+"/rhoova_folder/config"
print(configdirectory)
yieldcurveconfig=configdirectory+"/usd6m.json"
f = open (yieldcurveconfig, "r")
USD6M = json.loads(f.read())

yieldcurveconfig1=configdirectory+"/try6m.json"
f = open (yieldcurveconfig1, "r")
TRY6M = json.loads(f.read())

yieldcurveconfig3=configdirectory+"/tryois.json"
f = open (yieldcurveconfig3, "r")
TRYOIS = json.loads(f.read())

parallelshock=configdirectory+"/parallelshock100bp.json"
f = open (parallelshock, "r")
parallelshock100bp = json.loads(f.read())

parallelshock=configdirectory+"/parallelshockminus100bp.json"
f = open (parallelshock, "r")
parallelshockminus100bp = json.loads(f.read())

parallelshock=configdirectory+"/tradeprotection.json"
f = open (parallelshock, "r")
tradeprotection_ir_shock = json.loads(f.read())

parallelshock=configdirectory+"/localrisk.json"
f = open (parallelshock, "r")
localrisk_ir_shock = json.loads(f.read())



###########################################################
###########################################################
###########################################################

###########################################################
###########################################################
################Load Market Data###########################

directory = os.path.normpath(os.getcwd())
datadirectory=directory+"/rhoova_folder/data/yielddata/yielddata.csv"


yielddata = pd.read_csv(datadirectory)
yielddata = yielddata.replace(np.nan, '', regex=True)

mdirectory = os.path.normpath(os.getcwd() )
mdatadirectory=mdirectory+"/rhoova_folder/data/marketdata/marketdata.csv"

marketdata = pd.read_csv(mdatadirectory)
marketdata = marketdata.replace(np.nan, '', regex=True) 


vdirectory = os.path.normpath(os.getcwd() )
vdatadirectory=directory+"/rhoova_folder/data/volatilitydata/voldata.csv"

voldata = pd.read_csv(vdatadirectory)
voldata = voldata.replace(np.nan, '', regex=True) 

###########################################################
###########################################################
###########################################################

###########################################################
###########################################################
################Load Portfolio#############################

position_directory = os.path.normpath(os.getcwd()  )
fixedincome_def=position_directory+"/rhoova_folder/positionsdetail/bondsdefinition.xlsx"

#bondslist=pd.read_excel(fixedincome_def,engine='openpyxl')

positions=position_directory+"/rhoova_folder/positions.xlsx"
positionslist=pd.read_excel(positions,engine='openpyxl')

###########################################################
###########################################################
###########################################################
