from __future__ import annotations

from pathlib import Path

from Classes.resolved_proto import ResolvedProto
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath
from protoImplementationMatcher import build_proto_map


def _read_source(file_path: str | Path) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def generateHeader(
    filePath: str,
    proto: ResolvedProto,
    source_texts_by_path: SourceTextsByPath | None = None,
) -> GeneratedHeaders:
    source_path = Path(filePath).expanduser().resolve()
    source_text = _read_source(source_path)
    return build_proto_map(source_path, proto, source_text, source_texts_by_path or {})
