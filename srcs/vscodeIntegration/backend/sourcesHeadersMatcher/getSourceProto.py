import re


FUNCTION_NAME_RE = r"[A-Za-z_]\w*(?:::\w+)*"
FUNCTION_DECLARATION_NAME_RE = re.compile(rf"({FUNCTION_NAME_RE})\s*\(")
FUNCTION_IMP_RE = re.compile(
    rf"^\s*(?:extern\s+)?[\w:\<\>\~\*&,\s]+?{FUNCTION_NAME_RE}\s*\([^;{{}}]*\)\s*(?:const\s*)?\{{\s*$",
    re.MULTILINE,
)
CLASS_PROTO_RE = re.compile(
    r"^\s*(?:template\s*<[^;{}]+>\s*)?(?:class|struct)\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*;\s*$",
    re.MULTILINE,
)
CLASS_IMP_RE = re.compile(
    r"^\s*(?:template\s*<[^;{}]+>\s*)?(?:class|struct)\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*\{\s*$",
    re.MULTILINE,
)
MACRO_PROTO_RE = re.compile(r"^\s*#\s*define\s+[A-Za-z_]\w*(?:\([^)]*\))?(?:\s+.+)?$", re.MULTILINE)
STRUCT_FORWARD_DECL_RE = re.compile(
    r"^\s*struct\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*;\s*$",
    re.MULTILINE,
)
STRUCT_BLOCK_START_RE = re.compile(
    r"^\s*struct\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*\{",
)
TYPEDEF_START_RE = re.compile(r"^\s*typedef\b")
USING_PROTO_RE = re.compile(r"^\s*using\s+[A-Za-z_]\w*\s*=\s*.+;\s*$", re.MULTILINE)


def _extract_matches(text, pattern):
    if text is None:
        return []

    matches = pattern.findall(text.strip())
    if not matches:
        return []

    normalized_matches = []
    for match in matches:
        if isinstance(match, tuple):
            normalized_match = "".join(match)
        else:
            normalized_match = match
        normalized_matches.append(normalized_match.strip())

    return normalized_matches


def _extract_macro_names(text):
    return _extract_matches(text, MACRO_PROTO_RE)


def _extract_multiline_statements(text, start_pattern):
    if text is None:
        return []

    statements = []
    lines = text.splitlines()
    line_index = 0

    while line_index < len(lines):
        raw_line = lines[line_index]
        if start_pattern.match(raw_line.strip()) is None:
            line_index += 1
            continue

        statement_lines = [raw_line.rstrip()]
        brace_depth = raw_line.count("{") - raw_line.count("}")

        while True:
            stripped_line = statement_lines[-1].strip()
            if brace_depth <= 0 and stripped_line.endswith(";"):
                break

            line_index += 1
            if line_index >= len(lines):
                break

            next_line = lines[line_index]
            statement_lines.append(next_line.rstrip())
            brace_depth += next_line.count("{") - next_line.count("}")

        statement = "\n".join(statement_lines).strip()
        if statement:
            statements.append(statement)

        line_index += 1

    return statements


def _extract_function_statements(text, trailer):
    if text is None:
        return []

    matches = []
    for raw_line in text.splitlines():
        stripped_line = raw_line.strip()
        if not stripped_line or not stripped_line.endswith(trailer):
            continue
        if stripped_line.startswith("#"):
            continue
        if "(" not in stripped_line or ")" not in stripped_line:
            continue
        if re.match(r"^(return|if|for|while|switch)\b", stripped_line):
            continue
        if "=" in stripped_line.partition("(")[0]:
            continue

        name_match = FUNCTION_DECLARATION_NAME_RE.search(stripped_line)
        if name_match is None:
            continue

        prefix = stripped_line[:name_match.start()].strip()
        if prefix.startswith("extern "):
            prefix = prefix[len("extern "):].strip()
        if not prefix:
            continue

        matches.append(stripped_line)

    return matches


def get_c_function_proto(text):
    return _extract_function_statements(text, ";")


def get_c_function_imp(text):
    return _extract_matches(text, FUNCTION_IMP_RE)


def get_cpp_function_proto(text):
    return _extract_function_statements(text, ";")


def get_cpp_function_imp(text):
    return _extract_matches(text, FUNCTION_IMP_RE)


def get_cpp_class_proto(text):
    # Return an empty list when the text does not look like a forward declaration.
    return _extract_matches(text, CLASS_PROTO_RE)


def get_cpp_class_imp(text):
    return _extract_matches(text, CLASS_IMP_RE)


def get_macro_proto(text):
    return _extract_macro_names(text)


def get_macro_imp(text):
    return _extract_macro_names(text)


def get_struct_forward_decl(text):
    return _extract_matches(text, STRUCT_FORWARD_DECL_RE)


def get_struct_proto(text):
    forward_declarations = get_struct_forward_decl(text)
    struct_blocks = _extract_multiline_statements(text, STRUCT_BLOCK_START_RE)
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


def get_struct_imp(text):
    return _extract_multiline_statements(text, STRUCT_BLOCK_START_RE)


def get_typedef_proto(text):
    typedef_matches = _extract_multiline_statements(text, TYPEDEF_START_RE)
    using_matches = _extract_matches(text, USING_PROTO_RE)
    return typedef_matches + using_matches


def get_typedef_imp(text):
    return get_typedef_proto(text)
