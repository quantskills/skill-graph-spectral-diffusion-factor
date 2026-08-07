#!/usr/bin/env python3
"""Build a deterministic weighted undirected graph from relationship rows."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

GRAPH_VERSION = "relationship-graph-v1"


def build(rows, allowed_layers=("industry", "concept"), layer_weights=None):
    layer_weights = layer_weights or {"industry": 1.0, "concept": 0.5, "correlation": 0.0}
    edges = defaultdict(float)
    nodes = set()
    for row in rows:
        left = str(row.get("source", ""))
        right = str(row.get("target", ""))
        layer = row.get("layer")
        nodes.update(item for item in (left, right) if item)
        if not left or not right or left == right or layer not in allowed_layers:
            continue
        raw_weight = float(row.get("weight", 1.0))
        coefficient = float(layer_weights.get(layer, 0.0))
        if not math.isfinite(raw_weight) or raw_weight <= 0 or coefficient <= 0:
            continue
        key = tuple(sorted((left, right)))
        edges[key] += raw_weight * coefficient
    edge_rows = [
        {"source": left, "target": right, "weight": weight}
        for (left, right), weight in sorted(edges.items())
    ]
    degree = defaultdict(float)
    for edge in edge_rows:
        degree[edge["source"]] += edge["weight"]
        degree[edge["target"]] += edge["weight"]
    payload = {"version": GRAPH_VERSION, "nodes": sorted(nodes), "edges": edge_rows}
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    payload["degree"] = dict(sorted(degree.items()))
    payload["fingerprint"] = fingerprint
    return payload


def normalized_neighbors(graph):
    degree = graph.get("degree", {})
    neighbors = defaultdict(list)
    for edge in graph.get("edges", []):
        left, right, weight = edge["source"], edge["target"], float(edge["weight"])
        left_degree, right_degree = degree.get(left, 0.0), degree.get(right, 0.0)
        if left_degree <= 0 or right_degree <= 0:
            continue
        normalized = weight / math.sqrt(left_degree * right_degree)
        neighbors[left].append((right, normalized))
        neighbors[right].append((left, normalized))
    return {key: sorted(value) for key, value in neighbors.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--layer", action="append", default=[])
    args = parser.parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    graph = build(rows, tuple(args.layer) if args.layer else ("industry", "concept"))
    args.out.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
