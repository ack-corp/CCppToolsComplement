from __future__ import annotations

from regexTools.common import (
    CLASS_IMP_RE,
    FUNCTION_IMP_RE,
    STRUCT_BLOCK_START_RE,
    extract_macro_names,
    extract_matches,
    extract_multiline_statements,
)
from regexTools.getProto import get_typedef_proto


def get_c_function_imp(text: str | None) -> list[str]:
    return extract_matches(text, FUNCTION_IMP_RE)


def get_cpp_function_imp(text: str | None) -> list[str]:
    return extract_matches(text, FUNCTION_IMP_RE)


def get_cpp_class_imp(text: str | None) -> list[str]:
    return extract_matches(text, CLASS_IMP_RE)


def get_macro_imp(text: str | None) -> list[str]:
    return extract_macro_names(text)


def get_struct_imp(text: str | None) -> list[str]:
    return extract_multiline_statements(text, STRUCT_BLOCK_START_RE)


def get_typedef_imp(text: str | None) -> list[str]:
    return get_typedef_proto(text)
