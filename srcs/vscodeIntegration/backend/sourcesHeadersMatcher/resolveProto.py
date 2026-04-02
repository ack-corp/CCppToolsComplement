from pathlib import Path

from getSourceProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_proto,
    get_typedef_proto,
)


PROTO_GROUP_ORDER = ("class", "function", "macro", "struct", "typedef")


def _append_unique(target_list, seen_values, value):
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


def _normalize_excluded_paths(excluded_folder_paths):
    return {
        Path(folder_path).expanduser().resolve()
        for folder_path in excluded_folder_paths
    }


def _is_excluded(path, excluded_paths):
    return any(path == excluded_path or excluded_path in path.parents for excluded_path in excluded_paths)


def _normalize_extensions(extensions):
    normalized_extensions = set()
    for extension in extensions:
        if not extension:
            continue
        normalized_extension = extension.lower()
        if not normalized_extension.startswith("."):
            normalized_extension = f".{normalized_extension}"
        normalized_extensions.add(normalized_extension)
    return normalized_extensions


def _read_file(file_path):
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def _collect_from_text(file_text):
    struct_proto = get_struct_proto(file_text)
    class_proto = [proto for proto in get_cpp_class_proto(file_text) if proto not in struct_proto]
    function_proto = list(dict.fromkeys(get_c_function_proto(file_text) + get_cpp_function_proto(file_text)))
    macro_proto = get_macro_proto(file_text)
    typedef_proto = get_typedef_proto(file_text)

    return {
        "class": class_proto,
        "function": function_proto,
        "macro": macro_proto,
        "struct": struct_proto,
        "typedef": typedef_proto,
    }


def resolveProto(startPath, extensions, excludedFolderPath=None):
    start_path = Path(startPath).expanduser().resolve()
    normalized_extensions = _normalize_extensions(extensions)
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    grouped_proto = {proto_type: [] for proto_type in PROTO_GROUP_ORDER}
    seen_group_values = {proto_type: set() for proto_type in PROTO_GROUP_ORDER}

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if normalized_extensions and file_path.suffix.lower() not in normalized_extensions:
            continue

        file_text = _read_file(file_path)
        file_grouped_proto = _collect_from_text(file_text)

        for proto_type in PROTO_GROUP_ORDER:
            for proto in file_grouped_proto[proto_type]:
                _append_unique(grouped_proto[proto_type], seen_group_values[proto_type], proto)

    return [grouped_proto[proto_type] for proto_type in PROTO_GROUP_ORDER]
