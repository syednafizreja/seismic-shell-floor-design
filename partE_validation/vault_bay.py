"""First vault-bay homogenisation, after the flat patch test in rung 1.

One bay, z = f sin(pi x / Lx) sin(pi y / Ly), C30/37, linear S8R. The flat plate of the
same plan and the same thickness is the reference. Hypothesis H1 says that plate is an
upper bound at equal volume. This bay has no ribs. A rise of zero must recover the flat
cell: that is the only pass/fail here. The curved rows are the record.

Author to confirm the sine surface and the rises (L/10 and L/5).
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    faceted_area, grid_on_surface, membrane_stiffness, shell_membrane_stiffness, sinusoid_bay)

E, NU, T = 33e9, 0.2, 0.06
OUT = Path(__file__).parent / "out" / "vault_bay.txt"


def props(A):
    Et = A[0, 0] - A[0, 1] ** 2 / A[1, 1]
    Gt = A[2, 2]
    return Et, Gt


def main():
    G = E / (2 * (1 + NU))
    Et_exact, Gt_exact = E * T, G * T
    lines = [
        "Vault bay, sinusoidal, linear S8R. Plan-projected membrane stiffness.",
        f"E = {E:.3g} Pa, nu = {NU}, reference thickness {T} m.",
        "rise 0 must match membrane_stiffness on the same plan (limit 0.1 %).",
        "case                         mesh   t[mm]  area/plan   Et/Et_flat   Gt/Gt_flat",
    ]
    flat = membrane_stiffness(3.0, 3.0, T, E, NU, nx=8, ny=8)
    Et_f, Gt_f = props(flat)
    zero, _ = shell_membrane_stiffness(3.0, 3.0, T, E, NU, 0.0, nx=8, ny=8)
    Et0, Gt0 = props(zero)
    e_et, e_gt = abs(Et0 / Et_f - 1), abs(Gt0 / Gt_f - 1)
    lines.append(f"square 3 m, rise 0            8x8   {T * 1e3:5.1f}  {1:8.4f}   {Et0 / Et_exact:8.5f}    {Gt0 / Gt_exact:8.5f}"
                 f"    vs flat cell {100 * e_et:.3e} % and {100 * e_gt:.3e} %")

    cases = [
        (3.0, 3.0, 0.30, 8, 8, False),
        (3.0, 3.0, 0.30, 16, 16, False),
        (3.0, 3.0, 0.30, 16, 16, True),
        (3.0, 3.0, 0.60, 4, 4, False),
        (3.0, 3.0, 0.60, 8, 8, False),
        (3.0, 3.0, 0.60, 8, 8, True),
        (3.0, 3.0, 0.60, 12, 12, False),
        (3.0, 3.0, 0.60, 16, 16, False),
        (3.0, 3.0, 0.60, 16, 16, True),
        (6.0, 3.0, 0.60, 8, 4, False),
        (6.0, 3.0, 0.60, 16, 8, False),
        (6.0, 3.0, 0.60, 16, 8, True),
    ]
    for lx, ly, rise, nx, ny, equal_volume in cases:
        xyz, els = grid_on_surface(lx, ly, nx, ny, sinusoid_bay(lx, ly, rise))
        area = faceted_area(xyz, els)
        plan = lx * ly
        t = T * plan / area if equal_volume else T
        A, area_t = shell_membrane_stiffness(lx, ly, t, E, NU, rise, nx=nx, ny=ny)
        Et, Gt = props(A)
        # Reference is the flat plate of thickness t, so equal thickness and equal volume
        # are both ratios to their own flat plate.
        tag = "equal V" if equal_volume else "equal t"
        lines.append(
            f"{lx:.0f}x{ly:.0f} m rise {rise:.2f} {tag:7s}  {nx}x{ny:<2d} {t * 1e3:5.1f}  "
            f"{area_t / plan:8.4f}   {Et / (E * t):8.5f}    {Gt / (G * t):8.5f}")
    lines.append("Et_flat = E t and Gt_flat = G t of a flat plate with the thickness in the row.")
    lines.append("area/plan is the faceted corner area of the mesh over the plan area.")
    lines.append("PASS" if max(e_et, e_gt) < 0.001 else "FAIL")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if max(e_et, e_gt) >= 0.001:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
