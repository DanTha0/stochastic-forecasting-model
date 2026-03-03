"""
Outline-only signal rules: convert forecasts/distributions into buy/sell/hold signals.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Inputs (examples):
- expected return forecast (point)
- probability of positive return (prob_up)
- volatility forecast (sigma_hat)
- Monte Carlo distribution outputs (VaR, CVaR, Pr(drawdown > X))
- Markov regime probabilities (p_state_k)

Signal styles to support:

- Probability thresholding
  - long if Pr(R_{t:t+h} > 0) > tau_long
  - short if Pr(R_{t:t+h} > 0) < tau_short
  - otherwise flat

- Risk-adjusted expected return
  - long if E[R]/E[sigma] > threshold

- Regime filters
  - only trade if Pr(high-vol) < cap
  - reduce leverage in certain regimes

Outputs:
- target position weights w_t in [-1, 1] (single asset) or per-asset vector
- optional discrete signals in {-1, 0, 1}

Notes:
- Keep signal generation separate from backtest execution logic.
- Ensure signals are timestamp-aligned and contain no future information.
"""
