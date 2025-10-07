"""Shared helpers for JSON maintenance scripts.

These helpers provide a tiny abstraction layer that most scripts in
``tools/`` rely on.  The original versions were written with a heavy
dependency on ``os`` and ``subprocess``.  The updated implementation
embraces :mod:`pathlib` for path handling, provides stronger typing, and
improves error reporting while remaining backwards compatible with the
existing scripts.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Iterator, Optional, Protocol, TypeVar


FORMATTER_CANDIDATES = [
    Path("./json_formatter.exe"),
    Path("./tools/format/json_formatter.cgi"),
]


JsonData = TypeVar("JsonData")


class JsonTransformer(Protocol):
    """Callable protocol describing the ``gen_new`` helpers used by scripts."""

    def __call__(self, path: Path) -> Optional[JsonData]:  # pragma: no cover - documentation
        ...


def iter_json_files(root: Path) -> Iterator[Path]:
    """Yield all ``.json`` files contained within ``root``.

    ``root`` may be either a directory or a single JSON file.  ``Path.glob``
    naturally handles recursion with ``rglob`` which keeps the
    implementation compact and easy to reason about.
    """

    if root.is_file():
        if root.suffix.lower() == ".json":
            yield root
        return

    for path in root.rglob("*.json"):
        if path.is_file():
            yield path


def change_file(json_dir: Path | str, gen_new: JsonTransformer) -> None:
    """Rewrite all JSON files in ``json_dir`` using ``gen_new``.

    Parameters
    ----------
    json_dir:
        Directory or file containing JSON documents.
    gen_new:
        Callable that receives the path of the JSON file and returns the
        potentially modified data.  ``None`` indicates that the file was
        left untouched.
    """

    root = Path(json_dir).expanduser().resolve()
    if not root.exists():
        logging.error("Provided path %s does not exist", root)
        return

    for path in iter_json_files(root):
        modify_file(path, gen_new)


def modify_file(path: Path, gen_new: JsonTransformer) -> None:
    """Apply ``gen_new`` to ``path`` and write the result if required."""

    new = gen_new(path)
    if new is None:
        # The average user doesn't care about the files that don't change.
        logging.debug("No change to %s", path)
        return

    logging.info("Modified file %s", path)
    path.write_text(
        json.dumps(new, ensure_ascii=False),
        encoding="utf-8",
    )

    for formatter in FORMATTER_CANDIDATES:
        if formatter.exists():
            subprocess.run([str(formatter), str(path)], check=False)
            break
    else:
        logging.debug("No JSON formatter found; skipping formatting for %s", path)


def load_json(path: Path | str):
    """Handle errors when loading JSON documents.

    The helper prints *and* logs errors so the calling script always
    communicates the problem to users.
    """

    json_path = Path(path)
    try:
        json_text = json_path.read_text(encoding="utf-8")
    except OSError:
        logging.exception("Could not read %s", json_path)
        print(f"Failed to read {json_path}")
        return None

    try:
        return json.loads(json_text)
    except UnicodeDecodeError:
        print(f"UnicodeDecodeError in {json_path}")
        logging.error("UnicodeDecodeError in %s", json_path)
    except json.decoder.JSONDecodeError:
        print(f"JSONDecodeError in {json_path}")
        logging.error("JSONDecodeError in %s", json_path)
    return None

