"""Diagnostic for the rung-4 vault miss. Does not replace rung4_storey.txt.

The recorded check holds the vertical displacement only on the plan boundary.
The Timoshenko beam has no vertical freedom. This run holds every node at z = 0,
which is the flat-plate membrane case, and prints the bending and shear parts
of the beam formula. One change from the recorded check: lock_w = all.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    faceted_area, grid_on_surface, shell_membrane_stiffness, sinusoid_bay, solve)
from partA_mechanics.reduced import K_SHEAR, timoshenko_midspan

E, NU, T, Q = 33e9, 0.2, 0.06, 10e3
LX = LY = 3.0
N = 12
OUT = Path(__file__).parent / "out" / "rung4_wlock.txt"


def shell_deep(rise, t, area):
    xyz, els = grid_on_surface(LX, LY, N, N, sinusoid_bay(LX, LY, rise))
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
    g = Q * LX / (rho * t * area)
    U, _ = solve(xyz, els, t, E, NU, bcs, rho=rho, grav=-g, lock_w="all")
    mid = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LY / 2)))
    return -float(U[mid, 1])


def main():
    lines = [
        "Rung 4 diagnostic: same load and mesh as rung4_storey.txt, but w = 0 on every node.",
        "The recorded file keeps w free in the interior. This file does not replace it.",
        f"Bay {LX} m square, mesh {N}x{N}, q = {Q:.3g} N/m. k = {K_SHEAR:.6g}.",
        "case                         t mm    Et/ET    Gt/GT     FE mm    Timoshenko mm    error   bend share",
    ]
    G = E / (2 * (1 + NU))
    worst = 0.0
    for rise, name in ((0.0, "flat, w locked"), (0.60, "rise 0.60, w locked")):
        xyz, els = grid_on_surface(LX, LY, N, N, sinusoid_bay(LX, LY, rise))
        area = faceted_area(xyz, els)
        t = T * LX * LY / area
        A, _ = shell_membrane_stiffness(LX, LY, t, E, NU, rise, nx=N, ny=N)
        Et = A[0, 0] - A[0, 1] ** 2 / A[1, 1]
        Gt = A[2, 2]
        bend = 5 * Q * LX ** 4 / (384 * Et * LY ** 3 / 12)
        shear = Q * LX ** 2 / (8 * K_SHEAR * Gt * LY)
        d_t = timoshenko_midspan(LX, LY, Et, Gt, Q)
        if abs(d_t - (bend + shear)) / d_t > 1e-9:
            raise RuntimeError("bending plus shear does not match timoshenko_midspan")
        d_fe = shell_deep(rise, t, area)
        err = d_fe / d_t - 1
        worst = max(worst, abs(err))
        lines.append(
            f"{name:28s} {t * 1e3:6.1f}  {Et / (E * T):7.5f}  {Gt / (G * T):7.5f}  "
            f"{d_fe * 1e3:8.5f}  {d_t * 1e3:8.5f}  {100 * err:+7.2f} %  {bend / d_t:6.3f}")
    lines.append(f"worst |error| {100 * worst:.2f} %  ->  "
                 f"{'PASS' if worst < 0.05 else 'FAIL'} (limit 5 %)")
    lines.append("Bend share is the bending term over the Timoshenko total. Shear is the rest.")
    lines.append("Author to confirm k = 5/6, and that locking w is the right comparison for the beam.")
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
