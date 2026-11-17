#!/usr/bin/env python3
"""Migrate legacy/H mod JSON to the documented Cataclysm: DDA 0.I-1 formats.

Python 3.10+; standard library only; independent of update_legacy_json.py.

    python tools/update_i1_json.py path/to/mod --dry-run --diff
    python tools/update_i1_json.py path/to/mod --backup
    python tools/update_i1_json.py one.json two.json --formatter path/to/json_formatter.exe

Supported conversions:
* Legacy item types -> ITEM/subtypes, including TOOL_ARMOR and nested slots.
* Place subtypes immediately after type, preserving other fields' order.
* Flatten armor/book/ammo/gun/seed/brewing/milling/relic slot objects.
* TOOL ammo -> tool_ammo; BOOK fun/skill -> read_fun/read_skill;
  COMESTIBLE fatigue_mod -> sleepiness_mod; brewing time/results prefixes.
* Item price/price_postapoc -> exact cent/USD/kUSD strings; legacy weight,
  volume, gun damage, melee damage and minimum-skill fields.
* Material/monster resistance maps; monstergroup name -> id;
  copy_from/looks-like/ident and MOD_INFO author spellings.
* Mapgen scalar om_terrain selectors -> one-item arrays and removal of the
  obsolete mapgen method: json member.
* Legacy reproduction baby_egg/baby_monster -> nested baby_type fields.
* Numeric overmap see_cost values -> I-1's named see-cost enum values.

Only top-level definitions and explicitly supported inheritance/slot objects
are migrated. Arbitrary nested actions, mapgen weights and pricing rules are
not searched and replaced. Proportional values remain numeric. Relative item
quantities receive units because I-1's unit readers require them.

This is a schema migrator, not a complete game validator. Missing core IDs,
dependencies, removed use actions, old pockets and other unsupported fields
need review and a game load test. It does not run the H compatibility pass,
delete definitions, invent replacement IDs or change game balance.

Exit codes: 0 = completed; 1 = file/JSON/conversion error; 2 = manual review
needed (or invalid CLI arguments). Conflicts leave the entire file untouched.
Dry runs never write files. Changed files use two-space JSON formatting unless
--formatter is supplied. --backup creates FILE.json.bak without overwriting it.

Rules checked against these pinned upstream sources (not master):
https://github.com/CleverRaven/Cataclysm-DDA/releases/tag/0.I-1
https://github.com/CleverRaven/Cataclysm-DDA/blob/0.I-1/src/init.cpp
https://github.com/CleverRaven/Cataclysm-DDA/blob/0.I-1/src/item_factory.cpp
https://github.com/CleverRaven/Cataclysm-DDA/blob/0.I-1/doc/JSON/ITEM.md
https://github.com/CleverRaven/Cataclysm-DDA/tree/0.I-1/tools/json_tools
"""

from __future__ import annotations

import argparse
import copy
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from decimal import Decimal
from typing import Any


