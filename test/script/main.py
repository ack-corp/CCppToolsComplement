#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable

C_PROGRAM_DIR = ROOT / "test" / "cProgram"
PROGRAMS = [
    {
        "main_rel": "test/cProgram/main1.c",
        "program_name": "testCProgram1",
    },
    {
        "main_rel": "test/cProgram/main2.c",
        "program_name": "testCProgram2",
    },
]
HEADER_PATH = C_PROGRAM_DIR / "subfolder" / "header.h"

SCRIPT_GENERATE_JSON = ROOT / "srcs" / "script" / "generateJsonForMakefile.py"
SCRIPT_VERIFY_CONFIG = ROOT / "srcs" / "script" / "verifyMakefileConfig.py"
SCRIPT_GENERATE_MAKEFILE = ROOT / "srcs" / "script" / "generateMakefileFromJson.py"

DEFAULT_FLAGS = "-Wall -Wextra -Werror -MMD -MP"


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    input_text: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> str:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        input=input_text,
        capture_output=True,
        text=True,
        env=env,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode, cmd, output=completed.stdout, stderr=completed.stderr
        )
    return completed.stdout


def reset_artifacts() -> None:
    vscode_dir = ROOT / ".vscode"
    if vscode_dir.exists():
        shutil.rmtree(vscode_dir)

    patterns = ["*.o", "*.d", "*.out", "Makefile", "Makefile.*"]
    for pattern in patterns:
        for path in C_PROGRAM_DIR.rglob(pattern):
            if path.is_file():
                path.unlink()


def set_define_test(value: str) -> None:
    lines = HEADER_PATH.read_text(encoding="utf-8").splitlines()
    updated = False
    for idx, line in enumerate(lines):
        if line.strip().startswith("#define DEFINE_TEST"):
            lines[idx] = f'#define DEFINE_TEST "{value}"'
            updated = True
            break
    if not updated:
        raise RuntimeError("Could not find '#define DEFINE_TEST' in header.")
    HEADER_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_all() -> None:
    for program in PROGRAMS:
        main_rel = program["main_rel"]
        program_name = program["program_name"]
        bin_name = f"{program_name}.out"
        output_makefile_rel = f"test/cProgram/Makefile.{program_name}"
        generator_input = "\n".join(
            [
                main_rel,
                program_name,
                "",
                bin_name,
                output_makefile_rel,
                DEFAULT_FLAGS,
                "",
            ]
        )
        run([PYTHON, str(SCRIPT_GENERATE_JSON)], cwd=ROOT, input_text=generator_input)
    run([PYTHON, str(SCRIPT_VERIFY_CONFIG)], cwd=ROOT)
    run([PYTHON, str(SCRIPT_GENERATE_MAKEFILE)], cwd=ROOT)


def run_program(program_name: str) -> str:
    bin_name = f"{program_name}.out"
    child_makefile = C_PROGRAM_DIR / f"Makefile.{program_name}"
    run(
        ["make", "-f", str(child_makefile.name), "all"],
        cwd=C_PROGRAM_DIR,
        env_overrides={"CCACHE_DISABLE": "1"},
    )
    return run([str(C_PROGRAM_DIR / bin_name)], cwd=C_PROGRAM_DIR)


def assert_output(actual: str, expected: str, step: str) -> None:
    normalized_actual = actual.strip()
    normalized_expected = expected.strip()
    if normalized_actual != normalized_expected:
        raise AssertionError(
            f"{step} output mismatch.\nExpected:\n{normalized_expected}\n\nActual:\n{normalized_actual}"
        )
    print(f"{step} output verified.")


def main() -> None:
    print("Resetting generated artifacts...")
    reset_artifacts()

    print('Setting header to baseline: #define DEFINE_TEST "define test"...')
    set_define_test("define test")

    print("Generating config + Makefiles (first pass)...")
    generate_all()

    print("Launching C programs (first pass)...")
    for program in PROGRAMS:
        output_first = run_program(program["program_name"])
        assert_output(
            output_first,
            "define test\none\ntwo",
            f"First pass ({program['program_name']})",
        )

    print('Updating header define to: #define DEFINE_TEST "define test update"...')
    set_define_test("define test update")

    print("Generating config + Makefiles (second pass)...")
    generate_all()

    print("Launching C programs (second pass)...")
    for program in PROGRAMS:
        output_second = run_program(program["program_name"])
        assert_output(
            output_second,
            "define test update\none\ntwo",
            f"Second pass ({program['program_name']})",
        )

    print("All checks passed. You can now launch a debugging session in VSCode.")


if __name__ == "__main__":
    main()
