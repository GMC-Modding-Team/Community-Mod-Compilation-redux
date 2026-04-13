#!/usr/bin/env python3
"""
update_legacy_json.py
=====================
Scans one or more Cataclysm: DDA JSON files and updates legacy / obsolete
fields to the modern format documented in Updating_Legacy_JSON.md.

Usage
-----
  # Update a single file (in-place):
  python3 update_legacy_json.py path/to/file.json

  # Recursively update every .json file in a directory:
  python3 update_legacy_json.py path/to/mod/

  # Dry-run (preview changes without writing):
  python3 update_legacy_json.py path/to/mod/ --dry-run

Transformations applied
-----------------------
  1.  ident                     -> id
  2.  "ammo": "x"               -> "ammo": [ "x" ]          (GUN type)
  3.  "damage": N               -> "damage": { "damage_type": "bullet", "amount": N }
  4.  "damage": N, "pierce": M  -> "damage": { ..., "armor_penetration": M }
  5.  "barrel_length": N        -> "barrel_volume": "N*250 ml"
  6.  "blueprint": "x"          -> "blueprint": [ "x" ]
  7.  "copy_from"               -> "copy-from"
  8.  "looks-like"              -> "looks_like"
  9.  "material": "x"           -> "material": [ "x" ]
  10. "type": "CONTAINER"       -> "type": "GENERIC"
  11. "volume": N               -> "volume": "N*250 ml"  (0 -> "1 ml")
  12. "weight": N               -> "weight": "N g"
  13. "effect": "target_attack" -> "effect": "attack"
  14. "mod-type": "SUPPLEMENTAL"-> "category": "SUPPLEMENTAL"
  15. "author": "x"             -> "authors": [ "x" ]
  16. "note":                   -> "//"
  17. "price": N                -> "price": "N cent"
  18. "price_postapoc": N       -> "price_postapoc": "N cent"
  19. "min_melee": N            -> skill_requirements entry  (merged with min_unarmed)
  20. "min_unarmed": N          -> skill_requirements entry  (merged with min_melee)
  21. "bashing": N, "cutting": M-> "melee_damage": { "bash": N, "cut": M }
  22. "bash_resist": N, etc.    -> "resist": { "bash": N, ... }
"""

import os
import re
import argparse
import sys


# ---------------------------------------------------------------------------
# Individual transformation helpers
# ---------------------------------------------------------------------------

def _sub(pattern, repl, text, flags=0):
    """Thin wrapper around re.sub for readability."""
    return re.sub(pattern, repl, text, flags=flags)


def fix_ident(content):
    """Replace "ident": with "id":"""
    return _sub(r'"ident"\s*:', '"id":', content)


def fix_ammo_type(content):
    """
    "ammo": "x"  ->  "ammo": [ "x" ]
    Only when the value is a bare string (not already an array).
    """
    return _sub(r'"ammo"\s*:\s*"([^"]+)"', r'"ammo": [ "\1" ]', content)


def fix_damage(content):
    """
    "damage": N, "pierce": M  ->  "damage": { "damage_type": "bullet", "amount": N, "armor_penetration": M }
    "damage": N               ->  "damage": { "damage_type": "bullet", "amount": N }
    """
    # Combined form first (with pierce on the same or next line)
    content = _sub(
        r'"damage"\s*:\s*(\d+)\s*,\s*"pierce"\s*:\s*(\d+)',
        r'"damage": { "damage_type": "bullet", "amount": \1, "armor_penetration": \2 }',
        content,
        flags=re.DOTALL,
    )
    # Simple numeric form (guard against already-converted objects)
    content = _sub(
        r'"damage"\s*:\s*(\d+)(?!\s*[,}]?\s*"damage_type")',
        r'"damage": { "damage_type": "bullet", "amount": \1 }',
        content,
    )
    return content


def fix_barrel_length(content):
    """
    "barrel_length": N  ->  "barrel_volume": "N*250 ml"
    """
    def _replace(m):
        return f'"barrel_volume": "{int(m.group(1)) * 250} ml"'
    return _sub(r'"barrel_length"\s*:\s*(\d+)', _replace, content)


