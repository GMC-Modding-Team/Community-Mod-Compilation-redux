#!/usr/bin/env python3
"""Repair common legacy mod JSON patterns for Cataclysm: DDA 0.H.

The transformations in this file are intentionally type-aware.  In
particular, item ``variants`` and vehicle-part ``variants`` are unrelated
schemas and must never be treated as interchangeable.
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


ITEM_TYPES = {
    "AMMO",
    "ARMOR",
    "BATTERY",
    "BIONIC_ITEM",
    "BOOK",
    "COMESTIBLE",
    "ENGINE",
    "GENERIC",
    "GUN",
    "GUNMOD",
    "MAGAZINE",
    "PET_ARMOR",
    "TOOL",
    "TOOLMOD",
    "TOOL_ARMOR",
    "WHEEL",
}
H_BASE_COLORS = {
    "black",
    "blue",
    "brown",
    "cyan",
    "dark_gray",
    "green",
    "light_blue",
    "light_cyan",
    "light_gray",
    "light_green",
    "light_red",
    "magenta",
    "pink",
    "red",
    "white",
    "yellow",
}
ARMOR_TYPES = {"ARMOR", "TOOL_ARMOR"}
TOOL_TYPES = {"TOOL", "TOOL_ARMOR"}
SPECIAL_POCKETS = {"CABLE", "CORPSE", "MIGRATION", "MOD"}
LEGACY_VEHICLE_PARTS = {
    "kitchen_unit": ["veh_tools_kitchen"],
    "mounted_browning": ["turret_m2browning"],
    "wheel_small_steerable": ["wheel_mount_light_steerable", "wheel_motorbike"],
    "wheel_motorbike_steerable": ["wheel_mount_light_steerable", "wheel_motorbike"],
    "wheel_armor_steerable": ["wheel_mount_heavy_steerable", "wheel_armor"],
    "wheel_wide_steerable": ["wheel_mount_medium_steerable", "wheel_wide"],
    "xlframe_cross": ["xlframe#cross"],
    "xlframe_horizontal": ["xlframe#horizontal"],
    "xlframe_ne": ["xlframe#ne"],
    "xlframe_nw": ["xlframe#nw"],
    "xlframe_se": ["xlframe#se"],
    "xlframe_sw": ["xlframe#sw"],
    "xlframe_vertical": ["xlframe#vertical"],
    "xlframe_vertical_2": ["xlframe#vertical_2"],
    "frame_horizontal": ["frame#horizontal"],
    "frame_vertical": ["frame#vertical"],
    "hdframe_horizontal": ["hdframe#horizontal"],
    "hdframe_cover": ["hdframe#cover"],
    "hdframe_vertical": ["hdframe#vertical"],
}
WHEEL_MOUNTS = {
    "wheel": "wheel_mount_medium",
    "wheel_slick": "wheel_mount_medium",
    "wheel_armor": "wheel_mount_heavy",
    "wheel_motorbike": "wheel_mount_light",
    "wheel_motorbike_or": "wheel_mount_light",
    "wheel_bicycle": "wheel_mount_light",
    "wheel_bicycle_or": "wheel_mount_light",
    "wheel_wide": "wheel_mount_medium",
    "wheel_wide_or": "wheel_mount_medium",
}
MONSTER_TRIGGERS = {
    "anger_triggers": {
        "FIRE", "FRIEND_ATTACKED", "FRIEND_DIED", "HOSTILE_SEEN", "HURT",
        "MATING_SEASON", "PLAYER_CLOSE", "PLAYER_NEAR_BABY", "PLAYER_WEAK",
        "SOUND", "STALK",
    },
    "fear_triggers": {
        "BRIGHT_LIGHT", "FIRE", "FRIEND_ATTACKED", "FRIEND_DIED",
        "HOSTILE_SEEN", "HURT", "PLAYER_CLOSE", "SOUND",
    },
    "placate_triggers": {"HURT", "PLAYER_WEAK"},
}
BODY_PARTS = {
    "ARM": ["arm_l", "arm_r"],
    "ARMS": ["arm_l", "arm_r"],
    "EYES": ["eyes"],
    "FOOT": ["foot_l", "foot_r"],
    "FEET": ["foot_l", "foot_r"],
    "FOOTS": ["foot_l", "foot_r"],
    "HAND": ["hand_l", "hand_r"],
    "HANDS": ["hand_l", "hand_r"],
    "HEAD": ["head"],
    "LEG": ["leg_l", "leg_r"],
    "LEGS": ["leg_l", "leg_r"],
    "MOUTH": ["mouth"],
    "TORSO": ["torso"],
}
LAYER_MAP = {
    "UNDERWEAR": "SKINTIGHT",
    "SKINTIGHT": "SKINTIGHT",
    "REGULAR": "NORMAL",
    "NORMAL": "NORMAL",
    "WAIST": "BELTED",
    "OUTER": "OUTER",
    "BELTED": "BELTED",
    "AURA": "AURA",
}
HUMAN_TEXT_KEYS = {
    "accepted",
    "activation_message",
    "advice",
    "deactivation_message",
    "desc",
    "describe",
    "description",
    "dynamic_line",
    "failure",
    "failure_message",
    "friendly_msg",
    "gendered_line",
    "info",
    "menu_text",
    "message",
    "messages",
    "msg",
    "mutagen_message",
    "name",
    "no",
    "offer",
    "player_descriptions",
    "rejected",
    "responses",
    "snippet",
    "sound",
    "success",
    "summon_msg",
    "text",
    "use_message",
    "yes",
}
RECIPE_CATEGORY_DEFAULTS = {
    "CC_AMMO": ("CC_AMMO", "CSC_AMMO_OTHER"),
    "CC_ARMOR": ("CC_ARMOR", "CSC_ARMOR_OTHER"),
    "CC_CHEM": ("CC_CHEM", "CSC_CHEM_OTHER"),
    "CC_DRINK": ("CC_FOOD", "CSC_FOOD_DRINKS"),
    "CC_ELECTRONIC": ("CC_ELECTRONIC", "CSC_ELECTRONIC_OTHER"),
    "CC_FOOD": ("CC_FOOD", "CSC_FOOD_OTHER"),
    "CC_MISC": ("CC_OTHER", "CSC_OTHER_OTHER"),
    "CC_OTHER": ("CC_OTHER", "CSC_OTHER_OTHER"),
    "CC_TOOL": ("CC_OTHER", "CSC_OTHER_TOOLS"),
    "CC_WEAPON": ("CC_WEAPON", "CSC_WEAPON_OTHER"),
}
OBSOLETE_IUSE_ACTIONS = {
    "CAFF",
    "CIG",
    "CRACK",
    "DEJAR",
    "DEVAC",
    "EXTRA_BATTERY",
    "FIRSTAID",
    "GASMASK",
    "HALLU",
    "JACQUESHAMMER",
    "MUTAGEN",
    "NONE",
    "PDA",
    "PDA_FLASHLIGHT",
    "PHEROMONE",
    "PKILL",
    "SET_TRAP",
    "SLEEP",
    "UNFOLD_BICYCLE",
    "UPS_ON",
    "VACCINE",
    "WEED",
    "adv_UPS_OFF",
    "adv_UPS_ON",
    "CATFOOD",
    "DOGFOOD",
}
OBSOLETE_ITEM_FLAGS = {
    "FIRE_20",
    "FIRE_50",
    "HELMET_COMPAT",
    "MODE_BURST",
    "NO_QUICKDRAW",
    "PKILL_2",
    "PKILL_3",
    "PKILL_4",
    "RAPID",
    "UNARMED_WEAPON",
    "UNSAFE_CONSUME",
    "WATER_FRIENDLY",
}
UNCHARGED_GROUP_ITEMS = {
    "apple_canned",
    "can_tomato",
    "fish_pickled",
    "meat_canned",
    "meat_pickled",
    "slime_scrap",
    "veggy_canned",
    "veggy_pickled",
}
OBSOLETE_TECHNIQUES = {
    "tec_brawl_counter_unarmed",
    "tec_dragon_blockcounter",
    "tec_dragon_dodgecounter",
    "tec_sojutsu_push",
}
H_ENCHANTMENT_VALUE_MIGRATIONS = {
    "ATTACK_COST": "ATTACK_SPEED",
    "REGEN_HP_AWAKE": "REGEN_HP",
    "SLEEPINESS": "FATIGUE",
    "SLEEPINESS_REGEN": "FATIGUE",
    "STAMINA_REGEN_MOD": "REGEN_STAMINA",
}
H_ENCHANTMENT_VALUE_EXPANSIONS = {
    "ARMOR_ALL": [
        "ARMOR_ACID",
        "ARMOR_BASH",
        "ARMOR_BIO",
        "ARMOR_BULLET",
        "ARMOR_COLD",
        "ARMOR_CUT",
        "ARMOR_ELEC",
        "ARMOR_HEAT",
        "ARMOR_STAB",
    ],
}
H_MELEE_DAMAGE_BONUS_VALUES = {
    "acid": "EXTRA_ACID",
    "bash": "EXTRA_BASH",
    "biological": "EXTRA_BIO",
    "bio": "EXTRA_BIO",
    "bullet": "EXTRA_BULLET",
    "cold": "EXTRA_COLD",
    "cut": "EXTRA_CUT",
    "electric": "EXTRA_ELEC",
    "heat": "EXTRA_HEAT",
    "stab": "EXTRA_STAB",
}
H_UNSUPPORTED_ENCHANTMENT_VALUES = {
    "BIONIC_MANA_PENALTY",
    "BODYTEMP_SLEEP",
    "CARDIO_MULTIPLIER",
    "CRAFTING_SPEED_MULTIPLIER",
    "DODGE_CHANCE",
    "EQUIPMENT_DAMAGE_CHANCE",
    "HEARING_MULT",
    "ITEM_DAMAGE_AP",
    "MELEE_STAMINA_CONSUMPTION",
    "MENDING_MODIFIER",
    "MOVECOST_FLATGROUND_MOD",
    "MOVECOST_OBSTACLE_MOD",
    "MOVECOST_SWIM_MOD",
    "NIGHT_VIS",
    "OVERMAP_SIGHT",
    "POWER_TRICKLE",
    "READING_SPEED_MULTIPLIER",
    "SIGHT_RANGE_FAE",
    "STEALTH_MODIFIER",
    "STOMACH_SIZE_MULTIPLIER",
}
H_OVERMAP_SEE_COSTS = {
    "all_clear": 0,
    "none": 0,
    "low": 1,
    "medium": 2,
    "spaced_high": 4,
    "high": 5,
    "full_high": 10,
    "opaque": 999,
}
AMMO_TYPE_MIGRATIONS = {
    ".45": "45",
    "40mm": "40x46mm",
    "700nx": "458wm",
    "fusion": "battery",
}
ITEM_ID_MIGRATIONS = {
    "700nx": "458wm",
    "762_m43": "762_m87",
    "kitchen_unit": "veh_tools_kitchen",
    "weldrig": "welder",
    "mess_tin": "mess_kit",
    "jar_3l_glass": "jar_3l_glass_sealed",
    "chem_match_head_powder": "chem_black_powder",
    "ammonia": "ammonia_hydroxide",
    "rebar_rail": "rebar",
    "steel_rail": "railroad_track_small",
    "90two": "m9",
    "acid": "chem_muriatic_acid",
    "adv_UPS_off": "UPS_off",
    "m4a1": "modular_m4_carbine",
    "water_acid": "chem_muriatic_acid",
    "water_acid_weak": "chem_muriatic_acid",
}
OBSOLETE_MAPGEN_OM_IDS = {"FEMA_be", "bunker_basement", "house"}
OBSOLETE_ITEM_IDS = {
    "1st_aid",
    "aep_suit",
    "antagonizercomic",
    "armor_scavenger",
    "chaingangcomic",
    "chloroform_rag",
    "drivingzen",
    "electron_charge_pack_mod",
    "electronics_deans",
    "electronics_deans_vault",
    "fission_battery_mod",
    "fusion_core_mod",
    "grognakcomic",
    "gunrunnerbook",
    "holybook_fbible",
    "holybook_hintbook",
    "holybook_krivbeknih",
    "jar_3l_glass",
    "jerky_vendor",
    "mag_astounding",
    "mag_catspaw",
    "mag_chivalry",
    "mag_comic_fantoma",
    "mag_comic_police",
    "mag_pugilism",
    "mag_unstoppables",
    "mantamancomic",
    "manual_arroyo",
    "manual_boxing_newreno",
    "manual_gecko",
    "micro_fusion_cell_mod",
    "rag_bloody",
    "scout_guide",
    "shroudcomic",
    "small_energy_cell_mod",
    "toolbox",
    "totalhack",
    "tricksandtraps",
    "wasteland_survival_guide",
    "wastelandgunsmith",
}
TERRAIN_ID_MIGRATIONS = {
    "t_centrifuge": "t_floor",
    "t_machinery_electronic": "t_floor",
    "t_machinery_heavy": "t_floor",
    "t_machinery_light": "t_floor",
    "t_plut_generator": "t_floor",
    "t_generator_broken": "t_floor",
    "t_machinery_old": "t_floor",
}
FURNITURE_ID_MIGRATIONS = {"f_robotic_assembler": "f_rack"}
ITEM_GROUP_MIGRATIONS = {
    "ammo_fallout_rifle_common": "ammo_rifle_fallout_common",
    "bionics_op": "bionics_common",
    "bionics_op2_off": "bionics_common",
    "bionics_tech": "bionics_common",
    "fallout_glow_fatman": "military",
    "guns_fallout_rifle_common": "guns_rifle_fallout_common",
    "library_elec": "elecsto_books",
    "mine_storage": "tools_earthworking",
    "rare": "military",
}
MONSTER_ID_MIGRATIONS = {"mon_turret_light": "mon_turret"}
OBSOLETE_MONSTER_IDS = {
    "mon_chickenbot",
    "mon_copbot",
    "mon_eyebot",
    "mon_riotbot",
    "mon_tankbot",
    "mon_tripod",
}
OBSOLETE_MONSTER_FLAGS = {
    "ABSORBS",
    "BIRDFOOD",
    "BLEED",
    "BONES",
    "CATFOOD",
    "CBM_CIV",
    "CBM_POWER",
    "CBM_TECH",
    "CATTLEFODDER",
    "CHITIN",
    "DOGFOOD",
    "FAT",
    "FUR",
    "GUILT",
    "LARVA",
    "LEATHER",
}
MONSTER_FACTION_MIGRATIONS = {
    "ant_hack": "ant",
    "ant_male": "ant",
    "bear_mating": "bear",
    "doom": "nether",
    "finfected": "fungus",
    "fish_predator": "aquatic_predator",
    "mutant_omnivore": "mutant",
    "mutant_predator": "mutant",
    "mutant_small": "mutant",
    "pidgeon": "small_animal",
    "shadow": "nether",
    "spore": "fungus",
    "upper_doom": "nether",
    "wildlife": "animal",
    "zed_doom": "zombie",
}
OBSOLETE_BIONIC_IDS = {"bio_furnace"}
OBSOLETE_RECIPE_RESULT_IDS = {"broken_tripod"}
LOOPING_ACID_RECIPE_RESULTS = {
    "chem_muriatic_acid",
    "chem_sulphuric_acid",
    "chem_nitric_acid",
}
LEGACY_VARIANT_PART_BASES = {
    "aisle",
    "clothboard",
    "frame",
    "halfboard",
    "hdboard",
    "hdframe",
    "hdhalfboard",
    "wooden_aisle",
}
LEGACY_VARIANT_SUFFIXES = {
    "cross",
    "horizontal",
    "horizontal_2",
    "ne",
    "nw",
    "se",
    "sw",
    "vertical",
    "vertical_2",
}


def strip_json_comments(text: str) -> str:
    """Replace JavaScript-style comments with whitespace outside strings."""
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        char = text[i]
        next_char = text[i + 1] if i + 1 < len(text) else ""
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if char == '"':
            in_string = True
            out.append(char)
            i += 1
            continue
        if char == "/" and next_char == "/":
            out.extend((" ", " "))
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                out.append(" ")
                i += 1
            continue
        if char == "/" and next_char == "*":
            out.extend((" ", " "))
            i += 2
            while i < len(text):
                if i + 1 < len(text) and text[i : i + 2] == "*/":
                    out.extend((" ", " "))
                    i += 2
                    break
                out.append(text[i] if text[i] in "\r\n" else " ")
                i += 1
            continue
        out.append(char)
        i += 1
    return "".join(out)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def dedupe(values: list[Any]) -> tuple[list[Any], int]:
    seen: set[str] = set()
    result: list[Any] = []
    removed = 0
    for value in values:
        encoded = canonical(value)
        if encoded in seen:
            removed += 1
            continue
        seen.add(encoded)
        result.append(value)
    return result, removed


def top_level_identity(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, dict) or not isinstance(value.get("type"), str):
        return None
    obj_type = value["type"]
    ident = value.get("id", value.get("abstract"))
    if obj_type == "MONSTER_FACTION":
        ident = value.get("name")
    elif obj_type == "monstergroup":
        ident = value.get("name")
    if not isinstance(ident, str) or not ident:
        return None
    namespace = "ITEM" if obj_type.upper() in ITEM_TYPES else obj_type
    return namespace, ident


def definition_quality(value: dict[str, Any]) -> tuple[int, int]:
    encoded = canonical(value)
    score = len(value) * 100 + len(encoded)
    description = value.get("description")
    if isinstance(description, str) and "placeholder for a missing legacy" in description.lower():
        score -= 100_000
    if isinstance(value.get("copy-from"), str):
        score += 10_000
    return score, len(encoded)


def dedupe_top_level_identities(values: list[Any]) -> tuple[list[Any], int]:
    """Keep the strongest definition for duplicate factory IDs in one file."""
    result: list[Any] = []
    positions: dict[tuple[str, str], int] = {}
    removed = 0
    for value in values:
        identity = top_level_identity(value)
        if identity is None or identity not in positions:
            if identity is not None:
                positions[identity] = len(result)
            result.append(value)
            continue
        position = positions[identity]
        existing = result[position]
        if (
            isinstance(value, dict)
            and isinstance(existing, dict)
            and definition_quality(value) >= definition_quality(existing)
        ):
            result[position] = value
        removed += 1
    return result, removed


def remove_keys_recursive(value: Any, keys: set[str]) -> int:
    removed = 0
    if isinstance(value, dict):
        for key in list(value):
            if key in keys:
                del value[key]
                removed += 1
            else:
                removed += remove_keys_recursive(value[key], keys)
    elif isinstance(value, list):
        for child in value:
            removed += remove_keys_recursive(child, keys)
    return removed


def clean_structural_list_entries(value: Any) -> int:
    """Remove only structurally empty list members, preserving semantic strings."""
    removed = 0
    if isinstance(value, dict):
        for child in value.values():
            removed += clean_structural_list_entries(child)
    elif isinstance(value, list):
        kept: list[Any] = []
        for child in value:
            if child is None or child == {} or child == []:
                removed += 1
                continue
            removed += clean_structural_list_entries(child)
            kept.append(child)
        value[:] = kept
    return removed


def normalize_coordinate_ranges(value: Any) -> int:
    changed = 0
    if isinstance(value, dict):
        for key, child in value.items():
            if (
                key in {"x", "y"}
                and isinstance(child, list)
                and len(child) == 2
                and all(isinstance(number, (int, float)) for number in child)
            ):
                if child[0] > child[1]:
                    child[0], child[1] = child[1], child[0]
                    changed += 1
                if all(isinstance(number, int) for number in child) and child[0] // 24 != child[1] // 24:
                    child[1] = (child[0] // 24 + 1) * 24 - 1
                    changed += 1
            else:
                changed += normalize_coordinate_ranges(child)
    elif isinstance(value, list):
        for child in value:
            changed += normalize_coordinate_ranges(child)
    return changed


def normalize_text_style(text: str) -> str:
    """Apply the automatic fixes required by 0.H's text-style checker."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    text = re.sub(r"\.\s+\.\s+\.", "…", text)
    text = text.replace("...", "…")
    text = re.sub(r" +([!?.,;:])", r"\1", text)
    text = re.sub(r" +\n", "\n", text).rstrip(" ")

    punctuation = {
        ".": (3, 1, 3, 2),
        ";": (1, 1, 2, 1),
        "!": (1, 1, 3, 2),
        "?": (1, 1, 3, 2),
        ":": (1, 1, 1, 1),
        ",": (1, 1, 2, 1),
        "…": (1, 0, 2, 2),
    }
    result: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char not in punctuation:
            result.append(char)
            i += 1
            continue
        word_length = 0
        j = len(result) - 1
        while j >= 0 and (result[j].isalnum() or result[j] == "-"):
            word_length += 1
            j -= 1
        result.append(char)
        i += 1
        if char in "!?":
            while i < len(text) and text[i] in "!?":
                result.append(text[i])
                i += 1
        start_spaces = i
        while i < len(text) and text[i] == " ":
            i += 1
        spaces = i - start_spaces
        min_word, min_spaces, max_spaces, wanted = punctuation[char]
        if i < len(text) and text[i] != "\n" and word_length >= min_word:
            if min_spaces <= spaces <= max_spaces and spaces != wanted:
                spaces = wanted
        result.extend(" " * spaces)
    return "".join(result)


