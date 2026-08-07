#!/usr/bin/env python3
"""Build fixed graph-diffusion channels from a point-in-time factor panel."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import build_graph
import compute_spectral_features as spectral
import normalize_factor_panel

DEFAULT_CONFIG = {
    "channels": {
        "momentum": ["momentum", "cal_daily_rise"],
        "liquidity": ["liquidity", "cal_10d_120d_turnover_ratio"],
        "risk": ["residual_volatility", "cal_30d_close_std_ratio"],
    },
    "graph_layers": ["industry", "concept"],
    "layer_weights": {"industry": 1.0, "concept": 0.5, "correlation": 0.0},
    "propagation_steps": 2,
    "min_degree": 0.0,
}


def _config(value):
    result = {
        **DEFAULT_CONFIG,
        "channels": dict(DEFAULT_CONFIG["channels"]),
        "layer_weights": dict(DEFAULT_CONFIG["layer_weights"]),
    }
    result.update(value or {})
    if set(result["channels"]) != {"momentum", "liquidity", "risk"}:
        raise ValueError("channels must define momentum, liquidity, and risk")
    if any(not isinstance(fields, list) or not fields for fields in result["channels"].values()):
        raise ValueError("every channel must contain at least one field")
    if "correlation" in result["graph_layers"]:
        raise ValueError("correlation layer is diagnostic-only in v1")
    if int(result["propagation_steps"]) < 1:
        raise ValueError("propagation_steps must be positive")
    if float(result["min_degree"]) < 0:
        raise ValueError("min_degree must be non-negative")
    return result


def build(panel_rows, relationship_rows, steps=None, config=None, allow_static_fixture=False):
    config = _config(config)
    if steps is not None:
        config["propagation_steps"] = steps
    panel = normalize_factor_panel.normalize(panel_rows, channels=config["channels"])
    by_date = defaultdict(list)
    for row in panel:
        by_date[row["date"]].append(row)
    dates = sorted(by_date)
    output, diagnostics = [], []
    previous_rows = {}
    for date in dates:
        current_rows = {row["symbol"]: row for row in by_date[date]}
        graph = build_graph.build(
            relationship_rows,
            allowed_layers=tuple(config["graph_layers"]),
            layer_weights=config.get("layer_weights"),
            nodes=current_rows.keys(),
            date=date,
            allow_static=allow_static_fixture,
            min_degree=float(config.get("min_degree", 0.0)),
        )
        channels = {}
        for channel in ("momentum", "liquidity", "risk"):
            channels[channel] = spectral.compute(
                {symbol: row.get(channel) for symbol, row in current_rows.items()},
                {symbol: row.get(channel) for symbol, row in previous_rows.items()},
                graph, int(config["propagation_steps"]), min_degree=float(config.get("min_degree", 0.0)),
            )
        lag_m = spectral.robust_z({s: v["neighbor_lag"] for s, v in channels["momentum"].items()})
        lag_l = spectral.robust_z({s: v["neighbor_lag"] for s, v in channels["liquidity"].items()})
        high_m = spectral.robust_z({s: v["high"] for s, v in channels["momentum"].items()})
        low_m = spectral.robust_z({s: v["low"] for s, v in channels["momentum"].items()})
        low_l = spectral.robust_z({s: v["low"] for s, v in channels["liquidity"].items()})
        for symbol in current_rows:
            base = channels["momentum"][symbol]
            status = base["status"]
            if channels["liquidity"][symbol]["status"] != "available":
                status = channels["liquidity"][symbol]["status"]
            if channels["risk"][symbol]["status"] != "available":
                status = channels["risk"][symbol]["status"]
            available = status == "available"
            output.append({
                "date": date, "symbol": symbol, "factor_status": status,
                "degree": base["degree"],
                "graph_diffusion_confirmation": 0.5 * lag_m[symbol] + 0.5 * lag_l[symbol] if available and symbol in lag_m and symbol in lag_l else None,
                "graph_residual_reversal": -high_m[symbol] if available and symbol in high_m else None,
                "price_liquidity_divergence": low_m[symbol] - low_l[symbol] if available and symbol in low_m and symbol in low_l else None,
                "momentum_low": base["low"], "momentum_high": base["high"], "momentum_neighbor_lag": base["neighbor_lag"],
                "liquidity_low": channels["liquidity"][symbol]["low"], "liquidity_neighbor_lag": channels["liquidity"][symbol]["neighbor_lag"],
                "risk_low": channels["risk"][symbol]["low"], "graph_version": graph["version"],
                "graph_fingerprint": graph["fingerprint"], "algorithm_version": spectral.ALGORITHM_VERSION,
            })
        diagnostics.append({"date": date, "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
                            "isolated_node_count": sum(1 for node in graph["nodes"] if graph["degree"].get(node, 0.0) <= 0),
                            "below_min_degree_count": sum(1 for node in graph["nodes"] if 0 < graph["degree"].get(node, 0.0) < float(config.get("min_degree", 0.0))),
                            "graph_fingerprint": graph["fingerprint"], "layers": list(config["graph_layers"]), "config": config})
        previous_rows = current_rows
    return output, diagnostics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("panel", type=Path)
    parser.add_argument("relationships", type=Path)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--allow-static-fixture", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output, diagnostics = build(json.loads(args.panel.read_text(encoding="utf-8")), json.loads(args.relationships.read_text(encoding="utf-8")), config=json.loads(args.config.read_text(encoding="utf-8")), allow_static_fixture=args.allow_static_fixture)
    args.out.write_text(json.dumps({"factor_values": output, "diagnostics": diagnostics}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
