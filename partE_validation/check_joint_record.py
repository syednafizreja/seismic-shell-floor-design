"""The printed joint ratios must match the continuous row, and the docs must name them.

Reads partE_validation/out/joint_stiffness.txt, README.md, docs/preprint_v1.md
and docs/decisions.md. Et/cont and Gt/cont are the same row divided by the
factor-1 row. The print keeps five decimals, so that quotient can differ from
the printed continuous ratio by a few hundredths of a thousandth. The flat
factor-0.1 ratio stays with its strip width. The methods log names the vault
factor-0.1 Et/(E T), Et/cont, Gt/(G T) and Gt/cont. The methods log
names each equal-volume vault thickness beside its mesh. Does not call CalculiX,
does not write the file, and does not read the floor page.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "partE_validation" / "out" / "joint_stiffness.txt"
README = ROOT / "README.md"
PREPRINT = ROOT / "docs" / "preprint_v1.md"
DECISIONS = ROOT / "docs" / "decisions.md"
# Half a digit in the fourth decimal. Five-decimal rounding of both the
# numerator and the factor-1 denominator can move the quotient by about 3e-5.
RATIO_TOL = 5e-5
FACTORS = (1.0, 0.5, 0.2, 0.1)
ROW = re.compile(
    r"^(flat 60 mm|vault rise 0\.60 equal V)\s+(9x9|15x15)\s+"
    r"(\d+\.\d+)\s+(\d+\.\d+)\s+"
    r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$")
THICK = re.compile(
    r"^equal-volume thickness on the (9x9|15x15) vault: (\d+\.\d+) mm$",
    re.M)


def main():
    text = OUT.read_text(encoding="utf-8")
    problems = []
    if "Author to confirm the strip and the factor." not in text:
        problems.append("the print no longer marks the strip as still to confirm")
    if "Et/cont is the same row at factor 1." not in text:
        problems.append("the print no longer says Et/cont is the factor-1 row")
    if "E = 3.3e+10 Pa, nu = 0.2" not in text:
        problems.append("the print no longer states E = 3.3e+10 Pa and nu = 0.2")

    groups = {}
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        case, mesh, width, factor, et60, gt60, etcont, gtcont = match.groups()
        groups.setdefault((case, mesh), []).append({
            "width": float(width),
            "factor": float(factor),
            "et60": float(et60),
            "gt60": float(gt60),
            "etcont": float(etcont),
            "gtcont": float(gtcont),
            "et60_s": et60,
            "etcont_s": etcont,
            "gt60_s": gt60,
            "gtcont_s": gtcont,
            "width_s": width,
        })
    if len(groups) != 4 or sum(len(rows) for rows in groups.values()) != 16:
        problems.append(f"{sum(len(rows) for rows in groups.values())} joint rows, record has 16")

    flat_tokens = []
    flat_pairs = []
    vault_tokens = []
    vault_low = []
    for (case, mesh), rows in groups.items():
        n = int(mesh.split("x")[0])
        factors = [row["factor"] for row in rows]
        if sorted(factors, reverse=True) != list(FACTORS) or len(factors) != 4:
            problems.append(f"{case} {mesh} does not have factors 1, 0.5, 0.2 and 0.1")
            continue
        if any(abs(row["width"] - round(3.0 / n, 4)) > 1e-9 for row in rows):
            problems.append(f"{mesh} width is not 3/{n} m to four decimals")
        base = next(row for row in rows if row["factor"] == 1.0)
        if abs(base["etcont"] - 1.0) > 1e-9 or abs(base["gtcont"] - 1.0) > 1e-9:
            problems.append(f"{case} {mesh} factor 1 is not the continuous floor")
        if case.startswith("flat") and (abs(base["et60"] - 1.0) > 1e-9 or abs(base["gt60"] - 1.0) > 1e-9):
            problems.append(f"{mesh} flat factor 1 is not the 60 mm plate")
        ordered = sorted(rows, key=lambda row: row["factor"], reverse=True)
        for left, right in zip(ordered, ordered[1:]):
            if not (left["et60"] > right["et60"] and left["gt60"] > right["gt60"]):
                problems.append(f"{case} {mesh} stiffness does not fall as the factor falls")
                break
        for row in rows:
            if abs(row["etcont"] - row["et60"] / base["et60"]) > RATIO_TOL:
                problems.append(f"{case} {mesh} factor {row['factor']} Et/cont is not Et/E60 over factor 1")
            if abs(row["gtcont"] - row["gt60"] / base["gt60"]) > RATIO_TOL:
                problems.append(f"{case} {mesh} factor {row['factor']} Gt/cont is not Gt/G60 over factor 1")
        low = next(row for row in rows if row["factor"] == 0.1)
        if case.startswith("flat"):
            flat_tokens.append(low["etcont_s"])
            flat_pairs.append((low["etcont_s"], low["width_s"]))
        else:
            vault_tokens.append(base["et60_s"])
            vault_low.append((
                mesh, low["et60_s"], low["etcont_s"], low["gt60_s"], low["gtcont_s"]))

    thick = {mesh: float(mm) for mesh, mm in THICK.findall(text)}
    if set(thick) != {"9x9", "15x15"}:
        problems.append("the print does not give both vault thicknesses")
    elif any(not 50.0 < mm < 60.0 for mm in thick.values()):
        problems.append("a vault thickness is outside 50 mm to 60 mm")

    if len(flat_tokens) == 2 and len(vault_tokens) == 2:
        readme = README.read_text(encoding="utf-8")
        preprint = PREPRINT.read_text(encoding="utf-8")
        decisions = DECISIONS.read_text(encoding="utf-8")
        for token in flat_tokens:
            if token not in readme:
                problems.append(f"README has no flat factor-0.1 Et/cont {token}")
            if token not in preprint:
                problems.append(f"preprint has no flat factor-0.1 Et/cont {token}")
            if token not in decisions:
                problems.append(f"decisions has no flat factor-0.1 Et/cont {token}")
        for token in vault_tokens:
            if token not in decisions:
                problems.append(f"decisions has no vault factor-1 Et/E60 {token}")
        for mesh, et60, etcont, gt60, gtcont in vault_low:
            if et60 not in decisions or etcont not in decisions:
                problems.append(f"decisions has no vault factor-0.1 {et60} and {etcont} on {mesh}")
            if gt60 not in decisions or gtcont not in decisions:
                problems.append(f"decisions has no vault factor-0.1 {gt60} and {gtcont} on {mesh}")
        labels = {"9x9": "9×9", "15x15": "15×15"}
        for mesh, mm in THICK.findall(text):
            start = decisions.find(mm)
            window = decisions[start:start + 20] if start >= 0 else ""
            if labels[mesh] not in window:
                problems.append(f"decisions has no equal-volume thickness {mm} mm on {mesh}")
        if len(flat_pairs) == 2:
            for token, width in flat_pairs:
                shown = f"{float(width):.3f}"
                other = next(item[0] for item in flat_pairs if item[0] != token)
                hits = [
                    line for line in readme.splitlines()
                    if line.startswith("|") and token in line
                ]
                if len(hits) != 1 or shown not in hits[0]:
                    problems.append(f"README splits {shown} m from flat factor-0.1 Et/cont {token}")
                for name, body in (("preprint", preprint), ("decisions", decisions)):
                    start = body.find(token)
                    later = body.find(other, start + len(token)) if start >= 0 else -1
                    window = body[start:later] if later > start else body[start:start + 90]
                    if start < 0 or shown not in window:
                        problems.append(f"{name} splits {shown} m from flat factor-0.1 Et/cont {token}")

    if problems:
        print("\n".join(problems))
        return 1
    print("JOINT_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
