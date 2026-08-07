# Factor Channel Contract

The v1 channels are fixed before evaluation:

- momentum: `momentum`, `cal_daily_rise`;
- liquidity: `liquidity`, `cal_10d_120d_turnover_ratio`;
- risk: `residual_volatility`, `cal_30d_close_std_ratio`.

Each channel requires both fields. Missing one field makes that channel unavailable; there is no dynamic substitution. `beta` and `ratio_market_cap_float` are controls only. The latter is optional because bounded live coverage was incomplete.

Channel fields are averaged only after their own point-in-time and finite-value checks, then robustly standardized across the active graph nodes.
