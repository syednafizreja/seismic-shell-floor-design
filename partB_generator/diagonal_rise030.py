"""The recorded diagonals at rise 0.30 m.

Same width, same 50 mm shell, same volume. Does not rewrite diagonal_bay.txt.
Author to confirm the rise.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import diagonal_bay as bay

bay.RISE = 0.30
bay.OUT = Path(__file__).parent / "out" / "diagonal_rise030.txt"
bay.main()
text = bay.OUT.read_text(encoding="utf-8")
note = "Rise 0.30 m. Same diagonals and the same volume rule. This file does not replace diagonal_bay.txt.\n"
if not text.startswith("Rise 0.30"):
    bay.OUT.write_text(note + text, encoding="utf-8")
    print(note.strip())
