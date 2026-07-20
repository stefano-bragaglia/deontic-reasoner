#!/usr/bin/env python3
"""Fail if any file with statements sits below the aggregate coverage minimum.

pytest-cov/coverage.py only gate on the aggregate percentage across all files,
so one well-tested module can hide another sitting well below the threshold.
Run after `uv run coverage json -o coverage.json -q`.
"""

import json
import sys
from pathlib import Path

MIN_COVERAGE = 90.0


def main() -> int:
    coverage_path = Path("coverage.json")
    data = json.loads(coverage_path.read_text())

    offenders = []
    for filename, file_data in data["files"].items():
        summary = file_data["summary"]
        if summary["num_statements"] == 0:
            continue
        percent = summary["percent_covered"]
        if percent < MIN_COVERAGE:
            offenders.append((filename, percent))

    if offenders:
        print(f"Files below {MIN_COVERAGE:.0f}% coverage:")
        for filename, percent in sorted(offenders, key=lambda o: o[1]):
            print(f"  {filename}: {percent:.1f}%")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