LEGACY_TYPES = {
    "GENERIC": [], "CONTAINER": [], "TOOL_ARMOR": ["TOOL", "ARMOR"],
    **{name: [name] for name in (
        "AMMO", "GUN", "ARMOR", "PET_ARMOR", "TOOL", "TOOLMOD", "BOOK",
        "COMESTIBLE", "ENGINE", "WHEEL", "GUNMOD", "MAGAZINE", "BIONIC_ITEM",
    )},
}
SLOTS = {
    "armor_data": "ARMOR", "pet_armor_data": "PET_ARMOR",
    "book_data": "BOOK", "gun_data": "GUN", "bionic_data": "BIONIC_ITEM",
    "ammo_data": "AMMO", "seed_data": "SEED", "brewable": "BREWABLE",
    "compostable": "COMPOSTABLE", "milling": "MILLING",
    "gunmod_data": "GUNMOD", "relic_data": "ARTIFACT",
}
SLOT_RENAMES = {
    "TOOL": {"ammo": "tool_ammo"},
    "GUN": {"damage": "ranged_damage"},
    "BOOK": {"fun": "read_fun", "skill": "read_skill"},
    "COMESTIBLE": {"fatigue_mod": "sleepiness_mod"},
    "BREWABLE": {"time": "brew_time", "results": "brew_results"},
    "COMPOSTABLE": {"time": "compost_time", "results": "compost_results"},
}
MODIFIERS = ("relative", "proportional", "extend", "delete")
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
MONEY = re.compile(rf"\s*({NUMBER})\s*(cent|cents|USD|dollar|dollars|kUSD)?\s*", re.I)
SEE_COST_MIGRATION = {
    0: "none",
    1: "low",
    2: "medium",
    4: "spaced_high",
    5: "high",
    10: "full_high",
    999: "opaque",
}
UNSUPPORTED_ITEM_FIELDS = {
    "container_data", "magazines", "magazine_well", "rand_charges", "nutrition",
    "rot_spawn_chance", "tool_data", "comestible_data", "battery_data",
}


class MigrationError(ValueError):
    """Conversion would discard data or cannot be performed unambiguously."""


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def integer(value: Decimal, description: str) -> int:
    if not value.is_finite() or value != value.to_integral_value():
        raise MigrationError(f"{description}: fractional units cannot be converted losslessly ({value})")
    return int(value)


def money_string(value: Any) -> Any:
    """Bare numbers are cents; never truncate or reinterpret authored dollars."""
    if is_number(value):
        amount = Decimal(str(value))
    elif isinstance(value, str):
        match = MONEY.fullmatch(value)
        if not match:
            return value  # Preserve mixed-unit expressions.
        scale = {"usd": 100, "dollar": 100, "dollars": 100, "kusd": 100000}
        amount = Decimal(match[1]) * scale.get((match[2] or "cent").lower(), 1)
    else:
        return value
    cents = integer(amount, "price")
    if cents and cents % 100000 == 0:
        return f"{cents // 100000} kUSD"
    if cents and cents % 100 == 0:
        return f"{cents // 100} USD"
    return f"{cents} cent"


def merge(target: dict, incoming: dict, location: str) -> None:
    """Merge only equal values or disjoint dictionary fields; never overwrite."""
    for key, value in incoming.items():
        if key not in target:
            target[key] = copy.deepcopy(value)
        elif target[key] == value:
            continue
        elif isinstance(target[key], dict) and isinstance(value, dict):
            merge(target[key], value, f"{location}.{key}")
        elif key.startswith("//"):
            suffix = 2
            while f"{key} {suffix}" in target:
                suffix += 1
            target[f"{key} {suffix}"] = copy.deepcopy(value)
        else:
            raise MigrationError(f"{location}.{key}: conflicting old and new values")


def rename(obj: dict, old: str, new: str) -> None:
    if old in obj:
        merge(obj, {new: obj[old]}, new)
        del obj[old]


def modifier_objects(obj: dict):
    yield obj, "direct"
    for key in MODIFIERS:
        if key in obj:
            if not isinstance(obj[key], dict):
                raise MigrationError(f"{key} must be an object")
            yield obj[key], key


def rename_slot_fields(obj: dict, subtypes: list[str]) -> None:
    for part, _ in modifier_objects(obj):
        for subtype in subtypes:
            for old, new in SLOT_RENAMES.get(subtype, {}).items():
                rename(part, old, new)


def declared_subtypes(obj: dict) -> list[str]:
    subtypes = obj.get("subtypes", [])
    if not isinstance(subtypes, list) or not all(isinstance(s, str) for s in subtypes):
        raise MigrationError("subtypes must be an array of strings")
    types = list(LEGACY_TYPES.get(obj.get("type"), [])) + subtypes
    types.extend(subtype for key, subtype in SLOTS.items() if key in obj)
    return list(dict.fromkeys(types))


