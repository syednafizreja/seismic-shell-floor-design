"""One orthogonal rib cross on the smooth vault bay.

The smooth bay is already in vault_bay.py. This file adds the first ribbed case of H1:
a cross through the crown, on the same sine surface. The shell between the ribs is 50 mm.
The rib thickness is set so the faceted volume equals a flat plate of 60 mm on the plan.
The mesh is 21 by 21 on the 3 m bay, so one element sits on each centreline.
That rib is 3/21 m wide (142.9 mm). A 150 mm rib would fall on a grid line.

Author to confirm the cross, the rib width and the 50 mm shell.

Ratios Et/(E T) and Gt/(G T) use T = 60 mm, the flat plate of equal volume.
The smooth rows also print Et/(E t*) so they can be set beside vault_bay.txt,
where t* is the uniform thickness of that row.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    element_areas, grid_on_surface, shell_membrane_stiffness, sinusoid_bay)

E, NU, T, T_SHELL, N = 33e9, 0.2, 0.06, 0.05, 21
OUT = Path(__file__).parent / "out" / "vault_rib.txt"


def props(A):
    Et = A[0, 0] - A[0, 1] ** 2 / A[1, 1]
    Gt = A[2, 2]
    return Et, Gt


def rib_thickness(xyz, els, lx, ly):
    """50 mm shell, rib thickness set to the volume of a 60 mm flat plate.

    An element is on the cross when its corner-average plan point is within
    half a rib width of either centreline. At this mesh that is one element.
    """
    areas = element_areas(xyz, els)
    rib = np.zeros(len(els), dtype=bool)
    half = 0.5 * lx / N
    for k, e in enumerate(els):
        c = xyz[np.asarray(e[:4]) - 1]
        cx, cy = float(c[:, 0].mean()), float(c[:, 1].mean())
        if min(abs(cx - lx / 2), abs(cy - ly / 2)) <= half + 1e-9:
            rib[k] = True
    if int(rib.sum()) != 2 * N - 1:
        raise RuntimeError(f"expected {2 * N - 1} rib elements, got {int(rib.sum())}")
    v_target = T * lx * ly
    a_rib, a_shell = float(areas[rib].sum()), float(areas[~rib].sum())
    t_rib = (v_target - T_SHELL * a_shell) / a_rib
    if t_rib <= T_SHELL:
        raise RuntimeError(f"rib thickness {t_rib:.4f} m is not above the shell")
    th = np.full(len(els), T_SHELL)
    th[rib] = t_rib
    if abs(float(th @ areas) - v_target) / v_target > 1e-8:
        raise RuntimeError("volume did not match the 60 mm plate")
    return th, t_rib, a_rib, a_shell


def row(name, mesh, t_shell, t_rib, area_plan, et, gt, et_same):
    same = f"{et_same:8.5f}" if et_same is not None else "       -"
    return (f"{name:28s} {mesh:7s} {t_shell:6.1f} {t_rib:6.1f} {area_plan:8.4f} "
            f"{et:8.5f} {gt:8.5f} {same}")


def main():
    G = E / (2 * (1 + NU))
    lines = [
        "Vault bay with one orthogonal rib cross. Linear S8R. Plan-projected membrane stiffness.",
        f"E = {E:.3g} Pa, nu = {NU}. Equal volume to a flat plate of T = {T} m.",
        f"Shell between ribs {T_SHELL} m. Rib width {3 / N:.6f} m, one element on a {N}x{N} mesh. Author to confirm.",
        "case                         mesh    t_sh   t_rib  area/plan   Et/ET    Gt/GT   Et/(E t*)",
        "Et/ET and Gt/GT use T = 60 mm. Et/(E t*) is only for a uniform shell, t* = T * plan / area.",
    ]
    cases = [(3.0, 0.0), (3.0, 0.30), (3.0, 0.60)]
    for lx, rise in cases:
        ly = lx
        nx = ny = N
        if abs(lx - 3.0) > 1e-9:
            raise RuntimeError("this mesh is for the 3 m bay")
        xyz, els = grid_on_surface(lx, ly, nx, ny, sinusoid_bay(lx, ly, rise))
        areas = element_areas(xyz, els)
        area = float(areas.sum())
        plan = lx * ly
        t_star = T * plan / area
        mesh = f"{nx}x{ny}"
        A_s, _ = shell_membrane_stiffness(lx, ly, t_star, E, NU, rise, nx=nx, ny=ny)
        Et_s, Gt_s = props(A_s)
        lines.append(row(
            f"smooth rise {rise:.2f} equal V", mesh, t_star * 1e3, t_star * 1e3,
            area / plan, Et_s / (E * T), Gt_s / (G * T), Et_s / (E * t_star)))
        th, t_rib, a_rib, a_shell = rib_thickness(xyz, els, lx, ly)
        A_r, area_r = shell_membrane_stiffness(
            lx, ly, T_SHELL, E, NU, rise, nx=nx, ny=ny, thickness=th)
        if abs(area_r - area) / area > 1e-9:
            raise RuntimeError("ribbed area does not match the smooth mesh")
        Et_r, Gt_r = props(A_r)
        lines.append(row(
            f"cross rise {rise:.2f} equal V", mesh, T_SHELL * 1e3, t_rib * 1e3,
            area / plan, Et_r / (E * T), Gt_r / (G * T), None))
        lines.append(
            f"  rib area {a_rib:.4f} m2, shell area {a_shell:.4f} m2, "
            f"volume {T * plan:.4f} m3, Et_cross/Et_smooth {Et_r / Et_s:.5f}, "
            f"Gt_cross/Gt_smooth {Gt_r / Gt_s:.5f}")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