def fix_blueprint(content):
    """
    "blueprint": "x"  ->  "blueprint": [ "x" ]
    """
    return _sub(r'"blueprint"\s*:\s*"([^"]*)"', r'"blueprint": [ "\1" ]', content)


def fix_copy_from(content):
    """copy_from -> copy-from"""
    return _sub(r'"copy_from"\s*:', '"copy-from":', content)


def fix_looks_like(content):
    """looks-like -> looks_like"""
    return _sub(r'"looks-like"\s*:', '"looks_like":', content)


def fix_material(content):
    """
    "material": "x"  ->  "material": [ "x" ]
    """
    return _sub(r'"material"\s*:\s*"([^"]+)"', r'"material": [ "\1" ]', content)


def fix_container_type(content):
    """
    "type": "CONTAINER"  ->  "type": "GENERIC"
    """
    return _sub(r'"type"\s*:\s*"CONTAINER"', '"type": "GENERIC"', content)


def fix_volume(content):
    """
    "volume": N  ->  "volume": "N*250 ml"   (N==0 becomes "1 ml")
    Skips values that are already strings.
    """
    def _replace(m):
        val = int(m.group(1))
        ml = 1 if val == 0 else val * 250
        return f'"volume": "{ml} ml"'
    return _sub(r'"volume"\s*:\s*(\d+)', _replace, content)


def fix_folded_volume(content):
    """
    "folded_volume": N  ->  "folded_volume": "N*250 ml"
    """
    def _replace(m):
        val = int(m.group(1))
        return f'"folded_volume": "{val * 250} ml"'
    return _sub(r'"folded_volume"\s*:\s*(\d+)', _replace, content)


def fix_integral_volume(content):
    """
    "integral_volume": N  ->  "integral_volume": "N*250 ml"
    """
    def _replace(m):
        val = int(m.group(1))
        return f'"integral_volume": "{val * 250} ml"'
    return _sub(r'"integral_volume"\s*:\s*(\d+)', _replace, content)


def fix_weight(content):
    """
    "weight": N  ->  "weight": "N g"
    NOTE: selected object types (e.g. mapgen / mod_tileset) skip this
    transform via per-object pipeline selection.
    """
    return _sub(r'"weight"\s*:\s*(\d+)', r'"weight": "\1 g"', content)


def fix_effect(content):
    """
    "effect": "target_attack"  ->  "effect": "attack"
    """
    return _sub(r'"effect"\s*:\s*"target_attack"', '"effect": "attack"', content)


def fix_mod_type(content):
    """
    "mod-type": "SUPPLEMENTAL"  ->  "category": "SUPPLEMENTAL"
    """
    return _sub(r'"mod-type"\s*:\s*"SUPPLEMENTAL"', '"category": "SUPPLEMENTAL"', content)


def fix_author(content):
    """
    "author": "x"  ->  "authors": [ "x" ]
    """
    return _sub(r'"author"\s*:\s*"([^"]+)"', r'"authors": [ "\1" ]', content)


def fix_note(content):
    """
    "note":  ->  "//"
    """
    return _sub(r'"note"\s*:', '"//":', content)


def _mask_proportional(content):
    """
    Replace the contents of every "proportional": { ... } block with a
    placeholder so that subsequent transforms cannot touch them.
    Returns (masked_content, list_of_original_blocks).

    The placeholder format is  \x00PROP<index>\x00  which cannot appear in
    valid JSON, making it safe to restore later.
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"proportional"\s*:\s*\{')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        # Append everything up to the opening brace of the proportional block
        result.append(content[i:m.start()])
        # Find the matching closing brace, respecting nesting and strings
        brace_start = m.end() - 1  # position of the '{'
        depth = 0
        in_str = False
        escape = False
        j = brace_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        block = content[brace_start:j]          # the full { ... } block
        key_prefix = content[m.start():brace_start]  # '"proportional": '
        idx = len(originals)
        originals.append(key_prefix + block)
        result.append(f'\x00PROP{idx}\x00')
        i = j
    return ''.join(result), originals


def _restore_proportional(content, originals):
    """Restore the original proportional blocks from their placeholders."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00PROP{idx}\x00', original)
    return content