def migrate_item(obj: dict, warnings: list[str]) -> None:
    old_type = obj["type"]
    subtypes = declared_subtypes(obj)
    # Legacy top-level slot fields belong to the old type. Rename before
    # flattening extra slots so a gun/book hybrid keeps its gun skill.
    if old_type != "ITEM":
        rename_slot_fields(obj, LEGACY_TYPES[old_type])
    else:
        # Modern multi-slot items already use distinct keys. Only the
        # unambiguous legacy fatigue spelling is safe to rename here.
        if "COMESTIBLE" in subtypes:
            rename_slot_fields(obj, ["COMESTIBLE"])
    for key, subtype in SLOTS.items():
        if key not in obj:
            continue
        slot = obj[key]
        if not isinstance(slot, dict):
            raise MigrationError(f"{key}: expected an object; manual conversion needed")
        slot = copy.deepcopy(slot)
        rename_slot_fields(slot, [subtype])
        merge(obj, slot, key)
        del obj[key]
    for left, right in (("ARMOR", "PET_ARMOR"), ("GUNMOD", "TOOLMOD")):
        if left in subtypes and right in subtypes:
            raise MigrationError(f"I-1 cannot combine {left} and {right} subtypes")
    obj["type"] = "ITEM"
    if subtypes or "subtypes" in obj:
        obj["subtypes"] = subtypes

    flags = obj.get("flags", [])
    stab = isinstance(flags, list) and any(flag in flags for flag in ("STAB", "SPEAR"))
    for part, context in modifier_objects(obj):
        mapping = {"bashing": "bash", "cutting": "stab" if stab else "cut"}
        merge_map(part, mapping, "melee_damage")
        if context == "direct" and isinstance(part.get("flags"), list) and "STAB" in part["flags"]:
            # A STAB flag with no known damage needs an author decision.
            damage = part.get("melee_damage", {})
            if isinstance(damage, dict) and "stab" in damage:
                part["flags"].remove("STAB")
            else:
                warnings.append("STAB flag has no explicit stab damage; review inherited damage")
        if context in ("direct", "relative"):
            for key in ("price", "price_postapoc"):
                if key in part:
                    part[key] = money_string(part[key])
            for key in ("weight", "integral_weight"):
                if is_number(part.get(key)):
                    mg = integer(Decimal(str(part[key])) * 1000, key)
                    part[key] = f"{mg // 1000} g" if mg % 1000 == 0 else f"{mg} mg"
            for key in ("volume", "integral_volume"):
                if is_number(part.get(key)):
                    ml = integer(Decimal(str(part[key])) * 250, key)
                    part[key] = f"{ml} ml"
        if context == "direct":
            if isinstance(part.get("material"), str):
                part["material"] = [part["material"]]
            if "GUN" in subtypes:
                if "AMMO" not in subtypes:
                    rename(part, "damage", "ranged_damage")
                if isinstance(part.get("ammo"), str):
                    part["ammo"] = [part["ammo"]]
            for subtype, damage_key in (("GUN", "ranged_damage"), ("AMMO", "damage")):
                if subtype in subtypes and is_number(part.get(damage_key)):
                    damage = {"damage_type": "bullet", "amount": part[damage_key]}
                    if "pierce" in part:
                        if "GUN" in subtypes and "AMMO" in subtypes:
                            raise MigrationError("pierce is ambiguous on a GUN/AMMO hybrid")
                        damage["armor_penetration"] = part.pop("pierce")
                    part[damage_key] = damage
            if "pierce" in part:
                warnings.append("pierce with structured damage needs manual review")
            migrate_skills(part)
            if is_number(part.get("barrel_length")):
                warnings.append("numeric barrel_length is ambiguous (legacy volume versus length)")
        for key in UNSUPPORTED_ITEM_FIELDS.intersection(part):
            warnings.append(f"{context}.{key} needs manual I-1 conversion")
    # Nested slots in inheritance patches need schema-specific decisions;
    # do not silently drop them or treat their values as direct item fields.
    for modifier in MODIFIERS:
        patch = obj.get(modifier, {})
        for key in SLOTS.keys() & patch.keys():
            warnings.append(f"{modifier}.{key} needs manual slot migration")


