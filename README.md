# 图谱谱扩散因子

**简体中文** | [English](README.en.md)

> 一句话定位：把已确认的 PandaData 日频因子通道放到点时股票关系图上，用固定图滤波构造扩散、滞后与局部残差因子。

## 这是什么

本 Skill 使用行业/概念关系构建版本化股票图，对动量、流动性和风险通道执行确定性的对称归一化图传播。它不训练 GNN，不自动搜索因子字段，也不把当前行业分类倒填到历史。

真实 `get_factor` 小样本已经确认 `momentum`、`liquidity`、`beta`、`residual_volatility`、`cal_daily_rise`、`cal_10d_120d_turnover_ratio` 和 `cal_30d_close_std_ratio` 可返回。`ratio_market_cap_float` 仅作可选控制；分钟字段 `cal_open_30min_return` 当前服务端不支持。

## 快速开始

```bash
python scripts/build_diffusion_panel.py tests/fixtures/minimal_panel/panel.json tests/fixtures/minimal_panel/relationships.json --config examples/config.example.json --allow-static-fixture --out /tmp/factors.json
python -m unittest discover -s tests -v
node scripts/validate-qsh-form.mjs SKILL.md
```

`relationships.json` is a static synthetic fixture and therefore uses `--allow-static-fixture`. Formal runs must provide `effective_date` and must not use that flag.

## 核心通道

- 动量：`momentum` + `cal_daily_rise`
- 流动性：`liquidity` + `cal_10d_120d_turnover_ratio`
- 风险：`residual_volatility` + `cal_30d_close_std_ratio`
- 控制：`beta`、可选 `ratio_market_cap_float`

每个核心通道要求两个字段同时存在，缺失时不动态换权。

## 数学输出

- `low = S^2 x`：两步图平滑共同成分；
- `high = x - low`：局部图残差；
- `neighbor_lag = S x_(T-1) - x_T`：严格历史邻居传播滞后；
- `graph_diffusion_confirmation`：动量与流动性滞后的固定等权组合；
- `graph_residual_reversal`：独立的动量高频残差候选；
- `price_liquidity_divergence`：价格与流动性扩散分歧。

## 边界

本 Skill 不替代 PandaData API、因子评价、IC、回测、组合优化或风险模型，不训练神经网络，不使用未来图关系，不输出投资建议。当前为 `draft/listed`；synthetic 测试和两只股票的真实接口 smoke test 都不证明正式样本外有效性。

## 许可证

GPL-3.0，见 [LICENSE](LICENSE)。
