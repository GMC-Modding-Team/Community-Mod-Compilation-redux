#!/usr/bin/env python3

"""Convert integer weight fields into string representations."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from base_script import change_file, load_json


LOGGER = logging.getLogger(__name__)

EXCLUDED_TYPES = {"mapgen", "overmap_terrain", "mod_tileset"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert integer weight fields into string values.",
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
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Optional path to a log file.",
    )
    return parser.parse_args()


def gen_new(path: Path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None
    for jo in json_data:
        # We only want JsonObjects
        if isinstance(jo, str):
            continue
        # And only if they have weight
        if not jo.get("weight"):
            continue
        # Mapgen uses the wrong type of weight, so we exclude it.
        if jo.get("type") in EXCLUDED_TYPES:
            continue
        # We're only looking for integers.
        if isinstance(jo.get("weight"), int):
            jo["weight"] = f"{jo['weight']} g"
            change = True

    if change:
        LOGGER.debug("Updated weights in %s", path)
    return json_data if change else None


def main() -> None:
    args = parse_args()
    log_file = args.log_file.expanduser() if args.log_file else None
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        filename=str(log_file) if log_file else None,
        force=True,
    )
    change_file(args.directory, gen_new)


if __name__ == "__main__":
    main()
