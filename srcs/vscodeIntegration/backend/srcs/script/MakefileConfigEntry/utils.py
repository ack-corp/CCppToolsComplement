import json
from typing import Any

from srcs.script.MakefileConfigEntry.CompileProfile import CompileProfile
from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry


def makeEmptyCompileProfile() -> CompileProfile:
    return CompileProfile()


def makeEmptyMakefileConfigEntry() -> MakefileConfigEntry:
    return MakefileConfigEntry()


def parseMakefileConfigEntries(data: Any) -> list[MakefileConfigEntry]:
    if not isinstance(data, list):
        raise ValueError("makefile config must be a JSON array")
    return [MakefileConfigEntry.fromJsonObject(entry_data) for entry_data in data]


def parseMakefileConfigEntriesJson(json_text: str) -> list[MakefileConfigEntry]:
    return parseMakefileConfigEntries(json.loads(json_text))


def makefileConfigEntriesToJsonObject(entries: list[MakefileConfigEntry]) -> list[dict[str, Any]]:
    return [entry.toJsonObject() for entry in entries]


def makefileConfigEntriesToJson(entries: list[MakefileConfigEntry]) -> str:
    return json.dumps(makefileConfigEntriesToJsonObject(entries), indent=2)
