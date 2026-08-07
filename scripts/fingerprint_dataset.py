#!/usr/bin/env python3
"""Print a deterministic SHA-256 fingerprint for JSON content."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
args = parser.parse_args()
value = json.loads(args.input.read_text(encoding="utf-8"))
payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
print(json.dumps({"algorithm": "sha256", "fingerprint": hashlib.sha256(payload).hexdigest()}))
