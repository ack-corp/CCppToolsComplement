from __future__ import annotations
from pathlib import Path
from Classes.resolved_proto import ResolvedProto
from regexTools.getProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_proto,
    get_typedef_proto,
)
from utils import is_excluded, normalize_excluded_paths, read_file


def collect_from_text(file_text: str) -> ResolvedProto:
    struct_proto = get_struct_proto(file_text)
    class_proto = [proto for proto in get_cpp_class_proto(file_text) if proto not in struct_proto]
    function_proto = list(dict.fromkeys(get_c_function_proto(file_text) + get_cpp_function_proto(file_text)))
    macro_proto = get_macro_proto(file_text)
    typedef_proto = get_typedef_proto(file_text)
    return ResolvedProto(
        classes=class_proto,
        functions=function_proto,
        macros=macro_proto,
        structs=struct_proto,
        typedefs=typedef_proto,
    )


def getResolvedProto(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> ResolvedProto:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = normalize_excluded_paths(excludedFolderPath or [])
    grouped_proto = ResolvedProto()
    for file_path in start_path.rglob("*"):
        if file_path.is_file() and not is_excluded(file_path, excluded_paths) and extensions and file_path.suffix.lower() in extensions:
            file_text = read_file(file_path)
            file_grouped_proto = collect_from_text(file_text)
            grouped_proto.add_unique(file_grouped_proto)
    return grouped_proto
