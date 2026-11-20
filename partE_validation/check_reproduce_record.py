"""The generator print must match the recorded rib stiffness at five decimals.

The printed columns agree exactly. The file also records a smaller unrounded
difference, and that token has to stay in the README and the methods log.
The rib thickness is the gravity print; the rib file rounds it to one decimal.
Does not call CalculiX, does not write either file, and does not read the floor page.
"""
from __future__ import annotations

import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "partB_generator" / "out" / "reproduce_bay.txt"
RIB = ROOT / "partE_validation" / "out" / "vault_rib.txt"
GRAVITY = ROOT / "partE_validation" / "out" / "gravity_bay.txt"
README = ROOT / "README.md"
DECISIONS = ROOT / "docs" / "decisions.md"
PAIR = re.compile(
    r"^(smooth|cross)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$")
THICK = re.compile(r"rib thickness (\d+\.\d+) mm\. Largest absolute difference ([0-9.e+-]+)\.")


def main():
    text = REPRO.read_text(encoding="utf-8")
    rib = RIB.read_text(encoding="utf-8")
    problems = []
    if "PASS" not in text.splitlines():
        problems.append("reproduce_bay.txt does not pass")
    if "H1 stays open." not in text:
        problems.append("reproduce_bay.txt no longer leaves H1 open")
    rows = [PAIR.match(line).groups() for line in text.splitlines() if PAIR.match(line)]
    if [row[0] for row in rows] != ["smooth", "cross"]:
        problems.append("reproduce_bay.txt does not have the smooth shell and the cross")
    for name, got_et, file_et, got_gt, file_gt in rows:
        if got_et != file_et or got_gt != file_gt:
            problems.append(f"{name} got {got_et}, {got_gt} and file {file_et}, {file_gt}")
            continue
        line = next((item for item in rib.splitlines() if item.startswith(f"{name} rise 0.60 equal V")), "")
        if file_et not in line.split() or file_gt not in line.split():
            problems.append(f"vault_rib.txt rise 0.60 m {name} has no {file_et} or {file_gt}")
    thick = THICK.search(text)
    if not thick:
        problems.append("reproduce_bay.txt has no rib thickness or difference")
    else:
        if thick.group(1) not in GRAVITY.read_text(encoding="utf-8"):
            problems.append("the generator rib thickness is not the gravity cross rib")
        rounded = Decimal(thick.group(1)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        rib_line = next((item for item in rib.splitlines() if item.startswith("cross rise 0.60 equal V")), "")
        if str(rounded) not in rib_line.split():
            problems.append(f"vault_rib.txt does not round the rib to {rounded} mm")
        docs = (
            ("README", README.read_text(encoding="utf-8")),
            ("decisions", DECISIONS.read_text(encoding="utf-8")),
        )
        for name, body in docs:
            if thick.group(2) not in body:
                problems.append(f"{name} has no generator difference {thick.group(2)}")
    if problems:
        print("\n".join(problems))
        return 1
    print("REPRODUCE_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
