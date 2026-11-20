"""Rung 4, deflection only: shell deep beam against the Timoshenko model of its own Et, Gt.

The brief asks for one storey, reduced model against the full shell, deflection
within 5%. This is that comparison on the 3 m bay, not on the 38.4 m floor.
The period half of rung 4 is not run: both models would use the same mass, and
the stiffness ratio is the deflection ratio.

The vault is held vertically on its plan boundary. The in-plane supports and the
line load are those of rung 2. Author to confirm using the 3 m bay as the storey.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    faceted_area, grid_on_surface, shell_membrane_stiffness, sinusoid_bay, solve)
from partA_mechanics.reduced import timoshenko_midspan

E, NU, T, Q = 33e9, 0.2, 0.06, 10e3
LX = LY = 3.0
N = 12
OUT = Path(__file__).parent / "out" / "rung4_storey.txt"


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
    # g is set from the faceted area so the total in-plane force is q * L, the Timoshenko load.
    g = Q * LX / (rho * t * area)
    U, _ = solve(xyz, els, t, E, NU, bcs, rho=rho, grav=-g, lock_w="boundary")
    mid = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LY / 2)))
    return -float(U[mid, 1])


def main():
    lines = [
        "Rung 4 deflection: shell deep beam against Timoshenko using Et, Gt of the same mesh.",
        f"Bay {LX} m square, mesh {N}x{N}, q = {Q:.3g} N/m. Limit 5 % from the brief.",
        "case                         t mm    Et/ET    Gt/GT     FE mm    Timoshenko mm    error",
    ]
    G = E / (2 * (1 + NU))
    worst = 0.0
    for rise, name in ((0.0, "flat"), (0.60, "smooth rise 0.60 equal V")):
        xyz, els = grid_on_surface(LX, LY, N, N, sinusoid_bay(LX, LY, rise))
        t = T * LX * LY / faceted_area(xyz, els)
        A, _ = shell_membrane_stiffness(LX, LY, t, E, NU, rise, nx=N, ny=N)
        Et = A[0, 0] - A[0, 1] ** 2 / A[1, 1]
        Gt = A[2, 2]
        d_fe = shell_deep(rise, t, faceted_area(xyz, els))
        d_t = timoshenko_midspan(LX, LY, Et, Gt, Q)
        err = d_fe / d_t - 1
        worst = max(worst, abs(err))
        lines.append(
            f"{name:28s} {t * 1e3:6.1f}  {Et / (E * T):7.5f}  {Gt / (G * T):7.5f}  "
            f"{d_fe * 1e3:8.5f}  {d_t * 1e3:8.5f}  {100 * err:+7.2f} %")
    lines.append(f"worst |error| {100 * worst:.2f} %  ->  "
                 f"{'PASS' if worst < 0.05 else 'FAIL'} (limit 5 %)")
    lines.append("The cross is not in this check. The 38.4 m floor is not in this check.")
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
