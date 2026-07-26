#!/usr/bin/env python3
"""Remove generated H-release compatibility shims and their dependent entries.

The repository intentionally keeps real mod JSON files, but generated bridge
definitions are not portable content.  This tool removes bridge dependencies,
deletes references to bridge-only IDs, and leaves valid JSON arrays/files in
place so the original mod directories remain intact.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


BRIDGE_ID = "h_release_compat_bridge"


def records(value: Any) -> list[Any]:
    return value if isinstance(value, list) else [value]


def bridge_roots(root: Path) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("modinfo.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if any(isinstance(item, dict) and item.get("id") == BRIDGE_ID for item in records(data)):
            found.append(path.parent)
    return found


def bridge_ids(roots: list[Path]) -> set[str]:
    ids: set[str] = set()
    for root in roots:
        for path in root.glob("*.json"):
            if path.name.lower() == "modinfo.json":
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                continue
            for item in records(data):
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    ids.add(item["id"])
    return ids


def clean(value: Any, ids: set[str], *, root: bool = False) -> tuple[Any, int]:
    """Return a copy with bridge-only references removed and count removals."""
    removed = 0
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str) and item in ids:
                removed += 1
                continue
            cleaned, count = clean(item, ids)
            removed += count
            if cleaned is None:
                removed += 1
                continue
            if isinstance(cleaned, list) and not cleaned:
                continue
            if isinstance(cleaned, dict) and not cleaned:
                continue
            result.append(cleaned)
        return result, removed

    if isinstance(value, dict):
        # A top-level object whose identity or copy-from base is bridge-only is
        # itself unusable; drop the object rather than leaving a broken record.
        if any(
            isinstance(value.get(key), str) and value.get(key) in ids
            for key in ("id", "copy-from", "abstract")
        ):
            return None, 1
        result: dict[str, Any] = {}
        for key, item in value.items():
            if key == "dependencies" and isinstance(item, list):
                deps = [dep for dep in item if dep != BRIDGE_ID]
                removed += len(item) - len(deps)
                if deps:
                    result[key] = deps
                continue
            if isinstance(item, str) and item in ids:
                removed += 1
                continue
            cleaned, count = clean(item, ids)
            removed += count
            if cleaned is None:
                continue
            if isinstance(cleaned, list) and not cleaned:
                continue
            if isinstance(cleaned, dict) and not cleaned:
                continue
            result[key] = cleaned
        return result, removed

    return value, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--delete-bridges", action="store_true")
    args = parser.parse_args()

    search_root = Path.cwd()
    bridges = bridge_roots(search_root)
    ids = bridge_ids(bridges)
    if not bridges:
        print("No compatibility bridge mods found.")
        return 0

    changed_files = 0
    removed_entries = 0
    for root in args.roots:
        for path in root.rglob("*.json"):
            if any(path.resolve().is_relative_to(bridge.resolve()) for bridge in bridges):
                continue
            try:
                original_text = path.read_text(encoding="utf-8-sig")
                original = json.loads(original_text)
            except (OSError, json.JSONDecodeError):
                continue
            cleaned, count = clean(original, ids, root=True)
            if count:
                if cleaned is None:
                    cleaned = []
                path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                changed_files += 1
                removed_entries += count

    if args.delete_bridges:
        for bridge in bridges:
            shutil.rmtree(bridge)

    print(f"bridge_mods={len(bridges)} bridge_ids={len(ids)} changed_files={changed_files} removed_entries={removed_entries}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
