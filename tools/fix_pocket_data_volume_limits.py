#!/usr/bin/env python3
"""
Bump low CDDA pocket_data max_contains_volume values up to the item's own volume.

Use this when items/guns already have pocket_data, but their pocket max_contains_volume
is smaller than the item's top-level "volume".

What it changes:
- Scans JSON files or whole folders recursively.
- Skips any object with a local flags array containing TARDIS.
- Does NOT change the item's own "volume".
- Does NOT look for rigid.
- Does NOT target only 20L/20KG or 30L/30KG.
- For every max_contains_volume inside pocket_data:
    if max_contains_volume is lower than the item's own volume, bump it up.
- By default it sets the pocket to exactly the item volume.
- Optional --safety-gap-ml can set it slightly under the item volume instead.
- max_contains_weight is not changed unless --update-weight is used and that pocket already has max_contains_weight.
- No backups are created.

This script is text-preserving and does not require strict JSON parsing, so it works
better with CDDA-style JSON files that may contain comments/trailing commas.
"""

import argparse
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


LOG_PATH = "bump_low_max_contains_volume_to_item_volume.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
LOGGER = logging.getLogger(__name__)


VOLUME_RE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?)\s*(ml|milliliter|milliliters|l|liter|liters|litre|litres)\s*$",
    re.I,
)
WEIGHT_RE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?)\s*(mg|g|gram|grams|kg|kilogram|kilograms)\s*$",
    re.I,
)
MAX_CONTAINS_VOLUME_RE = re.compile(r'("max_contains_volume"\s*:\s*")([^"]+)(")')
MAX_CONTAINS_WEIGHT_RE = re.compile(r'("max_contains_weight"\s*:\s*")([^"]+)(")')
FLAGS_ARRAY_RE = re.compile(r'"flags"\s*:\s*\[(.*?)\]', re.DOTALL)
# Find pocket_data even in compact one-line JSON.
POCKET_DATA_START_RE = re.compile(r'"pocket_data"\s*:')


@dataclass
class FixStats:
    scanned_objects: int = 0
    fixed_objects: int = 0
    fixed_pockets: int = 0
    fixed_weights: int = 0
    skipped_tardis: int = 0
    skipped_no_item_volume: int = 0
    skipped_no_pocket_data: int = 0
    skipped_no_valid_pocket_volume: int = 0
    skipped_already_ok: int = 0

    def add(self, other: "FixStats") -> None:
        for name in self.__dataclass_fields__:
            setattr(self, name, getattr(self, name) + getattr(other, name))


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Bump existing CDDA pocket_data max_contains_volume values up to the item's own volume, "
            "while skipping objects that locally have the TARDIS flag."
        )
    )
    parser.add_argument("paths", nargs="+", help="JSON files or directories to process.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    parser.add_argument("--quiet", action="store_true", help="Only show updated files and errors.")
    parser.add_argument(
        "--formatter",
        help="Optional path to json_formatter.cgi/json_formatter.exe. Runs after writing each updated file.",
    )
    parser.add_argument(
        "--safety-gap-ml",
        type=int,
        default=0,
        help=(
            "Set pocket volume this many ml below item volume. Default: 0, meaning exactly item volume. "
            "Use 1 if you want it under the item volume."
        ),
    )
    parser.add_argument(
        "--update-weight",
        action="store_true",
        help=(
            "Also update existing max_contains_weight on pockets whose max_contains_volume was bumped. "
            "Missing max_contains_weight fields are left alone. By default weight is left alone."
        ),
    )
    parser.add_argument(
        "--kg-per-liter",
        type=float,
        default=1.0,
        help="Weight capacity to use with --update-weight. Default: 1 kg per 1 L.",
    )
    parser.add_argument(
        "--force-all-pockets",
        action="store_true",
        help=(
            "Change every max_contains_volume in pocket_data to the target value, even if it is already higher. "
            "Default only bumps values that are lower than the target."
        ),
    )
    return parser.parse_args()


def volume_to_ml(value: str) -> Optional[int]:
    """Convert a CDDA volume string like '250 ml', '2 L', or '2L' to whole ml."""
    match = VOLUME_RE.match(value)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2).lower()
    if unit == "ml" or unit.startswith("milliliter"):
        return int(round(number))
    return int(round(number * 1000))


