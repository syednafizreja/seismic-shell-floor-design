"""Rung 4 deflection on the recorded 21x21 mesh at rise 0.60 m.

Same supports, line load and Timoshenko formula as rung4_storey.py. The smooth
shell is the control. The cross is the recorded one. This file does not
replace rung4_storey.txt. The 38.4 m floor is not in this check.
Author to confirm the cross on this check.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    element_areas, faceted_area, grid_on_surface, shell_membrane_stiffness, sinusoid_bay, solve)
from partA_mechanics.reduced import timoshenko_midspan
from partE_validation.vault_rib import E, NU, T, T_SHELL, props, rib_thickness

LX = LY = 3.0
N = 21
RISE = 0.60
Q = 10e3
# Printed ratios in vault_rib.txt. Each run must match its row before the beam is compared.
RECORDED = {"smooth": (0.40763, 0.46892), "cross": (0.38984, 0.45189)}
OUT = Path(__file__).parent / "out" / "rung4_cross.txt"


def beam(xyz, els, t, volume, thickness):
    tol = 1e-9 * LX
    bcs = []
    for i, (x, y, _) in enumerate(xyz):
        if min(x, y, LX - x, LY - y) < tol:
            bcs.append((i + 1, 3, 0.0))
        if x < tol or x > LX - tol:
            bcs.append((i + 1, 2, 0.0))
        if x < tol and abs(y - LY / 2) < 0.5 * LY / N:
            bcs.append((i + 1, 1, 0.0))
    rho = 1000.0
    g = Q * LX / (rho * volume)
    U, _ = solve(
        xyz, els, t, E, NU, bcs, rho=rho, grav=-g, lock_w="boundary", thickness=thickness)
    mid = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LY / 2)))
    return -float(U[mid, 1])


def one(name, thickness, recorded):
    xyz, els = grid_on_surface(LX, LY, N, N, sinusoid_bay(LX, LY, RISE))
    areas = element_areas(xyz, els)
    volume = float(np.asarray(thickness) @ areas) if np.ndim(thickness) else float(thickness) * float(areas.sum())
    if abs(volume - T * LX * LY) / (T * LX * LY) > 1e-6:
        raise RuntimeError(f"{name} volume does not match the 60 mm plate")
    t_section = T_SHELL if np.ndim(thickness) else float(thickness)
    A, area_r = shell_membrane_stiffness(
        LX, LY, t_section, E, NU, RISE, nx=N, ny=N,
        thickness=thickness if np.ndim(thickness) else None)
    if abs(area_r - float(areas.sum())) / float(areas.sum()) > 1e-9:
        raise RuntimeError(f"{name} area does not match the mesh")
    Et, Gt = props(A)
    G = E / (2 * (1 + NU))
    ratios = (round(Et / (E * T), 5), round(Gt / (G * T), 5))
    if ratios != recorded:
        raise RuntimeError(f"{name} stiffness {ratios} does not match vault_rib.txt {recorded}")
    d_fe = beam(xyz, els, t_section, volume, thickness if np.ndim(thickness) else None)
    d_t = timoshenko_midspan(LX, LY, Et, Gt, Q)
    err = d_fe / d_t - 1
    return Et / (E * T), Gt / (G * T), d_fe, d_t, err


def main():
    xyz, els = grid_on_surface(LX, LY, N, N, sinusoid_bay(LX, LY, RISE))
    t_star = T * LX * LY / faceted_area(xyz, els)
    th, t_rib, _, _ = rib_thickness(xyz, els, LX, LY)
    smooth = one("smooth", t_star, RECORDED["smooth"])
    cross = one("cross", th, RECORDED["cross"])
    lines = [
        "Rung 4 deflection on the recorded 21x21 mesh. This file does not replace rung4_storey.txt.",
        f"Bay {LX} m square, rise {RISE} m, mesh {N}x{N}, q = {Q:.3g} N/m. Limit 5 % from the brief.",
        "The in-plane load totals q L. Vertical displacement is held on the plan boundary.",
        f"Smooth shell {t_star * 1e3:.2f} mm. Cross shell {T_SHELL * 1e3:.1f} mm, rib {t_rib * 1e3:.2f} mm, one element wide.",
        "case        Et/(E T)  Gt/(G T)    FE mm   Timoshenko mm    error",
    ]
    for name, row in (("smooth", smooth), ("cross", cross)):
        et, gt, d_fe, d_t, err = row
        lines.append(
            f"{name:10s}  {et:8.5f}  {gt:8.5f}  {d_fe * 1e3:8.5f}  {d_t * 1e3:8.5f}  {100 * err:+7.2f} %  "
            f"{'PASS' if abs(err) < 0.05 else 'FAIL'}")
    lines.append("The 12x12 smooth bay stays +15.80 % in rung4_storey.txt. The 38.4 m floor is not in this check.")
    lines.append("Author to confirm the cross on this check.")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
