"""
Outline-only time series feature engineering.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Inputs:
- Canonical processed dataframe (timestamp index) from `src/data/preprocess.py`

Feature families to implement:

- Lag features
  - r_{t-1}, r_{t-2}, ..., r_{t-k}
  - lagged realized vol proxies

- Rolling window statistics
  - rolling mean/median of returns
  - rolling std/variance of returns
  - rolling skew/kurtosis
  - rolling min/max and drawdown

- Technical indicators (optional; keep separated so you can turn on/off)
  - SMA/EMA, MACD, RSI
  - Bollinger bands

- Calendar/time features (optional)
  - day-of-week effects, month-end, earnings windows (if you add earnings data)

Output:
- A feature table with aligned timestamps, no lookahead, and NaNs only where unavoidable
  due to window sizes (then dropped consistently).

Critical constraints:
- No leakage: any statistic at time t must use data <= t.
"""
