"""Check the printed beam arithmetic against the Timoshenko formula.

Reads rung 1, rung 2, the rung-4 files and the X-strut file. Does not call
CalculiX and does not write them.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from partA_mechanics.reduced import K_SHEAR, timoshenko_midspan
from partE_validation.vault_rib import E, NU, T

OUT = Path(__file__).parent / "out"
LX = LY = 3.0
Q = 10e3
G = E / (2.0 * (1.0 + NU))
MM = 1e-3
# Printed Timoshenko values are millimetres to five decimal places.
TIMO_TOL_M = 5.1e-9

ERR = re.compile(r"([+-]\d+\.\d+)\s+%")
FLOAT = re.compile(r"\d+\.\d+")


def rows(path: Path):
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        err = ERR.search(line)
        if not err:
            continue
        nums = FLOAT.findall(line[: err.start()])
        if len(nums) < 4:
            continue
        et, gt, fe, timo = nums[-4:]
        found.append({
            "name": line[: err.start()].split()[0] if line.split() else path.name,
            "et": et, "gt": gt, "fe": fe, "timo": timo, "err": err.group(1),
        })
    if not found:
        raise RuntimeError(f"no rung-4 rows in {path.name}")
    return found


def check(path: Path):
    problems = []
    for row in rows(path):
        et = float(row["et"]) * E * T
        gt = float(row["gt"]) * G * T
        formula = timoshenko_midspan(LX, LY, et, gt, Q)
        printed = float(row["timo"]) * MM
        if abs(formula - printed) > TIMO_TOL_M:
            problems.append(
                f"{path.name} {row['name'].strip()}: formula {formula / MM:.5f} mm, "
                f"file {row['timo']} mm"
            )
        fe = float(row["fe"]) * MM
        err = 100.0 * (fe / printed - 1.0)
        # The printed percent uses the unrounded deflections. A reader has only
        # the five-decimal millimetre values, so the recomputed percent can move
        # by a few hundredths.
        if abs(err - float(row["err"])) > 0.08:
            problems.append(
                f"{path.name} {row['name'].strip()}: error {err:+.2f} %, file {row['err']} %"
            )
    return problems


def check_xstrut():
    text = (OUT / "xstrut_check.txt").read_text(encoding="utf-8")
    et = E * T
    gt = G * T
    problems = []
    target = re.search(r"target Et ([0-9.e+]+) N/m, Gt ([0-9.e+]+) N/m", text)
    if abs(float(target.group(1)) - et) / et > 1e-9 or abs(float(target.group(2)) - gt) / gt > 1e-9:
        problems.append("xstrut target Et or Gt does not match E t and G t")
    header = re.search(r"shell mid-span (\d+\.\d+) mm, Timoshenko (\d+\.\d+) mm", text)
    shell = float(header.group(1)) * MM
    printed = float(header.group(2)) * MM
    formula = timoshenko_midspan(12.0, 6.0, et, gt, Q)
    if abs(formula - printed) > TIMO_TOL_M:
        problems.append(f"xstrut Timoshenko {formula / MM:.5f} mm, file {header.group(2)} mm")
    checked = 0
    for line in text.splitlines():
        err = re.search(r"([+-]\d+\.\d+)\s+%", line)
        if not err:
            continue
        nums = re.findall(r"[+-]?\d+\.\d+(?:e[+-]\d+)?", line[: err.start()])
        if len(nums) < 5:
            continue
        dx = float(nums[-1])
        got = 100.0 * (dx * MM / shell - 1.0)
        if abs(got - float(err.group(1))) > 0.08:
            problems.append(f"xstrut error {got:+.2f} %, file {err.group(1)} %")
        checked += 1
    if checked != 2:
        problems.append(f"xstrut rows {checked}, record has 2")
    return problems


def check_rung2():
    text = (OUT / "rung2_deep_beam.txt").read_text(encoding="utf-8")
    et, gt = E * T, G * T
    depth = 6.0
    problems = []
    rows = re.findall(
        r"L/D\s+(\d+)\s+FE\s+(\d+\.\d+) mm \(coarse\s+\d+\.\d+\)\s+"
        r"Timoshenko\s+(\d+\.\d+) \(\s*([+-]\d+\.\d+) %\)\s+shear share\s+(\d+\.\d+)%",
        text,
    )
    if len(rows) != 5:
        problems.append(f"rung 2 rows {len(rows)}, record has 5")
    for ratio, fe, timo, err, share in rows:
        length = int(ratio) * depth
        formula = timoshenko_midspan(length, depth, et, gt, Q)
        if abs(formula - float(timo) * MM) > TIMO_TOL_M:
            problems.append(f"rung 2 L/D {ratio}: formula {formula / MM:.5f} mm, file {timo} mm")
        bend = 5 * Q * length ** 4 / (384 * et * depth ** 3 / 12)
        shear = Q * length ** 2 / (8 * K_SHEAR * gt * depth)
        if abs(100.0 * shear / formula - float(share)) > 0.05:
            problems.append(f"rung 2 L/D {ratio}: shear share {100.0 * shear / formula:.1f} %, file {share} %")
        got = 100.0 * (float(fe) / float(timo) - 1.0)
        if abs(got - float(err)) > 0.08:
            problems.append(f"rung 2 L/D {ratio}: error {got:+.2f} %, file {err} %")
    return problems


def check_rung1():
    text = (OUT / "rung1_unit_cell.txt").read_text(encoding="utf-8")
    match = re.search(r"exact: Et = ([0-9.e+]+) N/m, Gt = ([0-9.e+]+) N/m, nu = ([0-9.]+)", text)
    problems = []
    if not match:
        return ["rung 1 has no exact Et, Gt line"]
    if abs(float(match.group(1)) - E * T) / (E * T) > 1e-9:
        problems.append("rung 1 Et is not E t")
    if abs(float(match.group(2)) - G * T) / (G * T) > 1e-9:
        problems.append("rung 1 Gt is not G t")
    if abs(float(match.group(3)) - NU) > 1e-12:
        problems.append("rung 1 nu is not 0.2")
    return problems


def main():
    problems = []
    expected = {"rung4_layouts.txt": 7, "rung4_cross.txt": 2, "rung4_storey.txt": 2}
    for name, n in expected.items():
        got = rows(OUT / name)
        if len(got) != n:
            problems.append(f"{name}: {len(got)} rows, record has {n}")
        problems.extend(check(OUT / name))
    problems.extend(check_xstrut())
    problems.extend(check_rung2())
    problems.extend(check_rung1())
    if problems:
        print("\n".join(problems))
        return 1
    print("RUNG4_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
