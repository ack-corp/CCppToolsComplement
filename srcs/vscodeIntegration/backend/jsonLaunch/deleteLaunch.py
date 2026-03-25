#!/usr/bin/env python3
import argparse
from pathlib import Path

from helper.utils import readJsonObject, writeJsonObject


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete one generated launch from .vscode/launch.json.")
    parser.add_argument("program_name", help="Program name used in the generated launch configuration.")
    return parser.parse_args()


def deleteLaunch(program_name: str) -> None:
    workspace = Path.cwd().resolve()
    launch_path = (workspace / ".vscode/launch.json").resolve()
    launch_json = readJsonObject(launch_path, {"version": "0.2.0", "configurations": []})
    configurations = launch_json.get("configurations", [])
    if not isinstance(configurations, list):
        configurations = []
    launch_json["configurations"] = [
        configuration
        for configuration in configurations
        if not (isinstance(configuration, dict) and configuration.get("name") == program_name)
    ]
    writeJsonObject(launch_path, launch_json)
    print(f"Updated {launch_path}")


if __name__ == "__main__":
    deleteLaunch(parse_args().program_name)
