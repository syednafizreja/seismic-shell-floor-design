"""The README must name each recorded tensile count and largest principal.

Reads the compression prints and README.md. Does not call CalculiX and does
not write those files.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "partB_generator" / "out"
README = ROOT / "README.md"
COUNT = re.compile(r"With a tensile principal (\d+)\.")
LARGE = re.compile(r"Largest principal ([0-9.]+)e[+-]\d+")


def main():
    readme = README.read_text(encoding="utf-8")
    files = sorted(OUT.glob("compression_*.txt"))
    if len(files) != 9:
        print(f"{len(files)} compression prints, record has 9")
        return 1
    problems = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        count = COUNT.search(text)
        large = LARGE.search(text)
        if not count or not large:
            problems.append(f"{path.name} has no count or largest principal")
            continue
        n = count.group(1)
        mantissa = large.group(1)
        if f"{n} of 441" not in readme:
            problems.append(f"{path.name}: README has no '{n} of 441'")
        if mantissa not in readme:
            problems.append(f"{path.name}: README has no {mantissa}")
    if problems:
        print("\n".join(problems))
        return 1
    print("TENSION_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
