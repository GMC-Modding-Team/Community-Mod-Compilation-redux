#!/usr/bin/env python3
import argparse
import json
import os
import re
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("storage_to_pocket_data.log"),
        logging.StreamHandler()
    ]
)
LOGGER = logging.getLogger(__name__)

VOLUME_RE = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*(ml|l|L)\s*$')
STORAGE_RE = re.compile(r'^(\s*)"storage"\s*:\s*"([^"]+)"', re.MULTILINE)
VOLUME_FIELD_RE = re.compile(r'^(\s*)"volume"\s*:\s*"([^"]+)"', re.MULTILINE)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Convert legacy 'storage' to modern 'pocket_data' in CDDA JSON. "
            "Also raises item volume when needed so the converted container does not need TARDIS."
        )
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to process.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to files.")
    parser.add_argument("--quiet", action="store_true", help="Only show updated files and errors.")
    parser.add_argument("--formatter", help="Path to json_formatter.cgi/json_formatter.exe (optional).")
    parser.add_argument(
        "--no-volume-fix",
        action="store_true",
        help="Only replace storage with pocket_data. Do not change/insert item volume.",
    )
    parser.add_argument(
        "--volume-padding-ml",
        type=int,
        default=10,
        help=(
            "Extra outside volume added above max_contains_volume when volume must be raised. "
            "Default: 10 ml."
        ),
    )
    parser.add_argument(
        "--remove-tardis",
        action="store_true",
        help="Also remove the TARDIS flag from converted objects if it is present.",
    )
    return parser.parse_args()


def volume_to_ml(volume_str):
    """Return volume in ml, or None if the string is not a normal CDDA ml/L volume."""
    m = VOLUME_RE.match(volume_str)
    if not m:
        return None

    val = float(m.group(1))
    unit = m.group(2).lower()
    return int(round(val if unit == "ml" else val * 1000))


def format_volume_ml(ml):
    """Format volume safely for CDDA JSON."""
    ml = int(round(ml))
    if ml <= 0:
        return "1 ml"
    if ml % 1000 == 0:
        return f"{ml // 1000} L"
    return f"{ml} ml"


def get_weight_for_volume(volume_str):
    """
    Estimate a reasonable max_contains_weight based on volume.
    Rule of thumb: 1L ~ 4kg for typical CDDA containers.
    """
    volume_ml = volume_to_ml(volume_str)
    if volume_ml is None:
        return "2 kg"  # Default fallback

    liters = volume_ml / 1000.0
    weight_kg = max(1.0, round(liters * 4.0, 1))

    if weight_kg == int(weight_kg):
        return f"{int(weight_kg)} kg"
    return f"{weight_kg} kg"


def find_top_level_object_ranges(content):
    """
    Find root JSON object ranges while ignoring braces inside strings.
    CDDA JSON files are usually arrays of objects; this also handles a single root object.
    """
    ranges = []
    in_string = False
    escaped = False
    depth = 0
    start = None

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


def build_pocket_data(volume_str):
    weight_str = get_weight_for_volume(volume_str)
    return [
        {
            "pocket_type": "CONTAINER",
            "rigid": True,
            "max_contains_volume": volume_str,
            "max_contains_weight": weight_str,
        }
    ]


def replace_storage_fields(block):
    """Replace all top-level-looking storage fields in an object block with pocket_data."""

    def replace_storage(match):
        indent = match.group(1)
        volume_str = match.group(2)
        pd_json = json.dumps(build_pocket_data(volume_str), indent=2)
        indented_pd = pd_json.replace('\n', '\n' + indent)
        return f'{indent}"pocket_data": {indented_pd}'

    return STORAGE_RE.sub(replace_storage, block)


def highest_storage_volume_ml(block):
    values = []
    for match in STORAGE_RE.finditer(block):
        volume_ml = volume_to_ml(match.group(2))
        if volume_ml is not None:
            values.append(volume_ml)
    return max(values) if values else None


def raise_item_volume_if_needed(block, storage_ml, padding_ml):
    """
    Make the item's outside volume larger than the new container capacity.
    This avoids needing the TARDIS flag for normal containers.
    """
    if storage_ml is None:
        return block, False

    safe_volume_ml = storage_ml + max(0, int(padding_ml))
    volume_match = VOLUME_FIELD_RE.search(block)

    if volume_match:
        current_ml = volume_to_ml(volume_match.group(2))
        if current_ml is not None and current_ml > storage_ml:
            return block, False

        indent = volume_match.group(1)
        new_volume = format_volume_ml(safe_volume_ml)
        start, end = volume_match.span()
        replacement = f'{indent}"volume": "{new_volume}"'
        return block[:start] + replacement + block[end:], True

    # No local volume exists, probably inherited through copy-from. Add an explicit safe volume
    # before pocket_data if possible, otherwise after id/copy-from/type, otherwise after the opening brace.
    new_volume = format_volume_ml(safe_volume_ml)
    pocket_match = re.search(r'^(\s*)"pocket_data"\s*:', block, re.MULTILINE)
    if pocket_match:
        insert_at = pocket_match.start()
        indent = pocket_match.group(1)
        return block[:insert_at] + f'{indent}"volume": "{new_volume}",\n' + block[insert_at:], True

    anchor_match = None
    for key in ("copy-from", "name", "id", "type"):
        matches = list(re.finditer(rf'^\s*"{re.escape(key)}"\s*:.*?,?\s*$', block, re.MULTILINE))
        if matches:
            anchor_match = matches[-1]
            break

    if anchor_match:
        line = anchor_match.group(0)
        indent_match = re.match(r'^(\s*)', line)
        indent = indent_match.group(1) if indent_match else "  "
        insert_at = anchor_match.end()
        return block[:insert_at] + f'\n{indent}"volume": "{new_volume}",' + block[insert_at:], True

    first_newline = block.find("\n")
    if first_newline != -1:
        return block[:first_newline + 1] + f'  "volume": "{new_volume}",\n' + block[first_newline + 1:], True

    return block, False