def migrate_skills(obj: dict) -> None:
    skills = []
    for old, new in (("min_melee", "melee"), ("min_unarmed", "unarmed")):
        if old in obj:
            skills.append([new, obj.pop(old)])
    if "skill_requirements" in obj:
        old = obj.pop("skill_requirements")
        if not isinstance(old, list):
            raise MigrationError("skill_requirements must be an array")
        for skill in old:
            if isinstance(skill, dict) and set(skill) == {"name", "level"}:
                skills.append([skill["name"], skill["level"]])
            elif isinstance(skill, list) and len(skill) == 2:
                skills.append(skill)
            else:
                raise MigrationError("unsupported skill_requirements entry")
    if skills:
        existing = obj.setdefault("min_skills", [])
        if not isinstance(existing, list) or not all(isinstance(s, list) and len(s) == 2 for s in existing):
            raise MigrationError("cannot merge this min_skills representation")
        for skill in skills:
            matches = [s for s in existing if s[0] == skill[0]]
            if matches and any(s != skill for s in matches):
                raise MigrationError(f"conflicting minimum skill: {skill[0]}")
            if not matches:
                existing.append(skill)


def merge_map(obj: dict, mapping: dict[str, str], field: str) -> None:
    values = {new: obj[old] for old, new in mapping.items() if old in obj}
    if values:
        merge(obj, {field: values}, field)
        for old in mapping:
            obj.pop(old, None)


def place_subtypes_after_type(obj: dict) -> None:
    """Move only subtypes, preserving all values and other fields' order."""
    if "type" not in obj or "subtypes" not in obj:
        return
    fields = list(obj.items())
    obj.clear()
    for key, value in fields:
        if key == "subtypes":
            continue
        obj[key] = value
        if key == "type":
            obj["subtypes"] = next(value for name, value in fields if name == "subtypes")


def migrate_reproduction(obj: dict) -> None:
    """Move legacy reproduction baby fields into I-1's baby_type object."""
    reproduction = obj.get("reproduction")
    if not isinstance(reproduction, dict):
        return

    legacy_keys = [key for key in ("baby_egg", "baby_monster") if key in reproduction]
    if not legacy_keys:
        return
    if len(legacy_keys) > 1:
        raise MigrationError("reproduction cannot specify both baby_egg and baby_monster")

    legacy_key = legacy_keys[0]
    legacy_value = reproduction[legacy_key]
    existing = reproduction.get("baby_type")
    if existing is None:
        baby_type = {legacy_key: legacy_value}
    elif isinstance(existing, dict):
        baby_type = copy.deepcopy(existing)
        if legacy_key in baby_type and baby_type[legacy_key] != legacy_value:
            raise MigrationError(f"reproduction.baby_type.{legacy_key} conflicts with {legacy_key}")
        other_type_keys = {
            "baby_egg", "baby_egg_group", "baby_monster", "baby_monster_group",
        } - {legacy_key}
        if any(key in baby_type for key in other_type_keys):
            raise MigrationError("reproduction.baby_type specifies multiple baby types")
        baby_type[legacy_key] = legacy_value
    else:
        raise MigrationError("reproduction.baby_type must be an object")

    # Rebuild the small object so baby_type occupies the old baby_egg position
    # and all unrelated reproduction fields retain their authored order/values.
    migrated = {}
    inserted = False
    for key, value in reproduction.items():
        if key in legacy_keys:
            if not inserted:
                migrated["baby_type"] = baby_type
                inserted = True
        elif key == "baby_type":
            if not inserted:
                migrated["baby_type"] = baby_type
                inserted = True
        else:
            migrated[key] = value
    reproduction.clear()
    reproduction.update(migrated)


