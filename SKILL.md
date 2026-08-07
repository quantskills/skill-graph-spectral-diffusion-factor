---
name: graph-spectral-diffusion-factor
description: "Build auditable equity factors by filtering predeclared PandaData factor channels over point-in-time industry and concept graphs. Use when an agent needs to measure graph-wide diffusion, local residuals, lagged neighbor propagation, or price-liquidity disagreement from a date-by-symbol factor panel. Do not use this skill to train graph neural networks, search arbitrary factor fields, reconstruct future graph membership, run portfolio backtests, or issue investment advice."
quantSkills:
  organization: https://github.com/quantskills
  repository: quantskills/skill-graph-spectral-diffusion-factor
  repository_url: https://github.com/quantskills/skill-graph-spectral-diffusion-factor
  project_type: skill
  collection: factor-research-methods
  license: GPL-3.0
  category: factor
  tags: [graph-signal-processing, diffusion-factor, spectral-filter, pandadata, point-in-time]
  platforms: [claude-code, codex, openclaw, cursor, hermes]
  language: zh-en
  status: draft
  validation_level: listed
  maintainer_type: community
  requires: []
  summary_zh: 在点时股票关系图上构造可审计的因子扩散与局部残差
  summary_en: Build auditable factor diffusion and residuals on point-in-time equity graphs
---

```json qsh-form
{
  "version": 1,
  "task": {"placeholder": "构造图谱扩散因子", "required": true},
  "fields": [
    {"key": "input_panel", "type": "text", "label": "因子面板"},
    {"key": "graph_snapshot", "type": "text", "label": "关系图快照"},
    {"key": "graph_layers", "type": "select", "label": "图层", "options": [
      {"value": "industry", "label": "行业图"},
      {"value": "industry_concept", "label": "行业+概念图"}
    ]},
    {"key": "propagation_steps", "type": "number", "label": "传播步数"},
    {"key": "run_primary_test", "type": "select", "label": "执行主检验", "options": [
      {"value": "false", "label": "仅生成因子"},
      {"value": "true", "label": "确认后执行"}
    ]}
  ],
  "prompt_template": "{{task}}；面板：{{input_panel}}；图快照：{{graph_snapshot}}；图层：{{graph_layers}}；传播步数：{{propagation_steps}}；执行主检验：{{run_primary_test}}；附件：{{#attachments}}"
}
```

# Graph Spectral Diffusion Factor

## Scope

This skill consumes a normalized `date × symbol` factor panel and point-in-time relationship snapshots. It builds a deterministic weighted graph, robustly standardizes fixed signal channels, applies symmetric normalized graph propagation, and emits low-frequency diffusion, high-frequency local residual, lagged neighbor propagation, and price-liquidity disagreement features.

## Use When

Use this skill when the user asks to:

- study how momentum, liquidity, or risk signals propagate across an equity relationship graph;
- separate graph-smooth common movement from local stock-specific residuals;
- measure whether neighbors moved before a stock using strictly earlier signals;
- create an auditable factor panel for an existing IC or backtest workflow.

## Do Not Use When

Do not use this skill to:

- train GNN, TCN, Transformer, Autoencoder, or other black-box models;
- search the full `get_factor` field universe or select channels after seeing test results;
- use future industry, concept, correlation, or constituent membership;
- replace PandaData API documentation, factor evaluation, backtesting, portfolio optimization, or a risk model;
- issue buy, sell, sizing, or guaranteed-return instructions.

## Confirmed PandaData Contract

A bounded live smoke test with `panda_data==0.0.12` confirmed `get_factor` output keyed by `date × symbol` for two A-share symbols and two dates. The following fields were returned with complete coverage in that smoke test:

- momentum channel: `momentum`, `cal_daily_rise`;
- liquidity channel: `liquidity`, `cal_10d_120d_turnover_ratio`;
- risk channel: `residual_volatility`, `cal_30d_close_std_ratio`;
- control: `beta`.

`ratio_market_cap_float` was returned but had partial coverage and is optional. `cal_open_30min_return` was rejected by the service as unsupported and is not a runtime requirement. The smoke test verifies interface mechanics only, not full-universe coverage or investment validity.

## Graph and Signal Contract

The primary graph uses versioned industry edges. Optional concept edges have a separately declared coefficient. Correlation edges use only dates `< T` and are disabled in the primary factor by default. Edge weights, graph snapshot version, and graph fingerprint are recorded.

For channel signal `x` and symmetric normalized adjacency `S = D^(-1/2) A D^(-1/2)`:

```text
low_k = S^k x
high_k = x - low_k
neighbor_lag = S x_(T-1) - x_T
```

The default propagation depth is fixed at `k=2`. Isolated nodes fail closed for graph-derived factors. Missing core fields do not trigger dynamic channel reweighting.

The primary factor is a fixed combination of robustly standardized momentum and liquidity neighbor-lag features. `graph_residual_reversal = -z(momentum_high)` remains a separate candidate and is not selected after observing test performance.

## Point-in-Time and Output Boundary

T-day factor fields and the T graph snapshot generate signals after the close for T+1 use. Lagged neighbor propagation uses T-1 node signals. Labels and backtests are external. Outputs include graph/channel versions, coverage, degree, low/high components, lagged propagation, divergence, status, and input/graph fingerprints.

This is a falsifiable research method, not investment advice. Synthetic tests and the bounded live query do not justify upgrading `validation_level` beyond `listed`.

## Local Commands

```bash
python scripts/check_runtime.py
python scripts/build_graph.py tests/fixtures/minimal_panel/relationships.json --out /tmp/graph.json
python scripts/build_diffusion_panel.py tests/fixtures/minimal_panel/panel.json tests/fixtures/minimal_panel/relationships.json --out /tmp/factors.json
python -m unittest discover -s tests -v
node scripts/validate-qsh-form.mjs SKILL.md
```
