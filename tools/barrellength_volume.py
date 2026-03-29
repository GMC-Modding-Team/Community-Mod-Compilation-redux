#!/usr/bin/env python3
"""
barrellength_volume.py
======================
Converts legacy numeric "volume" and "barrel_length" values in Cataclysm: DDA
JSON files to their modern string equivalents.

Conversions applied
-------------------
  "volume": N          ->  "volume": "N*250 ml"   (or "N/4 L" when >= 10 L and divisible by 1000)
  "volume": 0          ->  "volume": "1 ml"        (intentional edge case per CDDA spec)
  "barrel_length": N   ->  "barrel_volume": "N*250 ml"   (integer input)
  "barrel_length": "x" ->  "barrel_volume": "x"          (string passthrough)
  The original "barrel_length" key is deleted in both cases.

Skipped entries
---------------
  - Entries whose "volume" is already a string (already converted)
  - Entries with "type": "sound_effect" or "type": "speech"  (volume = loudness, not size)

Usage
-----
  # Update a whole mod directory (recursive):
  python3 barrellength_volume.py path/to/mod/

  # Update specific files:
  python3 barrellength_volume.py guns.json armor.json

  # Mix files and directories:
  python3 barrellength_volume.py guns.json path/to/mod/

  # Preview without writing:
  python3 barrellength_volume.py path/to/mod/ --dry-run

  # Only show files that were actually changed:
  python3 barrellength_volume.py path/to/mod/ --quiet
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
    filename="barrellength_volume.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Volume helpers
# ---------------------------------------------------------------------------

VOLUME_SKIP_TYPES = {"sound_effect", "speech"}


def _convert_volume(raw: int) -> str:
    """Convert a legacy integer volume to its modern string form."""
    if raw == 0:
        return "1 ml"           # intentional per CDDA spec
    ml = raw * 250
    if ml >= 10000 and ml % 1000 == 0:
        return f"{ml // 1000} L"
    return f"{ml} ml"


def _convert_barrel(raw: int | str) -> str:
    """Convert a legacy barrel_length value to a barrel_volume string."""
    if isinstance(raw, str):
        return raw              # already a string — pass straight through
    return f"{raw * 250} ml"


# ---------------------------------------------------------------------------
# Core per-file logic
# ---------------------------------------------------------------------------

def process_entries(json_data: list) -> bool:
    """
    Mutate *json_data* in-place, applying volume and barrel_length conversions.
    Returns True if any entry was changed.
    """
    changed = False

    for entry in json_data:
        # Only process JSON objects; skip bare strings or other primitives
        if not isinstance(entry, dict):
            continue

        entry_type = entry.get("type", "")

        # --- volume ---
        raw_vol = entry.get("volume")
        if (
            raw_vol is not None
            and not isinstance(raw_vol, str)   # skip already-converted strings
            and entry_type not in VOLUME_SKIP_TYPES
        ):
            entry["volume"] = _convert_volume(int(raw_vol))
            changed = True

        # --- barrel_length -> barrel_volume ---
        raw_barrel = entry.get("barrel_length")
        if raw_barrel is not None:
            entry["barrel_volume"] = _convert_barrel(raw_barrel)
            del entry["barrel_length"]
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
    LOGGER.info("Processing %s", path)

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

    # CDDA files are always a list at the top level; skip anything else
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

        # Run the CDDA formatter if available
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
            "Convert legacy numeric 'volume' and 'barrel_length' values\n"
            "in Cataclysm: DDA JSON files to modern string format.\n"
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
    print(f"=== Barrel Length / Volume Converter [{mode}] ===")
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