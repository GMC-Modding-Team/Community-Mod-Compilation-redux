#!/usr/bin/env python3
import re
import argparse
import os

def _sub(pattern, repl, text, flags=0):
    return re.sub(pattern, repl, text, flags=flags)

def fix_armor_in_chunk(chunk):
    armor_keys = {
        'armor_bash': 'bash',
        'armor_cut': 'cut',
        'armor_bullet': 'bullet',
	'armor_stab': 'stab',
        'armor_acid': 'acid',
    }

    found = {}
    for legacy_key, modern_key in armor_keys.items():
        m = re.search(rf'"{legacy_key}"\s*:\s*(\d+)', chunk)
        if m:
            found[legacy_key] = (modern_key, int(m.group(1)))

    if not found:
        return chunk

    armor_parts = ', '.join(
        f'"{modern}": {val}' for _, (modern, val) in found.items()
    )
    armor_obj = f'"armor": {{ {armor_parts} }}'

    # remove keys
    for legacy_key in found:
        chunk = _sub(rf',?\s*"{legacy_key}"\s*:\s*\d+', '', chunk)

    # insert BEFORE final brace of THIS object
    chunk = re.sub(r'(\n\s*\})', f',\n    {armor_obj}\\1', chunk, count=1)

    return chunk

def split_objects(text):
    depth = 0
    start = None
    in_str = False
    escape = False

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
    spans = list(split_objects(content))
    if not spans:
        return content

    result = []
    prev = 0

    for start, end in spans:
        result.append(content[prev:start])
        chunk = content[start:end]
        chunk = fix_armor_in_chunk(chunk)
        result.append(chunk)
        prev = end

    result.append(content[prev:])
    return ''.join(result)

def process_file(filepath, dry_run=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    updated = update_json_content(original)

    if updated == original:
        return

    if dry_run:
        print(f"[DRY-RUN] {filepath}")
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated)

    print(f"[UPDATED] {filepath}")

def process_path(path, dry_run=False):
    if os.path.isfile(path):
        if path.endswith(".json"):
            process_file(path, dry_run)
    else:
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(".json"):
                    process_file(os.path.join(root, f), dry_run)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    process_path(args.path, args.dry_run)

if __name__ == "__main__":
    main()
