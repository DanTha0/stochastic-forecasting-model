"""
Outline-only entrypoint for an end-to-end research run.

DO NOT IMPLEMENT HERE YET (per project requirement: "do not code anything").

Intended future flow:

- Load configuration (tickers, timeframe, date range, data source = Alpaca)
  - config: `config/config.yaml`
  - secrets: `.env` (NOT committed; see `.env.example`)

- Fetch/cached data via Alpaca
  - module: `src/data/alpaca_client.py`
  - module: `src/data/fetch_data.py`
  - storage: `data/raw/` (e.g., parquet)

- Preprocess into a canonical research table
  - module: `src/data/preprocess.py`
  - outputs:
    - clean OHLCV
    - log returns
    - realized volatility proxies (rolling std, Parkinson/Garman-Klass if using OHLC)
    - train/val/test split indices (time-based)

- Build model features
  - module: `src/features/time_series_features.py`
  - module: `src/features/volatility_models.py` (GARCH family)
  - module: `src/features/markov_chains.py` (regime states / transition matrix)
  - module: `src/features/monte_carlo.py` (GBM / regime-conditional simulation)

- Produce signals and positions
  - module: `src/signals/signal_rules.py`
  - module: `src/signals/position_sizing.py`
  - goal: signal is a time series of desired position weights

- Backtest and report
  - module: `src/backtest/engine.py`
  - module: `src/backtest/metrics.py`
  - outputs:
    - equity curve
    - performance metrics (CAGR, Sharpe, MDD, turnover)
    - charts/report artifacts (optional)
"""