def migrate_overmap_terrain(obj: dict) -> None:
    """Convert legacy numeric see_cost values to I-1 enum names."""
    if obj.get("type") != "overmap_terrain" or "see_cost" not in obj:
        return
    value = obj["see_cost"]
    if not is_number(value):
        return
    if isinstance(value, float) and not value.is_integer():
        raise MigrationError(f"unsupported numeric see_cost: {value}")
    numeric = int(value)
    try:
        obj["see_cost"] = SEE_COST_MIGRATION[numeric]
    except KeyError as exc:
        raise MigrationError(f"unsupported numeric see_cost: {value}") from exc


def migrate_definition(obj: dict, warnings: list[str]) -> None:
    rename(obj, "ident", "id")
    rename(obj, "copy_from", "copy-from")
    rename(obj, "looks-like", "looks_like")
    migrate_reproduction(obj)
    migrate_overmap_terrain(obj)
    kind = obj.get("type")
    if not isinstance(kind, str):
        raise MigrationError("definition has no string type")
    if kind == "mapgen":
        # I-1 identifies mapgens by their definition type; the legacy
        # method selector is obsolete and rejected as an unknown member.
        if obj.get("method") == "json":
            del obj["method"]
        if isinstance(obj.get("om_terrain"), str):
            obj["om_terrain"] = [obj["om_terrain"]]
    if kind in LEGACY_TYPES or kind == "ITEM":
        migrate_item(obj, warnings)
    elif kind == "BATTERY":
        # The 0.I-1 loader has no BATTERY subtype branch, despite an outdated
        # example in ITEM.md. Never pretend adding that subtype is sufficient.
        warnings.append("BATTERY needs manual migration: I-1 does not load this item type")
    elif kind == "monstergroup":
        rename(obj, "name", "id")
    elif kind == "MOD_INFO":
        if "author" in obj:
            authors = obj["author"]
            merge(obj, {"authors": [authors] if isinstance(authors, str) else authors}, "authors")
            del obj["author"]
    elif kind in ("material", "MONSTER"):
        if kind == "material":
            mapping = {f"{name}_resist": target for name, target in (
                ("bash", "bash"), ("cut", "cut"), ("acid", "acid"),
                ("fire", "heat"), ("bullet", "bullet"), ("elec", "electric"),
                ("biologic", "biological"), ("cold", "cold"),
            )}
            field = "resist"
        else:
            mapping = {f"armor_{name}": target for name, target in (
                ("bash", "bash"), ("cut", "cut"), ("stab", "stab"),
                ("acid", "acid"), ("fire", "heat"), ("bullet", "bullet"),
                ("elec", "electric"), ("biological", "biological"),
                ("cold", "cold"), ("pure", "pure"),
            )}
            field = "armor"
        for part, _ in modifier_objects(obj):
            merge_map(part, mapping, field)
    place_subtypes_after_type(obj)


def migrate(data: Any) -> tuple[Any, list[str]]:
    """Return a migrated copy and review messages, leaving the input unchanged."""
    result = copy.deepcopy(data)
    entries = result if isinstance(result, list) else [result]
    warnings = []
    for index, obj in enumerate(entries):
        if not isinstance(obj, dict):
            raise MigrationError(f"entry {index}: expected a JSON definition object")
        label = obj.get("id", obj.get("abstract", obj.get("ident", index)))
        local_warnings = []
        try:
            migrate_definition(obj, local_warnings)
        except MigrationError as exc:
            raise MigrationError(f"{label}: {exc}") from exc
        warnings.extend(f"{label}: {message}" for message in local_warnings)
    return result, warnings


