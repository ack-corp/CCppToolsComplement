#!/usr/bin/env python3
from pathlib import Path
from typing import Any

from models.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from models.MakefileConfigEntry.utils import readEntries
from models.type import JsonItems, JsonObject
from helper.utils import readJsonObject, writeJsonObject
from jsonMakefileConfig.verify import verifyJson
from models.Makefile.Makefile import Makefile

TASKS_REL_PATH = Path(".vscode/tasks.json")


def mergeByKey(existing: JsonItems, generated: JsonItems, key: str) -> JsonItems:
    seen: set[Any] = set()
    duplicates: set[Any] = set()
    merged: JsonItems = []
    for item in generated:
        item_key = item.get(key)
        if item_key in seen:
            duplicates.add(item_key)
            continue
        seen.add(item_key)
        merged.append(item)
    for item in existing:
        item_key = item.get(key)
        if item_key in seen:
            duplicates.add(item_key)
            continue
        seen.add(item_key)
        merged.append(item)
    for item_key in duplicates:
        print(f"Multiple items with key {item_key!r}; kept the first occurrence.")
    return merged


def vscodePathForFsPath(path: Path, workspace: Path) -> str:
    rel = path.relative_to(workspace).as_posix()
    if rel == ".":
        return "${workspaceFolder}"
    return f"${{workspaceFolder}}/{rel}"


def getProgramName(entry: MakefileConfigEntry) -> str:
    output_makefile = Path(entry.output_makefile)
    program_name = Makefile.getProgramNameFromMakefileName(output_makefile)
    if not program_name:
        raise ValueError(f"Invalid output_makefile for entry: {entry.output_makefile!r}")
    return program_name


def makeTask(entry: MakefileConfigEntry, workspace: Path, target: str) -> JsonObject:
    output_makefile = (workspace / entry.output_makefile).resolve()
    program_name = getProgramName(entry)
    label_prefix = "build" if target == "all" else "rebuild"
    return {
        "label": f"{label_prefix} {program_name} (debug)",
        "type": "shell",
        "command": "make",
        "args": ["-f", output_makefile.name, target],
        "options": {"cwd": vscodePathForFsPath(output_makefile.parent, workspace)},
        "problemMatcher": ["$gcc"],
    }


def generateTask() -> None:
    if verifyJson() != 0:
        raise SystemExit("Makefile configuration verification failed.")
    workspace = Path.cwd().resolve()
    tasks_path = (workspace / TASKS_REL_PATH).resolve()
    config_path = (workspace / ".vscode/makefileConfig.json").resolve()
    entries = readEntries(config_path)
    generated_tasks = [
        task
        for entry in entries
        for task in (makeTask(entry, workspace, "all"), makeTask(entry, workspace, "re"))
    ]
    tasks_json = readJsonObject(tasks_path, {"version": "2.0.0", "tasks": []})
    existing_tasks = tasks_json.get("tasks", [])
    if not isinstance(existing_tasks, list):
        existing_tasks = []
    tasks_json["version"] = tasks_json.get("version", "2.0.0")
    tasks_json["tasks"] = mergeByKey(
        [item for item in existing_tasks if isinstance(item, dict)],
        generated_tasks,
        "label",
    )
    writeJsonObject(tasks_path, tasks_json)
    print(f"Generated {tasks_path}")


if __name__ == "__main__":
    generateTask()
