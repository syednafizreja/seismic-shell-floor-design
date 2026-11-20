"""Raw crown-to-all stress print for the smooth rise 0.60 m bay under self-weight.

Same mesh, thickness and supports as gravity_bay.py. The print set is every
element, so a later tracer can be checked against the file. This script does
not trace ribs and does not rewrite gravity_bay.txt.
"""
from pathlib import Path

from partA_mechanics.plate_fe import faceted_area, grid_on_surface, run_dat, sinusoid_bay
from partE_validation.gravity_bay import LX, N, T, deck

OUT = Path(__file__).parent / "out" / "smooth_gravity_stress.dat"
RISE = 0.60


def main():
    xyz, els = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, RISE))
    area = faceted_area(xyz, els)
    t = T * LX * LX / area
    static, _ = deck(xyz, els, t, None, buckle=False)
    static = static.replace("*EL PRINT, ELSET=CROWN", "*EL PRINT, ELSET=EALL")
    text = run_dat(static)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT}")
    print(f"t {t * 1e3:.2f} mm, elements {len(els)}, characters {len(text)}")


if __name__ == "__main__":
    main()
