#!/usr/bin/env python3
"""Fail closed when the graph-factor research configuration is incomplete."""
from __future__ import annotations
import argparse, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("config", type=Path)
args = parser.parse_args()
config = json.loads(args.config.read_text(encoding="utf-8"))
required = ["channels", "graph_layers", "propagation_steps", "min_degree"]
missing = [key for key in required if key not in config]
if missing:
    raise SystemExit("freeze blocked: missing " + ", ".join(missing))
if "industry" not in config["graph_layers"]:
    raise SystemExit("freeze blocked: primary graph requires industry layer")
if "correlation" in config["graph_layers"] and config.get("primary_uses_correlation", False):
    raise SystemExit("freeze blocked: correlation edges are diagnostic in v1")
print(json.dumps({"freeze_status": "pass", "algorithm_version": "symmetric-graph-diffusion-v1"}))