def weight_to_g(value: str) -> Optional[int]:
    """Convert a CDDA weight string like '500 g' or '2 kg' to whole g."""
    match = WEIGHT_RE.match(value)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2).lower()
    if unit == "mg":
        return max(1, int(round(number / 1000)))
    if unit in {"g", "gram", "grams"}:
        return int(round(number))
    return int(round(number * 1000))


def format_volume_ml(ml: int) -> str:
    """Always write whole ml to avoid decimal L values."""
    return f"{max(1, int(round(ml)))} ml"


def format_weight_g(g: int) -> str:
    """Avoid decimal kg. Use kg only for exact whole kg, otherwise g."""
    g = max(1, int(round(g)))
    if g % 1000 == 0:
        return f"{g // 1000} kg"
    return f"{g} g"


def realistic_weight_for_volume(volume_ml: int, kg_per_liter: float) -> str:
    grams = int(round((max(1, volume_ml) / 1000.0) * kg_per_liter * 1000.0))
    return format_weight_g(max(1, grams))


def brace_depth_at(text: str, pos: int) -> int:
    """Return object brace depth at pos, ignoring braces inside strings."""
    depth = 0
    in_string = False
    escaped = False

    for ch in text[:pos]:
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)

    return depth


def find_matching_closer(text: str, open_pos: int, open_char: str, close_char: str) -> Optional[int]:
    """Find the matching closing bracket/brace, ignoring strings."""
    depth = 0
    in_string = False
    escaped = False

    for i in range(open_pos, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return i

    return None


def find_top_level_object_ranges(content: str) -> List[Tuple[int, int]]:
    """
    Find top-level object ranges inside a CDDA JSON file.

    This handles both normal [ { ... }, { ... } ] files and single-object files.
    Nested objects are ignored because their brace depth never returns to zero.
    """
    ranges: List[Tuple[int, int]] = []
    in_string = False
    escaped = False
    depth = 0
    start: Optional[int] = None

    for i, ch in enumerate(content):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    ranges.append((start, i + 1))
                    start = None

    return ranges


def find_top_level_field(block: str, key: str) -> Optional[re.Match]:
    """Find a simple top-level field by key and return the regex match."""
    # Supports both pretty-printed and compact one-line JSON. The value capture is
    # intentionally simple because we only use this for string fields like volume.
    pattern = re.compile(rf'(\s*)"{re.escape(key)}"\s*:\s*("[^"]*"|[^,\n}}\]]+)')
    for match in pattern.finditer(block):
        quote_pos = match.start(0) + len(match.group(1))
        if brace_depth_at(block, quote_pos) == 1:
            return match
    return None


def get_top_level_volume_ml(block: str) -> Optional[int]:
    match = find_top_level_field(block, "volume")
    if not match:
        return None

    value = match.group(2).strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return volume_to_ml(value[1:-1])
    return None


def has_local_tardis_flag(block: str) -> bool:
    """Return True if any local flags array in the object contains TARDIS."""
    for match in FLAGS_ARRAY_RE.finditer(block):
        if re.search(r'"TARDIS"', match.group(1), re.I):
            return True
    return False


def find_pocket_data_range(block: str) -> Optional[Tuple[int, int]]:
    """Find the value range of the top-level pocket_data array in this object block."""
    for match in POCKET_DATA_START_RE.finditer(block):
        quote_pos = match.start(0) + (len(match.group(0)) - len(match.group(0).lstrip()))
        if brace_depth_at(block, quote_pos) != 1:
            continue

        bracket_pos = block.find("[", match.end())
        if bracket_pos == -1:
            return None
        close_pos = find_matching_closer(block, bracket_pos, "[", "]")
        if close_pos is None:
            return None
        return bracket_pos, close_pos + 1

    return None


def find_pocket_object_ranges(pocket_data_text: str) -> List[Tuple[int, int]]:
    """Find direct object ranges inside a pocket_data array."""
    ranges: List[Tuple[int, int]] = []
    in_string = False
    escaped = False
    depth = 0
    start: Optional[int] = None

    for i, ch in enumerate(pocket_data_text):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    ranges.append((start, i + 1))
                    start = None

    return ranges


def bump_volume_in_pocket_text(
    pocket_text: str,
    target_ml: int,
    *,
    force_all_pockets: bool,
    update_weight: bool,
    kg_per_liter: float,
) -> Tuple[str, int, int, bool]:
    """Return (new_text, volume_changes, weight_changes, had_valid_volume)."""
    match = MAX_CONTAINS_VOLUME_RE.search(pocket_text)
    if not match:
        return pocket_text, 0, 0, False

    current_ml = volume_to_ml(match.group(2))
    if current_ml is None:
        return pocket_text, 0, 0, False

    if not force_all_pockets and current_ml >= target_ml:
        return pocket_text, 0, 0, True

    new_volume = format_volume_ml(target_ml)
    new_text = pocket_text[: match.start()] + f'{match.group(1)}{new_volume}{match.group(3)}' + pocket_text[match.end() :]
    volume_changes = 1
    weight_changes = 0

    if update_weight:
        new_weight = realistic_weight_for_volume(target_ml, kg_per_liter)
        weight_match = MAX_CONTAINS_WEIGHT_RE.search(new_text)
        if weight_match:
            new_text = (
                new_text[: weight_match.start()]
                + f'{weight_match.group(1)}{new_weight}{weight_match.group(3)}'
                + new_text[weight_match.end() :]
            )
            weight_changes = 1

    return new_text, volume_changes, weight_changes, True


def bump_pockets_to_item_volume(block: str, item_volume_ml: int, args) -> Tuple[str, int, int, int]:
    """
    Return (fixed_block, changed_pockets, changed_weights, invalid_pocket_volumes).
    """
    target_ml = item_volume_ml - max(0, args.safety_gap_ml)
    if target_ml < 1:
        target_ml = 1

    pocket_range = find_pocket_data_range(block)
    if pocket_range is None:
        return block, 0, 0, 0

    start, end = pocket_range
    pocket_data_text = block[start:end]
    ranges = find_pocket_object_ranges(pocket_data_text)

    changed_pockets = 0
    changed_weights = 0
    invalid_pocket_volumes = 0
    new_pocket_data_text = pocket_data_text

    for p_start, p_end in reversed(ranges):
        pocket_text = new_pocket_data_text[p_start:p_end]
        fixed_pocket, vol_changes, weight_changes, had_valid_volume = bump_volume_in_pocket_text(
            pocket_text,
            target_ml,
            force_all_pockets=args.force_all_pockets,
            update_weight=args.update_weight,
            kg_per_liter=args.kg_per_liter,
        )
        if not had_valid_volume and '"max_contains_volume"' in pocket_text:
            invalid_pocket_volumes += 1
        if fixed_pocket != pocket_text:
            new_pocket_data_text = new_pocket_data_text[:p_start] + fixed_pocket + new_pocket_data_text[p_end:]
            changed_pockets += vol_changes
            changed_weights += weight_changes

    if new_pocket_data_text == pocket_data_text:
        return block, 0, 0, invalid_pocket_volumes

    fixed_block = block[:start] + new_pocket_data_text + block[end:]
    return fixed_block, changed_pockets, changed_weights, invalid_pocket_volumes


def fix_object_block(block: str, args) -> Tuple[str, FixStats]:
    stats = FixStats(scanned_objects=1)

    if '"pocket_data"' not in block or '"max_contains_volume"' not in block:
        stats.skipped_no_pocket_data += 1
        return block, stats

    if has_local_tardis_flag(block):
        stats.skipped_tardis += 1
        return block, stats

    item_volume_ml = get_top_level_volume_ml(block)
    if item_volume_ml is None:
        stats.skipped_no_item_volume += 1
        return block, stats

    fixed, changed_pockets, changed_weights, invalid_pocket_volumes = bump_pockets_to_item_volume(
        block, item_volume_ml, args
    )

    stats.skipped_no_valid_pocket_volume += invalid_pocket_volumes

    if changed_pockets:
        stats.fixed_objects += 1
        stats.fixed_pockets += changed_pockets
        stats.fixed_weights += changed_weights
    else:
        stats.skipped_already_ok += 1

    return fixed, stats


def fix_content(content: str, args) -> Tuple[str, FixStats]:
    ranges = find_top_level_object_ranges(content)
    stats = FixStats()

    if not ranges:
        return content, stats

    new_content = content
    for start, end in reversed(ranges):
        block = new_content[start:end]
        fixed_block, block_stats = fix_object_block(block, args)
        stats.add(block_stats)
        if fixed_block != block:
            new_content = new_content[:start] + fixed_block + new_content[end:]

    return new_content, stats


def process_file(path: str, args) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
    except Exception as exc:
        LOGGER.error("Could not read %s: %s", path, exc)
        return "error"

    if '"pocket_data"' not in original or '"max_contains_volume"' not in original:
        if not args.quiet:
            print(f"[UNCHANGED] {path}")
        return "unchanged"

    fixed, stats = fix_content(original, args)

    if fixed == original:
        if not args.quiet:
            print(
                f"[UNCHANGED] {path} "
                f"objects scanned: {stats.scanned_objects}, "
                f"already ok: {stats.skipped_already_ok}, "
                f"no item volume: {stats.skipped_no_item_volume}, "
                f"TARDIS skipped: {stats.skipped_tardis}"
            )
        return "unchanged"

    if args.dry_run:
        print(
            f"[DRY-RUN] {path} would be updated. "
            f"objects fixed: {stats.fixed_objects}, "
            f"pockets bumped: {stats.fixed_pockets}, "
            f"weights changed: {stats.fixed_weights}, "
            f"TARDIS skipped: {stats.skipped_tardis}"
        )
        return "updated"

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(fixed)

        if args.formatter and os.path.exists(args.formatter):
            subprocess.run([args.formatter, path], capture_output=True, check=False)

        print(
            f"[UPDATED] {path} "
            f"objects fixed: {stats.fixed_objects}, "
            f"pockets bumped: {stats.fixed_pockets}, "
            f"weights changed: {stats.fixed_weights}, "
            f"TARDIS skipped: {stats.skipped_tardis}"
        )
        return "updated"
    except Exception as exc:
        LOGGER.error("Could not write %s: %s", path, exc)
        return "error"


def process_path(path: str, args) -> Dict[str, int]:
    totals = {"scanned": 0, "updated": 0, "unchanged": 0, "error": 0}

    if os.path.isfile(path):
        if path.lower().endswith(".json"):
            totals["scanned"] += 1
            result = process_file(path, args)
            totals[result] += 1
        elif not args.quiet:
            print(f"[SKIPPED] {path} is not a .json file")
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for filename in sorted(files):
                if filename.lower().endswith(".json"):
                    full_path = os.path.join(root, filename)
                    totals["scanned"] += 1
                    result = process_file(full_path, args)
                    totals[result] += 1
    else:
        LOGGER.error("Path does not exist: %s", path)
        totals["error"] += 1

    return totals


def main() -> None:
    args = parse_args()

    if args.safety_gap_ml < 0:
        raise SystemExit("--safety-gap-ml cannot be negative")
    if args.kg_per_liter <= 0:
        raise SystemExit("--kg-per-liter must be greater than 0")

    totals = {"scanned": 0, "updated": 0, "unchanged": 0, "error": 0}

    print(
        "=== CDDA Bump Low Pocket max_contains_volume to Item Volume "
        f"{'[DRY-RUN]' if args.dry_run else '[UPDATE]'} ==="
    )
    print(
        "Mode: bump low max_contains_volume values. "
        "Objects with local TARDIS flag are skipped. "
        f"Safety gap: {args.safety_gap_ml} ml. "
        f"Update weight: {'yes' if args.update_weight else 'no'}."
    )

    for path in args.paths:
        path_totals = process_path(path, args)
        for key in totals:
            totals[key] += path_totals[key]

    print(
        f"\nDone. {totals['scanned']} file(s) scanned: "
        f"{totals['updated']} updated, "
        f"{totals['unchanged']} unchanged, "
        f"{totals['error']} error(s)."
    )
    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
