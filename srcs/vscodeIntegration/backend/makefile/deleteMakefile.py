#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

from models.MakefileConfigEntry.utils import getEntryByIndex, readEntries
from makefile.generateMakefile import getProgramsForDirectory, renderParentMakefile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete one makefile from .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Delete the makefile for the entry at this index.",
    )
    return parser.parse_args()


def deleteMakefile(entry_index: int) -> None:
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / ".vscode/makefileConfig.json").resolve()
    entries = readEntries(config_path)
    entry = getEntryByIndex(entries, entry_index)
    output_makefile = (workspace_root / entry.output_makefile).resolve()
    parent_directory = output_makefile.parent

    if output_makefile.exists() and output_makefile.is_file():
        subprocess.run(
            ["make", "-f", output_makefile.name, "fclean"],
            cwd=parent_directory,
            check=True,
        )
        output_makefile.unlink()
        print(f"Deleted {output_makefile}")

    remaining_entries = [candidate for index, candidate in enumerate(entries) if index != entry_index]
    parent_makefile = parent_directory / "Makefile"
    programs = getProgramsForDirectory(remaining_entries, parent_directory, workspace_root)

    if not programs:
        if parent_makefile.exists() and parent_makefile.is_file():
            parent_makefile.unlink()
            print(f"Deleted {parent_makefile}")
        return

    parent_makefile.write_text(renderParentMakefile(programs), encoding="utf-8")
    print(f"Updated parent {parent_makefile}")


if __name__ == "__main__":
    deleteMakefile(parse_args().entry_index)
