"""Rung 4 on the recorded layouts that are not already in rung4_cross.txt.

Same supports, line load and Timoshenko formula. Mesh 21x21. Each stiffness
must match the printed row before the beam is compared. This file does not
replace rung4_storey.txt or rung4_cross.txt.
Author to confirm these layouts on this check.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    element_areas, faceted_area, grid_on_surface, shell_membrane_stiffness, sinusoid_bay)
from partA_mechanics.reduced import timoshenko_midspan
from partB_generator.diagonal_bay import diagonal_thickness
from partB_generator import stress_rib as bay
from partE_validation.rung4_cross import E, LX, LY, N, NU, Q, T_SHELL, beam
from partE_validation.vault_rib import T, props, rib_thickness

OUT = Path(__file__).parent / "out" / "rung4_layouts.txt"
DAT60 = Path(__file__).parent.parent / "partB_generator" / "out" / "smooth_gravity_stress.dat"
DAT30 = Path(__file__).parent.parent / "partB_generator" / "out" / "smooth_gravity_stress_030.dat"
G = E / (2.0 * (1.0 + NU))


def mesh(rise):
    return grid_on_surface(LX, LY, N, N, sinusoid_bay(LX, LY, rise))


def smooth_thickness(rise):
    xyz, els = mesh(rise)
    t_star = T * LX * LY / faceted_area(xyz, els)
    return xyz, els, np.full(len(els), t_star), t_star, 0


def cross_thickness(rise):
    xyz, els = mesh(rise)
    th, t_rib, _, _ = rib_thickness(xyz, els, LX, LY)
    return xyz, els, th, t_rib, int(np.count_nonzero(th > T_SHELL + 1e-9))


def diagonal(rise):
    xyz, els = mesh(rise)
    th, t_rib, n_rib = diagonal_thickness(xyz, els, LX)
    return xyz, els, th, t_rib, n_rib


def stress(rise, d_sep, dat, field):
    if not dat.is_file():
        raise RuntimeError(f"missing {dat.name}")
    bay.RISE = rise
    bay.D_SEP = d_sep
    bay.DAT = dat
    bay.CROWN_SXX = field
    xyz, els = mesh(rise)
    xy, tensors, _, _, _ = bay.membrane_tensors(xyz, els)
    lines = bay.traced_lines(xy, tensors)
    th, t_rib, n_rib = bay.rib_thickness(xyz, els, lines)
    return xyz, els, th, t_rib, n_rib


CASES = (
    ("smooth rise 0.30", 0.30, (0.46875, 0.65578), None, lambda: smooth_thickness(0.30)),
    ("cross rise 0.30", 0.30, (0.43480, 0.60185), 41, lambda: cross_thickness(0.30)),
    ("diagonals rise 0.60", 0.60, (0.39834, 0.47168), 41, lambda: diagonal(0.60)),
    ("diagonals rise 0.30", 0.30, (0.44408, 0.65435), 41, lambda: diagonal(0.30)),
    ("stress 0.60 s0.375", 0.60, (0.40744, 0.46840), 236,
     lambda: stress(0.60, 0.375, DAT60, (-1.941393e4, -1.684599e4))),
    ("stress 0.60 s0.75", 0.60, (0.41394, 0.46365), 128,
     lambda: stress(0.60, 0.75, DAT60, (-1.941393e4, -1.684599e4))),
    ("stress 0.30 s0.375", 0.30, (0.46328, 0.64944), 232,
     lambda: stress(0.30, 0.375, DAT30, (-5.014637e4, -2.806953e4))),
)


def run_case(name, rise, recorded, n_expect, build):
    xyz, els, th, t_ref, n_rib = build()
    if n_expect is not None and n_rib != n_expect:
        raise RuntimeError(f"{name} has {n_rib} rib elements, record is {n_expect}")
    areas = element_areas(xyz, els)
    volume = float(th @ areas)
    if abs(volume - T * LX * LY) / (T * LX * LY) > 1e-6:
        raise RuntimeError(f"{name} volume does not match the 60 mm plate")
    varied = float(np.max(th) - np.min(th)) > 1e-9
    A, area_r = shell_membrane_stiffness(
        LX, LY, T_SHELL if varied else float(th[0]), E, NU, rise, nx=N, ny=N,
        thickness=th if varied else None)
    if abs(area_r - float(areas.sum())) / float(areas.sum()) > 1e-9:
        raise RuntimeError(f"{name} area does not match the mesh")
    Et, Gt = props(A)
    ratios = (round(Et / (E * T), 5), round(Gt / (G * T), 5))
    if ratios != recorded:
        raise RuntimeError(f"{name} stiffness {ratios} does not match the record {recorded}")
    d_fe = beam(xyz, els, float(th[0]), volume, th if varied else None)
    d_t = timoshenko_midspan(LX, LY, Et, Gt, Q)
    err = d_fe / d_t - 1.0
    return (
        f"{name:22s} {t_ref * 1e3:7.2f} {n_rib:4d}  {ratios[0]:8.5f}  {ratios[1]:8.5f}  "
        f"{d_fe * 1e3:8.5f}  {d_t * 1e3:8.5f}  {100 * err:+7.2f} %  "
        f"{'PASS' if abs(err) < 0.05 else 'FAIL'}"
    )


def main():
    OUT.parent.mkdir(exist_ok=True)
    header = [
        "Rung 4 on the other recorded 21x21 layouts. This file does not replace rung4_storey.txt or rung4_cross.txt.",
        f"Bay {LX} m square, mesh {N}x{N}, q = {Q:.3g} N/m. Limit 5 % from the brief.",
        "The in-plane load totals q L. Vertical displacement is held on the plan boundary.",
        "The rise 0.60 m smooth shell and the cross are in rung4_cross.txt.",
        "case                     t mm  ribs  Et/(E T)  Gt/(G T)    FE mm   Timoshenko mm    error",
    ]
    done = []
    for name, rise, recorded, n_expect, build in CASES:
        try:
            line = run_case(name, rise, recorded, n_expect, build)
        except Exception as exc:
            line = f"{name:22s}  ERROR  {exc}"
        done.append(line)
        OUT.write_text("\n".join(header + done) + "\n", encoding="utf-8")
        print(line, flush=True)
    print("LAYOUTS_DONE", flush=True)


if __name__ == "__main__":
    main()
