import numpy as np
from hmmlearn import hmm
import pandas as pd
from toolz import pipe
from ..features.get_indicators import add_indicators
from .ml_data_process import build_garch_history

# --- 1. Pure Transformation Functions ---

def add_hmm_regimes(df, n_states=3):
    """Fits an Hidden Markov Model to returns and GARCH forecasts, assigns regimes."""
    subset = df[['returns', 'garch_vol_forecast']].dropna()
    data = subset.values

    model = hmm.GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)
    model.fit(data)

    state_means = model.means_[:, 0] 
    idx = np.argsort(state_means)

    model.means_ = model.means_[idx]
    model.covars_ = model.covars_[idx]
    model.startprob_ = model.startprob_[idx]
    model.transmat_ = model.transmat_[idx, :][:, idx]

    states = model.predict(data)
    regime_series = pd.Series(states, index=subset.index, name="hmm_regimes")
        
    return df.assign(hmm_regimes=regime_series)

def normalize_columns(df):
    """Returns a new DF with lowercase, snake_case headers."""
    new_cols = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df.rename(columns=dict(zip(df.columns, new_cols)))

def fix_index(df):
    """Ensures a sorted, unique DatetimeIndex."""
    return (df.assign(temp_idx=pd.to_datetime(df.index))
            .set_index("temp_idx")
            .sort_index()
            .loc[~df.index.duplicated(keep="last")]
            .rename_axis("timestamp"))

def filter_invalid_bars(df):
    """Removes rows violating physical price constraints."""
    mask = (df["high"] >= df["low"]) & (df["low"] > 0) & (df["close"] > 0)
    return df.loc[mask]

def add_returns(df, log=True):
    """Calculates returns based on adjusted close or close."""
    target = "adj_close" if "adj_close" in df.columns else "close"
    if log:
        ret = np.log(df[target] / df[target].shift(1))
    else:
        ret = df[target].pct_change()
    return df.assign(returns=ret)

def add_volatility(df, window=21):
    """Adds annualized rolling realized volatility."""
    vol = df["returns"].rolling(window).std() * np.sqrt(252) # Annualize assuming 252 trading days
    return df.assign(volatility=vol)

def add_day_ahead_indicators(df):
    """Adds day-ahead indicators."""
    return add_indicators(df)

def winsorize(df, q=0.001):
    """Clips extreme outliers at the given quantiles."""
    lower, upper = df["returns"].quantile([q, 1-q])
    return df.assign(returns=df["returns"].clip(lower, upper))

# --- 2. The Functional Pipeline ---

def process_data(raw_df):
    """
    The pipeline: Data flows through these functions like an assembly line.
    Each function takes a DataFrame and returns a new DataFrame.
    """
    return pipe(
        raw_df,
        normalize_columns,
        fix_index,
        filter_invalid_bars,
        add_returns,
        winsorize,
        add_volatility,
        add_day_ahead_indicators,
        build_garch_history,
        add_hmm_regimes,
        lambda df: df.dropna()  # Final cleanup to remove rows with NaNs from indicators
    )

# --- 3.Data Allocation Functions ---

def split_data(df, ratio=0.8):
    """Splits data chronologically at a fixed point."""
    split_point = int(len(df) * ratio)
    return df.iloc[:split_point], df.iloc[split_point:]

# --- Execution Example ---
# cleaned_data = process_data(yahoo_df)
# train, test = split_data(cleaned_data)