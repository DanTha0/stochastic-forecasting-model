import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from arch import arch_model
import tqdm
from src.features.garch_volatility import forecast_garch_volatility

def build_garch_history(df, p=1, q=1, window_size=500, warmup=252):
    """
    Runs a rolling GARCH forecast for the entire dataframe.
    window_size: How many past days to look at for each day's fit.
    warmup: Number of initial days to skip before starting the forecast.

    THIS FUNCTION IS VERY COMPUTATIONALLY EXPENSIVE. ONLY RUN ONCE ON WHOLE DATA SET
    """
    garch_history = []

    for i in range(warmup, len(df)):
        # 1. Slice the dataframe up to 'i' (simulating "today")
        historical_slice = df.iloc[:i]
        
        vol_forecast, params = forecast_garch_volatility(historical_slice)
        garch_history.append(vol_forecast)

    # Since we skipped the 'warmup' period, we pad the start with NaNs
    padding = [np.nan] * warmup
    df['garch_vol_forecast'] = padding + garch_history
    return df