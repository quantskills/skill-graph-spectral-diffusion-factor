#!/usr/bin/env python3
"""Compute deterministic graph propagation and local residual features."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import build_graph

ALGORITHM_VERSION = "symmetric-graph-diffusion-v1"


def _median(values):
    ordered = sorted(values)
    count = len(ordered)
    if not count:
        return None
    middle = count // 2
    return ordered[middle] if count % 2 else (ordered[middle - 1] + ordered[middle]) / 2.0


def robust_z(values):
    finite = {key: float(value) for key, value in values.items() if value is not None and math.isfinite(float(value))}
    if not finite:
        return {}
    center = _median(list(finite.values()))
    mad = _median([abs(value - center) for value in finite.values()])
    if mad is None or mad <= 1e-12:
        return {key: 0.0 for key in finite}
    scale = 1.4826 * mad
    return {key: (value - center) / scale for key, value in finite.items()}


def propagate(values, graph, steps=1):
    neighbors = build_graph.normalized_neighbors(graph)
    current = dict(values)
    for _ in range(steps):
        current = {
            node: sum(weight * current.get(neighbor, 0.0) for neighbor, weight in neighbors.get(node, []))
            for node in graph.get("nodes", [])
        }
    return current


def compute(current_values, previous_values, graph, steps=2):
    current = robust_z(current_values)
    previous = robust_z(previous_values)
    low = propagate(current, graph, steps)
    one_step_previous = propagate(previous, graph, 1)
    records = {}
    degree = graph.get("degree", {})
    for node in graph.get("nodes", []):
        status = "available"
        if degree.get(node, 0.0) <= 0:
            status = "isolated_node"
        elif node not in current:
            status = "missing_channel"
        elif node not in previous:
            status = "missing_lag"
        value = current.get(node)
        records[node] = {
            "status": status,
            "degree": degree.get(node, 0.0),
            "standardized": value,
            "low": low.get(node) if status != "isolated_node" else None,
            "high": value - low.get(node, 0.0) if value is not None and status != "isolated_node" else None,
            "neighbor_lag": one_step_previous.get(node, 0.0) - value if value is not None and node in previous and status != "isolated_node" else None,
        }
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("current", type=Path)
    parser.add_argument("previous", type=Path)
    parser.add_argument("graph", type=Path)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = compute(
        json.loads(args.current.read_text(encoding="utf-8")),
        json.loads(args.previous.read_text(encoding="utf-8")),
        json.loads(args.graph.read_text(encoding="utf-8")),
        args.steps,
    )
    args.out.write_text(json.dumps({"algorithm_version": ALGORITHM_VERSION, "values": result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
