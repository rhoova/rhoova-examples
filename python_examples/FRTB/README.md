<h1 align="center">
  <br>
  <a href="https://rhoova.com/"><img src="https://avatars.githubusercontent.com/u/95615194?s=400&u=66884adf6c6497aab9087d0dfdd2035fe7bf75b3&v=4" alt="Rhoova" width="200"></a>
  <br>
  <br>
  Rhoova
</h1>

<h3 align="center">Pricing and Risk Management Solutions</h3>
<h6 align="center">Risk and Pricing of Balance Sheet and Off-Balance Sheet Items</h6>

<p align="center">
  <a target="_blank" href="https://rhoova.com/">Website</a> •
  <a target="_blank" href="https://app.rhoova.com">Application</a> •
  <a target="_blank" href="https://app.rhoova.com/docs">Docs</a> •
  <a target="_blank" href="https://pypi.org/project/rhoova/">Python Client</a> •
  <a target="_blank" href="#rhoova-examples">Examples</a>
</p>

## FRTB Examples

## Vision and Overview

We aim to foster a collaborative community of Market Risk and CVA professionals by providing a free, open-source implementation of Basel III Standardised Approach Market Risk Capital rules (FRTB). Our calculators also cover the Basel III CVA Standardised and Basic Approaches. Designed for flexibility, they can be adapted to accommodate various regional regulatory requirements.

In addition to these core calculators, we offer tools for regulatory reporting, in-depth capital charge analysis, and detailed breakdowns of capital calculations. These tools are provided separately—see below or contact us for more information.

## Core Calculators

The core calculator modules:

- **FRTBUtils.py** : Implements the Market Risk Standardised Approach calculations, including the Sensitivity-Based Method (SBM).
- **rhoova\_func.py** : Implements additional risk factor processing functions used in the capital calculation framework.
  ```python
  from rhoova.Client import *
  # Register and get API key from https://app.rhoova.com/
  config = ClientConfig("", "")
  api = Api(config)
  ```

### Helper Calculators

- **xls\_to\_py** : Converts Excel-based product data into a Python-compatible format for further processing.
- **create\_task** : Automates the task creation process for risk calculations.
- **positions.py** : Converts products to the Rhoova API format for risk computations.
- **tradefiles.py** : Processes trade files to align with Rhoova API specifications.

## Configs

The Configs folder includes definitions for yield curves, which are essential for interest rate risk calculations. These configurations provide structured yield curve data that facilitate accurate risk factor mapping and regulatory compliance.

## Data

The Data folder contains yield curve, market data, and volatility data, which is used for interest rate risk modeling and valuation adjustments in capital calculations.

## Positions

- **positions.xlsx** : Specifies the products to be included in the market risk calculations.
- **position\_data** : Contains detailed information about the products included in the risk assessments.

## Examples

- **SAMR.ipynb** : A Jupyter Notebook demonstrating the Standardised Approach Market Risk capital calculations.

## Feedback

If you have any feedback, please reach out to us at rhoova.ekinoks@gmail.com
