#!/usr/bin/env python3
"""
remove_magazine_reliability.py
===============================
Removes the deprecated "reliability" key from all MAGAZINE type entries
in a directory of Cataclysm: DDA JSON files.

Usage
-----
  # Remove "reliability" from all JSON files in a directory (recursive):
  python3 remove_magazine_reliability.py path/to/mod/

  # Preview changes without writing anything:
  python3 remove_magazine_reliability.py path/to/mod/ --dry-run

  # Silence unchanged-file noise, only show updated files:
  python3 remove_magazine_reliability.py path/to/mod/ --quiet
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def process_file(path: Path, dry_run: bool = False, formatter: Path | None = None) -> str:
    """
    Load a JSON file, strip "reliability" from every MAGAZINE entry,
    and write it back if anything changed.

    Returns one of: 'updated', 'unchanged', 'error'
    """
    try:
        with path.open("r", encoding="utf-8") as fh:
            json_data = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"  [ERROR] Invalid JSON in {path}: {exc}", file=sys.stderr)
        return "error"
    except OSError as exc:
        print(f"  [ERROR] Could not read {path}: {exc}", file=sys.stderr)
        return "error"

    # json_data must be a list of objects for CDDA files
    if not isinstance(json_data, list):
        return "unchanged"

    changed = False
    for entry in json_data:
        if isinstance(entry, dict) and entry.get("type") == "MAGAZINE" and "reliability" in entry:
            del entry["reliability"]
            changed = True

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

        print(f"  [UPDATED] {path}")
        return "updated"
    except OSError as exc:
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
        dirs.sort()  # alphabetical traversal
        for fname in sorted(files):
            if not fname.lower().endswith(".json"):
                continue
            filepath = Path(root) / fname
            result = process_file(filepath, dry_run=dry_run, formatter=formatter)
            counts["total"] += 1
            counts[result] += 1

            if quiet and result == "unchanged":
                continue  # suppress unchanged noise in quiet mode

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
            'Remove the deprecated "reliability" key from MAGAZINE entries\n'
            "in Cataclysm: DDA JSON files. Directories are scanned recursively."
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
    print(f"=== Remove Magazine Reliability [{mode}] ===")

    for path in args.paths:
        path = path.expanduser()
        if path.is_file():
            if not path.suffix.lower() == ".json":
                print(f"  [SKIP] Not a JSON file: {path}", file=sys.stderr)
                continue
            process_file(path, dry_run=args.dry_run, formatter=formatter)
        elif path.is_dir():
            process_directory(path, dry_run=args.dry_run, quiet=args.quiet, formatter=formatter)
        else:
            print(f"  [ERROR] Path not found: {path}", file=sys.stderr)
            sys.exit(1)

    print("Done.")


if __name__ == "__main__":
    main()