#!/usr/bin/env python3
import re
import argparse
import os

def _sub(pattern, repl, text, flags=0):
    return re.sub(pattern, repl, text, flags=flags)

def _merge_into_existing_armor(chunk, updates):
    def _replacer(match):
        opening = match.group(1)
        body = match.group(2)
        closing = match.group(3)

        merged_body = body
        for modern_key, value in updates.items():
            key_pattern = rf'"{modern_key}"\s*:\s*-?\d+'
            replacement = f'"{modern_key}": {value}'

            if re.search(key_pattern, merged_body):
                merged_body = re.sub(key_pattern, replacement, merged_body, count=1)
                continue

            if merged_body.strip():
                stripped = merged_body.rstrip()
                if re.search(r',\s*$', stripped):
                    merged_body = f'{stripped} {replacement}'
                else:
                    merged_body = f'{stripped}, {replacement}'
            else:
                merged_body = f' {replacement} '

        return f"{opening}{merged_body}{closing}"

    return re.sub(r'("armor"\s*:\s*\{)(.*?)(\})', _replacer, chunk, count=1, flags=re.S)

def fix_armor_in_chunk(chunk):
    armor_keys = {
        'armor_bash': 'bash',
        'armor_cut': 'cut',
        'armor_bullet': 'bullet',
        'armor_acid': 'acid',
        'armor_stab': 'stab',
        'armor_fire': 'fire',
    }

    found = {}
    for legacy_key, modern_key in armor_keys.items():
        m = re.search(rf'"{legacy_key}"\s*:\s*(\d+)', chunk)
        if m:
            found[legacy_key] = (modern_key, int(m.group(1)))

    if not found:
        return chunk

    updates = {modern: val for _, (modern, val) in found.items()}

    armor_parts = ', '.join(
        f'"{modern}": {val}' for _, (modern, val) in found.items()
    )
    armor_obj = f'"armor": {{ {armor_parts} }}'

    # remove legacy keys (handle key at beginning, middle, or end)
    for legacy_key in found:
        chunk = _sub(rf'\s*"{legacy_key}"\s*:\s*\d+\s*,', '', chunk)
        chunk = _sub(rf',\s*"{legacy_key}"\s*:\s*\d+', '', chunk)
        chunk = _sub(rf'\s*"{legacy_key}"\s*:\s*\d+', '', chunk)

    if re.search(r'"armor"\s*:\s*\{', chunk):
        return _merge_into_existing_armor(chunk, updates)

    # If an armor key already exists but is not an object, do not create a
    # second "armor" key.
    if re.search(r'"armor"\s*:', chunk):
        return chunk

    # Insert at the bottom of this object (before the final closing brace).
    closing = re.search(r'(\s*\})\s*$', chunk)
    if not closing:
        return chunk

    body = chunk[1:closing.start()].strip()
    separator = ',\n    ' if body else '\n    '
    chunk = (
        chunk[:closing.start()]
        + f'{separator}{armor_obj}'
        + chunk[closing.start():]
    )

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
