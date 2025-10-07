#!/usr/bin/env python3

"""Utility for removing obsolete magazine reliability fields."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from base_script import change_file, load_json

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove deprecated reliability fields from magazines.",
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing JSON files to update.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=str.upper,
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity.",
    )
    return parser.parse_args()


def gen_new(path: Path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None

    for jo in json_data:
        if "reliability" in jo and jo.get("type") == "MAGAZINE":
            del jo["reliability"]
            change = True

    if change:
        LOGGER.debug("Removed reliability from %s", path)
    return json_data if change else None


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), force=True)
    change_file(args.directory, gen_new)


if __name__ == "__main__":
    main()
