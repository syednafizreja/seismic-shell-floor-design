"""Membrane tension on the recorded stress-line ribs.

Same lines, shell and volume as the three result files. A principal above
zero is tension. Each crown must match that file. This script does not
replace those files, and it does not replace the smooth, cross or diagonal
counts.
Author to confirm the stress lines and this definition of compression-only.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import faceted_area, grid_on_surface, run_dat, sinusoid_bay
from partB_generator.compression_diagonal import local_membrane
from partB_generator.compression_smooth import principals
from partB_generator import stress_rib as bay
from partE_validation.gravity_bay import LX, N, T_SHELL, deck

OUT_DIR = Path(__file__).parent / "out"
DAT60 = OUT_DIR / "smooth_gravity_stress.dat"
DAT30 = OUT_DIR / "smooth_gravity_stress_030.dat"
# Ribbed crown faces are the recorded gravity lines. Field faces are the smooth print.
CASES = (
    {
        "tag": "rise060_s375",
        "rise": 0.60,
        "d_sep": 0.375,
        "dat": DAT60,
        "field": (-1.941393e4, -1.684599e4),
        "crown": (-2.022574e4, -1.691824e4),
        "n_rib": 236,
        "t_mm": 59.16,
        "label": "Rise 0.60 m, spacing 0.375 m.",
    },
    {
        "tag": "rise060_s750",
        "rise": 0.60,
        "d_sep": 0.75,
        "dat": DAT60,
        "field": (-1.941393e4, -1.684599e4),
        "crown": (-1.962041e4, -1.705144e4),
        "n_rib": 128,
        "t_mm": 66.65,
        "label": "Rise 0.60 m, spacing 0.75 m.",
    },
    {
        "tag": "rise030_s375",
        "rise": 0.30,
        "d_sep": 0.375,
        "dat": DAT30,
        "field": (-5.014637e4, -2.806953e4),
        "crown": (-5.470485e4, -2.852846e4),
        "n_rib": 232,
        "t_mm": 66.29,
        "label": "Rise 0.30 m, spacing 0.375 m.",
    },
)


def one(case):
    if not case["dat"].is_file():
        raise RuntimeError(f"missing stress print {case['dat'].name}")
    bay.RISE = case["rise"]
    bay.D_SEP = case["d_sep"]
    bay.DAT = case["dat"]
    bay.CROWN_SXX = case["field"]
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, case["rise"]))
    xy, tensors, _, _, _ = bay.membrane_tensors(xyz, els)
    lines = bay.traced_lines(xy, tensors)
    th, t_rib, n_rib = bay.rib_thickness(xyz, els, lines)
    t_mm = round(t_rib * 1e3, 2)
    if n_rib != case["n_rib"] or abs(t_mm - case["t_mm"]) > 0.001:
        raise RuntimeError(
            f"{case['tag']} rebuilt {n_rib} elements at {t_mm:.2f} mm, "
            f"record is {case['n_rib']} at {case['t_mm']:.2f} mm")
    area = faceted_area(xyz, els)
    static, _ = deck(xyz, els, T_SHELL, th, buckle=False)
    static = static.replace("*EL PRINT, ELSET=CROWN", "*EL PRINT, ELSET=EALL")
    local, acc, suffix = local_membrane(run_dat(static), len(els))
    crown, bestd = 0, 1e9
    for k, e in enumerate(els):
        c = xyz[np.asarray(e[:4]) - 1]
        d = (float(c[:, 0].mean()) - LX / 2) ** 2 + (float(c[:, 1].mean()) - LX / 2) ** 2
        if d < bestd:
            crown, bestd = k, d
    rows = [acc[crown + 1][i] for i in range(1, 9)]
    faces = (float(np.mean(rows[:4], axis=0)[0]), float(np.mean(rows[4:], axis=0)[0]))
    want = case["crown"]
    if max(abs(faces[0] - want[0]), abs(faces[1] - want[1])) > 1.0:
        raise RuntimeError(f"{case['tag']} crown faces {faces} do not match the recorded file")
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
    lines_out = [
        f"{case['label']} The recorded stress lines. This file does not replace the other counts.",
        "Shell-local membrane under self-weight. Positive principal stress is tension.",
        "Average of the two faces. Shell 50 mm. Same volume as a 60 mm flat plate.",
        f"Print suffix {suffix}. Rib elements {n_rib}. Rib thickness {t_rib * 1e3:.2f} mm. area/plan {area / LX / LX:.4f}.",
        f"Crown element {crown + 1}, faces {faces[0]:.6e} Pa and {faces[1]:.6e} Pa.",
        f"Elements {len(els)}. With a tensile principal {int(tension.sum())}.",
        f"With both principals tensile {int(both.sum())}.",
        f"Of the tensile elements, {edge} lie within one element pitch of the plan boundary.",
        "Further than one element pitch from the plan boundary: " + ("; ".join(further) if further else "none") + ".",
        f"Largest principal {lam1[k_max]:.6e} Pa at x {float(c[:, 0].mean()):.4f} m, y {float(c[:, 1].mean()):.4f} m.",
        f"Farthest tensile centroid from a plan corner {farthest[0]:.4f} m." if farthest else "No tensile element.",
        f"Smallest principal {float(lam2.min()):.6e} Pa.",
        "Author to confirm that a positive principal membrane stress is the tension check.",
        "No code limit is applied. The crown faces match the recorded file and are compression.",
    ]
    out = OUT_DIR / f"compression_stress_{case['tag']}.txt"
    out.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print("\n".join(lines_out))
    print(f"wrote {out.name}")


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for case in CASES:
        one(case)
    print("STRESS_TENSION_DONE")


if __name__ == "__main__":
    main()
