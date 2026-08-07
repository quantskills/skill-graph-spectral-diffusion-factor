#!/usr/bin/env python3
"""Emit a bounded get_factor query manifest; never performs login or execution."""
from __future__ import annotations
import argparse, json
from pathlib import Path

CORE_FACTORS = ["momentum", "cal_daily_rise", "liquidity", "cal_10d_120d_turnover_ratio", "residual_volatility", "cal_30d_close_std_ratio", "beta"]
parser = argparse.ArgumentParser()
parser.add_argument("--symbols", nargs="+", required=True)
parser.add_argument("--start-date", required=True)
parser.add_argument("--end-date", required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
manifest = {"method": "get_factor", "execution": "not_run", "transport": "direct_panda_data_if_authorized", "mcp_required": False, "params": {"symbol": args.symbols, "start_date": args.start_date, "end_date": args.end_date, "type": "stock", "factors": CORE_FACTORS}}
args.out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
