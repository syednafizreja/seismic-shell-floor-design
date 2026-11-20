"""The same stress-line ribs at twice the recorded spacing.

Does not rewrite stress_rib.txt. One check, not a spacing search.
Author to confirm 0.75 m.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import stress_rib as bay

bay.D_SEP = 0.75
bay.OUT = Path(__file__).parent / "out" / "stress_rib_075.txt"
bay.main()
text = bay.OUT.read_text(encoding="utf-8")
note = "Twice the recorded 0.375 m spacing. This file does not replace stress_rib.txt.\n"
if not text.startswith("Twice the recorded"):
    bay.OUT.write_text(note + text)
    print(note.strip())
