from __future__ import annotations

import re

from regexTools.common import (
    CLASS_PROTO_RE,
    STRUCT_BLOCK_START_RE,
    STRUCT_FORWARD_DECL_RE,
    TYPEDEF_START_RE,
    USING_PROTO_RE,
    extract_function_statements,
    extract_macro_names,
    extract_matches,
    extract_multiline_statements,
)


def get_c_function_proto(text: str | None) -> list[str]:
    return extract_function_statements(text, ";")


def get_cpp_function_proto(text: str | None) -> list[str]:
    return extract_function_statements(text, ";")


def get_cpp_class_proto(text: str | None) -> list[str]:
    return extract_matches(text, CLASS_PROTO_RE)


def get_macro_proto(text: str | None) -> list[str]:
    return extract_macro_names(text)


def get_struct_forward_decl(text: str | None) -> list[str]:
    return extract_matches(text, STRUCT_FORWARD_DECL_RE)


def get_struct_proto(text: str | None) -> list[str]:
    forward_declarations = get_struct_forward_decl(text)
    struct_blocks = extract_multiline_statements(text, STRUCT_BLOCK_START_RE)
    struct_block_names = {
        match.group(1)
        for struct_block in struct_blocks
        if (match := re.search(r"\bstruct\s+([A-Za-z_]\w*)", struct_block))
    }

    return [
        forward_declaration
        for forward_declaration in forward_declarations
        if re.search(r"\bstruct\s+([A-Za-z_]\w*)", forward_declaration).group(1) not in struct_block_names
    ] + struct_blocks


def get_typedef_proto(text: str | None) -> list[str]:
    typedef_matches = extract_multiline_statements(text, TYPEDEF_START_RE)
    using_matches = extract_matches(text, USING_PROTO_RE)
    return typedef_matches + using_matches
