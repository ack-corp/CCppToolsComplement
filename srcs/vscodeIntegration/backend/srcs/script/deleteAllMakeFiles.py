#!/usr/bin/env python3
from pathlib import Path

from srcs.script.generateJson import read_config_entries

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def deleteAllMakeFiles() -> None:
    config_path = (Path.cwd() / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    if not entries:
        raise SystemExit(f"No program entries found in {config_path}")

    workspace_root = Path.cwd().resolve()
    deleted_count = 0

    for entry in entries:
        output_makefile = entry.get("output_makefile")
        if not isinstance(output_makefile, str) or not output_makefile.strip():
            continue

        makefile_path = (workspace_root / output_makefile).resolve()
        if not makefile_path.exists() or not makefile_path.is_file():
            continue

        makefile_path.unlink()
        deleted_count += 1
        print(f"Deleted {makefile_path}")

    print(f"Deleted {deleted_count} makefile(s).")


if __name__ == "__main__":
    deleteAllMakeFiles()