def _mask_fg_weights(content):
    """
    Mask numeric "weight" entries inside every "fg": [ ... ] block so that
    fix_weight cannot convert them to grams.
    Returns (masked_content, list_of_original_weight_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"fg"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this fg array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        fg_block = content[bracket_start:j]

        def _replace_weight_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00FGW{idx}\x00'

        # Mask only numeric weight tokens inside fg objects.
        fg_block = re.sub(r'"weight"\s*:\s*\d+', _replace_weight_token, fg_block)
        result.append(key_prefix + fg_block)
        i = j

    return ''.join(result), originals


def _restore_fg_weights(content, originals):
    """Restore masked numeric fg weight tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00FGW{idx}\x00', original)
    return content


def _mask_gun_data_ammo(content):
    """
    Mask string "ammo" entries inside every "gun_data": { ... } block so
    fix_ammo_type cannot convert them to arrays.
    Returns (masked_content, list_of_original_ammo_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"gun_data"\s*:\s*\{')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing brace for this gun_data object.
        brace_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = brace_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():brace_start]
        gun_data_block = content[brace_start:j]

        def _replace_ammo_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00GDA{idx}\x00'

        gun_data_block = re.sub(r'"ammo"\s*:\s*"[^"]+"', _replace_ammo_token, gun_data_block)
        result.append(key_prefix + gun_data_block)
        i = j

    return ''.join(result), originals


def _restore_gun_data_ammo(content, originals):
    """Restore masked string gun_data ammo tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00GDA{idx}\x00', original)
    return content


def _mask_monsters_weights(content):
    """
    Mask numeric "weight" entries inside every "monsters": [ ... ] block so
    fix_weight cannot convert weighted spawn entries to grams.
    Returns (masked_content, list_of_original_weight_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"monsters"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this monsters array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        monsters_block = content[bracket_start:j]

        def _replace_weight_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00MSW{idx}\x00'

        monsters_block = re.sub(r'"weight"\s*:\s*\d+', _replace_weight_token, monsters_block)
        result.append(key_prefix + monsters_block)
        i = j

    return ''.join(result), originals


def _restore_monsters_weights(content, originals):
    """Restore masked numeric monsters weight tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00MSW{idx}\x00', original)
    return content


def _mask_mapgen_weights(content):
    """
    Mask numeric "weight" entries inside every "mapgen": [ ... ] block so
    mapgen weighted entries are not converted to grams.
    Returns (masked_content, list_of_original_weight_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"mapgen"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this mapgen array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        mapgen_block = content[bracket_start:j]

        def _replace_weight_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00MGW{idx}\x00'

        mapgen_block = re.sub(r'"weight"\s*:\s*\d+', _replace_weight_token, mapgen_block)
        result.append(key_prefix + mapgen_block)
        i = j

    return ''.join(result), originals


def _restore_mapgen_weights(content, originals):
    """Restore masked numeric mapgen weight tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00MGW{idx}\x00', original)
    return content


def _mask_relative_price_weight(content):
    """
    Mask numeric "price", "price_postapoc", and "weight" entries inside every
    "relative": { ... } block so those relative modifiers stay unchanged.
    Returns (masked_content, list_of_original_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"relative"\s*:\s*\{')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing brace for this relative object.
        brace_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = brace_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():brace_start]
        relative_block = content[brace_start:j]

        def _replace_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00REL{idx}\x00'

        relative_block = re.sub(
            r'"(?:price|price_postapoc|weight)"\s*:\s*\d+',
            _replace_token,
            relative_block,
        )
        result.append(key_prefix + relative_block)
        i = j

    return ''.join(result), originals


def _restore_relative_price_weight(content, originals):
    """Restore masked numeric relative price/weight tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00REL{idx}\x00', original)
    return content


def _mask_variants_weights(content):
    """
    Mask numeric "weight" entries inside every "variants": [ ... ] block so
    variant metadata weights are not converted to grams.
    Returns (masked_content, list_of_original_weight_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"variants"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this variants array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        variants_block = content[bracket_start:j]

        def _replace_weight_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00VRW{idx}\x00'

        variants_block = re.sub(r'"weight"\s*:\s*\d+', _replace_weight_token, variants_block)
        result.append(key_prefix + variants_block)
        i = j

    return ''.join(result), originals


def _restore_variants_weights(content, originals):
    """Restore masked numeric variants weight tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00VRW{idx}\x00', original)
    return content


