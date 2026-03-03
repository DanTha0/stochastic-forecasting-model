"""
Outline-only module for fetching and caching market data via Alpaca.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Responsibilities:

- Connect to Alpaca Market Data API (paper/live base URL selection is account-dependent)
  - Setup client in `src/data/alpaca_client.py`
  - Credentials loaded from environment (see `.env.example`)

- Fetch bars (OHLCV) for one or more symbols
  - Decide bar timeframe(s): 1Min, 5Min, 15Min, 1Hour, 1Day, etc.
  - Decide data feed: SIP vs IEX (availability depends on plan)
  - Handle pagination and rate limits

- Save raw data to disk (reproducibility)
  - Prefer parquet: `data/raw/{symbol}_{timeframe}_{start}_{end}.parquet`
  - Store metadata (request params, timezone, adjustments, feed)

- Provide loaders
  - Load raw dataset by path and return a canonical dataframe with:
    - index: timestamp (timezone-aware, consistent)
    - columns: open, high, low, close, volume, vwap, trade_count (as available)

Design notes:

- Keep this layer pure data I/O. No feature engineering here.
- Enforce strict time alignment and no forward-fill across missing timestamps
  (unless a specific resampling procedure in preprocessing requires it).
"""

