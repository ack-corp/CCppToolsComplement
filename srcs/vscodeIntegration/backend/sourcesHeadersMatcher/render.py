from pathlib import Path
import os

from getSourceProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_macro_proto,
    get_struct_proto,
    get_typedef_proto,
)


def _append_unique(target_list, seen_values, value):
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


def _header_path_from_source(source_path):
    return str(Path(source_path).with_suffix(".h"))


def _entry_recurence_score(entry):
    return sum(recurence.get("times", 0) for recurence in entry.get("recurence", []))


def _proto_type(proto):
    if get_macro_proto(proto):
        return "macro"
    if get_struct_proto(proto):
        return "struct"
    if get_cpp_class_proto(proto):
        return "class"
    if get_typedef_proto(proto):
        return "typedef"
    if get_c_function_proto(proto):
        return "function"
    return None


def _target_headers_for_proto(proto, entries):
    proto_type = _proto_type(proto)
    if proto_type == "function":
        return [_header_path_from_source(entry["source"]) for entry in entries]

    if proto_type in {"macro", "struct", "typedef", "class"}:
        best_entry = max(entries, key=_entry_recurence_score)
        return [_header_path_from_source(best_entry["source"])]

    return []


def _build_header_map(generated_headers):
    header_map = {}
    seen_header_values = {}

    for proto, entries in generated_headers.items():
        for header_path in _target_headers_for_proto(proto, entries):
            header_map.setdefault(header_path, [])
            seen_header_values.setdefault(header_path, set())
            _append_unique(header_map[header_path], seen_header_values[header_path], proto)

    return header_map


def _set_entry_header_paths(generated_headers):
    for proto, entries in generated_headers.items():
        target_headers = _target_headers_for_proto(proto, entries)
        if not target_headers:
            continue

        header_path = target_headers[0]
        for entry in entries:
            entry["headerPath"] = header_path


def _render_header_content(header_path, protos):
    body = "\n".join(protos)
    if body:
        body = f"{body}\n"

    return f"#pragma once\n\n{body}"


def _existing_include_lines(file_text):
    return {line.strip() for line in file_text.splitlines() if line.strip().startswith("#include ")}


def _insert_include(file_path, include_line):
    source_file = Path(file_path)
    file_text = source_file.read_text(encoding="utf-8", errors="ignore")
    if include_line in _existing_include_lines(file_text):
        return

    lines = file_text.splitlines()
    insert_index = 0
    while insert_index < len(lines) and lines[insert_index].strip().startswith("#include "):
        insert_index += 1

    updated_lines = lines[:insert_index] + [include_line] + lines[insert_index:]
    source_file.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def add_header_includes(generated_headers):
    include_map = {}
    for entries in generated_headers.values():
        for entry in entries:
            header_path = entry.get("headerPath")
            if not header_path:
                continue

            implementation_source = str(Path(entry["source"]).resolve())
            include_map.setdefault(implementation_source, set()).add(str(Path(header_path).resolve()))
            for recurence in entry.get("recurence", []):
                include_map.setdefault(str(Path(recurence["source"]).resolve()), set()).add(
                    str(Path(header_path).resolve())
                )

    for source_path, header_paths in include_map.items():
        for header_path in sorted(header_paths):
            include_path = os.path.relpath(
                Path(header_path).resolve(),
                Path(source_path).resolve().parent,
            )
            _insert_include(source_path, f'#include "{Path(include_path).as_posix()}"')


def renderHeaders(generatedHeaders):
    _set_entry_header_paths(generatedHeaders)
    header_map = _build_header_map(generatedHeaders)

    for header_path, protos in header_map.items():
        header_file = Path(header_path)
        header_file.parent.mkdir(parents=True, exist_ok=True)
        header_file.write_text(_render_header_content(header_path, protos), encoding="utf-8")

    add_header_includes(generatedHeaders)
    return header_map
