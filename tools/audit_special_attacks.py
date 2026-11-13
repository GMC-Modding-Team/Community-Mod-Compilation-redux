"""List legacy monster attacks unavailable in the selected CDDA source tree."""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any, Iterator


def walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("roots", type=Path, nargs="+")
    args = parser.parse_args()

    source = (args.source_root / "src" / "monstergenerator.cpp").read_text(encoding="utf-8")
    valid = set(re.findall(r'add_hardcoded_attack\(\s*"([^"]+)', source))
    for path in (args.source_root / "data").rglob("*.json"):
        value = read_json(path)
        if value is None:
            continue
        for obj in walk(value):
            if obj.get("type") == "monster_attack" and isinstance(obj.get("id"), str):
                valid.add(obj["id"])

    # Compilation mods may provide their own data-driven attacks.  Collect the
    # definitions before checking references so only genuinely absent IDs are
    # reported.
    for root in args.roots:
        for path in root.rglob("*.json"):
            value = read_json(path)
            if value is None:
                continue
            for obj in walk(value):
                if obj.get("type") == "monster_attack" and isinstance(obj.get("id"), str):
                    valid.add(obj["id"])

    invalid: dict[str, list[str]] = collections.defaultdict(list)
    for root in args.roots:
        for path in root.rglob("*.json"):
            value = read_json(path)
            if value is None:
                continue
            for obj in walk(value):
                attacks = obj.get("special_attacks")
                if not isinstance(attacks, list):
                    continue
                for attack in attacks:
                    if (
                        isinstance(attack, list)
                        and attack
                        and isinstance(attack[0], str)
                        and attack[0] not in valid
                    ):
                        invalid[attack[0]].append(str(path))

    print(f"valid={len(valid)} invalid_distinct={len(invalid)}")
    for attack_id, paths in sorted(invalid.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        print(f"{attack_id}\t{len(paths)}\t{paths[0]}")
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
