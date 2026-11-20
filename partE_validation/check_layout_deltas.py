"""The printed cross ratios and layout gaps must be the printed stiffness.

Reads vault_rib.txt and the diagonal and stress-line prints. The cross ratio
is Et and Gt of the cross divided by the smooth shell at that rise. A layout
gap is the smooth shell minus that layout. Five-decimal rounding of those
stiffnesses can move a ratio by one in the last place. Does not call CalculiX,
does not write the files, and does not read the floor page.
"""
from __future__ import annotations

import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RIB = ROOT / "partE_validation" / "out" / "vault_rib.txt"
BOUT = ROOT / "partB_generator" / "out"
README = ROOT / "README.md"
PREPRINT = ROOT / "docs" / "preprint_v1.md"
DECISIONS = ROOT / "docs" / "decisions.md"
# One unit in the fifth decimal. The printed ratio can use the unrounded stiffness.
RATIO_TOL = Decimal("0.00002")
CASE = re.compile(
    r"^(smooth|cross) rise (0\.00|0\.30|0\.60) equal V\s+21x21\s+"
    r"\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)",
    re.M)
RATIO = re.compile(r"Et_cross/Et_smooth (\d+\.\d+), Gt_cross/Gt_smooth (\d+\.\d+)")
VOLUME = re.compile(r"volume (\d+\.\d+) m3")
STIFF = re.compile(r"Et/\(E T\) (\d+\.\d+)\s+Gt/\(G T\) (\d+\.\d+)")


def gap(left, right):
    return abs(Decimal(left) - Decimal(right)).quantize(Decimal("0.00001"))


def word(left, right):
    return "below" if Decimal(right) < Decimal(left) else "above"


def main():
    problems = []
    rib = RIB.read_text(encoding="utf-8")
    if "Author to confirm." not in rib:
        problems.append("vault_rib.txt no longer marks the cross as still to confirm")
    rows = {}
    lines = rib.splitlines()
    for i, line in enumerate(lines):
        match = CASE.match(line)
        if not match:
            continue
        kind, rise, area, et, gt = match.groups()
        rows[(kind, rise)] = {"area": area, "et": et, "gt": gt, "line": i}
    if set(rows) != {(k, r) for k in ("smooth", "cross") for r in ("0.00", "0.30", "0.60")}:
        problems.append("vault_rib.txt does not have the six smooth and cross rows")
        print("\n".join(problems))
        return 1

    ratios = {}
    for rise in ("0.00", "0.30", "0.60"):
        smooth, cross = rows[("smooth", rise)], rows[("cross", rise)]
        if smooth["area"] != cross["area"]:
            problems.append(f"rise {rise} smooth and cross do not share area/plan")
        follow = "\n".join(lines[cross["line"] + 1:cross["line"] + 3])
        parsed = RATIO.search(follow)
        volume = VOLUME.search(follow)
        if not parsed or not volume:
            problems.append(f"rise {rise} has no cross-ratio line")
            continue
        if volume.group(1) != "0.5400":
            problems.append(f"rise {rise} volume is not 0.5400 m3")
        for kind, printed, s_value, c_value in (
            ("Et", parsed.group(1), smooth["et"], cross["et"]),
            ("Gt", parsed.group(2), smooth["gt"], cross["gt"]),
        ):
            quote = Decimal(c_value) / Decimal(s_value)
            if abs(quote - Decimal(printed)) > RATIO_TOL:
                problems.append(f"rise {rise} {kind} ratio {printed} is not the cross over the smooth shell")
        ratios[rise] = (parsed.group(1), parsed.group(2))

    readme = README.read_text(encoding="utf-8")
    preprint = PREPRINT.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    if len(ratios) == 3:
        r0, r3, r6 = ratios["0.00"], ratios["0.30"], ratios["0.60"]
        phrases = {
            "README": (
                f"{r6[0]} of the smooth shell in extension and {r6[1]} in shear",
                f"{r3[0]} and {r3[1]}",
                f"{r0[0]} and {r0[1]}",
            ),
            "decisions": (
                f"{r6[0]} and {r6[1]}",
                f"{r3[0]} and {r3[1]}",
                f"{r0[0]} and {r0[1]}",
            ),
            "preprint": (
                f"{r6[0]} of the smooth shell in extension and {r6[1]} in shear",
            ),
        }
        texts = {"README": readme, "decisions": decisions, "preprint": preprint}
        for name, expected in phrases.items():
            for phrase in expected:
                if phrase not in texts[name]:
                    problems.append(f"{name} has no '{phrase}'")

    layouts = (
        ("diagonal_rise030.txt", "0.30", "pair", "split"),
        ("stress_rib_rise030.txt", "0.30", "pair", "split"),
        ("stress_rib.txt", "0.60", "pair", "pair"),
        ("stress_rib_075.txt", "0.60", "split", "split"),
    )
    for filename, rise, doc_style, decision_style in layouts:
        text = (BOUT / filename).read_text(encoding="utf-8")
        stiff = STIFF.search(text)
        if not stiff:
            problems.append(f"{filename} has no Et, Gt line")
            continue
        smooth = rows[("smooth", rise)]
        et_word, gt_word = word(smooth["et"], stiff.group(1)), word(smooth["gt"], stiff.group(2))
        et_gap, gt_gap = gap(smooth["et"], stiff.group(1)), gap(smooth["gt"], stiff.group(2))
        if doc_style == "pair":
            phrase = f"{et_gap} and {gt_gap} below"
            if et_word != "below" or gt_word != "below":
                problems.append(f"{filename} is not below the smooth shell in both ratios")
            for name, body in (("README", readme), ("preprint", preprint)):
                if phrase not in body:
                    problems.append(f"{name} has no '{phrase}'")
        else:
            for name, body in (("README", readme), ("preprint", preprint)):
                if f"{et_gap} {et_word}" not in body or f"{gt_gap} {gt_word}" not in body:
                    problems.append(f"{name} has no {et_gap} {et_word} and {gt_gap} {gt_word}")
        if decision_style == "pair":
            phrase = f"{et_gap} and {gt_gap} below"
            if phrase not in decisions:
                problems.append(f"decisions has no '{phrase}'")
        else:
            if f"{et_gap} {et_word}" not in decisions or f"{gt_gap} {gt_word}" not in decisions:
                problems.append(f"decisions has no {et_gap} {et_word} and {gt_gap} {gt_word}")

    diag = (BOUT / "diagonal_bay.txt").read_text(encoding="utf-8")
    stiff = STIFF.search(diag)
    if stiff:
        smooth = rows[("smooth", "0.60")]
        if word(smooth["gt"], stiff.group(2)) != "above" or word(smooth["et"], stiff.group(1)) != "below":
            problems.append("the rise 0.60 m diagonals are not below in extension and above in shear")
        if "diagonal shear ratio is above the smooth shell" not in preprint:
            problems.append("the preprint no longer says the diagonal shear ratio is above the smooth shell")
        if "Shear is above it" not in decisions:
            problems.append("the methods log no longer says the diagonal shear is above the smooth shell")

    if problems:
        print("\n".join(problems))
        return 1
    print("LAYOUT_DELTAS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