def _mask_phases_weights(content):
    """
    Mask numeric "weight" entries inside every "phases": [ ... ] block so
    weighted phase entries are not converted to grams.
    Returns (masked_content, list_of_original_weight_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"phases"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this phases array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        phases_block = content[bracket_start:j]

        def _replace_weight_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00PHW{idx}\x00'

        phases_block = re.sub(r'"weight"\s*:\s*\d+', _replace_weight_token, phases_block)
        result.append(key_prefix + phases_block)
        i = j

    return ''.join(result), originals


def _restore_phases_weights(content, originals):
    """Restore masked numeric phases weight tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00PHW{idx}\x00', original)
    return content


def _mask_price_rules_prices(content):
    """
    Mask numeric "price" and "price_postapoc" entries inside every
    "price_rules": [ ... ] block so pricing rules remain untouched.
    Returns (masked_content, list_of_original_price_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"price_rules"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this price_rules array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        price_rules_block = content[bracket_start:j]

        def _replace_price_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00PRS{idx}\x00'

        price_rules_block = re.sub(
            r'"(?:price|price_postapoc)"\s*:\s*\d+(?:\.\d+)?',
            _replace_price_token,
            price_rules_block,
        )
        result.append(key_prefix + price_rules_block)
        i = j

    return ''.join(result), originals


def _restore_price_rules_prices(content, originals):
    """Restore masked numeric price_rules price tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00PRS{idx}\x00', original)
    return content


def _mask_companion_skill_practice_weights(content):
    """
    Mask numeric "weight" entries inside every "companion_skill_practice":
    [ ... ] block so weighted skill-practice entries remain untouched.
    Returns (masked_content, list_of_original_weight_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"companion_skill_practice"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this companion_skill_practice array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        practice_block = content[bracket_start:j]

        def _replace_weight_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00CSP{idx}\x00'

        practice_block = re.sub(r'"weight"\s*:\s*\d+', _replace_weight_token, practice_block)
        result.append(key_prefix + practice_block)
        i = j

    return ''.join(result), originals


def _restore_companion_skill_practice_weights(content, originals):
    """Restore masked numeric companion_skill_practice weight tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00CSP{idx}\x00', original)
    return content


def _mask_search_data_material(content):
    """
    Mask "material" entries inside every "search_data": [ ... ] block so
    fix_material does not alter search metadata.
    Returns (masked_content, list_of_original_material_tokens).
    """
    originals = []
    result = []
    i = 0
    pattern = re.compile(r'"search_data"\s*:\s*\[')
    while i < len(content):
        m = pattern.search(content, i)
        if not m:
            result.append(content[i:])
            break
        result.append(content[i:m.start()])

        # Find matching closing bracket for this search_data array.
        bracket_start = m.end() - 1
        depth = 0
        in_str = False
        escape = False
        j = bracket_start
        while j < len(content):
            ch = content[j]
            if escape:
                escape = False
                j += 1
                continue
            if ch == '\\' and in_str:
                escape = True
                j += 1
                continue
            if ch == '"':
                in_str = not in_str
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1

        key_prefix = content[m.start():bracket_start]
        search_data_block = content[bracket_start:j]

        def _replace_material_token(match):
            idx = len(originals)
            originals.append(match.group(0))
            return f'\x00SDM{idx}\x00'

        # Protect both string and array material forms.
        search_data_block = re.sub(
            r'"material"\s*:\s*"[^"]+"|"material"\s*:\s*\[[^\]]*\]',
            _replace_material_token,
            search_data_block,
        )
        result.append(key_prefix + search_data_block)
        i = j

    return ''.join(result), originals


def _restore_search_data_material(content, originals):
    """Restore masked search_data material tokens."""
    for idx, original in enumerate(originals):
        content = content.replace(f'\x00SDM{idx}\x00', original)
    return content


def fix_price(content):
    """
    "price": N          ->  "price": "N cent"
    "price_postapoc": N ->  "price_postapoc": "N cent"
    """
    content = _sub(r'"price"\s*:\s*(\d+)', r'"price": "\1 cent"', content)
    content = _sub(r'"price_postapoc"\s*:\s*(\d+)', r'"price_postapoc": "\1 cent"', content)
    return content


