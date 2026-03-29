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
  17. "chance": N               -> "prob": N
  18. "price": N                -> "price": "N cent"
  19. "price_postapoc": N       -> "price_postapoc": "N cent"
  20. "min_melee": N            -> skill_requirements entry  (merged with min_unarmed)
  21. "min_unarmed": N          -> skill_requirements entry  (merged with min_melee)
  22. "bashing": N, "cutting": M-> "melee_damage": { "bash": N, "cut": M }
  23. "bash_resist": N, etc.    -> "resist": { "bash": N, ... }
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


def fix_chance(content):
    """
    "chance": N  ->  "prob": N
    """
    return _sub(r'"chance"\s*:\s*(\d+)', r'"prob": \1', content)


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
    fix_chance,
    fix_price,
    fix_skill_requirements,
    fix_melee_damage,
    fix_resist,
]


def update_json_content(content):
    """Apply all transformations to a string of JSON content."""
    for transform in TRANSFORMS:
        content = transform(content)
    return content


# ---------------------------------------------------------------------------
# File / directory processing
# ---------------------------------------------------------------------------

def process_file(filepath, dry_run=False):
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            original = fh.read()
    except Exception as exc:
        print(f"  [ERROR] Could not read {filepath}: {exc}", file=sys.stderr)
        return

    updated = update_json_content(original)

    if updated == original:
        return  # Nothing changed – stay silent

    if dry_run:
        print(f"  [DRY-RUN] Would update: {filepath}")
        return

    try:
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(updated)
        print(f"  [UPDATED] {filepath}")
    except Exception as exc:
        print(f"  [ERROR] Could not write {filepath}: {exc}", file=sys.stderr)


def process_path(path, dry_run=False):
    if os.path.isfile(path):
        process_file(path, dry_run=dry_run)
    elif os.path.isdir(path):
        total = 0
        for root, _dirs, files in os.walk(path):
            for fname in files:
                if fname.lower().endswith('.json'):
                    process_file(os.path.join(root, fname), dry_run=dry_run)
                    total += 1
        print(f"\nScanned {total} JSON file(s) under '{path}'.")
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