"""Extract and transform sewing machine recipes."""

from __future__ import annotations

import argparse
import json
import logging
from copy import deepcopy
from pathlib import Path
from typing import Iterable


LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract recipes that require sewing qualities and adapt them.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Source JSON file containing recipe definitions.",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Destination file for the transformed recipes.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=str.upper,
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity.",
    )
    return parser.parse_args()


def requires_sewing(entry: dict) -> bool:
    qualities = entry.get("qualities")
    if not isinstance(qualities, list):
        return False
    for quality in qualities:
        if isinstance(quality, dict) and any(value == "SEW" for value in quality.values()):
            return True
    return False


def extract_recipes(data: Iterable[dict]) -> list[dict]:
    return [
        deepcopy(entry)
        for entry in data
        if isinstance(entry, dict) and requires_sewing(entry)
    ]


def increase_sew_level(entry: dict) -> None:
    for quality in entry.get("qualities", []):
        if isinstance(quality, dict) and "level" in quality:
            quality["level"] = 2


def halve_time(entry: dict) -> None:
    time_value = entry.get("time")
    if isinstance(time_value, (int, float)):
        entry["time"] = int(time_value * 0.5)


def set_subcategory(entry: dict) -> None:
    if "subcategory" in entry:
        entry["subcategory"] = "CSC_SEWING_MACHINE"


def add_suffix(entry: dict) -> None:
    entry["id_suffix"] = "sm"


def transform(entry: dict) -> dict:
    increase_sew_level(entry)
    halve_time(entry)
    set_subcategory(entry)
    add_suffix(entry)
    return entry


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), force=True)

    with args.input.open(encoding="utf-8") as recipejson:
        data_list = json.load(recipejson)

    if not isinstance(data_list, list):
        raise ValueError("Input JSON must contain a list of recipes")

    storage_data = [transform(recipe) for recipe in extract_recipes(data_list)]
    LOGGER.info("Extracted %s recipes", len(storage_data))

    with args.output.open("w", encoding="utf-8") as new_recipe:
        json.dump(storage_data, new_recipe, sort_keys=True, ensure_ascii=False)


if __name__ == "__main__":
    main()
