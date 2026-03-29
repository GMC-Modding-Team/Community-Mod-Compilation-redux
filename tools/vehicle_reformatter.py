#!/usr/bin/env python3

"""Reformat vehicle definitions to use compact part arrays."""

from __future__ import annotations

import argparse
import copy
import json
import logging
import subprocess
from pathlib import Path
from typing import Iterable


LOGGER = logging.getLogger(__name__)

LINE_LIMIT = 58


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reformat vehicles using parts arrays.",
    )
    parser.add_argument(
        "vehicle_sources",
        nargs="+",
        type=Path,
        help="One or more JSON files to convert to the new format.",
    )
    parser.add_argument(
        "--formatter",
        type=Path,
        default=Path(__file__).resolve().parent / "format" / "json_formatter.cgi",
        help="Optional path to the json formatter executable.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=str.upper,
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity.",
    )
    return parser.parse_args()


def load_vehicles(paths: Iterable[Path]) -> list[dict]:
    vehicles = []
    for path in paths:
        if path.suffix.lower() != ".json":
            LOGGER.warning("Skipping non-JSON file %s", path)
            continue
        if not path.exists():
            raise FileNotFoundError(f"Failed: could not find {path}")
        with path.open(encoding="utf-8") as resource_file:
            data = json.load(resource_file)
        # FIX 4: a file may contain a single object instead of a list;
        # wrapping it ensures we always iterate over a list of vehicles.
        if isinstance(data, dict):
            data = [data]
        vehicles.extend(data)
    return vehicles


def write_to_json(path: Path, data, formatter: Path) -> None:
    # FIX 3: use indent=2 as a readable fallback when the external formatter
    # is not present, instead of writing a single unformatted line.
    if formatter.exists():
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        subprocess.run([str(formatter), str(path)], check=False)
    else:
        LOGGER.debug("Formatter %s not found; using built-in indent=2 fallback", formatter)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def really_add_parts(
    revised_parts: list[dict],
    xpoint: int,
    ypoint: int,
    xparts: dict,
) -> None:
    y_part = xparts.get(ypoint, {})
    if not y_part:
        return
    pretty_parts = []
    pretty_subparts = []
    temp_parts = ""
    for part in y_part["parts"]:
        # FIX 2: part may be a dict (fuel/ammo entries); use json.dumps for an
        # accurate length measurement instead of f'"{part}"' which would
        # produce "{'part': ...}" and raise a TypeError on dict values.
        part_str = json.dumps(part) if isinstance(part, dict) else f'"{part}"'
        temp_parts += part_str
        if len(temp_parts) > LINE_LIMIT:
            pretty_parts.append(pretty_subparts)
            pretty_subparts = []
            temp_parts = part_str
        temp_parts += ", "
        pretty_subparts.append(part)
    pretty_parts.append(pretty_subparts)

    for subpart_list in pretty_parts:
        if len(subpart_list) > 1:
            rev_part = {"x": xpoint, "y": ypoint, "parts": subpart_list}
        else:
            subpart = subpart_list[0]
            if isinstance(subpart, str):
                rev_part = {"x": xpoint, "y": ypoint, "part": subpart}
            else:
                rev_part = {"x": xpoint, "y": ypoint}
                for key, value in subpart.items():
                    if key in {"x", "y"}:
                        continue
                    rev_part[key] = value
        revised_parts.append(rev_part)


def add_parts(
    revised_parts: list[dict],
    xpoint: int,
    last_center: int,
    new_parts: dict,
) -> int:
    xparts = new_parts.get(xpoint, {})
    if not xparts:
        # FIX 5: preserve last_center instead of resetting to 0 when a column
        # has no parts, so adjacent columns stay correctly aligned.
        return last_center

    min_y = 122
    max_y = -122
    for ypoint in xparts:
        min_y = min(min_y, ypoint)
        max_y = max(max_y, ypoint)

    # Emit the center row first, then walk outward in both directions.
    if xpoint == 0:
        really_add_parts(revised_parts, xpoint, last_center, xparts)
    # FIX 1: was range(min_y - 1, last_center) which started one row too low,
    # skipping the actual min_y row entirely.  Correct start is min_y.
    for ypoint in range(min_y, last_center):
        really_add_parts(revised_parts, xpoint, ypoint, xparts)
    if xpoint != 0:
        really_add_parts(revised_parts, xpoint, last_center, xparts)
    for ypoint in range(last_center + 1, max_y + 1):
        really_add_parts(revised_parts, xpoint, ypoint, xparts)
    return int((min_y + max_y) / 2)


def reformat_vehicle(old_vehicle: dict) -> None:
    min_x = 122
    max_x = -122
    new_parts: dict[int, dict[int, dict[str, list]]] = {}
    for part in old_vehicle.get("parts", []):
        part_x = part.get("x", 0)
        part_y = part.get("y", 0)
        min_x = min(min_x, part_x)
        max_x = max(max_x, part_x)
        new_parts.setdefault(part_x, {})
        new_parts[part_x].setdefault(part_y, {"parts": []})
        if part.get("parts"):
            for new_part in part.get("parts"):
                new_parts[part_x][part_y]["parts"].append(new_part)
        elif part.get("fuel") or part.get("ammo"):
            new_part = copy.deepcopy(part)
            new_part.pop("x", None)
            new_part.pop("y", None)
            new_parts[part_x][part_y]["parts"].append(new_part)
        else:
            new_parts[part_x][part_y]["parts"].append(part.get("part"))

    revised_parts: list[dict] = []
    last_center = add_parts(revised_parts, 0, 0, new_parts)
    for xpoint in range(1, max_x + 1):
        last_center = add_parts(revised_parts, xpoint, last_center, new_parts)
    for xpoint in range(-1, min_x - 1, -1):
        last_center = add_parts(revised_parts, xpoint, last_center, new_parts)

    old_vehicle["parts"] = revised_parts


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), force=True)

    formatter = args.formatter.expanduser()
    for datafile in [path.expanduser() for path in args.vehicle_sources]:
        LOGGER.info("Processing %s", datafile)
        vehicles = load_vehicles([datafile])
        for old_vehicle in vehicles:
            reformat_vehicle(old_vehicle)
        write_to_json(datafile, vehicles, formatter)


if __name__ == "__main__":
    main()