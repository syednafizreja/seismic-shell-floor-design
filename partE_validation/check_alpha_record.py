"""Recompute the printed alpha and alpha* from the printed frame stiffness.

Uses the Timoshenko beam on springs. Does not call OpenSees, and does not
write alpha_star.txt. The three K_f values stay the ones in that file.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

from partE_validation.alpha_star import (
    BAYS, DEPTH, E_FLOOR, NU, T, alpha_of, beam_element_check, excess, find_star,
    recorded_rows)

OUT = Path(__file__).parent / "out" / "alpha_star.txt"
KF = re.compile(r"K_f ground storey h=4\.55 m, beam I factor 2\.0: ([0-9.e+]+) N/m")
KF_EDGE = re.compile(r"K_f same storey, beam I factor 1\.5: ([0-9.e+]+) N/m")
STAR = re.compile(r"^(\S.*?)\s{2,}(\d+\.\d+)\s+(\d+\.\d+)\s*$")
CELL = re.compile(
    r"^(\S.*?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$"
)


def main():
    text = OUT.read_text(encoding="utf-8")
    k_mid = float(KF.search(text).group(1))
    k_edge = float(KF_EDGE.search(text).group(1))
    problems = []

    err, star2, got2 = beam_element_check()
    if abs(100.0 * err - (-0.003)) > 0.0006:
        problems.append(f"beam element {100.0 * err:+.3f} %, file -0.003 %")
    if abs(star2 - 19.9956) > 0.00015:
        problems.append(f"two-frame alpha* {star2:.4f}, file 19.9956")
    if abs(got2 - 0.1000) > 0.00015:
        problems.append(f"two-frame excess {got2:.4f}, file 0.1000")

    et0 = E_FLOOR * T
    gt0 = et0 / (2.0 * (1.0 + NU))
    kf_equal = np.full(len(BAYS) + 1, k_mid)
    kf_edge = np.array([k_edge, *([k_mid] * 5), k_edge])
    head, _, cell_text = text.partition("recorded cells")
    stars = []
    for line in head.splitlines():
        match = STAR.match(line)
        if match:
            stars.append((match.group(1).strip(), float(match.group(2)), float(match.group(3))))
    expected_names = (
        "anchor bays", "bays x 0.5", "bays x 2", "anchor, edge frames softer",
        "equal", "equal", "equal", "equal",
    )
    if [name for name, _, _ in stars] != list(expected_names):
        problems.append("alpha* rows are not the eight recorded layouts")
    cases = []
    for scale in (1.0, 0.5, 2.0):
        spans = tuple(s * scale for s in BAYS)
        cases.append((spans, kf_equal, max(spans)))
    cases.append((BAYS, kf_edge, max(BAYS)))
    for ratio in (0.3, 0.5, 1.0, 2.0):
        length = ratio * DEPTH
        cases.append(((length,) * 6, kf_equal, length))
    for (name, ld, printed), (spans, kf, lref) in zip(stars, cases):
        star, _ = find_star(spans, DEPTH, et0, gt0, kf, lref, k_mid)
        if abs(lref / DEPTH - ld) > 0.0006:
            problems.append(f"{name}: L/D {lref / DEPTH:.3f}, file {ld:.3f}")
        if abs(star - printed) > 0.0006:
            problems.append(f"{name}: alpha* {star:.3f}, file {printed:.3f}")

    cells = []
    for line in cell_text.splitlines():
        match = CELL.match(line)
        if match:
            cells.append(match.groups())
    if len(cells) != 6:
        problems.append(f"{len(cells)} cell rows, record has 6")
    rib = recorded_rows()
    for (label, et_r, gt_r, *_), (rib_label, rib_et, rib_gt) in zip(cells, rib):
        if label.strip() != rib_label or abs(float(et_r) - rib_et) > 1e-9 or abs(float(gt_r) - rib_gt) > 1e-9:
            problems.append(f"{label.strip()} does not match vault_rib.txt")
    for label, et_r, gt_r, alpha, ex, alpha_c, ex_c in cells:
        et, gt = float(et_r) * et0, float(gt_r) * gt0
        a = alpha_of(max(BAYS), DEPTH, et, gt, k_mid)
        r = excess(BAYS, DEPTH, et, gt, kf_equal)
        ac = alpha_of(max(BAYS), DEPTH, 0.5 * et, 0.5 * gt, k_mid)
        rc = excess(BAYS, DEPTH, 0.5 * et, 0.5 * gt, kf_equal)
        if abs(a - float(alpha)) > 0.006:
            problems.append(f"{label}: alpha {a:.2f}, file {alpha}")
        if abs(r - float(ex)) > 0.00006:
            problems.append(f"{label}: excess {r:.4f}, file {ex}")
        if abs(ac - float(alpha_c)) > 0.006:
            problems.append(f"{label}: cracked alpha {ac:.2f}, file {alpha_c}")
        if abs(rc - float(ex_c)) > 0.00006:
            problems.append(f"{label}: cracked excess {rc:.4f}, file {ex_c}")

    if problems:
        print("\n".join(problems))
        return 1
    print("ALPHA_RECORD_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
