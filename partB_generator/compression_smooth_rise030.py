"""Membrane tension on the smooth rise 0.30 m bay under self-weight.

Uses the stress print already written for the rise 0.30 m ribs.
A principal value above zero is tension. The check is the shell-local
membrane, the average of the two faces. It does not rerun the bay and it
does not replace compression_smooth.txt.
Author to confirm the rise and this definition of compression-only.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import grid_on_surface, sinusoid_bay
from partB_generator import stress_rib as bay
from partB_generator.compression_smooth import principals

OUT = Path(__file__).parent / "out" / "compression_smooth_rise030.txt"
FIELD = Path(__file__).parent / "out" / "smooth_gravity_stress_030.dat"
# Field crown faces printed in stress_rib_rise030.txt. Not gravity_bay.txt.
FIELD_CROWN = (-5.014637e4, -2.806953e4)


def main():
    if not FIELD.is_file():
        raise RuntimeError(f"missing stress print {FIELD.name}")
    bay.DAT = FIELD
    bay.RISE = 0.30
    bay.CROWN_SXX = FIELD_CROWN
    xyz, els = grid_on_surface(bay.LX, bay.LX, bay.N, bay.N, sinusoid_bay(bay.LX, bay.LX, bay.RISE))
    text = FIELD.read_text(encoding="utf-8", errors="replace")
    marker = "stresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz)"
    body = text.split(marker, 1)[1]
    acc = {}
    for ln in body.splitlines():
        q = ln.split()
        if len(q) < 8:
            continue
        try:
            eid, ip = int(q[0]), int(q[1])
            vals = [float(v) for v in q[2:8]]
        except ValueError:
            continue
        acc.setdefault(eid, {})[ip] = vals
    _, _, suffix, crown_id, faces = bay.membrane_tensors(xyz, els)
    local = np.zeros((len(els), 3))
    for k, _ in enumerate(els):
        rows = [acc[k + 1][i] for i in range(1, 9)]
        mid = 0.5 * (np.mean(rows[:4], axis=0) + np.mean(rows[4:], axis=0))
        local[k] = (mid[0], mid[1], mid[3])
    lam1 = np.empty(len(els))
    lam2 = np.empty(len(els))
    for k, (sxx, syy, sxy) in enumerate(local):
        lam1[k], lam2[k] = principals(sxx, syy, sxy)
    tension = lam1 > 0.0
    both = lam2 > 0.0
    k_max = int(np.argmax(lam1))
    c = xyz[np.asarray(els[k_max][:4]) - 1]
    pitch = bay.LX / bay.N
    edge = 0
    further = []
    farthest = None
    for k in np.flatnonzero(tension):
        cc = xyz[np.asarray(els[k][:4]) - 1]
        x, y = float(cc[:, 0].mean()), float(cc[:, 1].mean())
        corners = ((0.0, 0.0), (0.0, bay.LX), (bay.LX, 0.0), (bay.LX, bay.LX))
        dist = min(float(np.hypot(x - cx, y - cy)) for cx, cy in corners)
        if farthest is None or dist > farthest[0]:
            farthest = (dist, x, y)
        if min(x, y, bay.LX - x, bay.LX - y) <= pitch + 1e-9:
            edge += 1
        else:
            further.append(f"x {x:.4f} m, y {y:.4f} m, {lam1[k]:.6e} Pa")
    lines = [
        "Rise 0.30 m. Same tension check. This file does not replace compression_smooth.txt.",
        "Shell-local membrane of the smooth rise 0.30 m bay under self-weight.",
        "Positive principal stress is tension. Average of the two faces.",
        f"Print suffix {suffix}. Crown element {crown_id}, faces {faces[0]:.6e} Pa and {faces[1]:.6e} Pa.",
        f"Elements {len(els)}. With a tensile principal {int(tension.sum())}.",
        f"With both principals tensile {int(both.sum())}.",
        f"Of the tensile elements, {edge} lie within one element pitch of the plan boundary.",
        "Further than one element pitch from the plan boundary: " + ("; ".join(further) if further else "none") + ".",
        f"Largest principal {lam1[k_max]:.6e} Pa at x {float(c[:, 0].mean()):.4f} m, y {float(c[:, 1].mean()):.4f} m.",
        f"Farthest tensile centroid from a plan corner {farthest[0]:.4f} m.",
        f"Smallest principal {float(lam2.min()):.6e} Pa.",
        "Author to confirm that a positive principal membrane stress is the tension check.",
        "No code limit is applied. The crown faces in this print are compression.",
    ]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
