"""Run the vehicle reformatter across the entire data set."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path


LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    tools_dir = Path(__file__).resolve().parent
    default_data = tools_dir.parent / "data"
    default_formatter = tools_dir / "format" / "json_formatter.cgi"

    parser = argparse.ArgumentParser(
        description="Reformat all vehicle definitions using vehicle_reformatter.py.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=default_data,
        help="Root directory containing vehicle JSON definitions.",
    )
    parser.add_argument(
        "--formatter",
        type=Path,
        default=default_formatter,
        help="Path to the json_formatter executable.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        type=str.upper,
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Logging verbosity.",
    )
    return parser.parse_args()


def find_vehicle_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("vehicles.json") if path.is_file()]


def run_vehicle_reformatter(vehicle_file: Path, formatter: Path) -> None:
    tools_dir = Path(__file__).resolve().parent
    reformatter = tools_dir / "vehicle_reformatter.py"
    LOGGER.debug("Reformatting %s", vehicle_file)
    subprocess.run([sys.executable, str(reformatter), str(vehicle_file)], check=True)
    if formatter.exists():
        subprocess.run([str(formatter), str(vehicle_file)], check=False)
    else:
        LOGGER.debug("Formatter %s not found; skipping", formatter)


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), force=True)
    data_root = args.data_root.expanduser()
    formatter = args.formatter.expanduser()
    vehicle_files = find_vehicle_files(data_root)
    LOGGER.info("Found %s vehicle definition files", len(vehicle_files))
    for vehicle_file in vehicle_files:
        run_vehicle_reformatter(vehicle_file, formatter)


if __name__ == "__main__":
    main()