def unique_object(pairs: list[tuple[str, Any]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            if not key.startswith("//"):
                raise MigrationError(f"duplicate JSON key {key!r}; resolve before migrating")
            suffix = 2
            while f"{key} {suffix}" in obj:
                suffix += 1
            key = f"{key} {suffix}"
        obj[key] = value
    return obj


def load_json(text: str) -> Any:
    def invalid_constant(value):
        raise MigrationError(f"non-finite JSON number {value}")
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def collect_files(paths: list[str]) -> list[Path]:
    files = set()
    for raw in paths:
        path = Path(raw).resolve()
        if path.is_dir():
            files.update(p.resolve() for p in path.rglob("*") if p.is_file() and p.suffix.lower() == ".json")
        elif path.is_file() and path.suffix.lower() == ".json":
            files.add(path)
        else:
            raise MigrationError(f"not a JSON file or directory: {raw}")
    if not files:
        raise MigrationError("no JSON files found")
    return sorted(files)


def write_atomic(path: Path, text: str, original: bytes, backup: bool, formatter: Path | None) -> None:
    """Format and validate a temporary file before replacing the original."""
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.stem}.i1-", suffix=".json", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        if formatter:
            proc = subprocess.run([str(formatter), str(temp)], capture_output=True, text=True, timeout=120)
            # CDDA's formatter returns 1 when it reformats a valid file.
            if proc.returncode not in (0, 1):
                raise MigrationError(f"formatter failed ({proc.returncode}): {proc.stderr.strip()}")
            if load_json(temp.read_text(encoding="utf-8-sig")) != load_json(text):
                raise MigrationError("formatter changed JSON values")
            formatted = load_json(temp.read_text(encoding="utf-8-sig"))
            entries = formatted if isinstance(formatted, list) else [formatted]
            for obj in entries:
                if "type" in obj and "subtypes" in obj:
                    keys = list(obj)
                    if keys.index("subtypes") != keys.index("type") + 1:
                        raise MigrationError("formatter moved subtypes away from type; retry without --formatter")
        if path.read_bytes() != original:
            raise MigrationError("file changed during migration; refusing to overwrite")
        if backup:
            with path.with_name(path.name + ".bak").open("xb") as stream:
                stream.write(original)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", metavar="PATH", help="JSON files or directories (recursive)")
    parser.add_argument("--dry-run", action="store_true", help="preview without writing any files")
    parser.add_argument("--diff", action="store_true", help="print a unified diff for each changed file")
    parser.add_argument("--backup", action="store_true", help="save original bytes to FILE.json.bak")
    parser.add_argument("--formatter", type=Path, help="optional CDDA json_formatter executable")
    args = parser.parse_args(argv)
    try:
        files = collect_files(args.paths)
        formatter = args.formatter.resolve() if args.formatter else None
        if formatter and not formatter.is_file():
            raise MigrationError(f"formatter not found: {formatter}")
    except (OSError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    changed = errors = reviews = 0
    for path in files:
        try:
            original = path.read_bytes()
            before = original.decode("utf-8-sig")
            data = load_json(before)
            migrated, warnings = migrate(data)
            reviews += len(warnings)
            for warning in warnings:
                print(f"[REVIEW] {path}: {warning}")
            # Dictionary equality ignores field order; include ordering-only changes.
            if json.dumps(migrated, ensure_ascii=False) == json.dumps(data, ensure_ascii=False):
                continue
            after = json.dumps(migrated, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
            if args.diff:
                print("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                  fromfile=str(path), tofile=str(path) + " (I-1)")), end="")
            if not args.dry_run:
                write_atomic(path, after, original, args.backup, formatter)
            changed += 1
            print(f"[{'WOULD UPDATE' if args.dry_run else 'UPDATED'}] {path}")
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            errors += 1
            print(f"[ERROR] {path}: {exc}", file=sys.stderr)
    action = "would change" if args.dry_run else "changed"
    print(f"I-1: {len(files)} files checked; {changed} {action}; {reviews} review notes; {errors} errors.")
    return 1 if errors else 2 if reviews else 0


if __name__ == "__main__":
    raise SystemExit(main())
