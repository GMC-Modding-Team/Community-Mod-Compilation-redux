#!/usr/bin/env python3

"""Convert string names to object representations."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from base_script import change_file, load_json


LOGGER = logging.getLogger(__name__)

SUPPORTED_TYPES = {
    "AMMO",
    "ARMOR",
    "BATTERY",
    "bionic",
    "BIONIC_ITEM",
    "BOOK",
    "COMESTIBLE",
    "ENGINE",
    "fault",
    "GENERIC",
    "GUN",
    "GUNMOD",
    "item_action",
    "ITEM_CATEGORY",
    "MAGAZINE",
    "map_extra",
    "martial_art",
    "mission_definition",
    "MONSTER",
    "mutation",
    "npc_class",
    "PET_ARMOR",
    "proficiency",
    "skill",
    "SPELL",
    "TOOL",
    "TOOLMOD",
    "TOOL_ARMOR",
    "tool_quality",
    "vehicle_part",
    "vehicle_part_category",
    "vitamin",
    "WHEEL",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ensure that item names are stored as objects.",
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


def to_name_object(entry: str, plural: str | None) -> dict[str, str]:
    if plural:
        if entry == plural:
            return {"str_sp": entry}
        return {"str": entry, "str_pl": plural}
    return {"str": entry}


def gen_new(path: Path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None
    for jo in json_data:
        # We only want JsonObjects
        if isinstance(jo, str):
            continue
        if not jo.get("name"):
            continue
        if isinstance(jo["name"], dict):
            continue
        if jo.get("type") not in SUPPORTED_TYPES:
            continue
        jo["name"] = to_name_object(jo["name"], jo.get("name_plural"))
        if "name_plural" in jo:
            del jo["name_plural"]
        change = True

    if change:
        LOGGER.debug("Updated names in %s", path)
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
