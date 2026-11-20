"""Reduced diaphragm: Timoshenko stiffness, and an X-strut grid calibrated to it.

The shell cell supplies Et and Gt (N/m). The deep-beam stiffness is

    d = 5 q L^4 / (384 Et D^3/12) + q L^2 / (8 k Gt D),   k = 5/6
    K_d = q L / d

which is the flat-plate formula of rung 2 with E t and G t replaced by the cell result.
Rung 2 is the check for a flat plate. The X-strut grid is the fast model: chord and
diagonal areas are fixed on one panel so that the panel matches Et and Gt, and the
deep-beam deflection of that grid is then compared with the shell. That deflection
is not used in the calibration.

Author to confirm k = 5/6 for a shell diaphragm. It is the value already used in rung 2.
"""
from __future__ import annotations

import numpy as np

from partA_mechanics.plate_fe import _read_dat_text, run_dat

K_SHEAR = 5.0 / 6.0


def timoshenko_midspan(L: float, D: float, Et: float, Gt: float, q: float, k: float = K_SHEAR) -> float:
    """Simply-supported mid-span deflection (m) of a diaphragm of depth D and span L."""
    if min(L, D, Et, Gt, k) <= 0:
        raise ValueError("L, D, Et, Gt and k must be positive")
    bend = 5 * q * L ** 4 / (384 * Et * D ** 3 / 12)
    shear = q * L ** 2 / (8 * k * Gt * D)
    return bend + shear


def kd_timoshenko(L: float, D: float, Et: float, Gt: float, k: float = K_SHEAR) -> float:
    """K_d = (q L) / d (N/m). Independent of q."""
    d = timoshenko_midspan(L, D, Et, Gt, q=1.0, k=k)
    return L / d


def _panel_nodes(a: float, b: float):
    xyz = np.array([[0.0, 0.0, 0.0], [a, 0.0, 0.0], [a, b, 0.0], [0.0, b, 0.0]])
    return xyz


def _truss_dat(xyz, bars, areas, bcs, loads=()) -> str:
    """T3D2 truss. areas[i] is the cross-section of bars[i]. Modulus is 1, so area stands for EA."""
    out = ["*NODE"] + [f"{i + 1}, {x:.12g}, {y:.12g}, {z:.12g}" for i, (x, y, z) in enumerate(xyz)]
    out += ["*NSET, NSET=NALL, GENERATE", f"1, {len(xyz)}, 1"]
    out += ["*ELEMENT, TYPE=T3D2, ELSET=ALL"]
    out += [f"{k + 1}, {n1 + 1}, {n2 + 1}" for k, (n1, n2) in enumerate(bars)]
    groups: dict[float, list[int]] = {}
    order: list[float] = []
    for k, area in enumerate(areas):
        key = float(f"{area:.9g}")
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(k + 1)
    for i, key in enumerate(order):
        name = f"A{i}"
        out.append(f"*ELSET, ELSET={name}")
        ids = groups[key]
        for s in range(0, len(ids), 16):
            out.append(", ".join(str(n) for n in ids[s:s + 16]))
        out += ["*SOLID SECTION, ELSET=" + name + ", MATERIAL=S", f"{key:.9g}"]
    out += ["*MATERIAL, NAME=S", "*ELASTIC", "1, 0", "*BOUNDARY"]
    out += [f"{n}, {d}, {d}, {v:.12g}" for n, d, v in bcs]
    # Truss nodes have no rotational stiffness. Hold every node out of plane.
    out += [f"{i + 1}, 3, 3, 0." for i in range(len(xyz))]
    out += ["*STEP", "*STATIC"]
    if loads:
        out += ["*CLOAD"] + [f"{n}, {d}, {v:.12g}" for n, d, v in loads]
    out += ["*NODE PRINT, NSET=NALL", "U, RF", "*END STEP"]
    return "\n".join(out) + "\n"


def _bars_of_panel():
    chords = [(0, 1), (1, 2), (2, 3), (3, 0)]
    diags = [(0, 2), (1, 3)]
    return chords, diags


