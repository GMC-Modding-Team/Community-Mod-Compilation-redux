#!/usr/bin/env python3
"""Load a selected slice of a mod's JSON files as a minimal 0.H test mod."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from cdda_h_compat import load_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("modinfo", type=Path)
    parser.add_argument("exe", type=Path)
    parser.add_argument("data", type=Path)
    parser.add_argument("userdir", type=Path)
    parser.add_argument("start", type=int)
    parser.add_argument("stop", type=int)
    parser.add_argument(
        "--indices",
        help="Comma-separated file indices to select instead of the start/stop slice.",
    )
    parser.add_argument(
        "--always",
        help="Comma-separated paths, relative to the mod root, to include with the selection.",
    )
    parser.add_argument(
        "--exclude-prefix",
        help="Comma-separated relative path prefixes to omit from the selected files.",
    )
    parser.add_argument(
        "--always-except-prefix",
        help="Include all files except those under these comma-separated relative path prefixes.",
    )
    parser.add_argument("--entry-file", help="Relative JSON file whose top-level entries should be sliced.")
    parser.add_argument("--entry-start", type=int, default=0)
    parser.add_argument("--entry-stop", type=int)
    parser.add_argument("--drop-fields", help="Comma-separated fields to drop from sliced entries.")
    parser.add_argument("--drop-prefix", help="Relative path prefix whose top-level objects should lose drop-fields.")
    args = parser.parse_args()

    files = sorted(
        path
        for path in args.source.rglob("*.json")
        if path.resolve() != args.modinfo.resolve() and "modinfo" not in path.name.lower()
    )
    if args.indices:
        indices = [int(value) for value in args.indices.split(",") if value.strip()]
        selected = [files[index] for index in indices]
    else:
        selected = files[args.start : args.stop]
    if args.always:
        for value in args.always.split(","):
            path = args.source / value.strip()
            if path not in selected:
                selected.append(path)
    if args.always_except_prefix:
        skipped = tuple(
            value.strip().replace("\\", "/") for value in args.always_except_prefix.split(",")
        )
        for path in files:
            relative = path.relative_to(args.source).as_posix()
            if not relative.startswith(skipped) and path not in selected:
                selected.append(path)
    if args.exclude_prefix:
        prefixes = tuple(value.strip().replace("\\", "/") for value in args.exclude_prefix.split(","))
        selected = [
            path
            for path in selected
            if not path.relative_to(args.source).as_posix().startswith(prefixes)
        ]
    raw_modinfo = load_json(args.modinfo)
    mod_record = raw_modinfo[0] if isinstance(raw_modinfo, list) else raw_modinfo
    mod_record = dict(mod_record)
    mod_record["dependencies"] = ["dda"]

    if args.userdir.exists():
        shutil.rmtree(args.userdir)
    mod_root = args.userdir / "mods" / "isolated_mod"
    (args.userdir / "config").mkdir(parents=True)
    mod_root.mkdir(parents=True)
    (mod_root / "modinfo.json").write_text(
        json.dumps([mod_record], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for source_path in selected:
        destination = mod_root / source_path.relative_to(args.source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        relative_posix = source_path.relative_to(args.source).as_posix()
        is_entry_file = bool(
            args.entry_file and relative_posix == args.entry_file.replace("\\", "/")
        )
        is_drop_file = bool(
            args.drop_prefix and relative_posix.startswith(args.drop_prefix.replace("\\", "/"))
        )
        if is_entry_file or is_drop_file:
            data = load_json(source_path)
            if is_entry_file:
                stop = args.entry_stop if args.entry_stop is not None else len(data)
                entries = data[args.entry_start:stop]
            else:
                entries = data
            if args.drop_fields:
                fields = [value.strip() for value in args.drop_fields.split(",")]
                entries = [
                    {key: value for key, value in entry.items() if key not in fields}
                    if isinstance(entry, dict)
                    else entry
                    for entry in entries
                ]
            destination.write_text(
                json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            shutil.copy2(source_path, destination)

    result = subprocess.run(
        [
            str(args.exe.resolve()),
            "--userdir",
            str(args.userdir.resolve()),
            "--datadir",
            str(args.data.resolve()),
            "--check-mods",
            mod_record["id"],
        ],
        check=False,
    )
    log = args.userdir / "config" / "debug.log"
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    data_marker = str(args.data.resolve()).replace("\\", "/")
    print(
        json.dumps(
            {
                "start": args.start,
                "stop": args.stop,
                "files": len(selected),
                "total_files": len(files),
                "exit": result.returncode,
                "errors": text.count(" ERROR :"),
                "core_json_errors": text.count(f"Json error: {data_marker}"),
                "selected": [str(path.relative_to(args.source)) for path in selected],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