def fix_skill_requirements(content):
    """
    Merge "min_melee" and "min_unarmed" into a single "skill_requirements" array.
    If only one is present, emit a single-entry array.
    If both are present on adjacent lines, merge them.
    Zero values are dropped per the spec.
    """
    # Both on adjacent lines (melee first)
    content = _sub(
        r'"min_melee"\s*:\s*(\d+)\s*,\s*\n\s*"min_unarmed"\s*:\s*(\d+)',
        lambda m: (
            '"skill_requirements": [ { "name": "melee", "level": ' + m.group(1) + ' }, '
            '{ "name": "unarmed", "level": ' + m.group(2) + ' } ]'
            if int(m.group(1)) > 0 and int(m.group(2)) > 0
            else (
                '"skill_requirements": [ { "name": "melee", "level": ' + m.group(1) + ' } ]'
                if int(m.group(1)) > 0
                else '"skill_requirements": [ { "name": "unarmed", "level": ' + m.group(2) + ' } ]'
            )
        ),
        content,
    )
    # Both on adjacent lines (unarmed first)
    content = _sub(
        r'"min_unarmed"\s*:\s*(\d+)\s*,\s*\n\s*"min_melee"\s*:\s*(\d+)',
        lambda m: (
            '"skill_requirements": [ { "name": "unarmed", "level": ' + m.group(1) + ' }, '
            '{ "name": "melee", "level": ' + m.group(2) + ' } ]'
            if int(m.group(1)) > 0 and int(m.group(2)) > 0
            else (
                '"skill_requirements": [ { "name": "unarmed", "level": ' + m.group(1) + ' } ]'
                if int(m.group(1)) > 0
                else '"skill_requirements": [ { "name": "melee", "level": ' + m.group(2) + ' } ]'
            )
        ),
        content,
    )
    # Remaining single occurrences
    def _melee(m):
        val = int(m.group(1))
        if val == 0:
            return ''
        return f'"skill_requirements": [ {{ "name": "melee", "level": {val} }} ]'
    content = _sub(r'"min_melee"\s*:\s*(\d+)', _melee, content)

    def _unarmed(m):
        val = int(m.group(1))
        if val == 0:
            return ''
        return f'"skill_requirements": [ {{ "name": "unarmed", "level": {val} }} ]'
    content = _sub(r'"min_unarmed"\s*:\s*(\d+)', _unarmed, content)

    return content


def fix_melee_damage(content):
    """
    "bashing": N, "cutting": M  ->  "melee_damage": { "bash": N, "cut": M }
    """
    return _sub(
        r'"bashing"\s*:\s*(\d+)\s*,\s*"cutting"\s*:\s*(\d+)',
        r'"melee_damage": { "bash": \1, "cut": \2 }',
        content,
    )


def fix_resist(content):
    """
    Merge individual *_resist keys into a single "resist" object.
    bash_resist, cut_resist, bullet_resist, acid_resist, fire_resist, elec_resist
    """
    resist_keys = {
        'bash_resist':   'bash',
        'cut_resist':    'cut',
        'bullet_resist': 'bullet',
        'acid_resist':   'acid',
        'fire_resist':   'heat',
        'elec_resist':   'electric',
    }

    # Collect all present resist keys and their values
    found = {}
    for legacy_key, modern_key in resist_keys.items():
        m = re.search(rf'"{legacy_key}"\s*:\s*(\d+)', content)
        if m:
            found[legacy_key] = (modern_key, int(m.group(1)))

    if not found:
        return content

    # Build the resist object
    resist_parts = ', '.join(
        f'"{modern}": {val}' for _, (modern, val) in found.items()
    )
    resist_obj = f'"resist": {{ {resist_parts} }}'

    # Remove the individual keys
    for legacy_key in found:
        content = _sub(rf',?\s*"{legacy_key}"\s*:\s*\d+', '', content)

    # Insert the resist object after the last removed position
    # (simple approach: append before the closing brace of the object block)
    content = content.rstrip()
    # Find a sensible insertion point: before the last `}` of the enclosing object
    # We'll just append the key before the final closing brace of the first object
    # that had the resist keys. For safety, we insert it as a new line before the
    # first lone `}` we encounter after stripping.
    content = re.sub(r'(\n\s*\})', f',\n    {resist_obj}\\1', content, count=1)
    return content


