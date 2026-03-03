"""
Outline-only Markov chain / regime modeling.

DO NOT IMPLEMENT YET (per project requirement: "do not code anything").

Two starting approaches:

1) Observable-state Markov chain (recommended first)
   - Define discrete states by binning an observable series:
     - realized volatility bins (low/med/high)
     - return bins (neg/flat/pos)
   - Estimate transition matrix P from historical state sequences:
     P_ij = Pr(z_{t+1}=j | z_t=i)
   - Use P to forecast regime probabilities and regime persistence.

2) Hidden Markov Model (future upgrade)
   - Latent state z_t emits returns:
     r_t | z_t ~ Normal(mu_{z_t}, sigma_{z_t}^2) (or Student-t)
   - Fit via EM (Baum–Welch)
   - Use filtering to get p(z_t=k | data up to t)

Planned outputs:
- `state_t` (hard state) or `p_state_k_t` (soft probabilities)
- `transition_matrix` estimates
- derived features:
  - probability of high-vol regime
  - expected next-vol given current regime distribution

Integration points:
- Use regimes to:
  - gate strategies (only trade in certain regimes)
  - parameterize simulation (regime-dependent drift/vol)
  - set risk limits (reduce exposure in high-vol states)
"""
