"""
Get forecasted volatility for trading day ahead (RUN ONCE A DAY)
"""

import pandas as pd
import numpy as np
from arch import arch_model

def forecast_garch_volatility(df, p=1, q=1, dist='t'):
    """
    Fits a GARCH(p,q) model to the returns and forecasts 1-step ahead.
    Returns the annualized volatility forecast for 'tomorrow' as float and the model parameters as Pandas series.
    """
    returns = df['returns'].dropna() * 100
    
    # constant Mean + GARCH(1,1) with t-distribution for wider tails
    model = arch_model(returns, vol='Garch', p=p, q=q, dist=dist, rescale=False)
    
    # update_freq=0 silences the iteration logs for cleaner output
    res = model.fit(disp='off', update_freq=0)
    
    # horizon=1, next day ahead
    forecasts = res.forecast(horizon=1)
    
    # forecast.variance is for scaled returns, so we sqrt and divide by 100
    daily_vol_forecast = np.sqrt(forecasts.variance.values[-1, -1]) / 100
    return (daily_vol_forecast * np.sqrt(252)), res.params

if __name__ == "__main__":
    df = pd.read_parquet("data/processed/SPY_1d_clean.parquet")
    next_vol, params = forecast_garch_volatility(df)
    print(f"--- GARCH(1,1) Results ---")
    print(f"Alpha (Shock Intensity): {params['alpha[1]']:.4f}")
    print(f"Beta (Persistence):     {params['beta[1]']:.4f}")
    print(f"Next Day Annualized Vol: {next_vol:.2%}")