# The original helper above was retained for compatibility with older reports;
# this H-safe implementation uses the actual Unicode ellipsis instead of the
# mojibake sequence present in legacy copies of the script.
def normalize_text_style(text: str) -> str:
    ellipsis = chr(0x2026)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    text = re.sub(r"\.\s+\.\s+\.", ellipsis, text).replace("...", ellipsis)
    text = re.sub(r" +([!?.,;:])", r"\1", text)
    text = re.sub(r" +\n", "\n", text).rstrip(" ")
    punctuation = {
        ".": (3, 1, 3, 2),
        ";": (1, 1, 2, 1),
        "!": (1, 1, 3, 2),
        "?": (1, 1, 3, 2),
        ":": (1, 1, 1, 1),
        ",": (1, 1, 2, 1),
        ellipsis: (1, 0, 2, 2),
    }
    result: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char not in punctuation:
            result.append(char)
            i += 1
            continue
        word_length = 0
        j = len(result) - 1
        while j >= 0 and (result[j].isalnum() or result[j] == "-"):
            word_length += 1
            j -= 1
        result.append(char)
        i += 1
        if char in "!?":
            while i < len(text) and text[i] in "!?":
                result.append(text[i])
                i += 1
        start_spaces = i
        while i < len(text) and text[i] == " ":
            i += 1
        spaces = i - start_spaces
        min_word, min_spaces, max_spaces, wanted = punctuation[char]
        if i < len(text) and text[i] != "\n" and word_length >= min_word:
            if min_spaces <= spaces <= max_spaces and spaces != wanted:
                spaces = wanted
        result.extend(" " * spaces)
    return "".join(result)


def normalize_item_name_plural(name: Any) -> tuple[Any, bool]:
    if not isinstance(name, dict) or not isinstance(name.get("str"), str):
        return name, False
    singular = name["str"]
    if name.get("str_pl") == singular:
        fixed = {key: value for key, value in name.items() if key not in {"str", "str_pl"}}
        fixed["str_sp"] = singular
        return fixed, True
    certainly_irregular = bool(
        re.search(
            r"([^a-zA-Z0-9]$|(s|sh|x|tch|[rtpsdfgklzxcvnm]y|quy|[a-z]by)$|\+[0-9]+$|([ -]with[ -]|[ -]for[ -]))",
            singular,
        )
    )
    if "str_pl" in name and not certainly_irregular and name["str_pl"] == f"{singular}s":
        fixed = dict(name)
        del fixed["str_pl"]
        return fixed, True
    if set(name) != {"str"} or not certainly_irregular:
        return name, False
    lowered = singular.lower()
    if not singular[-1:].isalnum() or re.search(r"\+[0-9]+$", singular):
        return {"str_sp": singular}, True
    if lowered.endswith(("s", "sh", "x", "tch")):
        return {"str": singular, "str_pl": f"{singular}es"}, True
    if lowered.endswith("y") and len(singular) > 1 and lowered[-2] not in "aeiou":
        return {"str": singular, "str_pl": f"{singular[:-1]}ies"}, True
    return {"str": singular, "str_pl": f"{singular}s"}, True


def normalize_human_text(value: Any, counts: collections.Counter[str], human: bool = False) -> None:
    if isinstance(value, dict):
        if human and value.get("str_pl") == value.get("str") and isinstance(value.get("str"), str):
            singular = value["str"]
            value.pop("str", None)
            value.pop("str_pl", None)
            value["str_sp"] = singular
            counts["text_plural_forms"] += 1
        for key, child in list(value.items()):
            child_human = (
                human
                or key in HUMAN_TEXT_KEYS
                or key.endswith("_message")
                or key.endswith("_msg")
            )
            if isinstance(child, str) and child_human:
                fixed = normalize_text_style(child)
                if fixed != child:
                    value[key] = fixed
                    counts["text_style"] += 1
            else:
                normalize_human_text(child, counts, child_human)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, str) and human:
                fixed = normalize_text_style(child)
                if fixed != child:
                    value[index] = fixed
                    counts["text_style"] += 1
            else:
                normalize_human_text(child, counts, human)


def flatten_dynamic_line(value: Any) -> str:
    """Convert legacy conditional dynamic-line objects to H's string form."""
    parts: list[str] = []
    allowed_keys = {"and", "or", "yes", "no", "then", "else", "text", "message"}

    def collect(child: Any, key: str | None = None) -> None:
        if isinstance(child, str):
            if key is None or key in allowed_keys:
                parts.append(child)
            return
        if isinstance(child, list):
            for entry in child:
                collect(entry)
            return
        if isinstance(child, dict):
            for child_key, entry in child.items():
                if child_key in allowed_keys:
                    collect(entry, child_key)

    collect(value)
    return " ".join(part.strip() for part in parts if part.strip()) or "..."


def migrate_terrain_ids(value: Any, counts: collections.Counter[str], terrain_context: bool = False) -> None:
    """Replace removed terrain ids only in mapgen terrain-bearing structures."""
    if isinstance(value, dict):
        for key, child in list(value.items()):
            child_context = terrain_context or key in {"fill_ter", "terrain", "ter", "id"}
            if isinstance(child, str) and child_context and child in TERRAIN_ID_MIGRATIONS:
                value[key] = TERRAIN_ID_MIGRATIONS[child]
                counts["terrain_id_migrations"] += 1
            else:
                migrate_terrain_ids(child, counts, child_context)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, str) and terrain_context and child in TERRAIN_ID_MIGRATIONS:
                value[index] = TERRAIN_ID_MIGRATIONS[child]
                counts["terrain_id_migrations"] += 1
            else:
                migrate_terrain_ids(child, counts, terrain_context)


def migrate_mapgen_ids(
    value: Any, counts: collections.Counter[str], furniture_context: bool = False
) -> None:
    if isinstance(value, dict):
        for key, child in list(value.items()):
            child_furniture_context = furniture_context or key in {"furn", "furniture"}
            if isinstance(child, str) and child_furniture_context and child in FURNITURE_ID_MIGRATIONS:
                value[key] = FURNITURE_ID_MIGRATIONS[child]
                counts["furniture_id_migrations"] += 1
            elif isinstance(child, str) and child in ITEM_GROUP_MIGRATIONS:
                replacement = ITEM_GROUP_MIGRATIONS[child]
                if replacement is None:
                    del value[key]
                else:
                    value[key] = replacement
                counts["mapgen_item_group_migrations"] += 1
            elif key in {"groups", "item_groups"} and isinstance(child, list):
                migrated = [
                    ITEM_GROUP_MIGRATIONS.get(group, group)
                    for group in child
                    if not isinstance(group, str) or ITEM_GROUP_MIGRATIONS.get(group, group) is not None
                ]
                if migrated != child:
                    value[key] = migrated
                    counts["mapgen_item_group_migrations"] += 1
            else:
                migrate_mapgen_ids(child, counts, child_furniture_context)
    elif isinstance(value, list):
        for child in value:
            migrate_mapgen_ids(child, counts, furniture_context)


def clean_mapgen_placements(value: Any, counts: collections.Counter[str]) -> None:
    """Repair legacy per-placement fields without touching computer failures."""
    if isinstance(value, dict):
        if isinstance(value.get("item"), str) and any(key in value for key in ("x", "y", "chance")):
            for obsolete in ("ammo", "charges", "damage", "magazine"):
                if obsolete in value:
                    del value[obsolete]
                    counts["mapgen_item_obsolete_fields"] += 1
        if (
            isinstance(value.get("items"), list)
            and "x" in value
            and "y" in value
            and "prob" in value
            and "chance" not in value
        ):
            value["chance"] = value.pop("prob")
            counts["vehicle_spawn_probabilities"] += 1
        monster = value.get("monster")
        if isinstance(monster, str) and monster in MONSTER_ID_MIGRATIONS:
            value["monster"] = MONSTER_ID_MIGRATIONS[monster]
            counts["mapgen_monster_migrations"] += 1
        for child in value.values():
            clean_mapgen_placements(child, counts)
    elif isinstance(value, list):
        for child in value:
            clean_mapgen_placements(child, counts)


def normalize_mapgen_rows(obj: dict[str, Any], counts: collections.Counter[str]) -> None:
    """Make every textual mapgen row match the map's dominant width.

    Legacy maps occasionally contain a single hand-edited row with an extra or
    missing glyph.  H rejects the entire mapgen in that case.  The dominant
    width preserves the intended map size and is safer than blindly assuming a
    24-column map because multi-OMT mapgens legitimately use wider rows.
    """
    body = obj.get("object")
    if not isinstance(body, dict):
        return
    rows = body.get("rows")
    if not isinstance(rows, list) or not rows or not all(isinstance(row, str) for row in rows):
        return
    widths = collections.Counter(len(row) for row in rows)
    expected = widths.most_common(1)[0][0]
    for index, row in enumerate(rows):
        if len(row) < expected:
            rows[index] = row.ljust(expected)
            counts["mapgen_rows_padded"] += 1
        elif len(row) > expected:
            rows[index] = row[:expected]
            counts["mapgen_rows_trimmed"] += 1


def migrate_shrapnel(value: Any, counts: collections.Counter[str]) -> None:
    if isinstance(value, dict):
        shrapnel = value.get("shrapnel")
        if isinstance(shrapnel, dict):
            mass = shrapnel.pop("mass", None)
            if isinstance(mass, (int, float)) and "fragment_mass" not in shrapnel:
                shrapnel["fragment_mass"] = mass
            if mass is not None:
                counts["shrapnel_mass"] += 1
            if "count" in shrapnel:
                del shrapnel["count"]
                counts["shrapnel_count"] += 1
        for child in value.values():
            migrate_shrapnel(child, counts)
    elif isinstance(value, list):
        for child in value:
            migrate_shrapnel(child, counts)


def migrate_legacy_skills(value: Any, counts: collections.Counter[str]) -> None:
    skill_migrations = {"barter": "speech", "marksmanship": "gun"}
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if key in {"skill", "skill_used"} and isinstance(child, str) and child in skill_migrations:
                value[key] = skill_migrations[child]
                counts["skill_id_migrations"] += 1
            else:
                migrate_legacy_skills(child, counts)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, str) and child in skill_migrations:
                value[index] = skill_migrations[child]
                counts["skill_id_migrations"] += 1
            else:
                migrate_legacy_skills(child, counts)


def migrate_monster_fire_damage(value: Any, counts: collections.Counter[str]) -> None:
    if isinstance(value, dict):
        if value.get("damage_type") == "fire":
            value["damage_type"] = "heat"
            counts["monster_fire_damage"] += 1
        if "fire" in value and "heat" not in value:
            value["heat"] = value.pop("fire")
            counts["monster_fire_armor"] += 1
        for child in value.values():
            migrate_monster_fire_damage(child, counts)
    elif isinstance(value, list):
        for child in value:
            migrate_monster_fire_damage(child, counts)


def clean_explosion_actions(value: Any, counts: collections.Counter[str]) -> None:
    if isinstance(value, dict):
        if str(value.get("type", "")).lower() == "explosion":
            for obsolete in ("no_deactivate_msg", "sound_msg", "sound_volume"):
                if obsolete in value:
                    del value[obsolete]
                    counts["explosion_action_obsolete_fields"] += 1
        for child in value.values():
            clean_explosion_actions(child, counts)
    elif isinstance(value, list):
        for child in value:
            clean_explosion_actions(child, counts)


def clean_legacy_use_actions(value: Any, counts: collections.Counter[str]) -> None:
    """Drop action fields that the 0.H readers no longer accept.

    These are deliberately keyed by the action type so similarly named fields in
    unrelated JSON objects are left alone.
    """
    if isinstance(value, dict):
        action_type = str(value.get("type", "")).lower()
        obsolete: set[str] = set()
        if action_type == "fireweapon_off":
            obsolete.add("lacks_fuel_message")
        elif action_type == "fireweapon_on":
            obsolete.update(
                {
                    "auto_extinguish_chance",
                    "auto_extinguish_message",
                    "voluntary_extinguish_message",
                    # fireweapon_on accepts noise_chance, but not a sound volume.
                    "noise",
                }
            )
        elif action_type == "heal":
            obsolete.add("long_action")
        for key in obsolete:
            if key in value:
                del value[key]
                counts["obsolete_use_action_fields"] += 1
        for child in value.values():
            clean_legacy_use_actions(child, counts)
    elif isinstance(value, list):
        for child in value:
            clean_legacy_use_actions(child, counts)


def clean_dialogue_effects(value: Any, counts: collections.Counter[str]) -> None:
    if isinstance(value, dict):
        if "u_buy_item" in value:
            for obsolete in ("ammo-item", "charges", "container-item"):
                if obsolete in value:
                    del value[obsolete]
                    counts["buy_item_obsolete_fields"] += 1
        for child in value.values():
            clean_dialogue_effects(child, counts)
    elif isinstance(value, list):
        for child in value:
            clean_dialogue_effects(child, counts)


def remove_obsolete_item_refs(value: Any, counts: collections.Counter[str], parent_key: str | None = None) -> None:
    """Remove exact H-missing references while preserving their containing JSON files."""
    if isinstance(value, dict):
        for key in ("container", "container-item"):
            if value.get(key) in OBSOLETE_ITEM_IDS:
                del value[key]
                counts["obsolete_item_references"] += 1
        if value.get("container-item") == "soldering_iron":
            value["container-item"] = "soldering_iron_portable"
            counts["container_item_migrations"] += 1
        books = value.get("book_learn")
        if isinstance(books, list):
            kept_books = [
                book for book in books
                if not (isinstance(book, list) and book and book[0] in OBSOLETE_ITEM_IDS)
            ]
            if kept_books != books:
                if kept_books:
                    value["book_learn"] = kept_books
                else:
                    del value["book_learn"]
                counts["obsolete_recipe_books"] += len(books) - len(kept_books)
        for key, child in list(value.items()):
            if (
                isinstance(child, dict)
                and isinstance(child.get("item"), str)
                and child.get("item") in OBSOLETE_ITEM_IDS
            ):
                del value[key]
                counts["obsolete_item_references"] += 1
                continue
            remove_obsolete_item_refs(child, counts, key)
    elif isinstance(value, list):
        kept: list[Any] = []
        for child in value:
            if (
                isinstance(child, dict)
                and isinstance(child.get("item"), str)
                and child.get("item") in OBSOLETE_ITEM_IDS
            ):
                counts["obsolete_item_references"] += 1
                continue
            if parent_key == "items" and isinstance(child, str) and child in OBSOLETE_ITEM_IDS:
                counts["obsolete_item_references"] += 1
                continue
            kept.append(child)
        if len(kept) != len(value):
            value[:] = kept
        for child in value:
            remove_obsolete_item_refs(child, counts, parent_key)


ITEM_REFERENCE_KEYS = {
    "ammo-item",
    "built_in_mods",
    "components",
    "container",
    "container-item",
    "contents-item",
    "copy-from",
    "default_magazine",
    "item",
    "items",
    "looks_like",
    "magazine",
    "result",
    "revert_to",
    "revert_to_itype",
    "tool",
    "tools",
}


def migrate_item_id_references(
    value: Any, counts: collections.Counter[str], parent_key: str | None = None
) -> None:
    """Apply exact core item migrations only in item-bearing JSON fields."""
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if isinstance(child, str) and key in ITEM_REFERENCE_KEYS and child in ITEM_ID_MIGRATIONS:
                value[key] = ITEM_ID_MIGRATIONS[child]
                counts["item_id_migrations"] += 1
            else:
                migrate_item_id_references(child, counts, key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, str) and parent_key in ITEM_REFERENCE_KEYS and child in ITEM_ID_MIGRATIONS:
                value[index] = ITEM_ID_MIGRATIONS[child]
                counts["item_id_migrations"] += 1
            else:
                # Recipe components and item-group pairs remain in the same
                # item-bearing context through their nested arrays.
                migrate_item_id_references(child, counts, parent_key)


def remove_obsolete_monster_refs(
    value: Any, counts: collections.Counter[str], obsolete_ids: set[str]
) -> None:
    """Remove placements/actions for monsters that no longer exist in core H."""
    if isinstance(value, dict):
        monsters = value.get("monsters")
        if isinstance(monsters, list):
            kept = [
                child
                for child in monsters
                if not (
                    isinstance(child, dict)
                    and isinstance(child.get("monster"), str)
                    and child.get("monster") in obsolete_ids
                )
            ]
            if kept != monsters:
                value["monsters"] = kept
                counts["obsolete_monster_references"] += len(monsters) - len(kept)
        default = value.get("default")
        if isinstance(default, str) and default in obsolete_ids:
            replacement = next(
                (
                    child.get("monster")
                    for child in value.get("monsters", [])
                    if isinstance(child, dict)
                    and isinstance(child.get("monster"), str)
                    and child.get("monster") not in obsolete_ids
                ),
                None,
            )
            if replacement:
                value["default"] = replacement
            else:
                del value["default"]
            counts["obsolete_monster_defaults"] += 1
        for key, child in list(value.items()):
            if (
                isinstance(child, dict)
                and (
                    (
                        isinstance(child.get("monster"), str)
                        and child.get("monster") in obsolete_ids
                    )
                    or (
                        isinstance(child.get("monster_id"), str)
                        and child.get("monster_id") in obsolete_ids
                    )
                )
            ):
                del value[key]
                counts["obsolete_monster_references"] += 1
                continue
            remove_obsolete_monster_refs(child, counts, obsolete_ids)
    elif isinstance(value, list):
        kept = [
            child
            for child in value
            if not (
                isinstance(child, dict)
                and (
                    (
                        isinstance(child.get("monster"), str)
                        and child.get("monster") in obsolete_ids
                    )
                    or (
                        isinstance(child.get("monster_id"), str)
                        and child.get("monster_id") in obsolete_ids
                    )
                )
            )
        ]
        if kept != value:
            counts["obsolete_monster_references"] += len(value) - len(kept)
            value[:] = kept
        for child in value:
            remove_obsolete_monster_refs(child, counts, obsolete_ids)


