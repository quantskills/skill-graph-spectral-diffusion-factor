#!/usr/bin/env python3
"""Report direct panda_data availability without loading credentials."""
from __future__ import annotations
import importlib.metadata, importlib.util, json

available = importlib.util.find_spec("panda_data") is not None
version = None
if available:
    try:
        version = importlib.metadata.version("panda_data")
    except importlib.metadata.PackageNotFoundError:
        pass
print(json.dumps({"panda_data_importable": available, "panda_data_version": version, "credentials_handled": False, "mcp_required": False}, indent=2))