def panel_Et_Gt(a: float, b: float, ea_chord: float, ea_diag: float) -> tuple[float, float]:
    """Plan Et and Gt (N/m) of one X panel, from the same virtual-work strains as the shell cell."""
    xyz = _panel_nodes(a, b)
    chords, diags = _bars_of_panel()
    bars = chords + diags
    areas = [ea_chord] * len(chords) + [ea_diag] * len(diags)
    Et = Gt = None
    for kind, exx, eyy, gxy in (("E", 1e-4, 0.0, 0.0), ("G", 0.0, 0.0, 1e-4)):
        bcs = []
        for i, (x, y, _) in enumerate(xyz):
            bcs += [(i + 1, 1, exx * x + 0.5 * gxy * y), (i + 1, 2, eyy * y + 0.5 * gxy * x)]
        text = run_dat(_truss_dat(xyz, bars, areas, bcs))
        _, RF = _read_dat_text(text, len(xyz))
        if kind == "E":
            Et = float(np.sum(RF[:, 0] * xyz[:, 0]) / (a * b) / exx)
        else:
            Gt = float(np.sum(RF[:, 0] * xyz[:, 1] + RF[:, 1] * xyz[:, 0]) / (2 * a * b) / gxy)
    return Et, Gt


def calibrate_panel(a: float, b: float, Et: float, Gt: float) -> tuple[float, float]:
    """EA of each chord and each diagonal so the panel matches Et and Gt.

    Linear shear does not stretch the chords, so the diagonal is fixed from Gt alone.
    The chords then make up the part of Et that the diagonals do not already provide.
    """
    # One run with unit diagonal and no chord stiffness, for both resultants.
    # A zero-area section is rejected by CalculiX, so the chord area is a trace
    # and its contribution is removed by a second unit-chord run.
    et_d, gt_d = panel_Et_Gt(a, b, ea_chord=1e-12, ea_diag=1.0)
    et_c, gt_c = panel_Et_Gt(a, b, ea_chord=1.0, ea_diag=1e-12)
    if abs(gt_c) > 1e-6 * abs(gt_d):
        raise RuntimeError(f"chords contributed to linear shear ({gt_c}), the split is wrong")
    ea_diag = Gt / gt_d
    ea_chord = (Et - ea_diag * et_d) / et_c
    if ea_chord <= 0 or ea_diag <= 0:
        raise RuntimeError(f"calibration gave EA chord {ea_chord}, diagonal {ea_diag}")
    return ea_chord, ea_diag


def xstrut_deep_beam(L: float, D: float, ea_chord: float, ea_diag: float, q: float,
                     panel: float = 1.0) -> float:
    """Mid-span, mid-depth deflection of an X-strut grid under the rung-2 line load.

    Panel size is the calibration panel. End nodes are held in v; one corner is held in u.
    The load q (N/m of span) is spread over the plan as q/D.
    """
    if abs(L / panel - round(L / panel)) > 1e-8 or abs(D / panel - round(D / panel)) > 1e-8:
        raise ValueError("span and depth must be whole panels")
    nx, ny = int(round(L / panel)), int(round(D / panel))
    xs = np.linspace(0, L, nx + 1)
    ys = np.linspace(0, D, ny + 1)
    xyz = np.array([(x, y, 0.0) for x in xs for y in ys])

    def nid(i, j):
        return i * (ny + 1) + j

    bars, areas = [], []
    for i in range(nx):
        for j in range(ny):
            c00, c10 = nid(i, j), nid(i + 1, j)
            c11, c01 = nid(i + 1, j + 1), nid(i, j + 1)
            for bar in ((c00, c10), (c10, c11), (c11, c01), (c01, c00)):
                bars.append(bar)
                areas.append(ea_chord)
            for bar in ((c00, c11), (c10, c01)):
                bars.append(bar)
                areas.append(ea_diag)
    # Shared edges were added twice. Merge by keeping one of each undirected bar.
    # A shared edge is the chord of two panels, so its area is the sum.
    # A diagonal belongs to one panel. An outer chord belongs to one panel.
    merged: dict[tuple[int, int], float] = {}
    for (n1, n2), area in zip(bars, areas):
        key = (n1, n2) if n1 < n2 else (n2, n1)
        merged[key] = merged.get(key, 0.0) + area
    bars = list(merged)
    areas = [merged[b] for b in bars]

    tol = 1e-9 * L
    bcs = []
    for i, (x, y, _) in enumerate(xyz):
        if x < tol or x > L - tol:
            bcs.append((i + 1, 2, 0.0))
        if x < tol and y < tol:
            bcs.append((i + 1, 1, 0.0))
    # Loads go in the same deck. Rebuild with CLOAD.
    p = q / D
    loads = []
    for i in range(nx + 1):
        ax = panel * (0.5 if i in (0, nx) else 1.0)
        for j in range(ny + 1):
            ay = panel * (0.5 if j in (0, ny) else 1.0)
            loads.append((nid(i, j) + 1, 2, -p * ax * ay))
    U, _ = _read_dat_text(run_dat(_truss_dat(xyz, bars, areas, bcs, loads)), len(xyz))
    mid = int(np.argmin(np.hypot(xyz[:, 0] - L / 2, xyz[:, 1] - D / 2)))
    return -float(U[mid, 1])


