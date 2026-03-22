#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Any

from srcs.script.generateJson import read_config_entries, write_config_entries

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the run_args field of one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Update the entry at this index.",
    )
    parser.add_argument(
        "new_args",
        type=str,
        help="New run arguments string.",
    )
    return parser.parse_args()


def get_entry(entries: list[dict[str, Any]], entry_index: int) -> dict[str, Any]:
    if not entries:
        raise SystemExit("No program entries found in .vscode/makefileConfig.json")
    if entry_index < 0 or entry_index >= len(entries):
        raise SystemExit(f"Entry index {entry_index} is out of range.")
    entry = entries[entry_index]
    if not isinstance(entry, dict):
        raise SystemExit(f"Entry at index {entry_index} is invalid.")
    return entry


def updateRunArgs() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = get_entry(entries, args.entry_index)

    previous_run_args = entry.get("run_args", "")
    entry["run_args"] = args.new_args
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated run_args for entry {args.entry_index}: "
        f"{previous_run_args!r} -> {args.new_args!r}"
    )


if __name__ == "__main__":
    updateRunArgs()
