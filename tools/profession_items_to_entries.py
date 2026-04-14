#!/usr/bin/env python3
"""Convert legacy profession item lists to entry objects.

This updates profession JSON objects from:
    "items": {
      "both": ["item_a", "item_b"],
      "male": ["briefs"],
      "female": ["bra", "panties"]
    }

To:
    "items": {
      "both": {"entries": [{"item": "item_a"}, {"item": "item_b"}]},
      "male": {"entries": [{"item": "briefs"}]},
      "female": {"entries": [{"item": "bra"}, {"item": "panties"}]}
    }

By default the script runs in dry-run mode and only reports what would change.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TARGET_GROUPS = ("both", "male", "female")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert legacy profession items lists into entries objects. "
            "Defaults to dry-run."
        )
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a JSON file or directory to process (default: current directory).",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write changes to disk. Without this flag, the script only reports changes.",
    )
    return parser.parse_args()


def iter_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".json" else []
    return sorted(p for p in path.rglob("*.json") if p.is_file())


def normalize_item_entry(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        return {"item": value}
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Unsupported item entry type: {type(value).__name__}")


def convert_items(items: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    converted = dict(items)

    for group in TARGET_GROUPS:
        if group not in converted:
            continue

        group_value = converted[group]

        if isinstance(group_value, list):
            converted[group] = {
                "entries": [normalize_item_entry(entry) for entry in group_value]
            }
            changed = True
            continue

        if isinstance(group_value, dict):
            entries = group_value.get("entries")
            if isinstance(entries, list):
                normalized_entries = [normalize_item_entry(entry) for entry in entries]
                if normalized_entries != entries:
                    converted[group] = dict(group_value)
                    converted[group]["entries"] = normalized_entries
                    changed = True
            continue

    return converted, changed


def transform_json(data: Any) -> tuple[Any, int]:
    if not isinstance(data, list):
        return data, 0

    updates = 0
    transformed: list[Any] = []

    for obj in data:
        if not isinstance(obj, dict):
            transformed.append(obj)
            continue

        if str(obj.get("type", "")).lower() != "profession":
            transformed.append(obj)
            continue

        items = obj.get("items")
        if not isinstance(items, dict):
            transformed.append(obj)
            continue

        new_items, changed = convert_items(items)
        if not changed:
            transformed.append(obj)
            continue

        new_obj = dict(obj)
        new_obj["items"] = new_items
        transformed.append(new_obj)
        updates += 1

    return transformed, updates


def process_file(path: Path, write_changes: bool) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        print(f"[ERROR] {path}: {err}")
        return 0

    transformed, updates = transform_json(data)
    if updates == 0:
        return 0

    if write_changes:
        path.write_text(
            json.dumps(transformed, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[WRITE] {path} ({updates} profession object(s) updated)")
    else:
        print(f"[DRY-RUN] {path} ({updates} profession object(s) would be updated)")

    return updates


def main() -> int:
    args = parse_args()
    base_path = Path(args.path).resolve()

    files = iter_json_files(base_path)
    if not files:
        print(f"No JSON files found at: {base_path}")
        return 0

    files_changed = 0
    profession_updates = 0

    for json_file in files:
        updates = process_file(json_file, write_changes=args.write)
        if updates:
            files_changed += 1
            profession_updates += updates

    mode = "WRITE" if args.write else "DRY-RUN"
    print(
        f"[{mode}] Completed. Files affected: {files_changed}; "
        f"profession objects updated: {profession_updates}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