def beam_on_springs(bay_lengths, D, Et, Gt, Kf, q: float = 1.0, n_per_bay: int = 16,
                    k: float = K_SHEAR):
    """In-plane Timoshenko beam on lateral springs, one spring per frame line.

    Kf is one stiffness or a list with one value per frame (len(bay_lengths) + 1).
    Returns x, lateral displacement u, and the rigid-diaphragm displacement.
    """
    spans = [float(s) for s in bay_lengths]
    n_frame = len(spans) + 1
    if np.isscalar(Kf):
        kf = np.full(n_frame, float(Kf))
    else:
        kf = np.asarray(Kf, float)
        if len(kf) != n_frame:
            raise ValueError("Kf must have one value per frame line")
    EI = Et * D ** 3 / 12.0
    kGA = k * Gt * D
    # Nodes
    xs = [0.0]
    for span in spans:
        h = span / n_per_bay
        origin = xs[-1]
        xs.extend(origin + h * (i + 1) for i in range(n_per_bay))
    x = np.array(xs, float)
    n = len(x)
    ndof = 2 * n
    K = np.zeros((ndof, ndof))
    F = np.zeros(ndof)
    for e in range(n - 1):
        Le = x[e + 1] - x[e]
        phi = 12 * EI / (kGA * Le ** 2)
        c = EI / (Le ** 3 * (1 + phi))
        L2 = Le ** 2
        ke = c * np.array([
            [12, 6 * Le, -12, 6 * Le],
            [6 * Le, (4 + phi) * L2, -6 * Le, (2 - phi) * L2],
            [-12, -6 * Le, 12, -6 * Le],
            [6 * Le, (2 - phi) * L2, -6 * Le, (4 + phi) * L2],
        ])
        # lumped transverse load; checked against the closed Timoshenko formula
        fe = np.array([q * Le / 2, 0.0, q * Le / 2, 0.0])
        dof = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        for a in range(4):
            F[dof[a]] += fe[a]
            for b in range(4):
                K[dof[a], dof[b]] += ke[a, b]
    tol = 1e-6 * float(np.sum(spans))
    positions = np.cumsum([0.0, *spans])
    for s, px in enumerate(positions):
        i = int(np.argmin(np.abs(x - px)))
        if abs(x[i] - px) > tol:
            raise RuntimeError("frame line is not on a node")
        K[2 * i, 2 * i] += kf[s]
    u = np.linalg.solve(K, F)
    lateral = u[0::2]
    total = q * float(np.sum(spans))
    u_rigid = total / float(np.sum(kf))
    return x, lateral, u_rigid


def displacement_excess(lateral, u_rigid) -> float:
    """Largest (u - u_rigid) / |u_rigid|. EN 1998-1 4.3.1(4) NOTE uses 10% of this ratio.

    The clause text is the author's copy, BS EN 1998-1:2004, PDF page 55, printed page 53.
    Author to confirm the sentence against that page.
    """
    return float(np.max((lateral - u_rigid) / abs(u_rigid)))
