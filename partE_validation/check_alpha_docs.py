"""The README, the preprint and the methods log must name the printed alpha table.

Reads alpha_star.txt only. The three sensitivity rows and the two unused frame
stiffnesses stay in that file. They are not required in the documents, which
do not quote them. The README table keeps each cell's Et, Gt, alpha, excess
and cracked pair on one row. Does not call OpenSees and does not write the file.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "partE_validation" / "out" / "alpha_star.txt"
README = ROOT / "README.md"
PREPRINT = ROOT / "docs" / "preprint_v1.md"
DECISIONS = ROOT / "docs" / "decisions.md"
STAR = re.compile(r"^(\S.*?)\s{2,}(\d+\.\d+)\s+(\d+\.\d+)\s*$")
CELL = re.compile(
    r"^(\S.*?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$")
KF = re.compile(r"K_f ground storey h=4\.55 m, beam I factor 2\.0: ([0-9.]+)e\+")
QUOTED = ("smooth rise 0", "smooth 0.60", "cross 0.60")


def require(token, docs, label, problems):
    for name, text in docs:
        if token not in text:
            problems.append(f"{label}: {name} has no {token}")


def token_in(token, text):
    return re.search(rf"(?<![\d.]){re.escape(token)}(?![\d.])", text) is not None


def main():
    text = OUT.read_text(encoding="utf-8")
    problems = []
    for phrase in (
        "Author to confirm.",
        "Author to confirm the half.",
        "the definition gives 20",
        "K_f same storey, beam I factor 1.5:",
        "K_f upper storey h=3.6 m, beam I factor 2.0:",
    ):
        if phrase not in text:
            problems.append(f"alpha_star.txt no longer has '{phrase}'")
    kf = KF.search(text)
    if not kf:
        problems.append("alpha_star.txt has no ground-storey K_f")

    head, _, cell_text = text.partition("recorded cells")
    stars = [STAR.match(line).groups() for line in head.splitlines() if STAR.match(line)]
    cells = [CELL.match(line).groups() for line in cell_text.splitlines() if CELL.match(line)]
    if len(stars) != 8:
        problems.append(f"{len(stars)} alpha* rows, record has 8")
    if len(cells) != 6:
        problems.append(f"{len(cells)} cell rows, record has 6")
    if problems:
        print("\n".join(problems))
        return 1

    readme = README.read_text(encoding="utf-8")
    preprint = PREPRINT.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    three = (("README", readme), ("preprint", preprint), ("decisions", decisions))
    two = (("README", readme), ("decisions", decisions))
    require("19.9956", three, "two-frame alpha*", problems)
    require("0.003", two, "beam element", problems)
    require("H2 is not supported", three, "H2", problems)
    if kf:
        require(kf.group(1), three, "ground-storey K_f", problems)

    public = [row for row in stars if row[0] in ("anchor bays", "equal")]
    if len(public) != 5:
        problems.append(f"{len(public)} public alpha* rows, record shows 5")
    for _name, ld, star in public:
        require(ld, (("README", readme), ("preprint", preprint)), "alpha* L/D", problems)
        require(star, three, "alpha*", problems)

    labels = [row[0] for row in cells]
    if labels != [
        "smooth rise 0", "cross rise 0", "smooth 0.30", "cross 0.30", "smooth 0.60", "cross 0.60",
    ]:
        problems.append("cell rows are not the six recorded cases")
    for label, et, gt, alpha, excess, cracked, cracked_excess in cells:
        for token, kind in (
            (alpha, "alpha"), (excess, "excess"), (cracked, "cracked alpha"),
            (cracked_excess, "cracked excess"),
        ):
            require(token, (("README", readme),), f"{label} {kind}", problems)
        if label in QUOTED:
            require(excess, (("preprint", preprint), ("decisions", decisions)), f"{label} excess", problems)
            require(cracked_excess, (("preprint", preprint),), f"{label} cracked excess", problems)
        hits = [
            line for line in readme.splitlines()
            if line.startswith("|") and token_in(alpha, line)
        ]
        if len(hits) != 1:
            problems.append(f"{label}: README has {len(hits)} table rows for alpha {alpha}")
            continue
        for token, kind in (
            (et, "Et"), (gt, "Gt"), (excess, "excess"),
            (cracked, "cracked alpha"), (cracked_excess, "cracked excess"),
        ):
            if not token_in(token, hits[0]):
                problems.append(f"{label}: README splits {kind} {token} from alpha {alpha}")

    if problems:
        print("\n".join(problems))
        return 1
    print("ALPHA_DOCS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
