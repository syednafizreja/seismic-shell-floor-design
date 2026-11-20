"""The generator's first check: the recorded 21x21 bay, rise 0.60 m.

Smooth shell and one orthogonal cross. The target lines are read from
partE_validation/out/vault_rib.txt. This script does not rewrite that file.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    element_areas, grid_on_surface, shell_membrane_stiffness, sinusoid_bay)
from partE_validation.vault_rib import E, NU, T, T_SHELL, N, props, rib_thickness

LX = 3.0
RISE = 0.60
RECORD = Path(__file__).resolve().parents[1] / "partE_validation" / "out" / "vault_rib.txt"
OUT = Path(__file__).parent / "out" / "reproduce_bay.txt"


def recorded(prefix):
    for ln in RECORD.read_text().splitlines():
        if ln.startswith(prefix):
            parts = ln.split()
            return float(parts[-3]), float(parts[-2])
    raise RuntimeError(f"no recorded row {prefix}")


def main():
    G = E / (2 * (1 + NU))
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, RISE))
    area = float(element_areas(xyz, els).sum())
    t_star = T * LX * LX / area
    A_s, _ = shell_membrane_stiffness(LX, LX, t_star, E, NU, RISE, nx=N, ny=N)
    Et_s, Gt_s = props(A_s)
    th, t_rib, _, _ = rib_thickness(xyz, els, LX, LX)
    A_r, _ = shell_membrane_stiffness(LX, LX, T_SHELL, E, NU, RISE, nx=N, ny=N, thickness=th)
    Et_r, Gt_r = props(A_r)
    got = {
        "smooth": (Et_s / (E * T), Gt_s / (G * T)),
        "cross": (Et_r / (E * T), Gt_r / (G * T)),
    }
    exp = {
        "smooth": recorded("smooth rise 0.60"),
        "cross": recorded("cross rise 0.60"),
    }
    lines = [
        "Generator check against partE_validation/out/vault_rib.txt.",
        f"Bay {LX} m, rise {RISE} m, mesh {N}x{N}. Equal volume to a {T * 1e3:.0f} mm plate.",
        f"case        Et/ET got   Et/ET file   Gt/GT got   Gt/GT file",
    ]
    worst = 0.0
    for name in ("smooth", "cross"):
        ge, gg = got[name]
        ee, eg = exp[name]
        worst = max(worst, abs(ge - ee), abs(gg - eg))
        lines.append(f"{name:10s}  {ge:8.5f}    {ee:8.5f}    {gg:8.5f}    {eg:8.5f}")
    lines.append(f"rib thickness {t_rib * 1e3:.2f} mm. Largest absolute difference {worst:.2e}.")
    ok = worst <= 5e-5
    lines.append("PASS" if ok else "FAIL")
    lines.append("H1 stays open. This check is the recorded cross, not a new layout.")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
