from __future__ import annotations

import os
from pathlib import Path

from Classes.resolved_proto import ResolvedProto
from Classes.traversal_result import TraversalResult
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath
from getResolvedProto import getResolvedProto
from globals import C_SOURCE_EXTENSIONS, CPP_SOURCE_EXTENSIONS
from protoImplementationMatcher import build_proto_map
from utils import is_excluded, normalize_excluded_paths


def merge_header_map(global_header_map: GeneratedHeaders, file_header_map: GeneratedHeaders) -> None:
    for proto_name, entries in file_header_map.items():
        global_header_map.setdefault(proto_name, []).extend(entries)


def process_source_file(
    file_path: Path,
    proto: ResolvedProto,
    source_texts: SourceTextsByPath,
    generated_headers: GeneratedHeaders,
) -> None:
    resolved_path = str(file_path.resolve())
    source_text = file_path.read_text(encoding="utf-8", errors="ignore")
    source_texts[resolved_path] = source_text
    file_header_map = build_proto_map(resolved_path, proto, source_text)
    merge_header_map(generated_headers, file_header_map)


def collect_sources(
    start_path: Path,
    excluded_paths: set[Path],
    source_extensions: set[str],
    protos: ResolvedProto,
) -> tuple[SourceTextsByPath, GeneratedHeaders]:
    source_texts: SourceTextsByPath = {}
    generated_headers: GeneratedHeaders = {}

    for current_root, dir_names, file_names in os.walk(start_path):
        current_path = Path(current_root).resolve()
        if is_excluded(current_path, excluded_paths):
            dir_names[:] = []
            continue

        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if not is_excluded(current_path / dir_name, excluded_paths)
        ]

        for file_name in file_names:
            file_path = current_path / file_name
            if file_path.suffix.lower() in source_extensions:
                process_source_file(file_path, protos, source_texts, generated_headers)

    return source_texts, generated_headers


def getTraversalResult(startPath: str, excludedFolderPath: list[str]) -> TraversalResult:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = normalize_excluded_paths(excludedFolderPath)
    source_extensions = C_SOURCE_EXTENSIONS | CPP_SOURCE_EXTENSIONS
    protos = getResolvedProto(startPath, source_extensions, excludedFolderPath)
    source_texts_by_path, generated_headers = collect_sources(
        start_path,
        excluded_paths,
        source_extensions,
        protos,
    )
    return TraversalResult(
        proto=protos,
        generated_headers=generated_headers,
        source_texts_by_path=source_texts_by_path,
    )
