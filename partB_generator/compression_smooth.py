"""Membrane tension on the smooth rise 0.60 m bay under self-weight.

Uses the stress print already written for the rib layout. A principal value
above zero is tension. The check is the shell-local membrane, the average of
the two faces. It does not apply a code limit and it does not rerun the bay.
Author to confirm this definition of compression-only.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import grid_on_surface, sinusoid_bay
from partB_generator.stress_rib import DAT, LX, N, RISE, membrane_tensors

OUT = Path(__file__).parent / "out" / "compression_smooth.txt"


def principals(sxx, syy, sxy):
    half = 0.5 * (sxx - syy)
    root = np.sqrt(half * half + sxy * sxy)
    mid = 0.5 * (sxx + syy)
    return mid + root, mid - root


def local_membrane(xyz, els):
    """Shell-local sxx, syy, sxy after averaging the two faces."""
    text = DAT.read_text(encoding="utf-8", errors="replace")
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
    membrane_tensors(xyz, els)
    local = np.zeros((len(els), 3))
    for k, _ in enumerate(els):
        rows = [acc[k + 1][i] for i in range(1, 9)]
        mid = 0.5 * (np.mean(rows[:4], axis=0) + np.mean(rows[4:], axis=0))
        local[k] = (mid[0], mid[1], mid[3])
    return local


def main():
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, RISE))
    local = local_membrane(xyz, els)
    lam1 = np.empty(len(els))
    lam2 = np.empty(len(els))
    for k, (sxx, syy, sxy) in enumerate(local):
        lam1[k], lam2[k] = principals(sxx, syy, sxy)
    tension = lam1 > 0.0
    both = lam2 > 0.0
    k_max = int(np.argmax(lam1))
    c = xyz[np.asarray(els[k_max][:4]) - 1]
    pitch = LX / N
    edge = 0
    interior = []
    for k in np.flatnonzero(tension):
        cc = xyz[np.asarray(els[k][:4]) - 1]
        x, y = float(cc[:, 0].mean()), float(cc[:, 1].mean())
        if min(x, y, LX - x, LX - y) <= pitch + 1e-9:
            edge += 1
        else:
            interior.append(f"x {x:.4f} m, y {y:.4f} m, {lam1[k]:.6e} Pa")
    lines = [
        "Shell-local membrane of the smooth rise 0.60 m bay under self-weight.",
        "Positive principal stress is tension. Average of the two faces.",
        f"Elements {len(els)}. With a tensile principal {int(tension.sum())}.",
        f"With both principals tensile {int(both.sum())}.",
        f"Of the tensile elements, {edge} lie within one element pitch of the plan boundary.",
        "One element further in, still at the four corners: " + ("; ".join(interior) if interior else "none") + ".",
        f"Largest principal {lam1[k_max]:.6e} Pa at x {float(c[:, 0].mean()):.4f} m, y {float(c[:, 1].mean()):.4f} m.",
        f"Smallest principal {float(lam2.min()):.6e} Pa.",
        "Author to confirm that a positive principal membrane stress is the tension check.",
        "No code limit is applied. The crown of this bay is already on record as compression.",
    ]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
