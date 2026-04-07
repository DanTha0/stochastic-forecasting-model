"""
Outline-only volatility modeling (GARCH family and realized volatility).

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Primary goals:
- Estimate/forecast conditional volatility sigma_t
- Produce volatility features used by:
  - risk sizing (vol targeting)
  - regime labeling (Markov states)
  - Monte Carlo simulation (path generation)

Planned pieces:

- Realized volatility estimators (from returns or OHLC)
  - rolling std (baseline)
  - Parkinson / Garman–Klass / Rogers–Satchell if OHLC is available

- GARCH models (using `arch` package)
  - GARCH(1,1), EGARCH, GJR-GARCH (as needed)
  - Gaussian vs Student-t innovations

- Forecasting modes
  - one-step-ahead volatility forecasts
  - multi-step volatility forecasts (term structure)
  - rolling refit schedule (e.g., refit every N bars)

Interfaces to define:

- `fit_garch(returns, model_spec, distribution, ...)` returns a fitted model
- `forecast_vol(fitted_model, horizon, ...)` returns series or dataframe
- `rolling_garch_forecast(returns, window, refit_every, ...)` returns vol forecasts

Validation diagnostics to add:
- standardized residuals: should be closer to i.i.d.
- Ljung–Box on residuals and squared residuals
- backtest of VaR exceedances (optional)
"""
