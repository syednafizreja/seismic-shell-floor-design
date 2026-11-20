"""The printed gravity rows must match the layout files, and the docs must name them.

Reads the gravity, diagonal, stress-line and rise-0.30 stress prints. It does
not read the CalculiX .dat fields, does not call CalculiX, does not write
those files, and does not read the floor page.

The printed buckling factor is a rounding of the first factor in brackets.
The number of decimals is the one in the print, so 2789 stands for 2789.003.
Each crown and face pair has to stay on the same table row as its factor.
Where the methods log names a peak deflection, it is the printed largest |w|.
Gravity prints a thickness to hundredths. vault_rib.txt prints the same
thickness to tenths. Both stay as printed. The gravity print states
rho = 2500 kg/m3 and g = 9.81 m/s2.
"""
from __future__ import annotations

import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EOUT = ROOT / "partE_validation" / "out"
BOUT = ROOT / "partB_generator" / "out"
README = ROOT / "README.md"
PREPRINT = ROOT / "docs" / "preprint_v1.md"
DECISIONS = ROOT / "docs" / "decisions.md"

CROWN = re.compile(r"crown w(?: from the existing stress print)? ([+-]?\d+\.\d+) mm")
PEAK = re.compile(r"largest \|w\| (\d+\.\d+) mm")
SKIP_PEAK = {"flat", "smooth rise 0.60 m", "cross rise 0.60 m"}
FACTOR = re.compile(
    r"lowest positive buckling factor on self-weight (\d+\.?\d*)\s+factors \[([0-9.]+)")
FACES = re.compile(
    r"two faces ([+-]?\d+\.\d+e[+-]\d+) Pa and ([+-]?\d+\.\d+e[+-]\d+) Pa")
GATE = re.compile(
    r"Crown element 221, faces ([+-]?\d+\.\d+e[+-]\d+) Pa and ([+-]?\d+\.\d+e[+-]\d+) Pa")
STIFF = re.compile(r"Et/\(E T\) (\d+\.\d+)\s+Gt/\(G T\) (\d+\.\d+)")
RIB = re.compile(r"Rib thickness (\d+\.\d+) mm")
SHELL = re.compile(r"thickness shell (\d+\.\d+) mm, rib (\d+\.\d+) mm")


def between(text, start, end):
    i = text.find(start)
    if i < 0:
        return None
    j = text.find(end, i + len(start)) if end else len(text)
    if j < 0:
        return None
    return text[i:j]


def places(token):
    return len(token.split(".")[1]) if "." in token else 0


def mantissa(scientific):
    body = scientific.lower().split("e", 1)[0]
    return body[1:] if body.startswith(("+", "-")) else body


def one(pattern, text, label, problems):
    found = list(pattern.finditer(text))
    if len(found) != 1:
        problems.append(f"{label}: expected one match, found {len(found)}")
        return None
    return found[0]


def require(token, docs, label, problems):
    for name, text in docs:
        if token not in text:
            problems.append(f"{label}: {name} has no {token}")


def table_row(body, factor):
    pattern = re.compile(rf"(?<![\d.]){re.escape(factor)}(?![\d.])")
    return [line for line in body.splitlines() if line.startswith("|") and pattern.search(line)]


def row_from(text, label, problems, faces=True):
    crown = one(CROWN, text, label + " crown", problems)
    factor = one(FACTOR, text, label + " factor", problems)
    if crown is None or factor is None:
        return None
    printed, full = factor.group(1), factor.group(2)
    if abs(float(printed) - float(full)) > 0.51 * 10 ** (-places(printed)):
        problems.append(f"{label}: factor {printed} is not the rounded first eigenvalue {full}")
    peak = one(PEAK, text, label + " peak", problems)
    face = one(FACES, text, label + " faces", problems) if faces else None
    if faces and face is None:
        return None
    return {
        "crown": crown.group(1).lstrip("+-"),
        "peak": peak.group(1) if peak else "",
        "factor": printed,
        "faces": [mantissa(face.group(1)), mantissa(face.group(2))] if face else [],
        "signed": [float(face.group(1)), float(face.group(2))] if face else [],
    }


