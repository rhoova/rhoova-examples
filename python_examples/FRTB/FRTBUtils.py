import abc
import numpy as np
import datetime as dt
import pandas as pd

from Constants import *
from positions import loadpositions
from rhoova_func import *
from frtb_func import filter_girr_products

import warnings
warnings.filterwarnings('ignore')


class FRTBInit(object):
    def __init__(self,reportingdate,reportingcurrency):
        self.reportingdate = reportingdate    
        self.reportingcurrency = reportingcurrency    
        self.timebuckets=["0D","1D","3M","6M","1Y","2Y","3Y","4Y","5Y",
                          "6Y","7Y","8Y","9Y","10Y","15Y","20Y","25Y",
                          "30Y","40Y","50Y"]
        self._correlationLevels = ['Low', 'Medium', 'High']
        self._gamma_coefficients = {"Medium": 0.5, "Low": 0.375, "High": 0.625}
        
       
    def prepareData(self):
        trades=loadpositions()
        filtered_trades = filter_girr_products(trades)
        return filtered_trades

    def getResults(self,tasks):
        #tasks=tasks[:3]
        request=rhoova_request
        request["valuationDate"]=self.reportingdate 
        request["valuationCurrency"]=self.reportingcurrency
        request["tasks"]=tasks
        request["timeBucket"]=self.timebuckets
        result= get_result(request)
        #print(result.get("VaR"))
        return result

    def create_gamma_matrix(self,size: int, coeff: float) -> np.ndarray:
        """Generates a gamma correlation matrix of given size."""
        gamma = np.full((size, size), coeff)
        np.fill_diagonal(gamma, 1.0)
        return gamma
    
    

    @abc.abstractmethod
    def calcRiskClassCapital(self, df):
        return {}

    def getIRRiskFactor(self,result):
        return list(result.get("forDV01").keys())
 
    def getCurrencies(self,riskfactor):
        return [rf.split("_")[0] for rf in riskfactor]
    
    def getCorrelations(self):
        #correlations=pd.DataFrame(result.get("riskFactorsCorr"))
        return correlations
  
    def scaleCorrelation(self, level, corr):
        corr_df=pd.DataFrame(corr)
        if level == 'Low':
            newCorr = corr_df.applymap(lambda x : max(x*2 - 1 , 0.75 * x))
        elif level == 'High':
            newCorr = corr_df.applymap(lambda x : min(x*1.25,1))
        else:
            newCorr = corr_df.copy()
        return newCorr
    
    def getBuckets(self,result,riskfactors,currencies):
        ir_riskfactor_lst=[]
        for rf in riskfactors:
            rf_bucket=pd.DataFrame(result.get("forDV01").get(rf))
            rf_bucket["currency"]=rf_bucket["bin"].apply(lambda x: x.split('_')[0])
            ir_riskfactor_lst.append(rf_bucket)
        ir_riskfactor_df=pd.concat(ir_riskfactor_lst)
        
        buckets={}
        for curr in currencies:
            rf_bucket=ir_riskfactor_df[ir_riskfactor_df["currency"]==curr]  
            buckets[curr]=rf_bucket
        return buckets
    
    def calculateSensitivities(self,buckets,riskfactors):
        buckets_dict={}
        bp=1/10000
        for bckt in buckets:
            buckets_tmp=buckets.get(bckt)
            buckets_tmp["RF"] = buckets_tmp["bin"].apply(lambda x: next((p for p in riskfactors if x.startswith(p)), None))
            buckets_tmp["tenors"] = buckets_tmp.apply(lambda row: row["bin"].replace(row["RF"], "").strip(), axis=1)
            buckets_tmp['Sensitivity'] =buckets_tmp['cashflow'] * (pow((1+buckets_tmp['rate']-bp),-1*buckets_tmp['timeToMatByYear'])-pow((1+buckets_tmp['rate']),-1*buckets_tmp['timeToMatByYear']))/bp
            buckets_tmp_gr=buckets_tmp[["Sensitivity","tenors"]].groupby(['tenors']).sum()
            buckets_tmp_gr = buckets_tmp_gr.reindex(list(self.timebuckets))
            buckets_dict[bckt]=buckets_tmp_gr
        return buckets_dict
    
    def applyRiskWeights(self,sensitivities):
        sensitivities_dict={}
        for sn in sensitivities:
            sensitivities_tmp=sensitivities.get(sn)
            regulatoryRW=pd.DataFrame([regulatory_rw.get(sn)]).T
            regulatoryRW.columns=["RiskWeight"]
            sensitivities_tmp=pd.concat([sensitivities_tmp,regulatoryRW],axis=1)
            sensitivities_tmp["WeightedSensitivity"]=sensitivities_tmp["Sensitivity"]*sensitivities_tmp["RiskWeight"]
            sensitivities_dict[sn]=sensitivities_tmp[["WeightedSensitivity"]]
        return sensitivities_dict
    
    def calculateDelta(self,weighted_sensitivities):
        correlations=self.getCorrelations()
        delta_lst=[]
        for ws in weighted_sensitivities:
            weighted_sensitivities_tmp=weighted_sensitivities.get(ws)
            Sb=weighted_sensitivities_tmp.sum()
            for level in self._correlationLevels:
                delta_dict={}
                corr_level=self.scaleCorrelation(level,correlations.get(ws))
                Kb = np.sqrt(np.dot(np.dot(weighted_sensitivities_tmp.T,corr_level),weighted_sensitivities_tmp))
                delta_dict["bucket"]=ws
                delta_dict["level"]=level
                delta_dict["Kb"]=list(Kb)[0][0]   
                delta_dict["Sb"]=list(Sb)[0]
                delta_lst.append(delta_dict)    
        return pd.DataFrame(delta_lst)

    def RiskCapital(self,delta):
        number_of_bucket=len(delta["bucket"].unique())
        capital_dct={}
        for gamma in self._gamma_coefficients:
            gamma_level=delta[delta["level"]==gamma]
            gamma_matrix=self.create_gamma_matrix(number_of_bucket,self._gamma_coefficients[gamma])
            K=gamma_level["Kb"]
            S=gamma_level["Sb"]
            capital=np.sqrt(np.dot(np.dot(S.T,gamma_matrix),S)+np.sum(K ** 2))
            capital_dct[gamma]=capital
            #capital = Sb.T @ gamma_matrix @ Sb + Kb2.sum()
        return capital_dct 
         