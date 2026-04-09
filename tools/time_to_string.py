#!/usr/bin/env python3

"""Convert numeric time fields into string representations."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from base_script import change_file, load_json


LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert construction and recipe time fields to strings.",
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


def format_recipe_time(turns: int) -> str:
    seconds = turns // 100
    if seconds % 60 == 0:
        return f"{seconds // 60} m"
    return f"{seconds} s"


def gen_new(path: Path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None
    for jo in json_data:
        # We only want JsonObjects
        if isinstance(jo, str):
            continue

        # These need no conversion.
        if isinstance(jo.get("time"), str):
            continue

        # It has to have time.
        if not jo.get("time"):
            continue

        if jo.get("type") == "construction":
            # Convert time to minutes.
            jo["time"] = f"{jo['time']} m"
            change = True

        elif jo.get("type") == "recipe":
            # Convert time from turns to seconds, then minutes.
            jo["time"] = format_recipe_time(jo["time"])
            change = True

    if change:
        LOGGER.debug("Updated time strings in %s", path)
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
