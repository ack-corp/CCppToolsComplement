from __future__ import annotations

from pathlib import Path

from Classes.GeneratedHeaders import GeneratedHeaders
from Classes.ProtoMatch import ProtoMatch
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS


def header_path_from_source(source_path: str) -> str:
    source = Path(source_path)
    suffix = source.suffix.lower()
    if suffix in HEADER_EXTENSIONS:
        return str(source)
    if suffix == ".c":
        return str(source.with_suffix(".h"))
    if suffix == ".cpp":
        return str(source.with_suffix(".hpp"))
    return str(source.with_suffix(".h"))


def best_recurence_path(entry: ProtoMatch) -> str | None:
    best_score = 0
    best_path: str | None = None
    for key, recurence in entry.recurence.items():
        if recurence >= best_score:
            best_score = recurence
            best_path = key
    return best_path


def set_entry_header_paths(generated_headers: GeneratedHeaders) -> None:
    for entry in generated_headers.values():
        best_path = best_recurence_path(entry)
        if best_path is None:
            best_path = entry.source
        entry.header_path = header_path_from_source(best_path)
