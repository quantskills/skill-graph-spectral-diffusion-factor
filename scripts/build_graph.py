#!/usr/bin/env python3
"""Build a deterministic point-in-time weighted undirected graph."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

GRAPH_VERSION = "relationship-graph-v2"


def _active_rows(rows, date, allow_static=False):
    latest = {}
    for row in rows:
        effective = row.get("effective_date")
        if effective is None:
            if not allow_static:
                raise ValueError("formal graph rows require effective_date")
            effective = "00000000"
        if effective > date:
            continue
        key = (str(row.get("source", "")), str(row.get("target", "")), str(row.get("layer", "")))
        if effective >= latest.get(key, ("", {}))[0]:
            latest[key] = (effective, row)
    return [row for _, row in latest.values() if row.get("active", True)]


def build(rows, allowed_layers=("industry", "concept"), layer_weights=None,
          nodes=None, date=None, allow_static=False, min_degree=0.0):
    if date is not None:
        rows = _active_rows(rows, date, allow_static=allow_static)
    layer_weights = layer_weights or {"industry": 1.0, "concept": 0.5, "correlation": 0.0}
    node_set = set(str(node) for node in nodes) if nodes is not None else set()
    edges = defaultdict(float)
    for row in rows:
        left, right = str(row.get("source", "")), str(row.get("target", ""))
        layer = row.get("layer")
        if nodes is None:
            node_set.update(item for item in (left, right) if item)
        if not left or not right or left == right or layer not in allowed_layers:
            continue
        if nodes is not None and (left not in node_set or right not in node_set):
            continue
        raw_weight = float(row.get("weight", 1.0))
        coefficient = float(layer_weights.get(layer, 0.0))
        if not math.isfinite(raw_weight) or raw_weight <= 0 or coefficient <= 0:
            continue
        key = tuple(sorted((left, right)))
        edges[key] += raw_weight * coefficient
    edge_rows = [{"source": left, "target": right, "weight": weight} for (left, right), weight in sorted(edges.items())]
    degree = defaultdict(float)
    for edge in edge_rows:
        degree[edge["source"]] += edge["weight"]
        degree[edge["target"]] += edge["weight"]
    payload = {"version": GRAPH_VERSION, "date": date, "nodes": sorted(node_set), "edges": edge_rows,
               "min_degree": min_degree, "active_nodes": sorted(node for node in node_set if degree.get(node, 0.0) >= min_degree)}
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
    parser.add_argument("--date", required=True)
    parser.add_argument("--node", action="append", required=True)
    parser.add_argument("--layer", action="append", default=[])
    parser.add_argument("--allow-static-fixture", action="store_true")
    parser.add_argument("--min-degree", type=float, default=0.0)
    args = parser.parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    graph = build(rows, tuple(args.layer) if args.layer else ("industry", "concept"), nodes=args.node, date=args.date, allow_static=args.allow_static_fixture, min_degree=args.min_degree)
    args.out.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