def migrate_monster_factions(value: Any, counts: collections.Counter[str]) -> None:
    faction_keys = {"base_faction", "by_mood", "default_faction", "faction", "friendly", "hate", "neutral"}
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if isinstance(child, str) and key in faction_keys and child in MONSTER_FACTION_MIGRATIONS:
                value[key] = MONSTER_FACTION_MIGRATIONS[child]
                counts["monster_faction_migrations"] += 1
            elif isinstance(child, list) and key in faction_keys:
                migrated = [
                    MONSTER_FACTION_MIGRATIONS.get(entry, entry) if isinstance(entry, str) else entry
                    for entry in child
                ]
                migrated = list(dict.fromkeys(migrated))
                if migrated != child:
                    value[key] = migrated
                    counts["monster_faction_migrations"] += 1
            else:
                migrate_monster_factions(child, counts)
    elif isinstance(value, list):
        for child in value:
            migrate_monster_factions(child, counts)


def migrate_effect_mod_keys(value: Any, counts: collections.Counter[str]) -> None:
    """0.H renamed effect sleepiness modifiers back to fatigue modifiers."""
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if key.startswith("sleepiness_"):
                migrated_key = f"fatigue_{key[len('sleepiness_') :]}"
                if migrated_key not in value:
                    value[migrated_key] = child
                del value[key]
                counts["effect_sleepiness_modifiers"] += 1
                child = value.get(migrated_key)
            migrate_effect_mod_keys(child, counts)
    elif isinstance(value, list):
        for child in value:
            migrate_effect_mod_keys(child, counts)


def migrate_rotating_overmaps(
    value: Any,
    rotating_bases: set[str],
    nonrotating_bases: set[str],
    counts: collections.Counter[str],
) -> None:
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if key == "overmap" and isinstance(child, str):
                if child in rotating_bases:
                    value[key] = f"{child}_north"
                    counts["rotating_overmap_ids"] += 1
                elif child.endswith("_north") and child[:-6] in nonrotating_bases:
                    value[key] = child[:-6]
                    counts["nonrotating_overmap_ids"] += 1
            else:
                migrate_rotating_overmaps(child, rotating_bases, nonrotating_bases, counts)
    elif isinstance(value, list):
        for child in value:
            migrate_rotating_overmaps(child, rotating_bases, nonrotating_bases, counts)


def normalize_comment_keys(value: Any, counts: collections.Counter[str]) -> None:
    if isinstance(value, dict):
        if "_comment" in value:
            comment = value.pop("_comment")
            if "//" not in value:
                value["//"] = comment
            counts["comment_keys"] += 1
        for child in value.values():
            normalize_comment_keys(child, counts)
    elif isinstance(value, list):
        for child in value:
            normalize_comment_keys(child, counts)


def normalize_covers(value: Any) -> tuple[Any, bool]:
    if isinstance(value, str):
        covers = [value]
    elif isinstance(value, list):
        covers = value
    else:
        return value, False
    result: list[Any] = []
    sided = False
    for part in covers:
        if not isinstance(part, str):
            result.append(part)
            continue
        upper = part.upper()
        if upper.endswith("_EITHER"):
            upper = upper[:-7]
            sided = True
        result.extend(BODY_PARTS.get(upper, [part.lower()]))
    return result, sided


def storage_volume(value: Any) -> str | None:
    if isinstance(value, (int, float)):
        ml = int(round(float(value) * 250))
        return f"{ml} ml" if ml > 0 else None
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(ml|L)\s*", value, re.I)
    if not match or float(match.group(1)) <= 0:
        return None
    return value.strip()


def storage_weight(volume: str) -> str:
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(ml|L)\s*", volume, re.I)
    if not match:
        return "2 kg"
    liters = float(match.group(1)) / 1000 if match.group(2).lower() == "ml" else float(match.group(1))
    kilograms = max(1, round(liters * 4, 1))
    return f"{int(kilograms) if kilograms.is_integer() else kilograms} kg"


