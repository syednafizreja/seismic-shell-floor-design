"""Gravity on the recorded 3 m bay: deflection and linear buckling.

Plan-boundary translations are fixed and rotations are free, so the edge is pinned.
Author to confirm that support. Density 2500 kg/m3. Author to confirm.

The linear buckling factor multiplies self-weight. No imperfection and no
knockdown are applied: the brief names a knockdown and does not give its value.
A solver factor is not a design load.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import (
    _shell_sections, faceted_area, grid_on_surface, run_dat, sinusoid_bay)
from vault_rib import N, T, T_SHELL, rib_thickness

E, NU, RHO, G = 33e9, 0.2, 2500.0, 9.81
LX = 3.0
OUT = Path(__file__).parent / "out" / "gravity_bay.txt"


def on_boundary(x, y, lx, ly):
    tol = 1e-9 * max(lx, ly)
    return min(x, y, lx - x, ly - y) < tol


def deck(xyz, els, t, thickness, buckle: bool) -> str:
    out = ["*NODE"] + [f"{i + 1}, {x:.12g}, {y:.12g}, {z:.12g}" for i, (x, y, z) in enumerate(xyz)]
    out += ["*ELEMENT, TYPE=S8R, ELSET=EALL"]
    out += [f"{k + 1}, " + ", ".join(map(str, e)) for k, e in enumerate(els)]
    out += ["*NSET, NSET=NALL, GENERATE", f"1, {len(xyz)}, 1",
            "*MATERIAL, NAME=C", "*ELASTIC", f"{E:.9g}, {NU}", "*DENSITY", f"{RHO:.6g}"]
    if thickness is None:
        out += _shell_sections(els, t, None)
    else:
        out += _shell_sections(els, t, thickness)
    bcs = []
    for i, (x, y, _) in enumerate(xyz):
        if on_boundary(x, y, LX, LX):
            bcs += [f"{i + 1}, 1, 3, 0."]
    out += ["*BOUNDARY"] + bcs
    if buckle:
        out += ["*STEP", "*BUCKLE", "4", "*DLOAD",
                f"EALL, GRAV, {G:.6g}, 0., 0., -1.",
                "*NODE FILE", "U", "*END STEP"]
    else:
        crown = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LX / 2)))
        # Crown element: the one whose corner-average is closest to the centre.
        best, bestd = 0, 1e9
        for k, e in enumerate(els):
            c = xyz[np.asarray(e[:4]) - 1]
            d = (c[:, 0].mean() - LX / 2) ** 2 + (c[:, 1].mean() - LX / 2) ** 2
            if d < bestd:
                best, bestd = k, d
        out += ["*ELSET, ELSET=CROWN", str(best + 1)]
        out += ["*STEP", "*STATIC", "*DLOAD",
                f"EALL, GRAV, {G:.6g}, 0., 0., -1.",
                "*NODE PRINT, NSET=NALL", "U",
                "*EL PRINT, ELSET=CROWN", "S",
                "*END STEP"]
    return "\n".join(out) + "\n", crown if not buckle else None


def displacements(text, n):
    """First displacement table only. Later stress rows are not node results."""
    U = np.zeros((n, 3))
    seen = False
    for ln in text.splitlines():
        s = ln.strip().lower()
        if s.startswith("displacements"):
            seen = True
            continue
        if not seen:
            continue
        p = ln.split()
        if len(p) >= 4:
            try:
                nid = int(p[0])
                if 1 <= nid <= n:
                    U[nid - 1] = [float(p[1]), float(p[2]), float(p[3])]
                    continue
            except ValueError:
                pass
        if seen and np.any(U):
            break
    return U


def factors(text):
    """Buckling factors. CalculiX prints the heading with a space between capitals."""
    if "buckl" not in text.lower().replace(" ", ""):
        return []
    vals = []
    for ln in text.splitlines():
        p = ln.split()
        if len(p) != 2:
            continue
        try:
            mode = int(p[0])
            val = float(p[1])
        except ValueError:
            continue
        if mode == len(vals) + 1:
            vals.append(val)
    return vals


def face_sxx(text):
    """Mean sxx on the first four integration points, and on the next four."""
    sxx = []
    for ln in text.splitlines():
        if "stress" in ln.lower():
            sxx = []
            continue
        p = ln.split()
        if len(p) < 3:
            continue
        try:
            int(p[0])
            int(p[1])
            sxx.append(float(p[2]))
        except ValueError:
            if sxx:
                break
    if len(sxx) < 8:
        return float("nan"), float("nan")
    return float(np.mean(sxx[:4])), float(np.mean(sxx[4:8]))


def one(name, rise, rib):
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, rise))
    area = faceted_area(xyz, els)
    if rib:
        th, t_rib, _, _ = rib_thickness(xyz, els, LX, LX)
        t = T_SHELL
    else:
        t = T * LX * LX / area
        th = None
        t_rib = t
    static, _ = deck(xyz, els, t, th, buckle=False)
    text = run_dat(static)
    U = displacements(text, len(xyz))
    crown = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LX / 2)))
    w = U[:, 2]
    buck, _ = deck(xyz, els, t, th, buckle=True)
    btext = run_dat(buck)
    fac = factors(btext)
    positive = [v for v in fac if v > 0]
    lam = positive[0] if positive else float("nan")
    top, bot = face_sxx(text)
    return [
        f"{name}",
        f"  thickness shell {t * 1e3:.2f} mm, rib {t_rib * 1e3:.2f} mm, area/plan {area / LX / LX:.4f}",
        f"  crown w {w[crown] * 1e3:.4f} mm, largest |w| {np.max(np.abs(w)) * 1e3:.4f} mm, "
        f"crown |w|/span {abs(w[crown]) / LX:.6e}",
        f"  lowest positive buckling factor on self-weight {lam:.6g}  factors {fac}",
        f"  crown sxx, two faces {top:.6e} Pa and {bot:.6e} Pa. Negative is compression.",
    ]


def main():
    lines = [
        "Gravity on the 3 m bay. Boundary translations fixed, rotations free. rho = 2500 kg/m3, g = 9.81 m/s2.",
        "Author to confirm the support and the density. No knockdown is applied.",
        f"Mesh {N}x{N}, the rib mesh. Linear S8R.",
    ]
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, 0.0))
    # Flat plate, uniform 60 mm. Rise 0.60 smooth, equal volume. Rise 0.60 with the cross.
    lines += one("flat, rise 0, 60 mm", 0.0, rib=False)
    lines += one("smooth, rise 0.60 m, equal volume", 0.60, rib=False)
    lines += one("cross, rise 0.60 m, equal volume", 0.60, rib=True)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
