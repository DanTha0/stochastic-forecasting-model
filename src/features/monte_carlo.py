"""
Outline-only Monte Carlo simulation engine.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Goal:
- Simulate future distributions of returns/prices/volatility for signal generation and risk.

Simulation modes to support:

- GBM baseline (constant sigma)
- GARCH-driven simulation (time-varying sigma_t)
- Regime-switching simulation:
  - simulate regime z_t as Markov chain
  - conditional parameters (mu, sigma, GARCH params) depend on z_t

Key design choices:
- horizon h: number of steps to simulate (e.g., 5 days)
- n_paths: number of Monte Carlo paths (e.g., 10k)
- random seed control for reproducibility

Outputs to compute for signals:
- Pr(cumulative return > 0)
- expected return and variance
- tail risk metrics: VaR, CVaR (expected shortfall)
- probability of drawdown exceeding a threshold

Integration points:
- use `src/features/volatility_models.py` forecasts
- use `src/features/markov_chains.py` transition matrix / state probabilities
- use `src/signals/signal_rules.py` to translate distributions into trades
"""
