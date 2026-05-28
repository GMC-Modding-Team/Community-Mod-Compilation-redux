#!/usr/bin/env python3
"""
Fix CDDA pocket_data entries that use a target max_contains_volume / max_contains_weight
pair, without relying on the TARDIS flag.

Default target is:
    max_contains_volume: 20 L
    max_contains_weight: 20 kg

What it changes:
- Skips any item/object with flags containing TARDIS.
- Does NOT change the item's own "volume".
- Finds pockets with the target max_contains_volume, and with target max_contains_weight
  when that weight is present.
- If the pocket's target volume is too large for the item volume, lowers
  max_contains_volume to item volume minus a safety gap.
- Only changes max_contains_weight when max_contains_volume was changed on that same pocket.
- Writes volume as whole ml.
- Writes weight as whole kg only when exact, otherwise whole g. No decimal kg.
- No backups are created.
"""

import argparse
import json
import logging
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

LOG_PATH = "fix_20l_20kg_pocket_limits_no_tardis.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
LOGGER = logging.getLogger(__name__)

VOLUME_RE = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*(ml|milliliter|milliliters|l|liter|liters|litre|litres)\s*$", re.I)
WEIGHT_RE = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*(mg|g|gram|grams|kg|kilogram|kilograms)\s*$", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fix existing CDDA pocket_data max_contains_volume/max_contains_weight "
            "for target 20L/20KG-style pockets, skipping TARDIS items."
        )
    )
    parser.add_argument("paths", nargs="+", help="JSON files or directories to process.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    parser.add_argument("--quiet", action="store_true", help="Only print updated files and errors.")
    parser.add_argument(
        "--target-volume",
        default="20 L",
        help='Pocket max_contains_volume to look for. Default: "20 L". Accepts 20L, 20000 ml, etc.',
    )
    parser.add_argument(
        "--target-weight",
        default="20 kg",
        help='Pocket max_contains_weight to look for. Default: "20 kg". Accepts 20KG, 20000 g, etc.',
    )
    parser.add_argument(
        "--ignore-target-weight",
        action="store_true",
        help="Match target max_contains_volume even if max_contains_weight is different.",
    )
    parser.add_argument(
        "--safety-gap-ml",
        type=int,
        default=1,
        help="How far under item volume the pocket volume should be. Default: 1 ml.",
    )
    parser.add_argument(
        "--kg-per-liter",
        type=float,
        default=1.0,
        help="Realistic weight capacity to use after lowering volume. Default: 1 kg per 1 L.",
    )
    return parser.parse_args()


def parse_volume_to_ml(value: Any) -> Optional[int]:
    """Parse CDDA volume strings into whole ml. Numeric legacy values are treated as ml."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if not isinstance(value, str):
        return None

    m = VOLUME_RE.match(value)
    if not m:
        return None

    number = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "ml" or unit.startswith("milliliter"):
        return int(round(number))
    return int(round(number * 1000))


def parse_weight_to_g(value: Any) -> Optional[int]:
    """Parse CDDA weight strings into whole grams. Numeric legacy values are treated as grams."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if not isinstance(value, str):
        return None

    m = WEIGHT_RE.match(value)
    if not m:
        return None

    number = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "mg":
        return max(1, int(round(number / 1000)))
    if unit in {"g", "gram", "grams"}:
        return int(round(number))
    return int(round(number * 1000))


def format_volume_ml(ml: int) -> str:
    """Always write whole ml, never decimal L."""
    return f"{max(0, int(ml))} ml"


def format_weight_g(g: int) -> str:
    """Avoid decimal kg. Use kg only for exact whole kg, otherwise g."""
    g = max(1, int(round(g)))
    if g % 1000 == 0:
        return f"{g // 1000} kg"
    return f"{g} g"


def realistic_weight_for_volume(volume_ml: int, kg_per_liter: float) -> str:
    grams = int(round((max(1, volume_ml) / 1000.0) * kg_per_liter * 1000.0))
    return format_weight_g(max(1, grams))


def has_tardis_flag(obj: Dict[str, Any]) -> bool:
    flags = obj.get("flags")
    return isinstance(flags, list) and any(str(flag).upper() == "TARDIS" for flag in flags)


def iter_json_files(paths: Iterable[str]) -> Iterable[str]:
    for path in paths:
        if os.path.isfile(path):
            if path.lower().endswith(".json"):
                yield path
            continue

        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for filename in sorted(files):
                    if filename.lower().endswith(".json"):
                        yield os.path.join(root, filename)


def object_name(obj: Dict[str, Any]) -> str:
    value = obj.get("id") or obj.get("abstract") or obj.get("copy-from") or obj.get("type") or "<unknown>"
    return str(value)


def pocket_matches_target(
    pocket: Dict[str, Any],
    target_volume_ml: int,
    target_weight_g: int,
    ignore_target_weight: bool,
) -> bool:
    pocket_volume_ml = parse_volume_to_ml(pocket.get("max_contains_volume"))
    if pocket_volume_ml != target_volume_ml:
        return False

    if ignore_target_weight:
        return True

    # If the weight field is missing, still allow the volume repair and add a matching realistic weight.
    if "max_contains_weight" not in pocket:
        return True

    pocket_weight_g = parse_weight_to_g(pocket.get("max_contains_weight"))
    return pocket_weight_g == target_weight_g


def fix_object(
    obj: Dict[str, Any],
    *,
    target_volume_ml: int,
    target_weight_g: int,
    ignore_target_weight: bool,
    safety_gap_ml: int,
    kg_per_liter: float,
    file_path: str,
) -> Tuple[int, int, int]:
    """
    Return (pockets_checked, pockets_changed, pockets_skipped).
    """
    if has_tardis_flag(obj):
        return (0, 0, 0)

    pocket_data = obj.get("pocket_data")
    if not isinstance(pocket_data, list):
        return (0, 0, 0)

    item_volume_ml = parse_volume_to_ml(obj.get("volume"))
    if item_volume_ml is None:
        # Cannot safely calculate the item's volume limit, so do not guess.
        return (0, 0, 1)

    safe_max_ml = item_volume_ml - max(1, safety_gap_ml)
    if safe_max_ml < 1:
        return (0, 0, 1)

    checked = changed = skipped = 0

    for pocket in pocket_data:
        if not isinstance(pocket, dict):
            continue

        if not pocket_matches_target(pocket, target_volume_ml, target_weight_g, ignore_target_weight):
            continue

        checked += 1
        current_volume_ml = parse_volume_to_ml(pocket.get("max_contains_volume"))
        if current_volume_ml is None:
            skipped += 1
            continue

        # Only repair pockets whose target volume is outside the item volume limit.
        if current_volume_ml <= safe_max_ml:
            continue

        old_volume = pocket.get("max_contains_volume")
        old_weight = pocket.get("max_contains_weight")
        pocket["max_contains_volume"] = format_volume_ml(safe_max_ml)

        # Important: weight is changed only because this same pocket's volume changed.
        pocket["max_contains_weight"] = realistic_weight_for_volume(safe_max_ml, kg_per_liter)
        changed += 1

        LOGGER.info(
            "%s: %s pocket changed: max_contains_volume %r -> %r, max_contains_weight %r -> %r",
            file_path,
            object_name(obj),
            old_volume,
            pocket.get("max_contains_volume"),
            old_weight,
            pocket.get("max_contains_weight"),
        )

    return (checked, changed, skipped)


def walk_and_fix(
    node: Any,
    *,
    target_volume_ml: int,
    target_weight_g: int,
    ignore_target_weight: bool,
    safety_gap_ml: int,
    kg_per_liter: float,
    file_path: str,
) -> Tuple[int, int, int]:
    checked = changed = skipped = 0

    if isinstance(node, dict):
        a, b, c = fix_object(
            node,
            target_volume_ml=target_volume_ml,
            target_weight_g=target_weight_g,
            ignore_target_weight=ignore_target_weight,
            safety_gap_ml=safety_gap_ml,
            kg_per_liter=kg_per_liter,
            file_path=file_path,
        )
        checked += a
        changed += b
        skipped += c

        for value in node.values():
            a, b, c = walk_and_fix(
                value,
                target_volume_ml=target_volume_ml,
                target_weight_g=target_weight_g,
                ignore_target_weight=ignore_target_weight,
                safety_gap_ml=safety_gap_ml,
                kg_per_liter=kg_per_liter,
                file_path=file_path,
            )
            checked += a
            changed += b
            skipped += c

    elif isinstance(node, list):
        for value in node:
            a, b, c = walk_and_fix(
                value,
                target_volume_ml=target_volume_ml,
                target_weight_g=target_weight_g,
                ignore_target_weight=ignore_target_weight,
                safety_gap_ml=safety_gap_ml,
                kg_per_liter=kg_per_liter,
                file_path=file_path,
            )
            checked += a
            changed += b
            skipped += c

    return checked, changed, skipped


def process_file(path: str, args: argparse.Namespace, target_volume_ml: int, target_weight_g: int) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            original_content = f.read()
    except Exception as exc:
        LOGGER.error("Could not read %s: %s", path, exc)
        return "error"

    # Cheap skip for speed. Case-insensitive so 20KG/20kg variants are not missed.
    if "pocket_data" not in original_content:
        if not args.quiet:
            print(f"[UNCHANGED] {path}")
        return "unchanged"

    try:
        data = json.loads(original_content)
    except Exception as exc:
        LOGGER.error("Could not parse %s as strict JSON: %s", path, exc)
        return "error"

    checked, changed, skipped = walk_and_fix(
        data,
        target_volume_ml=target_volume_ml,
        target_weight_g=target_weight_g,
        ignore_target_weight=args.ignore_target_weight,
        safety_gap_ml=args.safety_gap_ml,
        kg_per_liter=args.kg_per_liter,
        file_path=path,
    )

    if changed == 0:
        if not args.quiet:
            extra = f"; checked {checked} target pocket(s)" if checked else ""
            if skipped:
                extra += f"; skipped {skipped} object(s) without usable volume"
            print(f"[UNCHANGED] {path}{extra}")
        return "unchanged"

    new_content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    if args.dry_run:
        print(f"[DRY-RUN] {path} would be updated ({changed} pocket(s) changed).")
        return "updated"

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as exc:
        LOGGER.error("Could not write %s: %s", path, exc)
        return "error"

    print(f"[UPDATED] {path} ({changed} pocket(s) changed).")
    return "updated"


def main() -> None:
    args = parse_args()

    target_volume_ml = parse_volume_to_ml(args.target_volume)
    target_weight_g = parse_weight_to_g(args.target_weight)
    if target_volume_ml is None:
        raise SystemExit(f"Could not parse --target-volume: {args.target_volume!r}")
    if target_weight_g is None:
        raise SystemExit(f"Could not parse --target-weight: {args.target_weight!r}")
    if args.safety_gap_ml < 1:
        raise SystemExit("--safety-gap-ml must be at least 1")
    if args.kg_per_liter <= 0:
        raise SystemExit("--kg-per-liter must be greater than 0")

    stats = {"scanned": 0, "updated": 0, "unchanged": 0, "error": 0}

    mode = "[DRY-RUN]" if args.dry_run else "[UPDATE]"
    print(f"=== CDDA 20L/20KG Pocket Limit Fixer {mode} ===")
    print(
        f"Target: max_contains_volume={format_volume_ml(target_volume_ml)}, "
        f"max_contains_weight={format_weight_g(target_weight_g)}, "
        f"skip flags containing TARDIS"
    )

    for file_path in iter_json_files(args.paths):
        stats["scanned"] += 1
        result = process_file(file_path, args, target_volume_ml, target_weight_g)
        stats[result] += 1

    print(
        f"\nDone. {stats['scanned']} file(s) scanned: "
        f"{stats['updated']} updated, "
        f"{stats['unchanged']} unchanged, "
        f"{stats['error']} error(s)."
    )
    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
