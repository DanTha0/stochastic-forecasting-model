# Stochastic Forecasting Model

This project is a quantitative research sandbox for equities. It lets you:

- **Fetch historical stock data** from an API (**Alpaca** only).
- **Build time series** of prices, returns, and volatility.
- **Experiment with stochastic models** (Markov chains, Brownian motion, GARCH, Monte Carlo).
- **Train ML models** on engineered features.
- **Generate buy/sell signals** and **backtest** them.

The initial scaffold focuses on:

- A minimal data pipeline (download + preprocess).
- A very simple strategy and backtest loop.
- A structure you can extend with more advanced models.

---

## Installation

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows PowerShell
pip install -r requirements.txt
```

If you use a different environment manager (Conda, etc.), adjust accordingly.

---

## Quick start: run a demo backtest

From the project root, after installing dependencies:

```bash
python run_backtest.py
```

What this script currently does:

- (Outline only scaffold) Defines the end-to-end flow you will implement:
  - Fetch OHLCV data from Alpaca.
  - Compute log returns and volatility features.
  - Generate signals (stochastic models / ML).
  - Backtest and report metrics.

This end‑to‑end example is intentionally simple. You will later replace the signal generation with:

- Markov chain / regime-based signals.
- GARCH / volatility-based signals.
- Monte Carlo / Brownian motion derived thresholds.
- ML-based predictions.

---

## Project layout

Planned `src/` structure:

- `src/data/`
  - `alpaca_client.py`: Alpaca API client setup (paper/live, keys, rate limits).
  - `fetch_data.py`: download and save raw data via Alpaca.
  - `preprocess.py`: load data, build returns, and basic transformations.
- `src/backtest/`
  - `engine.py`: simple vectorized backtest for signals and PnL.
- (to be added) `src/features/`, `src/models/`, `src/signals/`, etc.

You can iterate by:

1. Adding volatility and stochastic models (GARCH, Markov chains, GBM, Monte Carlo).
2. Engineering features and training ML models.
3. Wiring those into signal generation.
4. Backtesting and refining strategies.