def volume_ml(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(ml|L)\s*", value, re.I)
    if not match:
        return None
    amount = float(match.group(1))
    return amount if match.group(2).lower() == "ml" else amount * 1000


def convert_armor(obj: dict[str, Any], counts: collections.Counter[str]) -> None:
    if obj.get("type") not in ARMOR_TYPES:
        return

    if "encumberance" in obj and "encumbrance" not in obj:
        obj["encumbrance"] = obj.pop("encumberance")
        counts["armor_spelling"] += 1
    if "enviromental_protection" in obj and "environmental_protection" not in obj:
        obj["environmental_protection"] = obj.pop("enviromental_protection")
        counts["armor_spelling"] += 1

    covers, sided = normalize_covers(obj.get("covers"))
    if sided:
        obj["sided"] = True

    legacy_keys = ("coverage", "encumbrance")
    has_legacy_portion = covers is not None or any(key in obj for key in legacy_keys) or "layer" in obj
    armor = obj.get("armor")
    if isinstance(armor, dict):
        armor = [armor]
        obj["armor"] = armor
        counts["armor_object_wrapped"] += 1
    if not isinstance(armor, list) and has_legacy_portion and covers is not None:
        armor = [{}]
        obj["armor"] = armor

    if isinstance(armor, list) and armor:
        layer = obj.get("layer")
        layer_value = LAYER_MAP.get(str(layer).upper()) if layer is not None else None
        for portion in armor:
            if not isinstance(portion, dict):
                continue
            if portion.pop("sided", False):
                obj["sided"] = True
                counts["armor_portion_sided"] += 1
            for top_level_key in ("environmental_protection", "warmth"):
                if top_level_key not in portion:
                    continue
                portion_value = portion.pop(top_level_key)
                if top_level_key not in obj:
                    obj[top_level_key] = portion_value
                elif isinstance(obj[top_level_key], (int, float)) and isinstance(portion_value, (int, float)):
                    obj[top_level_key] = max(obj[top_level_key], portion_value)
                counts["armor_portion_top_level_fields"] += 1
            portion_covers, portion_sided = normalize_covers(portion.get("covers"))
            if portion_covers is not None:
                portion["covers"] = portion_covers
            if portion_sided:
                obj["sided"] = True
            if covers is not None and "covers" not in portion:
                portion["covers"] = covers
            if "covers" not in portion:
                portion["covers"] = ["torso"]
                counts["armor_portion_default_covers"] += 1
            for key in legacy_keys:
                if key in obj and key not in portion:
                    portion[key] = obj[key]
            if layer_value and "layers" not in portion:
                portion["layers"] = [layer_value]
        for key in ("covers", *legacy_keys, "layer"):
            obj.pop(key, None)
        counts["armor_portions"] += 1
    elif covers is not None:
        obj["covers"] = covers

    if "storage" in obj:
        volume = storage_volume(obj.pop("storage"))
        if volume:
            pockets = obj.setdefault("pocket_data", [])
            if isinstance(pockets, dict):
                pockets = [pockets]
                obj["pocket_data"] = pockets
            if isinstance(pockets, list) and not any(
                isinstance(pocket, dict) and pocket.get("pocket_type") == "CONTAINER" for pocket in pockets
            ):
                pockets.append(
                    {
                        "pocket_type": "CONTAINER",
                        "max_contains_volume": volume,
                        "max_contains_weight": storage_weight(volume),
                    }
                )
                counts["storage_pockets"] += 1

    if "max_encumbrance" in obj:
        max_encumbrance = obj.pop("max_encumbrance")
        pockets = obj.get("pocket_data")
        pocket_values = pockets if isinstance(pockets, list) else [pockets]
        for pocket in pocket_values:
            if isinstance(pocket, dict) and pocket.get("pocket_type") == "CONTAINER":
                pocket.setdefault("extra_encumbrance", max_encumbrance)
        counts["armor_max_encumbrance"] += 1


def convert_vehicle_part(obj: dict[str, Any], counts: collections.Counter[str]) -> None:
    if obj.get("type") != "vehicle_part":
        return
    for obsolete in ("difficulty", "range", "wheel_type"):
        if obsolete in obj:
            del obj[obsolete]
            counts["vehicle_part_obsolete_fields"] += 1
    requirements = obj.get("requirements")
    if isinstance(requirements, dict):
        for operation_name, operation in requirements.items():
            if not isinstance(operation, dict):
                continue
            if isinstance(operation.get("time"), (int, float)):
                operation["time"] = f"{max(1, int(round(operation['time'] / 100)))} s"
                counts["vehicle_part_requirement_times"] += 1
            using = operation.get("using")
            if isinstance(using, list):
                replacement = "vehicle_bolt_install" if operation_name == "install" else None
                kept_using: list[Any] = []
                for entry in using:
                    if isinstance(entry, list) and entry and entry[0] in {"vehicle_bolt", "vehicle_bolt_removal"}:
                        if replacement:
                            entry[0] = replacement
                            kept_using.append(entry)
                        counts["vehicle_part_requirements"] += 1
                    else:
                        kept_using.append(entry)
                if kept_using:
                    operation["using"] = kept_using
                else:
                    del operation["using"]
    flags = obj.get("flags")
    flag_values = flags if isinstance(flags, list) else []
    if isinstance(flags, list):
        if "WHEEL" in flags and not any(flag in flags for flag in ("STABLE", "UNSTABLE_WHEEL")):
            flags.append("STABLE")
            counts["stable_vehicle_wheels"] += 1
    if "CARGO" not in flag_values and "size" in obj:
        del obj["size"]
        counts["vehicle_part_non_cargo_size"] += 1
    variants = obj.get("variants")
    symbol = obj.get("symbol")
    broken = obj.get("broken_symbol")
    if not isinstance(variants, list) and (symbol is not None or broken is not None):
        variants = [{"symbols": symbol or broken or "?", "symbols_broken": broken or symbol or "?"}]
        obj["variants"] = variants
        counts["vehicle_variants_created"] += 1
    if isinstance(variants, list):
        variants, removed = dedupe(variants)
        obj["variants"] = variants
        counts["vehicle_variants_deduped"] += removed
        for variant in variants:
            if not isinstance(variant, dict):
                continue
            if "symbols" not in variant:
                variant["symbols"] = symbol or variant.get("symbols_broken") or broken or "?"
                counts["vehicle_variant_fields"] += 1
            if "symbols_broken" not in variant:
                variant["symbols_broken"] = broken or variant.get("symbols") or "?"
                counts["vehicle_variant_fields"] += 1
        if "symbol" in obj:
            del obj["symbol"]
            counts["vehicle_legacy_symbols"] += 1
        if "broken_symbol" in obj:
            del obj["broken_symbol"]
            counts["vehicle_legacy_symbols"] += 1


def vehicle_part_id(part: Any) -> str | None:
    if isinstance(part, str):
        return part.split("#", 1)[0]
    if isinstance(part, dict) and isinstance(part.get("part"), str):
        return part["part"].split("#", 1)[0]
    return None


def migrate_legacy_vehicle_part(part_id: str) -> list[str] | None:
    replacement = LEGACY_VEHICLE_PARTS.get(part_id)
    if replacement is not None:
        return replacement
    for base in LEGACY_VARIANT_PART_BASES:
        prefix = f"{base}_"
        if part_id.startswith(prefix) and part_id[len(prefix) :] in LEGACY_VARIANT_SUFFIXES:
            return [f"{base}#{part_id[len(prefix):]}"]
    return None


def convert_vehicle(obj: dict[str, Any], counts: collections.Counter[str]) -> None:
    """Migrate removed vehicle prototype parts and add required 0.H wheel mounts."""
    if obj.get("type") != "vehicle" or not isinstance(obj.get("parts"), list):
        return

    for record in obj["parts"]:
        if not isinstance(record, dict) or "part" not in record:
            continue
        part_id = record.pop("part")
        if isinstance(part_id, list):
            record["parts"] = part_id
            counts["vehicle_parts_arrays"] += 1
            continue
        if not isinstance(part_id, str):
            continue
        part_options = {key: record.pop(key) for key in list(record) if key not in {"x", "y", "parts"}}
        part: Any = {"part": part_id, **part_options} if part_options else part_id
        record["parts"] = [part]
        counts["vehicle_parts_arrays"] += 1

    records = [record for record in obj["parts"] if isinstance(record, dict) and isinstance(record.get("parts"), list)]
    for record in records:
        migrated: list[Any] = []
        for part in record["parts"]:
            part_id = vehicle_part_id(part)
            replacement = migrate_legacy_vehicle_part(part_id or "")
            if replacement is None:
                migrated.append(part)
                continue
            if isinstance(part, dict) and len(replacement) == 1:
                migrated_part = copy.deepcopy(part)
                migrated_part["part"] = replacement[0]
                migrated.append(migrated_part)
            elif isinstance(part, str):
                migrated.extend(replacement)
            else:
                migrated.append(part)
                continue
            counts["vehicle_part_migrations"] += 1
        record["parts"] = migrated

    coordinate_parts: dict[tuple[Any, Any], set[str]] = collections.defaultdict(set)
    for record in records:
        coordinate = (record.get("x"), record.get("y"))
        coordinate_parts[coordinate].update(filter(None, (vehicle_part_id(part) for part in record["parts"])))

    mount_ids = {mount for mount in WHEEL_MOUNTS.values()}
    mount_ids.update({f"{mount}_steerable" for mount in WHEEL_MOUNTS.values()})
    mount_ids.add("wheel_mount_skateboard")
    for record in records:
        coordinate = (record.get("x"), record.get("y"))
        installed = coordinate_parts[coordinate]
        has_mount = bool(installed & mount_ids)
        rebuilt: list[Any] = []
        for part in record["parts"]:
            part_id = vehicle_part_id(part)
            if part_id in WHEEL_MOUNTS and not has_mount:
                mount = WHEEL_MOUNTS[part_id]
                rebuilt.append(mount)
                installed.add(mount)
                has_mount = True
                counts["vehicle_wheel_mounts"] += 1
            if part_id == "turret_m2browning" and "turret_mount" not in installed:
                rebuilt.append("turret_mount")
                installed.add("turret_mount")
                counts["vehicle_turret_mounts"] += 1
            rebuilt.append(part)
        record["parts"] = rebuilt

    # Install structural records from the centre outward, and install the
    # structural part before accessories at each mount point.
    def part_priority(part: Any) -> int:
        part_id = vehicle_part_id(part) or ""
        return 0 if "frame" in part_id else 1

    for record in records:
        record["parts"].sort(key=part_priority)
    obj["parts"].sort(
        key=lambda record: (
            abs(record.get("x", 9999)) + abs(record.get("y", 9999))
            if isinstance(record, dict)
            and isinstance(record.get("x"), (int, float))
            and isinstance(record.get("y"), (int, float))
            else 9999,
            min((part_priority(part) for part in record.get("parts", [])), default=1)
            if isinstance(record, dict)
            else 1,
        )
    )

    # Obsolete vehicle spawn records used repeat counts which 0.H no longer
    # accepts.  Keeping the spawn once is preferable to rejecting the vehicle.
    for spawn in obj.get("items", []) if isinstance(obj.get("items"), list) else []:
        if isinstance(spawn, dict) and "repeat" in spawn:
            del spawn["repeat"]
            counts["vehicle_item_repeat"] += 1


def convert_gun(obj: dict[str, Any], counts: collections.Counter[str]) -> None:
    if obj.get("type") != "GUN":
        return
    if isinstance(obj.get("recoil"), (int, float)) and obj["recoil"] < 0:
        obj["recoil"] = 0
        counts["gun_recoil_ranges"] += 1
    if "ups_charges" in obj:
        charges = obj.pop("ups_charges")
        if "energy_drain" not in obj and isinstance(charges, (int, float)):
            obj["energy_drain"] = f"{charges:g} kJ"
        counts["gun_ups_charges"] += 1
    if "burst" in obj:
        burst = obj.pop("burst")
        if "modes" not in obj and isinstance(burst, int) and burst > 1:
            obj["modes"] = [["DEFAULT", "semi-auto", 1], ["BURST", "burst", burst]]
        counts["gun_burst"] += 1
    if isinstance(obj.get("ranged_damage"), (int, float)):
        obj["ranged_damage"] = {"damage_type": "bullet", "amount": obj["ranged_damage"]}
        counts["gun_ranged_damage"] += 1
    if "pierce" in obj:
        pierce = obj.pop("pierce")
        ranged_damage = obj.setdefault("ranged_damage", {"damage_type": "bullet", "amount": 0})
        if isinstance(ranged_damage, dict) and "armor_penetration" not in ranged_damage:
            ranged_damage["armor_penetration"] = pierce
        counts["gun_pierce"] += 1
    if "aim_speed" in obj:
        del obj["aim_speed"]
        counts["gun_aim_speed"] += 1
    magazines = obj.pop("magazines", None)
    if isinstance(magazines, list):
        magazine_ids: list[str] = []
        for magazine_entry in magazines:
            if not isinstance(magazine_entry, list) or len(magazine_entry) < 2:
                continue
            choices = magazine_entry[1]
            if isinstance(choices, str):
                magazine_ids.append(choices)
            elif isinstance(choices, list):
                magazine_ids.extend(value for value in choices if isinstance(value, str))
        magazine_ids = list(dict.fromkeys(magazine_ids))
        if magazine_ids:
            pockets = obj.get("pocket_data")
            if not isinstance(pockets, list):
                pockets = []
            pockets = [
                pocket
                for pocket in pockets
                if not isinstance(pocket, dict) or pocket.get("pocket_type") not in {"MAGAZINE", "MAGAZINE_WELL"}
            ]
            pockets.append({"pocket_type": "MAGAZINE_WELL", "item_restriction": magazine_ids})
            obj["pocket_data"] = pockets
            obj.pop("magazine_well", None)
            counts["gun_magazine_wells"] += 1
    clip_size = obj.pop("clip_size", None)
    ammo = obj.get("ammo")
    if isinstance(clip_size, (int, float)) and clip_size > 0 and "pocket_data" not in obj:
        ammo_values = [ammo] if isinstance(ammo, str) else ammo
        if isinstance(ammo_values, list) and ammo_values and all(isinstance(value, str) for value in ammo_values):
            obj["pocket_data"] = [
                {
                    "pocket_type": "MAGAZINE",
                    "rigid": True,
                    "ammo_restriction": {value: int(clip_size) for value in ammo_values},
                }
            ]
            counts["gun_magazine_pockets"] += 1


def convert_comestible(obj: dict[str, Any], counts: collections.Counter[str]) -> None:
    if obj.get("type") != "COMESTIBLE" or "nutrition" not in obj:
        return
    nutrition = obj.pop("nutrition")
    if "calories" not in obj and isinstance(nutrition, (int, float)):
        # 0.H defines one legacy nutrition point as 2500 / (12 * 24) kcal.
        obj["calories"] = int(round(float(nutrition) * 2500 / (12 * 24)))
    counts["nutrition"] += 1


def normalize_optional_mod_item_groups(
    data: Any, path: Path, counts: collections.Counter[str]
) -> None:
    """Keep optional-mod item-group files loadable without importing dependencies.

    Arcana ships compatibility item groups for Cata++ and Magiclysm, but its
    modinfo does not require either dependency.  H still parses those files
    when Arcana is enabled, so retain the group definitions while removing
    unavailable cross-mod entries and converting Magiclysm extensions into
    standalone groups.
    """
    normalized_path = path.as_posix().lower()
    entries = data if isinstance(data, list) else [data]
    if normalized_path.endswith("/arcana/mod_interactions/cata++/item_groups_modcompat.json"):
        unavailable = {
            "megamap",
            "stim",
            "boots_stealth",
            "acs_74_stealth_cloak_on",
            "goggles_nv_clairvoyance",
            "blood_m",
            "blood_p",
        }
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("type") not in {"ITEM_GROUP", "item_group"}:
                continue
            items = entry.get("items")
            if isinstance(items, list):
                kept = [
                    item for item in items
                    if not (isinstance(item, dict) and item.get("item") in unavailable)
                ]
                if kept != items:
                    entry["items"] = kept
                    counts["optional_group_entries"] += len(items) - len(kept)
    elif normalized_path.endswith("/arcana/mod_interactions/magiclysm/item_groups_modcompat.json"):
        unavailable_items = {
            "wizard_beginner",
            "wizard_advanced",
            "priest_beginner",
            "priest_advanced",
            "techno_fundamentals",
        }
        unavailable_groups = {"dragon_books", "spellbook_loot_0", "spellbook_loot_1"}
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("type") not in {"ITEM_GROUP", "item_group"}:
                continue
            if "copy-from" in entry:
                del entry["copy-from"]
                counts["optional_group_copy_from"] += 1
            extend = entry.pop("extend", None)
            if isinstance(extend, dict) and isinstance(extend.get("items"), list):
                existing = entry.get("items")
                if not isinstance(existing, list):
                    existing = []
                entry["items"] = existing + extend["items"]
                counts["optional_group_extensions"] += 1
            items = entry.get("items")
            if isinstance(items, list):
                kept = [
                    item for item in items
                    if not (
                        isinstance(item, dict)
                        and (
                            item.get("item") in unavailable_items
                            or item.get("group") in unavailable_groups
                        )
                    )
                ]
                if kept != items:
                    entry["items"] = kept
                    counts["optional_group_entries"] += len(items) - len(kept)


def clean_fantasy_blacklist_refs(
    data: Any, path: Path, valid_ids: set[str], counts: collections.Counter[str]
) -> None:
    """Drop stale blacklist IDs that H would otherwise report as errors."""
    if "/fantasy/" not in path.as_posix().lower():
        return
    entries = data if isinstance(data, list) else [data]
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("type") != "ITEM_BLACKLIST":
            continue
        items = entry.get("items")
        if not isinstance(items, list):
            continue
        kept = [item for item in items if not isinstance(item, str) or item in valid_ids]
        if kept != items:
            entry["items"] = kept
            counts["fantasy_blacklist_entries"] += len(items) - len(kept)


def transform_object(
    obj: dict[str, Any],
    counts: collections.Counter[str],
    obsolete_monster_ids: set[str] = OBSOLETE_MONSTER_IDS,
) -> None:
    obj_type = obj.get("type")
    # These factories are intentionally lowercase in H.  Older collections
    # (and an earlier compatibility pass) used uppercase spellings, which H
    # rejects as an unrecognized object.  Normalize both spellings to the
    # actual H factory names without changing the definitions themselves.
    legacy_type_names = {
        "item_group": "item_group",
        "ITEM_GROUP": "item_group",
        "scenario": "scenario",
        "SCENARIO": "scenario",
    }
    if isinstance(obj_type, str) and obj_type in legacy_type_names:
        obj["type"] = legacy_type_names[obj_type]
        obj_type = obj["type"]
        counts["legacy_type_case"] += 1
    if isinstance(obj_type, str) and obj_type.upper() in ITEM_TYPES and obj_type != obj_type.upper():
        obj["type"] = obj_type.upper()
        counts["item_type_case"] += 1

    # H rejects a second assignment when an object supplies a field directly
    # and repeats that same field inside an ``extend`` block.  Preserve the
    # extension intent by folding only overlapping list/object members into the
    # direct value; unrelated extension members remain available to H's normal
    # extension handling.
    extension = obj.get("extend")
    if isinstance(extension, dict):
        for key in list(extension):
            if key not in obj:
                continue
            extra = extension[key]
            current = obj[key]
            if isinstance(current, list) and isinstance(extra, list):
                obj[key] = dedupe(current + extra)[0]
                del extension[key]
                counts["extend_overlapping_lists"] += 1
            elif isinstance(current, dict) and isinstance(extra, dict):
                merged = copy.deepcopy(current)
                merged.update(copy.deepcopy(extra))
                obj[key] = merged
                del extension[key]
                counts["extend_overlapping_objects"] += 1
        if not extension:
            obj.pop("extend", None)
            counts["empty_extend_blocks"] += 1

    # Legacy item/monster overrides also used a sibling ``delete`` block to
    # remove inherited members.  In H that block can become a second
    # assignment (for example, direct ``flags`` plus ``delete.flags``).  Apply
    # the requested removals to the current definition and drop only the
    # obsolete wrapper.
    deletion = obj.get("delete")
    if isinstance(deletion, dict) and obj_type != "overmap_terrain":
        for key, value in deletion.items():
            current = obj.get(key)
            if isinstance(current, list) and isinstance(value, list):
                obj[key] = [entry for entry in current if entry not in value]
            elif isinstance(current, dict) and isinstance(value, dict):
                for nested_key in value:
                    current.pop(nested_key, None)
            elif key in obj:
                obj.pop(key, None)
        obj.pop("delete", None)
        counts["generic_delete_blocks"] += 1

    color = obj.get("color")
    if isinstance(color, str):
        normalized_color = color
        if color in {"gray", "grey"}:
            normalized_color = "light_gray"
        elif color == "light_magenta":
            normalized_color = "magenta"
        else:
            # Older tileset colors sometimes encoded foreground/background
            # pairs (or UI prefixes) that are not accepted by H's color
            # parser.  Retain the first valid base color as a close visual
            # equivalent instead of dropping the definition.
            candidate = color
            for prefix in ("c_", "h_", "i_"):
                if candidate.startswith(prefix):
                    candidate = candidate[len(prefix):]
                    break
            if candidate not in H_BASE_COLORS:
                parts = candidate.split("_")
                for end in range(len(parts), 0, -1):
                    prefix = "_".join(parts[:end])
                    if prefix in H_BASE_COLORS:
                        candidate = prefix
                        break
            if candidate in H_BASE_COLORS:
                normalized_color = candidate
        if normalized_color != color:
            obj["color"] = normalized_color
            counts["invalid_colors"] += 1

    # Once a child has been materialized from an abstract/copy-from parent,
    # retaining both `abstract` and a concrete `id` makes H treat the object
    # as an invalid abstract definition.  The concrete id is the actual
    # registered entry, so discard only the stale abstract marker.
    if isinstance(obj.get("id"), str) and isinstance(obj.get("abstract"), str):
        del obj["abstract"]
        counts["concrete_abstract_markers"] += 1

    def apply_numeric_delta(target: dict[str, Any], delta: dict[str, Any], proportional: bool) -> None:
        for key, value in delta.items():
            current = target.get(key)
            if isinstance(value, dict) and isinstance(current, dict):
                apply_numeric_delta(current, value, proportional)
            elif isinstance(value, (int, float)) and isinstance(current, (int, float)):
                target[key] = current * value if proportional else current + value
            elif key not in target:
                if key != "dispersion":
                    target[key] = copy.deepcopy(value)

    if "copy-from" not in obj:
        relative_fields = obj.pop("relative", None)
        if isinstance(relative_fields, dict):
            apply_numeric_delta(obj, relative_fields, proportional=False)
            counts["relative_fields_inlined"] += 1
        proportional_fields = obj.pop("proportional", None)
        if isinstance(proportional_fields, dict):
            apply_numeric_delta(obj, proportional_fields, proportional=True)
            counts["proportional_fields_inlined"] += 1
    if obj.get("type") == "MOD_INFO" and isinstance(obj.get("id"), str):
        mod_id = obj["id"]
        raw_dependencies = obj.get("dependencies", [])
        if isinstance(raw_dependencies, str):
            dependencies = [raw_dependencies]
        elif isinstance(raw_dependencies, list):
            dependencies = list(raw_dependencies)
        else:
            dependencies = []
        cleaned_dependencies = [
            dependency
            for dependency in dependencies
            if isinstance(dependency, str) and dependency and dependency != mod_id
        ]
        if not obj.get("core") and "dda" not in cleaned_dependencies:
            cleaned_dependencies.insert(0, "dda")
        if cleaned_dependencies != dependencies or "dependencies" not in obj:
            obj["dependencies"] = cleaned_dependencies
            counts["mod_dependencies"] += 1
    if obj.get("type") == "ARMOR" and (
        "ammo" in obj or "charges_per_use" in obj or "max_charges" in obj
    ):
        obj["type"] = "TOOL_ARMOR"
        counts["charged_armor_types"] += 1

    identifier = obj.get("id", obj.get("abstract"))
    if (
        "type" not in obj
        and isinstance(identifier, str)
        and identifier.startswith("bio_")
        and ("cost" in obj or "time" in obj)
        and not any(key in obj for key in ("weight", "volume", "symbol", "category", "material"))
    ):
        # Pre-JSONized bionic definitions omitted their dispatch type.  Do
        # not apply this to CBM item definitions, which have item dimensions.
        obj["type"] = "bionic"
        counts["legacy_bionic_types"] += 1

    if (
        "type" not in obj
        and isinstance(identifier, str)
        and "dmg_adj" in obj
        and any(key in obj for key in ("bash_dmg_verb", "cut_dmg_verb", "resist"))
    ):
        obj["type"] = "material"
        counts["legacy_material_types"] += 1

    if (
        "type" not in obj
        and isinstance(obj.get("id"), str)
        and all(key in obj for key in ("name", "material", "weight", "volume", "symbol"))
        and not any(
            key in obj
            for key in (
                "ammo_type",
                "barrel_length",
                "charges_per_use",
                "covers",
                "coverage",
                "encumbrance",
                "magazine_well",
                "max_charges",
                "nutrition",
                "pocket_data",
                "quench",
                "skill",
                "storage",
            )
        )
    ):
        obj["type"] = "GENERIC"
        counts["legacy_generic_types"] += 1

    convert_armor(obj, counts)
    convert_vehicle_part(obj, counts)
    convert_vehicle(obj, counts)
    convert_gun(obj, counts)
    convert_comestible(obj, counts)
    migrate_shrapnel(obj, counts)
    migrate_legacy_skills(obj, counts)
    clean_dialogue_effects(obj, counts)
    if obj.get("type") == "effect_type":
        migrate_effect_mod_keys(obj, counts)
    migrate_item_id_references(obj, counts)
    remove_obsolete_monster_refs(obj, counts, obsolete_monster_ids)
    migrate_monster_factions(obj, counts)

    if obj.get("type") == "AMMO":
        if "damage_states" in obj:
            del obj["damage_states"]
            counts["ammo_damage_states"] += 1
        pierce = obj.pop("pierce", None)
        damage = obj.get("damage")
        if isinstance(pierce, (int, float)) and isinstance(damage, dict):
            damage.setdefault("armor_penetration", pierce)
            counts["ammo_pierce"] += 1
    if obj.get("type") == "GENERIC":
        for obsolete in ("count", "damage_states", "stack_size"):
            if obsolete in obj:
                del obj[obsolete]
                counts["generic_charge_fields"] += 1
    if obj.get("type") == "GUN":
        for obsolete in ("covers", "coverage", "encumbrance"):
            if obsolete in obj:
                del obj[obsolete]
                counts["gun_armor_fields"] += 1
        flags = obj.get("flags", [])
        if "energy_drain" in obj and isinstance(flags, list) and "USE_UPS" in flags:
            obj.pop("ammo", None)
            pockets = obj.get("pocket_data")
            if isinstance(pockets, list):
                kept_pockets = [
                    pocket
                    for pocket in pockets
                    if not isinstance(pocket, dict)
                    or pocket.get("pocket_type") not in {"MAGAZINE", "MAGAZINE_WELL"}
                ]
                if kept_pockets:
                    obj["pocket_data"] = kept_pockets
                else:
                    obj.pop("pocket_data", None)
            counts["ups_gun_battery_pockets"] += 1
    if obj.get("type") == "region_overlay":
        if "id" in obj:
            del obj["id"]
            counts["region_overlay_ids"] += 1
        if "river_scale" in obj:
            del obj["river_scale"]
            counts["region_overlay_obsolete_fields"] += 1
    if obj.get("type") == "field_type":
        immunity = obj.get("immunity_data")
        if isinstance(immunity, dict) and "traits" in immunity:
            traits = immunity.pop("traits")
            if isinstance(traits, list) and "ACIDPROOF" in traits:
                flags = immunity.setdefault("flags", [])
                if isinstance(flags, list) and "ACID_IMMUNE" not in flags:
                    flags.append("ACID_IMMUNE")
            counts["field_immunity_traits"] += 1
    if obj.get("type") == "mission_definition" and "assign_mission_target" in obj:
        target = obj.pop("assign_mission_target")
        start = obj.setdefault("start", {})
        if isinstance(start, dict) and "assign_mission_target" not in start:
            start["assign_mission_target"] = target
        counts["mission_targets"] += 1
    if obj.get("type") == "npc_class" and "name_unique" in obj:
        unique_name = obj.pop("name_unique")
        if isinstance(unique_name, str):
            obj["name"] = {"str": unique_name}
        counts["npc_class_unique_names"] += 1

    # These ids were migrated by the 0.H core data.  Apply the same migration
    # to copy-from and ordinary reference fields without inventing shims.
    for key in ("copy-from", "result", "item", "container", "magazine", "default_magazine"):
        value = obj.get(key)
        if isinstance(value, str) and value in ITEM_ID_MIGRATIONS:
            obj[key] = ITEM_ID_MIGRATIONS[value]
            counts["item_id_migrations"] += 1

    if obj.get("type") == "MAGAZINE" and "pocket_data" not in obj:
        capacity = obj.get("capacity")
        ammo = obj.get("ammo_type", obj.get("ammo"))
        ammo_values = [ammo] if isinstance(ammo, str) else ammo
        if (
            isinstance(capacity, (int, float))
            and capacity > 0
            and isinstance(ammo_values, list)
            and ammo_values
            and all(isinstance(value, str) for value in ammo_values)
        ):
            obj["pocket_data"] = [
                {
                    "pocket_type": "MAGAZINE",
                    "rigid": True,
                    "ammo_restriction": {value: int(capacity) for value in ammo_values},
                }
            ]
            counts["magazine_pockets"] += 1

    if obj.get("type") in ITEM_TYPES and isinstance(obj.get("magazines"), list):
        magazine_ids: list[str] = []
        for magazine_entry in obj.pop("magazines"):
            if not isinstance(magazine_entry, list) or len(magazine_entry) < 2:
                continue
            choices = magazine_entry[1]
            if isinstance(choices, str):
                magazine_ids.append(choices)
            elif isinstance(choices, list):
                magazine_ids.extend(value for value in choices if isinstance(value, str))
        magazine_ids = list(dict.fromkeys(magazine_ids))
        if magazine_ids:
            pockets = obj.get("pocket_data")
            if not isinstance(pockets, list):
                pockets = []
            pockets = [
                pocket
                for pocket in pockets
                if not isinstance(pocket, dict) or pocket.get("pocket_type") not in {"MAGAZINE", "MAGAZINE_WELL"}
            ]
            pockets.append({"pocket_type": "MAGAZINE_WELL", "item_restriction": magazine_ids})
            obj["pocket_data"] = pockets
            counts["item_magazine_wells"] += 1
        obj.pop("magazine_well", None)
    elif obj.get("type") in ITEM_TYPES and "magazine_well" in obj:
        # A copied item can inherit the real MAGAZINE_WELL pocket from its
        # parent, so the removed scalar field must still be discarded.
        del obj["magazine_well"]
        counts["obsolete_magazine_wells"] += 1

    if obj.get("type") in ARMOR_TYPES and isinstance(obj.get("armor_data"), dict):
        legacy_armor = obj.pop("armor_data")
        covers, sided = normalize_covers(legacy_armor.pop("covers", None))
        if covers:
            legacy_armor["covers"] = covers
        if sided:
            obj["sided"] = True
        obj["armor"] = [legacy_armor]
        counts["armor_data"] += 1
    elif "armor_data" in obj:
        del obj["armor_data"]
        counts["obsolete_armor_data"] += 1

    if isinstance(obj.get("name"), str) and isinstance(obj.get("name_plural"), str):
        singular = obj["name"]
        plural = obj.pop("name_plural")
        obj["name"] = {"str_sp": singular} if singular == plural else {"str": singular, "str_pl": plural}
        counts["legacy_name_plural"] += 1

    if obj.get("type") in {"mapgen", "mapgen_palette", "palette"}:
        counts["reversed_coordinate_ranges"] += normalize_coordinate_ranges(obj)
        if obj.get("type") == "mapgen":
            normalize_mapgen_rows(obj, counts)
        migrate_terrain_ids(obj, counts)
        migrate_mapgen_ids(obj, counts)
        clean_mapgen_placements(obj, counts)
        if obj.get("type") == "mapgen":
            om_terrain = obj.get("om_terrain")
            om_values = [om_terrain] if isinstance(om_terrain, str) else om_terrain
            placements = obj.get("object", {}).get("place_vehicles") if isinstance(obj.get("object"), dict) else None
            if isinstance(om_values, list) and isinstance(placements, list):
                if "orchard_processing" in om_values:
                    for placement in placements:
                        if isinstance(placement, dict) and placement.get("y") == 21:
                            placement["y"] = 19
                            counts["mapgen_vehicle_bounds"] += 1
                if "s_garage" in om_values:
                    for placement in placements:
                        if (
                            isinstance(placement, dict)
                            and placement.get("vehicle") == "parkinglot"
                            and placement.get("x") == [10, 11]
                        ):
                            placement["x"] = [11, 11]
                            counts["mapgen_vehicle_bounds"] += 1
    elif obj.get("type") == "vehicle":
        clean_mapgen_placements(obj, counts)

    musical_action = obj.get("use_action")
    if isinstance(musical_action, dict) and musical_action.get("type") == "musical_instrument":
        tick_action = copy.deepcopy(musical_action)
        if isinstance(tick_action.get("volume"), str):
            # Legacy mods occasionally confused item volume with sound volume.
            tick_action["volume"] = 20
        obj["tick_action"] = tick_action
        obj["use_action"] = [{"type": "play_instrument"}]
        counts["musical_instrument_actions"] += 1
    use_actions = obj.get("use_action")
    use_action_values = use_actions if isinstance(use_actions, list) else [use_actions]
    for action in use_action_values:
        if isinstance(action, dict):
            for obsolete in ("skill1", "skill2"):
                if obsolete in action:
                    del action[obsolete]
                    counts["use_action_obsolete_fields"] += 1

    # 0.H rejects negative values for dispersion while applying `relative`.
    # Preserve the intended accuracy improvement as a positive proportional
    # multiplier (for example, -15 becomes 0.85 of the inherited dispersion).
    relative = obj.get("relative")
    if isinstance(relative, dict) and isinstance(relative.get("dispersion"), (int, float)):
        relative_dispersion = relative.get("dispersion")
        if relative_dispersion < 0:
            del relative["dispersion"]
            if not relative:
                del obj["relative"]
            proportional = obj.setdefault("proportional", {})
            if isinstance(proportional, dict) and "dispersion" not in proportional:
                proportional["dispersion"] = max(0.01, 1 + relative_dispersion / 100)
            counts["negative_relative_dispersion"] += 1

    damage = obj.get("damage")
    damage_units = damage if isinstance(damage, list) else [damage]
    for damage_unit in damage_units:
        if isinstance(damage_unit, dict) and "pierce" in damage_unit:
            pierce = damage_unit.pop("pierce")
            if "armor_penetration" not in damage_unit:
                damage_unit["armor_penetration"] = pierce
            counts["damage_armor_penetration"] += 1

    if obj.get("type") == "GUNMOD":
        gun_data = obj.get("gun_data")
        if isinstance(gun_data, dict):
            gun_ammo = gun_data.get("ammo")
            if isinstance(gun_ammo, list) and len(gun_ammo) == 1 and isinstance(gun_ammo[0], str):
                gun_ammo = gun_ammo[0]
                gun_data["ammo"] = gun_ammo
                counts["gunmod_gun_data_ammo"] += 1
            clip_size = gun_data.get("clip_size")
            if (
                isinstance(gun_ammo, str)
                and isinstance(clip_size, (int, float))
                and clip_size > 0
                and "pocket_data" not in obj
            ):
                obj["pocket_data"] = [
                    {
                        "pocket_type": "MAGAZINE",
                        "ammo_restriction": {gun_ammo: int(clip_size)},
                    }
                ]
                counts["gunmod_magazine_pockets"] += 1
        if isinstance(obj.get("blacklist_mod"), str):
            obj["blacklist_mod"] = [obj["blacklist_mod"]]
            counts["gunmod_blacklists"] += 1
        if isinstance(obj.get("energy_drain_modifier"), (int, float)):
            obj["energy_drain_modifier"] = f"{obj['energy_drain_modifier']:g} kJ"
            counts["gunmod_energy_modifiers"] += 1
        if isinstance(obj.get("damage_modifier"), (int, float)):
            obj["damage_modifier"] = {"damage_type": "bullet", "amount": obj["damage_modifier"]}
            counts["gunmod_damage"] += 1
        if isinstance(obj.get("ammo_modifier"), str):
            ammo_modifier = obj["ammo_modifier"]
            if ammo_modifier.upper() == "NULL":
                del obj["ammo_modifier"]
            else:
                obj["ammo_modifier"] = [ammo_modifier]
            counts["gunmod_ammo"] += 1
        for key in ("burst_modifier", "clip_size_modifier", "recoil_modifier"):
            if key in obj:
                del obj[key]
                counts["gunmod_obsolete_modifiers"] += 1
        if "location" not in obj:
            obj["location"] = "mechanism"
            counts["gunmod_locations"] += 1
        if "install_time" not in obj:
            obj["install_time"] = "5 m"
            counts["gunmod_install_times"] += 1

    use_action = obj.get("use_action")
    if isinstance(use_action, str) and use_action in OBSOLETE_IUSE_ACTIONS:
        del obj["use_action"]
        counts["obsolete_iuse_actions"] += 1
    elif isinstance(use_action, dict) and str(use_action.get("type", "")).lower() in {
        "catfood", "dogfood", "mutagen", "ups_based_armor"
    }:
        del obj["use_action"]
        counts["obsolete_iuse_actions"] += 1
    elif isinstance(use_action, dict) and str(use_action.get("type", "")).lower() in {"bandolier", "holster"}:
        action_type = str(use_action.get("type")).lower()
        pocket: dict[str, Any] = {"pocket_type": "CONTAINER", "rigid": True}
        if action_type == "bandolier":
            capacity = use_action.get("capacity", use_action.get("max_charges", 1))
            ammo = use_action.get("ammo", use_action.get("ammo_type"))
            ammo_values = [ammo] if isinstance(ammo, str) else ammo
            if isinstance(capacity, (int, float)) and isinstance(ammo_values, list):
                pocket["ammo_restriction"] = {
                    value: int(capacity) for value in ammo_values if isinstance(value, str)
                }
            pocket["max_contains_volume"] = obj.get("volume", "2 L")
            pocket["max_contains_weight"] = "5 kg"
        else:
            pocket["max_contains_volume"] = storage_volume(use_action.get("max_volume")) or "2 L"
            max_weight = use_action.get("max_weight")
            pocket["max_contains_weight"] = f"{int(max_weight)} g" if isinstance(max_weight, (int, float)) else "5 kg"
            if isinstance(use_action.get("min_volume"), str):
                pocket["min_item_volume"] = use_action["min_volume"]
            if isinstance(use_action.get("draw_cost"), (int, float)):
                pocket["moves"] = int(use_action["draw_cost"])
            restrictions = use_action.get("flags")
            if isinstance(restrictions, list):
                pocket["flag_restriction"] = [value for value in restrictions if isinstance(value, str)]
        pockets = obj.setdefault("pocket_data", [])
        if isinstance(pockets, dict):
            pockets = [pockets]
            obj["pocket_data"] = pockets
        if isinstance(pockets, list):
            pockets.append(pocket)
        del obj["use_action"]
        counts["legacy_holster_pockets"] += 1

    material = obj.get("material")
    if isinstance(material, list):
        fixed_material = ["hflesh" if value == "Hflesh" else value for value in material if value != "null"]
        if fixed_material != material:
            obj["material"] = fixed_material or ["plastic"]
            counts["legacy_material_ids"] += 1

    if obj.get("type") in {"AMMO", "ARMOR", "GUN", "MAGAZINE", "TOOL", "TOOL_ARMOR"}:
        ammo_key = "ammo_type" if obj.get("type") == "AMMO" else "ammo"
        ammo_value = obj.get(ammo_key)
        if isinstance(ammo_value, str):
            migrated = AMMO_TYPE_MIGRATIONS.get(ammo_value, ammo_value)
            if migrated.lower() in {"none", "null"}:
                del obj[ammo_key]
            elif migrated != ammo_value:
                obj[ammo_key] = migrated
            if migrated != ammo_value or migrated.lower() in {"none", "null"}:
                counts["ammo_type_migrations"] += 1
        elif isinstance(ammo_value, list):
            migrated_values = [AMMO_TYPE_MIGRATIONS.get(value, value) for value in ammo_value if value.lower() not in {"none", "null"}]
            if migrated_values != ammo_value:
                if migrated_values:
                    obj[ammo_key] = migrated_values
                else:
                    del obj[ammo_key]
                counts["ammo_type_migrations"] += 1
        pockets = obj.get("pocket_data")
        pocket_list = pockets if isinstance(pockets, list) else [pockets]
        kept_pockets: list[Any] = []
        for pocket in pocket_list:
            if isinstance(pocket, dict) and isinstance(pocket.get("ammo_restriction"), dict):
                restrictions = {
                    AMMO_TYPE_MIGRATIONS.get(key, key): value
                    for key, value in pocket["ammo_restriction"].items()
                    if key.lower() not in {"none", "null"}
                }
                if restrictions:
                    pocket["ammo_restriction"] = restrictions
                    if any(
                        key in {"diesel", "gasoline", "jp8", "smoke_juice", "water_smoke", "zetan_plasma"}
                        for key in restrictions
                    ):
                        pocket["watertight"] = True
                elif pocket.get("pocket_type") == "MAGAZINE":
                    counts["empty_magazine_pockets"] += 1
                    continue
            if pocket is not None:
                kept_pockets.append(pocket)
        if isinstance(pockets, list) and kept_pockets != pockets:
            if kept_pockets:
                obj["pocket_data"] = kept_pockets
            else:
                del obj["pocket_data"]

    if (
        obj.get("type") in {"TOOL", "TOOL_ARMOR"}
        and isinstance(obj.get("initial_charges"), (int, float))
        and obj["initial_charges"] > 0
        and "max_charges" not in obj
        and "ammo" not in obj
        and "pocket_data" not in obj
    ):
        obj["max_charges"] = obj["initial_charges"]
        counts["tool_charge_capacities"] += 1

    if obj.get("type") == "AMMO" and "ammo_type" not in obj and "copy-from" not in obj:
        if obj.get("id") == "charge_shot":
            obj["ammo_type"] = "plasma"
        elif obj.get("id") == "40mm_casing":
            obj["ammo_type"] = "40x46mm"
        else:
            obj["type"] = "GENERIC"
            for key in ("count", "damage", "dispersion", "effects", "range", "recoil"):
                obj.pop(key, None)
        counts["ammo_without_types"] += 1

    if obj.get("type") == "AMMO" and isinstance(obj.get("dispersion"), (int, float)):
        # H's current ammo schema rejects the legacy top-level dispersion
        # field in a number of older mod definitions (the value was formerly
        # accepted as a per-ammo accuracy override).  Preserve the original
        # number as an ignored JSON comment and omit the invalid field so the
        # ammo remains loadable.
        obj["//legacy_dispersion"] = obj.pop("dispersion")
        counts["ammo_legacy_dispersion"] += 1
        # The remaining defaults apply only to definitions retaining an H
        # dispersion value; this branch intentionally skips them.
    if obj.get("type") == "AMMO" and "//legacy_dispersion" not in obj and isinstance(obj.get("dispersion"), (int, float)):
        if obj["dispersion"] > 200:
            obj["dispersion"] = 200
            counts["ammo_dispersion_caps"] += 1
        if isinstance(obj.get("range"), (int, float)) and obj["range"] > 80:
            obj["range"] = 80
            counts["ammo_range_caps"] += 1
        if "range" not in obj:
            obj["range"] = 10
            counts["ammo_default_ranges"] += 1
        if "loudness" not in obj:
            obj["loudness"] = 0
            counts["ammo_default_loudness"] += 1
        if "recoil" not in obj:
            obj["recoil"] = 0
            counts["ammo_default_recoil"] += 1
        if "melee_damage" in obj:
            melee_damage = obj.pop("melee_damage")
            obj["melee_damage"] = melee_damage
            counts["ammo_melee_field_order"] += 1

    flags = obj.get("flags")
    if isinstance(flags, list):
        original_flags = list(flags)
        flags = [
            "FLOTATION" if flag == "FLOATATION"
            else "NON_FOULING" if flag == "NON-FOULING"
            else "BELTED" if flag == "WAIST"
            else flag
            for flag in flags
        ]
        flags = [flag for flag in flags if flag not in {"CHARGE", "FIRE_100", "MUTAGEN_STRONG"}]
        fixed_flags = [flag for flag in flags if flag not in OBSOLETE_ITEM_FLAGS]
        if "STAB" in fixed_flags:
            fixed_flags.remove("STAB")
            melee = obj.setdefault("melee_damage", {})
            if isinstance(melee, dict) and "stab" not in melee:
                melee["stab"] = max(1, int(melee.get("cut", 0)))
            counts["obsolete_stab_flags"] += 1
        if fixed_flags != original_flags:
            if fixed_flags:
                obj["flags"] = fixed_flags
            else:
                del obj["flags"]
            counts["obsolete_item_flags"] += 1

    if obj.get("type") in ITEM_TYPES:
        # H expects monetary fields as numbers.  Older mods commonly used
        # human-readable strings such as "250 USD"; retain the amount while
        # dropping only the presentation suffix.
        for price_key in ("price", "price_postapoc"):
            price = obj.get(price_key)
            if isinstance(price, str):
                match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(?:USD|\$)?\s*", price, re.I)
                if match:
                    numeric = float(match.group(1))
                    obj[price_key] = int(numeric) if numeric.is_integer() else numeric
                    counts["numeric_prices"] += 1
        if obj.get("description") == "":
            name_value = obj.get("name", {})
            display_name = name_value.get("str", name_value.get("str_sp", obj.get("id", "item"))) if isinstance(name_value, dict) else name_value
            obj["description"] = f"Legacy {display_name}."
            counts["empty_item_descriptions"] += 1
        weight = obj.get("weight")
        is_zero_weight = weight == 0 or (
            isinstance(weight, str) and re.fullmatch(r"\s*0+(?:\.0+)?\s*(?:mg|g|kg)\s*", weight, re.I)
        )
        if is_zero_weight:
            item_flags = obj.setdefault("flags", [])
            if isinstance(item_flags, list) and "ZERO_WEIGHT" not in item_flags:
                item_flags.append("ZERO_WEIGHT")
                counts["zero_weight_flags"] += 1
        item_volume = volume_ml(obj.get("volume"))
        if item_volume == 0:
            item_flags = obj.setdefault("flags", [])
            if isinstance(item_flags, list) and "ZERO_WEIGHT" not in item_flags:
                item_flags.append("ZERO_WEIGHT")
                counts["zero_volume_flags"] += 1
        pockets = obj.get("pocket_data")
        pocket_list = pockets if isinstance(pockets, list) else [pockets]
        if item_volume is not None and any(
            isinstance(pocket, dict)
            and pocket.get("pocket_type") == "CONTAINER"
            and (volume_ml(pocket.get("max_contains_volume")) or 0) >= item_volume
            for pocket in pocket_list
        ):
            item_flags = obj.setdefault("flags", [])
            if isinstance(item_flags, list) and "TARDIS" not in item_flags:
                item_flags.append("TARDIS")
                counts["tardis_flags"] += 1

    if "contains" in obj:
        volume = storage_volume(obj.pop("contains"))
        if volume:
            old_flags = flags if isinstance(flags, list) else []
            pocket = {
                "pocket_type": "CONTAINER",
                "max_contains_volume": volume,
                "max_contains_weight": storage_weight(volume),
                "rigid": "RIGID" in old_flags,
            }
            if "WATERTIGHT" in old_flags:
                pocket["watertight"] = True
            if "SEALS" in old_flags:
                pocket["airtight"] = True
            obj["pocket_data"] = [pocket]
            if isinstance(obj.get("flags"), list):
                obj["flags"] = [flag for flag in obj["flags"] if flag not in {"RIGID", "WATERTIGHT", "SEALS"}]
                if not obj["flags"]:
                    del obj["flags"]
            item_flags = obj.setdefault("flags", [])
            if isinstance(item_flags, list) and "TARDIS" not in item_flags:
                item_flags.append("TARDIS")
            counts["container_pockets"] += 1

    properties = obj.get("properties")
    if isinstance(properties, list) and all(
        isinstance(entry, list) and len(entry) == 2 and isinstance(entry[0], str) for entry in properties
    ):
        obj["properties"] = {entry[0]: entry[1] for entry in properties}
        counts["item_properties_objects"] += 1

    pockets = obj.get("pocket_data")
    pocket_list = pockets if isinstance(pockets, list) else [pockets]
    container_pocket = next(
        (
            pocket
            for pocket in pocket_list
            if isinstance(pocket, dict) and pocket.get("pocket_type") == "CONTAINER"
        ),
        None,
    )
    if container_pocket is not None:
        for legacy_key, pocket_key in (("rigid", "rigid"), ("watertight", "watertight"), ("seals", "airtight")):
            if legacy_key in obj:
                container_pocket[pocket_key] = obj.pop(legacy_key)
                counts["container_pocket_properties"] += 1

    if obj.get("type") == "COMESTIBLE" and "heal" in obj:
        del obj["heal"]
        counts["obsolete_comestible_heal"] += 1
    if obj.get("type") == "COMESTIBLE":
        if obj.get("comestible_type") == "CHEM":
            obj["comestible_type"] = "MED"
            counts["comestible_types"] += 1
        if str(obj.get("phase", "solid")).lower() == "solid" and "charges" in obj:
            del obj["charges"]
            counts["solid_comestible_charges"] += 1
        elif str(obj.get("phase", "solid")).lower() == "liquid" and not isinstance(obj.get("charges"), (int, float)):
            obj["charges"] = 1
            counts["liquid_comestible_charges"] += 1

    for null_key in ("container", "revert_to", "tool"):
        null_value = obj.get(null_key)
        if isinstance(null_value, str) and null_value.lower() in {"", "null", "none", "apparatus"}:
            del obj[null_key]
            counts["null_item_references"] += 1

    if isinstance(obj.get("death_function"), list):
        death_functions = obj.pop("death_function")
        if "BROKEN" in death_functions:
            obj["death_function"] = {"corpse_type": "BROKEN"}
        counts["monster_death_functions"] += 1

    if obj.get("type") == "MONSTER":
        counts["monster_gun_obsolete_fields"] += remove_keys_recursive(obj, {"burst_limit", "range"})
        migrate_monster_fire_damage(obj, counts)
        monster_flags = obj.get("flags")
        if isinstance(monster_flags, list):
            kept_monster_flags = [flag for flag in monster_flags if flag not in OBSOLETE_MONSTER_FLAGS]
            if kept_monster_flags != monster_flags:
                obj["flags"] = kept_monster_flags
                counts["obsolete_monster_flags"] += len(monster_flags) - len(kept_monster_flags)
        melee = obj.get("melee_damage")
        if isinstance(melee, list):
            melee_values = {
                unit.get("damage_type"): unit.get("amount", 0)
                for unit in melee
                if isinstance(unit, dict) and isinstance(unit.get("damage_type"), str)
            }
        elif isinstance(melee, dict):
            melee_values = dict(melee)
        else:
            melee_values = {}
        for legacy, damage_type in (("melee_bash", "bash"), ("melee_cut", "cut")):
            value = obj.pop(legacy, None)
            if isinstance(value, (int, float)) and damage_type not in melee_values:
                melee_values[damage_type] = value
                counts["monster_melee_damage"] += 1
        if melee_values:
            obj["melee_damage"] = [
                {"damage_type": damage_type, "amount": amount}
                for damage_type, amount in melee_values.items()
                if isinstance(amount, (int, float)) and amount > 0
            ]
            if not obj["melee_damage"]:
                del obj["melee_damage"]
        if obj.get("harvest") in {"CBM_BASIC", "CBM_CIV", "CBM_OP", "CBM_SCI", "CBM_SUBS"}:
            obj["harvest"] = "human"
            counts["monster_harvest_migrations"] += 1
        special_attacks = obj.get("special_attacks")
        if isinstance(special_attacks, list):
            migrated_attacks: list[Any] = []
            for index, attack in enumerate(special_attacks):
                if isinstance(attack, list) and attack and attack[0] == "ANTQUEEN":
                    flags = obj.setdefault("flags", [])
                    if isinstance(flags, list) and "QUEEN" not in flags:
                        flags.append("QUEEN")
                    counts["legacy_antqueen_attacks"] += 1
                    continue
                if isinstance(attack, list) and len(attack) >= 2 and attack[0] in {"GRAB", "GRAB_DRAG"}:
                    attack = {"id": "grab", "cooldown": attack[1]}
                    counts["legacy_grab_attacks"] += 1
                elif isinstance(attack, list) and len(attack) >= 2 and attack[0] == "RANGED_PULL":
                    attack = {"id": "ranged_pull", "cooldown": attack[1]}
                    counts["legacy_ranged_pull_attacks"] += 1
                elif (
                    isinstance(attack, list)
                    and len(attack) >= 2
                    and isinstance(attack[0], str)
                    and not attack[0].isupper()
                ):
                    # Lowercase IDs name data-driven ``monster_attack`` objects.
                    # H only accepts the old [ name, cooldown ] pair for its
                    # uppercase, hard-coded attacks.
                    attack = {"id": attack[0], "cooldown": attack[1]}
                    counts["data_driven_monster_attacks"] += 1
                if isinstance(attack, dict) and attack.get("id") == "inject" and "type" not in attack:
                    # This is a mod-local syringe jab, not a registered core attack.
                    attack["type"] = "bite"
                    counts["inline_inject_attacks"] += 1
                migrated_attacks.append(attack)
            attack_types = collections.Counter(
                attack.get("type")
                for attack in migrated_attacks
                if isinstance(attack, dict) and isinstance(attack.get("type"), str)
            )
            used_attack_ids = {
                attack.get("id")
                for attack in migrated_attacks
                if isinstance(attack, dict) and isinstance(attack.get("id"), str)
            }
            attack_ordinals: collections.Counter[str] = collections.Counter()
            for attack in migrated_attacks:
                if not isinstance(attack, dict) or isinstance(attack.get("id"), str):
                    continue
                attack_type = attack.get("type")
                if not isinstance(attack_type, str) or attack_types[attack_type] < 2:
                    continue
                while True:
                    attack_ordinals[attack_type] += 1
                    candidate = f"{attack_type}_{attack_ordinals[attack_type]}"
                    if candidate not in used_attack_ids:
                        break
                attack["id"] = candidate
                used_attack_ids.add(candidate)
                counts["duplicate_inline_attack_ids"] += 1
            obj["special_attacks"] = migrated_attacks
        for trigger_key, valid_triggers in MONSTER_TRIGGERS.items():
            triggers = obj.get(trigger_key)
            if isinstance(triggers, list):
                kept_triggers = [trigger for trigger in triggers if trigger in valid_triggers]
                if kept_triggers != triggers:
                    if kept_triggers:
                        obj[trigger_key] = kept_triggers
                    else:
                        del obj[trigger_key]
                    counts["invalid_monster_triggers"] += len(triggers) - len(kept_triggers)

    if isinstance(obj.get("techniques"), str):
        obj["techniques"] = [obj["techniques"]]
        counts["technique_arrays"] += 1
    if isinstance(obj.get("techniques"), list):
        techniques = obj["techniques"]
        kept = [technique for technique in techniques if technique not in OBSOLETE_TECHNIQUES]
        if kept != techniques:
            if kept:
                obj["techniques"] = kept
            else:
                del obj["techniques"]
                counts["obsolete_techniques"] += len(techniques) - len(kept)

    if obj.get("type") == "profession":
        cbms = obj.get("CBMs")
        if isinstance(cbms, list):
            kept_cbms = [cbm for cbm in cbms if cbm not in OBSOLETE_BIONIC_IDS]
            if kept_cbms != cbms:
                obj["CBMs"] = kept_cbms
                counts["obsolete_profession_bionics"] += len(cbms) - len(kept_cbms)

        def clean_profession_entries(value: Any) -> None:
            if isinstance(value, dict):
                if value.get("item") == "chemistry_set":
                    for key in ("ammo-item", "charges"):
                        if key in value:
                            del value[key]
                            counts["profession_item_modifiers"] += 1
                if value.get("item") == "load_bearing_vest" and "contents-group" in value:
                    value["item"] = "tacvest"
                    counts["profession_containers"] += 1
                if value.get("item") == "modular_m4_carbine" and "contents-item" in value:
                    value.setdefault("variant", "modular_m4a1")
                    counts["profession_gun_variants"] += 1
                for child in value.values():
                    clean_profession_entries(child)
            elif isinstance(value, list):
                for child in value:
                    clean_profession_entries(child)

        clean_profession_entries(obj.get("items"))

    if obj.get("type") == "recipe" and "subcategory" not in obj:
        category = obj.get("category")
        if category in RECIPE_CATEGORY_DEFAULTS:
            obj["category"], obj["subcategory"] = RECIPE_CATEGORY_DEFAULTS[category]
            counts["recipe_subcategories"] += 1
    elif obj.get("type") == "uncraft" and obj.get("category") == "CC_NONCRAFT":
        del obj["category"]
        counts["obsolete_uncraft_categories"] += 1

    if obj.get("type") in {"recipe", "uncraft"} and isinstance(obj.get("difficulty"), (int, float)):
        difficulty = obj["difficulty"]
        if difficulty < 0 or difficulty > 10:
            obj["difficulty"] = max(0, min(10, difficulty))
            counts["recipe_difficulty_ranges"] += 1

    if obj.get("type") in {"recipe", "uncraft"}:
        if isinstance(obj.get("time"), (int, float)):
            obj["time"] = f"{max(1, int(round(obj['time'] / 100)))} s"
            counts["recipe_times"] += 1
        if "skill_pri" in obj:
            skill = obj.pop("skill_pri")
            if "skill_used" not in obj:
                obj["skill_used"] = skill
            counts["recipe_primary_skills"] += 1
        if "skill_sec" in obj:
            skill = obj.pop("skill_sec")
            if "skills_required" not in obj and isinstance(skill, str):
                obj["skills_required"] = [skill, int(obj.get("difficulty", 0))]
            counts["recipe_secondary_skills"] += 1
        components = obj.get("components")
        if isinstance(components, list):
            for group_index, group in enumerate(components):
                if not isinstance(group, list):
                    continue
                valid_group = [
                    component
                    for component in group
                    if not (
                        isinstance(component, list)
                        and (not component or not isinstance(component[0], str))
                    )
                ]
                if len(valid_group) != len(group):
                    components[group_index] = valid_group
                    counts["recipe_component_entries"] += len(group) - len(valid_group)
                for component in group:
                    if (
                        isinstance(component, list)
                        and len(component) >= 2
                        and isinstance(component[1], (int, float))
                        and component[1] <= 0
                    ):
                        component[1] = max(1, abs(component[1]))
                        counts["recipe_component_counts"] += 1
            components[:] = [group for group in components if not isinstance(group, list) or group]
        for key in ("tools", "using"):
            tool_groups = obj.get(key)
            if not isinstance(tool_groups, list):
                continue
            for group_index, group in enumerate(tool_groups):
                if not isinstance(group, list):
                    continue
                valid_group = [
                    tool
                    for tool in group
                    if not (isinstance(tool, list) and (not tool or not isinstance(tool[0], str)))
                ]
                if len(valid_group) != len(group):
                    tool_groups[group_index] = valid_group
                    counts["recipe_tool_entries"] += len(group) - len(valid_group)
            tool_groups[:] = [group for group in tool_groups if not isinstance(group, list) or group]
        byproducts = obj.get("byproducts")
        if isinstance(byproducts, list):
            valid_byproducts = [
                byproduct
                for byproduct in byproducts
                if isinstance(byproduct, dict)
                and ("item" in byproduct or "group" in byproduct)
            ]
            if len(valid_byproducts) != len(byproducts):
                obj["byproducts"] = valid_byproducts
                counts["recipe_byproduct_entries"] += len(byproducts) - len(valid_byproducts)
        if obj.get("type") == "uncraft":
            for key in ("id_suffix", "reversible", "autolearn", "difficulty"):
                if key in obj:
                    del obj[key]
                    counts["obsolete_uncraft_fields"] += 1
            # Numeric time was normalized above for both recipes and uncrafts.

    if obj.get("type") in ITEM_TYPES | {"MONSTER"}:
        if obj.get("use_action") == "BOOTS":
            del obj["use_action"]
            counts["obsolete_use_actions"] += 1
        if "rarity" in obj:
            del obj["rarity"]
            counts["item_rarity"] += 1
        name = obj.get("name")
        if isinstance(name, str):
            name = {"str": name}
            obj["name"] = name
        fixed_name, changed_name = normalize_item_name_plural(name)
        if changed_name:
            obj["name"] = fixed_name
            counts["plural_names"] += 1

    if "countdown_destroy" in obj and obj.get("type") in ITEM_TYPES:
        del obj["countdown_destroy"]
        counts["countdown_destroy"] += 1

    if obj.get("type") in {"ITEM_GROUP", "item_group"}:
        if "subtype" not in obj:
            obj["subtype"] = "distribution"
            counts["item_group_subtypes"] += 1
        # H-release item groups use `items` for their entries.  Older mods
        # commonly used a top-level `entries` array (the same spelling used
        # by harvest definitions).  Move it into `items` while preserving
        # both lists when a file supplied both forms.
        if isinstance(obj.get("entries"), list):
            legacy_entries = obj.pop("entries")
            if isinstance(obj.get("items"), list):
                obj["items"].extend(legacy_entries)
            else:
                obj["items"] = legacy_entries
            counts["item_group_top_level_entries"] += 1
        extend = obj.get("extend")
        if isinstance(extend, dict) and "entries" in extend and "items" not in extend:
            extend["items"] = extend.pop("entries")
            counts["item_group_extend_entries"] += 1
        group_lists: list[list[Any]] = []
        for key in ("items", "entries"):
            if isinstance(obj.get(key), list):
                group_lists.append(obj[key])
        if isinstance(extend, dict) and isinstance(extend.get("items"), list):
            group_lists.append(extend["items"])
        for group_entries in group_lists:
                normalized_entries: list[Any] = []
                for group_entry in group_entries:
                    if (
                        isinstance(group_entry, list)
                        and len(group_entry) >= 2
                        and isinstance(group_entry[0], str)
                        and isinstance(group_entry[1], (int, float))
                    ):
                        normalized_entries.append({"item": group_entry[0], "prob": group_entry[1]})
                        counts["item_group_array_entries"] += 1
                    elif isinstance(group_entry, str):
                        normalized_entries.append({"item": group_entry})
                        counts["item_group_string_entries"] += 1
                    else:
                        normalized_entries.append(group_entry)
                normalized_entries = [
                    entry
                    for entry in normalized_entries
                    if (
                        not isinstance(entry, dict)
                        or "item" in entry
                        or "group" in entry
                        or "collection" in entry
                        or "distribution" in entry
                    )
                ]
                normalized_entries, removed = dedupe(normalized_entries)
                counts["item_group_entries"] += removed
                for entry in normalized_entries:
                    if not isinstance(entry, dict):
                        continue
                    for obsolete in ("repeat", "ammo-item", "container-item"):
                        if obsolete in entry:
                            del entry[obsolete]
                            counts["item_group_obsolete_fields"] += 1
                    if entry.get("item") in UNCHARGED_GROUP_ITEMS and "charges" in entry:
                        del entry["charges"]
                        counts["item_group_invalid_charges"] += 1
                    if "chance" in entry and "prob" not in entry:
                        entry["prob"] = entry.pop("chance")
                        counts["item_group_chance"] += 1
                    if "entry-wrapper" in entry and "container-item" not in entry:
                        entry["container-item"] = "null"
                        counts["item_group_wrappers"] += 1
                if isinstance(obj.get("items"), list) and obj["items"] is group_entries:
                    obj["items"] = normalized_entries
                elif isinstance(obj.get("entries"), list) and obj["entries"] is group_entries:
                    obj["entries"] = normalized_entries
                elif isinstance(extend, dict) and extend.get("items") is group_entries:
                    extend["items"] = normalized_entries

    if obj.get("type") in {"SCENARIO", "scenario"} and isinstance(obj.get("extend"), dict):
        # Scenario extensions were accepted by older releases but are not a
        # valid H field.  Apply the extension to this concrete scenario,
        # preserving existing scalar values and appending list fields.
        extension = obj.pop("extend")
        if isinstance(extension, dict):
            for key, value in extension.items():
                if isinstance(value, list) and isinstance(obj.get(key), list):
                    merged = obj[key] + value
                    obj[key] = dedupe(merged)[0]
                elif key not in obj:
                    obj[key] = value
        counts["scenario_extensions"] += 1

    if obj.get("type") == "overmap_terrain" and isinstance(obj.get("extend"), dict):
        # H no longer accepts the legacy overmap `extend` wrapper.  Apply its
        # fields directly to this terrain definition; list fields are merged
        # rather than replaced so graphical flags are retained.
        extension = obj.pop("extend")
        if isinstance(extension, dict):
            for key, value in extension.items():
                if isinstance(value, list) and isinstance(obj.get(key), list):
                    obj[key] = dedupe(obj[key] + value)[0]
                elif key not in obj:
                    obj[key] = value
        counts["overmap_extensions"] += 1

    if obj.get("type") == "overmap_terrain" and isinstance(obj.get("delete"), dict):
        # Apply legacy overmap delete directives to the materialized terrain.
        # This keeps the override's intent while removing the unsupported
        # wrapper itself.
        deletion = obj.pop("delete")
        if isinstance(deletion, dict):
            for key, value in deletion.items():
                current = obj.get(key)
                if isinstance(current, list) and isinstance(value, list):
                    obj[key] = [entry for entry in current if entry not in value]
                elif isinstance(current, dict) and isinstance(value, dict):
                    for nested_key in value:
                        current.pop(nested_key, None)
                elif key in obj:
                    obj.pop(key, None)
        counts["overmap_deletes"] += 1

    if obj.get("type") == "mutation" and isinstance(obj.get("extend"), dict):
        extension = obj.pop("extend")
        if isinstance(extension, dict):
            for key, value in extension.items():
                if isinstance(value, list) and isinstance(obj.get(key), list):
                    obj[key] = dedupe(obj[key] + value)[0]
                elif key not in obj:
                    obj[key] = value
        counts["mutation_extensions"] += 1

    if obj.get("type") == "monstergroup" and isinstance(obj.get("monsters"), list):
        original_monster_count = len(obj["monsters"])
        valid_monsters = [
            entry
            for entry in obj["monsters"]
            if not isinstance(entry, dict) or "monster" in entry or "group" in entry
        ]
        if len(valid_monsters) != len(obj["monsters"]):
            obj["monsters"] = valid_monsters
            counts["monstergroup_entries"] += original_monster_count - len(valid_monsters)

    if obj.get("type") == "vehicle_group" and isinstance(obj.get("vehicles"), list):
        # Older vehicle groups used a synthetic "none" entry to represent no
        # spawn.  H tries to instantiate it during validation and hits an
        # empty-parts assertion; retain the group and all real vehicle IDs.
        vehicles = obj["vehicles"]
        kept_vehicles = [
            entry
            for entry in vehicles
            if not (
                isinstance(entry, list)
                and entry
                and entry[0] == "none"
            )
        ]
        if kept_vehicles != vehicles:
            obj["vehicles"] = kept_vehicles
            counts["vehicle_group_none_entries"] += len(vehicles) - len(kept_vehicles)

    if obj.get("type") == "mapgen":
        map_object = obj.get("object") if isinstance(obj.get("object"), dict) else obj
        for key in ("place_loot", "place_items"):
            entries = map_object.get(key)
            if not isinstance(entries, list):
                continue
            valid_entries = [
                entry
                for entry in entries
                if not isinstance(entry, dict) or "item" in entry or "group" in entry
            ]
            if len(valid_entries) != len(entries):
                map_object[key] = valid_entries
                counts["mapgen_item_entries"] += len(entries) - len(valid_entries)
        palette = map_object.get("items")
        if isinstance(palette, dict):
            valid_palette = {
                symbol: entry
                for symbol, entry in palette.items()
                if not isinstance(entry, dict) or "item" in entry or "group" in entry
            }
            if len(valid_palette) != len(palette):
                map_object["items"] = valid_palette
                counts["mapgen_palette_entries"] += len(palette) - len(valid_palette)

    if obj.get("type") == "mutation_category":
        for key in list(obj):
            if key.startswith("iv_") or key == "junkie_message":
                del obj[key]
                counts["mutation_category_obsolete_fields"] += 1
    if obj.get("type") == "mutation" and "healing_resting" in obj:
        del obj["healing_resting"]
        counts["mutation_obsolete_fields"] += 1

    if obj.get("type") == "technique":
        # These target-state selectors were removed from the H technique
        # schema.  Keep the technique itself and its supported effects.
        for obsolete in ("stunned_target", "downed_target", "req_buffs"):
            if obsolete in obj:
                del obj[obsolete]
                counts["technique_obsolete_fields"] += 1

    if obj.get("type") == "terrain":
        bash = obj.get("bash")
        bash_items = bash.get("items") if isinstance(bash, dict) else None
        if isinstance(bash_items, list):
            default_charge_items = {"t_rock_coal": "coal_lump"}
            kept_bash_items: list[Any] = []
            for bash_item in bash_items:
                if isinstance(bash_item, dict) and "charges" in bash_item and "item" not in bash_item:
                    default_item = default_charge_items.get(obj.get("id"))
                    if default_item:
                        bash_item["item"] = default_item
                        counts["terrain_bash_charge_items"] += 1
                    else:
                        counts["terrain_bash_entries"] += 1
                        continue
                kept_bash_items.append(bash_item)
            bash["items"] = kept_bash_items

    if obj.get("type") == "profession":
        def clean_profession_inventory(value: Any) -> None:
            if isinstance(value, dict):
                for key, child in list(value.items()):
                    if key == "entries" and isinstance(child, list):
                        kept_entries = [
                            entry
                            for entry in child
                            if not isinstance(entry, dict) or "item" in entry or "group" in entry
                        ]
                        counts["profession_item_entries"] += len(child) - len(kept_entries)
                        value[key] = kept_entries
                    else:
                        clean_profession_inventory(child)
            elif isinstance(value, list):
                for child in value:
                    clean_profession_inventory(child)

        clean_profession_inventory(obj.get("items"))

    if obj.get("type") == "region_settings":
        # H no longer reads these legacy trail/weather controls.  Removing
        # only the obsolete members preserves the region and mapgen data.
        regional_obsolete = {
            "clear_trail_terrain",
            "trail_center_variance",
            "trail_terrain",
            "trail_width_offset_max",
            "trail_width_offset_min",
            "weather_types",
            "field_coverage",
        }
        counts["region_obsolete_fields"] += remove_keys_recursive(obj, regional_obsolete)

    counts["obsolete_nested_fields"] += remove_keys_recursive(obj, {"no_infection_chance"})

    if obj.get("type") == "material":
        for obsolete in ("compacts_into", "damage_states", "reinforces"):
            if obsolete in obj:
                del obj[obsolete]
                counts["material_obsolete_fields"] += 1

    material_value = obj.get("material")
    if isinstance(material_value, str) and material_value == "hardsteel":
        obj["material"] = "steel"
        counts["legacy_material_ids"] += 1
    elif isinstance(material_value, list) and "hardsteel" in material_value:
        obj["material"] = ["steel" if value == "hardsteel" else value for value in material_value]
        counts["legacy_material_ids"] += 1
    if obj.get("type") == "ITEM_BLACKLIST" and isinstance(obj.get("items"), list):
        obj["items"], removed = dedupe(obj["items"])
        counts["blacklist_entries"] += removed

    if isinstance(obj.get("dynamic_line"), (dict, list)):
        obj["dynamic_line"] = flatten_dynamic_line(obj["dynamic_line"])
        counts["dynamic_line_objects"] += 1

    if obj.get("type") == "mapgen" and isinstance(obj.get("object"), dict):
        map_object = obj["object"]
        rows = map_object.get("rows")
        if isinstance(rows, list):
            # Nested mapgens inherit their terrain from the caller and H does
            # not accept a fill_ter member in their object payload.
            if obj.get("nested_mapgen_id"):
                map_object.pop("fill_ter", None)
            # H requires a fill terrain whenever a row glyph is not explicitly
            # mapped, including mapgens that also reference a palette or nested
            # mapgen.  Preserve any explicit fill_ter and add a harmless
            # regional fallback to legacy row maps that omit one.
            if "fill_ter" not in map_object and not obj.get("nested_mapgen_id"):
                map_object["fill_ter"] = "t_region_groundcover"
                counts["mapgen_fill_terrain"] += 1
            # Some legacy mapgens reference palettes that are no longer
            # shipped by the mod.  H then rejects every glyph not covered by
            # a local terrain/furniture mapping.  Keep the map layout intact
            # and give only those orphan glyphs a harmless terrain fallback;
            # valid palette mappings continue to take precedence.
            if rows:
                fallback = map_object.get("fill_ter") or "t_region_groundcover"
                terrain = map_object.setdefault("terrain", {})
                furniture = map_object.get("furniture", {})
                known = set(terrain) | set(furniture)
                for row in rows:
                    if not isinstance(row, str):
                        continue
                    for glyph in set(row):
                        if glyph != " " and glyph not in known:
                            terrain[glyph] = fallback
                            known.add(glyph)
            mapgensize = map_object.get("mapgensize") or obj.get("mapgensize")
            expected_height = None
            expected_width = None
            if isinstance(mapgensize, list) and len(mapgensize) == 2 and isinstance(mapgensize[1], int):
                expected_height = mapgensize[1]
                if isinstance(mapgensize[0], int):
                    expected_width = mapgensize[0]
            else:
                om_terrain = obj.get("om_terrain")
                if isinstance(om_terrain, list) and om_terrain and all(isinstance(entry, list) for entry in om_terrain):
                    expected_height = len(om_terrain) * 24
                    expected_width = max((len(entry) for entry in om_terrain), default=1) * 24
                elif isinstance(om_terrain, (list, str)):
                    expected_height = 24
                    expected_width = 24
            if expected_height is not None and len(rows) > expected_height:
                trailing = rows[expected_height:]
                if all(isinstance(row, str) and not row.strip() for row in trailing):
                    del rows[expected_height:]
                    counts["mapgen_rows_trimmed"] += len(trailing)
            elif expected_height is not None and len(rows) < expected_height:
                missing_rows = expected_height - len(rows)
                rows.extend([" " * (expected_width or 24) for _ in range(missing_rows)])
                counts["mapgen_rows_padded"] += missing_rows
            if expected_width is not None:
                for index, row in enumerate(rows):
                    if isinstance(row, str) and len(row) < expected_width:
                        rows[index] = row + " " * (expected_width - len(row))
                        counts["mapgen_columns_padded"] += 1

    normalize_comment_keys(obj, counts)
    clean_explosion_actions(obj, counts)
    clean_legacy_use_actions(obj, counts)
    normalize_human_text(obj, counts)
    remove_obsolete_item_refs(obj, counts)
    counts["empty_list_entries"] += clean_structural_list_entries(obj)


def load_json(path: Path) -> Any:
    return json.loads(strip_json_comments(path.read_text(encoding="utf-8-sig")))


def iter_json(paths: Iterable[Path]) -> Iterable[Path]:
    seen: set[Path] = set()
    for path in paths:
        candidates = [path] if path.is_file() else sorted(path.rglob("*.json"))
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield candidate


def normalize_copy_from_order(value: Any) -> None:
    """Put H's inheritance marker before inherited fields.

    The 0.H JSON factories resolve ``copy-from`` while reading an object.  A
    legacy definition that places the marker after all of its inherited fields
    is consequently parsed as though those fields belonged to an unknown
    object, producing a cascade of misleading "invalid or misplaced field"
    errors.  Keep the definition intact, but place its identity and type first
    and the inheritance marker immediately after them.
    """

    if isinstance(value, dict):
        if isinstance(value.get("copy-from"), str):
            ordered: dict[str, Any] = {}
            for key in ("id", "abstract", "type", "copy-from"):
                if key in value:
                    ordered[key] = value[key]
            for key, child in value.items():
                if key not in ordered:
                    ordered[key] = child
            value.clear()
            value.update(ordered)
        for child in value.values():
            normalize_copy_from_order(child)
    elif isinstance(value, list):
        for child in value:
            normalize_copy_from_order(child)


def write_json(path: Path, data: Any, formatter: Path | None) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if formatter and formatter.exists():
        # CDDA's formatter returns 1 when it changed a file and 0 when the
        # file was already formatted, so both are successful outcomes here.
        result = subprocess.run([str(formatter), str(path)], check=False)
        if result.returncode not in (0, 1):
            raise subprocess.CalledProcessError(result.returncode, result.args)


def general_pass(
    files: list[Path],
    h_files: list[Path],
    dry_run: bool,
    formatter: Path | None,
    prune_core_copies: bool = False,
) -> collections.Counter[str]:
    totals: collections.Counter[str] = collections.Counter()
    # Optional built-in mods are not part of the H core contract and can
    # redefine core-looking IDs with different rotation/flags semantics.
    h_core_files = [path for path in h_files if "mods" not in {part.lower() for part in path.parts}]
    h_index, h_sources, _ = collect_items(h_core_files)
    h_material_ids: set[str] = set()
    h_core_keys: set[tuple[str, str]] = set()
    h_core_item_ids: set[str] = set()
    h_core_bionic_item_ids: set[str] = set()
    h_core_monster_groups: set[str] = set()
    h_core_monster_ids: set[str] = set()
    h_core_recipe_keys: set[tuple[str, str, str]] = set()
    h_rotating_overmap_bases: set[str] = set()
    h_nonrotating_overmap_bases: set[str] = set()
    h_overmap_definitions: dict[str, dict[str, Any]] = {}
    h_core_monster_factions: set[str] = set()
    local_index, _, _ = collect_items(files)
    # Keep a type-aware index for self-copy expansion beyond ordinary items.
    # Mods also use self-copy overrides for monsters, mutations, terrain,
    # spells, and other factories, so an item-only index leaves most of them
    # unresolved and risks losing their contents.
    definition_index: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    definition_sources: dict[int, Path] = {}

    def collect_definitions(paths: list[Path]) -> None:
        for definition_path in paths:
            try:
                definition_data = load_json(definition_path)
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            definition_entries = definition_data if isinstance(definition_data, list) else [definition_data]
            for definition in definition_entries:
                if not isinstance(definition, dict) or not isinstance(definition.get("type"), str):
                    continue
                ident = definition.get("id", definition.get("abstract"))
                if not isinstance(ident, str):
                    if definition.get("type") in {"MONSTER_FACTION", "monstergroup"}:
                        ident = definition.get("name")
                if isinstance(ident, str) and ident:
                    definition_index[(definition["type"], ident)].append(definition)
                    definition_sources[id(definition)] = definition_path

    collect_definitions(h_core_files)
    collect_definitions(files)
    local_bionic_item_ids = {
        ident for ident, entries in local_index.items() if any(entry.get("type") == "BIONIC_ITEM" for entry in entries)
    }
    pruned_definition_ids: set[str] = set()
    for h_path in h_core_files:
        try:
            h_data = load_json(h_path)
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        h_entries = h_data if isinstance(h_data, list) else [h_data]
        for h_entry in h_entries:
            if isinstance(h_entry, dict) and h_entry.get("type") == "overmap_terrain":
                h_ident = h_entry.get("id")
                h_idents = [h_ident] if isinstance(h_ident, str) else h_ident
                if isinstance(h_idents, list):
                    for ident in h_idents:
                        if isinstance(ident, str):
                            h_overmap_definitions[ident] = h_entry
            if isinstance(h_entry, dict) and h_entry.get("type") == "MONSTER_FACTION":
                h_name = h_entry.get("name")
                if isinstance(h_name, str):
                    h_core_monster_factions.add(h_name)
            if isinstance(h_entry, dict) and h_entry.get("type") == "MONSTER":
                h_monster_id = h_entry.get("id")
                if isinstance(h_monster_id, str):
                    h_core_monster_ids.add(h_monster_id)
            if isinstance(h_entry, dict) and h_entry.get("type") == "material":
                h_ident = h_entry.get("id")
                if isinstance(h_ident, str):
                    h_material_ids.add(h_ident)
            if prune_core_copies and isinstance(h_entry, dict):
                h_type = h_entry.get("type")
                h_ident = h_entry.get("id", h_entry.get("abstract"))
                if (
                    isinstance(h_ident, str)
                    and h_type
                    not in {
                        "ITEM_BLACKLIST",
                        "ITEM_GROUP",
                        "MOD_INFO",
                        "item_group",
                        "migration",
                        "monstergroup",
                        "recipe",
                        "recipe_category",
                        "requirement",
                        "snippet",
                        "uncraft",
                    }
                ):
                    h_core_keys.add((str(h_type), h_ident))
                    if h_type in ITEM_TYPES:
                        h_core_item_ids.add(h_ident)
                    if h_type == "BIONIC_ITEM":
                        h_core_bionic_item_ids.add(h_ident)
                if h_type in {"recipe", "uncraft"} and isinstance(h_entry.get("result"), str):
                    h_core_recipe_keys.add((h_type, h_entry["result"], str(h_entry.get("id_suffix", ""))))
                if h_type == "monstergroup" and isinstance(h_entry.get("name"), str):
                    h_core_monster_groups.add(h_entry["name"])

    def overmap_flags(ident: str, seen: set[str] | None = None) -> list[str]:
        seen = set() if seen is None else seen
        if ident in seen:
            return []
        seen.add(ident)
        definition = h_overmap_definitions.get(ident)
        if not definition:
            return []
        flags = definition.get("flags")
        if isinstance(flags, list):
            return [flag for flag in flags if isinstance(flag, str)]
        parent = definition.get("copy-from")
        return overmap_flags(parent, seen) if isinstance(parent, str) else []

    for h_ident in h_overmap_definitions:
        if "NO_ROTATE" in overmap_flags(h_ident):
            h_nonrotating_overmap_bases.add(h_ident)
        else:
            h_rotating_overmap_bases.add(h_ident)

    local_monster_ids: set[str] = set()
    for local_path in files:
        try:
            local_data = load_json(local_path)
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        local_entries = local_data if isinstance(local_data, list) else [local_data]
        for local_entry in local_entries:
            if isinstance(local_entry, dict) and local_entry.get("type") == "MONSTER":
                local_monster_id = local_entry.get("id")
                if isinstance(local_monster_id, str):
                    local_monster_ids.add(local_monster_id)
    active_obsolete_monster_ids = OBSOLETE_MONSTER_IDS - h_core_monster_ids - local_monster_ids

    def finish_armor(obj: dict[str, Any]) -> None:
        if obj.get("type") not in ARMOR_TYPES:
            return
        for key in ("bashing_protection", "cutting_protection", "acid_protection", "fire_protection"):
            if key in obj:
                del obj[key]
                totals["armor_obsolete_protection"] += 1
        legacy_keys = ("covers", "coverage", "encumbrance", "layer")
        if "armor" in obj or not any(key in obj for key in legacy_keys):
            return
        reference = None
        ident = item_id(obj)
        if ident and h_index.get(ident):
            reference = h_index[ident][-1]
        reference_armor = inherited(reference, "armor", h_index, h_sources) if reference else None
        if isinstance(reference_armor, (dict, list)):
            obj["armor"] = copy.deepcopy(reference_armor)
            totals["armor_reference_portions"] += 1
        for key in legacy_keys:
            obj.pop(key, None)
        totals["armor_legacy_without_covers"] += 1

    def expand_copy_from(obj: dict[str, Any]) -> bool:
        """Materialize an override and remove its copy-from link.

        Older mods commonly use this form to override a core item in place.
        Treating it as a circular definition and deleting it loses the entire
        override.  If the H core supplies the referenced item, merge the core
        definition first and retain the mod's override fields.  If the base is
        not present, leave the entry intact so the validator can report it.
        """
        parent_id = obj.get("copy-from")
        if not isinstance(parent_id, str):
            return False
        obj_type = obj.get("type")
        ident = obj.get("id", obj.get("abstract"))
        candidates = definition_index.get((obj_type, parent_id), []) if isinstance(obj_type, str) else []
        candidates = [candidate for candidate in candidates if candidate is not obj]
        # Prefer a real H-core definition, then a non-self definition from the
        # same mod/file, then any other included definition.
        core_candidates = [candidate for candidate in candidates if definition_sources.get(id(candidate)) in h_core_files]
        local_candidates = [
            candidate
            for candidate in candidates
            if definition_sources.get(id(candidate)) == definition_sources.get(id(obj))
            and candidate.get("copy-from") != candidate.get("id")
        ]
        non_self_candidates = [candidate for candidate in candidates if candidate.get("copy-from") != candidate.get("id")]
        candidates = core_candidates or local_candidates or non_self_candidates
        if not candidates:
            # Preserve the mod's own fields even when the external/base
            # definition is unavailable.  Removing only the circular link
            # avoids a hard factory error without inventing a compatibility
            # shim or discarding the extension data.
            obj.pop("copy-from", None)
            if parent_id == ident:
                totals["unresolved_self_copy_entries"] += 1
            else:
                totals["unresolved_copy_from_entries"] += 1
            totals["removed_unresolved_self_copy_links"] += 1
            return False

        # Keep valid inheritance links.  H can resolve these definitions, so
        # expanding them would only duplicate parent data and make later
        # updates harder to maintain.  Broken/self links were handled above.
        totals["kept_copy_from_entries"] += 1
        return False

        def materialize(base: dict[str, Any], seen: set[tuple[str, str]]) -> dict[str, Any]:
            base_type = base.get("type")
            base_id = base.get("id", base.get("abstract"))
            base_key = (base_type, base_id)
            if base_key in seen:
                return {}
            if isinstance(base_type, str) and isinstance(base_id, str):
                seen.add(base_key)
            parent_id = base.get("copy-from")
            merged: dict[str, Any] = {}
            if isinstance(base_type, str) and isinstance(parent_id, str) and parent_id != base_id:
                parents = definition_index.get((base_type, parent_id), [])
                parents = [parent for parent in parents if parent.get("copy-from") != parent.get("id")]
                if parents:
                    merged.update(materialize(parents[-1], seen))
            merged.update(copy.deepcopy(base))
            merged.pop("copy-from", None)
            return merged

        merged = materialize(candidates[-1], set())
        override = copy.deepcopy(obj)
        override.pop("copy-from", None)
        merged.update(override)
        obj.clear()
        obj.update(merged)
        if parent_id == ident:
            totals["expanded_self_copy_entries"] += 1
        else:
            totals["expanded_copy_from_entries"] += 1
        return True

    for path in files:
        try:
            data = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            print(f"[ERROR] {path}: {error}", file=sys.stderr)
            totals["errors"] += 1
            continue

        before = canonical(data)
        if isinstance(data, dict) and data.get("type") == "MOD_INFO":
            data = [data]
            totals["modinfo_wrapped"] += 1
        normalize_optional_mod_item_groups(data, path, totals)
        clean_fantasy_blacklist_refs(data, path, set(h_index), totals)
        if isinstance(data, list):
            original_length = len(data)
            data, removed = dedupe(data)
            data, duplicate_ids = dedupe_top_level_identities(data)
            totals["duplicate_top_level_ids"] += duplicate_ids
            data[:] = [entry for entry in data if entry is not None and entry != {} and entry != []]
            totals["top_level_entries"] += original_length - len(data)
            for entry in data:
                if isinstance(entry, dict):
                    if isinstance(entry.get("copy-from"), str):
                        expand_copy_from(entry)
                    transform_object(entry, totals, active_obsolete_monster_ids)
                    migrate_rotating_overmaps(
                        entry, h_rotating_overmap_bases, h_nonrotating_overmap_bases, totals
                    )
                    finish_armor(entry)
            kept_entries: list[Any] = []
            for entry in data:
                entry_type = entry.get("type") if isinstance(entry, dict) else None
                entry_ident = entry.get("id", entry.get("abstract")) if isinstance(entry, dict) else None
                if entry_type == "sound_effect":
                    # H loads sounds from its built-in registry; legacy JSON
                    # sound_effect objects are rejected by the H factory.
                    totals["obsolete_sound_effects"] += 1
                    continue
                if (
                    entry_type in {"BOOK", "SPELL"}
                    and isinstance(entry, dict)
                    and entry.get("//") == "obsoleted"
                ):
                    totals["obsolete_migration_entries"] += 1
                    continue
                if (
                    entry_type in {"recipe", "uncraft"}
                    and isinstance(entry, dict)
                    and (entry.get("obsolete") is True or not isinstance(entry.get("result"), str))
                ):
                    totals["invalid_recipe_entries"] += 1
                    continue
                if (
                    entry_type == "MONSTER_FACTION"
                    and isinstance(entry, dict)
                    and (
                        entry.get("name") in MONSTER_FACTION_MIGRATIONS
                        or entry.get("name") in h_core_monster_factions
                    )
                ):
                    totals["obsolete_monster_factions"] += 1
                    continue
                if (
                    entry_type in {"recipe", "uncraft"}
                    and isinstance(entry, dict)
                    and (
                        entry.get("result") in OBSOLETE_RECIPE_RESULT_IDS
                        or entry.get("result") in LOOPING_ACID_RECIPE_RESULTS
                    )
                ):
                    totals["obsolete_recipe_results"] += 1
                    continue
                if entry_type == "mapgen":
                    om_terrain = entry.get("om_terrain")
                    om_values: list[str] = []
                    stack = [om_terrain]
                    while stack:
                        current = stack.pop()
                        if isinstance(current, str):
                            om_values.append(current)
                        elif isinstance(current, list):
                            stack.extend(current)
                    if any(value in OBSOLETE_MAPGEN_OM_IDS for value in om_values):
                        totals["obsolete_mapgen_entries"] += 1
                        continue
                recipe_key = None
                if isinstance(entry, dict) and entry_type in {"recipe", "uncraft"} and isinstance(entry.get("result"), str):
                    recipe_key = (entry_type, entry["result"], str(entry.get("id_suffix", "")))
                if prune_core_copies and (
                    (
                        isinstance(entry_ident, str)
                        and (
                            (entry_type in ITEM_TYPES and entry_ident in h_core_item_ids)
                            or (str(entry_type), entry_ident) in h_core_keys
                        )
                    )
                    or (recipe_key is not None and recipe_key in h_core_recipe_keys)
                    or (
                        entry_type == "bionic"
                        and isinstance(entry_ident, str)
                        and entry_ident not in h_core_bionic_item_ids
                        and entry_ident not in local_bionic_item_ids
                    )
                    or (
                        entry_type == "monstergroup"
                        and isinstance(entry.get("name"), str)
                        and entry["name"] in h_core_monster_groups
                    )
                    or (
                        entry_type in {"recipe", "uncraft"}
                        and isinstance(entry.get("result"), str)
                        and entry["result"] in pruned_definition_ids
                    )
                ):
                    totals["obsolete_core_copies"] += 1
                    if isinstance(entry_ident, str):
                        pruned_definition_ids.add(entry_ident)
                    continue
                if (
                    isinstance(entry, dict)
                    and entry.get("type") == "material"
                    and "chip_resist" not in entry
                    and entry.get("id") in h_material_ids
                ):
                    totals["obsolete_core_material_copies"] += 1
                    continue
                kept_entries.append(entry)
            data[:] = kept_entries
        elif isinstance(data, dict):
            if isinstance(data.get("copy-from"), str):
                expand_copy_from(data)
            transform_object(data, totals, active_obsolete_monster_ids)
            migrate_rotating_overmaps(
                data, h_rotating_overmap_bases, h_nonrotating_overmap_bases, totals
            )
            finish_armor(data)

        # H resolves inheritance before validating the inherited fields.  A
        # retained legacy marker may be located at the end of an object, which
        # makes otherwise valid fields look misplaced.  Reorder only the
        # marker; all inherited data and valid copy-from links remain intact.
        before_ordered = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        normalize_copy_from_order(data)

        order_changed = json.dumps(data, ensure_ascii=False, separators=(",", ":")) != before_ordered
        if canonical(data) != before or order_changed:
            totals["files_changed"] += 1
            if not dry_run:
                write_json(path, data, formatter)
    return totals


def item_id(obj: dict[str, Any]) -> str | None:
    for key in ("id", "abstract"):
        value = obj.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def collect_items(
    files: Iterable[Path], *, keep_file_data: bool = False
) -> tuple[dict[str, list[dict[str, Any]]], dict[int, Path], dict[Path, Any]]:
    index: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    sources: dict[int, Path] = {}
    file_data: dict[Path, Any] = {}
    for path in files:
        try:
            data = load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if keep_file_data:
            file_data[path] = data
        entries = data if isinstance(data, list) else [data]
        for obj in entries:
            if not isinstance(obj, dict) or obj.get("type") not in ITEM_TYPES:
                continue
            ident = item_id(obj)
            if ident:
                index[ident].append(obj)
                sources[id(obj)] = path
    return index, sources, file_data


def parent_for(obj: dict[str, Any], index: dict[str, list[dict[str, Any]]], source: Path | None, sources: dict[int, Path]) -> dict[str, Any] | None:
    parent_id = obj.get("copy-from")
    if not isinstance(parent_id, str):
        return None
    candidates = index.get(parent_id, [])
    if not candidates:
        return None
    if source:
        local = [candidate for candidate in candidates if sources.get(id(candidate)) == source]
        if local:
            return local[-1]
        same_tree = [candidate for candidate in candidates if sources.get(id(candidate)) and source.parent in sources[id(candidate)].parents]
        if same_tree:
            return same_tree[-1]
    return candidates[-1]


def inherited(obj: dict[str, Any], key: str, index: dict[str, list[dict[str, Any]]], sources: dict[int, Path], seen: set[int] | None = None) -> Any:
    if key in obj:
        return obj[key]
    seen = set() if seen is None else seen
    if id(obj) in seen:
        return None
    seen.add(id(obj))
    parent = parent_for(obj, index, sources.get(id(obj)), sources)
    return inherited(parent, key, index, sources, seen) if parent else None


def has_magazine_pocket(pockets: Any) -> bool:
    if isinstance(pockets, dict):
        pockets = [pockets]
    return isinstance(pockets, list) and any(
        isinstance(pocket, dict) and pocket.get("pocket_type") in {"MAGAZINE", "MAGAZINE_WELL"}
        for pocket in pockets
    )


def tool_pocket_pass(files: list[Path], h_files: list[Path], dry_run: bool, formatter: Path | None) -> collections.Counter[str]:
    local_index, local_sources, file_data = collect_items(files, keep_file_data=True)
    h_index, h_sources, _ = collect_items(h_files)
    index = h_index
    for ident, entries in local_index.items():
        index.setdefault(ident, []).extend(entries)
    sources = {**h_sources, **local_sources}
    totals: collections.Counter[str] = collections.Counter()

    before_by_file = {path: canonical(data) for path, data in file_data.items()}
    visiting: set[int] = set()

    def ensure(obj: dict[str, Any]) -> None:
        if id(obj) in visiting:
            return
        visiting.add(id(obj))
        parent = parent_for(obj, index, sources.get(id(obj)), sources)
        if parent and sources.get(id(parent)) in files:
            ensure(parent)

        ammo = inherited(obj, "ammo", index, sources)
        max_charges = inherited(obj, "max_charges", index, sources)
        pockets = inherited(obj, "pocket_data", index, sources)
        if obj.get("type") in TOOL_TYPES and ammo:
            local_max = obj.get("max_charges")
            if not has_magazine_pocket(pockets) and isinstance(max_charges, (int, float)) and max_charges > 0:
                ammo_values = [ammo] if isinstance(ammo, str) else ammo
                if isinstance(ammo_values, list) and all(isinstance(value, str) for value in ammo_values):
                    magazine_pocket = {
                        "pocket_type": "MAGAZINE",
                        "rigid": True,
                        "ammo_restriction": {value: int(max_charges) for value in ammo_values},
                    }
                    local_pockets = obj.get("pocket_data")
                    if isinstance(local_pockets, list):
                        local_pockets.append(magazine_pocket)
                    else:
                        obj["pocket_data"] = [magazine_pocket]
                    totals["magazine_pockets"] += 1
            if has_magazine_pocket(inherited(obj, "pocket_data", index, sources)):
                if "max_charges" in obj:
                    del obj["max_charges"]
                    totals["redundant_max_charges"] += 1
                if "initial_charges" in obj:
                    del obj["initial_charges"]
                    totals["redundant_initial_charges"] += 1
                if local_max is not None and "pocket_data" not in obj:
                    totals["inherited_magazine_pockets"] += 1

        visiting.remove(id(obj))

    for entries in local_index.values():
        for obj in entries:
            ensure(obj)

    for path, data in file_data.items():
        if canonical(data) != before_by_file[path]:
            totals["files_changed"] += 1
            if not dry_run:
                write_json(path, data, formatter)
    return totals


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--h-data-root", type=Path, help="Optional exact 0.H data tree for copy-from resolution.")
    parser.add_argument("--formatter", type=Path, help="Optional CDDA json_formatter executable.")
    parser.add_argument(
        "--prune-core-copies",
        action="store_true",
        help="Remove obsolete copied core definitions while preserving mod-only objects and JSON files.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--nested-special-only",
        action="store_true",
        help="Only restore H-release monster special-attack, pathing, and faction compatibility tokens.",
    )
    parser.add_argument(
        "--enchantment-values-only",
        action="store_true",
        help="Only migrate or remove enchantment value tokens unavailable in 0.H.",
    )
    parser.add_argument(
        "--overmap-see-cost-only",
        action="store_true",
        help="Only convert named modern overmap see costs to their numeric 0.H values.",
    )
    parser.add_argument(
        "--graphical-overmap-only",
        action="store_true",
        help="Repair graphical overmap overrides that self-copy or inherit missing 0.H terrain definitions.",
    )
    return parser.parse_args()


def nested_special_attack_pass(
    files: list[Path], dry_run: bool, formatter: Path | None
) -> collections.Counter[str]:
    totals: collections.Counter[str] = collections.Counter()

    def fix(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("type") == "GUN" and "gun_type" in value:
                value["type"] = "gun"
                totals["monster_gun_special_types"] += 1
            path_settings = value.get("path_settings")
            if isinstance(path_settings, dict) and "avoid_dangerous_fields" in path_settings:
                del path_settings["avoid_dangerous_fields"]
                totals["h_path_settings_fields"] += 1
            if value.get("type") == "faction" and "fac_food_supply" in value:
                modern_supply = value.pop("fac_food_supply")
                if "food_supply" not in value:
                    if isinstance(modern_supply, dict):
                        value["food_supply"] = int(modern_supply.get("calories", 0))
                    elif isinstance(modern_supply, (int, float)):
                        value["food_supply"] = int(modern_supply)
                    else:
                        value["food_supply"] = 0
                totals["h_faction_food_supply_fields"] += 1
            flags = value.get("flags")
            if isinstance(flags, list):
                for index, flag in enumerate(flags):
                    if flag == "PATH_AVOID_DANGER":
                        flags[index] = "PATH_AVOID_DANGER_1"
                        totals["h_path_avoid_danger_flags"] += 1
            for child in value.values():
                fix(child)
        elif isinstance(value, list):
            for child in value:
                fix(child)

    for path in files:
        try:
            data = load_json(path)
        except Exception:
            totals["errors"] += 1
            continue
        before = canonical(data)
        fix(data)
        if canonical(data) != before:
            totals["files_changed"] += 1
            if not dry_run:
                write_json(path, data, formatter)
    return totals


def enchantment_value_pass(
    files: list[Path], dry_run: bool, formatter: Path | None
) -> collections.Counter[str]:
    totals: collections.Counter[str] = collections.Counter()

    def fix_enchantment(value: Any) -> Any:
        if isinstance(value, dict):
            melee_damage_bonus = value.pop("melee_damage_bonus", None)
            if isinstance(melee_damage_bonus, list):
                migrated_values = value.setdefault("values", [])
                if not isinstance(migrated_values, list):
                    migrated_values = []
                    value["values"] = migrated_values
                for bonus in melee_damage_bonus:
                    if not isinstance(bonus, dict):
                        continue
                    replacement = H_MELEE_DAMAGE_BONUS_VALUES.get(bonus.get("type"))
                    if not replacement:
                        totals["unsupported_melee_damage_bonus"] += 1
                        continue
                    migrated = {"value": replacement}
                    for operation in ("add", "multiply"):
                        if operation in bonus:
                            migrated[operation] = bonus[operation]
                    if len(migrated) > 1:
                        migrated_values.append(migrated)
                        totals["melee_damage_bonus_values"] += 1
            old_value = value.get("value")
            if isinstance(old_value, str) and ("add" in value or "multiply" in value):
                replacement = H_ENCHANTMENT_VALUE_MIGRATIONS.get(old_value)
                if replacement:
                    value["value"] = replacement
                    totals[f"enchantment_value_{old_value}_to_{replacement}"] += 1
                elif old_value in H_UNSUPPORTED_ENCHANTMENT_VALUES:
                    totals[f"unsupported_enchantment_value_{old_value}"] += 1
                    return None
            for key in list(value):
                child = fix_enchantment(value[key])
                if child is None:
                    del value[key]
                else:
                    value[key] = child
            if isinstance(value.get("values"), list):
                value["values"] = [entry for entry in value["values"] if entry is not None]
                if not value["values"]:
                    del value["values"]
            meaningful = set(value) - {"condition", "has"}
            if not meaningful:
                totals["empty_inline_enchantments"] += 1
                return None
        elif isinstance(value, list):
            fixed = []
            for child in value:
                if isinstance(child, dict) and child.get("value") in H_ENCHANTMENT_VALUE_EXPANSIONS:
                    old_value = child["value"]
                    for replacement in H_ENCHANTMENT_VALUE_EXPANSIONS[old_value]:
                        expanded = copy.deepcopy(child)
                        expanded["value"] = replacement
                        fixed.append(expanded)
                    totals[f"expanded_enchantment_value_{old_value}"] += 1
                    continue
                child = fix_enchantment(child)
                if child is not None:
                    fixed.append(child)
            return fixed
        return value

    def visit(value: Any, in_enchantment: bool = False) -> None:
        if isinstance(value, dict):
            is_definition = value.get("type") == "enchantment"
            for key in list(value):
                child = value[key]
                child_context = in_enchantment or is_definition or key in {"enchantments", "passive_effects"}
                if child_context:
                    fixed = fix_enchantment(child)
                    if fixed is None:
                        del value[key]
                    else:
                        value[key] = fixed
                else:
                    visit(child, False)
        elif isinstance(value, list):
            for child in value:
                visit(child, in_enchantment)

    for path in files:
        try:
            data = load_json(path)
        except Exception:
            totals["errors"] += 1
            continue
        before = canonical(data)
        visit(data)
        if canonical(data) != before:
            totals["files_changed"] += 1
            if not dry_run:
                write_json(path, data, formatter)
    return totals


def overmap_see_cost_pass(
    files: list[Path], dry_run: bool, formatter: Path | None
) -> collections.Counter[str]:
    totals: collections.Counter[str] = collections.Counter()

    def fix(value: Any) -> None:
        if isinstance(value, dict):
            see_cost = value.get("see_cost")
            if value.get("type") == "overmap_terrain" and isinstance(see_cost, str):
                if see_cost in H_OVERMAP_SEE_COSTS:
                    value["see_cost"] = H_OVERMAP_SEE_COSTS[see_cost]
                    totals[f"overmap_see_cost_{see_cost}"] += 1
                else:
                    totals[f"unsupported_overmap_see_cost_{see_cost}"] += 1
            for child in value.values():
                fix(child)
        elif isinstance(value, list):
            for child in value:
                fix(child)

    for path in files:
        try:
            data = load_json(path)
        except Exception:
            totals["errors"] += 1
            continue
        before = canonical(data)
        fix(data)
        if canonical(data) != before:
            totals["files_changed"] += 1
            if not dry_run:
                write_json(path, data, formatter)
    return totals


def graphical_overmap_pass(
    files: list[Path], h_data_root: Path, dry_run: bool, formatter: Path | None
) -> collections.Counter[str]:
    totals: collections.Counter[str] = collections.Counter()
    unsafe_overrides = {
        "river_center",
        "river_c_not_ne",
        "river_c_not_nw",
        "river_c_not_se",
        "river_c_not_sw",
        "river_ne",
        "river_nw",
        "river_se",
        "river_sw",
    }
    core_definitions: dict[str, dict[str, Any]] = {}

    for path in iter_json([h_data_root / "json"]):
        try:
            data = load_json(path)
        except Exception:
            continue
        entries = data if isinstance(data, list) else [data]
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("type") != "overmap_terrain":
                continue
            ident = entry.get("id", entry.get("abstract"))
            idents = [ident] if isinstance(ident, str) else ident
            if isinstance(idents, list):
                for value in idents:
                    if isinstance(value, str):
                        core_definitions[value] = entry

    file_data: dict[Path, Any] = {}
    before_by_file: dict[Path, str] = {}
    for path in files:
        try:
            data = load_json(path)
        except Exception:
            totals["errors"] += 1
            continue
        file_data[path] = data
        before_by_file[path] = canonical(data)

    removed: set[int] = set()
    overmap_entries: list[dict[str, Any]] = []
    for data in file_data.values():
        entries = data if isinstance(data, list) else [data]
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("type") != "overmap_terrain":
                continue
            overmap_entries.append(entry)
            ident = entry.get("id", entry.get("abstract"))
            if isinstance(ident, str) and entry.get("copy-from") == ident:
                core = core_definitions.get(ident)
                if core is None:
                    removed.add(id(entry))
                    totals["missing_self_copy_overmaps"] += 1
                    continue
                overlay = {key: copy.deepcopy(value) for key, value in entry.items() if key != "copy-from"}
                entry.clear()
                entry.update(copy.deepcopy(core))
                entry.update(overlay)
                totals["expanded_self_copy_overmaps"] += 1

    for entry in overmap_entries:
        if id(entry) in removed:
            continue
        ident = entry.get("id")
        if isinstance(ident, str) and ident in unsafe_overrides:
            removed.add(id(entry))
            totals["unsafe_graphical_overrides"] += 1
        elif isinstance(ident, str) and ident not in core_definitions:
            removed.add(id(entry))
            totals["obsolete_graphical_overmaps"] += 1
        elif isinstance(ident, list):
            retained = [value for value in ident if isinstance(value, str) and value in core_definitions]
            totals["obsolete_graphical_overmap_ids"] += len(ident) - len(retained)
            if retained:
                entry["id"] = retained
            else:
                removed.add(id(entry))
                totals["obsolete_graphical_overmaps"] += 1

    # A number of old graphical definitions inherit helper terrains that no
    # longer exist in 0.H.  Remove only those broken entries, then repeat so
    # descendants of a removed helper are handled as well.
    changed = True
    while changed:
        changed = False
        local_definitions: set[str] = set()
        for entry in overmap_entries:
            if id(entry) in removed:
                continue
            ident = entry.get("id", entry.get("abstract"))
            idents = [ident] if isinstance(ident, str) else ident
            if isinstance(idents, list):
                local_definitions.update(value for value in idents if isinstance(value, str))
        available = set(core_definitions) | local_definitions
        for entry in overmap_entries:
            if id(entry) in removed:
                continue
            parent = entry.get("copy-from")
            if isinstance(parent, str) and parent not in available:
                removed.add(id(entry))
                totals["missing_parent_overmaps"] += 1
                changed = True

    for path, data in file_data.items():
        if isinstance(data, list):
            data[:] = [entry for entry in data if id(entry) not in removed]
        elif id(data) in removed:
            data = []
            file_data[path] = data
        if canonical(data) != before_by_file[path]:
            totals["files_changed"] += 1
            if not dry_run:
                write_json(path, data, formatter)
    return totals


def main() -> int:
    args = parse_args()
    files = list(iter_json(args.paths))
    if args.nested_special_only:
        totals = nested_special_attack_pass(files, args.dry_run, args.formatter)
        print(json.dumps({"nested_special_attacks": totals}, indent=2, sort_keys=True))
        return 1 if totals["errors"] else 0
    if args.enchantment_values_only:
        totals = enchantment_value_pass(files, args.dry_run, args.formatter)
        print(json.dumps({"enchantment_values": totals}, indent=2, sort_keys=True))
        return 1 if totals["errors"] else 0
    if args.overmap_see_cost_only:
        totals = overmap_see_cost_pass(files, args.dry_run, args.formatter)
        print(json.dumps({"overmap_see_costs": totals}, indent=2, sort_keys=True))
        return 1 if totals["errors"] else 0
    if args.graphical_overmap_only:
        if args.h_data_root is None:
            print("--graphical-overmap-only requires --h-data-root", file=sys.stderr)
            return 2
        totals = graphical_overmap_pass(files, args.h_data_root, args.dry_run, args.formatter)
        print(json.dumps({"graphical_overmaps": totals}, indent=2, sort_keys=True))
        return 1 if totals["errors"] else 0
    h_files = list(iter_json([args.h_data_root])) if args.h_data_root else []
    general = general_pass(files, h_files, args.dry_run, args.formatter, args.prune_core_copies)
    pockets = tool_pocket_pass(files, h_files, args.dry_run, args.formatter)
    print(json.dumps({"general": general, "tool_pockets": pockets}, indent=2, sort_keys=True))
    return 1 if general["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
