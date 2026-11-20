"""Principal-stress ribs at rise 0.30 m and the recorded 0.375 m spacing.

Writes a new stress print. Does not replace stress_rib.txt or the rise 0.60 m print.
Author to confirm the rise.
"""
import sys
from pathlib import Path

import numpy as np

from partA_mechanics.plate_fe import grid_on_surface, sinusoid_bay
from partE_validation.gravity_bay import LX, N, displacements

sys.path.insert(0, str(Path(__file__).parent))
import smooth_stress as field
import stress_rib as bay

field.RISE = 0.30
field.OUT = Path(__file__).parent / "out" / "smooth_gravity_stress_030.dat"
field.main()

bay.RISE = 0.30
bay.DAT = field.OUT
bay.CROWN_SXX = None
bay.OUT = Path(__file__).parent / "out" / "stress_rib_rise030.txt"
bay.main()
text = bay.OUT.read_text(encoding="utf-8")
note = "Rise 0.30 m at the recorded 0.375 m spacing. This file does not replace stress_rib.txt.\n"
if not text.startswith("Rise 0.30"):
    text = note + text
xyz, _ = grid_on_surface(LX, LX, N, N, sinusoid_bay(LX, LX, 0.30))
U = displacements(field.OUT.read_text(encoding="utf-8", errors="replace"), len(xyz))
w = U[:, 2]
crown = int(np.argmin(np.hypot(xyz[:, 0] - LX / 2, xyz[:, 1] - LX / 2)))
extra = f"Smooth shell in the same print: crown w {w[crown] * 1e3:.6f} mm, largest |w| {np.max(np.abs(w)) * 1e3:.6f} mm.\n"
if "Smooth shell in the same print" not in text:
    text += extra
bay.OUT.write_text(text, encoding="utf-8")
print(extra.strip())
