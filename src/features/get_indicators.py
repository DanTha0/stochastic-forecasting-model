"""
Get day-ahead indicators (RUN ONCE A DAY)
"""
import pandas_ta as ta
import pandas as pd

def add_indicators(df):
    """
    Add technical indicators to the dataframe: RSI and MACD.
    
    Args:
        df: DataFrame with OHLCV data including 'close' column
        
    Returns:
        DataFrame with added 'RSI', 'MACD_*' columns
    """
    # RSI (14 day)
    df["RSI"] = ta.rsi(df["close"], length=14)
    
    # MACD (12, 26, 9)
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    
    # This returns a DataFrame with MACD, Signal, and Hist columns
    df = pd.concat([df, macd], axis=1)
    
    df['MACD_norm'] = df['MACD_12_26_9'] / df['close']
    df['MACDh_norm'] = df['MACDh_12_26_9'] / df['close']
    df['MACDs_norm'] = df['MACDs_12_26_9'] / df['close']
    
    return df