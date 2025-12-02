import datetime
import pandas as pd
import numpy as np
import math

def safe_strftime(value):
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value)  # zaten string ise veya başka türde ise stringe çevir

def extract_field(wb: pd.DataFrame, isin: str, column: str, default=None):
    """
    Extract a single field for a given ISIN and convert it to a JSON-safe Python type.

    Parameters
    ----------
    wb : pandas.DataFrame
        Source dataframe that contains at least 'isin_code' and the target column.
    isin : str
        ISIN code to match in the 'isin_code' column.
    column : str
        Column name whose value will be extracted.
    default : Any, optional
        Value to return when the ISIN is not found or the extracted value is NaN.
        Defaults to None.

    Returns
    -------
    Any
        JSON-safe Python object: native int/float/str or None.
    """
    series = wb.loc[wb["isin_code"] == isin, column]

    if series.empty:
        return default

    value = series.iloc[0]

    # NaN kontrolü
    if (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return default

    # numpy türlerini dönüştür
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64)):
        return float(value)
    elif isinstance(value, (np.bool_, bool)):
        return bool(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()

    return value


def extract_field2(wb: pd.DataFrame, isin: str, column: str, default=None):
    """
    Extract a single field for a given ISIN and convert it to a JSON-safe Python type.

    Parameters
    ----------
    wb : pandas.DataFrame
        Source dataframe that contains at least 'isin_code' and the target column.
    isin : str
        ISIN code to match in the 'isin_code' column.
    column : str
        Column name whose value will be extracted.
    default : Any, optional
        Value to return when the ISIN is not found or the extracted value is NaN.
        Defaults to None.

    Returns
    -------
    Any
        JSON-safe Python object: native int/float/str or None.
    """
    series = wb.loc[wb["trade_code"] == isin, column]

    if series.empty:
        return default

    value = series.iloc[0]

    # NaN kontrolü
    if (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return default

    # numpy türlerini dönüştür
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64)):
        return float(value)
    elif isinstance(value, (np.bool_, bool)):
        return bool(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()

    return value

#def extract_field(wb, isin, column):
#    return list(wb[wb["isin_code"] == isin][column])[0]


#def extract_field2(wb, trade_code, column):
#    return list(wb[wb["trade_code"] == trade_code][column])[0]