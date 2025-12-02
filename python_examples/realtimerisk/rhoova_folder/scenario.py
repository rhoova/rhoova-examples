import numpy as np
import pandas as pd
import json
from rhoova_folder.Constants import *
from rhoova_folder.portfolio import get_rhoova_cashflows


class ScenarioAnalyzer:
    """
    A framework for deterministic scenario testing of asset and liability cash flows.

    Attributes:
        base_cashflows (pd.DataFrame): A dataframe containing base case asset and liability cash flows.
        scenarios (dict): Predefined deterministic scenarios for testing.
    """
    def __init__(self,portfolio: dict):
        """
        Initializes the ScenarioTester with base cash flows.
        
        Args:
            base_cashflows (pd.DataFrame): Dataframe containing base cash flows for assets and liabilities.
        """
        self.portfolio = portfolio
        self.history = []  # Store scenario history
        

        self.scenarios = {
            #"Base Case": {},
            "Interest Rate +100bps": {"interest_rate_shock":parallelshock100bp},
            "Interest Rate -100bps": {"interest_rate_shock":parallelshockminus100bp},
            #"Equity Market Drop -20%": {"equity_shock": -0.20},
            #"Lapse Rate +10%": {"lapse_shock": 0.10},
            #"Mortality Shock +10%": {"mortality_shock": 0.10},
            "Macro Recession": {"interest_rate_shock":-0.05*10000, 
                                "fx_shock":30, 
                                "lapse_shock": 0.15, 
                                "inflation_shock": 0.03},
            "Trade Protectionism": {"interest_rate_shock":tradeprotection_ir_shock, 
                                    "equity_shock": -0.10, 
                                    "inflation_shock": 0.02, 
                                    "fx_shock": -10},
            "Local Risk": {"interest_rate_shock":localrisk_ir_shock, 
                                    "equity_shock": -0.10, 
                                    "inflation_shock": 0.02, 
                                    "fx_shock": 0}
        }
        
    
    def list_available_scenarios(self):
        print("Available predefined scenarios:")
        for scenario in self.scenarios:
            print(f"- {scenario}")
        print("You can type the name of one to use, or ask to generate a new scenario.")
        
        
    def apply_curves(self,scenario):
        # Tüm eğrilere applyShock ekle
        curves=[]
        for curve in self.portfolio["curves"]:
            curve['applyShock'] = scenario
        curves.append(curve)
        return curves

    def apply_defined_scenario(self, scenario_name: str) -> pd.DataFrame:
        """
        Applies a specified scenario to the base cash flows.
        
        Args:
            scenario_name (str): The name of the scenario to apply.
        
        Returns:
            pd.DataFrame: Adjusted cash flows under the given scenario.
        """
        if scenario_name not in self.scenarios:
            raise ValueError("Scenario not found")
        
        scenario = self.scenarios[scenario_name]
        self.cashflows=get_rhoova_cashflows(self.portfolio)
        #adjusted_cashflows = self.base_cashflows.copy()
        if "interest_rate_shock" in scenario:
            self.portfolio["curves"]=self.apply_curves(scenario.get("interest_rate_shock"))
            adjusted_cashflows=get_rhoova_cashflows(self.portfolio)
        
        return adjusted_cashflows

    def apply_shock(self, scenario_name: dict) -> pd.DataFrame:
        """
        Applies shock values to the base cash flows based on the given shock data.
        
        Args:
            shock_data (dict): A dictionary containing shock values.
        
        Returns:
            pd.DataFrame: Adjusted cash flows under the given shocks.
        """
        #adjusted_cashflows = self.base_cashflows.copy()
        scenario = self.scenarios[scenario_name]
        if "interest_rate_shock" in scenario:
            print("interest_rate_shock:",str(scenario.get("interest_rate_shock").get("shockValues")[0].get("shockValue"))+"bps")
            self.cashflows=get_rhoova_cashflows(self.portfolio)
            self.portfolio["curves"]=self.apply_curves(scenario.get("interest_rate_shock"))
            scenario_cashflows=get_rhoova_cashflows(self.portfolio)
            self.cashflows["after_shock_pv_ir_shock"]=scenario_cashflows['cashflowPv']
            adjusted_cashflows=self.cashflows.copy()
        #if "equity_shock" in scenario:
        #    adjusted_cashflows["after_shock_pv_eq_shock"]=adjusted_cashflows['cashflowPv']
        
        if "fx_shock" in scenario:
            print("fx_shock:",str(scenario.get("fx_shock"))+"%")

            adjusted_cashflows["after_shock_pv_fx_shock"] = adjusted_cashflows['cashflowPv']*(1 + float(scenario["fx_shock"])/100)
        
        if not 'after_shock_pv_fx_shock' in adjusted_cashflows.columns:
            adjusted_cashflows["after_shock_pv_fx_shock"]=adjusted_cashflows['cashflowPv']
  
        if not 'after_shock_pv_ir_shock' in adjusted_cashflows.columns:
            adjusted_cashflows["after_shock_pv_ir_shock"]=adjusted_cashflows['cashflowPv']
            
        
        adjusted_cashflows=adjusted_cashflows.groupby(["position","instrument"])[["cashflowPv","after_shock_pv_ir_shock","after_shock_pv_fx_shock"]].sum()
        adjusted_cashflows["total_shock"]=(adjusted_cashflows["after_shock_pv_ir_shock"]-adjusted_cashflows["cashflowPv"])+adjusted_cashflows["after_shock_pv_fx_shock"]-adjusted_cashflows["cashflowPv"]
        self.history.append(scenario) 
        return adjusted_cashflows
    
    def run_all_defined_scenarios(self) -> dict:
        """
        Runs all predefined scenarios and stores the results.
        
        Returns:
            dict: A dictionary where keys are scenario names and values are adjusted cash flow dataframes.
        """
        results = {}
        for scenario in self.scenarios:
            #print(scenario)
            results[scenario] = self.apply_defined_scenario(scenario)
        return results