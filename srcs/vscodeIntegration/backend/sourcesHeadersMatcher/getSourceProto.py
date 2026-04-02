import re


FUNCTION_NAME_RE = r"[A-Za-z_]\w*(?:::\w+)*"
TYPE_PREFIX_RE = r"(?:[\w:\<\>\~\*&,\s]+?\s+)?"

FUNCTION_PROTO_RE = re.compile(
    rf"^\s*(?:extern\s+)?{TYPE_PREFIX_RE}{FUNCTION_NAME_RE}\s*\([^;{{}}]*\)\s*(?:const\s*)?;\s*$",
    re.MULTILINE,
)
FUNCTION_IMP_RE = re.compile(
    rf"^\s*(?:extern\s+)?{TYPE_PREFIX_RE}{FUNCTION_NAME_RE}\s*\([^;{{}}]*\)\s*(?:const\s*)?\{{\s*$",
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
STRUCT_PROTO_RE = re.compile(
    r"^\s*struct\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*;\s*$",
    re.MULTILINE,
)
STRUCT_IMP_RE = re.compile(
    r"^\s*struct\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*\{\s*$",
    re.MULTILINE,
)
TYPEDEF_PROTO_RE = re.compile(r"^\s*typedef\s+.+;\s*$", re.MULTILINE)
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


def get_c_function_proto(text):
    return _extract_matches(text, FUNCTION_PROTO_RE)


def get_c_function_imp(text):
    return _extract_matches(text, FUNCTION_IMP_RE)


def get_cpp_function_proto(text):
    return _extract_matches(text, FUNCTION_PROTO_RE)


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


def get_struct_proto(text):
    return _extract_matches(text, STRUCT_PROTO_RE)


def get_struct_imp(text):
    return _extract_matches(text, STRUCT_IMP_RE)


def get_typedef_proto(text):
    typedef_matches = _extract_matches(text, TYPEDEF_PROTO_RE)
    using_matches = _extract_matches(text, USING_PROTO_RE)
    return typedef_matches + using_matches


def get_typedef_imp(text):
    return get_typedef_proto(text)
