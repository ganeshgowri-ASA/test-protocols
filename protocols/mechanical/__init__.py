"""Mechanical Testing Protocols"""

from pathlib import Path
import importlib

# Auto-import all protocols in this category
_protocol_dir = Path(__file__).parent
_protocol_files = [f.stem for f in _protocol_dir.glob("*.py") if f.stem != "__init__"]

__all__ = _protocol_files

# Dynamically import all protocol modules
for protocol_file in _protocol_files:
    try:
        importlib.import_module(f".{protocol_file}", package=__package__)
    except Exception as e:
        print(f"Warning: Could not import {protocol_file}: {e}")
