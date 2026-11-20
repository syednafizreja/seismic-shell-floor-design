"""Membrane tension on the recorded cross at rise 0.30 m and 0.60 m.

Same cross, shell and volume as the gravity files. A principal value above
zero is tension. The check is the shell-local membrane, the average of the
two faces. Each crown must match the gravity file. This script does not
replace those files or the smooth-bay counts.
Author to confirm the cross and this definition of compression-only.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import faceted_area, grid_on_surface, run_dat, sinusoid_bay
from partB_generator.compression_smooth import principals
from partE_validation.gravity_bay import LX, N, T_SHELL, deck
from partE_validation.vault_rib import rib_thickness

OUT_DIR = Path(__file__).parent / "out"
# Crown faces in gravity_rise030.txt and gravity_bay.txt.
EXPECTED = {
    0.30: (-4.546519e4, -3.102803e4),
    0.60: (-1.867630e4, -1.325382e4),
}


def local_membrane(text, n_el):
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
    if len(acc) != n_el:
        raise RuntimeError(f"stress file has {len(acc)} elements, mesh has {n_el}")
    local = np.zeros((n_el, 3))
    for k in range(n_el):
        rows = [acc[k + 1][i] for i in range(1, 9)]
        mid = 0.5 * (np.mean(rows[:4], axis=0) + np.mean(rows[4:], axis=0))
        local[k] = (mid[0], mid[1], mid[3])
    return local, acc, suffix


def one(rise):
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, rise))
    th, t_rib, _, _ = rib_thickness(xyz, els, LX, LX)
    area = faceted_area(xyz, els)
    static, _ = deck(xyz, els, T_SHELL, th, buckle=False)
    static = static.replace("*EL PRINT, ELSET=CROWN", "*EL PRINT, ELSET=EALL")
    text = run_dat(static)
    local, acc, suffix = local_membrane(text, len(els))
    crown, bestd = 0, 1e9
    for k, e in enumerate(els):
        c = xyz[np.asarray(e[:4]) - 1]
        d = (float(c[:, 0].mean()) - LX / 2) ** 2 + (float(c[:, 1].mean()) - LX / 2) ** 2
        if d < bestd:
            crown, bestd = k, d
    rows = [acc[crown + 1][i] for i in range(1, 9)]
    faces = (float(np.mean(rows[:4], axis=0)[0]), float(np.mean(rows[4:], axis=0)[0]))
    want = EXPECTED[rise]
    if max(abs(faces[0] - want[0]), abs(faces[1] - want[1])) > 1.0:
        raise RuntimeError(f"rise {rise} crown faces {faces} do not match the gravity file")
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
    further = []
    farthest = None
    corners = ((0.0, 0.0), (0.0, LX), (LX, 0.0), (LX, LX))
    for k in np.flatnonzero(tension):
        cc = xyz[np.asarray(els[k][:4]) - 1]
        x, y = float(cc[:, 0].mean()), float(cc[:, 1].mean())
        dist = min(float(np.hypot(x - cx, y - cy)) for cx, cy in corners)
        if farthest is None or dist > farthest[0]:
            farthest = (dist, x, y)
        if min(x, y, LX - x, LX - y) <= pitch + 1e-9:
            edge += 1
        else:
            further.append(f"x {x:.4f} m, y {y:.4f} m, {lam1[k]:.6e} Pa")
    lines = [
        f"Rise {rise:.2f} m. The recorded cross. This file does not replace the smooth-bay count.",
        "Shell-local membrane under self-weight. Positive principal stress is tension.",
        "Average of the two faces. Shell 50 mm. Same volume as a 60 mm flat plate.",
        f"Print suffix {suffix}. Rib thickness {t_rib * 1e3:.2f} mm. area/plan {area / LX / LX:.4f}.",
        f"Crown element {crown + 1}, faces {faces[0]:.6e} Pa and {faces[1]:.6e} Pa.",
        f"Elements {len(els)}. With a tensile principal {int(tension.sum())}.",
        f"With both principals tensile {int(both.sum())}.",
        f"Of the tensile elements, {edge} lie within one element pitch of the plan boundary.",
        "Further than one element pitch from the plan boundary: " + ("; ".join(further) if further else "none") + ".",
        f"Largest principal {lam1[k_max]:.6e} Pa at x {float(c[:, 0].mean()):.4f} m, y {float(c[:, 1].mean()):.4f} m.",
        f"Farthest tensile centroid from a plan corner {farthest[0]:.4f} m." if farthest else "No tensile element.",
        f"Smallest principal {float(lam2.min()):.6e} Pa.",
        "Author to confirm that a positive principal membrane stress is the tension check.",
        "No code limit is applied. The crown faces match the gravity file and are compression.",
    ]
    out = OUT_DIR / f"compression_cross_rise{int(round(rise * 100)):03d}.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"wrote {out.name}")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    one(0.30)
    one(0.60)
    print("CROSS_TENSION_DONE")


if __name__ == "__main__":
    main()
