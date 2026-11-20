"""Principal-stress ribs on the smooth rise 0.60 m bay.

The field is the gravity membrane stress already printed in
out/smooth_gravity_stress.dat. This script does not rewrite that file, and it
does not rerun the smooth bay. Ribs follow both principal families. The shell
between the ribs is 50 mm, and the rib thickness meets the volume of a flat
60 mm plate. A rib element is one whose plan centroid lies within half an
element pitch of a traced line.

Author to confirm the field, the shell axes, the scaled spacing and the width.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.append(r"C:\Users\ASUS\ComputationalEngineering\P2_ribs_vs_thickness\src")
from cecore.env import ccx_version
from cecore.tracer import trace_lines

from partA_mechanics.plate_fe import (
    element_areas, faceted_area, grid_on_surface, run_dat, shell_membrane_stiffness, sinusoid_bay)
from partE_validation.gravity_bay import deck, displacements, face_sxx, factors
from partE_validation.vault_rib import E, N, NU, T, T_SHELL, props

G = E / (2.0 * (1.0 + NU))
LX = 3.0
RISE = 0.60
# P2 layout C uses 1.5 m on a 12 m span, and drops a line within 0.5 m of the edge.
D_SEP = 1.5 * (LX / 12.0)
EDGE = 0.5 * (LX / 12.0)
DAT = Path(__file__).parent / "out" / "smooth_gravity_stress.dat"
OUT = Path(__file__).parent / "out" / "stress_rib.txt"
# Crown faces in gravity_bay.txt for the smooth rise 0.60 m bay.
CROWN_SXX = (-1.941393e4, -1.684599e4)


def shell_axes(x, y):
    """CalculiX default shell axes on z = rise * sin(pi x / L) * sin(pi y / L).

    Local x is the projection of global x onto the tangent plane. Local y is
    normal cross local x. The normal points to the positive z side.
    """
    zx = RISE * (np.pi / LX) * np.cos(np.pi * x / LX) * np.sin(np.pi * y / LX)
    zy = RISE * (np.pi / LX) * np.sin(np.pi * x / LX) * np.cos(np.pi * y / LX)
    normal = np.array([-zx, -zy, 1.0], float)
    normal /= np.linalg.norm(normal)
    ang = np.degrees(np.arccos(np.clip(abs(float(normal[0])), -1.0, 1.0)))
    src = np.array([1.0, 0.0, 0.0]) if ang >= 0.1 else np.array([0.0, 0.0, 1.0])
    local_x = src - np.dot(src, normal) * normal
    local_x /= np.linalg.norm(local_x)
    return local_x, np.cross(normal, local_x)


def membrane_tensors(xyz, els):
    """Plan xx, yy, xy of the shell-local membrane stress at each centroid."""
    text = DAT.read_text(encoding="utf-8", errors="replace")
    marker = "stresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz)"
    if marker not in text:
        raise RuntimeError("stress header is missing")
    body = text.split(marker, 1)[1]
    acc = {}
    suffix = None
    for ln in body.splitlines():
        q = ln.split()
        if len(q) < 8:
            continue
        try:
            eid, ip = int(q[0]), int(q[1])
            vals = [float(v) for v in q[2:8]]
        except ValueError:
            continue
        if suffix is None and len(q) > 8:
            suffix = q[8]
        acc.setdefault(eid, {})[ip] = vals
    if len(acc) != len(els):
        raise RuntimeError(f"stress file has {len(acc)} elements, mesh has {len(els)}")
    tensors = np.zeros((len(els), 2, 2))
    xy = np.zeros((len(els), 2))
    crown, bestd = 0, 1e9
    for k, e in enumerate(els):
        c = xyz[np.asarray(e[:4]) - 1]
        cx, cy = float(c[:, 0].mean()), float(c[:, 1].mean())
        xy[k] = (cx, cy)
        d = (cx - LX / 2) ** 2 + (cy - LX / 2) ** 2
        if d < bestd:
            crown, bestd = k, d
        rows = [acc[k + 1][i] for i in range(1, 9)]
        mid = 0.5 * (np.mean(rows[:4], axis=0) + np.mean(rows[4:], axis=0))
        local_x, local_y = shell_axes(cx, cy)
        full = (mid[0] * np.outer(local_x, local_x) + mid[1] * np.outer(local_y, local_y)
                + mid[3] * (np.outer(local_x, local_y) + np.outer(local_y, local_x)))
        tensors[k] = full[:2, :2]
    rows = [acc[crown + 1][i] for i in range(1, 9)]
    faces = (float(np.mean(rows[:4], axis=0)[0]), float(np.mean(rows[4:], axis=0)[0]))
    if max(abs(faces[0] - CROWN_SXX[0]), abs(faces[1] - CROWN_SXX[1])) > 1.0:
        raise RuntimeError(f"crown faces {faces} do not match gravity_bay.txt")
    return xy, tensors, suffix, crown + 1, faces


def symmetry_gap(xy, tensors):
    """Largest break of the square-bay mirror Txx(x, y) = Tyy(y, x)."""
    worst = 0.0
    for k, (x, y) in enumerate(xy):
        j = int(np.argmin((xy[:, 0] - y) ** 2 + (xy[:, 1] - x) ** 2))
        worst = max(worst, abs(float(tensors[k, 0, 0] - tensors[j, 1, 1])))
        worst = max(worst, abs(float(tensors[k, 0, 1] - tensors[j, 0, 1])))
    return worst


def traced_lines(xy, tensors):
    bounds = (0.0, LX, 0.0, LX)
    lines = []
    for fam in ("max", "min"):
        lines += trace_lines(
            xy, tensors, bounds, d_sep=D_SEP, which=fam, degenerate_tol=0.02,
            magnitude_tol=0.0, min_len_frac=1.5, symmetry="D4",
            step=0.02, ds_out=0.05, snap=0.075)
    kept = []
    for ln in lines:
        med = np.median(np.minimum.reduce([
            ln[:, 0], LX - ln[:, 0], ln[:, 1], LX - ln[:, 1]]))
        if med >= EDGE:
            kept.append(ln)
    if len(kept) < 2:
        raise RuntimeError(f"only {len(kept)} stress lines survived")
    return kept


def near_line(point, lines, half):
    for ln in lines:
        for a, b in zip(ln[:-1], ln[1:]):
            ab = b - a
            den = float(np.dot(ab, ab))
            if den == 0.0:
                dist = float(np.linalg.norm(point - a))
            else:
                t = min(1.0, max(0.0, float(np.dot(point - a, ab)) / den))
                dist = float(np.linalg.norm(point - (a + t * ab)))
            if dist <= half + 1e-9:
                return True
    return False


def rib_thickness(xyz, els, lines):
    areas = element_areas(xyz, els)
    half = 0.5 * LX / N
    rib = np.zeros(len(els), dtype=bool)
    for k, e in enumerate(els):
        c = xyz[np.asarray(e[:4]) - 1]
        if near_line(np.array([float(c[:, 0].mean()), float(c[:, 1].mean())]), lines, half):
            rib[k] = True
    if int(rib.sum()) < N:
        raise RuntimeError(f"stress-line strip has only {int(rib.sum())} elements")
    v_target = T * LX * LX
    t_rib = (v_target - T_SHELL * float(areas[~rib].sum())) / float(areas[rib].sum())
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
    xy, tensors, suffix, crown, faces = membrane_tensors(xyz, els)
    gap = symmetry_gap(xy, tensors)
    if gap > 1.0e3:
        raise RuntimeError(f"plan stress breaks the square symmetry by {gap:.3f} Pa")
    lines = traced_lines(xy, tensors)
    length = sum(float(np.sum(np.linalg.norm(np.diff(ln, axis=0), axis=1))) for ln in lines)
    th, t_rib, n_rib = rib_thickness(xyz, els, lines)
    A, area_r = shell_membrane_stiffness(
        LX, LX, T_SHELL, E, NU, RISE, nx=N, ny=N, thickness=th)
    if abs(area_r - area) / area > 1e-9:
        raise RuntimeError("rib area does not match the smooth mesh")
    Et, Gt = props(A)
    static, _ = deck(xyz, els, T_SHELL, th, buckle=False)
    text = run_dat(static)
    U = displacements(text, len(xyz))
    crown_node = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LX / 2)))
    w = U[:, 2]
    buck, _ = deck(xyz, els, T_SHELL, th, buckle=True)
    fac = factors(run_dat(buck))
    positive = [v for v in fac if v > 0]
    lam = positive[0] if positive else float("nan")
    top, bot = face_sxx(text)
    version = ccx_version()
    out = [
        "Principal-stress ribs on the sine bay. Linear S8R. Not the recorded cross.",
        f"Bay {LX} m, rise {RISE} m, mesh {N}x{N}. Shell {T_SHELL * 1e3:.0f} mm.",
        f"Solver {version}.",
        "Field: gravity membrane stress of the smooth equal-volume bay.",
        f"Print suffix {suffix}. Crown element {crown}, faces {faces[0]:.6e} Pa and {faces[1]:.6e} Pa.",
        f"Square-symmetry gap {gap:.3f} Pa.",
        f"Line spacing {D_SEP:.3f} m. Edge clearance {EDGE:.3f} m. Lines {len(lines)}. Plan length {length:.3f} m.",
        f"Rib elements {n_rib}. Rib thickness {t_rib * 1e3:.2f} mm. area/plan {area / LX / LX:.4f}.",
        "Author to confirm the gravity field, the shell axes, the scaled spacing and the half-pitch width.",
        "No knockdown is applied.",
        f"Et/(E T) {Et / (E * T):.5f}   Gt/(G T) {Gt / (G * T):.5f}",
        f"crown w {w[crown_node] * 1e3:.4f} mm, largest |w| {np.max(np.abs(w)) * 1e3:.4f} mm",
        f"lowest positive buckling factor on self-weight {lam:.6g}  factors {fac}",
        f"crown sxx, two faces {top:.6e} Pa and {bot:.6e} Pa. Negative is compression.",
        "H1 stays open. One stress-line layout is not the ribbed floor.",
    ]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
