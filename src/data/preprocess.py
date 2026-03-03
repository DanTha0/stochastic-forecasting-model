"""
Outline-only module for preprocessing raw Alpaca data into research-ready time series.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Inputs:
- Raw bar data from `data/raw/` produced by `src/data/fetch_data.py`

Outputs:
- Processed datasets under `data/processed/`:
  - canonical OHLCV table
  - returns table
  - volatility features table (basic proxies)
  - optional aligned multi-asset panel

Core transformations to implement:

- Normalize schema
  - standardize column names: open/high/low/close/volume/vwap/trade_count
  - ensure timestamp index is timezone-aware and consistent
  - sort by time, drop duplicates

- Returns
  - log returns: r_t = log(C_t / C_{t-1})
  - arithmetic returns: (C_t / C_{t-1}) - 1
  - decide which return type is used by each downstream model

- Realized volatility proxies (examples for daily; adjust for intraday)
  - rolling window std of returns
  - OHLC estimators (Parkinson, Garman–Klass, Rogers–Satchell)
  - optional microstructure handling for intraday (outliers, gaps)

- Resampling
  - resample intraday to daily/weekly when needed
  - decide fill policy (generally avoid forward-fill for prices)

- Split logic
  - time-based train/val/test split
  - walk-forward windows for refitting (store window definitions)

Quality checks to add:
  - missing bars, holiday gaps, early closes
  - abnormal returns/outliers
  - symbol changes/corporate actions policy (splits/dividends)
"""

