#!/usr/bin/env python3
import argparse
import json
import os
import re
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("storage_to_pocket_data.log"),
        logging.StreamHandler()
    ]
)
LOGGER = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Convert legacy 'storage' to modern 'pocket_data' in CDDA JSON.")
    parser.add_argument("paths", nargs="+", help="Files or directories to process.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to files.")
    parser.add_argument("--quiet", action="store_true", help="Only show updated files and errors.")
    parser.add_argument("--formatter", help="Path to json_formatter.cgi (optional).")
    return parser.parse_args()

def get_weight_for_volume(volume_str):
    """
    Estimate a reasonable max_contains_weight based on volume.
    Rule of thumb: 1L ~ 4kg for typical CDDA containers.
    """
    m = re.match(r'(\d+(?:\.\d+)?)\s*(ml|L)', volume_str)
    if not m:
        return "2 kg" # Default fallback
    
    val = float(m.group(1))
    unit = m.group(2)
    
    # Convert to Liters for calculation
    liters = val / 1000.0 if unit == "ml" else val
    
    # 4kg per Liter, minimum 1kg
    weight_kg = max(1.0, round(liters * 4.0, 1))
    
    if weight_kg == int(weight_kg):
        return f"{int(weight_kg)} kg"
    return f"{weight_kg} kg"

def fix_storage(content):
    """
    Find "storage": "X" and replace with "pocket_data": [ ... ]
    """
    # Pattern to find "storage": "..."
    # We capture the leading indentation and the volume string
    pattern = re.compile(r'^(\s*)"storage"\s*:\s*"([^"]+)"', re.MULTILINE)
    
    def replace_storage(match):
        indent = match.group(1)
        volume_str = match.group(2)
        weight_str = get_weight_for_volume(volume_str)
        
        pocket_data = [
            {
                "pocket_type": "CONTAINER",
                "rigid": True,
                "max_contains_volume": volume_str,
                "max_contains_weight": weight_str
            }
        ]
        
        # Convert to JSON string and indent to match the original line
        pd_json = json.dumps(pocket_data, indent=2)
        # Indent every line of the generated JSON
        indented_pd = pd_json.replace('\n', '\n' + indent)
        
        return f'{indent}"pocket_data": {indented_pd}'

    new_content = pattern.sub(replace_storage, content)
    return new_content

def process_file(path, args):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        LOGGER.error(f"Could not read {path}: {e}")
        return "error"

    # Check if "storage" exists before processing
    if '"storage"' not in original_content:
        if not args.quiet:
            print(f"[UNCHANGED] {path}")
        return "unchanged"

    new_content = fix_storage(original_content)

    if new_content == original_content:
        if not args.quiet:
            print(f"[UNCHANGED] {path}")
        return "unchanged"

    if args.dry_run:
        print(f"[DRY-RUN] {path} would be updated.")
        return "updated"

    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Run formatter if provided
        if args.formatter and os.path.exists(args.formatter):
            subprocess.run([args.formatter, path], capture_output=True)
        
        print(f"[UPDATED] {path}")
        return "updated"
    except Exception as e:
        LOGGER.error(f"Could not write {path}: {e}")
        return "error"

def process_path(path, args):
    stats = {"scanned": 0, "updated": 0, "unchanged": 0, "error": 0}
    
    if os.path.isfile(path):
        if path.endswith(".json"):
            stats["scanned"] += 1
            res = process_file(path, args)
            stats[res] += 1
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in sorted(files):
                if file.endswith(".json"):
                    full_path = os.path.join(root, file)
                    stats["scanned"] += 1
                    res = process_file(full_path, args)
                    stats[res] += 1
    
    return stats

def main():
    args = parse_args()
    total_stats = {"scanned": 0, "updated": 0, "unchanged": 0, "error": 0}
    
    print(f"=== CDDA Storage to Pocket Data Converter {'[DRY-RUN]' if args.dry_run else '[UPDATE]'} ===")
    
    for path in args.paths:
        path_stats = process_path(path, args)
        for k in total_stats:
            total_stats[k] += path_stats[k]
            
    print(f"\nDone. {total_stats['scanned']} file(s) scanned: "
          f"{total_stats['updated']} updated, "
          f"{total_stats['unchanged']} unchanged, "
          f"{total_stats['error']} error(s).")

if __name__ == "__main__":
    main()
