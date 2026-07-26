#!/usr/bin/env python3
"""Resolve known cross-file duplicate IDs in Fallout CDDA Remastered.

The loader rejects two definitions with the same type and ID from one mod.  This
script preserves the more focused definition, removes only the obsolete object,
and renames genuinely distinct NPC equipment pools rather than dropping them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REMOVE: dict[str, set[tuple[str, str]]] = {
    "Items/armor/armor.json": {("ARMOR", "jumpsuit_vault")},
    "Items/combestible/capital_combestible.json": {
        ("COMESTIBLE", "macaroni_blamco_raw"),
        ("COMESTIBLE", "can_cram"),
        ("COMESTIBLE", "instamash_raw"),
        ("COMESTIBLE", "instamash_cooked"),
        ("COMESTIBLE", "fancylad"),
        ("COMESTIBLE", "sugarbombs"),
    },
    "Items/weaponry/casing.json": {("GENERIC", "20ga_hull")},
    "Items/weaponry/ammo_heavy.json": {("AMMO", "47mm_caseless")},
    "Items/weaponry/gun_shot.json": {("GUN", "caravan_shotgun")},
    "Items/weaponry/gun_cowboy.json": {("GUN", "revolver_ranger")},
    "Items/zeta/materials_zetan.json": {("AMMO", "zetan_sheet")},
    "Mobs/Monsters/reptiles.json": {
        ("MONSTER", "mon_deathclaw"),
        ("MONSTER", "mon_deathclaw_young"),
        ("MONSTER", "mon_deathclaw_mother"),
    },
    "Mobs/NPCs/BoS_Paladin.json": {
        ("item_group", "NC_BOSPAL_carry"),
        ("item_group", "NC_BOSPAL_weapon"),
    },
    "Mobs/NPCs/ncr_ranger.json": {("item_group", "drops_ncr_trooper_melee")},
    "Mobs/NPCs/vault_hostile_npc.json": {("item_group", "mon_vault_vault_dweller_guns")},
    "Mobs/NPCs/vault_hostile_npc.json#athlete": {
        ("item_group", "mon_vault_vault_dweller_melee_athlete")
    },
    "Vehicles/vehicleparts/vehicle_parts.json": {
        ("vehicle_part", "mounted_ak112"),
        ("vehicle_part", "mounted_cz53"),
        ("vehicle_part", "mounted_avenger"),
        ("vehicle_part", "mounted_10mm_gatling"),
        ("vehicle_part", "mounted_bozar"),
    },
}


def object_key(obj: dict[str, Any]) -> tuple[str, str] | None:
    ident = obj.get("id", obj.get("abstract"))
    if not isinstance(ident, str):
        return None
    return str(obj.get("type", "")), ident


def load(path: Path) -> list[Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError(f"expected a top-level array: {path}")
    return value


def save(path: Path, value: list[Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def remove_keys(root: Path, rel: str, keys: set[tuple[str, str]]) -> int:
    path = root / rel.split("#", 1)[0]
    value = load(path)
    kept: list[Any] = []
    removed = 0
    for obj in value:
        if isinstance(obj, dict) and object_key(obj) in keys:
            removed += 1
            continue
        kept.append(obj)
    if removed:
        save(path, kept)
    return removed


def rename_nth(root: Path, rel: str, old: str, new: str, occurrence: int) -> None:
    path = root / rel
    value = load(path)
    seen = 0
    changed = False
    for obj in value:
        if not isinstance(obj, dict):
            continue
        if obj.get("id") == old:
            seen += 1
            if seen == occurrence:
                obj["id"] = new
                changed = True
        if seen >= occurrence:
            # References after the renamed definition belong to its local NPC block.
            for key in ("worn_override", "carry_override", "weapon_override", "class"):
                if obj.get(key) == old:
                    obj[key] = new
                    changed = True
            entries = obj.get("entries")
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict) and entry.get("group") == old:
                        entry["group"] = new
                        changed = True
    if not changed:
        raise ValueError(f"could not rename occurrence {occurrence} of {old} in {rel}")
    save(path, value)


def rename_all(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    value = load(path)
    changed = False
    for obj in value:
        if not isinstance(obj, dict):
            continue
        for key in ("id", "class", "worn_override", "carry_override", "weapon_override"):
            if obj.get(key) == old:
                obj[key] = new
                changed = True
    if not changed:
        raise ValueError(f"could not rename {old} in {rel}")
    save(path, value)


def replace_group_in_object(root: Path, rel: str, object_id: str, old: str, new: str) -> None:
    path = root / rel
    value = load(path)
    changed = False
    for obj in value:
        if not isinstance(obj, dict) or obj.get("id") != object_id:
            continue
        for key in ("worn_override", "carry_override", "weapon_override"):
            if obj.get(key) == old:
                obj[key] = new
                changed = True
        for entry in obj.get("entries", []):
            if isinstance(entry, dict) and entry.get("group") == old:
                entry["group"] = new
                changed = True
    if not changed:
        raise ValueError(f"could not update {old} reference in {object_id} ({rel})")
    save(path, value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    removed = 0
    for rel, keys in REMOVE.items():
        removed += remove_keys(root, rel, keys)

    # Preserve distinct loadouts by giving the later/local definition its own ID.
    rename_nth(root, "Mobs/NPCs/BoS_Scribe.json", "NC_BOSSCRIBE_worn", "NC_BOSSCRIBE_RECRUIT_worn", 2)
    replace_group_in_object(
        root,
        "Mobs/NPCs/BoS_Scribe.json",
        "fo_bos_scribe_recruit_npc",
        "NC_BOSSCRIBE_worn",
        "NC_BOSSCRIBE_RECRUIT_worn",
    )
    rename_nth(root, "Mobs/NPCs/legion_troop.json", "drops_leg_gun", "drops_leg_v_gun", 2)
    replace_group_in_object(
        root,
        "Mobs/NPCs/legion_troop.json",
        "NC_CLG_V_weapon",
        "drops_leg_gun",
        "drops_leg_v_gun",
    )
    rename_all(
        root,
        "Mobs/NPCs/wasteland_scavenger.json",
        "fo_deathclaw_hunter_npc",
        "fo_wasteland_scavenger_npc",
    )
    rename_all(
        root,
        "Mobs/NPCs/vault_friendly_npc.json",
        "mon_vault_vault_dweller_melee",
        "mon_vault_friendly_dweller_melee",
    )

    # The same-file ammunition-type duplicate differs only in display wording.
    ammo_types = root / "Items/weaponry/ammo_types.json"
    values = load(ammo_types)
    found = False
    result: list[Any] = []
    for obj in values:
        if isinstance(obj, dict) and object_key(obj) == ("ammunition_type", "bbrocket"):
            if found:
                removed += 1
                continue
            found = True
        result.append(obj)
    if result != values:
        save(ammo_types, result)

    print(f"removed={removed}; renamed_distinct_definitions=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
