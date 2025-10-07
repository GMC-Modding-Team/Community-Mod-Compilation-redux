#!/usr/bin/env python3

"""Convert integer price fields into human readable strings."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from base_script import change_file, load_json


LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert price integers into string representations.",
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


def convert_price(jo: dict, key: str) -> None:
    price = jo[key]
    if price == 0:
        jo[key] = "0 cent"
    elif price % 100000 == 0:
        jo[key] = f"{price // 100000} kUSD"
    elif price % 100 == 0:
        jo[key] = f"{price // 100} USD"
    else:
        jo[key] = f"{price} cent"


def gen_new(path: Path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None
    for jo in json_data:
        # We only want JsonObjects
        if isinstance(jo, str):
            continue
        if isinstance(jo.get("price"), int):
            convert_price(jo, "price")
            change = True

        if isinstance(jo.get("price_postapoc"), int):
            convert_price(jo, "price_postapoc")
            change = True

    if change:
        LOGGER.debug("Updated prices in %s", path)
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
