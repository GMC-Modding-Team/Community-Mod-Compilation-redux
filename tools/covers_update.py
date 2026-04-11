#!/usr/bin/env python3
"""
covers_update.py
================
Converts legacy uppercase body-part identifiers in the "covers" key of
Cataclysm: DDA armor JSON entries to their modern lowercase equivalents.

Conversions applied
-------------------
  Paired body parts (expand to left/right):
    ARMS          ->  [ "arm_l",  "arm_r"  ]
    FEET / FOOTS  ->  [ "foot_l", "foot_r" ]
    HANDS         ->  [ "hand_l", "hand_r" ]
    LEGS          ->  [ "leg_l",  "leg_r"  ]

  Single body parts (lowercase):
    EYES          ->  "eyes"
    HEAD          ->  "head"
    MOUTH         ->  "mouth"
    TORSO         ->  "torso"

  _EITHER suffix:
    Any part ending in "_EITHER" has the suffix stripped, the entry is
    expanded as above, and "sided": true is added to the object.

  Unknown values are lowercased and passed through unchanged.

Usage
-----
  # Update a whole mod directory (recursive):
  python3 covers_update.py path/to/mod/

  # Update specific files:
  python3 covers_update.py armor.json helmets.json

  # Mix files and directories:
  python3 covers_update.py armor.json path/to/mod/

  # Preview without writing:
  python3 covers_update.py path/to/mod/ --dry-run

  # Only show files that were actually changed:
  python3 covers_update.py path/to/mod/ --quiet
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    filename="covers_update.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)
LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Body-part mapping
# ---------------------------------------------------------------------------

# Maps a (normalised, _EITHER-stripped) uppercase body-part name to the list
# of modern lowercase identifiers it expands into.
BODYPART_MAP: dict[str, list[str]] = {
    "ARMS":  ["arm_l",  "arm_r"],
    "EYES":  ["eyes"],
    "FEET":  ["foot_l", "foot_r"],
    "FOOTS": ["foot_l", "foot_r"],   # legacy spelling
    "HANDS": ["hand_l", "hand_r"],
    "HEAD":  ["head"],
    "LEGS":  ["leg_l",  "leg_r"],
    "MOUTH": ["mouth"],
    "TORSO": ["torso"],
}


def convert_covers(entry: dict) -> bool:
    """
    Mutate *entry* in-place, converting its "covers" list to modern form.
    Returns True if the entry was changed.
    """
    raw_covers: list = entry.get("covers")
    if not raw_covers:
        return False

    new_covers: list[str] = []
    sided = False

    for bodypart in raw_covers:
        if not isinstance(bodypart, str):
            # Already a non-string value — pass through untouched
            new_covers.append(bodypart)
            continue

        # Strip the _EITHER suffix and flag the item as sided
        if bodypart.upper().endswith("_EITHER"):
            bodypart = bodypart[:-7]
            sided = True

        normalised = bodypart.upper()
        expanded = BODYPART_MAP.get(normalised)

        if expanded:
            new_covers.extend(expanded)
        else:
            # Unknown body part — lowercase and pass through
            new_covers.append(bodypart.lower())

    if new_covers == raw_covers and not sided:
        return False  # Nothing actually changed

    entry["covers"] = new_covers
    if sided:
        entry["sided"] = True
    return True


# ---------------------------------------------------------------------------
# Core per-file logic
# ---------------------------------------------------------------------------

def process_entries(json_data: list) -> bool:
    """
    Iterate over all objects in *json_data* and apply cover conversions.
    Returns True if any entry was changed.
    """
    changed = False
    for entry in json_data:
        if not isinstance(entry, dict):
            continue
        if convert_covers(entry):
            changed = True
    return changed


def process_file(
    path: Path,
    dry_run: bool = False,
    formatter: Path | None = None,
) -> str:
    """
    Load, transform, and write back a single JSON file.
    Returns one of: 'updated', 'unchanged', 'error'
    """
    LOGGER.debug("Processing %s", path)

    try:
        with path.open("r", encoding="utf-8") as fh:
            json_data = json.load(fh)
    except json.JSONDecodeError as exc:
        LOGGER.error("Invalid JSON in %s: %s", path, exc)
        print(f"  [ERROR] Invalid JSON in {path}: {exc}", file=sys.stderr)
        return "error"
    except OSError as exc:
        LOGGER.error("Could not read %s: %s", path, exc)
        print(f"  [ERROR] Could not read {path}: {exc}", file=sys.stderr)
        return "error"

    if not isinstance(json_data, list):
        return "unchanged"

    changed = process_entries(json_data)

    if not changed:
        return "unchanged"

    if dry_run:
        print(f"  [DRY-RUN] Would update: {path}")
        return "updated"

    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(json_data, fh, ensure_ascii=False, indent=2)

        if formatter and formatter.exists():
            subprocess.run([str(formatter), str(path)], check=False)

        LOGGER.info("Updated %s", path)
        print(f"  [UPDATED] {path}")
        return "updated"

    except OSError as exc:
        LOGGER.error("Could not write %s: %s", path, exc)
        print(f"  [ERROR] Could not write {path}: {exc}", file=sys.stderr)
        return "error"


# ---------------------------------------------------------------------------
# Directory walker
# ---------------------------------------------------------------------------

def process_directory(
    directory: Path,
    dry_run: bool = False,
    quiet: bool = False,
    formatter: Path | None = None,
) -> None:
    """Recursively walk *directory* and process every .json file found."""
    counts: dict[str, int] = {"updated": 0, "unchanged": 0, "error": 0, "total": 0}

    for root, dirs, files in os.walk(directory):
        dirs.sort()
        for fname in sorted(files):
            if not fname.lower().endswith(".json"):
                continue
            filepath = Path(root) / fname
            result = process_file(filepath, dry_run=dry_run, formatter=formatter)
            counts["total"] += 1
            counts[result] += 1

    label = "DRY-RUN" if dry_run else "DONE"
    print(
        f"\n[{label}] '{directory}' \u2014 "
        f"{counts['total']} file(s) scanned: "
        f"{counts['updated']} updated, "
        f"{counts['unchanged']} unchanged, "
        f"{counts['error']} error(s)."
    )


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert legacy uppercase body-part identifiers in the 'covers'\n"
            "key of Cataclysm: DDA armor JSON entries to modern lowercase form.\n"
            "Directories are scanned recursively."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        type=Path,
        help="One or more .json files or directories to process.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview which files would be changed without writing anything.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print files that were actually updated.",
    )
    parser.add_argument(
        "--formatter",
        type=Path,
        default=Path(__file__).resolve().parent / "tools" / "format" / "json_formatter.cgi",
        help="Path to the CDDA json_formatter.cgi executable (optional).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    formatter = args.formatter.expanduser()

    mode = "DRY-RUN" if args.dry_run else "UPDATE"
    print(f"=== Covers Updater [{mode}] ===")
    LOGGER.info("Started. mode=%s paths=%s", mode, args.paths)

    for path in args.paths:
        path = path.expanduser()
        if path.is_file():
            if path.suffix.lower() != ".json":
                print(f"  [SKIP] Not a JSON file: {path}", file=sys.stderr)
                continue
            process_file(path, dry_run=args.dry_run, formatter=formatter)
        elif path.is_dir():
            process_directory(
                path,
                dry_run=args.dry_run,
                quiet=args.quiet,
                formatter=formatter,
            )
        else:
            print(f"  [ERROR] Path not found: {path}", file=sys.stderr)
            sys.exit(1)

    print("Done.")
    LOGGER.info("Finished.")


if __name__ == "__main__":
    main()
