#!/usr/bin/env python3
"""
CDDA JSON translator - in-place, no backups, old + new JSON name support.

Translates human-readable JSON strings to English while avoiding IDs/data fields.
Works with:
  - Old style: "name": "...", "name_plural": "..."
  - New style: "name": { "str": "...", "str_pl": "..." }
  - Common CDDA message fields: "description", "msg", "not_ready_msg", etc.

Input methods:
  - Drag a folder onto the script/shortcut
  - Drag multiple JSON files onto the script/shortcut
  - Run without paths to open a Windows folder picker
  - Use -i / --input paths

No .bak backups are created.
No translated copy/folder is created.
Original JSON files are overwritten only if translated text changes.

Dependency:
  py -m pip install deep-translator
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    from deep_translator import GoogleTranslator
except Exception:  # pragma: no cover
    GoogleTranslator = None  # type: ignore


DEFAULT_TEXT_KEYS: Set[str] = {
    # Core item/monster/terrain/furniture text
    "name",
    "name_plural",  # old CDDA/mod style: do not forget this one
    "description",
    "snippet",
    "text",
    "title",
    "label",
    "menu_text",
    "menu_name",
    "option",

    # New-style translation/name objects
    "str",
    "str_pl",
    "str_sp",

    # Use action / activity / transform / iuse messages
    "msg",
    "message",
    "messages",
    "not_ready_msg",
    "done_message",
    "fail_message",
    "failure_message",
    "success_message",
    "activate_msg",
    "deactivate_msg",
    "out_of_power_msg",
    "need_charges_msg",
    "no_charges_msg",
    "need_fire_msg",
    "no_ammo_msg",
    "no_deactivate_msg",
    "description_frequency",

    # Sound/user-facing messages
    "sound",
    "sound_fail",
    "sound_msg",
    "sound_description",

    # Dialogue / EOC / NPC text
    "dynamic_line",
    "u_message",
    "npc_message",
    "u_buy_monster",
    "npc_buy_monster",
    "yes",
    "no",
    "topic_item",
    "effect_description",

    # Books / martial arts / missions / professions / mutation-style descriptions
    "book_learned_message",
    "learned_message",
    "start_name",
    "goal",
    "difficulty",
    "urgent",
    "dialogue",
}

# Keys whose nested string values should be considered human text if the whole
# value is a dict/list. This helps with dialogue and snippets.
DEFAULT_TEXT_CONTAINERS: Set[str] = {
    "description",
    "message",
    "messages",
    "dynamic_line",
    "snippets",
    "responses",
    "dialogue",
    "text",
}

# Never translate these unless the user explicitly passes --aggressive and even
# then only strings with obvious non-English characters are considered.
PROTECTED_KEYS: Set[str] = {
    "id",
    "copy-from",
    "abstract",
    "type",
    "subtype",
    "category",
    "symbol",
    "color",
    "looks_like",
    "material",
    "material_id",
    "phase",
    "container",
    "ammo",
    "skill_used",
    "skills_required",
    "using",
    "qualities",
    "components",
    "tools",
    "charges",
    "charges_per_use",
    "flags",
    "item",
    "items",
    "group",
    "groups",
    "target",
    "result",
    "result_eocs",
    "effect",
    "effect_on_conditions",
    "eoc",
    "condition",
    "techniques",
    "valid_mod_locations",
    "repo_id",
    "mod_tileset",
    "ascii_picture",
    "path",
    "file",
    "folder",
    "extend",
    "delete",
    "proportional",
    "entries",
    "mapgen",
    "terrain",
    "furniture",
    "vehicle",
    "vehicle_part",
    "transform_age",
    "moves",
    "weight",
    "volume",
    "price",
    "price_postapoc",
    "count",
    "amount",
    "minamount",
}

# New-style name object keys that are actual displayed text. Do not include
# "ctxt" here; that is context, not the displayed name.
NAME_OBJECT_TEXT_KEYS: Set[str] = {"str", "str_pl", "str_sp", "name_plural"}

IDENTIFIER_LIKE = re.compile(r"^[A-Za-z0-9_./:+#@-]+$")
NON_ASCII = re.compile(r"[^\x00-\x7F]")


@dataclass
class Stats:
    files_found: int = 0
    files_updated: int = 0
    files_unchanged: int = 0
    files_failed: int = 0
    strings_attempted: int = 0
    strings_changed: int = 0
    parse_fallbacks: int = 0
    errors: List[str] = field(default_factory=list)


class TranslatorCache:
    def __init__(self, source: str = "auto", target: str = "en", sleep: float = 0.0, verbose: bool = False):
        if GoogleTranslator is None:
            raise RuntimeError(
                "Missing dependency: deep-translator. Install it with:\n"
                "  py -m pip install deep-translator"
            )
        self.source = source
        self.target = target
        self.sleep = max(0.0, sleep)
        self.verbose = verbose
        self.cache: Dict[str, str] = {}
        self.translator = GoogleTranslator(source=source, target=target)

    def translate(self, text: str) -> Tuple[str, bool]:
        original = text
        if not should_try_translate(original):
            return original, False
        if original in self.cache:
            translated = self.cache[original]
            return translated, translated != original
        try:
            translated = self.translator.translate(original)
            if translated is None:
                translated = original
            translated = str(translated)
            self.cache[original] = translated
            if self.sleep:
                time.sleep(self.sleep)
            if self.verbose and translated != original:
                print(f"    {original!r} -> {translated!r}")
            return translated, translated != original
        except Exception as exc:
            if self.verbose:
                print(f"    TRANSLATE FAILED: {original!r}: {exc}")
            return original, False


def should_try_translate(value: str) -> bool:
    """Return True for strings worth sending to the translator."""
    if not isinstance(value, str):
        return False
    s = value.strip()
    if not s:
        return False
    # Avoid URLs and obvious technical strings.
    if s.startswith(("http://", "https://", "//")):
        return False
    if len(s) <= 1 and s.isascii():
        return False
    return True


def looks_like_identifier(value: str) -> bool:
    s = value.strip()
    if not s:
        return True
    if IDENTIFIER_LIKE.match(s) and not any(ch.isspace() for ch in s):
        return True
    return False


def translate_any_string(value: str, translator: TranslatorCache, stats: Stats, aggressive: bool = False) -> str:
    if not should_try_translate(value):
        return value
    if aggressive:
        # In aggressive mode, still avoid plain technical ASCII IDs.
        if looks_like_identifier(value) and not NON_ASCII.search(value):
            return value
    stats.strings_attempted += 1
    translated, changed = translator.translate(value)
    if changed:
        stats.strings_changed += 1
    return translated


def translate_tree(
    value: Any,
    translator: TranslatorCache,
    stats: Stats,
    text_keys: Set[str],
    text_containers: Set[str],
    aggressive: bool = False,
    current_key: Optional[str] = None,
    parent_key: Optional[str] = None,
    under_text_container: bool = False,
) -> Any:
    """Translate selected human-readable values in parsed JSON data."""
    key_l = current_key.lower() if isinstance(current_key, str) else None
    parent_l = parent_key.lower() if isinstance(parent_key, str) else None

    # New-style name object: "name": { "str": "...", "str_pl": "..." }
    if isinstance(value, dict):
        out: Dict[Any, Any] = {}
        for k, v in value.items():
            k_l = k.lower() if isinstance(k, str) else k

            # For a name object, only translate displayed text members.
            if key_l == "name" and isinstance(k_l, str):
                if k_l in NAME_OBJECT_TEXT_KEYS:
                    out[k] = translate_tree(
                        v, translator, stats, text_keys, text_containers,
                        aggressive=False, current_key=k_l, parent_key=key_l,
                        under_text_container=True,
                    )
                else:
                    out[k] = v
                continue

            # Old style or direct fields: "name": "...", "name_plural": "...", "msg": "..."
            if isinstance(k_l, str) and k_l in text_keys:
                if isinstance(v, str):
                    out[k] = translate_any_string(v, translator, stats, aggressive=False)
                elif isinstance(v, (dict, list)):
                    out[k] = translate_tree(
                        v, translator, stats, text_keys, text_containers,
                        aggressive=False, current_key=k_l, parent_key=key_l,
                        under_text_container=(k_l in text_containers),
                    )
                else:
                    out[k] = v
                continue

            # If we are inside a user-facing text container, translate nested strings
            # unless they are known technical keys.
            if under_text_container and isinstance(k_l, str) and k_l not in PROTECTED_KEYS:
                out[k] = translate_tree(
                    v, translator, stats, text_keys, text_containers,
                    aggressive=False, current_key=k_l, parent_key=key_l,
                    under_text_container=True,
                )
                continue

            # Aggressive fallback inside parsed JSON: translate non-ASCII strings that
            # do not belong to protected keys. This helps custom mods with custom text
            # keys, but keeps IDs mostly safe.
            if aggressive and isinstance(k_l, str) and k_l not in PROTECTED_KEYS:
                out[k] = translate_tree(
                    v, translator, stats, text_keys, text_containers,
                    aggressive=True, current_key=k_l, parent_key=key_l,
                    under_text_container=False,
                )
                continue

            # Normal descent so nested use_action/msg fields still get found.
            out[k] = translate_tree(
                v, translator, stats, text_keys, text_containers,
                aggressive=aggressive, current_key=k_l if isinstance(k_l, str) else None,
                parent_key=key_l, under_text_container=False,
            )
        return out

    if isinstance(value, list):
        return [
            translate_tree(
                item, translator, stats, text_keys, text_containers,
                aggressive=aggressive, current_key=current_key,
                parent_key=parent_key,
                under_text_container=under_text_container,
            )
            for item in value
        ]

    if isinstance(value, str):
        if under_text_container:
            return translate_any_string(value, translator, stats, aggressive=False)
        if aggressive and key_l not in PROTECTED_KEYS:
            # Only translate in aggressive mode if it looks like actual language.
            if NON_ASCII.search(value) or not looks_like_identifier(value):
                return translate_any_string(value, translator, stats, aggressive=True)
        return value

    return value


_STRING_LITERAL = r'"(?:\\.|[^"\\])*"'


def json_load_string_literal(lit: str) -> str:
    try:
        return json.loads(lit)
    except Exception:
        # Very defensive fallback; should rarely happen.
        return lit[1:-1]


def json_dump_string_literal(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def fallback_regex_translate(
    text: str,
    translator: TranslatorCache,
    stats: Stats,
    text_keys: Set[str],
    aggressive: bool = False,
) -> str:
    """Best-effort translation for JSON-ish files that json.loads cannot parse.

    This preserves formatting and comments, but is less smart than parsed JSON mode.
    """
    stats.parse_fallbacks += 1
    text_key_pattern = "|".join(re.escape(k) for k in sorted(text_keys, key=len, reverse=True))

    # Direct old/common form: "name": "...", "name_plural": "...", "msg": "..."
    direct_pattern = re.compile(
        rf'(?P<prefix>"(?P<key>{text_key_pattern})"\s*:\s*)(?P<val>{_STRING_LITERAL})',
        re.IGNORECASE,
    )

    def direct_repl(m: re.Match[str]) -> str:
        key = m.group("key").lower()
        raw_val = m.group("val")
        value = json_load_string_literal(raw_val)
        # Do not translate standalone str/str_pl unless handled inside a name object below.
        if key in {"str", "str_pl", "str_sp"}:
            return m.group(0)
        translated = translate_any_string(value, translator, stats, aggressive=False)
        return m.group("prefix") + json_dump_string_literal(translated)

    out = direct_pattern.sub(direct_repl, text)

    # New name object form: "name": { "str": "...", "str_pl": "..." }
    # The object is normally shallow, so this intentionally handles shallow objects.
    name_obj_pattern = re.compile(
        rf'(?P<prefix>"name"\s*:\s*\{{)(?P<body>[^{{}}]*)(?P<suffix>\}})',
        re.IGNORECASE | re.DOTALL,
    )
    inner_key_pattern = "|".join(re.escape(k) for k in sorted(NAME_OBJECT_TEXT_KEYS, key=len, reverse=True))
    inner_pattern = re.compile(
        rf'(?P<prefix>"(?P<key>{inner_key_pattern})"\s*:\s*)(?P<val>{_STRING_LITERAL})',
        re.IGNORECASE,
    )

    def name_obj_repl(m: re.Match[str]) -> str:
        body = m.group("body")

        def inner_repl(im: re.Match[str]) -> str:
            value = json_load_string_literal(im.group("val"))
            translated = translate_any_string(value, translator, stats, aggressive=False)
            return im.group("prefix") + json_dump_string_literal(translated)

        return m.group("prefix") + inner_pattern.sub(inner_repl, body) + m.group("suffix")

    out = name_obj_pattern.sub(name_obj_repl, out)

    if aggressive:
        # Last resort: translate non-ASCII values for keys that are not protected.
        any_prop = re.compile(
            rf'(?P<prefix>"(?P<key>[^"]+)"\s*:\s*)(?P<val>{_STRING_LITERAL})',
            re.IGNORECASE,
        )

        def aggressive_repl(m: re.Match[str]) -> str:
            key = m.group("key").lower()
            if key in PROTECTED_KEYS:
                return m.group(0)
            value = json_load_string_literal(m.group("val"))
            if not NON_ASCII.search(value):
                return m.group(0)
            if looks_like_identifier(value):
                return m.group(0)
            translated = translate_any_string(value, translator, stats, aggressive=True)
            return m.group("prefix") + json_dump_string_literal(translated)

        out = any_prop.sub(aggressive_repl, out)

    return out


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp932", "shift_jis", "gb18030", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")


def process_file(
    path: Path,
    translator: TranslatorCache,
    stats: Stats,
    text_keys: Set[str],
    text_containers: Set[str],
    aggressive: bool = False,
    preserve_format: bool = False,
) -> bool:
    original = read_text(path)
    before_changed = stats.strings_changed

    if preserve_format:
        new_text = fallback_regex_translate(original, translator, stats, text_keys, aggressive=aggressive)
    else:
        try:
            data = json.loads(original)
            new_data = translate_tree(
                data, translator, stats, text_keys, text_containers,
                aggressive=aggressive,
            )
            # Keep readable CDDA-like formatting. ensure_ascii=False keeps translated
            # English readable and preserves any still-untranslated Unicode.
            new_text = json.dumps(new_data, ensure_ascii=False, indent=2)
            new_text += "\n"
        except Exception as exc:
            print(f"  JSON parse failed, using text fallback: {exc}")
            new_text = fallback_regex_translate(original, translator, stats, text_keys, aggressive=aggressive)

    if new_text != original and stats.strings_changed > before_changed:
        write_text(path, new_text)
        return True
    return False


def collect_json_files(paths: Sequence[Path], recursive: bool = True) -> List[Path]:
    found: List[Path] = []
    for p in paths:
        try:
            p = p.expanduser().resolve()
        except Exception:
            p = Path(str(p).strip('"')).expanduser().resolve()
        if p.is_file() and p.suffix.lower() == ".json":
            found.append(p)
        elif p.is_dir():
            pattern = "**/*.json" if recursive else "*.json"
            found.extend(sorted(p.glob(pattern)))
        else:
            print(f"Skipping missing/non-json path: {p}")
    # Deduplicate while preserving order.
    seen: Set[Path] = set()
    unique: List[Path] = []
    for f in found:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def pick_folder() -> Optional[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.update()
        selected = filedialog.askdirectory(title="Choose mod folder to translate JSON in-place")
        root.destroy()
        if selected:
            return Path(selected)
    except Exception as exc:
        print(f"Folder picker failed: {exc}")
    return None


def pick_files() -> List[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.update()
        selected = filedialog.askopenfilenames(
            title="Choose JSON files to translate in-place",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        root.destroy()
        return [Path(x) for x in selected]
    except Exception as exc:
        print(f"File picker failed: {exc}")
    return []


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate CDDA JSON human-readable text to English in-place. No backups, no output folder.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("paths", nargs="*", help="JSON files or folders. Drag/drop paths work here.")
    parser.add_argument("-i", "--input", nargs="+", help="JSON files or folders to process.")
    parser.add_argument("--file-picker", action="store_true", help="Open a JSON file picker instead of folder picker.")
    parser.add_argument("--no-recursive", action="store_true", help="Do not recursively scan folders.")
    parser.add_argument("--source", default="auto", help="Source language for GoogleTranslator. Use auto for any language.")
    parser.add_argument("--target", default="en", help="Target language. English is en.")
    parser.add_argument("--extra-keys", nargs="*", default=[], help="Extra JSON keys to translate as human text.")
    parser.add_argument("--aggressive", action="store_true", help="Translate extra non-ASCII custom string values. Safer than full translate-all, but still riskier.")
    parser.add_argument("--preserve-format", action="store_true", help="Use regex mode to preserve formatting. Good for JSON with comments, less smart for nested structures.")
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to wait between translation requests.")
    parser.add_argument("--verbose", action="store_true", help="Print each changed string.")
    parser.add_argument("--pause", action="store_true", help="Pause before closing, useful for shortcuts.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)

    paths: List[Path] = []
    if args.input:
        paths.extend(Path(p.strip('"')) for p in args.input)
    if args.paths:
        paths.extend(Path(p.strip('"')) for p in args.paths)

    if not paths:
        if args.file_picker:
            paths = pick_files()
        else:
            folder = pick_folder()
            if folder:
                paths = [folder]

    if not paths:
        print("No folder or JSON files selected.")
        return 2

    text_keys = {k.lower() for k in DEFAULT_TEXT_KEYS}
    text_keys.update(k.lower() for k in args.extra_keys)
    text_containers = {k.lower() for k in DEFAULT_TEXT_CONTAINERS}
    text_containers.update(k.lower() for k in args.extra_keys)

    files = collect_json_files(paths, recursive=not args.no_recursive)
    stats = Stats(files_found=len(files))

    print("CDDA JSON translate in-place v11")
    print("No backups. No output copy. Original files are overwritten only if text changes.")
    print(f"Source: {args.source}  Target: {args.target}")
    print(f"JSON files found: {len(files)}")
    if not files:
        return 1

    try:
        translator = TranslatorCache(source=args.source, target=args.target, sleep=args.sleep, verbose=args.verbose)
    except Exception as exc:
        print(str(exc))
        return 3

    for index, path in enumerate(files, 1):
        print(f"[{index}/{len(files)}] {path}")
        before = stats.strings_changed
        try:
            updated = process_file(
                path,
                translator,
                stats,
                text_keys=text_keys,
                text_containers=text_containers,
                aggressive=args.aggressive,
                preserve_format=args.preserve_format,
            )
            changed_here = stats.strings_changed - before
            if updated:
                stats.files_updated += 1
                print(f"  UPDATED - strings changed: {changed_here}")
            else:
                stats.files_unchanged += 1
                print(f"  no change - strings changed: {changed_here}")
        except KeyboardInterrupt:
            print("Stopped by user.")
            return 130
        except Exception as exc:
            stats.files_failed += 1
            message = f"FAILED {path}: {exc}"
            stats.errors.append(message)
            print(f"  {message}")

    print("\nDone.")
    print(f"Files found:      {stats.files_found}")
    print(f"Files updated:    {stats.files_updated}")
    print(f"Files unchanged:  {stats.files_unchanged}")
    print(f"Files failed:     {stats.files_failed}")
    print(f"Strings attempted:{stats.strings_attempted}")
    print(f"Strings changed:  {stats.strings_changed}")
    print(f"Regex fallbacks:  {stats.parse_fallbacks}")

    if stats.errors:
        print("\nErrors:")
        for err in stats.errors[:20]:
            print("  " + err)
        if len(stats.errors) > 20:
            print(f"  ... plus {len(stats.errors) - 20} more")

    if args.pause:
        input("\nPress Enter to close...")

    return 0 if stats.files_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
