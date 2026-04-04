from __future__ import annotations
import re
from Classes.recurrence import Recurrence
from Classes.resolved_proto import ResolvedProto
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath
from getSourceProto import (
    get_c_function_imp,
    get_c_function_proto,
    get_cpp_class_proto,
    get_cpp_class_imp,
    get_cpp_function_imp,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_forward_decl,
    get_struct_imp,
    get_typedef_proto,
)


def extract_name(statement: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(statement)
    if match is None:
        return None
    return match.group(1)


def extract_symbol_name(
    statement: str,
    primary_pattern: re.Pattern[str],
    fallback_pattern: re.Pattern[str] | None = None,
) -> str | None:
    symbol_name = extract_name(statement, primary_pattern)
    if symbol_name is not None or fallback_pattern is None:
        return symbol_name
    return extract_name(statement, fallback_pattern)


def _count_matches(file_text: str, pattern: re.Pattern[str] | None) -> int:
    if pattern is None:
        return 0
    return len(pattern.findall(file_text))


def _remove_statements_from_text(file_text: str, statements: list[str]) -> str:
    updated_text = file_text
    for statement in statements:
        if not statement:
            continue
        updated_text = updated_text.replace(statement, "")
    return updated_text


def _strip_non_usage_statements(file_text: str) -> str:
    non_usage_statements = list(
        dict.fromkeys(
            get_c_function_proto(file_text)
            + get_cpp_function_proto(file_text)
            + get_c_function_imp(file_text)
            + get_cpp_function_imp(file_text)
            + get_cpp_class_proto(file_text)
            + get_struct_forward_decl(file_text)
            + get_struct_imp(file_text)
            + get_typedef_proto(file_text)
            + get_cpp_class_imp(file_text)
            + get_macro_proto(file_text)
        )
    )
    return _remove_statements_from_text(file_text, non_usage_statements)


def _proto_type_and_name(proto: str) -> tuple[str | None, str | None]:
    for proto_type, _, symbol_pattern, fallback_symbol_pattern in ResolvedProto.iter_proto_groups(ResolvedProto()):
        symbol_name = extract_symbol_name(proto, symbol_pattern, fallback_symbol_pattern)
        if symbol_name is not None:
            return proto_type, symbol_name
    return None, None


def _usage_pattern_for_proto(proto_type: str | None, symbol_name: str | None) -> re.Pattern[str] | None:
    if not proto_type or not symbol_name:
        return None

    escaped_symbol_name = re.escape(symbol_name)
    if proto_type in {"function", "macro"}:
        return re.compile(rf"\b{escaped_symbol_name}\b\s*(?=\()")
    return re.compile(rf"\b{escaped_symbol_name}\b")


def build_recurence(
    proto: str,
    source_texts_by_path: SourceTextsByPath,
) -> Recurrence:
    proto_type, symbol_name = _proto_type_and_name(proto)
    usage_pattern = _usage_pattern_for_proto(proto_type, symbol_name)
    recurence: Recurrence = {}
    for source_path, source_text in source_texts_by_path.items():
        usage_text = _strip_non_usage_statements(source_text)
        times = _count_matches(usage_text, usage_pattern)
        if times > 0:
            recurence[str(source_path)] = recurence.get(str(source_path), 0) + times
    return recurence


def setRecurence(generated_headers: GeneratedHeaders, source_texts_by_path: SourceTextsByPath) -> None:
    for proto, entries in generated_headers.items():
        for entry in entries:
            entry.recurence = build_recurence(proto, source_texts_by_path)
