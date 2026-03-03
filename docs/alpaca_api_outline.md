# Alpaca API (outline only)

This project will use **Alpaca** for market data (and optionally trading).

This file is intentionally an outline (no code).

---

## What you need from Alpaca

- API key + secret
- Knowledge of your allowed **market data feed** (IEX vs SIP)
- Whether you're using paper or live trading base URL

Credentials are expected in `.env` (see `.env.example`).

---

## Primary Alpaca capabilities to use

### Market data: historical bars

Goal: fetch OHLCV bars for one or more symbols over a date range.

Parameters you’ll standardize in the project:
- **symbols**: list like `["SPY", "AAPL"]`
- **timeframe**: e.g., 1Min / 5Min / 1Hour / 1Day
- **start/end**
- **feed**: `iex` or `sip` (plan-dependent)
- **adjustment**: policy for splits/dividends (confirm available options in Alpaca docs)

Output schema (canonical):
- timestamp index
- open, high, low, close, volume
- optional: vwap, trade_count

### Market data: latest quote/trade (optional later)

Used for live execution or sanity checks in a paper-trading loop.

---

## How it maps into the repo

- `src/data/alpaca_client.py`
  - outlines how clients are constructed from env vars
- `src/data/fetch_data.py`
  - outlines how you’ll request bars, handle pagination/rate limits, and cache to `data/raw/`
- `src/data/preprocess.py`
  - outlines how you normalize timestamps/schema and compute returns

---

## Notes (important)

- Keep research/backtest reproducible by caching raw responses (or normalized raw bars).
- Never hardcode keys in code or config YAML.
- Treat timezones carefully; convert to one canonical timezone early.

