"""
Outline-only ML models.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Scope:
- Train predictive models to forecast:
  - next-period return sign (classification)
  - next-period return magnitude (regression)
  - next-period volatility or tail risk (regression/classification)

Data protocol:
- Input: feature table aligned by time, produced by `src/features/*`
- Target definitions (examples):
  - y_t = 1[r_{t+1} > 0]
  - y_t = r_{t+1}
  - y_t = realized_vol_{t+1:t+h}

Validation protocol:
- Strict time-series splits
  - expanding window train -> validate -> test
  - or walk-forward with periodic refits
- Avoid leakage:
  - scaling and feature selection must be fit on train only

Planned models:
- baseline: logistic regression, ridge regression
- tree-based: random forest, gradient boosting
- optional later: XGBoost/LightGBM (additional deps)

Outputs:
- predicted probabilities or forecasts
- calibration metrics (Brier, reliability curve) for probabilistic outputs
"""
