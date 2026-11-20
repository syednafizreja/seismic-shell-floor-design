"""The printed cross ratios and layout gaps must be the printed stiffness.

Reads vault_rib.txt and the diagonal and stress-line prints. The cross ratio
is Et and Gt of the cross divided by the smooth shell at that rise. A layout
gap is the smooth shell minus that layout. Five-decimal rounding of those
stiffnesses can move a ratio by one in the last place. Each smooth and cross
Et stays on the same table row as its Gt. The H1 row keeps those stiffnesses
and stays open. The key finding states the recorded rise 0.60 m ratios.
Does not call CalculiX, does not
write the files, and does not read the floor page.
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
ELEMENTS = re.compile(r"Rib elements (\d+)\.")
NLINES = re.compile(r"Lines (\d+)\.")
GAP = re.compile(r"Square-symmetry gap (\d+\.\d+) Pa")
LENGTH = re.compile(r"Plan length (\d+\.\d+) m")
# The preprint names elements and not lines. The README names 24 and 12 lines, not 32.
ELEMENT_STYLE = {
    "diagonal_bay.txt": {"README": "elements", "preprint": "elements", "decisions": "elements"},
    "diagonal_rise030.txt": {"README": "elements", "preprint": "elements", "decisions": "elements"},
    "stress_rib.txt": {"README": "of", "preprint": "elements", "decisions": "of"},
    "stress_rib_075.txt": {"README": "elements", "preprint": "elements", "decisions": "elements"},
    "stress_rib_rise030.txt": {"README": "of", "preprint": "elements", "decisions": "of"},
}
LINE_DOCS = {
    "stress_rib.txt": ("README", "decisions"),
    "stress_rib_075.txt": ("README", "decisions"),
    "stress_rib_rise030.txt": ("decisions",),
}
RIB_LABELS = {
    ("smooth", "0.00"): ("Smooth, rise 0 |", False),
    ("cross", "0.00"): ("Cross, rise 0 |", False),
    ("smooth", "0.30"): ("Smooth, rise 0.30 m |", True),
    ("cross", "0.30"): ("Cross, rise 0.30 m |", True),
    ("smooth", "0.60"): ("Smooth, rise 0.60 m |", True),
    ("cross", "0.60"): ("Cross, rise 0.60 m |", True),
}


def has_token(line, token):
    return re.search(rf"(?<!\d){re.escape(token)}(?!\d)", line) is not None


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
        for key, (label, in_preprint) in RIB_LABELS.items():
            et, gt, area = rows[key]["et"], rows[key]["gt"], rows[key]["area"]
            bodies = [("README", readme)]
            if in_preprint:
                bodies.append(("preprint", preprint))
            for name, body in bodies:
                hits = [
                    line for line in body.splitlines()
                    if line.startswith("|") and label in line and has_token(line, et)
                ]
                if not hits:
                    problems.append(f"{name} has no {label} row with {et}")
                    continue
                for line in hits:
                    if not has_token(line, gt):
                        problems.append(f"{name} splits {gt} from {et} on {label}")
                if name == "README":
                    mesh = [line for line in hits if "21×21" in line or "21x21" in line]
                    if len(mesh) != 1 or not has_token(mesh[0], area):
                        problems.append(f"README splits area/plan {area} from {et} on {label}")

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

    bodies = {"README": readme, "preprint": preprint, "decisions": decisions}
    for filename, styles in ELEMENT_STYLE.items():
        text = (BOUT / filename).read_text(encoding="utf-8")
        count = ELEMENTS.search(text)
        if not count:
            problems.append(f"{filename} has no rib-element count")
            continue
        n = count.group(1)
        for doc, style in styles.items():
            phrase = f"{n} of 441" if style == "of" else f"{n} elements"
            if phrase not in bodies[doc]:
                problems.append(f"{doc} has no '{phrase}'")
        lines = NLINES.search(text)
        if filename in LINE_DOCS:
            if not lines:
                problems.append(f"{filename} has no line count")
            else:
                phrase = f"{lines.group(1)} lines"
                for doc in LINE_DOCS[filename]:
                    if phrase not in bodies[doc]:
                        problems.append(f"{doc} has no '{phrase}'")
        for pattern in (GAP, LENGTH):
            found = pattern.search(text)
            if found and found.group(1) not in decisions:
                problems.append(f"decisions has no {found.group(1)} from {filename}")

    h1 = next((line for line in readme.splitlines() if "None of these layouts closes H1" in line), "")
    if "Open." not in h1:
        problems.append("the H1 row no longer stays open")
    else:
        pairs = [
            (rows[("smooth", "0.60")]["et"], rows[("smooth", "0.60")]["gt"]),
            (rows[("cross", "0.60")]["et"], rows[("cross", "0.60")]["gt"]),
        ]
        for filename in (
            "diagonal_rise030.txt",
            "stress_rib_rise030.txt",
            "diagonal_bay.txt",
            "stress_rib.txt",
            "stress_rib_075.txt",
        ):
            stiff = STIFF.search((BOUT / filename).read_text(encoding="utf-8"))
            if not stiff:
                problems.append(f"{filename} has no Et, Gt line")
                continue
            pairs.append((stiff.group(1), stiff.group(2)))
        for et, gt in pairs:
            if not has_token(h1, et) or not has_token(h1, gt):
                problems.append(f"the H1 row splits {et} from {gt}")
    finding = (
        "One rib cross stays below the smooth shell. At rise 0.60 m, "
        f"Et/(E T) is {rows[('cross', '0.60')]['et']} on the cross and "
        f"{rows[('smooth', '0.60')]['et']} on the smooth shell. "
        f"The flat plate is {rows[('smooth', '0.00')]['et']}."
    )
    if finding not in readme:
        problems.append("the key finding no longer states the recorded rise 0.60 m ratios")

    if problems:
        print("\n".join(problems))
        return 1
    print("LAYOUT_DELTAS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
