"""Two diagonal ribs on the recorded sine bay. A new layout, not a rerun of the cross.

The shell between the ribs is 50 mm. The rib thickness meets the volume of a
flat 60 mm plate. A rib element is one whose corner-average lies within half
an element pitch of either diagonal, measured square to that diagonal.
Author to confirm the diagonals, the width and the 50 mm shell.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    element_areas, faceted_area, grid_on_surface, run_dat, shell_membrane_stiffness, sinusoid_bay)
from partE_validation.gravity_bay import deck, displacements, face_sxx, factors
from partE_validation.vault_rib import E, N, NU, T, T_SHELL, props

# G is not exported by vault_rib. Compute it here.
G = E / (2 * (1 + NU))
LX = 3.0
RISE = 0.60
OUT = Path(__file__).parent / "out" / "diagonal_bay.txt"


def diagonal_thickness(xyz, els, lx):
    areas = element_areas(xyz, els)
    half = 0.5 * lx / N
    rib = np.zeros(len(els), dtype=bool)
    for k, e in enumerate(els):
        c = xyz[np.asarray(e[:4]) - 1]
        cx, cy = float(c[:, 0].mean()), float(c[:, 1].mean())
        d1 = abs(cx - cy) / np.sqrt(2.0)
        d2 = abs(cx + cy - lx) / np.sqrt(2.0)
        if min(d1, d2) <= half + 1e-9:
            rib[k] = True
    if int(rib.sum()) < N:
        raise RuntimeError(f"diagonal strip has only {int(rib.sum())} elements")
    v_target = T * lx * lx
    a_rib, a_shell = float(areas[rib].sum()), float(areas[~rib].sum())
    t_rib = (v_target - T_SHELL * a_shell) / a_rib
    if t_rib <= T_SHELL:
        raise RuntimeError(f"rib thickness {t_rib:.4f} m is not above the shell")
    th = np.full(len(els), T_SHELL)
    th[rib] = t_rib
    if abs(float(th @ areas) - v_target) / v_target > 1e-6:
        raise RuntimeError("volume did not match the 60 mm plate")
    return th, t_rib, int(rib.sum())


def main():
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, RISE))
    area = faceted_area(xyz, els)
    th, t_rib, n_rib = diagonal_thickness(xyz, els, LX)
    A, area_r = shell_membrane_stiffness(
        LX, LX, T_SHELL, E, NU, RISE, nx=N, ny=N, thickness=th)
    if abs(area_r - area) / area > 1e-9:
        raise RuntimeError("diagonal area does not match the smooth mesh")
    Et, Gt = props(A)
    static, _ = deck(xyz, els, T_SHELL, th, buckle=False)
    text = run_dat(static)
    U = displacements(text, len(xyz))
    crown = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LX / 2)))
    w = U[:, 2]
    buck, _ = deck(xyz, els, T_SHELL, th, buckle=True)
    fac = factors(run_dat(buck))
    positive = [v for v in fac if v > 0]
    lam = positive[0] if positive else float("nan")
    top, bot = face_sxx(text)
    lines = [
        "Two diagonals on the sine bay. Linear S8R. Not the recorded cross.",
        f"Bay {LX} m, rise {RISE} m, mesh {N}x{N}. Shell {T_SHELL * 1e3:.0f} mm.",
        f"Rib elements {n_rib}. Rib thickness {t_rib * 1e3:.2f} mm. area/plan {area / LX / LX:.4f}.",
        "Author to confirm the diagonals, the half-pitch width and the 50 mm shell.",
        "No knockdown is applied.",
        f"Et/(E T) {Et / (E * T):.5f}   Gt/(G T) {Gt / (G * T):.5f}",
        f"crown w {w[crown] * 1e3:.4f} mm, largest |w| {np.max(np.abs(w)) * 1e3:.4f} mm",
        f"lowest positive buckling factor on self-weight {lam:.6g}  factors {fac}",
        f"crown sxx, two faces {top:.6e} Pa and {bot:.6e} Pa. Negative is compression.",
        "H1 stays open. One diagonal pair is not the ribbed floor.",
    ]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
