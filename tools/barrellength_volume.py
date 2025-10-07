#!/usr/bin/env python3

"""Convert numeric volume and barrel length fields to strings."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from base_script import change_file, load_json

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert legacy volume fields to string representations.",
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
        if (
            not isinstance(jo.get("volume"), str)
            and jo.get("volume")
            and jo.get("type") not in {"sound_effect", "speech"}
        ):
            volume = jo["volume"] * 250
            if volume > 10000 and volume % 1000 == 0:
                jo["volume"] = f"{volume // 1000} L"
            else:
                jo["volume"] = f"{volume} ml"
            change = True
        if jo.get("barrel_length"):
            if isinstance(jo["barrel_length"], int):
                barrel_length = jo["barrel_length"] * 250
                jo["barrel_volume"] = f"{barrel_length} ml"
            elif isinstance(jo["barrel_length"], str):
                jo["barrel_volume"] = jo["barrel_length"]
            else:
                LOGGER.debug("Unexpected barrel_length type in %s", path)
            del jo["barrel_length"]
            change = True

    return json_data if change else None


def main() -> None:
    args = parse_args()
    log_file = args.log_file.expanduser() if args.log_file else None
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        filename=str(log_file) if log_file else None,
        force=True,
    )
    LOGGER.info("Starting conversion for directory %s", args.directory)
    change_file(args.directory, gen_new)


if __name__ == "__main__":
    main()
