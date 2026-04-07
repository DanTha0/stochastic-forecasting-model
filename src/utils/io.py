"""
Load and save processed time-series tables so you preprocess once and reuse everywhere.

Typical layout:
  - ``data/processed/{SYMBOL}_{interval}_clean.csv`` — main artifact (training, backtests, notebooks).
  - ``data/processed/{SYMBOL}_{interval}_clean.parquet`` — optional fast reload in pandas.
"""

from pathlib import Path

import pandas as pd


def save_processed_csv(df, path):
    """
    Write a processed DataFrame to CSV with the datetime index preserved (first column).

    Use this after ``process_data`` so you can reload later without Yahoo or preprocessing.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=True)


def load_processed_csv(path):
    """
    Load a CSV saved by ``save_processed_csv``.

    Returns a DataFrame with a DatetimeIndex parsed from the first column.
    """
    path = Path(path)
    return pd.read_csv(path, index_col=0, parse_dates=True)


def save_processed_parquet(df, path):
    """Write processed data as Parquet (requires pyarrow or fastparquet)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
