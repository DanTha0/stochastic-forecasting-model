"""
Outline-only stochastic processes: Brownian motion, GBM, and extensions.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Core mathematical objects to support:

- Standard Brownian motion W_t
  - increments: W_{t+dt} - W_t ~ Normal(0, dt)

- Geometric Brownian motion (GBM) for prices
  - dS_t = mu S_t dt + sigma S_t dW_t
  - discrete:
    S_{t+dt} = S_t * exp((mu - 0.5 sigma^2) dt + sigma sqrt(dt) Z)

- Discrete-time return model (often better for empirical work)
  - r_t = mu_t dt + sigma_t sqrt(dt) epsilon_t
  - where sigma_t comes from GARCH / regime model / stochastic vol

Calibration (outline):
- estimate drift and diffusion parameters from historical returns
- choose dt consistent with bar frequency (daily => dt=1/252; intraday needs scaling)

Validation (outline):
- compare empirical return distribution vs simulated
- check autocorrelation of returns and squared returns
"""
