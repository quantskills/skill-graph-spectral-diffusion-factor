# Spectral Filter Contract

This Skill uses deterministic polynomial graph filtering, not a trained graph model.

```text
low_k = S^k x
high_k = x - low_k
neighbor_lag = S x_(T-1) - x_T
```

The default `k=2` is frozen before evaluation. Every channel is median/MAD standardized before filtering. If MAD is zero, the standardized cross-section becomes zero and the state remains diagnostic; a constant channel cannot generate cross-sectional rank information.

The primary factor combines momentum and liquidity neighbor-lag z-scores at fixed 0.5/0.5 weights. Graph residual reversal is a separate candidate.
