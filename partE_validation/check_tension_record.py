"""The documents must name each recorded tensile count, largest principal, smallest principal and reach.

Reads the compression prints, README.md, the preprint and the methods log.
The smooth rise 0.60 m print has no farthest-centroid line: those elements
stay at the four corners. Each largest principal has to stay in that layout's
sentences. Each print keeps 20 tensile elements within one element pitch of
the plan boundary, and each principal on the next line is named in the
methods log. Does not call CalculiX and does not write the prints.
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
SPANS = (
    ("24 of 441 elements", "32 of 441 elements", ("6.950346",)),
    ("32 of 441 elements", "On the cross", ("9.369478",)),
    (
        "32 at rise 0.30 m and 24 at rise 0.60 m",
        "On the diagonals",
        ("1.031277", "7.047014"),
    ),
    ("24 at both rises", "On the stress lines", ("5.770915", "5.506480")),
)
STRESS = ("1.020770", "6.630235", "6.193632")
OWNED = tuple(item for _, _, group in SPANS for item in group) + STRESS


def find_phrase(body, phrase, start=0):
    match = re.search(r"(?<!\d)" + re.escape(phrase), body[start:])
    return start + match.start() if match else -1


def layout_order(body, label, problems):
    for start, end, mantissas in SPANS:
        begin = find_phrase(body, start)
        finish = find_phrase(body, end, begin + len(start)) if begin >= 0 else -1
        if begin < 0 or finish < 0:
            problems.append(f"{label} has no span from '{start}' to '{end}'")
            continue
        chunk = body[begin:finish]
        positions = [chunk.find(mantissa) for mantissa in mantissas]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            problems.append(f"{label} does not keep {' '.join(mantissas)} with '{start}'")
        for mantissa in OWNED:
            if mantissa not in mantissas and mantissa in chunk:
                problems.append(f"{label} puts {mantissa} in the '{start}' span")
    begin = find_phrase(body, "On the stress lines")
    cursor = begin
    positions = []
    for mantissa in STRESS:
        found = body.find(mantissa, cursor) if cursor >= 0 else -1
        positions.append(found)
        cursor = found + len(mantissa) if found >= 0 else cursor
    if begin < 0 or any(position < 0 for position in positions) or not (
        begin < positions[0] < positions[1] < positions[2]
    ):
        problems.append(f"{label} does not keep the stress-line principals in spacing order")
        return
    chunk = body[begin:positions[-1]]
    for mantissa in OWNED:
        if mantissa not in STRESS and mantissa in chunk:
            problems.append(f"{label} puts {mantissa} in the stress-line span")


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
        edge = "Of the tensile elements, 20 lie within one element pitch of the plan boundary."
        lines = text.splitlines()
        if edge not in lines:
            problems.append(f"{path.name} no longer keeps 20 tensile elements within one element pitch")
        else:
            inner = lines[lines.index(edge) + 1] if lines.index(edge) + 1 < len(lines) else ""
            found = re.findall(r"([0-9.]+)e[+-]\d+ Pa", inner)
            if not found:
                problems.append(f"{path.name} has no interior principal")
            for token in found:
                if token not in decisions:
                    problems.append(f"{path.name}: decisions has no interior principal {token}")
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
    layout_order(readme, "README", problems)
    layout_order(preprint, "preprint", problems)
    if problems:
        print("\n".join(problems))
        return 1
    print("TENSION_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
