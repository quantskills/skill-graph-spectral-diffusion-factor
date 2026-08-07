# PandaData Contract

Runtime reference: `panda_data==0.0.12` and `skill-pandadata-api`.

Confirmed signature:

```python
get_factor(symbol="", start_date="", end_date="", type="stock", factors=None, index_component="", **kwargs)
```

`start_date`, `end_date`, and `factors` are required; dates use `YYYYMMDD`; `symbol` and `factors` accept strings or lists; the SDK rejects extra parameters and date spans over five years.

A bounded live smoke test on `000001.SZ` and `600000.SH`, 20260803-20260804, returned unique `date × symbol` rows and complete coverage for `momentum`, `liquidity`, `beta`, `residual_volatility`, `cal_daily_rise`, `cal_10d_120d_turnover_ratio`, and `cal_30d_close_std_ratio`. `ratio_market_cap_float` had 50% coverage in that sample. `cal_open_30min_return` was rejected with service code 100006 and is blocked in v1.

This repository does not perform login or store credentials. MCP is not a runtime dependency. A field dictionary is not evidence that a field is enabled by the current service.
