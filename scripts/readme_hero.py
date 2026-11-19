"""Draw the README hero from the vault-bay record.

Two panels, same scale, bars from zero: extensional and shear stiffness of one
smooth bay, divided by a flat plate of the same thickness. One PNG per GitHub
theme, 1280 x 640 px. The plotted numbers are written to docs/img/hero.json.
Nothing here changes a result.

Colours are fixed to the bay, in file order. They are not sorted by the result.

Run: python scripts/readme_hero.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "partE_validation" / "out" / "vault_bay.txt"
OUT = ROOT / "docs" / "img"

# Identity colours, ShellBench slot order, fixed to these bays. Never re-ordered by rank.
WANT = [
    ("square 3 m, rise 0", "8x8", "flat", "rise 0", "#2a78d6"),
    ("3x3 m rise 0.30 equal V", "16x16", "3 m", "rise 0.30 m", "#eb6834"),
    ("3x3 m rise 0.60 equal V", "16x16", "3 m", "rise 0.60 m", "#1baf7a"),
    ("6x3 m rise 0.60 equal V", "16x8", "6×3 m", "rise 0.60 m", "#eda100"),
]

THEMES = {
    "light": {"bg": "#ffffff", "ink": "#0b0b0b", "muted": "#52514e", "faint": "#898781",
              "grid": "#e1e0d9", "spine": "#c3c2b7"},
    "dark": {"bg": "#0d1117", "ink": "#f0efec", "muted": "#c3c2b7", "faint": "#8f8d86",
             "grid": "#30363d", "spine": "#484f58"},
}


def load() -> tuple[list[dict], dict[str, str]]:
    """Equal-volume rows, plus the rise-zero row, as printed in the record."""
    text = SRC.read_text(encoding="utf-8")
    found = {}
    for ln in text.splitlines():
        m = re.match(
            r"^(square 3 m, rise 0|[\d.]+x[\d.]+ m rise [\d.]+ equal [tV])\s+"
            r"(\d+x\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
            ln,
        )
        if m:
            found[(m.group(1), m.group(2))] = {
                "case": m.group(1), "mesh": m.group(2), "t_mm": m.group(3),
                "area_plan": m.group(4), "Et": m.group(5), "Gt": m.group(6),
            }
    rows = []
    for case, mesh, name, role, colour in WANT:
        row = found.get((case, mesh))
        if row is None:
            raise SystemExit(f"vault_bay.txt has no row {case} {mesh}")
        rows.append({**row, "name": name, "role": role, "colour": colour})
    err = re.search(r"vs flat cell ([\deE.+-]+) % and ([\deE.+-]+) %", text)
    if not err:
        raise SystemExit("vault_bay.txt has no rise-zero comparison")
    return rows, {"Et_percent": err.group(1), "Gt_percent": err.group(2)}


def _fit(fig, text: str, x: float, y: float, color: str, weight: str, start: float, floor: float) -> None:
    t = fig.text(x, y, text, fontsize=start, fontweight=weight, color=color, ha="left", va="top")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    size = start
    while size > floor:
        bb = t.get_window_extent(renderer)
        if bb.x1 <= fig.bbox.xmax - 28:
            return
        size -= 0.5
        t.set_fontsize(size)
        fig.canvas.draw()


def fonts() -> list[str]:
    """Arial, then its metric twin, then DejaVu. Skip names that are not installed."""
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    names = [n for n in ("Arial", "Liberation Sans", "DejaVu Sans") if n in have]
    return names or ["DejaVu Sans"]


def draw(rows: list[dict], theme: str) -> Path:
    th = THEMES[theme]
    plt.rcParams.update({"font.family": fonts(), "font.size": 11, "axes.unicode_minus": False})
    fig = plt.figure(figsize=(12.8, 6.4), dpi=100, facecolor=th["bg"])
    lead = next(r for r in rows if r["case"] == "3x3 m rise 0.60 equal V")
    _fit(fig, f"Smooth 3 m bay, rise 0.60 m, equal volume: extensional stiffness {lead['Et']} of the flat plate.",
         0.045, 0.955, th["ink"], "bold", 15.5, 12)
    fig.text(0.045, 0.875,
             "Plan-projected membrane stiffness.  Thickness set so the faceted surface matches a 60 mm flat plate.  No ribs.",
             fontsize=11, color=th["muted"], ha="left", va="top")

    ymax = 1.38
    panels = [
        (0.055, "Et", "Extensional,  Et / (E t)"),
        (0.545, "Gt", "Shear,  Gt / (G t)"),
    ]
    for x0, key, title in panels:
        ax = fig.add_axes([x0, 0.18, 0.40, 0.56], facecolor=th["bg"])
        xpos = np.arange(len(rows))
        heights = [float(r[key]) for r in rows]
        ax.bar(xpos, heights, width=0.68, color=[r["colour"] for r in rows], zorder=3, linewidth=0)
        ax.axhline(1.0, color=th["muted"], lw=0.8, ls=(0, (3, 2)), zorder=4)
        for x, r, h in zip(xpos, rows, heights):
            ax.text(x, h + ymax * 0.018, r[key], ha="center", va="bottom",
                    fontsize=9.5, color=th["ink"], zorder=5)
        ax.set_ylim(0, ymax)
        ax.set_xlim(-0.55, len(rows) - 0.45)
        ax.set_xticks(xpos, [f"{r['name']}\n{r['role']}" for r in rows])
        ax.tick_params(axis="x", length=0, pad=4, colors=th["muted"], labelsize=9)
        ax.tick_params(axis="y", length=3, direction="out", colors=th["muted"], labelsize=9)
        ax.yaxis.grid(True, color=th["grid"], lw=0.6, zorder=0)
        ax.set_axisbelow(True)
        for name, spine in ax.spines.items():
            spine.set_visible(name in ("left", "bottom"))
            spine.set_color(th["spine"])
            spine.set_linewidth(0.6)
        ax.set_title(title, loc="left", color=th["ink"], fontsize=12.5, fontweight="bold", pad=8)
        if x0 < 0.1:
            ax.set_ylabel("Ratio to a flat plate of the same thickness", color=th["muted"], fontsize=10)
        else:
            ax.set_yticklabels([])
    lines = [
        "Bars start at zero and stay in bay order. Dashed line: the flat plate. The number is the file value.",
        "Data: partE_validation/out/vault_bay.txt. Curved bars are the finest equal-volume mesh of that bay.",
    ]
    for y, line in ((0.058, lines[0]), (0.026, lines[1])):
        _fit(fig, line, 0.045, y, th["faint"], "normal", 8.5, 7.5)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"hero_{theme}.png"
    fig.savefig(path, dpi=100, facecolor=th["bg"], metadata={"Software": None})
    plt.close(fig)
    return path


def main() -> None:
    rows, err = load()
    for theme in THEMES:
        print(draw(rows, theme))
    payload = {
        "sources": ["partE_validation/out/vault_bay.txt"],
        "rule": "Et/(E t) and Gt/(G t) of a flat plate with the thickness in the row. Equal-volume thickness matches the faceted area to a 60 mm plate.",
        "order": [r["case"] + " " + r["mesh"] for r in rows],
        "rise_zero_vs_flat_cell_percent": err,
        "rows": [{k: r[k] for k in ("case", "mesh", "t_mm", "area_plan", "Et", "Gt")} for r in rows],
    }
    (OUT / "hero.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    from PIL import Image
    for theme in THEMES:
        im = Image.open(OUT / f"hero_{theme}.png")
        if im.size != (1280, 640):
            raise SystemExit(f"hero_{theme}.png is {im.size}, expected 1280x640")
    print("wrote", OUT / "hero.json")


if __name__ == "__main__":
    main()
