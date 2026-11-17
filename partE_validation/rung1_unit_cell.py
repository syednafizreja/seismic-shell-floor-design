"""Validation rung 1 (brief Part E): flat-plate unit cell against the exact membrane stiffness.

A flat isotropic plate has A11 = A22 = E t / (1 - nu^2), A12 = nu A11 and A66 = G t, so
(E t)_eq = A11 - A12^2 / A22 = E t exactly. The homogenisation in ``plate_fe.membrane_stiffness``
must return these to under 1 % (pass mark from the brief) before it is used on vault bays.
Cells: square and 2:1 bays, two meshes, C30/37 concrete (E = 33 GPa, nu = 0.2), t = 60 mm.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import membrane_stiffness

E, NU, T = 33e9, 0.2, 0.06
OUT = Path(__file__).parent / "out" / "rung1_unit_cell.txt"


def main():
    G = E / (2 * (1 + NU))
    exact = {"Et": E * T, "Gt": G * T, "nu": NU}
    rows, worst = [], 0.0
    for lx, ly in [(3.0, 3.0), (6.0, 3.0)]:
        for n in (2, 8):
            A = membrane_stiffness(lx, ly, T, E, NU, nx=n, ny=n)
            got = {"Et": A[0, 0] - A[0, 1] ** 2 / A[1, 1], "Gt": A[2, 2], "nu": A[0, 1] / A[1, 1]}
            err = {k: abs(got[k] / exact[k] - 1) for k in exact}
            worst = max(worst, *err.values())
            rows.append(f"{lx:4.1f} x {ly:3.1f}  {n:2d}x{n:<2d}  " + "  ".join(
                f"{k} {got[k]:.6e} ({100 * err[k]:.2e} %)" for k in exact))
    head = [f"Rung 1: flat-plate unit cell, E = {E:.3g} Pa, nu = {NU}, t = {T} m",
            f"exact: Et = {exact['Et']:.6e} N/m, Gt = {exact['Gt']:.6e} N/m, nu = {NU}",
            "cell [m]   mesh    results (relative error)"]
    tail = [f"worst relative error {100 * worst:.2e} %  ->  {'PASS' if worst < 0.01 else 'FAIL'} (limit 1 %)"]
    OUT.write_text("\n".join(head + rows + tail) + "\n")
    print("\n".join(head + rows + tail))


if __name__ == "__main__":
    main()
