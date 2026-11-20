"""Gravity at rise 0.30 m for the recorded smooth shell and the cross.

The smooth static solution is already in the rise 0.30 m stress print.
This script adds that bay's buckling factor and runs the cross.
It does not replace gravity_bay.txt.
Author to confirm the rise.
"""
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import faceted_area, grid_on_surface, run_dat, sinusoid_bay
from partE_validation.gravity_bay import LX, N, T, deck, displacements, factors, one

OUT = Path(__file__).parent / "out" / "gravity_rise030.txt"
DAT = Path(__file__).parent.parent / "partB_generator" / "out" / "smooth_gravity_stress_030.dat"
# Crown deflection already parsed from that print.
SMOOTH_CROWN_MM = -0.006964


def smooth_buckle():
    if not DAT.is_file():
        raise RuntimeError(f"missing stress print {DAT.name}")
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, 0.30))
    area = faceted_area(xyz, els)
    t = T * LX * LX / area
    U = displacements(DAT.read_text(encoding="utf-8", errors="replace"), len(xyz))
    w = U[:, 2]
    crown = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LX / 2)))
    crown_mm = float(w[crown] * 1e3)
    if abs(crown_mm - SMOOTH_CROWN_MM) > 5e-7:
        raise RuntimeError(f"smooth crown {crown_mm:.6f} mm does not match the stress print")
    buck, _ = deck(xyz, els, t, None, buckle=True)
    fac = factors(run_dat(buck))
    positive = [v for v in fac if v > 0]
    lam = positive[0] if positive else float("nan")
    return [
        "smooth, rise 0.30 m, equal volume",
        f"  thickness shell {t * 1e3:.2f} mm, rib {t * 1e3:.2f} mm, area/plan {area / LX / LX:.4f}",
        f"  crown w from the existing stress print {crown_mm:.6f} mm, largest |w| {np.max(np.abs(w)) * 1e3:.6f} mm",
        f"  lowest positive buckling factor on self-weight {lam:.6g}  factors {fac}",
        "  Static stresses stay in the existing stress print. This run is the buckle only.",
    ]


def main():
    lines = [
        "Rise 0.30 m. This file does not replace gravity_bay.txt.",
        "Same supports, density and volume rule as gravity_bay.py. No knockdown is applied.",
        f"Mesh {N}x{N}. Linear S8R.",
    ]
    lines += smooth_buckle()
    lines += one("cross, rise 0.30 m, equal volume", 0.30, rib=True)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("GRAV030_DONE")


if __name__ == "__main__":
    main()