def remove_tardis_flag(block):
    """Remove TARDIS from simple JSON flag arrays in a converted object."""
    before = block

    # Remove TARDIS when it is followed by another flag.
    block = re.sub(r'"TARDIS"\s*,\s*', "", block)
    # Remove TARDIS when it is the last flag after another flag.
    block = re.sub(r',\s*"TARDIS"', "", block)
    # Remove TARDIS if it was the only flag.
    block = re.sub(r'"TARDIS"', "", block)

    # Clean up any empty flags array left as [  ] or multi-line empty brackets.
    block = re.sub(r'"flags"\s*:\s*\[\s*\]\s*,?\n?', "", block)
    return block, block != before


def fix_storage(content, *, fix_volume=True, padding_ml=10, remove_tardis=False):
    """
    Find legacy "storage": "X" and replace it with pocket_data.
    If fix_volume is enabled, also ensure item volume is bigger than pocket capacity.
    """
    object_ranges = find_top_level_object_ranges(content)

    # If the scanner cannot find useful object ranges, fall back to the old whole-file replacement.
    if not object_ranges:
        return replace_storage_fields(content), {"storage": 0, "volume": 0, "tardis": 0}

    stats = {"storage": 0, "volume": 0, "tardis": 0}
    new_content = content

    for start, end in reversed(object_ranges):
        block = new_content[start:end]
        if '"storage"' not in block:
            continue

        storage_count = len(STORAGE_RE.findall(block))
        storage_ml = highest_storage_volume_ml(block)

        changed_block = replace_storage_fields(block)
        if changed_block != block:
            stats["storage"] += storage_count

        if fix_volume:
            changed_block, volume_changed = raise_item_volume_if_needed(
                changed_block, storage_ml, padding_ml
            )
            if volume_changed:
                stats["volume"] += 1

        if remove_tardis:
            changed_block, tardis_changed = remove_tardis_flag(changed_block)
            if tardis_changed:
                stats["tardis"] += 1

        new_content = new_content[:start] + changed_block + new_content[end:]

    return new_content, stats


def process_file(path, args):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        LOGGER.error(f"Could not read {path}: {e}")
        return "error"

    if '"storage"' not in original_content:
        if not args.quiet:
            print(f"[UNCHANGED] {path}")
        return "unchanged"

    new_content, change_stats = fix_storage(
        original_content,
        fix_volume=not args.no_volume_fix,
        padding_ml=args.volume_padding_ml,
        remove_tardis=args.remove_tardis,
    )

    if new_content == original_content:
        if not args.quiet:
            print(f"[UNCHANGED] {path}")
        return "unchanged"

    if args.dry_run:
        msg = f"[DRY-RUN] {path} would be updated."
        if not args.quiet:
            msg += (
                f" storage fields: {change_stats['storage']},"
                f" volume fixes: {change_stats['volume']},"
                f" TARDIS removals: {change_stats['tardis']}"
            )
        print(msg)
        return "updated"

    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if args.formatter and os.path.exists(args.formatter):
            subprocess.run([args.formatter, path], capture_output=True)

        msg = f"[UPDATED] {path}"
        if not args.quiet:
            msg += (
                f" storage fields: {change_stats['storage']},"
                f" volume fixes: {change_stats['volume']},"
                f" TARDIS removals: {change_stats['tardis']}"
            )
        print(msg)
        return "updated"
    except Exception as e:
        LOGGER.error(f"Could not write {path}: {e}")
        return "error"


def process_path(path, args):
    stats = {"scanned": 0, "updated": 0, "unchanged": 0, "error": 0}

    if os.path.isfile(path):
        if path.endswith(".json"):
            stats["scanned"] += 1
            res = process_file(path, args)
            stats[res] += 1
        elif not args.quiet:
            print(f"[SKIPPED] {path} is not a .json file")
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in sorted(files):
                if file.endswith(".json"):
                    full_path = os.path.join(root, file)
                    stats["scanned"] += 1
                    res = process_file(full_path, args)
                    stats[res] += 1
    else:
        LOGGER.error(f"Path does not exist: {path}")
        stats["error"] += 1

    return stats


def main():
    args = parse_args()
    total_stats = {"scanned": 0, "updated": 0, "unchanged": 0, "error": 0}

    print(f"=== CDDA Storage to Pocket Data Converter {'[DRY-RUN]' if args.dry_run else '[UPDATE]'} ===")
    if not args.no_volume_fix:
        print("Volume safety fix: ON. Converted containers should not need TARDIS.")
    else:
        print("Volume safety fix: OFF. Some converted containers may still need TARDIS.")

    for path in args.paths:
        path_stats = process_path(path, args)
        for k in total_stats:
            total_stats[k] += path_stats[k]

    print(f"\nDone. {total_stats['scanned']} file(s) scanned: "
          f"{total_stats['updated']} updated, "
          f"{total_stats['unchanged']} unchanged, "
          f"{total_stats['error']} error(s).")


if __name__ == "__main__":
    main()
