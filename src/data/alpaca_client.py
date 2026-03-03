"""
Outline-only Alpaca client configuration.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Use Alpaca's official Python SDK: `alpaca-py`.

What this module should eventually do:

- Load environment variables (prefer `.env` for local dev)
  - `ALPACA_API_KEY`
  - `ALPACA_API_SECRET`
  - `ALPACA_BASE_URL` (paper vs live trading)
  - `ALPACA_DATA_FEED` (e.g., "iex" or "sip", depending on plan)

- Construct clients for:
  - Market data (historical bars, latest quote/trade, etc.)
  - Trading (submit orders, positions, account, etc.) — optional until live trading

- Centralize:
  - retry policy for transient errors
  - rate limit handling
  - request logging
  - timeouts

Notes:
- Keep "trading" client separate from "data" client so research/backtest can run without
  any trading permissions.
"""
