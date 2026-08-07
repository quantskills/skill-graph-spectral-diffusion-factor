#!/usr/bin/env python3
"""Normalize fixed PandaData factor channels without dynamic substitution."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

CHANNELS = {
    "momentum": ["momentum", "cal_daily_rise"],
    "liquidity": ["liquidity", "cal_10d_120d_turnover_ratio"],
    "risk": ["residual_volatility", "cal_30d_close_std_ratio"],
}


def normalize(rows, channels=None):
    channels = channels or CHANNELS
    output = []
    seen = set()
    for row in rows:
        key = (row.get("date"), row.get("symbol"))
        if not all(key) or key in seen:
            continue
        item = {"date": key[0], "symbol": key[1]}
        for channel, fields in channels.items():
            values = []
            for field in fields:
                value = row.get(field)
                if value is None or not math.isfinite(float(value)):
                    values = []
                    break
                values.append(float(value))
                item[field] = float(value)
            item[channel] = sum(values) / len(values) if len(values) == len(fields) else None
        item["beta"] = float(row["beta"]) if row.get("beta") is not None and math.isfinite(float(row["beta"])) else None
        item["ratio_market_cap_float"] = float(row["ratio_market_cap_float"]) if row.get("ratio_market_cap_float") is not None and math.isfinite(float(row["ratio_market_cap_float"])) else None
        output.append(item)
        seen.add(key)
    return sorted(output, key=lambda row: (row["date"], row["symbol"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    args.out.write_text(json.dumps(normalize(rows), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
