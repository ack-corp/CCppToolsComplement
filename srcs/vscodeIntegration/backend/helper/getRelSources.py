import os
from pathlib import Path
import re
from typing import Optional

SRC_EXTS = [".cpp", ".cc", ".cxx", ".c"]
HDR_EXTS = [".hpp", ".hh", ".hxx", ".h"]
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*"([^"]+)"')


def parse_local_includes(path: Path) -> list[str]:
    includes: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")
    for line in text.splitlines():
        match = INCLUDE_RE.match(line)
        if match:
            includes.append(match.group(1))
    return includes


def resolve_include(include_name: str, base_file: Path, project_root: Path) -> Path | None:
    candidates = [
        base_file.parent / include_name,
        project_root / include_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def sibling_source_for(header_path: Path, preferred_ext: str) -> Path | None:
    stem = header_path.with_suffix("")
    preferred = stem.with_suffix(preferred_ext)
    if preferred.exists():
        return preferred.resolve()
    for ext in SRC_EXTS:
        candidate = stem.with_suffix(ext)
        if candidate.exists():
            return candidate.resolve()
    return None


def discover_sources(main_src: Path, project_root: Path) -> list[Path]:
    preferred_ext = main_src.suffix
    queue = [main_src.resolve()]
    seen: set[Path] = set()
    sources: set[Path] = set()

    while queue:
        current = queue.pop()
        if current in seen:
            continue
        seen.add(current)

        if current.suffix in SRC_EXTS:
            sources.add(current)

        for include_name in parse_local_includes(current):
            included = resolve_include(include_name, current, project_root)
            if included is None:
                continue
            if included not in seen:
                queue.append(included)
            if included.suffix in HDR_EXTS:
                sibling = sibling_source_for(included, preferred_ext)
                if sibling and sibling not in seen:
                    queue.append(sibling)

    main_resolved = main_src.resolve()
    return sorted(sources, key=lambda path: (0 if path == main_resolved else 1, str(path)))


def program_from_submake(path: Path) -> Optional[str]:
    name = path.name
    prefix = "Makefile."
    if not name.startswith(prefix):
        return None
    program = name[len(prefix) :].strip()
    if program.endswith(".json"):
        return None
    return program or None


def getMainPath(main_input: str, project_root: Path) -> Path:
    main_path = Path(main_input)
    if not main_path.is_absolute():
        main_path = (project_root / main_path).resolve()
    if not main_path.exists():
        raise SystemExit(f"Main file not found: {main_path}")
    if main_path.suffix not in SRC_EXTS:
        raise SystemExit(
            f"Unsupported main extension '{main_path.suffix}'. Supported: {', '.join(SRC_EXTS)}"
        )
    return main_path


def getSource(main_path: Path, project_root: Path) -> list[Path]:
    sources = discover_sources(main_path, project_root)
    if not sources:
        return [main_path.resolve()]
    return sources


def getOutputPath(main_path: Path, program_name: str) -> Path:
    out_path = (main_path.parent / f"Makefile.{program_name}").resolve()
    if out_path.name == "Makefile":
        raise SystemExit("Output path must be a sub-Makefile, not the parent Makefile.")
    if not out_path.name.startswith("Makefile."):
        raise SystemExit("Output filename must match format: Makefile.<program>")
    path_program = program_from_submake(out_path)
    if path_program != program_name:
        raise SystemExit(
            f"Program name '{program_name}' must match output filename suffix '{path_program}'."
        )
    return out_path


def getRelativePath(sources: list[Path], start: Path) -> list[str]:
    return [os.path.relpath(source.resolve(), start.resolve()).replace("\\", "/") for source in sources]


def getRelSources(main_input: str, program_name: str, project_root: Path | None = None) -> list[str]:
    root = project_root if project_root is not None else Path.cwd()
    main_path = getMainPath(main_input, root)
    sources = getSource(main_path, root)
    out_path = getOutputPath(main_path, program_name)
    return getRelativePath(sources, out_path.parent)
