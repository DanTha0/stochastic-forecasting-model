import numpy as np
import pandas as pd
from toolz import pipe
from ..features.get_indicators import add_indicators

# --- 1. Pure Transformation Functions ---

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
        lambda x: x.dropna()  # Final cleanup of rolling/shift NaNs
    )

# --- 3.Data Allocation Functions ---

def split_data(df, ratio=0.8):
    """Splits data chronologically at a fixed point."""
    split_point = int(len(df) * ratio)
    return df.iloc[:split_point], df.iloc[split_point:]

# --- Execution Example ---
# cleaned_data = process_data(yahoo_df)
# train, test = split_data(cleaned_data)