# ---------------------------------------------------------------------------
# Master pipeline
# ---------------------------------------------------------------------------

TRANSFORMS = [
    fix_ident,
    fix_ammo_type,
    fix_damage,
    fix_barrel_length,
    fix_blueprint,
    fix_copy_from,
    fix_looks_like,
    fix_material,
    fix_container_type,
    fix_volume,
    fix_folded_volume,
    fix_integral_volume,
    fix_weight,
    fix_effect,
    fix_mod_type,
    fix_author,
    fix_note,
    fix_price,
    fix_skill_requirements,
    fix_melee_damage,
    fix_resist,
]


# ---------------------------------------------------------------------------
# Per-type pipeline variants
# ---------------------------------------------------------------------------

# mapgen: leave weight untouched
_TRANSFORMS_MAPGEN = [
    t for t in TRANSFORMS
    if t is not fix_weight
]

# speech: leave volume completely alone ("volume" is loudness, not item size)
_TRANSFORMS_SPEECH = [
    t for t in TRANSFORMS
    if t is not fix_volume
]

# mod_tileset: leave weight untouched (metadata weighting, not item mass)
_TRANSFORMS_MOD_TILESET = [
    t for t in TRANSFORMS
    if t is not fix_weight
]


def _split_top_level_objects(text):
    """
    Yield (start, end) index pairs for every top-level JSON object { ... }
    found in *text*, ignoring content inside strings.
    """
    depth = 0
    in_str = False
    escape = False
    start = None
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_str:
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                yield start, i + 1
                start = None


def update_json_content(content):
    """
    Apply all transformations to a string of JSON content.

    Per-type special rules
    ----------------------
    "mapgen"  : "weight" is left completely untouched.
    "speech"  : "volume" is left completely untouched.
    "mod_tileset": "weight" is left completely untouched.
    "fg" arrays: nested numeric "weight" entries are left untouched.
    "gun_data" objects: string "ammo" entries are left untouched.
    "monsters" arrays: nested numeric "weight" entries are left untouched.
    "mapgen" arrays: nested numeric "weight" entries are left untouched.
    "relative" objects: numeric "price"/"price_postapoc"/"weight" are untouched.
    "variants" arrays: nested numeric "weight" entries are left untouched.
    "phases" arrays: nested numeric "weight" entries are left untouched.
    "price_rules" arrays: numeric "price"/"price_postapoc" are untouched.
    "companion_skill_practice" arrays: nested numeric "weight" are untouched.
    "search_data" arrays: "material" entries are untouched.
    all types : nothing inside a "proportional": { ... } block is touched.
    """
    # ------------------------------------------------------------------
    # Step 1: mask every "proportional": { ... } block so that none of
    # the regex transforms can accidentally modify values inside them.
    # ------------------------------------------------------------------
    content, prop_originals = _mask_proportional(content)
    content, fg_weight_originals = _mask_fg_weights(content)
    content, gun_data_ammo_originals = _mask_gun_data_ammo(content)
    content, monsters_weight_originals = _mask_monsters_weights(content)
    content, mapgen_weight_originals = _mask_mapgen_weights(content)
    content, relative_originals = _mask_relative_price_weight(content)
    content, variants_weight_originals = _mask_variants_weights(content)
    content, phases_weight_originals = _mask_phases_weights(content)
    content, price_rules_originals = _mask_price_rules_prices(content)
    content, companion_skill_practice_originals = _mask_companion_skill_practice_weights(content)
    content, search_data_material_originals = _mask_search_data_material(content)

    # ------------------------------------------------------------------
    # Step 2: split into individual top-level objects and apply the
    # correct per-type pipeline to each one.
    # ------------------------------------------------------------------
    spans = list(_split_top_level_objects(content))
    if not spans:
        # File is not a JSON array of objects (e.g. a bare object or
        # non-standard structure) — fall back to the full pipeline.
        for transform in TRANSFORMS:
            content = transform(content)
    else:
        result = []
        prev_end = 0
        for start, end in spans:
            # Preserve whitespace / punctuation between objects verbatim.
            result.append(content[prev_end:start])
            chunk = content[start:end]
            if re.search(r'"type"\s*:\s*"mapgen"', chunk):
                pipeline = _TRANSFORMS_MAPGEN
            elif re.search(r'"type"\s*:\s*"speech"', chunk):
                pipeline = _TRANSFORMS_SPEECH
            elif re.search(r'"type"\s*:\s*"mod_tileset"', chunk):
                pipeline = _TRANSFORMS_MOD_TILESET
            else:
                pipeline = TRANSFORMS
            for transform in pipeline:
                chunk = transform(chunk)
            result.append(chunk)
            prev_end = end
        result.append(content[prev_end:])
        content = ''.join(result)

    # ------------------------------------------------------------------
    # Step 3: restore the original proportional blocks.
    # ------------------------------------------------------------------
    content = _restore_search_data_material(content, search_data_material_originals)
    content = _restore_companion_skill_practice_weights(content, companion_skill_practice_originals)
    content = _restore_price_rules_prices(content, price_rules_originals)
    content = _restore_phases_weights(content, phases_weight_originals)
    content = _restore_variants_weights(content, variants_weight_originals)
    content = _restore_relative_price_weight(content, relative_originals)
    content = _restore_mapgen_weights(content, mapgen_weight_originals)
    content = _restore_monsters_weights(content, monsters_weight_originals)
    content = _restore_gun_data_ammo(content, gun_data_ammo_originals)
    content = _restore_fg_weights(content, fg_weight_originals)
    content = _restore_proportional(content, prop_originals)
    return content


