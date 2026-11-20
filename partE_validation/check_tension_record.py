"""The documents must name each recorded tensile count, largest principal, smallest principal and reach.

Reads the compression prints, README.md, the preprint and the methods log.
The smooth rise 0.60 m print has no farthest-centroid line: those elements
stay at the four corners. Does not call CalculiX and does not write the prints.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "partB_generator" / "out"
README = ROOT / "README.md"
PREPRINT = ROOT / "docs" / "preprint_v1.md"
DECISIONS = ROOT / "docs" / "decisions.md"
COUNT = re.compile(r"With a tensile principal (\d+)\.")
LARGE = re.compile(r"Largest principal ([0-9.]+)e[+-]\d+")
SMALL = re.compile(r"Smallest principal -([0-9.]+)e[+-]\d+")
FAR = re.compile(r"Farthest tensile centroid from a plan corner (\d+\.\d+) m")


def main():
    readme = README.read_text(encoding="utf-8")
    preprint = PREPRINT.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    files = sorted(OUT.glob("compression_*.txt"))
    if len(files) != 9:
        print(f"{len(files)} compression prints, record has 9")
        return 1
    problems = []
    saw_corners = False
    for path in files:
        text = path.read_text(encoding="utf-8")
        count = COUNT.search(text)
        large = LARGE.search(text)
        if not count or not large:
            problems.append(f"{path.name} has no count or largest principal")
            continue
        if "With both principals tensile 0." not in text:
            problems.append(f"{path.name} no longer says both principals stay compressive")
        n = count.group(1)
        mantissa = large.group(1)
        for name, body in (("README", readme), ("preprint", preprint)):
            if f"{n} of 441" not in body:
                problems.append(f"{path.name}: {name} has no '{n} of 441'")
            if mantissa not in body:
                problems.append(f"{path.name}: {name} has no {mantissa}")
        if mantissa not in decisions:
            problems.append(f"{path.name}: decisions has no {mantissa}")
        small = SMALL.search(text)
        if not small:
            problems.append(f"{path.name} has no smallest principal")
        elif small.group(1) not in decisions:
            problems.append(f"{path.name}: decisions has no smallest principal {small.group(1)}")
        far = FAR.search(text)
        if far:
            for name, body in (("README", readme), ("preprint", preprint), ("decisions", decisions)):
                if far.group(1) not in body:
                    problems.append(f"{path.name}: {name} has no farthest centroid {far.group(1)}")
        elif path.name == "compression_smooth.txt" and "still at the four corners" in text:
            saw_corners = True
            if "all at the four corners" not in readme or "all at the four corners" not in preprint:
                problems.append("a document no longer keeps the smooth rise 0.60 m elements at the four corners")
        else:
            problems.append(f"{path.name} has no farthest centroid")
    if not saw_corners:
        problems.append("compression_smooth.txt no longer keeps the tensile elements at the four corners")
    if problems:
        print("\n".join(problems))
        return 1
    print("TENSION_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
