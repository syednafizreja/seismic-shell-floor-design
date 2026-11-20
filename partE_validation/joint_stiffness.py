"""Joint-stiffness factor on one centreline strip.

The factor multiplies the modulus of the elements on the centreline, x = L/2.
Factor 1 is the continuous floor. The strip is one element wide, so its width
is the element width. Two odd meshes are reported because that width changes.
Author to confirm the strip, and that a modulus factor is the joint model.

The vault row is the equal-volume smooth bay, rise 0.60 m, not the rib cross.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    faceted_area, grid_on_surface, membrane_stiffness, shell_membrane_stiffness, sinusoid_bay)

E, NU, T = 33e9, 0.2, 0.06
LX = LY = 3.0
FACTORS = (1.0, 0.5, 0.2, 0.1)
OUT = Path(__file__).parent / "out" / "joint_stiffness.txt"


def centre_modulus(nx, ny, factor):
    """Element order is a (x) outer, b (y) inner, as in grid_q8. Odd nx only."""
    if nx % 2 == 0 or ny % 2 == 0:
        raise RuntimeError("an even mesh puts the centreline on a node line")
    em = np.full(nx * ny, E)
    em.reshape(nx, ny)[nx // 2, :] = factor * E
    return em


def props(A):
    Et = A[0, 0] - A[0, 1] ** 2 / A[1, 1]
    return Et, A[2, 2]


def main():
    lines = [
        "Joint strip: modulus factor on the centreline column of elements.",
        f"E = {E:.3g} Pa, nu = {NU}. Bay {LX} m square. Factor 1 is the continuous floor.",
        "Author to confirm the strip and the factor.",
        "case                         mesh   width m   factor     Et/E60     Gt/G60    Et/cont   Gt/cont",
    ]
    G = E / (2 * (1 + NU))
    ref_et, ref_gt = E * T, G * T
    for nx in (9, 15):
        width = LX / nx
        base = None
        for factor in FACTORS:
            em = centre_modulus(nx, nx, factor)
            A = membrane_stiffness(LX, LY, T, E, NU, nx=nx, ny=nx, modulus=em)
            et, gt = props(A)
            if factor == 1.0:
                base = (et, gt)
            lines.append(
                f"{'flat 60 mm':28s} {nx:2d}x{nx:<2d}  {width:7.4f}  {factor:6.2f}  "
                f"{et / ref_et:9.5f}  {gt / ref_gt:9.5f}  {et / base[0]:8.5f}  {gt / base[1]:8.5f}")
        xyz, els = grid_on_surface(LX, LY, nx, nx, sinusoid_bay(LX, LY, 0.60))
        t_star = T * LX * LY / faceted_area(xyz, els)
        base = None
        for factor in FACTORS:
            em = centre_modulus(nx, nx, factor)
            A, _ = shell_membrane_stiffness(
                LX, LY, t_star, E, NU, 0.60, nx=nx, ny=nx, modulus=em)
            et, gt = props(A)
            if factor == 1.0:
                base = (et, gt)
            lines.append(
                f"{'vault rise 0.60 equal V':28s} {nx:2d}x{nx:<2d}  {width:7.4f}  {factor:6.2f}  "
                f"{et / ref_et:9.5f}  {gt / ref_gt:9.5f}  {et / base[0]:8.5f}  {gt / base[1]:8.5f}")
        lines.append(f"equal-volume thickness on the {nx}x{nx} vault: {t_star * 1e3:.2f} mm")
    lines.append("Et/E60 and Gt/G60 use the flat 60 mm plate. Et/cont is the same row at factor 1.")
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
