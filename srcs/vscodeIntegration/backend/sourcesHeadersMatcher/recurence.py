from __future__ import annotations

import re

from Classes.proto_match import ProtoMatch
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath


def usage_pattern_for_proto(proto_type: str | None, symbol_name: str | None) -> re.Pattern[str] | None:
    if not proto_type or not symbol_name:
        return None

    escaped_symbol_name = re.escape(symbol_name)
    if proto_type in {"function", "macro"}:
        return re.compile(rf"\b{escaped_symbol_name}\b\s*(?=\()")
    return re.compile(rf"\b{escaped_symbol_name}\b")


def countProtoUsage(proto_match: ProtoMatch, source_text: str) -> int:
    usage_pattern = usage_pattern_for_proto(proto_match.proto_type, proto_match.symbol_name)
    if usage_pattern is None:
        return 0
    return len(usage_pattern.findall(source_text))


def setRecurence(generated_headers: GeneratedHeaders, source_texts_by_path: SourceTextsByPath) -> None:
    for source_path, source_text in source_texts_by_path.items():
        for proto_matches in generated_headers.values():
            if not proto_matches:
                continue
            recurence = countProtoUsage(proto_matches[0], source_text)
            if recurence > 0:
                for proto_match in proto_matches:
                    proto_match.recurence[source_path] = proto_match.recurence.get(source_path, 0) + recurence
