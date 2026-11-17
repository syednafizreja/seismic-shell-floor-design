"""In-plane analysis of flat floor plates with CalculiX S8R shells (Part A, mechanics core).

A structured grid of 8-node quadrilaterals covers the rectangle [0, Lx] x [0, Ly] in the
x-y plane. Out-of-plane displacement is held at zero, so the shell works as a membrane:
the in-plane stiffness that the diaphragm check needs. Units: N, m, Pa.

Two uses:
- ``membrane_stiffness``: unit-cell homogenisation. Three affine strain states imposed on the
  whole boundary give the membrane stiffness matrix A (N/m), from which (E t)_eq and (G t)_eq.
- ``deep_beam``: a simply supported floor strip loaded in its own plane, for the Timoshenko check.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from cecore.env import run_ccx


def grid_q8(lx: float, ly: float, nx: int, ny: int):
    """Structured S8R mesh. Returns node coordinates (n x 3, node i has id i+1) and
    element connectivity (corners counter-clockwise, then mid-sides), 1-based."""
    gx, gy = 2 * nx + 1, 2 * ny + 1
    xs, ys = np.linspace(0, lx, gx), np.linspace(0, ly, gy)
    nid = -np.ones((gx, gy), int)
    xyz = []
    for i in range(gx):
        for j in range(gy):
            if i % 2 and j % 2:          # cell centres are not nodes of an 8-node element
                continue
            nid[i, j] = len(xyz) + 1
            xyz.append((xs[i], ys[j], 0.0))
    els = []
    for a in range(nx):
        for b in range(ny):
            i, j = 2 * a, 2 * b
            els.append((nid[i, j], nid[i + 2, j], nid[i + 2, j + 2], nid[i, j + 2],
                        nid[i + 1, j], nid[i + 2, j + 1], nid[i + 1, j + 2], nid[i, j + 1]))
    return np.array(xyz), np.array(els)


def _deck(xyz, els, t, E, nu, rho, bcs, loads, grav=None) -> str:
    out = ["*NODE"] + [f"{i + 1}, {x:.12g}, {y:.12g}, {z:.12g}" for i, (x, y, z) in enumerate(xyz)]
    out += ["*ELEMENT, TYPE=S8R, ELSET=EALL"] + [f"{k + 1}, " + ", ".join(map(str, e)) for k, e in enumerate(els)]
    out += ["*NSET, NSET=NALL, GENERATE", f"1, {len(xyz)}, 1",
            "*MATERIAL, NAME=C", "*ELASTIC", f"{E:.9g}, {nu:.6g}", "*DENSITY", f"{rho:.6g}",
            "*SHELL SECTION, ELSET=EALL, MATERIAL=C", f"{t:.9g}",
            "*BOUNDARY", "NALL, 3, 3, 0."]                  # membrane: no out-of-plane motion
    out += ["*STEP", "*STATIC", "*BOUNDARY"] + [f"{n}, {d}, {d}, {v:.12g}" for n, d, v in bcs]
    if loads:
        out += ["*CLOAD"] + [f"{n}, {d}, {v:.12g}" for n, d, v in loads]
    if grav is not None:
        out += ["*DLOAD", f"EALL, GRAV, {abs(grav):.9g}, 0., {np.sign(grav):.0f}, 0."]
    out += ["*NODE PRINT, NSET=NALL", "U, RF", "*END STEP"]
    return "\n".join(out) + "\n"


def _read_dat(path: Path, n: int):
    """Displacements and reaction forces of all n nodes from a CalculiX .dat file."""
    U, RF, cur = np.zeros((n, 3)), np.zeros((n, 3)), None
    for ln in path.read_text().splitlines():
        s = ln.strip().lower()
        if s.startswith("displacements"):
            cur = U
        elif s.startswith("forces"):
            cur = RF
        elif cur is not None and s:
            p = s.split()
            try:
                cur[int(p[0]) - 1] = [float(v) for v in p[1:4]]
            except (ValueError, IndexError):
                pass
    return U, RF


def solve(xyz, els, t, E, nu, bcs, loads=(), rho=0.0, grav=None):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "job.inp").write_text(_deck(xyz, els, t, E, nu, rho, bcs, loads, grav))
        r = run_ccx("job", d, threads=2)
        if not (d / "job.dat").exists():
            raise RuntimeError("ccx failed:\n" + r.stdout[-2000:])
        return _read_dat(d / "job.dat", len(xyz))


def membrane_stiffness(lx, ly, t, E, nu, nx=8, ny=8):
    """Membrane stiffness A (3x3, Voigt order xx, yy, xy with engineering shear) of a plate cell.

    Each column comes from one affine state u = eps . x imposed on every boundary node; the
    stress resultants are the boundary reactions divided by the edge length (virtual work)."""
    xyz, els = grid_q8(lx, ly, nx, ny)
    tol = 1e-9 * max(lx, ly)
    bnd = [i for i, (x, y, _) in enumerate(xyz) if min(x, y, lx - x, ly - y) < tol]
    A = np.zeros((3, 3))
    for k, e in enumerate(np.eye(3) * 1e-4):
        exx, eyy, gxy = e
        bcs = []
        for i in bnd:
            x, y, _ = xyz[i]
            bcs += [(i + 1, 1, exx * x + 0.5 * gxy * y), (i + 1, 2, eyy * y + 0.5 * gxy * x)]
        _, RF = solve(xyz, els, t, E, nu, bcs)
        # average resultants from the work of the reactions: N . eps * area = sum RF . u
        R = RF[bnd, :2]
        P = xyz[bnd, :2]
        Sxx = np.sum(R[:, 0] * P[:, 0]) / (lx * ly)
        Syy = np.sum(R[:, 1] * P[:, 1]) / (lx * ly)
        Sxy = np.sum(R[:, 0] * P[:, 1] + R[:, 1] * P[:, 0]) / (2 * lx * ly)
        A[:, k] = np.array([Sxx, Syy, Sxy]) / e[k]
    return A


def deep_beam(L, D, t, E, nu, q, nx=40, ny=12):
    """Simply supported in-plane beam (span L along x, depth D along y) under a uniform line
    load q (N/m) applied as a body force through the depth. Supports: v = 0 over the full depth
    at both ends, u = 0 at mid-depth of the left end. Returns the mid-span deflection of the
    mid-depth node (m, positive down)."""
    xyz, els = grid_q8(L, D, nx, ny)
    tol = 1e-9 * L
    bcs = []
    for i, (x, y, _) in enumerate(xyz):
        if x < tol or x > L - tol:
            bcs.append((i + 1, 2, 0.0))
        if x < tol and abs(y - D / 2) < tol:
            bcs.append((i + 1, 1, 0.0))
    rho = 1000.0
    g = q / (rho * t * D)              # body acceleration that gives line load q
    U, _ = solve(xyz, els, t, E, nu, bcs, rho=rho, grav=-g)
    mid = int(np.argmin(np.hypot(xyz[:, 0] - L / 2, xyz[:, 1] - D / 2)))
    return -U[mid, 1]
