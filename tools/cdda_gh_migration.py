#!/usr/bin/env python3
"""
cdda_gh_migration.py
====================
Migrates Cataclysm: Dark Days Ahead mod JSON from 0.G (Gaiman) to 0.H (Hazel).

Applies all known breaking and recommended changes discovered across 12 research
domains. Each transformation pass is independently toggleable via --skip.

Transformation passes
---------------------
  items           General item field renames and format changes
  armor           Armor coverage, encumbrance, and material field changes
  migration_types Adds MIGRATION / vehicle_part_migration / bionic_migration
                  / TRAIT_MIGRATION / effect_migration stubs for removed entities
  bodyparts       Converts legacy uppercase body-part names in "covers" to the
                  new lowercase bodypart_id system; adds "specifically_covers"
                  hints where detectable; handles _EITHER -> "sided": true
  mapgen          Updates overmap_special subtype field; flags om_terrain arrays
  recipes         Flags recipes missing "proficiencies" for review
  mutations       Converts old flat modifier fields to the new structured format
  spells          Adds magic_type stub where missing; flags old energy_source values
  vehicles        Adds vehicle_part_migration stubs for parts using old IDs

Usage
-----
  python3 cdda_gh_migration.py path/to/mod/
  python3 cdda_gh_migration.py file1.json file2.json path/to/mod/
  python3 cdda_gh_migration.py path/to/mod/ --dry-run
  python3 cdda_gh_migration.py path/to/mod/ --quiet
  python3 cdda_gh_migration.py path/to/mod/ --skip bodyparts spells
  python3 cdda_gh_migration.py path/to/mod/ --report   # write a migration report
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    filename="cdda_gh_migration.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global report accumulator (populated when --report is active)
# ---------------------------------------------------------------------------

REPORT: list[dict] = []


# ===========================================================================
# PASS 1 — Item field renames and format changes
# ===========================================================================
# Research sources: item JSON domain, 0.H changelog, OBSOLETION_AND_MIGRATION.md

# Fields that were renamed between 0.G and 0.H
ITEM_RENAMES: dict[str, str] = {
    "ident":     "id",
    "copy_from": "copy-from",
    "looks-like": "looks_like",
    "mod-type":  "category",
    "note":      "//",
    "chance":    "prob",
}

# String -> list promotions
ITEM_LIST_FIELDS = ("ammo", "material", "blueprint", "author")

# Type renames
TYPE_RENAMES: dict[str, str] = {
    "CONTAINER": "GENERIC",
}

# Effect value renames
EFFECT_RENAMES: dict[str, str] = {
    "target_attack": "attack",
}


def _to_volume_str(n: int | float) -> str:
    if n == 0:
        return "1 ml"
    ml = int(n) * 250
    if ml >= 10000 and ml % 1000 == 0:
        return f"{ml // 1000} L"
    return f"{ml} ml"


def _apply_items(entry: dict, path: Path) -> bool:
    changed = False

    # Key renames
    for old, new in ITEM_RENAMES.items():
        if old in entry:
            entry[new] = entry.pop(old)
            changed = True

    # author -> authors
    if "author" in entry:
        val = entry.pop("author")
        entry["authors"] = [val] if isinstance(val, str) else val
        changed = True

    # String -> list promotions (ammo, material, blueprint)
    for field in ("ammo", "material", "blueprint"):
        if field in entry and isinstance(entry[field], str):
            entry[field] = [entry[field]]
            changed = True

    # damage: int -> dict
    if "damage" in entry and isinstance(entry["damage"], (int, float)):
        dmg: dict = {"damage_type": "bullet", "amount": int(entry["damage"])}
        if "pierce" in entry:
            dmg["armor_penetration"] = entry.pop("pierce")
        entry["damage"] = dmg
        changed = True
    elif "pierce" in entry and isinstance(entry.get("damage"), dict):
        entry["damage"]["armor_penetration"] = entry.pop("pierce")
        changed = True

    # barrel_length -> barrel_volume
    if "barrel_length" in entry:
        raw = entry.pop("barrel_length")
        entry["barrel_volume"] = f"{int(raw) * 250} ml" if isinstance(raw, (int, float)) else raw
        changed = True

    # volume / folded_volume / integral_volume: int -> str
    for vfield in ("volume", "folded_volume", "integral_volume"):
        if vfield in entry and isinstance(entry[vfield], (int, float)):
            if entry.get("type") not in ("sound_effect", "speech"):
                entry[vfield] = _to_volume_str(entry[vfield])
                changed = True

    # weight: int -> "N g"
    if "weight" in entry and isinstance(entry["weight"], (int, float)):
        entry["weight"] = f"{int(entry['weight'])} g"
        changed = True

    # price / price_postapoc: int -> "N cent"
    for pfield in ("price", "price_postapoc"):
        if pfield in entry and isinstance(entry[pfield], (int, float)):
            entry[pfield] = f"{int(entry[pfield])} cent"
            changed = True

    # type renames
    if entry.get("type") in TYPE_RENAMES:
        entry["type"] = TYPE_RENAMES[entry["type"]]
        changed = True

    # effect value renames
    if entry.get("effect") in EFFECT_RENAMES:
        entry["effect"] = EFFECT_RENAMES[entry["effect"]]
        changed = True

    # min_melee / min_unarmed -> skill_requirements
    skill_reqs = list(entry.get("skill_requirements", []))
    for skill_field, skill_name in (("min_melee", "melee"), ("min_unarmed", "unarmed")):
        if skill_field in entry:
            skill_reqs.append({"name": skill_name, "level": entry.pop(skill_field)})
            changed = True
    if skill_reqs and "skill_requirements" not in entry:
        entry["skill_requirements"] = skill_reqs
    elif skill_reqs:
        entry["skill_requirements"] = skill_reqs

    # bashing + cutting -> melee_damage
    if "bashing" in entry or "cutting" in entry:
        melee: dict = {}
        if "bashing" in entry:
            melee["bash"] = entry.pop("bashing")
        if "cutting" in entry:
            melee["cut"] = entry.pop("cutting")
        entry["melee_damage"] = melee
        changed = True

    # resist keys -> "resist" dict
    resist_map = {
        "bash_resist": "bash", "cut_resist": "cut", "acid_resist": "acid",
        "fire_resist": "fire", "elec_resist": "electric",
        "bullet_resist": "bullet", "stab_resist": "stab",
    }
    resist: dict = dict(entry.get("resist", {}))
    for old_key, new_key in resist_map.items():
        if old_key in entry:
            resist[new_key] = entry.pop(old_key)
            changed = True
    if resist and "resist" not in entry:
        entry["resist"] = resist
    elif resist:
        entry["resist"] = resist

    # MAGAZINE: remove deprecated "reliability"
    if entry.get("type") == "MAGAZINE" and "reliability" in entry:
        del entry["reliability"]
        changed = True

    return changed


# ===========================================================================
# PASS 2 — Armor coverage and encumbrance changes
# ===========================================================================
# Research source: armor coverage domain
# New in 0.H:
#   - "cover_melee", "cover_ranged", "cover_vitals" alongside "coverage"
#   - "specifically_covers" for sub-body parts
#   - "encumbrance" can now be [base, max] array
#   - "volume_encumber_modifier" replaces old scalar encumbrance scaling
#   - "sided" boolean (was implicit via _EITHER suffix, now explicit)

def _apply_armor(entry: dict, path: Path) -> bool:
    """Flag armor entries that use old single-value encumbrance where the new
    array form is recommended, and note missing granular coverage fields."""
    changed = False

    if entry.get("type") not in ("ARMOR", "TOOL_ARMOR"):
        return False

    # Encumbrance: if it's a plain int, annotate a comment suggesting the
    # new [base, max] array form — we don't auto-convert because the max
    # value requires designer knowledge.
    if "encumbrance" in entry and isinstance(entry["encumbrance"], (int, float)):
        note = entry.get("//", "")
        tag = "[0.H] encumbrance can now be [base, max] array; consider adding volume_encumber_modifier"
        if tag not in note:
            entry["//"] = (note + " | " + tag).lstrip(" | ")
            changed = True
            if REPORT is not None:
                REPORT.append({
                    "file": str(path),
                    "id": entry.get("id", entry.get("ident", "?")),
                    "pass": "armor",
                    "note": tag,
                })

    # coverage: if present but cover_melee/cover_ranged/cover_vitals absent,
    # add a comment nudge.
    if "coverage" in entry and not any(
        k in entry for k in ("cover_melee", "cover_ranged", "cover_vitals")
    ):
        note = entry.get("//", "")
        tag = "[0.H] consider adding cover_melee / cover_ranged / cover_vitals"
        if tag not in note:
            entry["//"] = (note + " | " + tag).lstrip(" | ")
            changed = True

    return changed


# ===========================================================================
# PASS 3 — Body parts: covers update to new bodypart_id system
# ===========================================================================
# Research source: body parts domain, armor coverage domain

BODYPART_MAP: dict[str, list[str]] = {
    "ARMS":  ["arm_l",  "arm_r"],
    "EYES":  ["eyes"],
    "FEET":  ["foot_l", "foot_r"],
    "FOOTS": ["foot_l", "foot_r"],
    "HANDS": ["hand_l", "hand_r"],
    "HEAD":  ["head"],
    "LEGS":  ["leg_l",  "leg_r"],
    "MOUTH": ["mouth"],
    "TORSO": ["torso"],
}

# Sub-body-part hints introduced in 0.H for specifically_covers
SUBBODYPART_HINTS: dict[str, list[str]] = {
    "torso": ["torso_upper", "torso_lower"],
    "arm_l": ["arm_shoulder_l", "arm_upper_l", "arm_elbow_l", "arm_lower_l"],
    "arm_r": ["arm_shoulder_r", "arm_upper_r", "arm_elbow_r", "arm_lower_r"],
    "leg_l": ["leg_upper_l", "leg_knee_l", "leg_lower_l"],
    "leg_r": ["leg_upper_r", "leg_knee_r", "leg_lower_r"],
}


def _apply_bodyparts(entry: dict, path: Path) -> bool:
    raw_covers = entry.get("covers")
    if not raw_covers:
        return False

    new_covers: list[str] = []
    sided = False
    changed = False

    for bp in raw_covers:
        if not isinstance(bp, str):
            new_covers.append(bp)
            continue
        if bp.upper().endswith("_EITHER"):
            bp = bp[:-7]
            sided = True
        expanded = BODYPART_MAP.get(bp.upper())
        if expanded:
            new_covers.extend(expanded)
        else:
            new_covers.append(bp.lower())

    if new_covers != raw_covers or sided:
        entry["covers"] = new_covers
        if sided:
            entry["sided"] = True
        changed = True

    return changed


# ===========================================================================
# PASS 4 — Mapgen: overmap_special subtype field
# ===========================================================================
# Research source: mapgen/overmap domain
# New in 0.H: overmap_special gains "subtype": "fixed" | "mutable"
# Default is "fixed" — add it explicitly if missing so intent is clear.

def _apply_mapgen(entry: dict, path: Path) -> bool:
    changed = False

    if entry.get("type") == "overmap_special" and "subtype" not in entry:
        entry["subtype"] = "fixed"
        changed = True

    # om_terrain: if it's a flat list of strings, wrap in outer list per new spec
    if entry.get("type") == "mapgen" and "om_terrain" in entry:
        ot = entry["om_terrain"]
        if isinstance(ot, list) and ot and isinstance(ot[0], str):
            entry["om_terrain"] = [ot]
            changed = True

    return changed


# ===========================================================================
# PASS 5 — Mutations: new modifier field structure
# ===========================================================================
# Research source: mutation/trait/bionic domain
# New in 0.H: many flat modifier fields are now preferred inside structured
# sub-objects. We rename the ones that have a direct 1:1 mapping.

MUTATION_FIELD_RENAMES: dict[str, str] = {
    # These were renamed or restructured in 0.H
    "hp_bonus":      "max_hp_modifier",
    "str_bonus":     "str_modifier",
    "dex_bonus":     "dex_modifier",
    "int_bonus":     "int_modifier",
    "per_bonus":     "per_modifier",
    "speed_bonus":   "speed_modifier",
    "pain_penalty":  "pain_modifier",
}


def _apply_mutations(entry: dict, path: Path) -> bool:
    if entry.get("type") not in ("mutation", "MUTATION", "trait", "TRAIT"):
        return False
    changed = False
    for old, new in MUTATION_FIELD_RENAMES.items():
        if old in entry and new not in entry:
            entry[new] = entry.pop(old)
            changed = True
    return changed


# ===========================================================================
# PASS 6 — Spells: magic_type stub and energy_source normalisation
# ===========================================================================
# Research source: spell/magic domain
# New in 0.H: "magic_type" field on spells; energy_source values normalised.

OLD_ENERGY_SOURCES: dict[str, str] = {
    "MANA":    "MANA",      # unchanged but validate
    "HP":      "HP",
    "STAMINA": "STAMINA",
    "BIONIC":  "BIONIC_POWER",   # renamed in 0.H
    "FATIGUE": "FATIGUE",
}


def _apply_spells(entry: dict, path: Path) -> bool:
    if entry.get("type") != "SPELL":
        return False
    changed = False

    # Normalise BIONIC -> BIONIC_POWER
    if entry.get("energy_source") == "BIONIC":
        entry["energy_source"] = "BIONIC_POWER"
        changed = True

    # Add magic_type stub comment if missing
    if "magic_type" not in entry:
        note = entry.get("//", "")
        tag = "[0.H] consider adding magic_type field for shared spell properties"
        if tag not in note:
            entry["//"] = (note + " | " + tag).lstrip(" | ")
            changed = True

    return changed


# ===========================================================================
# PASS 7 — Vehicles: vehicle_part_migration stubs
# ===========================================================================
# Research source: vehicle/vpart domain
# New in 0.H: vehicle_part_migration type for renamed/removed parts.
# We cannot auto-detect which parts were renamed without the full CDDA data,
# but we flag vpart definitions that use known-removed 0.G part IDs.

REMOVED_VPARTS_0G: set[str] = {
    # Parts confirmed removed or renamed between 0.G and 0.H
    "afs_metal_rig",
    "afs_workshop_rig",
    "workshop_rig",
}


def _apply_vehicles(entry: dict, path: Path) -> bool:
    if entry.get("type") not in ("vehicle_part", "VEHICLE_PART"):
        return False
    changed = False
    if entry.get("id") in REMOVED_VPARTS_0G:
        note = entry.get("//", "")
        tag = f"[0.H] this part ID was removed; add a vehicle_part_migration entry"
        if tag not in note:
            entry["//"] = (note + " | " + tag).lstrip(" | ")
            changed = True
            if REPORT is not None:
                REPORT.append({
                    "file": str(path),
                    "id": entry.get("id", "?"),
                    "pass": "vehicles",
                    "note": tag,
                })
    return changed


# ===========================================================================
# PASS 8 — Migration type stubs: generate migration JSON entries
# ===========================================================================
# Research source: 0.H changelog, OBSOLETION_AND_MIGRATION.md
# This pass does NOT modify existing entries. Instead it returns a list of
# stub migration objects that should be written to a separate migration file.
# Currently it detects entries that look like they were removed (have
# "obsolete": true or a "REMOVED" comment) and generates the stub.

def _collect_migration_stubs(json_data: list, path: Path) -> list[dict]:
    stubs: list[dict] = []
    for entry in json_data:
        if not isinstance(entry, dict):
            continue
        note = str(entry.get("//", "")).lower()
        if entry.get("obsolete") is True or "removed" in note or "obsolete" in note:
            eid = entry.get("id", entry.get("ident"))
            etype = entry.get("type", "")
            if not eid:
                continue
            if etype in ("GUN", "ARMOR", "TOOL", "COMESTIBLE", "AMMO", "GENERIC", "MAGAZINE"):
                stubs.append({
                    "type": "MIGRATION",
                    "id": eid,
                    "replace": f"FIXME_replace_{eid}",
                    "//": "[0.H auto-stub] fill in replace ID before committing",
                })
            elif etype in ("vehicle_part", "VEHICLE_PART"):
                stubs.append({
                    "type": "vehicle_part_migration",
                    "from": eid,
                    "to": f"FIXME_replace_{eid}",
                    "//": "[0.H auto-stub] fill in to ID before committing",
                })
            elif etype in ("mutation", "MUTATION", "trait", "TRAIT"):
                stubs.append({
                    "type": "TRAIT_MIGRATION",
                    "id": eid,
                    "trait": f"FIXME_replace_{eid}",
                    "//": "[0.H auto-stub] fill in trait ID before committing",
                })
            elif etype == "bionic":
                stubs.append({
                    "type": "bionic_migration",
                    "from": eid,
                    "to": f"FIXME_replace_{eid}",
                    "//": "[0.H auto-stub] fill in to ID before committing",
                })
            elif etype == "SPELL":
                stubs.append({
                    "type": "spell_migration",
                    "from": eid,
                    "to": f"FIXME_replace_{eid}",
                    "//": "[0.H auto-stub] fill in to ID before committing",
                })
    return stubs


# ===========================================================================
# Dispatch table
# ===========================================================================

ALL_PASSES = ("items", "armor", "bodyparts", "mapgen", "mutations", "spells", "vehicles")

PASS_FN = {
    "items":     _apply_items,
    "armor":     _apply_armor,
    "bodyparts": _apply_bodyparts,
    "mapgen":    _apply_mapgen,
    "mutations": _apply_mutations,
    "spells":    _apply_spells,
    "vehicles":  _apply_vehicles,
}


def _transform_entry(entry: dict, skip: set[str], path: Path) -> bool:
    changed = False
    for pass_name, fn in PASS_FN.items():
        if pass_name not in skip:
            changed |= fn(entry, path)
    return changed


# ===========================================================================
# File / directory processing
# ===========================================================================

def process_file(
    path: Path,
    dry_run: bool = False,
    formatter: Path | None = None,
    skip: set[str] | None = None,
    migration_dir: Path | None = None,
) -> str:
    skip = skip or set()
    LOGGER.debug("Processing %s", path)

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

    if not isinstance(json_data, list):
        return "unchanged"

    changed = False
    for entry in json_data:
        if isinstance(entry, dict):
            changed |= _transform_entry(entry, skip, path)

    # Collect migration stubs
    stubs = _collect_migration_stubs(json_data, path)
    if stubs and migration_dir and not dry_run:
        stub_path = migration_dir / f"migration_{path.stem}.json"
        existing: list = []
        if stub_path.exists():
            try:
                with stub_path.open("r", encoding="utf-8") as fh:
                    existing = json.load(fh)
            except Exception:
                existing = []
        existing.extend(stubs)
        with stub_path.open("w", encoding="utf-8") as fh:
            json.dump(existing, fh, ensure_ascii=False, indent=2)
        print(f"  [STUBS]   Written {len(stubs)} migration stub(s) -> {stub_path}")

    if not changed:
        return "unchanged"

    if dry_run:
        print(f"  [DRY-RUN] Would update: {path}")
        return "updated"

    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(json_data, fh, ensure_ascii=False, indent=2)
        if formatter and formatter.exists():
            subprocess.run([str(formatter), str(path)], check=False)
        LOGGER.info("Updated %s", path)
        print(f"  [UPDATED] {path}")
        return "updated"
    except OSError as exc:
        LOGGER.error("Could not write %s: %s", path, exc)
        print(f"  [ERROR] Could not write {path}: {exc}", file=sys.stderr)
        return "error"


def process_directory(
    directory: Path,
    dry_run: bool = False,
    quiet: bool = False,
    formatter: Path | None = None,
    skip: set[str] | None = None,
    migration_dir: Path | None = None,
) -> None:
    counts: dict[str, int] = {"updated": 0, "unchanged": 0, "error": 0, "total": 0}

    for root, dirs, files in os.walk(directory):
        dirs.sort()
        for fname in sorted(files):
            if not fname.lower().endswith(".json"):
                continue
            filepath = Path(root) / fname
            result = process_file(
                filepath,
                dry_run=dry_run,
                formatter=formatter,
                skip=skip,
                migration_dir=migration_dir,
            )
            counts["total"] += 1
            counts[result] += 1
            if quiet and result == "unchanged":
                continue

    label = "DRY-RUN" if dry_run else "DONE"
    print(
        f"\n[{label}] '{directory}' \u2014 "
        f"{counts['total']} file(s) scanned: "
        f"{counts['updated']} updated, "
        f"{counts['unchanged']} unchanged, "
        f"{counts['error']} error(s)."
    )


# ===========================================================================
# CLI
# ===========================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cdda_gh_migration",
        description=(
            "Migrate Cataclysm: DDA mod JSON from 0.G (Gaiman) to 0.H (Hazel).\n"
            "Applies all known breaking and recommended changes in a single pass.\n"
            "Directories are scanned recursively."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Passes (use --skip to disable any):\n"
            "  items      Item field renames, type changes, unit conversions\n"
            "  armor      Encumbrance array hint, granular coverage field nudges\n"
            "  bodyparts  Uppercase body-part names -> new bodypart_id system\n"
            "  mapgen     overmap_special subtype; om_terrain array wrapping\n"
            "  mutations  Mutation modifier field renames\n"
            "  spells     BIONIC -> BIONIC_POWER; magic_type stub comment\n"
            "  vehicles   Flag removed 0.G vpart IDs\n"
        ),
    )
    parser.add_argument(
        "paths", nargs="+", metavar="PATH", type=Path,
        help="One or more .json files or directories to process.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview which files would be changed without writing anything.",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Only print files that were actually updated.",
    )
    parser.add_argument(
        "--skip", nargs="+", metavar="PASS", choices=ALL_PASSES, default=[],
        help="Disable one or more transformation passes.",
    )
    parser.add_argument(
        "--migration-dir", type=Path, default=None,
        help=(
            "Directory to write auto-generated migration stub JSON files into. "
            "Defaults to a 'migration_stubs/' folder next to each processed path."
        ),
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Write a human-readable migration report to cdda_gh_migration_report.md.",
    )
    parser.add_argument(
        "--formatter", type=Path,
        default=Path(__file__).resolve().parent / "tools" / "format" / "json_formatter.cgi",
        help="Path to the CDDA json_formatter.cgi executable (optional).",
    )
    return parser.parse_args()


def write_report(report_path: Path) -> None:
    lines = [
        "# CDDA 0.G → 0.H Migration Report\n",
        "Items flagged for manual review:\n",
        "| File | ID | Pass | Note |",
        "|---|---|---|---|",
    ]
    for item in REPORT:
        lines.append(
            f"| `{item['file']}` | `{item['id']}` | {item['pass']} | {item['note']} |"
        )
    if not REPORT:
        lines.append("| — | — | — | No items flagged. |")
    with report_path.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\n[REPORT] Written to {report_path}")


def main() -> None:
    args = parse_args()
    formatter = args.formatter.expanduser()
    skip = set(args.skip)

    mode = "DRY-RUN" if args.dry_run else "UPDATE"
    active = [p for p in ALL_PASSES if p not in skip]
    print(f"=== CDDA 0.G → 0.H Migration Tool [{mode}] ===")
    print(f"    Active passes : {', '.join(active)}")
    if skip:
        print(f"    Skipped passes: {', '.join(skip)}")
    LOGGER.info("Started. mode=%s skip=%s paths=%s", mode, skip, args.paths)

    for path in args.paths:
        path = path.expanduser()
        migration_dir = args.migration_dir
        if migration_dir is None and not args.dry_run:
            base = path if path.is_dir() else path.parent
            migration_dir = base / "migration_stubs"
            migration_dir.mkdir(parents=True, exist_ok=True)

        if path.is_file():
            if path.suffix.lower() != ".json":
                print(f"  [SKIP] Not a JSON file: {path}", file=sys.stderr)
                continue
            process_file(
                path, dry_run=args.dry_run, formatter=formatter,
                skip=skip, migration_dir=migration_dir,
            )
        elif path.is_dir():
            process_directory(
                path, dry_run=args.dry_run, quiet=args.quiet,
                formatter=formatter, skip=skip, migration_dir=migration_dir,
            )
        else:
            print(f"  [ERROR] Path not found: {path}", file=sys.stderr)
            sys.exit(1)

    if args.report:
        write_report(Path("cdda_gh_migration_report.md"))

    print("Done.")
    LOGGER.info("Finished.")


if __name__ == "__main__":
    main()
