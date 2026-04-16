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

    state_probs = model.predict_proba(data)

    df_probs = pd.DataFrame(state_probs, columns=['prob_bear', 'prob_chop', 'prob_bull'], index=subset.index)
    df = pd.concat([df, df_probs], axis=1)
        
    return df.assign(hmm_regimes=regime_series)

import numpy as np
import pandas as pd

def add_triple_barrier_labels(df, days=5, pt_mult=2, sl_mult=1):
    """
    Adds target_label to the dataframe.
    1  : Profit Target Hit
    0  : Time Limit Hit (Vertical Barrier)
    -1 : Stop Loss Hit
    """
    # 1. Use the returns you already calculated to find daily volatility
    # We use a 20-day rolling standard deviation
    vol = df['returns'].rolling(window=20).std()
    
    # 2. Define the barriers
    # Profit target and Stop loss are multiples of the current volatility
    df['upper_barrier'] = df['close'] * (1 + (vol * pt_mult))
    df['lower_barrier'] = df['close'] * (1 - (vol * sl_mult))
    
    labels = []
    
    # 3. Labeling Loop
    # We look ahead 'days' to see which barrier is crossed first
    prices = df['close'].values
    upper = df['upper_barrier'].values
    lower = df['lower_barrier'].values
    
    for i in range(len(prices) - days):
        # Look at the window of future prices
        future_window = prices[i+1 : i+1+days]
        
        # Check for touches
        hits_upper = np.where(future_window >= upper[i])[0]
        hits_lower = np.where(future_window <= lower[i])[0]
        
        first_upper = hits_upper[0] if len(hits_upper) > 0 else 1000
        first_lower = hits_lower[0] if len(hits_lower) > 0 else 1000
        
        if first_upper < first_lower and first_upper < days:
            labels.append(1)  # Profit
        elif first_lower < first_upper and first_lower < days:
            labels.append(-1) # Loss
        else:
            labels.append(0)  # Time out (Vertical Barrier)

    # Pad the end with NaNs because we can't look forward at the very end
    labels += [np.nan] * days
    df['target_label'] = labels
    return df

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
        add_triple_barrier_labels,
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