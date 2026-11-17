#!/usr/bin/env python3
"""Compatibility entry point for the Cataclysm 0.I-1 JSON migrator.

The implementation lives in :mod:`update_i1_json`; this name is provided so
the tool can be invoked as ``python tools/update_i_json.py ...`` without
accidentally selecting the legacy/H updater.
"""

from update_i1_json import main


if __name__ == "__main__":
    raise SystemExit(main())
