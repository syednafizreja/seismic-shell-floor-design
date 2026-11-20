"""The CalculiX field print must carry the crown gate named in the stress-line file.

Element 221, integration points 1 to 4, is one face. Points 5 to 8 are the
other. The 0.75 m print names the same rise 0.60 m gate. The two in-plane
stresses on each point agree. Does not call CalculiX, does not write the
prints, and does not read the floor page.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "partB_generator" / "out"
GATE = re.compile(
    r"Crown element 221, faces ([+-]?\d+\.\d+e[+-]\d+) Pa and ([+-]?\d+\.\d+e[+-]\d+) Pa")
PAIRS = (
    ("smooth_gravity_stress.dat", "stress_rib.txt"),
    ("smooth_gravity_stress.dat", "stress_rib_075.txt"),
    ("smooth_gravity_stress_030.dat", "stress_rib_rise030.txt"),
)


def crown_points(text):
    found = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[0] != "221" or parts[1] not in "12345678":
            continue
        if "E" not in parts[2].upper():
            continue
        found[int(parts[1])] = (float(parts[2]), float(parts[3]))
    return found


def main():
    problems = []
    for dat_name, txt_name in PAIRS:
        dat = (OUT / dat_name).read_text(encoding="utf-8", errors="replace")
        txt = (OUT / txt_name).read_text(encoding="utf-8")
        gate = GATE.search(txt)
        if not gate:
            problems.append(f"{txt_name} has no crown-element gate")
            continue
        faces = (float(gate.group(1)), float(gate.group(2)))
        if faces[0] >= 0 or faces[1] >= 0:
            problems.append(f"{txt_name} crown gate is not compression")
        points = crown_points(dat)
        if set(points) != set(range(1, 9)):
            problems.append(f"{dat_name} does not have eight crown integration points")
            continue
        for point, stresses in points.items():
            if abs(stresses[0] - stresses[1]) > 0.05:
                problems.append(f"{dat_name} point {point} in-plane stresses differ")
            face = faces[0] if point <= 4 else faces[1]
            if abs(stresses[0] - face) > 0.05:
                problems.append(f"{dat_name} point {point} is not the {txt_name} crown gate")
    if problems:
        print("\n".join(problems))
        return 1
    print("STRESS_FIELD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
