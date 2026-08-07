#!/usr/bin/env python3
"""Fingerprint a normalized graph independently of source file paths."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import build_graph

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
args = parser.parse_args()
graph = build_graph.build(json.loads(args.input.read_text(encoding="utf-8")))
print(json.dumps({"graph_version": graph["version"], "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]), "fingerprint": graph["fingerprint"]}))
