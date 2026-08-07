# Graph Spectral Diffusion Factor

> One-line positioning: Apply fixed graph-signal filters to confirmed PandaData daily factor channels and produce auditable diffusion, lag, and local-residual factors.

## What this is

This Skill builds a versioned equity graph from industry/concept relationships and applies deterministic symmetric normalized propagation to momentum, liquidity, and risk channels. It trains no GNN, searches no factor universe, and never applies current graph membership retroactively.

A bounded live `get_factor` smoke test confirmed `momentum`, `liquidity`, `beta`, `residual_volatility`, `cal_daily_rise`, `cal_10d_120d_turnover_ratio`, and `cal_30d_close_std_ratio`. `ratio_market_cap_float` is an optional control because observed coverage was partial. The service rejected `cal_open_30min_return`, so minute-derived fields are not v1 requirements.

## Quick start

```bash
python scripts/build_diffusion_panel.py tests/fixtures/minimal_panel/panel.json tests/fixtures/minimal_panel/relationships.json --config examples/config.example.json --allow-static-fixture --out /tmp/factors.json
python -m unittest discover -s tests -v
node scripts/validate-qsh-form.mjs SKILL.md
```

`relationships.json` is a static synthetic fixture and therefore uses `--allow-static-fixture`. Formal runs must provide `effective_date` and must not use that flag.

## Fixed channels

- momentum: `momentum` + `cal_daily_rise`;
- liquidity: `liquidity` + `cal_10d_120d_turnover_ratio`;
- risk: `residual_volatility` + `cal_30d_close_std_ratio`;
- controls: `beta`, optional `ratio_market_cap_float`.

Both fields are required for a core channel. Missing fields never trigger dynamic substitution.

## Outputs

- `low = S^2 x`: two-step graph-smooth component;
- `high = x - low`: local graph residual;
- `neighbor_lag = S x_(T-1) - x_T`: strictly lagged neighbor propagation;
- `graph_diffusion_confirmation`: fixed equal-weight momentum/liquidity lag combination;
- `graph_residual_reversal`: separate momentum residual candidate;
- `price_liquidity_divergence`: disagreement between price and liquidity diffusion.

## Boundary

This Skill does not replace PandaData APIs, factor evaluation, IC, backtests, portfolio optimization, or risk models. It trains no neural network, uses no future graph relation, and provides no investment advice. It remains `draft/listed`; synthetic tests and a two-symbol API smoke test do not establish out-of-sample validity.

## License

GPL-3.0. See [LICENSE](LICENSE).
