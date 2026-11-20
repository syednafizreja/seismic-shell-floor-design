"""The mesh-table numbers must match vault_bay.txt, including the 60 mm conversion.

The 16×16 equal-volume row at rise 0.60 m prints Et/(E t). Dividing by
area/plan converts it to Et/(E T) for the flat 60 mm plate. Each of the
thirteen README rows keeps its thickness, area/plan, Et and Gt together.
Does not call CalculiX, does not write the file, and does not read the floor page.
"""
from __future__ import annotations

import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "partE_validation" / "out" / "vault_bay.txt"
README = ROOT / "README.md"
PREPRINT = ROOT / "docs" / "preprint_v1.md"
DECISIONS = ROOT / "docs" / "decisions.md"
ROW = re.compile(
    r"^(square 3 m, rise 0|3x3 m rise 0\.30 equal [tV]|3x3 m rise 0\.60 equal [tV]|"
    r"6x3 m rise 0\.60 equal [tV])\s+"
    r"(\d+x\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)")
ERR = re.compile(r"vs flat cell ([0-9.e+-]+) % and ([0-9.e+-]+) %")
PAIRS = (
    ("3x3 m rise 0.30 equal t", "8x8", "16x16"),
    ("3x3 m rise 0.60 equal t", "12x12", "16x16"),
    ("6x3 m rise 0.60 equal t", "8x4", "16x8"),
)


def require(token, docs, label, problems):
    for name, text in docs:
        if token not in text:
            problems.append(f"{label}: {name} has no {token}")


def has_token(token, line):
    return re.search(rf"(?<![\d.]){re.escape(token)}(?![\d.])", line) is not None


def case_label(case):
    if case == "square 3 m, rise 0":
        return "Square 3 m, rise 0"
    kind = "equal V" if case.endswith("V") else "equal t"
    plan, _, rise = case.rsplit(" ", 2)[0].partition(" rise ")
    return f"{plan.replace('x', '×')}, rise {rise} m, {kind}"


def main():
    text = OUT.read_text(encoding="utf-8")
    problems = []
    if "E = 3.3e+10 Pa, nu = 0.2, reference thickness 0.06 m." not in text:
        problems.append("vault_bay.txt no longer states the flat-plate reference")
    if "limit 0.1 %" not in text or "PASS" not in text.splitlines():
        problems.append("vault_bay.txt no longer records the 0.1 % pass")
    rows = {}
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        case, mesh, thick, area, et, gt = match.groups()
        rows[(case, mesh)] = {"t": thick, "area": area, "et": et, "gt": gt}
    if len(rows) != 13:
        problems.append(f"{len(rows)} mesh rows, record has 13")
        print("\n".join(problems))
        return 1

    err = ERR.search(text)
    if not err:
        problems.append("vault_bay.txt has no flat-cell comparison")
    elif float(err.group(1)) >= 0.1 or float(err.group(2)) >= 0.1:
        problems.append("the rise-zero error is not inside 0.1 %")

    readme = README.read_text(encoding="utf-8")
    preprint = PREPRINT.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    for row in rows.values():
        for token in row.values():
            require(token, (("README", readme),), "mesh row", problems)
    for (case, mesh), row in rows.items():
        label = case_label(case)
        mesh_label = mesh.replace("x", "×")
        hits = [
            line for line in readme.splitlines()
            if line.startswith("|") and label in line and mesh_label in line
            and all(has_token(row[key], line) for key in ("t", "area", "et", "gt"))
        ]
        if len(hits) != 1:
            problems.append(f"README has {len(hits)} rows for {label} {mesh_label}")
    if err:
        require(err.group(1), (("README", readme), ("decisions", decisions)), "rise zero", problems)
        require(err.group(2), (("README", readme), ("decisions", decisions)), "rise zero", problems)
        require(err.group(1).split("e")[0], (("preprint", preprint),), "rise zero", problems)
        require(err.group(2).split("e")[0], (("preprint", preprint),), "rise zero", problems)

    for case, fine, coarse in PAIRS:
        left, right = rows[(case, fine)], rows[(case, coarse)]
        require(f"{left['et']} to {right['et']}", (("README", readme),), case, problems)
        require(f"{left['gt']} to {right['gt']}", (("README", readme),), case, problems)

    plate = rows[("3x3 m rise 0.60 equal V", "16x16")]
    quote = (Decimal(plate["et"]) / Decimal(plate["area"])).quantize(
        Decimal("0.00001"), rounding=ROUND_HALF_UP)
    equation = f"{plate['et']} / {plate['area']} = {quote}"
    require(equation, (("README", readme), ("decisions", decisions)), "60 mm conversion", problems)

    # The methods log quotes these fields and not the whole mesh table.
    quoted = (
        (("3x3 m rise 0.30 equal V", "16x16"), ("t", "et", "gt")),
        (("3x3 m rise 0.60 equal V", "16x16"), ("t", "area", "et", "gt")),
        (("6x3 m rise 0.60 equal V", "16x8"), ("t", "et", "gt")),
        (("3x3 m rise 0.60 equal t", "12x12"), ("et", "gt")),
        (("3x3 m rise 0.60 equal t", "16x16"), ("et", "gt")),
        (("6x3 m rise 0.60 equal t", "8x4"), ("gt",)),
        (("6x3 m rise 0.60 equal t", "16x8"), ("gt",)),
    )
    for key, fields in quoted:
        for field in fields:
            require(rows[key][field], (("decisions", decisions),), " ".join(key), problems)

    if problems:
        print("\n".join(problems))
        return 1
    print("VAULT_BAY_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
