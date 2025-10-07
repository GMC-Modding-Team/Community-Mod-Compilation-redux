#!/usr/bin/env python3

"""Translate legacy cover entries to modern body part identifiers."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from base_script import change_file, load_json

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert cover strings to modern body part identifiers.",
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


BODY_PART_MAP = {
    "ARMS": ["arm_l", "arm_r"],
    "EYES": ["eyes"],
    "FEET": ["foot_l", "foot_r"],
    "FOOTS": ["foot_l", "foot_r"],
    "HANDS": ["hand_l", "hand_r"],
    "HEAD": ["head"],
    "LEGS": ["leg_l", "leg_r"],
    "MOUTH": ["mouth"],
    "TORSO": ["torso"],
}


def expand_bodypart(bodypart: str, jo: dict) -> list[str]:
    if bodypart.endswith("_EITHER"):
        jo["sided"] = True
        base = bodypart[:-7]
        bodypart = f"{base}s"
    key = bodypart.upper()
    if key not in BODY_PART_MAP and key.endswith("S"):
        key = key[:-1]
    return BODY_PART_MAP.get(key, [bodypart])


def gen_new(path: Path):
    change = False
    json_data = load_json(path)
    if json_data is None:
        return None
    for jo in json_data:
        # We only want JsonObjects
        if isinstance(jo, str):
            continue
        # And only if they have coverage
        covers = jo.get("covers")
        if not covers:
            continue
        joc: list[str] = []
        for bodypart in covers:
            joc.extend(expand_bodypart(bodypart, jo))
        if jo["covers"] == joc:
            continue
        jo["covers"] = joc
        change = True

    if change:
        LOGGER.debug("Updated covers in %s", path)
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
