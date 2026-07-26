#!/usr/bin/env python3
"""Load selected top-level JSON entries as a minimal 0.H test mod."""

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
    parser.add_argument("--drop-fields", default="")
    args = parser.parse_args()

    entries = load_json(args.source)
    if not isinstance(entries, list):
        raise SystemExit("source must contain a top-level array")
    selected = entries[args.start : args.stop]
    drop_fields = {field for field in args.drop_fields.split(",") if field}
    if drop_fields:
        selected = [
            {key: value for key, value in entry.items() if key not in drop_fields}
            if isinstance(entry, dict)
            else entry
            for entry in selected
        ]
    mod_id = load_json(args.modinfo)
    mod_record = mod_id[0] if isinstance(mod_id, list) else mod_id
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
    (mod_root / args.source.name).write_text(
        json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

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
    core_errors = text.count(f"Json error: {data_marker}")
    all_errors = text.count(" ERROR :")
    print(
        json.dumps(
            {
                "start": args.start,
                "stop": args.stop,
                "entries": len(selected),
                "exit": result.returncode,
                "errors": all_errors,
                "core_json_errors": core_errors,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
