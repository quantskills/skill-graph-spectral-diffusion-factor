#!/usr/bin/env python3
"""Build fixed graph-diffusion factor channels from normalized panel rows."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import build_graph
import compute_spectral_features as spectral
import normalize_factor_panel


def build(panel_rows, relationship_rows, steps=2):
    panel = normalize_factor_panel.normalize(panel_rows)
    graph = build_graph.build(relationship_rows)
    by_date = defaultdict(list)
    for row in panel:
        by_date[row["date"]].append(row)
    dates = sorted(by_date)
    output = []
    diagnostics = []
    for index, date in enumerate(dates):
        current_rows = {row["symbol"]: row for row in by_date[date]}
        previous_rows = {row["symbol"]: row for row in by_date[dates[index - 1]]} if index else {}
        channels = {}
        for channel in ("momentum", "liquidity", "risk"):
            channels[channel] = spectral.compute(
                {symbol: row.get(channel) for symbol, row in current_rows.items()},
                {symbol: row.get(channel) for symbol, row in previous_rows.items()},
                graph,
                steps,
            )
        momentum_lag = {symbol: values["neighbor_lag"] for symbol, values in channels["momentum"].items()}
        liquidity_lag = {symbol: values["neighbor_lag"] for symbol, values in channels["liquidity"].items()}
        momentum_high = {symbol: values["high"] for symbol, values in channels["momentum"].items()}
        price_low = {symbol: values["low"] for symbol, values in channels["momentum"].items()}
        liquidity_low = {symbol: values["low"] for symbol, values in channels["liquidity"].items()}
        z_momentum_lag = spectral.robust_z(momentum_lag)
        z_liquidity_lag = spectral.robust_z(liquidity_lag)
        z_momentum_high = spectral.robust_z(momentum_high)
        z_price_low = spectral.robust_z(price_low)
        z_liquidity_low = spectral.robust_z(liquidity_low)
        for symbol in graph["nodes"]:
            base = channels["momentum"][symbol]
            status = base["status"]
            if channels["liquidity"][symbol]["status"] != "available":
                status = channels["liquidity"][symbol]["status"]
            confirmation = None
            reversal = None
            divergence = None
            if symbol in z_momentum_lag and symbol in z_liquidity_lag and status == "available":
                confirmation = 0.5 * z_momentum_lag[symbol] + 0.5 * z_liquidity_lag[symbol]
            if symbol in z_momentum_high and status == "available":
                reversal = -z_momentum_high[symbol]
            if symbol in z_price_low and symbol in z_liquidity_low and status == "available":
                divergence = z_price_low[symbol] - z_liquidity_low[symbol]
            record = {
                "date": date,
                "symbol": symbol,
                "factor_status": status,
                "degree": base["degree"],
                "graph_diffusion_confirmation": confirmation,
                "graph_residual_reversal": reversal,
                "price_liquidity_divergence": divergence,
                "momentum_low": base["low"],
                "momentum_high": base["high"],
                "momentum_neighbor_lag": base["neighbor_lag"],
                "liquidity_low": channels["liquidity"][symbol]["low"],
                "liquidity_neighbor_lag": channels["liquidity"][symbol]["neighbor_lag"],
                "risk_low": channels["risk"][symbol]["low"],
                "graph_version": graph["version"],
                "graph_fingerprint": graph["fingerprint"],
                "algorithm_version": spectral.ALGORITHM_VERSION,
            }
            output.append(record)
        diagnostics.append({
            "date": date,
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "isolated_node_count": sum(1 for node in graph["nodes"] if graph["degree"].get(node, 0.0) <= 0),
            "graph_fingerprint": graph["fingerprint"],
            "layers": ["industry", "concept"],
        })
    return output, diagnostics, graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("panel", type=Path)
    parser.add_argument("relationships", type=Path)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output, diagnostics, graph = build(
        json.loads(args.panel.read_text(encoding="utf-8")),
        json.loads(args.relationships.read_text(encoding="utf-8")),
        args.steps,
    )
    args.out.write_text(json.dumps({"factor_values": output, "diagnostics": diagnostics, "graph": graph}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