# ---------------------------------------------------------------------------
# File / directory processing
# ---------------------------------------------------------------------------

def process_file(filepath, dry_run=False):
    """
    Process a single JSON file.
    Returns one of: 'updated', 'unchanged', 'error'
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            original = fh.read()
    except Exception as exc:
        print(f"  [ERROR] Could not read {filepath}: {exc}", file=sys.stderr)
        return 'error'

    updated = update_json_content(original)

    if updated == original:
        return 'unchanged'

    if dry_run:
        print(f"  [DRY-RUN] Would update: {filepath}")
        return 'updated'

    try:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(updated)
        print(f"  [UPDATED] {filepath}")
        return 'updated'
    except Exception as exc:
        print(f"  [ERROR] Could not write {filepath}: {exc}", file=sys.stderr)
        return 'error'


def process_path(path, dry_run=False):
    """
    Process a single file or recursively walk a directory tree.
    Prints a summary of results when finished.
    """
    if os.path.isfile(path):
        if not path.lower().endswith('.json'):
            print(f"  [SKIP] Not a JSON file: {path}", file=sys.stderr)
            return
        process_file(path, dry_run=dry_run)

    elif os.path.isdir(path):
        counts = {'updated': 0, 'unchanged': 0, 'error': 0, 'total': 0}

        for root, dirs, files in os.walk(path):
            # Sort dirs in-place so os.walk visits sub-folders alphabetically
            dirs.sort()
            for fname in sorted(files):
                if not fname.lower().endswith('.json'):
                    continue
                filepath = os.path.join(root, fname)
                result = process_file(filepath, dry_run=dry_run)
                counts['total'] += 1
                counts[result] += 1

        label = "DRY-RUN" if dry_run else "DONE"
        print(
            f"\n[{label}] '{path}' — "
            f"{counts['total']} file(s) scanned: "
            f"{counts['updated']} updated, "
            f"{counts['unchanged']} unchanged, "
            f"{counts['error']} error(s)."
        )

    else:
        print(f"[ERROR] Path not found: {path}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Update legacy Cataclysm: DDA JSON files to the modern format.\n"
            "Accepts one or more .json files and/or directories (scanned recursively).\n"
            "Files are modified in-place unless --dry-run is specified."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'paths',
        nargs='+',
        metavar='PATH',
        help='One or more .json files or directories to process.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview which files would be changed without writing anything.',
    )
    args = parser.parse_args()

    mode = "DRY-RUN" if args.dry_run else "UPDATE"
    print(f"=== CDDA Legacy JSON Updater [{mode}] ===")
    for path in args.paths:
        process_path(path, dry_run=args.dry_run)
    print("Done.")


if __name__ == '__main__':
    main()
