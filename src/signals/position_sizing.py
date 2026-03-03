"""
Outline-only position sizing and risk management.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Responsibilities:
- Convert raw directional signals into position sizes with risk controls.

Sizing methods to support:
- constant notional
- volatility targeting:
  - w_t = target_vol / sigma_hat_t (clipped)
- Kelly-inspired sizing (only after strong validation)
- risk parity across assets (if multi-asset)

Risk constraints:
- max gross exposure / leverage
- max position per asset
- stop-loss / take-profit rules (careful: can introduce lookahead if not designed well)
- cooldown periods after stopouts

Integration:
- consume sigma forecasts from `src/features/volatility_models.py`
- consume regime probabilities from `src/features/markov_chains.py`
"""