def main():
    problems = []
    bay = (EOUT / "gravity_bay.txt").read_text(encoding="utf-8")
    low = (EOUT / "gravity_rise030.txt").read_text(encoding="utf-8")
    diag = (BOUT / "diagonal_bay.txt").read_text(encoding="utf-8")
    diag_low = (BOUT / "diagonal_rise030.txt").read_text(encoding="utf-8")
    stress = (BOUT / "stress_rib.txt").read_text(encoding="utf-8")
    stress_wide = (BOUT / "stress_rib_075.txt").read_text(encoding="utf-8")
    stress_low = (BOUT / "stress_rib_rise030.txt").read_text(encoding="utf-8")
    smooth_low = (BOUT / "compression_smooth_rise030.txt").read_text(encoding="utf-8")

    if "Author to confirm the support and the density." not in bay:
        problems.append("gravity_bay.txt no longer marks the support and the density")
    if "This file does not replace gravity_bay.txt." not in low:
        problems.append("gravity_rise030.txt no longer says it leaves gravity_bay.txt in place")
    if "This file does not replace diagonal_bay.txt." not in diag_low:
        problems.append("diagonal_rise030.txt no longer says it leaves diagonal_bay.txt in place")
    if "This file does not replace stress_rib.txt." not in stress_wide:
        problems.append("stress_rib_075.txt no longer says it leaves stress_rib.txt in place")
    if "This file does not replace stress_rib.txt." not in stress_low:
        problems.append("stress_rib_rise030.txt no longer says it leaves stress_rib.txt in place")
    for name, text in (
        ("gravity_bay.txt", bay),
        ("gravity_rise030.txt", low),
        ("diagonal_bay.txt", diag),
        ("diagonal_rise030.txt", diag_low),
        ("stress_rib.txt", stress),
        ("stress_rib_075.txt", stress_wide),
        ("stress_rib_rise030.txt", stress_low),
    ):
        if "No knockdown is applied." not in text:
            problems.append(f"{name} no longer says no knockdown is applied")
        if "21x21" not in text:
            problems.append(f"{name} is not the 21x21 mesh")

    flat = between(bay, "flat, rise 0, 60 mm", "smooth, rise 0.60 m, equal volume")
    smooth = between(bay, "smooth, rise 0.60 m, equal volume", "cross, rise 0.60 m, equal volume")
    cross = between(bay, "cross, rise 0.60 m, equal volume", "")
    smooth30 = between(low, "smooth, rise 0.30 m, equal volume", "cross, rise 0.30 m, equal volume")
    cross30 = between(low, "cross, rise 0.30 m, equal volume", "")
    if any(part is None for part in (flat, smooth, cross, smooth30, cross30)):
        problems.append("a gravity heading is missing")
        print("\n".join(problems))
        return 1
    if "from the existing stress print" not in smooth30 or "two faces" in smooth30:
        problems.append("the rise 0.30 m smooth row is no longer the buckle-only print")
    rib_lines = (EOUT / "vault_rib.txt").read_text(encoding="utf-8").splitlines()
    for section, heading in (
        (flat, "smooth rise 0.00 equal V"),
        (smooth, "smooth rise 0.60 equal V"),
        (cross, "cross rise 0.60 equal V"),
        (smooth30, "smooth rise 0.30 equal V"),
        (cross30, "cross rise 0.30 equal V"),
    ):
        thick = SHELL.search(section)
        line = next((item for item in rib_lines if item.startswith(heading)), "")
        if not thick or not line:
            problems.append(f"{heading} has no thickness pair to compare")
            continue
        for raw in thick.groups():
            tenth = Decimal(raw).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            if str(tenth) not in line.split():
                problems.append(f"{heading} does not round {raw} mm to {tenth} mm")

    records = [
        ("flat", row_from(flat, "flat", problems), True, None),
        ("smooth rise 0.60 m", row_from(smooth, "smooth rise 0.60 m", problems), True, None),
        # The gravity row in the methods log quotes this crown and factor, not the faces.
        ("cross rise 0.60 m", row_from(cross, "cross rise 0.60 m", problems), False, None),
        ("smooth rise 0.30 m", row_from(smooth30, "smooth rise 0.30 m", problems, faces=False), True, None),
        ("cross rise 0.30 m", row_from(cross30, "cross rise 0.30 m", problems), True, None),
        ("diagonals rise 0.60 m", row_from(diag, "diagonals rise 0.60 m", problems), True, diag),
        ("diagonals rise 0.30 m", row_from(diag_low, "diagonals rise 0.30 m", problems), True, diag_low),
        ("stress lines 0.375 m", row_from(stress, "stress lines 0.375 m", problems), True, stress),
        ("stress lines 0.75 m", row_from(stress_wide, "stress lines 0.75 m", problems), True, stress_wide),
    ]
    layout, _, smooth_note = stress_low.partition("Smooth shell in the same print:")
    records.append((
        "stress lines rise 0.30 m",
        row_from(layout, "stress lines rise 0.30 m", problems),
        True,
        layout,
    ))

    gate_low = one(GATE, smooth_low, "rise 0.30 m stress print", problems)
    gate_rib = one(GATE, stress_low, "rise 0.30 m stress-line field", problems)
    if gate_low and gate_rib and gate_low.groups() != gate_rib.groups():
        problems.append("the rise 0.30 m stress-line field does not use the smooth crown gate")
    if gate_low:
        for item in records:
            if item[0] == "smooth rise 0.30 m" and item[1] is not None:
                item[1]["faces"] = [mantissa(gate_low.group(1)), mantissa(gate_low.group(2))]
                item[1]["signed"] = [float(gate_low.group(1)), float(gate_low.group(2))]
    for name, text in (("stress lines 0.375 m", stress), ("stress lines 0.75 m", stress_wide)):
        gate = one(GATE, text, name + " field", problems)
        smooth_row = next(item[1] for item in records if item[0] == "smooth rise 0.60 m")
        if gate and smooth_row and [mantissa(gate.group(1)), mantissa(gate.group(2))] != smooth_row["faces"]:
            problems.append(f"{name} field gate is not the smooth rise 0.60 m crown")

    note_crown = one(CROWN, smooth_note, "smooth crown in the rise 0.30 m stress-line print", problems)
    smooth30_row = next(item[1] for item in records if item[0] == "smooth rise 0.30 m")
    if note_crown and smooth30_row and note_crown.group(1).lstrip("+-") != smooth30_row["crown"]:
        problems.append("the stress-line print's smooth crown is not the gravity crown")

    readme = README.read_text(encoding="utf-8")
    preprint = PREPRINT.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    if "rho = 2500 kg/m3, g = 9.81 m/s2." not in bay:
        problems.append("gravity_bay.txt no longer states rho = 2500 kg/m3 and g = 9.81 m/s2")
    if "Density 2500 kg/m³, g = 9.81 m/s²." not in decisions:
        problems.append("decisions no longer states the density and g")
    if "Density 2500 kg/m³." not in preprint:
        problems.append("preprint no longer states the density")
    both = (("README", readme), ("preprint", preprint))
    three = both + (("decisions", decisions),)
    for label, parsed, faces_in_decisions, stiff_text in records:
        if parsed is None:
            continue
        signed = parsed["signed"]
        if label == "flat":
            if not (signed[0] > 0 > signed[1] and abs(signed[0] + signed[1]) < 1.0):
                problems.append("the flat crown is not equal bending")
        elif signed and not (signed[0] < 0 and signed[1] < 0):
            problems.append(f"{label} crown has a tensile face")
        docs = three if faces_in_decisions else both
        require(parsed["crown"], docs, label + " crown", problems)
        require(parsed["factor"], docs, label + " factor", problems)
        face_docs = three if faces_in_decisions else both
        for token in parsed["faces"]:
            require(token, face_docs, label + " face", problems)
        for name, body in both:
            hits = table_row(body, parsed["factor"])
            if len(hits) != 1:
                problems.append(f"{label}: {name} has {len(hits)} table rows for {parsed['factor']}")
                continue
            row = hits[0]
            if parsed["crown"] not in row:
                problems.append(f"{label}: {name} table row splits the crown from {parsed['factor']}")
            for token in parsed["faces"]:
                if token not in row:
                    problems.append(f"{label}: {name} table row splits {token} from {parsed['factor']}")
        if label not in SKIP_PEAK and parsed["peak"]:
            factor_at = [
                match.start() for match in re.finditer(
                    rf"(?<!\d){re.escape(parsed['factor'])}(?!\d)", decisions)
            ]
            peak_at = [
                match.start() for match in re.finditer(
                    rf"(?<!\d){re.escape(parsed['peak'])}(?!\d)", decisions)
            ]
            gap = min((abs(left - right) for left in factor_at for right in peak_at), default=None)
            if gap is None or gap > 90:
                problems.append(
                    f"{label}: decisions splits peak {parsed['peak']} from {parsed['factor']}"
                )
        if stiff_text is None:
            continue
        stiff = one(STIFF, stiff_text, label + " stiffness", problems)
        rib = one(RIB, stiff_text, label + " rib", problems)
        if stiff:
            require(stiff.group(1), three, label + " Et", problems)
            require(stiff.group(2), three, label + " Gt", problems)
        if rib:
            require(rib.group(1), three, label + " rib", problems)

    if problems:
        print("\n".join(problems))
        return 1
    print("GRAVITY_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
