"""
Outline-only backtest engine.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Purpose:
- Convert signals/positions into a portfolio equity curve and performance metrics.

Core interfaces to design:

- Inputs
  - prices:
    - single-asset Series or multi-asset DataFrame (close prices)
  - signals / target weights:
    - time series in [-1, 1] per asset (or per strategy)
  - trading assumptions:
    - execution delay (trade at next bar open/close)
    - transaction costs (fixed + proportional)
    - slippage model
    - borrow costs for shorts, margin/leverage constraints

- Outputs
  - per-period portfolio returns
  - equity curve
  - trade log (optional, but extremely useful)
  - metrics (delegate to `src/backtest/metrics.py`)

Avoiding common pitfalls:
- Enforce no lookahead: signal at time t trades at t+1.
- Align timestamps exactly between prices, signals, and any features.
- Handle missing bars and partial trading days.

Planned components:
- `BacktestConfig` (dataclass-like): costs, slippage, execution timing, frequency
- `BacktestResults` (dataclass-like): returns, equity, drawdowns, exposures, turnover
- `run_backtest(...)`: orchestrate simulation
"""

