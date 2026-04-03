from __future__ import annotations

from pathlib import Path

from Classes.resolved_proto import ResolvedProto
from getSourceProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_forward_decl,
    get_struct_imp,
    get_struct_proto,
    get_typedef_proto,
)


PROTO_GROUP_ORDER = ("class", "function", "macro", "struct", "typedef")


def _append_unique(target_list: list[str], seen_values: set[str], value: str) -> None:
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


def _normalize_excluded_paths(excluded_folder_paths: list[str]) -> set[Path]:
    return {
        Path(folder_path).expanduser().resolve()
        for folder_path in excluded_folder_paths
    }


def _is_excluded(path: Path, excluded_paths: set[Path]) -> bool:
    return any(path == excluded_path or excluded_path in path.parents for excluded_path in excluded_paths)


def _normalize_extensions(extensions: set[str]) -> set[str]:
    normalized_extensions: set[str] = set()
    for extension in extensions:
        if not extension:
            continue
        normalized_extension = extension.lower()
        if not normalized_extension.startswith("."):
            normalized_extension = f".{normalized_extension}"
        normalized_extensions.add(normalized_extension)
    return normalized_extensions


def _read_file(file_path: Path) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def _write_file(file_path: Path, file_text: str) -> None:
    Path(file_path).write_text(file_text, encoding="utf-8")


def _delete_file(file_path: Path) -> None:
    Path(file_path).unlink()


def _collect_from_text(file_text: str) -> ResolvedProto:
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


def _remove_statements_from_text(file_text: str, statements: list[str]) -> str:
    updated_text = file_text
    for statement in statements:
        if not statement:
            continue

        statement_with_newline = f"{statement}\n"
        if statement_with_newline in updated_text:
            updated_text = updated_text.replace(statement_with_newline, "")
        else:
            updated_text = updated_text.replace(statement, "")

    return updated_text


def _delete_empty_source_files(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    normalized_extensions = _normalize_extensions(extensions)
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if normalized_extensions and file_path.suffix.lower() not in normalized_extensions:
            continue

        file_text = _read_file(file_path)
        if file_text.strip():
            continue

        _delete_file(file_path)


def remove_function_proto_from_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    normalized_extensions = _normalize_extensions(extensions)
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if normalized_extensions and file_path.suffix.lower() not in normalized_extensions:
            continue

        file_text = _read_file(file_path)
        function_proto = list(dict.fromkeys(get_c_function_proto(file_text) + get_cpp_function_proto(file_text)))
        if not function_proto:
            continue

        updated_text = _remove_statements_from_text(file_text, function_proto)
        if updated_text != file_text:
            _write_file(file_path, updated_text)


def remove_struct_declarations_from_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    normalized_extensions = _normalize_extensions(extensions)
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if normalized_extensions and file_path.suffix.lower() not in normalized_extensions:
            continue

        file_text = _read_file(file_path)
        struct_statements = list(
            dict.fromkeys(
                get_struct_forward_decl(file_text)
                + get_struct_imp(file_text)
            )
        )
        typedef_statements = get_typedef_proto(file_text)
        statements_to_remove = list(dict.fromkeys(struct_statements + typedef_statements))
        if not statements_to_remove:
            continue

        updated_text = _remove_statements_from_text(file_text, statements_to_remove)
        if updated_text != file_text:
            _write_file(file_path, updated_text)


def remove_macro_definitions_from_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    normalized_extensions = _normalize_extensions(extensions)
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if normalized_extensions and file_path.suffix.lower() not in normalized_extensions:
            continue

        file_text = _read_file(file_path)
        macro_statements = get_macro_proto(file_text)
        if not macro_statements:
            continue

        updated_text = _remove_statements_from_text(file_text, macro_statements)
        if updated_text != file_text:
            _write_file(file_path, updated_text)


def cleanup_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    remove_function_proto_from_sources(startPath, extensions, excludedFolderPath)
    remove_macro_definitions_from_sources(startPath, extensions, excludedFolderPath)
    remove_struct_declarations_from_sources(startPath, extensions, excludedFolderPath)
    _delete_empty_source_files(startPath, extensions, excludedFolderPath)


def resolveProto(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> ResolvedProto:
    start_path = Path(startPath).expanduser().resolve()
    normalized_extensions = _normalize_extensions(extensions)
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    grouped_proto = ResolvedProto()
    seen_group_values: dict[str, set[str]] = {proto_type: set() for proto_type in PROTO_GROUP_ORDER}

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
            target_list = grouped_proto.get_by_type(proto_type)
            for proto in file_grouped_proto.get_by_type(proto_type):
                _append_unique(target_list, seen_group_values[proto_type], proto)

    return grouped_proto
