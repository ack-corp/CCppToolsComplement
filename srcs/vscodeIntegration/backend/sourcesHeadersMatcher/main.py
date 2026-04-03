from __future__ import annotations

import argparse

from getTraversalResult import getTraversalResult
from printer import format_stringified_headers
from recurence import setRecurence
from stringify import stringify_headers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("startPath")
    parser.add_argument("excludedFolderPath", nargs="*")
    args = parser.parse_args()
    startPath = args.startPath
    excludedFolderPath = args.excludedFolderPath

    traversal_result = getTraversalResult(startPath, excludedFolderPath)
    setRecurence(traversal_result.generated_headers, traversal_result.source_texts_by_path)

    stringified_headers = stringify_headers(traversal_result.generated_headers)
    print(format_stringified_headers(stringified_headers))


if __name__ == "__main__":
    main()
