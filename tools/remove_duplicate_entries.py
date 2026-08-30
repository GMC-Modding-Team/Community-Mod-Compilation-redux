#!/usr/bin/env python3
"""Safely remove duplicate CDDA JSON entries from non-Mainline mod trees.

This is intentionally conservative.  It removes only exact duplicate
top-level factory objects within a mod's source tree (for example two
``{"type": "ARMOR", "id": "same_id"}`` definitions).  It does not alter
item-group/blacklist arrays, variants, or any other nested list.  Differing
definitions are reported for review instead of being guessed away, including
definitions in files named ``obsolete``.

Usage::

    python tools/remove_duplicate_entries.py data workshop --dry-run
    python tools/remove_duplicate_entries.py data/Legacy_mods --write

With no roots, the repository's ``data`` and ``workshop`` trees are scanned.
The default is still a dry run; pass ``--write`` to apply removals.

Use ``--write`` to modify files.  Mainline_mods is always skipped, even when
the root passed on the command line includes it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ITEM_TYPES = {
    "AMMO", "ARMOR", "BATTERY", "BIONIC_ITEM", "BOOK", "COMESTIBLE",
    "ENGINE", "GENERIC", "GUN", "GUNMOD", "MAGAZINE", "PET_ARMOR",
    "TOOL", "TOOLMOD", "TOOL_ARMOR", "WHEEL",
}

INLINE_FACTORY_KEYS = {
    "static_buffs", "onmove_buffs", "onattack_buffs", "onhit_buffs",
    "onblock_buffs", "onmiss_buffs", "oncrit_buffs", "ondodge_buffs",
}


def strip_comments(text: str) -> str:
    """Remove C++-style comments without changing string contents."""
    out: list[str] = []
    i = 0
    quoted = False
    escaped = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if quoted:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                quoted = False
            i += 1
            continue
        if ch == '"':
            quoted = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and nxt == "/":
            out.extend((" ", " "))
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                out.append(" ")
                i += 1
            continue
        if ch == "/" and nxt == "*":
            out.extend((" ", " "))
            i += 2
            while i < len(text):
                if i + 1 < len(text) and text[i:i + 2] == "*/":
                    out.extend((" ", " "))
                    i += 2
                    break
                out.append(text[i] if text[i] in "\r\n" else " ")
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def is_mainline(path: Path) -> bool:
    return any(part.lower() in {"mainline_mods", "mainline"} for part in path.parts)


def json_files(roots: Iterable[Path]) -> list[Path]:
    result: set[Path] = set()
    for root in roots:
        root = root.resolve()
        if root.is_file() and root.suffix.lower() == ".json":
            if not is_mainline(root):
                result.add(root)
            continue
        if root.is_dir():
            for path in root.rglob("*.json"):
                if not is_mainline(path):
                    result.add(path)
    return sorted(result)


def load(path: Path) -> tuple[Any | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8-sig")
        return json.loads(strip_comments(text)), None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, str(exc)


def mod_root(path: Path) -> Path:
    current = path.parent
    while current != current.parent:
        if (current / "modinfo.json").exists():
            return current
        current = current.parent
    return path.parent


def identity(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, dict) or not isinstance(value.get("type"), str):
        return None
    kind = value["type"]
    ident = value.get("id", value.get("abstract"))
    if kind.upper() in {"MONSTER_FACTION", "MONSTER_FACTION"}:
        ident = value.get("name", ident)
    elif kind.lower() == "monstergroup":
        ident = value.get("name", ident)
    if not isinstance(ident, str) or not ident:
        return None
    namespace = "ITEM" if kind.upper() in ITEM_TYPES else kind.upper()
    return namespace, ident


def quality(value: Any) -> tuple[int, int]:
    if not isinstance(value, dict):
        return (0, 0)
    score = len(value) * 100 + len(canonical(value))
    if isinstance(value.get("copy-from"), str):
        score += 10_000
    description = value.get("description")
    if isinstance(description, str) and "placeholder for a missing legacy" in description.lower():
        score -= 100_000
    return score, len(canonical(value))


def path_label(path: Path, base: Path | None) -> str:
    try:
        return path.relative_to(base).as_posix() if base else path.as_posix()
    except ValueError:
        return path.as_posix()


def remove_exact_duplicates(values: list[Any]) -> tuple[list[Any], int]:
    kept: list[Any] = []
    seen: set[str] = set()
    removed = 0
    for value in values:
        key = canonical(value)
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept.append(value)
    return kept, removed


def remove_top_level_duplicates(
    file_data: dict[Path, Any], counts: Counter[str], reports: list[str], base: Path | None
) -> None:
    """Remove exact/safely-obsolete duplicate factory definitions per mod."""
    registry: dict[tuple[Path, tuple[str, str]], tuple[Path, Any]] = {}
    removed_ids: dict[Path, set[int]] = defaultdict(set)
    for path in sorted(file_data):
        data = file_data[path]
        entries = data if isinstance(data, list) else [data]
        owner = mod_root(path)
        for entry in entries:
            ident = identity(entry)
            if ident is None or ident[0] == "MOD_INFO":
                continue
            key = (owner, ident)
            previous = registry.get(key)
            if previous is None:
                registry[key] = (path, entry)
                continue
            prev_path, prev_entry = previous
            if canonical(entry) == canonical(prev_entry):
                removed_ids[path].add(id(entry))
                counts["duplicate_definitions_exact"] += 1
                continue
            # A differing definition in an obsolete-named file is still
            # authored data.  Keep it and report it rather than silently
            # dropping fields (obsolete files can contain intentional
            # overrides or migration data).  Exact duplicates were handled
            # above, so no obsolete special case is needed here.
            reports.append(
                f"DIFFERING duplicate {ident[0]} {ident[1]}: "
                f"{path_label(prev_path, base)} vs {path_label(path, base)}"
            )

    for path, ids in removed_ids.items():
        data = file_data[path]
        if isinstance(data, list):
            file_data[path] = [entry for entry in data if id(entry) not in ids]
        elif id(data) in ids:
            file_data[path] = []


def dedupe_inline_factory_entries(
    file_data: dict[Path, Any], counts: Counter[str], reports: list[str], base: Path | None
) -> None:
    """Dedupe globally registered martial-art buff IDs within each mod."""
    registry: dict[tuple[Path, str, str], tuple[Path, list[Any], Any]] = {}

    def visit(value: Any, path: Path, *, in_variants: bool = False) -> None:
        if in_variants:
            return
        if isinstance(value, dict):
            for key, child in list(value.items()):
                if key == "variants":
                    continue
                if key in INLINE_FACTORY_KEYS and isinstance(child, list):
                    kept: list[Any] = []
                    for entry in child:
                        ident = entry.get("id") if isinstance(entry, dict) else None
                        if not isinstance(ident, str) or not ident:
                            kept.append(entry)
                            continue
                        registry_key = (mod_root(path), key, ident)
                        previous = registry.get(registry_key)
                        if previous is None:
                            registry[registry_key] = (path, kept, entry)
                            kept.append(entry)
                            continue
                        prev_path, prev_list, prev_entry = previous
                        if canonical(entry) == canonical(prev_entry):
                            counts["duplicate_inline_factory_entries"] += 1
                            continue
                        reports.append(
                            f"DIFFERING inline {key} {ident}: "
                            f"{path_label(prev_path, base)} vs {path_label(path, base)}"
                        )
                        kept.append(entry)
                    value[key] = kept
                    for entry in kept:
                        visit(entry, path)
                else:
                    visit(child, path)
        elif isinstance(value, list):
            for child in value:
                visit(child, path)

    for path in sorted(file_data):
        visit(file_data[path], path)


def write_json(path: Path, data: Any, formatter: Path | None) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if formatter:
        # The repository formatter returns non-zero when it changed a file;
        # that is normal, so do not treat that status as a failure.
        subprocess.run([str(formatter), str(path)], check=False, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        help="JSON file or directory roots (defaults to data and workshop)",
    )
    parser.add_argument("--write", action="store_true", help="modify files; default is report-only")
    parser.add_argument("--dry-run", action="store_true", help="report only (the default)")
    parser.add_argument("--formatter", type=Path, help="optional CDDA JSON formatter executable")
    parser.add_argument("--report", type=Path, help="write the report as JSON")
    args = parser.parse_args()
    if args.write and args.dry_run:
        parser.error("choose either --write or --dry-run")

    # Explorer launches Python scripts with an unrelated working directory
    # (often ``C:\\Windows\\System32``).  Resolve the implicit repository
    # roots beside this script so a double-click or an absolute script path
    # still scans the intended checkout.
    repo_root = Path(__file__).resolve().parents[1]
    roots = args.roots or [repo_root / "data", repo_root / "workshop"]
    files = json_files(roots)
    base = Path(os.path.commonpath([str(path) for path in files])) if files else None
    file_data: dict[Path, Any] = {}
    errors: list[str] = []
    for path in files:
        data, error = load(path)
        if error:
            errors.append(f"PARSE ERROR {path_label(path, base)}: {error}")
        else:
            file_data[path] = data

    counts: Counter[str] = Counter(files=len(files), parsed=len(file_data))
    reports: list[str] = []
    originals = {path: canonical(data) for path, data in file_data.items()}
    remove_top_level_duplicates(file_data, counts, reports, base)

    changed: list[Path] = []
    for path, data in file_data.items():
        if canonical(data) == originals[path]:
            continue
        changed.append(path)
        if args.write:
            write_json(path, data, args.formatter)

    output = {
        "mode": "write" if args.write else "dry-run",
        "files": len(files),
        "changed_files": len(changed),
        "counts": dict(sorted(counts.items())),
        "differing_duplicates": reports,
        "parse_errors": errors,
        "changed_paths": [path_label(path, base) for path in changed],
        "mainline_skipped": True,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if not files:
        print(
            "No JSON files found. Run this from the repository or pass a data/workshop path.",
            file=sys.stderr,
        )
    if args.report:
        args.report.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not args.write:
        print("Dry run only; pass --write to apply duplicate-header removals.", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
